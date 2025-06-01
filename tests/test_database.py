import unittest
from datetime import datetime, timedelta
from app.data.fetcher import DataFetcher
from app.database.models import Stock, HistoricalPrice, SessionLocal

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Set up test data before each test"""
        self.data_fetcher = DataFetcher()
        self.session = SessionLocal()
        self.test_symbol = "TEST123"  # Use a unique symbol that won't conflict
        
        # Clean up any existing test data
        self.session.query(HistoricalPrice).filter_by(symbol=self.test_symbol).delete()
        self.session.query(Stock).filter_by(symbol=self.test_symbol).delete()
        self.session.commit()
        
        # Create test stock
        self.test_stock = Stock(
            symbol=self.test_symbol,
            name="Test Company",
            sector="Technology",
            market_cap=1000000000.0,
            info={
                "shortName": "Test Company",
                "sector": "Technology",
                "marketCap": 1000000000.0,
                "pe_ratio": 15.5,
                "dividend_yield": 2.5
            }
        )
        
        # Create test historical prices
        self.test_prices = []
        base_price = 100.0
        for i in range(5):
            date = datetime.now().date() - timedelta(days=i)
            price = HistoricalPrice(
                symbol=self.test_symbol,
                date=date,
                open=base_price + i,
                high=base_price + i + 5,
                low=base_price + i - 5,
                close=base_price + i + 5,
                volume=1000000
            )
            self.test_prices.append(price)
        
        # Add test data to database
        self.session.add(self.test_stock)
        for price in self.test_prices:
            self.session.add(price)
        self.session.commit()

    def tearDown(self):
        """Clean up test data after each test"""
        self.session.query(HistoricalPrice).filter_by(symbol=self.test_symbol).delete()
        self.session.query(Stock).filter_by(symbol=self.test_symbol).delete()
        self.session.commit()
        self.session.close()

    def test_get_stock_info(self):
        """Test getting stock information including JSON info field"""
        stock = self.session.query(Stock).filter_by(symbol=self.test_symbol).first()
        
        self.assertIsNotNone(stock)
        self.assertEqual(stock.symbol, self.test_symbol)
        self.assertEqual(stock.name, "Test Company")
        self.assertEqual(stock.sector, "Technology")
        self.assertEqual(stock.market_cap, 1000000000.0)
        
        # Test JSON info field
        self.assertIn("pe_ratio", stock.info)
        self.assertIn("dividend_yield", stock.info)
        self.assertEqual(stock.info["pe_ratio"], 15.5)
        self.assertEqual(stock.info["dividend_yield"], 2.5)

    def test_get_historical_prices(self):
        """Test getting historical prices with date range"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=3)
        
        prices = self.session.query(HistoricalPrice)\
            .filter(HistoricalPrice.symbol == self.test_symbol)\
            .filter(HistoricalPrice.date >= start_date)\
            .filter(HistoricalPrice.date <= end_date)\
            .order_by(HistoricalPrice.date)\
            .all()
        
        self.assertEqual(len(prices), 4)  # Should get 4 days of data
        self.assertEqual(prices[0].close, 105.0)
        self.assertEqual(prices[0].volume, 1000000)

    def test_get_stocks_by_sector(self):
        """Test getting stocks by sector"""
        tech_stocks = self.session.query(Stock)\
            .filter(Stock.sector == "Technology")\
            .filter(Stock.symbol == self.test_symbol)\
            .all()
        
        self.assertEqual(len(tech_stocks), 1)
        self.assertEqual(tech_stocks[0].symbol, self.test_symbol)
        self.assertEqual(tech_stocks[0].info["sector"], "Technology")

    def test_stock_relationship(self):
        """Test the relationship between Stock and HistoricalPrice"""
        stock = self.session.query(Stock).filter_by(symbol=self.test_symbol).first()
        
        self.assertIsNotNone(stock.prices)
        self.assertEqual(len(stock.prices), 5)
        self.assertEqual(stock.prices[0].symbol, self.test_symbol)
        self.assertEqual(stock.prices[0].close, 105.0)

if __name__ == '__main__':
    unittest.main() 