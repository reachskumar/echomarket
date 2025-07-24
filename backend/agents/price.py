# Gets current price and recent price history for a stock
# Uses TwelveData API

import logging
from datetime import datetime
from typing import Any, Dict
import requests
from backend.config import settings
from backend.agents.logger import log_agent
from openai import OpenAIError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@log_agent("price")  # Logs price analysis
def price_agent(state: Any) -> Dict[str, Any]:
    ticker = getattr(state, "ticker", "").upper()
    if not ticker:
        # Make sure we have a ticker
        logger.error("No ticker provided")
        return {"price": None, "prices": {}, "source": "none"}

    logger.info(f"Fetching price for {ticker}")
    try:
        api_key = settings.TWELVE_DATA_API_KEY
        if not api_key:

            logger.error("TWELVE_DATA_API_KEY not set")
            return {"price": None, "prices": {}, "source": "none"}

        # Get current price from TwelveData
        url = "https://api.twelvedata.com/price"
        params = {"symbol": ticker, "apikey": api_key}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        payload = resp.json()
        price_str = payload.get("price")
        price = None
        if price_str:
            try:
                price = float(price_str)
            except Exception:
                logger.warning(f"Could not convert price: {price_str}")
                price = None

        # Get 7 days of price history
        hist_url = "https://api.twelvedata.com/time_series"
        hist_params = {
            "symbol": ticker,
            "interval": "1day",
            "outputsize": 7,
            "apikey": api_key
        }
        hist_resp = requests.get(hist_url, params=hist_params, timeout=10)
        hist_resp.raise_for_status()
        hist_payload = hist_resp.json()
        prices = {}
        if "values" in hist_payload:
            for entry in hist_payload["values"]:
                date = entry.get("datetime")
                close = entry.get("close")
                if date and close:
                    try:
                        prices[date] = float(close)
                    except Exception:
                        continue
        if not prices and price is not None and price > 0:
            today = datetime.utcnow().date()
            prices[str(today)] = price
        if price is not None and price > 0:
            # Return price and history if found, else warn
            return {"price": price, "prices": prices, "source": "twelvedata"}
        else:
            logger.warning(f"Price not found for {ticker}")
            return {"price": None, "prices": prices, "source": "twelvedata"}
    except Exception as e:
        # Handle any errors and log them
        logger.error(f"Error fetching price for {ticker}: {e}")
        return {"price": None, "prices": {}, "source": "none"}
