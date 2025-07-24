# EchoMarket

A simple stock analysis tool that pulls together price data, news, and sentiment analysis to help you research stocks without drowning in information overload.

## What it does

Ever tried researching a stock and ended up with 20 browser tabs open? Yeah, me too. This tool grabs the essentials - current price, recent news, what people are saying about it - and gives you a clean summary instead of making you piece everything together yourself.

You can search by company name (like "Apple") or ticker symbol ("AAPL"), and it'll figure out what you mean either way.

## What you get

- Current stock price and recent price movements
- Sentiment analysis from recent news articles
- Buy/hold/sell recommendation with reasoning
- Trend analysis that actually explains what's happening
- Export your analysis to PDF or CSV

The AI tries to explain its reasoning instead of just spitting out numbers, which I find way more useful than most stock analysis tools.

## Getting it running

You'll need both the backend (Python) and frontend (React) running.

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**API Keys:**
Check `backend/.env.example` for what you'll need. The main ones are:
- OpenAI API key (for the AI analysis)
- TwelveData API key (for stock prices)
- Tavily API key (for news)

## How it works

The backend chains together several analysis steps:
1. Fetches current price and recent price history
2. Grabs recent news articles about the company
3. Analyzes sentiment from those articles
4. Looks at price trends and volatility
5. Generates a buy/hold/sell recommendation
6. Summarizes everything in plain English

Each step is handled by a separate "agent" that focuses on one thing, then passes its results to the next step.

## Tech stack

- **Backend:** Python with FastAPI
- **Frontend:** React with TypeScript
- **AI:** OpenAI GPT models
- **Data:** TwelveData for prices, Tavily for news
- **Database:** MongoDB (for storing analysis results)
- **Styling:** Tailwind CSS

## Notes

This is for research and educational purposes. Don't make investment decisions based solely on what any AI tells you - always do your own research and consider talking to a financial advisor.

The tool works pretty well for getting a quick overview of a stock, but it's not meant to replace thorough due diligence.