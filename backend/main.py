# Main FastAPI server for EchoMarket – wires up all the analysis agents and API routes

# Set up imports and app config

import io, csv, re, os
from fpdf import FPDF
import anyio
import uvicorn
from datetime import datetime
from uuid import uuid4
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import requests


app = FastAPI(title="EchoMarket API", version="0.1.0")

# Allow frontend to make requests from different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Basic logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

# Load environment variables from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

# Connect to MongoDB for storing analysis results
try:
    mongo = MongoClient(MONGO_URI)[MONGO_DB][MONGO_COLLECTION]
    logging.info("[MONGO] Connected to MongoDB Atlas successfully.")
except Exception as e:
    logging.error(f"[MONGO] Connection failed: {e}")
    raise

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")



# Import the analysis workflow system
from langgraph.graph import StateGraph

# Import our analysis agents - each one handles a specific part of the analysis
from backend.agents.price import price_agent
from backend.agents.market_news import market_news_agent
from backend.agents.sentiment import sentiment_agent
from backend.agents.trend import trend_agent
from backend.agents.prediction import prediction_agent
from backend.agents.summary import summary_agent
from backend.agents.logger import logger_agent

# Data models for API requests and responses

class GraphState(BaseModel):
    """Data that gets passed between analysis steps"""
    ticker: str
    news: List[Dict[str, Any]] = []
    extracted_content: List[Dict[str, Any]] = []  # Full article content from Tavily extract
    key_insights: List[Dict[str, Any]] = []  # Key insights from advanced processing
    structured_data: Dict[str, Any] = {}  # Mapped financial data
    content_quality_score: Optional[float] = None  # Overall content quality
    sentiment: Optional[str] = None
    confidence: Optional[float] = None
    prices: Dict[str, float] = {}
    trend: Optional[Dict[str, Any]] = None
    recommendation: Optional[str] = None
    insight: Optional[str] = None
    summary: Optional[str] = None
    log_id: Optional[str] = None

class QueryRequest(BaseModel):
    """Request format for analysis endpoints"""
    ticker: str

# Set up the analysis workflow - each step feeds into the next

graph = StateGraph(state_schema=GraphState)

# Add each analysis step
graph.add_node("price", price_agent)
graph.add_node("market_news", market_news_agent)
graph.add_node("sentiment", sentiment_agent)
graph.add_node("trend", trend_agent)
graph.add_node("prediction", prediction_agent)
graph.add_node("summary", summary_agent)
graph.add_node("logger", logger_agent)

# Define the order: price -> news -> sentiment -> trend -> prediction -> summary -> log
graph.set_entry_point("price")
graph.add_edge("price", "market_news")
graph.add_edge("market_news", "sentiment")
graph.add_edge("sentiment", "trend")
graph.add_edge("trend", "prediction")
graph.add_edge("prediction", "summary")
graph.add_edge("summary", "logger")
graph.set_finish_point("logger")

# Compile the workflow
compiled_graph = graph.compile()

# Helper function to format results for storage

def normalize_output(query_id, ticker, result):
    return {
        "query_id": query_id,
        "ticker": ticker,
        "timestamp": datetime.utcnow().isoformat(),
        "summary": result.get("summary"),
        "sentiment": result.get("sentiment"),
        "confidence": result.get("confidence"),
        "recommendation": result.get("recommendation"),
        "insight": result.get("insight"),
        "trend": result.get("trend"),  # if available
        "prices": result.get("prices", {}),
        "news": result.get("news", []),
        "extracted_content": result.get("extracted_content", []),  # Full article content
        "key_insights": result.get("key_insights", []),  # Advanced insights
        "structured_data": result.get("structured_data", {}),  # Mapped financial data
        "content_quality_score": result.get("content_quality_score")  # Quality metrics
    }

# Routes

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

# Run full analysis (POST)
@app.post("/analyze", response_model=GraphState, tags=["Analysis"])
async def analyze_post(req: QueryRequest):
    try:
        return await anyio.to_thread.run_sync(compiled_graph.invoke, {"ticker": req.ticker})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run full analysis (GET)
