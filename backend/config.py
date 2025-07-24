# Configuration Settings
# 
# This file manages all the environment variables and API keys our app needs.
#

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings:
    
    
    # OpenAI API for analysis
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # TwelveData API for stock prices
    TWELVE_DATA_API_KEY: str = os.getenv("TWELVE_DATA_API_KEY", "")
    
    # Tavily API for news search
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    # MongoDB for storing analysis results
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "echomarket")
    MONGO_COLLECTION: str = os.getenv("MONGO_COLLECTION", "analyses")
    
    # Optional: Analysis settings (with sensible defaults)
    MAX_NEWS_ITEMS: int = int(os.getenv("MAX_NEWS_ITEMS", "10"))
    ANALYSIS_TIMEOUT: int = int(os.getenv("ANALYSIS_TIMEOUT", "30"))
    
    def __init__(self):
        required_keys = [
            ("OPENAI_API_KEY", self.OPENAI_API_KEY),
            ("TWELVE_DATA_API_KEY", self.TWELVE_DATA_API_KEY),
            ("TAVILY_API_KEY", self.TAVILY_API_KEY)
        ]
        
        # Warn if any required keys are missing
        missing_keys = [name for name, value in required_keys if not value]
        
        if missing_keys:
            print(f"⚠️  Warning: Missing required environment variables: {', '.join(missing_keys)}")
            print("   The app may not work correctly without these API keys.")
            print("   Check your .env file or environment configuration.")

settings = Settings()
