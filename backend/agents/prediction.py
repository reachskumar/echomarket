# Uses OpenAI to make a buy/hold/sell recommendation based on all analysis

import json
import re
import logging
from typing import Any, Dict
import openai
from openai import OpenAIError
from backend.config import settings
from backend.agents.logger import log_agent
from openai import OpenAIError

logger = logging.getLogger(__name__)

openai.api_key = settings.OPENAI_API_KEY
PRIMARY_MODEL = getattr(settings, "OPENAI_MODEL", "gpt-4")
FALLBACK_MODEL = "gpt-3.5-turbo"

@log_agent("prediction")  # Logs prediction using custom logger
def prediction_agent(state: Any) -> Dict[str, Any]:
    # Gathers data and asks OpenAI for a recommendation
    ticker = getattr(state, "ticker", "")
    current_price = getattr(state, "price", None)
    prices = getattr(state, "prices", {})
    # Use latest price from prices if needed
    if (not isinstance(current_price, (int, float)) or current_price is None or current_price == 0) and prices:
        try:
            current_price = prices[max(prices.keys())]
        except Exception:
            try:
                current_price = list(prices.values())[-1]
            except Exception:
                current_price = None
    sentiment = getattr(state, "sentiment", "Neutral")
    confidence = getattr(state, "confidence", 0.0)
    trend = getattr(state, "trend", {})
    news = getattr(state, "news", [])
    logger.info(f"Generating investment recommendation for {ticker}")
    try:
        # Build a summary of all analysis for OpenAI
        price_str = f"${current_price:.2f}" if isinstance(current_price, (int, float)) and current_price is not None else "N/A"
        analysis_summary = f"""
        Stock: {ticker}
        Current Price: {price_str} (if available)
        
        Sentiment Analysis:
        - Overall sentiment: {sentiment}
        - Confidence level: {confidence:.2f}
        
        Trend Analysis:
        - Direction: {trend.get('direction', 'Unknown')}
        - Strength: {trend.get('strength', 'N/A')}
        - Risk level: {trend.get('risk', 'Unknown')}
        - Summary: {trend.get('summary', 'No trend summary available')}
        
        Recent News Headlines:
        """
        for i, article in enumerate(news[:3]):
            analysis_summary += f"  {i+1}. {article.get('title', 'No title')}\n"
        if len(news) > 3:
            analysis_summary += f"  ... and {len(news) - 3} more articles\n"
        # Ask OpenAI for a recommendation
        prompt = f"""
        Based on the following stock analysis, provide an investment recommendation:

        {analysis_summary}

        Please provide your recommendation in JSON format with these fields:
        - recommendation: "Buy", "Hold", or "Sell"
        - confidence: a number between 0 and 1 indicating how confident you are
        - reasoning: 2-3 sentences explaining your recommendation
        - keyFactors: array of 2-3 main factors that influenced your decision
        - riskLevel: "Low", "Medium", or "High"
        - timeHorizon: suggested investment timeframe (e.g., "Short-term", "Medium-term", "Long-term")

        Consider both the quantitative data (price trends) and qualitative factors (news sentiment).
        Be conservative and highlight any risks or uncertainties.

        Respond ONLY with valid JSON.
        """
        messages = [
            {
                "role": "system", 
                "content": "You are a conservative financial advisor. Provide balanced investment recommendations based on available data. Always disclose limitations and risks."
            },
            {"role": "user", "content": prompt}
        ]
        model = PRIMARY_MODEL
        for attempt in range(2):
            try:
                # Ask OpenAI for a recommendation (fallback to GPT-3.5 if needed)
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=0.2,
                    max_tokens=512,
                    timeout=15,
                )
                raw_response = response.choices[0].message.content.strip()
                logger.info(f"OpenAI response: {raw_response}")
                # Extract and parse JSON from OpenAI response
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                if json_match:
                    prediction_data = json.loads(json_match.group())
                    required_fields = ["recommendation", "confidence", "reasoning"]
                    if all(field in prediction_data for field in required_fields):
                        recommendation = prediction_data["recommendation"]
                        logger.info(f"Generated recommendation: {recommendation}")
                        return {
                            "recommendation": recommendation,
                            "insight": prediction_data.get("reasoning", "No reasoning provided"),
                            "prediction_data": prediction_data
                        }
                    else:
                        raise ValueError(f"Missing required fields in response: {prediction_data.keys()}")
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
        # If OpenAI fails, use a conservative rule-based fallback
        logger.warning("OpenAI recommendation failed, providing conservative fallback")
        return _conservative_fallback_recommendation(sentiment, trend)
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error generating recommendation: {e}")
        return {"recommendation": "Hold", "insight": "Unable to generate recommendation due to analysis error"}

# Simple fallback: Hold unless signals are very clear
def _conservative_fallback_recommendation(sentiment: str, trend: Dict[str, Any]) -> Dict[str, Any]:
    if sentiment == "Bullish" and trend.get("direction") == "Uptrend":
        recommendation = "Hold"
        reasoning = "Positive sentiment and upward trend detected, but limited analysis available"
    elif sentiment == "Bearish" and trend.get("direction") == "Downtrend":
        recommendation = "Hold"
        reasoning = "Negative sentiment and downward trend detected, consider careful monitoring"
    else:
        recommendation = "Hold"
        reasoning = "Mixed or unclear signals from available data"
    # Return fallback recommendation
    return {
        "recommendation": recommendation,
        "insight": reasoning,
        "prediction_data": {
            "recommendation": recommendation,
            "confidence": 0.5,
            "reasoning": reasoning,
            "riskLevel": "Medium"
        }
    }
