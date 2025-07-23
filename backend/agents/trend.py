"""
Tavily Trend Agent (Search + Advanced Extract + Crawl + Map)
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests

from backend.config import settings
from backend.agents.logger import log_agent

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
TAVILY_SEARCH_URL  = "https://api.tavily.com/search"
TAVILY_EXTRACT_URL = "https://api.tavily.com/extract"
TAVILY_CRAWL_URL   = "https://api.tavily.com/crawl"
TAVILY_MAP_URL     = "https://api.tavily.com/map"

WINDOW_DAYS = getattr(settings, "PRICE_HISTORY_DAYS", 30)
API_KEY     = settings.TAVILY_API_KEY

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type":  "application/json",
}

# -----------------------------------------------------------------------------
# Regexes
# -----------------------------------------------------------------------------
DATE_ISO_RE   = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
DATE_SLASH_RE = re.compile(r"\b(\d{1,2}/\d{1,2}/(?:\d{2}|\d{4}))\b")
MONEY_RE      = re.compile(r"\$?\s*([0-9]{1,5}(?:,[0-9]{3})*(?:\.\d{1,2})?)")

# -----------------------------------------------------------------------------
# Tavily helpers
# -----------------------------------------------------------------------------
def _tavily_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    try:
        logger.info("[TrendAgent] 🔍 Tavily search for query: %r", query)
        r = requests.post(TAVILY_SEARCH_URL, headers=HEADERS, json={"query": query}, timeout=20)
        r.raise_for_status()
        return r.json().get("results", [])[:max_results]
    except Exception as e:
        logger.error("[TrendAgent] search failed %r: %s", query, e)
        return []

def _tavily_extract(url: str, advanced: bool = True) -> str:
    endpoint = TAVILY_EXTRACT_URL + ("/advanced" if advanced else "")
    logger.info("[TrendAgent] 🧪 Extracting (%s): %s", "advanced" if advanced else "basic", url)
    payload = {
        "urls":           [url],
        "extract_depth":  "advanced" if advanced else "basic",
        "include_images": False,
        "include_favicon": False,
        "format":         "text",
    }
    r = requests.post(endpoint, headers=HEADERS, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    if results := data.get("results"):
        first = results[0]
        return first.get("raw_content") or first.get("content", "") or ""
    return data.get("content", "") or ""

def _tavily_crawl(url: str) -> str:
    try:
        logger.info("[TrendAgent] 🕷️ Crawling: %s", url)
        r = requests.post(TAVILY_CRAWL_URL, headers=HEADERS, json={"url": url}, timeout=30)
        r.raise_for_status()
        return r.json().get("content", "") or ""
    except Exception as e:
        logger.warning("[TrendAgent] crawl failed %s: %s", url, e)
        return ""

def _tavily_map(url: str) -> str:
    try:
        logger.info("[TrendAgent] 🗺️ Mapping table data from: %s", url)
        r = requests.post(TAVILY_MAP_URL, headers=HEADERS, json={"url": url}, timeout=30)
        r.raise_for_status()
        tables = r.json().get("results", [])
        body = ""
        for tbl in tables:
            for row in tbl.get("rows", []):
                body += " ".join(row) + "\n"
        return body
    except Exception as e:
        logger.warning("[TrendAgent] map failed %s: %s", url, e)
        return ""

# -----------------------------------------------------------------------------
# Parsing utilities
# -----------------------------------------------------------------------------
def _norm_date(text: str) -> str | None:
    if m := DATE_ISO_RE.fullmatch(text):
        return text
    if m := DATE_SLASH_RE.fullmatch(text):
        mm, dd, yy = text.split("/")
        mm, dd = mm.zfill(2), dd.zfill(2)
        if len(yy) == 2:
            yy = "20" + yy
        return f"{yy}-{mm}-{dd}"
    return None

def _pick_price(tokens: List[str]) -> float | None:
    for t in tokens:
        clean = t.replace(",", "").lstrip("$")
        if "." in clean:
            try:
                return float(clean)
            except ValueError:
                continue
    for t in tokens:
        clean = t.replace(",", "").lstrip("$")
        try:
            v = float(clean)
            if v < 1000:
                return v
        except ValueError:
            continue
    return None

def _parse_dates_prices(text: str) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for line in text.splitlines():
        dm = DATE_ISO_RE.search(line) or DATE_SLASH_RE.search(line)
        if not dm:
            continue
        if not (sd := _norm_date(dm.group(1))):
            continue
        after = line[dm.end():]
        toks  = MONEY_RE.findall(after) or MONEY_RE.findall(line)
        if price := _pick_price(toks):
            out[sd] = price
    return out

def _filter_series(series: Dict[str, float], days: int) -> Dict[str, float]:
    cutoff = datetime.utcnow().date() - timedelta(days=days)
    return {
        d: p
        for d, p in sorted(series.items())
        if datetime.strptime(d, "%Y-%m-%d").date() >= cutoff
    }

# -----------------------------------------------------------------------------
# Public agent
# -----------------------------------------------------------------------------
@log_agent("trend")
def trend_agent(state: Any) -> Dict[str, Dict[str, float]]:
    """
    Tavily TrendAgent (Search + Extract + Crawl + Map).
    """
    ticker = getattr(state, "ticker", "").upper()
    if not ticker:
        raise ValueError("TrendAgent: no ticker provided")
    if not API_KEY:
        logger.error("TrendAgent: missing Tavily API key")
        return {"prices": {}}

    logger.info("[TrendAgent] 🧭 Starting trend detection for ticker: %s", ticker)

    queries   = [
        f"{ticker} historical closing prices last {WINDOW_DAYS} days",
        f"{ticker} daily close price history table",
        f"{ticker} stock price history",
    ]
    aggregate = {}
    seen_urls = set()

    for q in queries:
        for r in _tavily_search(q):
            url = r.get("url")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            text = ""
            try:
                text = _tavily_extract(url, advanced=True)
            except:
                try:
                    text = _tavily_extract(url, advanced=False)
                except:
                    text = _tavily_crawl(url)

            if not text:
                text = _tavily_map(url)
            if not text:
                logger.warning("[TrendAgent] Skipping empty content from %s", url)
                continue

            parsed = _parse_dates_prices(text)
            logger.info("[TrendAgent] 📅 Parsed %d date-price entries from %s", len(parsed), url)
            for date_str, price in parsed.items():
                aggregate.setdefault(date_str, price)

    prices = _filter_series(aggregate, WINDOW_DAYS)
    logger.info("[TrendAgent] ✅ Final trend series for %s: %d points", ticker, len(prices))
    return {"prices": prices}
