
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Locate the project root (../ from this file)
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"

# Load .env *before* instantiating settings
# override=False -> do not clobber already-exported shell vars
load_dotenv(dotenv_path=ENV_PATH, override=False)


class Settings(BaseModel):
    # API keys
    TAVILY_API_KEY: str | None = Field(default=None)
    OPENAI_API_KEY: str | None = Field(default=None)
    TWELVE_DATA_API_KEY: str | None = Field(default=None)
    #ALPHA_VANTAGE_API_KEY: str | None = Field(default=None)
    #FINNHUB_API_KEY: str | None = Field(default=None)

    # Database
    MONGODB_URI: str | None = Field(default=None)
    MONGODB_DB_NAME: str = "echomarket"

    # Tunables
    PRICE_HISTORY_DAYS: int = 30
    OPENAI_MODEL: str = "gpt-4o-mini"

    def masked(self) -> dict:
        def _m(v):
            if not v:
                return "<missing>"
            return (v if len(v) <= 8 else f"{v[:4]}…{v[-4:]}")
        return {
            "TAVILY_API_KEY": _m(self.TAVILY_API_KEY),
            "OPENAI_API_KEY": _m(self.OPENAI_API_KEY),
            "ALPHA_VANTAGE_API_KEY": _m(self.ALPHA_VANTAGE_API_KEY),
            "FINNHUB_API_KEY": _m(self.FINNHUB_API_KEY),
            "MONGODB_URI": _m(self.MONGODB_URI),
            "MONGODB_DB_NAME": self.MONGODB_DB_NAME,
            "PRICE_HISTORY_DAYS": self.PRICE_HISTORY_DAYS,
            "OPENAI_MODEL": self.OPENAI_MODEL,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    # Pull from environment (already populated by load_dotenv)
    return Settings(
        TAVILY_API_KEY=os.getenv("TAVILY_API_KEY"),
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"),
        TWELVE_DATA_API_KEY=os.getenv("TWELVE_DATA_API_KEY"),
        MONGODB_URI=os.getenv("MONGODB_URI"),
        MONGODB_DB_NAME=os.getenv("MONGODB_DB_NAME", "echomarket"),
        PRICE_HISTORY_DAYS=int(os.getenv("PRICE_HISTORY_DAYS", "30") or 30),
        OPENAI_MODEL=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )


# module-level instance
settings = get_settings()
