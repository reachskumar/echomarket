import logging
import requests
import re
from datetime import datetime
from typing import Any, Dict, List
from backend.config import settings
from backend.agents.logger import log_agent

logger = logging.getLogger(__name__)

@log_agent("market_news") # Logs news search+extract+crawl+map using our logger
def market_news_agent(state: Any) -> Dict[str, Any]:
    ticker = getattr(state, "ticker", "")
    api_key = settings.TAVILY_API_KEY
    
    if not ticker or not api_key:
        logger.error(f"Missing ticker ({bool(ticker)}) or API key ({bool(api_key)})")
        return {"news": [], "extracted_content": [], "key_insights": [], "structured_data": {}, "content_quality_score": 0}
    
    try:
        logger.info(f"[Tavily] Starting all 4 features for {ticker}: Search + Extract + Crawl + Map")
        
        # Step 1: SEARCH For News
        logger.info(f"[Tavily] Step 1 - SEARCH: Basic news for {ticker}")
        search_news = _tavily_api_call(api_key, {
            "query": f"{ticker} stock news earnings financial",
            "search_depth": "basic",
            "max_results": 6
        }, "SEARCH")
        
        # Step 2: EXTRACT - Max content extraction from top articles
        logger.info(f"[Tavily] Step 2 - EXTRACT: Full content from top {min(3, len(search_news))} articles")
        extracted = _extract_content(api_key, search_news[:3])
        
        # Step 3: CRAWL - Advanced search
        logger.info(f"[Tavily] Feature 3 - CRAWL: Advanced search ")
        crawl_news = _tavily_api_call(api_key, {
            "query": f"{ticker} financial analysis market outlook", 
            "search_depth": "advanced",
            "max_results": 4,
            "include_raw_content": True,
            "include_domains": ["bloomberg.com", "reuters.com", "wsj.com", "cnbc.com"],
            "exclude_domains": ["reddit.com", "twitter.com"]
        }, "CRAWL")
        
        # Step 4: MAP - Structured financial data mapping
        logger.info(f"[Tavily] Step 4 - MAP: Structured financial data mapping")
        mapped = _map_financial_data(api_key, ticker)
        
        # Process everything
        result = _process_results(search_news + crawl_news, extracted, mapped)
        logger.info(f"[Tavily]  ALL 4 FEATURES COMPLETE: {len(result['news'])} articles, {len(result['key_insights'])} insights, quality={result['quality_score']}")
        return result
        
    except Exception as e:
        logger.error(f"[Tavily] CRITICAL: Multi-feature extraction failed for {ticker}: {e}")
        import traceback
        logger.error(f"[Tavily] Stack trace: {traceback.format_exc()}")
        return {"news": [], "extracted_content": [], "key_insights": [], "structured_data": {}, "content_quality_score": 0}
        

def _tavily_api_call(api_key: str, params: Dict, feature_name: str = "API") -> List[Dict]:
    """Unified Tavily API caller with detailed logging"""
    query = params.get('query', 'unknown')
    logger.info(f"[Tavily] {feature_name} - Sending request: '{query}' with depth='{params.get('search_depth', 'basic')}'")
    
    try:
        response = requests.post("https://api.tavily.com/search", 
                               json={"api_key": api_key, **params}, timeout=20)
        response.raise_for_status()
        
        results = response.json().get("results", [])
        logger.info(f"[Tavily] {feature_name} - API returned {len(results)} results")
        
        processed_results = []
        for r in results:
            processed_results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("content", "")[:200] + "...",
                "raw_content": r.get("raw_content", ""),
                "score": r.get("score", 0),
                "source": f"tavily_{params.get('search_depth', 'search')}"
            })
        
        logger.info(f"[Tavily] {feature_name} - Processed {len(processed_results)} valid items")
        return processed_results
        
    except requests.exceptions.Timeout:
        logger.error(f"[Tavily] {feature_name} - API call TIMEOUT after 20s")
        return []
    except requests.exceptions.HTTPError as e:
        logger.error(f"[Tavily] {feature_name} - HTTP ERROR: {e.response.status_code}")
        return []
    except Exception as e:
        logger.error(f"[Tavily] {feature_name} - UNEXPECTED ERROR: {e}")
        return []

def _extract_content(api_key: str, news_items: List[Dict]) -> List[Dict]:
    """ EXTRACT - Advanced content extraction with detailed logging"""
    urls = [item["url"] for item in news_items if item.get("url")][:3]
    if not urls:
        logger.warning("[Tavily] EXTRACT - No URLs to extract from")
        return []
    
    logger.info(f"[Tavily] EXTRACT - Requesting full content from {len(urls)} URLs")
    
    try:
        response = requests.post("https://api.tavily.com/extract", json={
            "api_key": api_key,
            "urls": urls,
            "include_raw_content": True
        }, timeout=25)
        response.raise_for_status()
        
        api_results = response.json().get("results", [])
        logger.info(f"[Tavily] EXTRACT - API returned {len(api_results)} extracted articles")
        
        results = []
        for r in api_results:
            content = r.get("content", "")
            if content:
                analysis = _quick_analysis(content)
                results.append({
                    "url": r.get("url", ""),
                    "title": r.get("title", ""),
                    "content": content,
                    "word_count": len(content.split()),
                    **analysis,  # Financial analysis
                    "source": "tavily_extract"
                })
                logger.debug(f"[Tavily] EXTRACT - Analyzed article: {len(content)} chars, {len(analysis.get('financial_figures', []))} figures")
        
        logger.info(f"[Tavily] EXTRACT - Successfully processed {len(results)} articles with financial analysis")
        return results
        
    except requests.exceptions.Timeout:
        logger.error("[Tavily] EXTRACT - TIMEOUT after 25s")
        return []
    except Exception as e:
        logger.error(f"[Tavily] EXTRACT - ERROR: {e}")
        return []

