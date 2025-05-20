
from data_fetcher import DataFetcher

fetcher = DataFetcher()

# Test with a known symbol, e.g., AAPL
result = fetcher.fetch_alpha_vantage_data("AAPL")

if result:
    print("Alpha Vantage data fetched successfully!")
    # Print the top-level keys of the result to inspect
    print("Keys in result:", list(result.keys()))
    # Optionally, print a sample of the data
    for k, v in list(result.items())[:2]:
        print(f"{k}: {str(v)[:200]}...")  # Print first 200 chars for brevity
else:
    print("Failed to fetch data. Check your API key, symbol, or network.")