# EchoMarket

A simple stock analysis tool that pulls together price data, news, and sentiment analysis to help you research stocks without drowning in information overload.

## What it does

Ever tried researching a stock and ended up with 20 browser tabs open? Echomarket grabs the essentials - current price, recent news, what people are saying about it - and gives you a clean summary instead of making you piece everything together yourself.

You can search by company name (like "Apple") or ticker symbol ("AAPL"), and it'll figure out what you mean either way.

##  How It Works

1. Finds the ticker if you type a company name.
2. Fetches live price and price history (TwelveData).
3. Pulls relevant news via Tavily.
4. Analyzes sentiment and trend.
5. Chains agent-based steps using LangGraph and OpenAI.
6. Delivers a clean summary and recommendation.




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
- cd backend
- pip install -r requirements.txt

### 3. Running It

Make sure to run from the project root using:
python -m backend.main 
Don’t run `main.py` directly — it’ll break imports.

##  Running the Frontend (Locally)

cd frontend
npm install
npm run dev 

## 🔑 API Keys Needed

Make sure these are in .env:

- OPENAI_API_KEY 
- TWELVEDATA_API_KEY ( I am using TwelveData, you can use any financial API like AlphaVantage, FinHub etc.
- TAVILY_API_KEY
- MONGODB_URI



## AWS Deployment Guide

### Frontend (on AWS S3)

 Build the frontend:

   cd frontend
   npm install
   npm run build
   

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
