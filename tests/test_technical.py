from app.screener.screener import StockScreener
from app.config import ALPHA_VANTAGE_API_KEY
from app.data.fetcher import DataFetcher

# Create a screener instance
screener = StockScreener()

# Use a small set of symbols for a quick test
symbols = ["AAPL", "MSFT", "GOOGL"]

# Load data for these symbols (force reload for fresh data)
screener.load_data(symbols=symbols, reload=True, period="3mo", interval="1d")

# Define technical screening criteria
criteria = {
    'rsi': ('>', 40),           # RSI less than 40 (potentially oversold)
    
    #'ma': ('>', 100),           # 20-day MA greater than 100
    #'ema': ('>', 100),          # 20-day EMA greater than 100
    #'macd_hist': ('>', 0),      # MACD histogram positive
    #'boll_lower': ('<', 0),     # Price below lower Bollinger Band
    #'atr': ('>', 2),            # ATR greater than 2
    #'obv': ('>', 0),            # OBV positive
   # 'stoch_k': ('<', 20),       # Stochastic %K less than 20
   # 'stoch_d': ('<', 20),       # Stochastic %D less than 20
    #'roc': ('>', 0)             # Rate of Change positive
  
}

# Run the technical screener
results = screener.screen_by_technical(criteria)

# Print the results
print(f"Found {len(results)} stocks matching the technical criteria:")
for stock in results:
    print(f"{stock['symbol']} - {stock['name']} (Current Price: ${stock['price']:.2f})")