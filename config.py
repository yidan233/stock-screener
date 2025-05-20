
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# if none exists, set to empty string 
load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
FINANCIAL_MODELING_PREP_API_KEY = os.getenv("FINANCIAL_MODELING_PREP_API_KEY", "")

# Default settings
DEFAULT_CACHE_EXPIRY = 3600  # 1 hour
DATA_DIRECTORY = "data"
STOCK_LISTS = {
    "sp500": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
    "nasdaq100": "https://en.wikipedia.org/wiki/Nasdaq-100",
    "dow30": "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
}

# Database settings (if using a database)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "stock_screener")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "stock_screener.log")