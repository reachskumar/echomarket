# Finds recent news for a stock using Tavily API

import logging
from typing import Any, Dict
import requests
from backend.config import settings
from backend.agents.logger import log_agent
from openai import OpenAIError

logger = logging.getLogger(__name__)

@log_agent("market_news")  # Logs news search steps using our custom logger
def market_news_agent(state: Any) -> Dict[str, Any]:
    ticker = getattr(state, "ticker", "")
    if not ticker:
        # Make sure we have a ticker
        logger.error("No ticker for news search")
        return {"news": []}
    logger.info(f"Looking for news about {ticker}")
    try:
        api_key = settings.TAVILY_API_KEY
        if not api_key:
            # Make sure API key is set
            logger.error("TAVILY_API_KEY not set")
            return {"news": []}
        # Search query for Tavily
        search_query = f"{ticker} stock news earnings financial"
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": api_key,
            "query": search_query,
            "search_depth": "basic",
            "include_answer": False,
            "include_images": False,
            "include_raw_content": False,
            "max_results": 10,
            "include_domains": [],
            "exclude_domains": []
        }
        # Tavily API logging
        logger.info(f"[Tavily] Sending news search for '{search_query}' to Tavily API")
        # Call Tavily API for news
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        news_items = []
        results = data.get("results", [])
        logger.info(f"[Tavily] Tavily API returned {len(results)} results for '{search_query}'")
        for item in results:
            title = item.get("title", "").strip()
            snippet = item.get("content", "").strip()
            url = item.get("url", "")
            if title and snippet:
                # Parse and collect news items
                news_items.append({"title": title, "snippet": snippet, "url": url})
        # Log how many news items found
        logger.info(f"Found {len(news_items)} news for {ticker}")
        return {"news": news_items}
    except Exception as e:
        # Handle any errors and log them
        logger.error(f"Error fetching news: {e}")
        return {"news": []}
