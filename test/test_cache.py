from data_fetcher import DataFetcher

fetcher = DataFetcher()

# Example data to cache
test_data = {
    "AAPL": {"price": 190.5, "volume": 1000000},
    "MSFT": {"price": 320.1, "volume": 800000}
}
filename = "test_cache.json"

# Test saving to cache
saved = fetcher.save_to_cache(test_data, filename)
print("Saved to cache:", saved)

# Test loading from cache
loaded_data = fetcher.load_from_cache(filename, max_age_hours=24)
print("Loaded from cache:", loaded_data)

expired_data = fetcher.load_from_cache(filename, max_age_hours=0)
print("Loaded after expiry (should be None):", expired_data)