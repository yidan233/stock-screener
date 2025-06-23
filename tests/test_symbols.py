from app.data.symbols import get_stock_symbols

def test_get_stock_symbols():
    for idx in ["sp500", "nasdaq100", "dow30"]:
        symbols = get_stock_symbols(idx)
        print(f"{idx}: {symbols[:5]} ... total: {len(symbols)}")
        assert isinstance(symbols, list), f"{idx} did not return a list"
        assert len(symbols) > 0, f"{idx} returned an empty list"
        assert all(isinstance(s, str) for s in symbols), f"{idx} contains non-string symbols"
    print("All tests passed!")

if __name__ == "__main__":
    test_get_stock_symbols() 