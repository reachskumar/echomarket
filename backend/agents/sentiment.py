# Figures out if the news is bullish, bearish, or neutral for this stock

import re
import json
import time
import logging
import openai
from openai import OpenAIError
from backend.config import settings
from backend.agents.logger import log_agent

logger = logging.getLogger(__name__)

openai.api_key = settings.OPENAI_API_KEY
PRIMARY_MODEL = getattr(settings, "OPENAI_MODEL", "gpt-4")
FALLBACK_MODEL = "gpt-3.5-turbo"

MIN_NEWS_ITEMS = 3
MAX_RETRIES = 3
INITIAL_BACKOFF = 1
REQUEST_TIMEOUT = 10

@log_agent("sentiment")  # Logs sentiment analysis
def sentiment_agent(state):
    # Checks news count, builds prompt, and asks OpenAI for sentiment
    news_items = state.news or []
    extracted_content = getattr(state, "extracted_content", [])
    key_insights = getattr(state, "key_insights", [])
    content_quality_score = getattr(state, "content_quality_score", 0)
    
    if len(news_items) < MIN_NEWS_ITEMS:
        logger.warning("Not enough news; defaulting to Neutral.")
        return {"sentiment": "Neutral", "confidence": 0.0}

    logger.info(f"Analyzing sentiment from {len(news_items)} news items (Quality Score: {content_quality_score})...")
    
    # Use extracted content for deeper analysis if available
    if extracted_content:
        logger.info(f"Enhanced analysis using {len(extracted_content)} extracted articles with advanced processing")
        combined = "\n".join(f"- {item['title']}: {item['snippet']}" for item in news_items)
        
        # Add key insights from advanced processing
        if key_insights:
            combined += "\n\nKey Market Insights:"
            for insight in key_insights[:3]:
                combined += f"\n- {insight.get('type', 'insight')}: {insight.get('key_point', '')[:100]}"
        
        # Add extracted content with financial analysis
        for content in extracted_content[:2]:  # Use top 2 extracted articles
            if content.get("content"):
                combined += f"\n\nDetailed Analysis: {content['content'][:400]}..."
                
                # Include financial figures if available
                if content.get("financial_figures"):
                    combined += "\nFinancial Data: " + ", ".join([
                        f"{fig['type']}: {fig['amount']} {fig['unit']}" 
                        for fig in content["financial_figures"][:3]
                    ])
                
                # Include sentiment indicators
                if content.get("sentiment_indicators"):
                    combined += "\nMarket Indicators: " + ", ".join(content["sentiment_indicators"][:3])
                
                # Include key quotes
                if content.get("key_quotes"):
                    combined += f"\nKey Quote: {content['key_quotes'][0][:150]}..."
    else:
        combined = "\n".join(f"- {item['title']}: {item['snippet']}" for item in news_items)
    
    # Build the enhanced prompt for OpenAI
    analysis_type = "advanced" if extracted_content else "basic"
    quality_score = content_quality_score or 0
    confidence_boost = "high" if quality_score > 70 else "moderate" if quality_score > 40 else "low"
    user_prompt = (
        f"Given the following financial news analysis ({analysis_type} extraction, {confidence_boost} quality sources), "
        "provide an overall sentiment: Bullish, Bearish, or Neutral. Also give a confidence score between 0 and 1."
        "\n\n"
        f"{combined}\n\n"
        "Consider financial figures, executive statements, market indicators, and source quality in your analysis. "
        "Respond ONLY with JSON in the format: {\"sentiment\": \"Bullish\", \"confidence\": 0.85}."
    )
    messages = [
        {"role": "system", "content": "You are a financial-market sentiment analysis assistant."},
        {"role": "user", "content": user_prompt}
    ]
    model = PRIMARY_MODEL
    backoff = INITIAL_BACKOFF
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Try up to 3 times, fallback to GPT-3.5 if needed
            resp = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.0,
                max_tokens=64,
                request_timeout=REQUEST_TIMEOUT,
            )
            raw = resp.choices[0].message.content.strip()
            logger.info(f"AI response: {raw}")

            match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            json_text = match.group(0) if match else raw
            data = json.loads(json_text)
            
            if set(data.keys()) <= {"sentiment", "confidence"}:
                sentiment = data.get("sentiment") or "Neutral"
                confidence = float(data.get("confidence") or 0.0)
                logger.info(f"Analysis complete: {sentiment} (confidence: {confidence:.2f})")
                return {"sentiment": sentiment, "confidence": confidence}
            else:
                raise ValueError(f"Unexpected response format: {data.keys()}")
        except (OpenAIError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Attempt {attempt} failed with model {model}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(backoff)
                backoff *= 2
                if attempt == 1:
                    model = FALLBACK_MODEL
                    logger.info(f"Falling back to {model}")
                continue
            logger.error("All retries failed; defaulting to Neutral.")
            return {"sentiment": "Neutral", "confidence": 0.0}
