import logging
from typing import Any, Dict, List
import requests

from backend.config import settings
from backend.agents.logger import log_agent

logger = logging.getLogger(__name__)

MAX_NEWS_ITEMS    = getattr(settings, "MARKET_NEWS_MAX_RESULTS", 20)
TAVILY_SEARCH_URL = getattr(settings, "TAVILY_SEARCH_URL", "https://api.tavily.com/search")
TAVILY_API_KEY    = settings.TAVILY_API_KEY

session = requests.Session()

@log_agent("market_news")
def market_news_agent(state: Any) -> Dict[str, List[Dict[str, str]]]:
    ticker = state.ticker
    query  = f"{ticker} latest financial news"

    payload = {
        "query": query,
        "max_results": MAX_NEWS_ITEMS,
    }
    headers = {
        "Authorization": f"Bearer {TAVILY_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        resp = session.post(TAVILY_SEARCH_URL, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        raw_items = data.get("results", [])
        if not isinstance(raw_items, list):
            logger.warning("Unexpected format for `results`: %r", raw_items)
            raw_items = []
    except requests.HTTPError as e:
        status = e.response.status_code if e.response else "?"
        logger.error("HTTP error %s: %s", status, e, exc_info=True)
        raw_items = []
    except requests.RequestException as e:
        logger.error("Request failed: %s", e, exc_info=True)
        raw_items = []
    except ValueError as e:
        logger.error("Invalid JSON response: %s", e, exc_info=True)
        raw_items = []

    news: List[Dict[str, str]] = []
    for item in raw_items[:MAX_NEWS_ITEMS]:
        title   = item.get("title", "").strip()
        url     = item.get("url", "").strip()
        snippet = (item.get("snippet") or item.get("content") or "").strip()
        if title and url:
            news.append({"title": title, "url": url, "snippet": snippet})

    logger.info("[MarketNewsAgent] ✅ Completed news fetch for %s – %d articles found", ticker, len(news))

    if news:
        logger.info("[MarketNewsAgent] 📰 Top headline: %s", news[0]["title"])

    return {"news": news}