@app.get("/analyze/{ticker}", response_model=GraphState, tags=["Analysis"])
async def analyze_get(ticker: str):
    try:
        return await anyio.to_thread.run_sync(compiled_graph.invoke, {"ticker": ticker})
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
# Detect ticker from company name
@app.get("/detect_ticker", tags=["Ticker"])
async def detect_ticker(company: str):
    from tavily import TavilyClient
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    try:
        response = client.search(query=f"Ticker symbol for {company}", max_results=3)
        for res in response["results"]:
            title = res["title"]
            content = res.get("content", "")
            combined_text = f"{title} {content}"

            # Match patterns for ticker symbols
            match = (
                # Company Name (TICKER) format
                re.search(r'\(([A-Z]{1,5})\)', combined_text) or
                # NYSE: TICKER or NASDAQ: TICKER format
                re.search(r'(?:NYSE|NASDAQ)[:\s]+([A-Z]{1,5})', combined_text) or
                # Ticker: TICKER format
                re.search(r'Ticker[:\s]+([A-Z]{1,5})', combined_text) or
                # Symbol: TICKER format
                re.search(r'Symbol[:\s]+([A-Z]{1,5})', combined_text) or
                # General Motors Corporation (GM) - specific pattern
                re.search(r'Corporation[:\s]+\(([A-Z]{1,5})\)', combined_text) or
                # Look for ticker patterns in content
                re.search(r'\b([A-Z]{1,5})\s+stock', combined_text) or
                re.search(r'stock\s+([A-Z]{1,5})\b', combined_text)
            )

            if match:
                ticker = match.group(1)
                if ticker not in ["NYSE", "NASDAQ", "STOCK", "INC", "CORP", "LLC", "LTD"]:
                    return {"ticker": ticker}

        return {"ticker": None, "message": "Ticker not found in results"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



    
# Root endpoint
@app.get("/")
def root():
    return {"message": "EchoMarket backend running"}
    
# Query handler
@app.post("/query")
async def query_handler(req: QueryRequest):
    query_id = str(uuid4())
    logging.info(f"[QUERY] Started analysis for {req.ticker} | Query ID: {query_id}")

    try:
        result = await anyio.to_thread.run_sync(compiled_graph.invoke, {"ticker": req.ticker})
        normalized = normalize_output(query_id, req.ticker, result)

        mongo.insert_one({**normalized})
        logging.info(f"[MONGO] Inserted query result into MongoDB | Query ID: {query_id}")

        return normalized

    except Exception as e:
        logging.error(f"[ERROR] Query pipeline failed for {req.ticker} | Error: {e}")
        raise HTTPException(status_code=500, detail="Internal error in agent pipeline")

# UI analyzer
@app.get("/ui/analyze/{ticker}", tags=["UI"])
async def analyze_ui(ticker: str):
    try:
        raw_result = await anyio.to_thread.run_sync(compiled_graph.invoke, {"ticker": ticker})

    
        if hasattr(raw_result, "dict"):
            raw_result = raw_result.dict()
        elif not isinstance(raw_result, dict):
            try:
                raw_result = dict(raw_result)
            except Exception:
                raw_result = vars(raw_result)

        # --- Ensure 'price' is set to latest from 'prices' if missing or invalid ---
        prices = raw_result.get("prices", {})
        price = raw_result.get("price", None)
        if (not isinstance(price, (int, float)) or price is None or price == 0) and prices:
            # Get the latest price by date
            try:
                latest_price = prices[max(prices.keys())]
                raw_result["price"] = latest_price
            except Exception:
                try:
                    raw_result["price"] = list(prices.values())[-1]
                except Exception:
                    pass

        summary = raw_result.get("summary", {})
        if isinstance(summary, str):
            summary = {"content": summary}

        sentiment = raw_result.get("sentiment", {})
        if isinstance(sentiment, str):
            sentiment = {"sentiment": sentiment}

        trend = raw_result.get("trend", {})
        if isinstance(trend, str):
            trend = {"trend": trend}

        recommendation = raw_result.get("recommendation", {})
        if isinstance(recommendation, str):
            recommendation = {"recommendation": recommendation}

        price = raw_result.get("price", {})
        if isinstance(price, str):
            price = {"current_price": price}

        news = raw_result.get("market_news", {})
        if isinstance(news, str):
            news = {"headlines": [news]}

        prices = raw_result.get("prices", {})
        latest_price = None
        if isinstance(prices, dict) and prices:
            # Get the latest price by date
            try:
                latest_price = prices[max(prices.keys())]
            except Exception:
                latest_price = list(prices.values())[-1]

        news = raw_result.get("news", [])

        # Ensure real_time_price is present and not overwritten by trend_agent
        real_time_price = raw_result.get("price")
        historical_prices = raw_result.get("prices", {})
        summary_price = raw_result.get("summary", {}).get("price") if isinstance(raw_result.get("summary"), dict) else None
        # Fallback: if real_time_price is missing or invalid, use latest non-zero from prices, then summary agent's price
        def get_latest_nonzero_price(prices_dict):
            if isinstance(prices_dict, dict) and prices_dict:
                sorted_items = sorted(prices_dict.items())
                for date, price in reversed(sorted_items):
                    if isinstance(price, (int, float)) and price > 0:
                        return price
                    # Try to convert string price to float
                    try:
                        fprice = float(price)
                        if fprice > 0:
                            return fprice
                    except Exception:
                        continue
            return None
        # Try to convert real_time_price to float if it's a string
        try:
            if isinstance(real_time_price, str):
                real_time_price = float(real_time_price)
        except Exception:
            real_time_price = None
        if not isinstance(real_time_price, (int, float)) or real_time_price <= 0:
            real_time_price = get_latest_nonzero_price(historical_prices)
        if (real_time_price is None or real_time_price == 0) and summary_price:
            try:
                real_time_price = float(summary_price)
            except Exception:
                real_time_price = "N/A"
        if real_time_price is None:
            real_time_price = "N/A"

        # Ensure confidence is present from sentiment agent
        confidence = raw_result.get("confidence")
        if confidence is None:
            sentiment_obj = raw_result.get("sentiment")
            if isinstance(sentiment_obj, dict):
                confidence = sentiment_obj.get("confidence")
            if confidence is None:
                confidence = 0.0

        response_dict = {
            "symbol": ticker.upper(),
            "price": real_time_price,
            "prices": historical_prices,
            "sentiment": raw_result.get("sentiment", "N/A"),
            "confidence": confidence,
            "summary": raw_result.get("summary", "N/A"),
            "trend": raw_result.get("trend", {}),
            "recommendation": raw_result.get("recommendation", "N/A"),
            "insight": raw_result.get("insight", "N/A"),
            "news": raw_result.get("news", []),
            "chart_url": ""
        }
        print("FINAL RESPONSE:", response_dict)
        return response_dict

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="UI analyzer failed: " + str(e))

    

        return normalized

    except Exception as e:
        logging.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail="Internal error in agent pipeline")
    
