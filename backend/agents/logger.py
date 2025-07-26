# Logs and saves analysis results to MongoDB

import logging
from datetime import datetime
from uuid import uuid4
from functools import wraps
from typing import Any, Dict, Callable
from pymongo import MongoClient
from backend.config import settings
from openai import OpenAIError

logger = logging.getLogger(__name__)

# Set up MongoDB connection
try:
    mongo = MongoClient(settings.MONGODB_URI)[settings.MONGO_DB_NAME][settings.MONGO_COLLECTION]
    logger.info("[Logger] Connected to MongoDB for analysis logging")
except Exception as e:
    # If connection fails, log error and set mongo to None
    logger.error(f"[Logger] Failed to connect to MongoDB: {e}")
    mongo = None

def log_agent(agent_name: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(state: Any) -> Dict[str, Any]:
            logger.info(f"[{agent_name}] Starting analysis step")
            result = func(state)
            logger.info(f"[{agent_name}] Completed analysis step")
            return result
        return wrapper
    return decorator

@log_agent("logger")  # Logs and saves analysis results to MongoDB
def logger_agent(state: Any) -> Dict[str, Any]:
    # Skips if MongoDB isn't available
    if mongo is None:
        logger.warning("[LoggerAgent] MongoDB not available, skipping result storage")
        return {"log_id": None}
    try:
        ticker = getattr(state, "ticker", "")
         # Build the analysis record
        analysis_record = {
            "query_id": str(uuid4()),
            "ticker": ticker,
            "timestamp": datetime.utcnow(),
            "price": getattr(state, "price", None),
            "prices": getattr(state, "prices", {}),
            "sentiment": getattr(state, "sentiment", None),
            "confidence": getattr(state, "confidence", None),
            "trend": getattr(state, "trend", {}),
            "recommendation": getattr(state, "recommendation", None),
            "insight": getattr(state, "insight", None),
            "summary": getattr(state, "summary", None),
            "news": getattr(state, "news", []),
            "extracted_content": getattr(state, "extracted_content", []),  # Full content
            "key_insights": getattr(state, "key_insights", []),  # Advanced insights
            "structured_data": getattr(state, "structured_data", {}),  # Mapped financial data
            "content_quality_score": getattr(state, "content_quality_score", None),  # Quality metrics
            "chart_url": getattr(state, "chart_url", None)
        }
        # Save to MongoDB
        result = mongo.insert_one(analysis_record)
        log_id = str(result.inserted_id)
        logger.info(f"[LoggerAgent] Saved analysis for {ticker} with ID {log_id}")
        return {"log_id": log_id}
    except Exception as e:
        # If saving fails, just return log_id: None
        logger.error(f"[LoggerAgent] Failed to save analysis results: {e}")
        return {"log_id": None}
