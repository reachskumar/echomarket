"""
Logger and logging‐decorator for EchoMarket agents.
"""
import logging
from functools import wraps
from typing import Any, Dict
from datetime import datetime

from backend.config import settings

logger = logging.getLogger("echomarket.agents")

def log_agent(name: str):
    """Decorator to log an agent’s inputs and outputs."""
    def decorator(fn):
        @wraps(fn)
        def wrapped(state):
            logger.info(
                f"▶ {name}: input = {{"
                f"ticker={getattr(state, 'ticker', '')!r}, "
                f"news_count={len(getattr(state, 'news', []))}, "
                f"sentiment={getattr(state, 'sentiment', None)!r}, "
                f"prices_count={len(getattr(state, 'prices', {}))}"
                f"}}"
            )
            result = fn(state)
            logger.info(f"◀ {name}: output = {result}")
            return result
        return wrapped
    return decorator

# -----------------------------------------------------------------------------
# LoggerAgent: persist pipeline run to MongoDB if configured; else no‐op.
# -----------------------------------------------------------------------------
try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None  # no pymongo => no persistence

_logs = None
if MongoClient and settings.MONGODB_URI:
    try:
        _client = MongoClient(settings.MONGODB_URI)
        _db = _client[settings.MONGODB_DB_NAME or "echomarket"]
        _logs = _db["echomarket_logs"]
    except Exception as e:
        logger.error("[LoggerAgent] Mongo init failed: %s", e)
        _logs = None

def logger_agent(state: Any) -> Dict[str, str | None]:
    """
    Final agent in pipeline: writes the entire GraphState to MongoDB.
    Returns {"log_id": <inserted_id>}, or {"log_id": None} on no‐op/failure.
    """
    if _logs is None:
        return {"log_id": None}


    doc = {
        "timestamp":      datetime.utcnow(),
        "ticker":         getattr(state, "ticker", None),
        "news":           getattr(state, "news", None),
        "sentiment":      getattr(state, "sentiment", None),
        "confidence":     getattr(state, "confidence", None),
        "prices":         getattr(state, "prices", None),
        "recommendation": getattr(state, "recommendation", None),
        "insight":        getattr(state, "insight", None),
        "summary":        getattr(state, "summary", None),
    }
    try:
        res = _logs.insert_one(doc)
        return {"log_id": str(res.inserted_id)}
    except Exception as e:
        logger.error("[LoggerAgent] insert failed: %s", e)
        return {"log_id": None}
