from typing import Dict, Any, List
from .fundamental import screen_stocks
from .technical import screen_by_technical

def create_combined_screen(screener, fundamental_criteria: Dict[str, Any], technical_criteria: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
    
    fundamental_results = screen_stocks(screener.stock_data, fundamental_criteria)
    fundamental_symbols = [stock['symbol'] for stock in fundamental_results]

    filtered_data = {symbol: screener.stock_data[symbol] for symbol in fundamental_symbols if symbol in screener.stock_data}

    # Create a temporary screener-like object to pass to screen_by_technical
    class TempScreener:
        pass

    temp = TempScreener()
    temp.stock_data = filtered_data
    temp.indicators = screener.indicators

    technical_results = screen_by_technical(temp.stock_data, temp.indicators, technical_criteria)
    technical_results.sort(key=lambda x: x.get('market_cap', 0), reverse=True)
    
    if limit:
        return technical_results[:limit]
    return technical_results 