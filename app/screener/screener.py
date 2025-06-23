from datetime import datetime
import pandas as pd
import numpy as np
import logging
import operator
from app.data import get_stock_symbols, fetch_yfinance_data, load_from_database, save_to_database
from app.database import SessionLocal
from app.indicators.indicators import TechnicalIndicators
from .fundamental import screen_stocks as fundamental_screen_stocks, apply_criteria
from .technical import screen_by_technical
from .combined import create_combined_screen

# logging leven is Error! 
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class StockScreener:

    # for comparison operators ('>', 20) 
    OPERATORS = {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne
    }
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.stock_data = {} # will hold all loaded stock data for display 

    def load_data(self, symbols=None, reload=False, period="1y", interval="1d"):
        if symbols is None:
            symbols = get_stock_symbols(index="sp500") # defalt value 

        self.stock_data = fetch_yfinance_data(
            symbols,
            period=period,
            interval=interval,
            reload=reload,
            load_from_db=lambda symbol: load_from_database(symbol, SessionLocal),
            save_to_db=lambda symbol, data: save_to_database(symbol, data, SessionLocal)
        )
        return self.stock_data
    

    def screen_stocks(self, criteria, limit=None):
        return fundamental_screen_stocks(self.stock_data, criteria, limit)
    
    
    def screen_by_technical(self, criteria):
        return screen_by_technical(self.stock_data, self.indicators, criteria)
    

    def create_combined_screen(self, fundamental_criteria, technical_criteria, limit=50):
        return create_combined_screen(self, fundamental_criteria, technical_criteria, limit)

 
# Example Usage 
if __name__ == "__main__":
    screener = StockScreener()
    symbols = get_stock_symbols(index="dow30")  # Get first 50 S&P 500 symbols
    screener.load_data(symbols)
    
    # Fundamental screening example
    print("=" * 50)
    print("FUNDAMENTAL SCREENING")
    print("=" * 50)
    
    criteria = {
        'market_cap': ('>', 10e9),     
        'sector': 'Technology'          
    }
    
    results = screener.screen_stocks(criteria)
    
    print(f"Found {len(results)} stocks that match the criteria:")
    for stock in results:
        print(f"{stock['symbol']} - {stock['name']} (Market Cap: ${stock['market_cap']:,.0f})")
    
    # Technical screening example
    print("\n" + "=" * 50)
    print("TECHNICAL SCREENING")
    print("=" * 50)
   
    tech_criteria = {
        'rsi': ('<', 40),            # RSI < 40 (potentially oversold)
        'ma': ('>', 100),            # 20-day MA > 100
        'ema': ('>', 100)            # 20-day EMA > 100
    }
    
    tech_results = screener.screen_by_technical(tech_criteria)
    
    print(f"Found {len(tech_results)} stocks that match the technical criteria:")
    for stock in tech_results:
        print(f"{stock['symbol']} - {stock['name']} (Current Price: ${stock['price']:.2f})")
    
    # Combined screening example
    print("\n" + "=" * 50)
    print("COMBINED SCREENING")
    print("=" * 50)
    
  
    fundamental_criteria = {
        'market_cap': ('>', 10e9),   
        'sector': 'Technology'       
    }
    
   
    technical_criteria = {
        'ma': ('>', 100)            
    }
    
   
    
    combined_results = screener.create_combined_screen(
        fundamental_criteria, 
        technical_criteria, 
        limit=10
    )
    
    print(f"\nFound {len(combined_results)} stocks matching combined criteria:")
    for stock in combined_results:
        market_cap = stock.get('market_cap', 0)
        price = stock.get('price', 0)
        print(f"✓ {stock['symbol']} - {stock['name']} "
              f"(Market Cap: ${market_cap:,.0f}, Price: ${price:.2f})")
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Fundamental screening: {len(results)} stocks")
    print(f"Technical screening: {len(tech_results)} stocks")
    print(f"Combined screening: {len(combined_results)} stocks")
    print("=" * 50)
