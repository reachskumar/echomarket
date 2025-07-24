# Uses OpenAI to write a summary of all the analysis

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

@log_agent("summary")  # Logs summary
def summary_agent(state: Any) -> Dict[str, Any]:
    # Gathers all analysis, builds prompt, and asks OpenAI for a summary
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
    recommendation = getattr(state, "recommendation", "Hold")
    insight = getattr(state, "insight", "")
    news = getattr(state, "news", [])
    logger.info(f"Creating final summary for {ticker}")
    try:
        price_str = f"${current_price:.2f}" if isinstance(current_price, (int, float)) and current_price is not None else "price data unavailable"
        analysis_context = f"""
        Stock Analysis for {ticker}:
        
        Current Price: {price_str}
        
        News Sentiment: {sentiment} (confidence: {confidence:.2f})
        
        Price Trend: 
        - Direction: {trend.get('direction', 'Unknown')}
        - Strength: {trend.get('strength', 'N/A')}
        - Risk Level: {trend.get('risk', 'Unknown')}
        - Trend Summary: {trend.get('summary', 'No trend data available')}
        
        AI Recommendation: {recommendation}
        Reasoning: {insight}
        
        Key News Headlines ({len(news)} articles found):
        """
        for i, article in enumerate(news[:5]):
            analysis_context += f"  • {article.get('title', 'No title')}\n"
        # Ask OpenAI to write a summary
        prompt = f"""
        Create a comprehensive, easy-to-understand investment summary based on this analysis:

        {analysis_context}

        Write a summary that:
        1. Explains the current situation with this stock in plain English
        2. Summarizes what the data tells us about recent performance and sentiment
        3. Explains the recommendation and reasoning
        4. Mentions any important risks or limitations
        5. Is written for someone who isn't a financial expert

        Keep it informative but accessible. Aim for 2-3 paragraphs.
        """
        messages = [
            {
                "role": "system", 
                "content": "You are a financial analyst who excels at explaining complex market analysis in simple, clear language. Write for a general audience."
            },
            {"role": "user", "content": prompt}
        ]
        model = PRIMARY_MODEL
        for attempt in range(2):
            try:
                # Ask OpenAI to write a summary (fallback to GPT-3.5 if needed)
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=800,
                    timeout=15,
                )
                summary_text = response.choices[0].message.content.strip()
                logger.info(f"Generated summary ({len(summary_text)} characters)")
                chart_url = f"https://example.com/chart/{ticker}"
                return {
                    "summary": summary_text,
                    "chart_url": chart_url
                }
            except OpenAIError as e:
                # Fallback to GPT-3.5 if needed
                logger.error(f"Attempt {attempt+1} failed with model {model}: {e}")
                if attempt == 0:
                    model = FALLBACK_MODEL
                    logger.info(f"Falling back to {model}")
                    continue
                break
        # If OpenAI fails, use a simple template summary
        logger.warning("OpenAI summary failed, creating template summary")
        return _create_template_summary(ticker, current_price, sentiment, recommendation, insight, len(news))
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error creating summary: {e}")
        return _create_template_summary(ticker, current_price, sentiment, recommendation, insight, len(news))

# Basic summary if OpenAI is unavailable
def _create_template_summary(ticker: str, price: float, sentiment: str, recommendation: str, insight: str, news_count: int) -> Dict[str, Any]:
    price_text = f"${price:.2f}" if price else "price data unavailable"
    # Build a fallback summary with available data
    summary = f"""
    Analysis Summary for {ticker}:
    
    Current trading price is {price_text}. Based on analysis of {news_count} recent news articles, 
    the overall market sentiment appears to be {sentiment.lower()}. 
    
    Our recommendation is to {recommendation.lower()} this stock. {insight}
    
    Please note that this analysis is based on limited data and should not be used as the sole 
    basis for investment decisions. Always conduct additional research and consider consulting 
    with a financial advisor.
    """
    return {
        "summary": summary.strip(),
        "chart_url": f"https://example.com/chart/{ticker}"
    }
