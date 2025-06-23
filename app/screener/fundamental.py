from typing import Dict, Any, Tuple, Optional, List
import logging
import operator

logger = logging.getLogger(__name__)

OPERATORS = {
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne
}

FIELD_MAPPING = {
    'market_cap': 'marketCap',
    'pe_ratio': 'trailingPE',
    'forward_pe': 'forwardPE',
    'price_to_book': 'priceToBook',
    'price_to_sales': 'priceToSales',
    'dividend_yield': 'dividendYield',
    'payout_ratio': 'payoutRatio',
    'return_on_equity': 'returnOnEquity',
    'return_on_assets': 'returnOnAssets',
    'profit_margin': 'profitMargins',
    'operating_margin': 'operatingMargins',
    'revenue_growth': 'revenueGrowth',
    'earnings_growth': 'earningsGrowth',
    'beta': 'beta',
    'current_ratio': 'currentRatio',
    'debt_to_equity': 'debtToEquity',
    'enterprise_to_revenue': 'enterpriseToRevenue',
    'enterprise_to_ebitda': 'enterpriseToEbitda',
    'price': 'currentPrice'
}

EXACT_MATCH_FIELDS = ['sector', 'industry', 'country']

'''
example:
criteria = {
    'pe_ratio': ('<', 15),           
    'market_cap': ('>', 1000000000), 
    'sector': 'Technology'           # Exact sector match
}
'''
def apply_criteria(stock_info: Dict[str, Any], criteria: Dict[str, Any]) -> bool:

    for field, condition in criteria.items():
        if field in EXACT_MATCH_FIELDS:
            if stock_info.get(field, '') != condition:
                return False
            continue

        if isinstance(condition, tuple) and len(condition) == 2:
            op_symbol, threshold = condition
            info_field = FIELD_MAPPING.get(field, field)
            actual_value = stock_info.get(info_field)

            if actual_value is None:
                return False
            
            op_func = OPERATORS.get(op_symbol)
            if op_func is None or not op_func(actual_value, threshold):
                return False
    return True

# NEW TASK: enable sorting based on user input
def screen_stocks(stock_data: Dict[str, Any], criteria: Dict[str, Any], limit: Optional[int] = None) -> List[Dict[str, Any]]:
    
    results = []

    for symbol, data in stock_data.items():
        info = data.get('info', {})
        if apply_criteria(info, criteria):
            results.append({
                'symbol': symbol,
                'name': info.get('shortName', 'Unknown'),
                'sector': info.get('sector', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'price': info.get('currentPrice', 0),
                'pe_ratio': info.get('trailingPE', 0)
            })

    results.sort(key=lambda x: x['market_cap'], reverse=True)
    if limit is not None:
        results = results[:limit]
    return results 