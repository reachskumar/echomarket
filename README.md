# EchoMarket

A simple stock analysis tool that pulls together price data, news, and sentiment analysis to help you research stocks without drowning in information overload.

## What it does

Ever tried researching a stock and ended up with 20 browser tabs open? Echomarket grabs the essentials - current price, recent news, what people are saying about it - and gives you a clean summary instead of making you piece everything together yourself.

You can search by company name (like "Apple") or ticker symbol ("AAPL"), and it'll figure out what you mean either way. ( Currently only ticker search is supported )

##  How It Works

**Price Discovery**: Fetches live price and historical data (TwelveData API)

**Multi-Source News Gathering**: 
   - **Basic Search**: Headlines and snippets from Tavily
   - **Advanced Extract**: Full article content with financial analysis
   - **Crawl-Enhanced Search**: Premium sources with domain filtering
   - **Data Mapping**: Structured financial metrics and insights
     
**Intelligent Content Processing**: Quality scoring, deduplication, and ranking


**AI-Powered Analysis**: Sentiment analysis using extracted quotes and financial figures

**Trend Analysis**: Price pattern recognition with OpenAI

**Investment Recommendations**: Conservative buy/hold/sell guidance

**Executive Summary**: Simple summary

##  Advanced Tavily API Integration

EchoMarket implements **all four Tavily API features** for comprehensive data gathering:

### ** Search**
- Basic financial news search with targeted queries
- Real-time headlines and market updates
- Configurable result limits and domain filtering

### ** Extract** 
- Full article content extraction from top sources
- Automated financial figure detection (revenue, earnings, percentages)
- Key quote extraction from executives and analysts
- Sentiment indicator identification (bullish/bearish language)
- Content quality assessment and scoring

### ** Crawl (Advanced Search)**
- Deep search with enhanced crawl depth
- Premium financial source targeting (Bloomberg, Reuters, WSJ)
- Raw content inclusion for detailed analysis
- Domain-specific filtering for quality assurance

### ** Map**
- Structured financial data mapping
- Automated answer generation for specific queries
- Follow-up question suggestions
- Multi-source data correlation and validation

### ** Intelligent Processing**
- Content deduplication across all sources
- Quality scoring based on source reliability and content depth
- Relevance ranking using financial keywords and recency
- Key insight extraction and summarization



## Tech Stack

| Layer         | Tech                              |
|---------------|-----------------------------------|
| Backend       | FastAPI (Python), LangGraph       |
| Frontend      | React + Vite + TypeScript         |
| AI Models     | OpenAI GPT                        |
| News Search   | Tavily API                        |
| Stock Prices  | TwelveData API                    |
| Storage       | MongoDB Atlas                     |
| Styling       | Tailwind CSS                      |
| Deployment    | AWS (S3 + Elastic Beanstalk)      |



##  Running the Backend (Locally)

Here’s how to get the backend up and running:

### 1. Prerequisites
- Python 3.10+
- `pip`
- API keys for:
  - OpenAI
  - TwelveData
  - Tavily
  - MongoDB Atlas

### 2. Setup

- cd echomarket
- cp backend/.env.example backend/.env  # Fill in your API keys
- cd yourproject
- pip install -r requirements.txt

### 3. Running It

Make sure to run from the project root using:

- python -m backend.main 
- Don’t run `main.py` directly — it’ll break imports.

##  Running the Frontend (Locally)

- cd frontend
- npm install
- npm run dev 

## 🔑 API Keys Needed

## You need two .env file one inside your project root and the other one insdie your frontend folder Make sure these are in .env:

Make sure these are in .env under project root:
- OPENAI_API_KEY 
- TWELVEDATA_API_KEY ( I am using TwelveData, you can use any financial API like AlphaVantage, FinHub etc.
- TAVILY_API_KEY
- MONGODB_URI

  
This one, under frontend, talks to your backend URL. This is where you update the backend url.
- VITE_API_URL



## AWS Deployment Guide

### Frontend (on AWS S3)

 Build the frontend:

   -  cd frontend
   - npm install
   - npm run build
   

 Create an S3 bucket:
   - Uncheck “Block all public access”.
   - Enable **static website hosting**.
   - Set `index.html` as the Index and Error document.

 Upload contents of `dist/` folder (not the folder itself).

 Use this bucket policy (replace `YOUR_BUCKET_NAME`):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
    }
  ]
}
```

---

### Backend (on AWS Elastic Beanstalk)

 Make sure your Dockerfile is present.

Install the EB CLI (or use AWS Console):

   pip install awsebcli
   
 Initialize:
 
   eb init  # Choose Docker platform
  

Deploy:
   
   eb create echomarket-backend-env
   # Or redeploy later:
   eb deploy
  

Set environment variables in EB Console
   Add OpenAI, MongoDB URI, etc.

 Check EB health & logs.


## IMP Once your backend is running on AWS ElasticBeanstalk, make sure you whitelist your backend public IP in MOngoDB Atlas to avoid SSL handshake issues.

 ##  Architecture Summary

- **LangGraph** agents handle each step: retrieval → sentiment → reasoning → recommendation.
- Logs and results stored in **MongoDB Atlas**.
- Entire pipeline is modular and auditable.


## Disclaimer

This is for **educational/research** use. Don't make investment decisions based solely on this — always do your own due diligence or consult a financial advisor.
