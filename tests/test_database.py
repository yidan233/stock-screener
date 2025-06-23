import unittest
import os
import json
from datetime import datetime, timedelta

# --- Updated Imports for the new database structure ---
# We now import all necessary components from the new database package
from app.database import (
    Stock,
    HistoricalPrice,
    ScreeningResult,
    reset_database,
    backup_database,
    restore_database
)
from app.database.connection import SessionLocal, engine

class TestDatabase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("\n---> Setting up test database schema...")
        reset_database()
        print("✅ Test database schema is ready.")

    @classmethod
    def tearDownClass(cls):
        print("\n---> Tearing down database connections...")
        engine.dispose()
        print("✅ Database connections closed.")

    def setUp(self):
        """
        Set up a new session and fresh test data before each individual test.
        This ensures that tests are independent and don't affect each other.
        """
        self.session = SessionLocal()
        self.test_symbol = "TEST_STOCK"
        
        # Clean up data with the same symbol from a previously failed test run
        self.session.query(HistoricalPrice).filter_by(symbol=self.test_symbol).delete()
        self.session.query(Stock).filter_by(symbol=self.test_symbol).delete()
        self.session.commit()
        
        self.test_stock = Stock(
            symbol=self.test_symbol,
            name="Test Company Inc.",
            sector="Technology",
            industry="Software - Infrastructure",
            market_cap=1234567890.0,
            current_price=150.25,
            pe_ratio=25.5,
            dividend_yield=1.5,
            beta=1.1,
            info={"note": "This is a complete test object."}
        )
        self.session.add(self.test_stock)
        
        self.test_prices = []
        for i in range(5):
            # This now includes the adj_close field.
            price = HistoricalPrice(
                symbol=self.test_symbol,
                date=datetime.now().date() - timedelta(days=i),
                open=100 + i,
                high=105 + i,
                low=99 + i,
                close=102 + i,
                adj_close=102.5 + i, # Adjusted close price
                volume=1000000 + (i * 10000)
            )
            self.test_prices.append(price)

        self.session.add_all(self.test_prices)
        self.session.commit()

    def tearDown(self):
        """
        Clean up test data and close the session after each test runs.
        This now also cleans up ScreeningResult objects to ensure test isolation.
        """
        self.session.query(HistoricalPrice).filter_by(symbol=self.test_symbol).delete()
        self.session.query(Stock).filter_by(symbol=self.test_symbol).delete()
        self.session.query(ScreeningResult).delete()
        self.session.commit()
        self.session.close()


    def test_get_stock_info(self):
        stock = self.session.query(Stock).filter_by(symbol=self.test_symbol).first()
        self.assertIsNotNone(stock)
        self.assertEqual(stock.name, "Test Company Inc.")
        self.assertEqual(stock.industry, "Software - Infrastructure")
        self.assertEqual(stock.current_price, 150.25)
        self.assertEqual(stock.pe_ratio, 25.5)
        self.assertEqual(stock.beta, 1.1)
        self.assertEqual(stock.info["note"], "This is a complete test object.")

    def test_get_historical_prices_date_range(self):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=2) # Should get 3 days of data (day 0, 1, 2)
        
        prices = self.session.query(HistoricalPrice)\
            .filter(HistoricalPrice.symbol == self.test_symbol)\
            .filter(HistoricalPrice.date >= start_date)\
            .filter(HistoricalPrice.date <= end_date)\
            .all()
        
        self.assertEqual(len(prices), 3)

    def test_stock_to_prices_relationship(self):
        """Test the one-to-many relationship between a Stock and its HistoricalPrices."""
        stock = self.session.query(Stock).filter_by(symbol=self.test_symbol).first()
        self.assertIsNotNone(stock.prices)
        self.assertEqual(len(stock.prices), 5)
        # Check if the back-reference from price to stock works
        self.assertEqual(stock.prices[0].stock.symbol, self.test_symbol)

    # --- New tests to cover the updated database module's features ---

    def test_screening_result_cache(self):
        criteria = {"sector": "Technology", "min_market_cap": 1000000000}
        results_data = [{"symbol": "TEST_STOCK", "price": 102.0}]
        criteria_hash = str(hash(str(criteria)))
        
        cache_entry = ScreeningResult(
            criteria_hash=criteria_hash,
            criteria=criteria,
            results=results_data,
            index_used="sp500",
            expires_at=datetime.now() + timedelta(hours=1)
        )
        self.session.add(cache_entry)
        self.session.commit()

        # This now queries for the specific entry we created, not just the first one.
        retrieved_entry = self.session.query(ScreeningResult)\
            .filter(ScreeningResult.criteria_hash == criteria_hash)\
            .first()
            
        self.assertIsNotNone(retrieved_entry)
        self.assertEqual(retrieved_entry.criteria["sector"], "Technology")
        self.assertEqual(retrieved_entry.results[0]["symbol"], "TEST_STOCK")

    def test_find_cache_by_hash(self):
        """Test finding a specific cache entry by its unique criteria_hash."""
        # 1. Arrange: Create two different cache entries with unique criteria.
        criteria1 = {"sector": "Technology"}
        hash1 = str(hash(str(criteria1))) # Use str() for consistency
        results1 = [{"symbol": "TEST1"}]
        entry1 = ScreeningResult(criteria_hash=hash1, criteria=criteria1, results=results1, expires_at=datetime.now() + timedelta(hours=1), index_used="sp500")

        criteria2 = {"sector": "Healthcare"}
        hash2 = str(hash(str(criteria2)))
        results2 = [{"symbol": "TEST2"}]
        entry2 = ScreeningResult(criteria_hash=hash2, criteria=criteria2, results=results2, expires_at=datetime.now() + timedelta(hours=1), index_used="sp500")
        
        self.session.add_all([entry1, entry2])
        self.session.commit()

        # 2. Act: Query for the second entry using its specific hash.
        # This simulates how the real application would look up a cached result.
        retrieved_entry = self.session.query(ScreeningResult)\
            .filter(ScreeningResult.criteria_hash == hash2)\
            .first()

        # 3. Assert: Verify that we got the correct entry back.
        self.assertIsNotNone(retrieved_entry)
        self.assertEqual(retrieved_entry.criteria_hash, hash2)
        self.assertEqual(retrieved_entry.criteria["sector"], "Healthcare")
        self.assertEqual(retrieved_entry.results[0]["symbol"], "TEST2")

    def test_backup_and_restore_database(self):
        """Test the full cycle of database backup and restore utilities."""
        # 1. Create a backup of the current state (1 stock, 5 prices)
        backup_file = backup_database()
        self.assertIsNotNone(backup_file)
        self.assertTrue(os.path.exists(backup_file))

        # 2. Verify the content of the backup file
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        self.assertEqual(backup_data['stocks_count'], 1)
        self.assertEqual(backup_data['prices_count'], 5)
        
        # 3. Reset the database (which wipes all data)
        reset_database()
        self.assertEqual(self.session.query(Stock).count(), 0)
        self.assertEqual(self.session.query(HistoricalPrice).count(), 0)

        # 4. Restore the database from our backup file
        success = restore_database(backup_file)
        self.assertTrue(success)

        # 5. Verify that all the data has been correctly restored
        self.assertEqual(self.session.query(Stock).count(), 1)
        self.assertEqual(self.session.query(HistoricalPrice).count(), 5)
        restored_stock = self.session.query(Stock).filter_by(symbol=self.test_symbol).first()
        self.assertIsNotNone(restored_stock)
        self.assertEqual(restored_stock.name, "Test Company Inc.")
        
        # 6. Clean up the created backup file
        os.remove(backup_file)


if __name__ == '__main__':
    unittest.main() 