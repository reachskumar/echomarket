import logging
import json
from typing import Any, Dict, List, Tuple

import openai
from backend.config import settings
from backend.agents.logger import log_agent 

logger = logging.getLogger(__name__)

# Config from .env or settings
MODEL_NAME       = getattr(settings, "PREDICTION_MODEL", "gpt-4")
TEMPERATURE      = getattr(settings, "PREDICTION_TEMPERATURE", 0.0)
MAX_TOKENS       = getattr(settings, "PREDICTION_MAX_TOKENS", 60)
HISTORY_WINDOW   = getattr(settings, "PREDICTION_HISTORY_WINDOW", 5)

@log_agent("prediction")
def prediction_agent(state: Any) -> Dict[str, str]:
    """
    Generate a Buy/Hold/Sell recommendation plus a one-sentence insight.
    """
    raw_prices  = getattr(state, "prices", {}) or {}
    sentiment   = getattr(state, "sentiment", "Neutral")
    confidence  = getattr(state, "confidence", 0.0)

    try:
        sorted_items: List[Tuple[str, float]] = sorted(
            raw_prices.items(), key=lambda x: x[0]
        )
        history_window = sorted_items[-HISTORY_WINDOW:]
    except Exception as e:
        logger.warning(
            "[PredictionAgent] Failed to sort price history, defaulting to empty: %s", e
        )
        history_window = []

    prompt = (
        "You are a seasoned financial analyst AI.\n\n"
        f"1️⃣ Latest sentiment: {sentiment} (confidence {confidence:.2f})\n"
        f"2️⃣ Recent price points: {history_window}\n\n"
        "Based on this, give exactly one recommendation: Buy, Hold, or Sell. "
        "Then provide a one-sentence rationale.\n\n"
        'Respond in JSON like: {"recommendation":"Buy","insight":"..."}'
    )

    try:
        resp = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        content = resp.choices[0].message.content.strip()
        data = json.loads(content)
        recommendation = data.get("recommendation", "Hold")
        insight        = data.get("insight", "No clear signal.")
    except json.JSONDecodeError as e:
        logger.error(
            "[PredictionAgent] JSON parse error: %s\nRaw content: %r", e, content, exc_info=True
        )
        recommendation, insight = "Hold", "Could not interpret model response."
    except Exception as e:
        logger.exception("[PredictionAgent] Unexpected error during prediction")
        recommendation, insight = "Hold", "Prediction failed due to an internal error."

    # structured logging
    logger.info("[PredictionAgent] ✅ Prediction complete for recent trend and sentiment")
    logger.info(
        "[PredictionAgent] 📈 Sentiment: %s | 💡 Confidence: %.2f | 📊 Price Points: %d",
        sentiment, confidence, len(history_window)
    )
    logger.info(
        "[PredictionAgent] 🤖 GPT Recommendation: %s | Insight: %s",
        recommendation, insight
    )

    return {"recommendation": recommendation, "insight": insight}
