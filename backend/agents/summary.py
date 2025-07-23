import time
import logging

import openai
from openai.error import OpenAIError
from backend.config import settings
from backend.agents.logger import log_agent 

logger = logging.getLogger(__name__)

# OpenAI setup
openai.api_key       = settings.OPENAI_API_KEY
PRIMARY_MODEL        = getattr(settings, "OPENAI_MODEL", "gpt-4")
FALLBACK_MODEL       = "gpt-3.5-turbo"
REQUEST_TIMEOUT      = getattr(settings, "SUMMARY_REQUEST_TIMEOUT", 10)

# Summary agent configuration
MAX_NEWS_ITEMS       = getattr(settings, "SUMMARY_MAX_NEWS_ITEMS", 5)
MAX_RETRIES          = getattr(settings, "SUMMARY_MAX_RETRIES", 3)
INITIAL_BACKOFF      = getattr(settings, "SUMMARY_BACKOFF_SEC", 1)
SUMMARY_TEMPERATURE  = getattr(settings, "SUMMARY_TEMPERATURE", 0.3)
SUMMARY_MAX_TOKENS   = getattr(settings, "SUMMARY_MAX_TOKENS", 150)


@log_agent("summary")
def summary_agent(state):
    """
    Create a concise, human‐readable market summary.

    Inputs on state:
      - state.news           : list of {title, url, snippet}
      - state.sentiment      : str
      - state.confidence     : float
      - state.recommendation : str
      - state.insight        : str
      - state.prices         : dict {date: price}

    Returns: {"summary": <str>, "recommendation": <str>, "insight": <str>, "price": <str>}
    """
    news_items     = state.news or []
    sentiment      = state.sentiment or "Neutral"
    confidence     = state.confidence or 0.0
    recommendation = state.recommendation or "Hold"
    insight        = state.insight or ""

    # --- Real-time price from state ---
    price_value = "N/A"
    if isinstance(state.get("prices"), dict) and state["prices"]:
        price_value = str(list(state["prices"].values())[0])

    # 1) Short-circuit if no news
    if not news_items:
        logger.warning("[SummaryAgent] No news items found. Returning default summary.")
        msg = (
            f"No recent news to summarize. Based on a {sentiment} sentiment "
            f"(confidence {confidence:.2f}) and a recommendation to {recommendation}, "
            "there are no new highlights."
        )
        return {
            "summary": msg,
            "recommendation": recommendation,
            "insight": insight,
            "price": price_value
        }

    logger.info("[SummaryAgent] ✏️ Generating summary from %d news items...", len(news_items))
    logger.info("[SummaryAgent] 📊 Sentiment: %s | 💡 Confidence: %.2f | 🧠 Recommendation: %s", sentiment, confidence, recommendation)

    # 2) Truncate to avoid token overrun
    selected   = news_items[:MAX_NEWS_ITEMS]
    news_block = "".join(f"  • {item['title']}: {item['snippet']}\n" for item in selected)

    # Build the chat messages
    system_msg = {
        "role": "system",
        "content": "You are a senior financial analyst who writes clear, professional summaries."
    }
    user_msg = {
        "role": "user",
        "content": (
            "Given the following market data, write a concise, professional summary in 2–3 sentences:\n\n"
            f"- Overall sentiment: {sentiment} (confidence {confidence:.2f})\n"
            f"- Recommendation: {recommendation} (insight: {insight})\n"
            f"- Real-time price: {price_value}\n"
            "- Top news headlines:\n"
            f"{news_block}"
        )
    }

    model   = PRIMARY_MODEL
    backoff = INITIAL_BACKOFF

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = openai.ChatCompletion.create(
                model=model,
                messages=[system_msg, user_msg],
                temperature=SUMMARY_TEMPERATURE,
                max_tokens=SUMMARY_MAX_TOKENS,
                request_timeout=REQUEST_TIMEOUT,
            )
            summary_text = resp.choices[0].message.content.strip()
            logger.info("[SummaryAgent] ✅ Summary generated successfully")
            return {
                "summary": summary_text,
                "recommendation": recommendation,
                "insight": insight,
                "price": price_value
            }

        except OpenAIError as e:
            logger.error("[SummaryAgent] ❌ Attempt %d with model %s failed: %s", attempt, model, e)
            if attempt < MAX_RETRIES:
                time.sleep(backoff)
                backoff *= 2
                if attempt == 1:
                    model = FALLBACK_MODEL
                    logger.info("[SummaryAgent] 🔁 Falling back to %s", model)
                continue

    logger.error("[SummaryAgent] ⚠️ All retries exhausted. Returning fallback summary.")
    return {
        "summary": "Market summary is currently unavailable — please try again later.",
        "recommendation": recommendation,
        "insight": insight,
        "price": price_value
    }
