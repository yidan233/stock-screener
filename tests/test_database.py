import unittest
from datetime import datetime, timedelta, date
import pandas as pd
import sys
import os

# Add the parent directory to the Python path so that app/ is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data.fetcher import DataFetcher
from app.database.models import Stock, HistoricalPrice, SessionLocal

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.data_fetcher = DataFetcher()
        self.session = SessionLocal()
        self.test_symbol = "AAPL"  # Using Apple as a test case
    
    def tearDown(self):
        self.session.close()
    
    def test_fetch_and_store(self):
        """Test fetching and storing stock data"""
        # Fetch data for Apple
        data = self.data_fetcher.fetch_yfinance_data([self.test_symbol], period="1mo", interval="1d")
        
        # Verify data was stored
        self.assertIn(self.test_symbol, data)
        
        # Check stock info in database
        stock = self.session.query(Stock).filter(Stock.symbol == self.test_symbol).first()
        self.assertIsNotNone(stock)
        self.assertEqual(stock.symbol, self.test_symbol)
        
        # Check historical prices
        prices = self.session.query(HistoricalPrice).filter(
            HistoricalPrice.symbol == self.test_symbol
        ).order_by(HistoricalPrice.date).all()
        
        self.assertGreater(len(prices), 0)
        
        # Verify price data
        latest_price = prices[-1]
        self.assertIsInstance(latest_price.date, date)
        self.assertIsInstance(latest_price.open, float)
        self.assertIsInstance(latest_price.close, float)
        self.assertIsInstance(latest_price.volume, int)
    
    def test_get_stock_data(self):
        """Test retrieving stock data from database"""
        # First fetch and store some data
        self.data_fetcher.fetch_yfinance_data([self.test_symbol], period="1mo", interval="1d")
        
        # Now try to get it from database
        data = self.data_fetcher.get_stock_data(self.test_symbol)
        
        self.assertIsNotNone(data)
        self.assertIn('info', data)
        self.assertIn('historical', data)
        self.assertIsInstance(data['historical'], pd.DataFrame)
        
        # Verify the data is recent
        self.assertGreater(len(data['historical']), 0)
    
    def test_get_stocks_by_sector(self):
        """Test getting stocks by sector"""
        # First fetch some data for a few stocks
        symbols = ["AAPL", "MSFT", "GOOGL"]  # All tech stocks
        self.data_fetcher.fetch_yfinance_data(symbols, period="1mo", interval="1d")
        
        # Get tech stocks
        tech_stocks = self.data_fetcher.get_stocks_by_sector("Technology")
        
        self.assertGreater(len(tech_stocks), 0)
        self.assertIn(self.test_symbol, tech_stocks)
    
    def test_get_historical_prices(self):
        """Test getting historical prices with date range"""
        # First fetch some data
        self.data_fetcher.fetch_yfinance_data([self.test_symbol], period="1mo", interval="1d")
        
        # Get prices for last week
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        prices = self.data_fetcher.get_historical_prices(
            self.test_symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        self.assertIsInstance(prices, pd.DataFrame)
        self.assertGreater(len(prices), 0)
        
        # Verify date range
        if not prices.empty:
            self.assertGreaterEqual(prices.index.min(), start_date)
            self.assertLessEqual(prices.index.max(), end_date)

if __name__ == '__main__':
    unittest.main() 