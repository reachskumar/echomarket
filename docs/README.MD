# EchoMarket Documentation

## Project Overview

EchoMarket is a stock analysis tool that helps you research stocks without getting overwhelmed by information. Instead of jumping between multiple websites and trying to piece together price data, news, and analysis, this tool does it all in one place.

## How It Works

The app follows a simple workflow:

1. **User Input**: Type in a company name or stock ticker
2. **Ticker Resolution**: If you entered a company name, we figure out the ticker symbol
3. **Data Collection**: We fetch current prices, recent news, and market data
4. **AI Analysis**: Our AI analyzes sentiment, trends, and generates recommendations
5. **Results Display**: Everything gets presented in an easy-to-read format

## Architecture

### Backend (Python)
- **FastAPI**: Main API server that coordinates everything
- **Analysis Agents**: Each agent handles one part of the analysis
  - Price Agent: Gets current and historical prices
  - News Agent: Fetches recent news articles
  - Sentiment Agent: Analyzes if news is positive/negative
  - Trend Agent: Looks at price movements and volatility
  - Prediction Agent: Generates buy/hold/sell recommendations
  - Summary Agent: Puts everything together in plain English
- **External APIs**: 
  - TwelveData for stock prices
  - Tavily for news articles
  - OpenAI for AI analysis

### Frontend (React + TypeScript)
- **Search Interface**: Simple input for company names or tickers
- **Results Display**: Multiple components showing different aspects of analysis
- **Export Options**: Save your research as PDF or CSV

## Code Style

The codebase uses natural, conversational comments that explain what things do and why, rather than just how they work. Functions have clear names and the logic flows in a way that makes sense to humans reading the code.

## Getting Started

See the main README.md for setup instructions.

## File Structure

```
backend/
├── main.py              # Main API server
├── agents/              # Analysis components
│   ├── price.py         # Gets stock prices
│   ├── market_news.py   # Fetches news articles
│   ├── sentiment.py     # Analyzes news sentiment
│   ├── trend.py         # Analyzes price trends
│   ├── prediction.py    # Generates recommendations
│   ├── summary.py       # Creates final summary
│   └── logger.py        # Logs analysis results
└── config.py            # Configuration settings

frontend/
├── src/
│   ├── pages/
│   │   └── home.tsx     # Main application page
│   ├── components/ui/   # Reusable UI components
│   └── lib/             # Utility functions
└── ...                  # Configuration files
```

## API Endpoints

- `GET /` - Health check
- `POST /analyze` - Run full analysis for a ticker
- `GET /ui/analyze/{ticker}` - UI-optimized analysis endpoint
- `GET /detect-ticker` - Convert company name to ticker
- `GET /analyze/{ticker}/export/pdf` - Export analysis as PDF
- `GET /analyze/{ticker}/export/csv` - Export analysis as CSV
