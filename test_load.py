from screener import StockScreener

# Create a screener instance
screener = StockScreener()

# Choose a few symbols for a quick test
symbols = ["AAPL"]

# Load data for these symbols
data = screener.load_data(symbols=symbols, reload=True, period="1mo", interval="1d")

# Print summary of loaded data
print(f"Loaded data for {len(data)} stocks:")
for symbol, stock in data.items():
    print(f"{symbol}:")
    print("  Info keys:", list(stock.get('info', {}).keys()))
    print("  Historical data head:")
    print(stock.get('historical', '').head())