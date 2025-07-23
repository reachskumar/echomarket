import logging
from datetime import datetime
from typing import Any, Dict

import requests
from backend.config import settings
from backend.agents.logger import log_agent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@log_agent("price")
def price_agent(state: Any) -> Dict[str, Any]:
    ticker = getattr(state, "ticker", "").upper()
    if not ticker:
        raise ValueError("[PriceAgent] ❌ No ticker provided in state")

    logger.info("[PriceAgent] 📈 Fetching real-time price from TwelveData for %s", ticker)

    try:
        api_key = settings.TWELVE_DATA_API_KEY
        if not api_key:
            logger.error("[PriceAgent] ❌ TWELVE_DATA_API_KEY not configured in environment.")
            return {"price": "N/A", "prices": {}, "source": "none"}

        url = "https://api.twelvedata.com/price"
        params = {"symbol": ticker, "apikey": api_key}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()

        payload = resp.json()
        price_str = payload.get("price")

        if price_str:
            price = float(price_str)
            today = datetime.utcnow().date()
            logger.info("[PriceAgent] ✅ Price fetched for %s: %.2f", ticker, price)
            return {
                "price": price,  # <-- New direct field
                "prices": {
                    str(today): price
                },
                "source": "twelvedata"
            }
        else:
            logger.warning("[PriceAgent] ⚠️ Price not found in response for %s", ticker)
            return {"price": "N/A", "prices": {}, "source": "twelvedata"}

    except Exception as e:
        logger.error("[PriceAgent] ❌ Error fetching price for %s: %s", ticker, e)
        return {"price": "N/A", "prices": {}, "source": "none"}
