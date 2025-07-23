import re
import json
import time
import logging

import openai
from openai.error import OpenAIError
from backend.config import settings
from backend.agents.logger import log_agent

logger = logging.getLogger(__name__)

# OpenAI config
openai.api_key = settings.OPENAI_API_KEY
PRIMARY_MODEL   = getattr(settings, "OPENAI_MODEL", "gpt-4")
FALLBACK_MODEL  = "gpt-3.5-turbo"

# Configuration
MIN_NEWS_ITEMS  = 3
MAX_RETRIES     = 3
INITIAL_BACKOFF = 1    # seconds
REQUEST_TIMEOUT = 10   # seconds

@log_agent("sentiment")
def sentiment_agent(state):
    """
    Analyze overall sentiment of news items.
    Returns: {'sentiment': <str>, 'confidence': <float>}
    """
    news_items = state.news or []

    # 1) Minimum-news threshold
    if len(news_items) < MIN_NEWS_ITEMS:
        logger.warning("[SentimentAgent] Not enough news items (%d); defaulting to Neutral.", len(news_items))
        return {"sentiment": "Neutral", "confidence": 0.0}

    logger.info("[SentimentAgent] 🚀 Analyzing sentiment from %d news items...", len(news_items))

    combined = "\n".join(f"- {item['title']}: {item['snippet']}" for item in news_items)
    user_prompt = (
        "Given the following financial news items, provide an overall sentiment: "
        "Bullish, Bearish, or Neutral. Also give a confidence score between 0 and 1."
        "\n\n"
        f"{combined}\n\n"
        "Respond ONLY with JSON in the format: {\"sentiment\": \"Bullish\", \"confidence\": 0.85}."
    )

    messages = [
        {"role": "system", "content": "You are a financial-market sentiment analysis assistant."},
        {"role": "user", "content": user_prompt}
    ]

    model   = PRIMARY_MODEL
    backoff = INITIAL_BACKOFF

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.0,
                max_tokens=64,
                request_timeout=REQUEST_TIMEOUT,
            )
            raw = resp.choices[0].message.content.strip()

            match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            json_text = match.group(0) if match else raw
            data = json.loads(json_text)

            if set(data.keys()) <= {"sentiment", "confidence"}:
                sentiment = data.get("sentiment", "Neutral")
                confidence = float(data.get("confidence", 0.0))

                logger.info("[SentimentAgent] ✅ Sentiment analysis complete")
                logger.info("[SentimentAgent] 📊 Sentiment: %s | 💡 Confidence: %.2f", sentiment, confidence)
                return {"sentiment": sentiment, "confidence": confidence}
            else:
                raise ValueError(f"Unexpected keys in JSON: {data.keys()}")

        except (OpenAIError, json.JSONDecodeError, ValueError) as e:
            logger.error("[SentimentAgent] ❌ Attempt %d with model %s failed: %s", attempt, model, e)
            if attempt < MAX_RETRIES:
                time.sleep(backoff)
                backoff *= 2
                if attempt == 1:
                    model = FALLBACK_MODEL
                    logger.info("[SentimentAgent] 🔁 Falling back to %s", model)
                continue

            logger.error("[SentimentAgent] ⚠️ All retries failed; defaulting to Neutral.")
            return {"sentiment": "Neutral", "confidence": 0.0}
