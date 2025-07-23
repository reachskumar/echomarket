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
from backend.routes import graph
import logging
import requests


app = FastAPI()
app.include_router(graph.router)

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

# Config
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

mongo = MongoClient(MONGO_URI)[MONGO_DB][MONGO_COLLECTION]

try:
    mongo = MongoClient(MONGO_URI)[MONGO_DB][MONGO_COLLECTION]
    logging.info("[MONGO] Connected to MongoDB Atlas successfully.")
except Exception as e:
    logging.error(f"[MONGO] Connection failed: {e}")
    raise

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")



# LangGraph
from langgraph.graph import StateGraph

# Agents
from backend.agents.price import price_agent
from backend.agents.market_news import market_news_agent
from backend.agents.sentiment import sentiment_agent
from backend.agents.trend import trend_agent
from backend.agents.prediction import prediction_agent
from backend.agents.summary import summary_agent
from backend.agents.logger import logger_agent



# FastAPI Setup

app = FastAPI(title="EchoMarket API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

#  Models

class GraphState(BaseModel):
    ticker: str
    news: List[Dict[str, Any]] = []
    sentiment: Optional[str] = None
    confidence: Optional[float] = None
    prices: Dict[str, float] = {}
    recommendation: Optional[str] = None
    insight: Optional[str] = None
    summary: Optional[str] = None
    log_id: Optional[str] = None

class QueryRequest(BaseModel):
    ticker: str

# LangGraph Setup

from langgraph.graph import StateGraph
from backend.agents.market_news import market_news_agent
from backend.agents.sentiment import sentiment_agent
from backend.agents.trend import trend_agent
from backend.agents.prediction import prediction_agent
from backend.agents.summary import summary_agent
from backend.agents.logger import logger_agent

graph = StateGraph(state_schema=GraphState)
graph.add_node("price", price_agent)
graph.add_node("market_news", market_news_agent)
graph.add_node("sentiment", sentiment_agent)
graph.add_node("trend", trend_agent)
graph.add_node("prediction", prediction_agent)
graph.add_node("summary", summary_agent)
graph.add_node("logger", logger_agent)

graph.set_entry_point("price")
graph.add_edge("price", "market_news")
graph.add_edge("market_news", "sentiment")
graph.add_edge("sentiment", "trend")
graph.add_edge("trend", "prediction")
graph.add_edge("prediction", "summary")
graph.add_edge("summary", "logger")

graph.set_finish_point("logger")

compiled_graph = graph.compile()

# Utility: Normalize Output

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
        "news": result.get("news", [])
    }

# Routes

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

@app.post("/analyze", response_model=GraphState, tags=["Analysis"])
async def analyze_post(req: QueryRequest):
    try:
        return await anyio.to_thread.run_sync(compiled_graph.invoke, {"ticker": req.ticker})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze/{ticker}", response_model=GraphState, tags=["Analysis"])
async def analyze_get(ticker: str):
    try:
        return await anyio.to_thread.run_sync(compiled_graph.invoke, {"ticker": ticker})
    except Exception as e:
        import traceback
        traceback.print_exc()  # <-- Add this line
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/detect-ticker", tags=["Utility"])
async def detect_ticker(company: str):
    from tavily import TavilyClient
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    try:
        response = client.search(query=f"Ticker symbol for {company}", max_results=3)
        for res in response["results"]:
            title = res["title"]

            # Match patterns
            match = re.search(r'\(([^)]+)\)', title) or \
                    re.search(r'NSE[:\s]+([A-Z]{2,10})', title) or \
                    re.search(r'Ticker[:\s]+([A-Z]{2,10})', title)

            if match:
                return {"ticker": match.group(1)}

        return {"ticker": None, "message": "Ticker not found in results"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



    
@app.get("/")
def root():
    return {"message": "EchoMarket backend running"}
    
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

@app.get("/ui/analyze/{ticker}", tags=["UI"])
async def analyze_ui(ticker: str):
    try:
        raw_result = await anyio.to_thread.run_sync(compiled_graph.invoke, {"ticker": ticker})

        
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

        return {
            "symbol": ticker.upper(),
            "price": price.get("current_price", "N/A"),
            "sentiment": sentiment.get("sentiment", "N/A"),
            "summary": summary.get("content", "N/A"),
            "trend": trend.get("trend", "N/A"),
            "recommendation": recommendation.get("recommendation", "N/A"),
            "news": news.get("headlines", []),
            "chart_url": price.get("chart_url", "")
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="UI analyzer failed: " + str(e))

    

        return normalized

    except Exception as e:
        logging.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail="Internal error in agent pipeline")
    
@app.get("/export/query/{query_id}", tags=["Export"])
def export_query_json(query_id: str):
    record = mongo.find_one({"query_id": query_id})
    if not record:
        raise HTTPException(status_code=404, detail="Query ID not found")
    
    record.pop("_id", None)
    return record

@app.get("/test-mongo")
def test_mongo():
    try:
        doc = {"status": "connected from /test-mongo"}
        result = mongo.insert_one(doc)
        return JSONResponse(content={"inserted_id": str(result.inserted_id), "status": "success"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# ─── CSV Export ───────────────────────────────────────────────────────────────

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

# ─── PDF Export ───────────────────────────────────────────────────────────────

def safe_text(text):
    clean = re.sub(r'[^\x20-\x7E]+', ' ', str(text))  # strip non-ASCII
    clean = clean.replace("\n", " ").replace("\r", " ")
    return clean[:200]

@app.get("/analyze/{ticker}/export/pdf", tags=["Export"])
async def export_pdf(ticker: str):
    result: dict = await anyio.to_thread.run_sync(compiled_graph.invoke, {"ticker": ticker})
    buf = io.BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Header
    pdf.cell(0, 10, f"Analysis for {ticker}", ln=True)
    pdf.ln(4)

    # Key metrics
    pdf.cell(0, 8, f"Sentiment: {safe_text(result.get('sentiment'))} (confidence {safe_text(result.get('confidence'))})", ln=True)
    pdf.cell(0, 8, f"Recommendation: {safe_text(result.get('recommendation'))}", ln=True)

    try:
        pdf.multi_cell(0, 8, f"Insight: {safe_text(result.get('insight'))}")
    except:
        pdf.multi_cell(0, 8, "Insight: [Unrenderable]")

    pdf.ln(4)

    # News Section
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 8, "Top News:", ln=True)
    pdf.set_font("Arial", size=11)
    for idx, item in enumerate(result.get("news", []), start=1):
        title = safe_text(item.get("title", ""))
        try:
            pdf.multi_cell(0, 6, f"{idx}. {title}")
        except Exception as e:
            pdf.multi_cell(0, 6, f"{idx}. News item")

    pdf.ln(4)

    # Summary
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 8, "Summary:", ln=True)
    pdf.set_font("Arial", size=11)
    try:
        pdf.multi_cell(0, 8, safe_text(result.get("summary")))
    except:
        pdf.multi_cell(0, 8, "[Summary unavailable]")

    pdf.ln(4)

    # Price History
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 8, "Price History (last 30 days):", ln=True)
    pdf.set_font("Arial", size=11)
    for date, price in result.get("prices", {}).items():
        try:
            pdf.cell(0, 6, f"{date}: {price}", ln=True)
        except:
            continue

    pdf.output(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={ticker}_analysis.pdf"},
    )

# ─── Root ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    return {"message": "EchoMarket backend running"}

