# Checks if the stock is trending up, down, or sideways using price history

import json
import re
import logging
from typing import Any, Dict
import openai
from openai import OpenAIError
from backend.config import settings
from backend.agents.logger import log_agent

logger = logging.getLogger(__name__)

openai.api_key = settings.OPENAI_API_KEY
PRIMARY_MODEL = getattr(settings, "OPENAI_MODEL", "gpt-4")
FALLBACK_MODEL = "gpt-3.5-turbo"

@log_agent("trend")  # Logs trend analysis
def trend_agent(state: Any) -> Dict[str, Any]:
    prices = getattr(state, "prices", {})
    current_price = getattr(state, "price", None)
    ticker = getattr(state, "ticker", "")
    if not prices:
        # If no price data, can't analyze trend
        logger.warning("No price data for trend analysis")
        return {"trend": {"direction": "Unknown", "strength": "N/A", "confidence": 0.0}}
    logger.info(f"Analyzing price trends for {ticker} using {len(prices)} data points")
    try:
        # Build a summary of price history for OpenAI
        price_summary = f"Current price: ${current_price:.2f}\n" if current_price else ""
        price_summary += "Recent price history:\n"
        sorted_prices = sorted(prices.items())
        for date, price in sorted_prices:
            price_summary += f"  {date}: ${price:.2f}\n"
        # Ask OpenAI to analyze the trend
        prompt = f"""
        Analyze the following stock price data and provide a trend analysis:

        {price_summary}

        Please provide your analysis in JSON format with these fields:
        - direction: "Uptrend", "Downtrend", or "Sideways"
        - strength: "Strong", "Moderate", or "Weak"
        - confidence: a number between 0 and 1
        - risk: "High", "Medium", or "Low"
        - timeframe: brief description of the timeframe analyzed
        - keyFactors: array of 2-3 key observations about the price movement
        - summary: 1-2 sentence summary of the trend

        Respond ONLY with valid JSON.
        """
        messages = [
            {"role": "system", "content": "You are a financial market trend analyst. Analyze price data objectively and provide clear, actionable insights."},
            {"role": "user", "content": prompt}
        ]
        model = PRIMARY_MODEL
        for attempt in range(2):
            try:
                # Ask OpenAI for trend analysis (fallback to GPT-3.5 if needed)
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=512,
                    timeout=15,
                )
                raw_response = response.choices[0].message.content.strip()
                logger.info(f"OpenAI response: {raw_response}")
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                if json_match:
                    trend_data = json.loads(json_match.group())
                    required_fields = ["direction", "strength", "confidence"]
                    if all(field in trend_data for field in required_fields):
                        logger.info(f"Trend analysis complete: {trend_data.get('strength', '')} {trend_data.get('direction', '')} trend")
                        return {"trend": trend_data}
                    else:
                        raise ValueError(f"Missing required fields in response: {trend_data.keys()}")
                else:
                    raise ValueError("No JSON found in OpenAI response")
            except (OpenAIError, json.JSONDecodeError, ValueError) as e:
                # Fallback to GPT-3.5 if needed
                logger.error(f"Attempt {attempt+1} failed with model {model}: {e}")
                if attempt == 0:
                    model = FALLBACK_MODEL
                    logger.info(f"Falling back to {model}")
                    continue
                break
        # If OpenAI fails, do a basic trend check
        logger.warning("OpenAI analysis failed, providing basic trend assessment")
        return _basic_trend_analysis(prices, current_price)
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in trend analysis: {e}")
        return {"trend": {"direction": "Unknown", "strength": "N/A", "confidence": 0.0}}

# Simple trend check if OpenAI is unavailable
def _basic_trend_analysis(prices: Dict[str, float], current_price: float) -> Dict[str, Any]:
    # Simple trend check if OpenAI is unavailable
    if not prices or len(prices) < 2:
        return {"trend": {"direction": "Unknown", "strength": "N/A", "confidence": 0.0}}
    sorted_prices = sorted(prices.items())
    first_price = sorted_prices[0][1]
    last_price = sorted_prices[-1][1]
    # Calculate percent change
    price_change_percent = ((last_price - first_price) / first_price) * 100
    # Decide direction and strength
    if price_change_percent > 2:
        direction = "Uptrend"
    elif price_change_percent < -2:
        direction = "Downtrend"
    else:
        direction = "Sideways"
    strength = "Moderate" if abs(price_change_percent) > 5 else "Weak"
    # Return basic trend summary
    return {
        "trend": {
            "direction": direction,
            "strength": strength,
            "confidence": 0.7,
            "summary": f"Basic analysis shows {direction.lower()} movement with {price_change_percent:.1f}% change"
        }
    }
