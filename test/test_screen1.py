from screener import StockScreener

screener = StockScreener()
symbols = ["AAPL", "MSFT", "GOOGL"]

screener.load_data(symbols=symbols, reload=True, period="1mo", interval="1d")

criteria = {
    'market_cap': ('>', 1e11),         # Market cap > $100B
    'pe_ratio': ('<', 40),             # P/E ratio < 40
    'dividend_yield': ('>=', 0.005),   # Dividend yield >= 0.5%
    'sector': 'Technology',            # Sector must be Technology
    'country': 'United States',        # Country must be United States
    'price_to_book': ('<', 20),        # Price/Book < 20
    'profit_margin': ('>', 0.05),      # Profit margin > 5%
    'beta': ('<', 2),                  # Beta < 2
}

results = screener.screen_stocks(criteria)
print(f"Found {len(results)} stocks matching the criteria:")
for stock in results:
    print(f"{stock['symbol']} - {stock['name']} (Market Cap: ${stock['market_cap']:,.0f}, Price: ${stock['price']})")