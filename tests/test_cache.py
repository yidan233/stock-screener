import unittest
import sys
import os

# Add the parent directory to the Python path so that app/ is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data.fetcher import DataFetcher
from app.database.models import Stock, HistoricalPrice, SessionLocal
from app.config import ALPHA_VANTAGE_API_KEY, FINANCIAL_MODELING_PREP_API_KEY, DATA_DIRECTORY


class TestCache(unittest.TestCase):
    def setUp(self):
        self.data_fetcher = DataFetcher()
        self.session = SessionLocal()
        self.test_symbol = "AAPL"  # Using Apple as a test case

    def tearDown(self):
        self.session.close()

    def test_fetch_and_store_in_db(self):
        """Test that fetching stock data (via fetch_yfinance_data) stores data in the database."""
        # Fetch stock data for AAPL (using a short period to avoid rate limits)
        data = self.data_fetcher.fetch_yfinance_data([self.test_symbol], period="1mo", interval="1d")
        self.assertIn(self.test_symbol, data, "fetch_yfinance_data did not return data for AAPL.")

        # Verify that a Stock record was created (or updated) in the database
        stock = self.session.query(Stock).filter(Stock.symbol == self.test_symbol).first()
        self.assertIsNotNone(stock, "Stock record for AAPL not found in database.")
        self.assertEqual(stock.symbol, self.test_symbol, "Stock symbol mismatch.")

        # Verify that at least one HistoricalPrice record was stored
        prices = self.session.query(HistoricalPrice).filter(HistoricalPrice.symbol == self.test_symbol).all()
        self.assertGreater(len(prices), 0, "No historical price records found for AAPL in database.")

        # (Optional) Verify that the returned data (from fetch_yfinance_data) contains expected keys
        self.assertIn("info", data[self.test_symbol], "Expected 'info' key in fetched data.")
        self.assertIn("historical", data[self.test_symbol], "Expected 'historical' key in fetched data.")


if __name__ == '__main__':
    unittest.main()