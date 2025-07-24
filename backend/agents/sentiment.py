# Figures out if the news is bullish, bearish, or neutral for this stock

import re
import json
import time
import logging
import openai
from openai import OpenAIError
from backend.config import settings
from backend.agents.logger import log_agent

logger = logging.getLogger(__name__)

openai.api_key = settings.OPENAI_API_KEY
PRIMARY_MODEL = getattr(settings, "OPENAI_MODEL", "gpt-4")
FALLBACK_MODEL = "gpt-3.5-turbo"

MIN_NEWS_ITEMS = 3
MAX_RETRIES = 3
INITIAL_BACKOFF = 1
REQUEST_TIMEOUT = 10

@log_agent("sentiment")  # Logs sentiment analysis
def sentiment_agent(state):
    # Checks news count, builds prompt, and asks OpenAI for sentiment
    news_items = state.news or []
    if len(news_items) < MIN_NEWS_ITEMS:
        logger.warning("Not enough news; defaulting to Neutral.")
        return {"sentiment": "Neutral", "confidence": 0.0}

    logger.info(f"Analyzing sentiment from {len(news_items)} news items...")
    combined = "\n".join(f"- {item['title']}: {item['snippet']}" for item in news_items)
    # Build the prompt for OpenAI
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
    model = PRIMARY_MODEL
    backoff = INITIAL_BACKOFF
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Try up to 3 times, fallback to GPT-3.5 if needed
            resp = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.0,
                max_tokens=64,
                request_timeout=REQUEST_TIMEOUT,
            )
            raw = resp.choices[0].message.content.strip()
            logger.info(f"AI response: {raw}")

            match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            json_text = match.group(0) if match else raw
            data = json.loads(json_text)
            
            if set(data.keys()) <= {"sentiment", "confidence"}:
                sentiment = data.get("sentiment") or "Neutral"
                confidence = float(data.get("confidence") or 0.0)
                logger.info(f"Analysis complete: {sentiment} (confidence: {confidence:.2f})")
                return {"sentiment": sentiment, "confidence": confidence}
            else:
                raise ValueError(f"Unexpected response format: {data.keys()}")
        except (OpenAIError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Attempt {attempt} failed with model {model}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(backoff)
                backoff *= 2
                if attempt == 1:
                    model = FALLBACK_MODEL
                    logger.info(f"Falling back to {model}")
                continue
            logger.error("All retries failed; defaulting to Neutral.")
            return {"sentiment": "Neutral", "confidence": 0.0}