# Export query JSON
@app.get("/export/query/{query_id}", tags=["Export"])
def export_query_json(query_id: str):
    record = mongo.find_one({"query_id": query_id})
    if not record:
        raise HTTPException(status_code=404, detail="Query ID not found")
    
    record.pop("_id", None)
    return record

# Test MongoDB connection
@app.get("/test-mongo")
def test_mongo():
    try:
        doc = {"status": "connected from /test-mongo"}
        result = mongo.insert_one(doc)
        return JSONResponse(content={"inserted_id": str(result.inserted_id), "status": "success"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# --- CSV Export----

# Export CSV
@app.get("/analyze/{ticker}/export/csv", tags=["Export"])
async def export_csv(ticker: str):
    result: dict = await anyio.to_thread.run_sync(compiled_graph.invoke, {"ticker": ticker})
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["field", "value"])
    writer.writerow(["ticker", result["ticker"]])
    writer.writerow(["sentiment", result["sentiment"]])
    writer.writerow(["confidence", result["confidence"]])
    writer.writerow(["recommendation", result["recommendation"]])
    writer.writerow(["insight", result["insight"]])
    writer.writerow(["summary", result["summary"]])

    for i, item in enumerate(result["news"], 1):
        writer.writerow([f"news_{i}_title", item["title"]])
        writer.writerow([f"news_{i}_url", item["url"]])
        writer.writerow([f"news_{i}_snippet", item["snippet"]])

    for date, price in result["prices"].items():
        writer.writerow([date, price])

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={ticker}_analysis.csv"},
    )

