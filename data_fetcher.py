# retrieving financial data from various sources.
# cacheing to avoid repeated API calls
import os
import pandas as pd
import yfinance as yf
import requests
import json
from datetime import datetime, timedelta
import time
import logging
from config import ALPHA_VANTAGE_API_KEY, FINANCIAL_MODELING_PREP_API_KEY, DATA_DIRECTORY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# fetch financial data from various sources
class DataFetcher:
    def __init__(self, cache_dir=DATA_DIRECTORY):
        self.cache_dir = cache_dir # cache directory for storing data
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
   
   # supported indeces is SP 500, NASDAQ 100, and DOW 30
   # error might exist if the page structure changes? 
   # FIX!!!!: instead of stating which table it is , see which table has the correct columns 
    def get_stock_symbols(self, index="sp500"):
      try:
          if index == "sp500":
              try:
                  table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
                  df = table[0]
                  return df['Symbol'].str.replace('.', '-').tolist()
              except Exception as e:
                  logger.error(f"Error reading S&P 500 from Wikipedia: {e}")
                  # in case of error, fallback to a small sample of known S&P 500 stocks
                  return ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "JPM", "V", "PG", "UNH"]
          
          elif index == "nasdaq100":
              try:
                  table = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
                  df = table[4]
                  return df['Ticker'].tolist()
              except Exception as e:
                  logger.error(f"Error reading Nasdaq 100 from Wikipedia: {e}")
                  return ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", "NFLX", "PYPL", "INTC"]
          
          elif index == "dow30":
              try:
                  table = pd.read_html('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average')
                  df = table[2]
                  return df['Symbol'].tolist()
              except Exception as e:
                  logger.error(f"Error reading Dow 30 from Wikipedia: {e}")
                  return ["AAPL", "AMGN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS", "DOW", 
                          "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", 
                          "MRK", "MSFT", "NKE", "PG", "TRV", "UNH", "V", "VZ", "WBA", "WMT"]
          else:
              logger.error(f"Unknown index: {index}, try Sp500/Dow30/nasdaq100")
              return []
                  
      except Exception as e:
          logger.error(f"Error fetching symbols for {index}: {e}")
          return ["AAPL", "MSFT", "AMZN", "GOOGL", "META"]
      
    # fetch data from yfinance 
    # symbols is a list of stock symbols
    # period is the time period for the data (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
    # interval is the data interval (e.g., '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
    # returns a dictionary with stock data for each symbol
    def fetch_yfinance_data(self, symbols, period="1y", interval="1d"):
        result = {}
        # Split symbols into batches to avoid rate limiting issue 
        batch_size = 20
        symbol_batches = [symbols[i:i + batch_size] for i in range(0, len(symbols), batch_size)]
        
        for batch in symbol_batches:
            try:
                data = yf.download(
                    tickers=batch,
                    period=period,
                    interval=interval,
                    group_by='ticker',
                    auto_adjust=True,
                    prepost=False,
                    threads=True
                )
                
                for symbol in batch:
                    try:
                        # If we have only one symbol, data is a DataFrame
                        if len(batch) == 1:
                            symbol_data = data
                        else:
                            # If we have multiple symbols, data is a Panel
                            symbol_data = data[symbol]
                        
                        # Skip symbols with empty data
                        if symbol_data.empty:
                            logger.warning(f"No data available for {symbol}")
                            continue
                        
                        # Add to results
                        result[symbol] = {
                            'historical': symbol_data,
                            'last_updated': datetime.now().isoformat()
                        }
                        
                        # Get additional info
                        ticker = yf.Ticker(symbol)
                        result[symbol]['info'] = ticker.info
                        
                        # Get financials if available
                        try:
                            result[symbol]['financials'] = {
                                'income_statement': ticker.income_stmt,
                                'balance_sheet': ticker.balance_sheet,
                                'cash_flow': ticker.cashflow
                            }
                        except:
                            logger.warning(f"Could not fetch financials for {symbol}")
                            
                    except Exception as e:
                        logger.error(f"Error processing data for {symbol}: {e}")
                
                # Wait to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error fetching data for batch: {e}")
        
        return result
    
    def fetch_alpha_vantage_data(self, symbol, function="TIME_SERIES_DAILY_ADJUSTED"):
        """
        Fetch stock data from Alpha Vantage API.
        
        Args:
            symbol (str): Stock symbol
            function (str): Alpha Vantage function to call
            
        Returns:
            dict: Alpha Vantage data
        """
        if not ALPHA_VANTAGE_API_KEY:
            logger.error("Alpha Vantage API key not set")
            return None
        
        base_url = "https://www.alphavantage.co/query"
        params = {
            "function": function,
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY,
            "outputsize": "full"
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check for error messages
            if "Error Message" in data:
                logger.error(f"Alpha Vantage error: {data['Error Message']}")
                return None
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage data for {symbol}: {e}")
            return None
    
    def save_to_cache(self, data, filename):
        """Save data to cache."""
        filepath = os.path.join(self.cache_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f)
            logger.info(f"Data saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
            return False
    
    def load_from_cache(self, filename, max_age_hours=24):
        """Load data from cache if not too old."""
        filepath = os.path.join(self.cache_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        # Check if cache is too old
        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        if datetime.now() - file_time > timedelta(hours=max_age_hours):
            logger.info(f"Cache for {filename} is too old")
            return None
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            logger.info(f"Data loaded from {filepath}")
            return data
        except Exception as e:
            logger.error(f"Error loading from cache: {e}")
            return None