from typing import TypedDict, List, Dict, Any
from fastapi import APIRouter, HTTPException, Request
from langgraph.graph import StateGraph, END

from backend.agents.market_news import market_news_agent
from backend.agents.price import price_agent
from backend.agents.trend import trend_agent
from backend.agents.sentiment import sentiment_agent
from backend.agents.prediction import prediction_agent
from backend.agents.summary import summary_agent
from backend.agents.logger import logger_agent

router = APIRouter()

# --- LangGraph State Schema ---
class GraphState(TypedDict, total=False):
    ticker: str
    news: List[Dict[str, str]]
    sentiment: str
    confidence: float
    prices: Dict[str, float]
    recommendation: str
    insight: str
    summary: str
    log_id: str


# --- Graph Construction ---
def create_graph() -> Any:
    workflow = StateGraph(GraphState)

    def input_agent(state: GraphState) -> Dict[str, str]:
        return {"ticker": state["ticker"]}

    workflow.add_node("input", input_agent)
    workflow.add_node("market_news", market_news_agent)
    workflow.add_node("price", price_agent)
    workflow.add_node("trend", trend_agent)
    workflow.add_node("sentiment", sentiment_agent)
    workflow.add_node("prediction", prediction_agent)
    workflow.add_node("summary", summary_agent)
    workflow.add_node("logger", logger_agent)

    workflow.set_entry_point("input")
    workflow.add_edge("input", "market_news")
    workflow.add_edge("market_news", "sentiment")
    workflow.add_edge("sentiment", "price")
    workflow.add_edge("price", "trend")
    workflow.add_edge("trend", "prediction")
    workflow.add_edge("prediction", "summary")
    workflow.add_edge("summary", "logger")
    workflow.add_edge("logger", END)

    return workflow.compile()


# --- Single route for both GET and POST ---
@router.api_route("/analyze", methods=["GET", "POST"])
async def analyze(request: Request):
    try:
        if request.method == "GET":
            ticker = request.query_params.get("ticker")
        else:
            body = await request.json()
            ticker = body.get("ticker")

        if not ticker:
            raise HTTPException(status_code=400, detail="Ticker is required")

        graph = create_graph()
        result = graph.invoke({"ticker": ticker})
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