# ─── PDF Export ───

def safe_text(text):
    clean = re.sub(r'[^\x20-\x7E]+', ' ', str(text))  # strip non-ASCII
    clean = clean.replace("\n", " ").replace("\r", " ")
    return clean[:200]

# Export PDF
@app.get("/analyze/{ticker}/export/pdf", tags=["Export"])
async def export_pdf(ticker: str):
    try:
        # Get analysis data
        raw_result = await anyio.to_thread.run_sync(compiled_graph.invoke, {"ticker": ticker})
        
        # Convert to dict if it's a Pydantic model
        if hasattr(raw_result, "dict"):
            result = raw_result.dict()
        elif not isinstance(raw_result, dict):
            try:
                result = dict(raw_result)
            except Exception:
                result = vars(raw_result)
        else:
            result = raw_result
            
        # Create PDF
        buf = io.BytesIO()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Header
        pdf.cell(0, 10, f"EchoMarket Analysis Report - {ticker}", ln=True)
        pdf.ln(5)

        # Key metrics
        sentiment = safe_text(result.get('sentiment', 'N/A'))
        confidence = safe_text(result.get('confidence', 'N/A'))
        recommendation = safe_text(result.get('recommendation', 'N/A'))
        
        pdf.cell(0, 8, f"Sentiment: {sentiment} (Confidence: {confidence})", ln=True)
        pdf.cell(0, 8, f"Recommendation: {recommendation}", ln=True)
        pdf.ln(3)

        # Insight
        insight = safe_text(result.get('insight', 'No insight available'))
        pdf.multi_cell(0, 8, f"Key Insight: {insight}")
        pdf.ln(3)

        # Summary
        pdf.set_font("Arial", style="B", size=11)
        pdf.cell(0, 8, "Executive Summary:", ln=True)
        pdf.set_font("Arial", size=10)
        summary = safe_text(result.get('summary', 'No summary available'))
        pdf.multi_cell(0, 6, summary)
        pdf.ln(3)

        # News headlines (limit to 5)
        pdf.set_font("Arial", style="B", size=11)
        pdf.cell(0, 8, "Top News Headlines:", ln=True)
        pdf.set_font("Arial", size=10)
        
        news_items = result.get("news", [])
        for idx, item in enumerate(news_items[:5], start=1):
            if isinstance(item, dict):
                title = safe_text(item.get("title", "News item"))
                pdf.multi_cell(0, 6, f"{idx}. {title}")
                pdf.ln(1)

        # Price data
        pdf.ln(3)
        pdf.set_font("Arial", style="B", size=11)
        pdf.cell(0, 8, "Recent Price Data:", ln=True)
        pdf.set_font("Arial", size=10)
        
        prices = result.get("prices", {})
        if prices:
            for date, price in list(prices.items())[-5:]:  # Last 5 days
                pdf.cell(0, 6, f"{date}: ${price}", ln=True)
        else:
            pdf.cell(0, 6, "No price data available", ln=True)

        pdf.output(buf)
        buf.seek(0)
        
        return StreamingResponse(
            buf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={ticker}_analysis.pdf"},
        )
        
    except Exception as e:
        logging.error(f"PDF export failed for {ticker}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

# ─── Root ───

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {"message": "EchoMarket backend running"}

# Start the server when this file is run directly
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

