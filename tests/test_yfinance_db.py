import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.data.yfinance_fetcher import fetch_yfinance_data
from app.data.db_utils import save_to_database, load_from_database
from app.database import SessionLocal

def test_yfinance_db_integration(symbols=None):
    if symbols is None:
        symbols = ["AAPL", "MSFT", "GOOGL"]
    # 1. Fetch data from yfinance
    data = fetch_yfinance_data(symbols)
    for symbol in symbols:
        assert symbol in data, f"No data fetched for {symbol}"
        print(f"Fetched data for {symbol} from yfinance.")

        # 2. Save to database
        save_to_database(symbol, data[symbol], SessionLocal)
        print(f"Saved {symbol} data to database.")

        # 3. Load from database
        loaded = load_from_database(symbol, SessionLocal)
        assert loaded is not None, f"Failed to load data for {symbol} from database"
        assert "info" in loaded and "historical" in loaded, f"Loaded data for {symbol} missing keys"
        assert isinstance(loaded["historical"], pd.DataFrame), f"Historical data for {symbol} is not a DataFrame"
        print(f"Loaded {symbol} data from database.")

        # 4. Check that key fields match
        for key in ["symbol", "sector", "marketCap"]:
            yf_val = data[symbol]["info"].get(key)
            db_val = loaded["info"].get(key)
            print(f"{symbol} {key}: yfinance={yf_val}, db={db_val}")
            assert db_val == yf_val or (db_val is None and yf_val is None), f"Mismatch for {symbol} {key}"

    print("All integration tests for multiple symbols passed!")

if __name__ == "__main__":
    test_yfinance_db_integration()