def _map_financial_data(api_key: str, ticker: str) -> Dict:
    """MAP - Structured financial data mapping with detailed logging"""
    query = f"{ticker} stock price earnings revenue financial metrics"
    logger.info(f"[Tavily] MAP - Requesting structured data: '{query}'")
    
    try:
        response = requests.post("https://api.tavily.com/search", json={
            "api_key": api_key,
            "query": query,
            "search_depth": "advanced", 
            "include_answer": True, 
            "max_results": 3,
            "include_domains": ["finance.yahoo.com", "marketwatch.com", "bloomberg.com"]
        }, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        answer = data.get("answer", "")
        results_count = len(data.get("results", []))
        
        logger.info(f"[Tavily] MAP - API returned structured answer ({len(answer)} chars) from {results_count} sources")
        
        mapped = {
            "ticker": ticker,
            "answer": answer,
            "follow_up_questions": data.get("follow_up_questions", []),
            "sources": [r.get("url", "") for r in data.get("results", [])],
            "mapped_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"[Tavily] MAP - Successfully mapped financial data with {len(mapped['sources'])} sources")
        return mapped
        
    except requests.exceptions.Timeout:
        logger.error("[Tavily] MAP - TIMEOUT after 15s")
        return {}
    except Exception as e:
        logger.error(f"[Tavily] MAP - ERROR: {e}")
        return {}

def _quick_analysis(content: str) -> Dict:
    """Lightning-fast financial content analysis"""
    if not content:
        return {"financial_figures": [], "key_quotes": [], "sentiment_indicators": []}
    
    # Extract key financial data with combined regex
    figures = []
    
    # Money amounts: $X billion/million in revenue/earnings
    for match in re.findall(r'\$(\d+(?:\.\d+)?)\s*(billion|million|B|M)?\s*(?:in\s*)?(revenue|sales|earnings|profit)', content, re.IGNORECASE)[:3]:
        figures.append(f"{match[2]}: ${match[0]} {match[1] or 'unknown'}")
    
    # Percentages: X% increase/decrease 
    for match in re.findall(r'(\d+(?:\.\d+)?)%\s*(?:increase|decrease|growth|decline)', content, re.IGNORECASE)[:2]:
        figures.append(f"Change: {match}%")
    
    # Quick quotes extraction
    quotes = re.findall(r'"([^"]*(?:revenue|earnings|CEO|outlook|growth)[^"]*)"', content, re.IGNORECASE)[:2]
    
    # Sentiment words
    positive = len(re.findall(r'\b(strong|growth|beat|surge|bullish|excellent)\b', content, re.IGNORECASE))
    negative = len(re.findall(r'\b(weak|decline|miss|bearish|poor|disappointing)\b', content, re.IGNORECASE))
    sentiment = ["POSITIVE" if positive > negative else "NEGATIVE" if negative > positive else "NEUTRAL"]
    
    return {
        "financial_figures": figures,
        "key_quotes": quotes,
        "sentiment_indicators": sentiment
    }

def _process_results(all_news: List[Dict], extracted: List[Dict], mapped: Dict) -> Dict:
    """Ultra-fast processing and insights extraction"""
    
    # Deduplicate by URL and score
    seen_urls = set()
    unique_news = []
    
    for item in all_news:
        url = item.get('url', '')
        if url and url not in seen_urls:
            # Quick relevance scoring
            text = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
            financial_words = sum(1 for word in ['stock', 'earnings', 'revenue', 'financial'] if word in text)
            premium_source = any(domain in url for domain in ['bloomberg.com', 'reuters.com', 'wsj.com'])
            
            item['overall_score'] = (financial_words * 15) + (30 if premium_source else 0) + (item.get('score', 0) * 20)
            unique_news.append(item)
            seen_urls.add(url)
    
    # Sort by score
    unique_news.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
    
    # Quick insights extraction
    insights = []
    
    # Top article insight
    if unique_news:
        insights.append({
            "type": "top_news",
            "key_point": unique_news[0].get('snippet', '')[:80] + "..."
        })
    
    # Key quote from extracted content
    for content in extracted:
        if content.get('key_quotes'):
            insights.append({
                "type": "key_quote", 
                "key_point": content['key_quotes'][0][:80] + "..."
            })
            break
    
    # Structured answer from mapping
    if mapped.get('answer'):
        insights.append({
            "type": "structured_answer",
            "key_point": mapped['answer'][:80] + "..."
        })
    
    # Calculate average quality
    scores = [item.get('overall_score', 0) for item in unique_news]
    avg_quality = round(sum(scores) / len(scores), 1) if scores else 0
    
    logger.info(f"[Tavily] PROCESSING - Unique articles: {len(unique_news)}, Insights: {len(insights)}, Avg quality: {avg_quality}")
    
    return {
        "news": unique_news[:8],  # Top 8 articles
        "extracted_content": extracted,
        "key_insights": insights,
        "structured_data": mapped,
        "quality_score": avg_quality
    }

def _empty_result() -> Dict[str, Any]:
    """Return empty result structure"""
    return {
        "news": [],
        "extracted_content": [],
        "key_insights": [],
        "structured_data": {},
        "quality_score": 0.0
    }
