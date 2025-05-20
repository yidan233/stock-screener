# designed to filter and select stocks on both fundamental and technical criteria
from datetime import datetime
import pandas as pd
import numpy as np
import logging
import operator
from data_fetcher import DataFetcher
from indicators import TechnicalIndicators


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockScreener:
    # for comparison operators ('>', 20) 
    OPERATORS = {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne
    }
    
    def __init__(self):
        self.data_fetcher = DataFetcher() # retrive or cache stock data
        self.indicators = TechnicalIndicators() # caculate technical indicators 
        self.stock_data = {} # stores the loaded stock data for screening 

        
    # symbols: list of stock symbols to load data for
    # reload: whether to reload data from the source (forced refresh)
    # period: time period for historical data (e.g., '1y', '5y')
    # interval: data interval (e.g., '1d', '1wk', '1mo')
    # returns a dictionary with stock data for each symbol
    def load_data(self, symbols=None, reload=False, period="1y", interval="1d"):
        # defaulted to S&P 500 if no symbols are provided
        if symbols is None:
            symbols = self.data_fetcher.get_stock_symbols(index="sp500")
            logger.info(f"Loaded {len(symbols)} symbols from S&P 500")
        
        # ideas: use cache metadata to check if we have all the symbols we need, and use the cache file to load the data
        cache_file = f"stock_data_{period}_{interval}.json"
        # cache file: main cache file stores the actual stock data 
        cache_metadata_file = f"stock_data_{period}_{interval}_metadata.json"
        # cache metadata file: stores the metadata about the stock data (e.g., symbols, period, interval)
      
        if not reload: # try from cache 
            metadata = self.data_fetcher.load_from_cache(cache_metadata_file)
            if metadata is not None:
                # Check if we have all the symbols we need
                cached_symbols = set(metadata.get('symbols', []))
                requested_symbols = set(symbols)

                 # We have all the symbols in cache, load the data
                if requested_symbols.issubset(cached_symbols):
                    self.stock_data = self.data_fetcher.load_from_cache(cache_file)
                    if self.stock_data is not None:
                        logger.info(f"Loaded {len(self.stock_data)} stocks from cache")
                        return self.stock_data
        
        # cache is disables or not all symbols found
        logger.info(f"Fetching stock data for {len(symbols)} symbols")
        self.stock_data = self.data_fetcher.fetch_yfinance_data(symbols, period, interval)
        
        # Save to cache
        self.data_fetcher.save_to_cache(self.stock_data, cache_file)
        
        # Save metadata
        metadata = {
            'symbols': list(self.stock_data.keys()),
            'period': period,
            'interval': interval,
            'last_updated': datetime.now().isoformat()
        }
        self.data_fetcher.save_to_cache(metadata, cache_metadata_file)
        logger.info(f"Fetched and cached data for {len(self.stock_data)} stocks")
        return self.stock_data
    
    # it checks if a stock meets the screening criteria
    # stock_info: dictionary with stock information
    # criteria: dictionary with screening criteria
    """
    Example: {
                    'market_cap': ('>', 1e9),  # Market cap > $1 billion
                    'pe_ratio': ('<', 20),     # P/E ratio < 20
                    'dividend_yield': ('>=', 0.02)  # Dividend yield >= 2%
                }
    """
    def apply_criteria(self, stock_info, criteria):
       # map user friendly field names to actual field names in the stock_info dictionary
        field_mapping = {
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
        exact_match_fields = ['sector', 'industry', 'country']
       
        for field, condition in criteria.items():
            # case1: exact match fields -> needs to be exact the same 
            if field in exact_match_fields:
                expected_value = condition
                actual_value = stock_info.get(field, '')
                if actual_value != expected_value:
                    return False
                continue
            
            # case2: numeric fields -> needs to be compared with the operator
            if isinstance(condition, tuple) and len(condition) == 2:
                op_symbol, threshold = condition
                info_field = field_mapping.get(field, field)
                actual_value = stock_info.get(info_field)
                
                if actual_value is None:
                    return False
                op_func = self.OPERATORS.get(op_symbol)

                if op_func is None:
                    logger.error(f"Unknown operator: {op_symbol}")
                    return False
                
                if not op_func(actual_value, threshold):
                    return False
        
        return True
    # filters loded stocks based on fundamental criteria
    # like sector, market cap, P/E ratio, etc.
    # IDEAS: add sorting options or fields shown 
    def screen_stocks(self, criteria, limit=None):
        # loads data before screening
        if not self.stock_data:
            raise ValueError("No stock data loaded. Call load_data first.")
        
        results = []
        
        for symbol, data in self.stock_data.items():
            info = data.get('info', {})
            
            # Apply the criteria for each
            if self.apply_criteria(info, criteria):
                results.append({
                    'symbol': symbol,
                    'name': info.get('shortName', 'Unknown'),
                    'sector': info.get('sector', 'Unknown'),
                    'market_cap': info.get('marketCap', 0),
                    'price': info.get('currentPrice', 0)
                })
        results.sort(key=lambda x: x['market_cap'], reverse=True)
        
        if limit is not None:
            results = results[:limit]
        
        return results
    
    # filters loaded stocks based on technical criteria
    # like RSI, moving averages, etc. ( those are defined in the indicators.py file)
    # IDEAS: add the argumentt input!!! 
    # now it uses the default values set in the indicators.py file -> makes user set itself 
    """
    criteria = {
    'rsi': ('<', 40)
    }
    """
    # data looks like 
    """
    {
    'AAPL': {
        'info': { ... },         # Dictionary of fundamental info (from yfinance)
        'historical': DataFrame  # Pandas DataFrame of historical price/volume data
    },
    'MSFT': {
        'info': { ... },
        'historical': DataFrame
    },
    ...
}
    """
    def screen_by_technical(self, criteria):
        if not self.stock_data:
            raise ValueError("No stock data loaded. Call load_data first.")

        results = []

        for symbol, data in self.stock_data.items():
            if 'historical' not in data or data['historical'].empty:
                continue

            hist = data['historical']
            meets_criteria = True

            for indicator, condition in criteria.items():
                op_symbol, threshold = condition
                op_func = self.OPERATORS.get(op_symbol)

                # --- Moving Average (ma) ---
                if indicator == 'ma':
                    ma = self.indicators.moving_average(hist['Close']) # returns a series, based on historial data closed data set 
                    value = ma.iloc[-1] # load the most recent value 
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                # --- Exponential Moving Average (ema) ---
                elif indicator == 'ema':
                    ema = self.indicators.exponential_moving_average(hist['Close'])
                    value = ema.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                # --- Relative Strength Index (rsi) ---
                elif indicator == 'rsi':
                    rsi = self.indicators.relative_strength_index(hist['Close'])
                    value = rsi.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                # --- MACD Histogram (macd_hist) ---
                elif indicator == 'macd_hist':
                    macd_line, signal_line, histogram = self.indicators.macd(hist['Close'])
                    value = histogram.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                # --- Bollinger Bands (boll_upper, boll_lower) ---
                elif indicator == 'boll_upper':
                    upper, middle, lower = self.indicators.bollinger_bands(hist['Close'])
                    price = hist['Close'].iloc[-1]
                    value = price - upper.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break
                elif indicator == 'boll_lower':
                    upper, middle, lower = self.indicators.bollinger_bands(hist['Close'])
                    price = hist['Close'].iloc[-1]
                    value = price - lower.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                # --- Average True Range (atr) ---
                elif indicator == 'atr':
                    atr = self.indicators.average_true_range(hist['High'], hist['Low'], hist['Close'])
                    value = atr.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                # --- On-Balance Volume (obv) ---
                elif indicator == 'obv':
                    obv = self.indicators.on_balance_volume(hist['Close'], hist['Volume'])
                    value = obv.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                # --- Stochastic Oscillator %K (stoch_k) ---
                elif indicator == 'stoch_k':
                    k, d = self.indicators.stochastic_oscillator(hist['High'], hist['Low'], hist['Close'])
                    value = k.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                # --- Stochastic Oscillator %D (stoch_d) ---
                elif indicator == 'stoch_d':
                    k, d = self.indicators.stochastic_oscillator(hist['High'], hist['Low'], hist['Close'])
                    value = d.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                # --- Rate of Change (roc) ---
                elif indicator == 'roc':
                    roc = self.indicators.rate_of_change(hist['Close'])
                    value = roc.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                # --- Add more indicators as needed ---

            if meets_criteria:
                info = data.get('info', {})
                results.append({
                    'symbol': symbol,
                    'name': info.get('shortName', 'Unknown'),
                    'sector': info.get('sector', 'Unknown'),
                    'price': hist['Close'].iloc[-1]
                })

        return results
    # combines both fundamental and technical screening -> limits 
    def create_combined_screen(self, fundamental_criteria, technical_criteria, limit=50):
        # first filter based on fundamental criteria -> get stock symbols that passed -> creates a dict contains only the data for stock passed
        fundamental_results = self.screen_stocks(fundamental_criteria)
        fundamental_symbols = [stock['symbol'] for stock in fundamental_results]
        filtered_data = {symbol: self.stock_data[symbol] for symbol in fundamental_symbols if symbol in self.stock_data}
        
        # Create a temporary screener with only the filtered data
        temp_screener = StockScreener()
        temp_screener.stock_data = filtered_data
        
        # Apply technical criteria -> sort 
        technical_results = temp_screener.screen_by_technical(technical_criteria)
        technical_results.sort(key=lambda x: x.get('market_cap', 0), reverse=True)
        
        if limit:
            return technical_results[:limit]
  
        return technical_results

# Example 
if __name__ == "__main__":
    # first load symbol from an idx -> load data for the symbols
    screener = StockScreener()
    symbols = screener.data_fetcher.get_stock_symbols(index="sp500")[:50] 
    screener.load_data(symbols)
    
    # criteriafundamental screening  +  technical screening
    criteria = {
        'market_cap': ('>', 10e9),      # Market cap > $10 billion
        'pe_ratio': ('<', 20),          # P/E ratio < 20
        'dividend_yield': ('>', 0.02),  # Dividend yield > 2%
        'sector': 'Technology'          # In the Technology sector
    }
    
    results = screener.screen_stocks(criteria)
    
    print(f"Found {len(results)} stocks that match the criteria:")
    for stock in results:
        print(f"{stock['symbol']} - {stock['name']} (Market Cap: ${stock['market_cap']:,.0f})")
    
   
    tech_criteria = {
        'rsi': ('<', 40),            # RSI < 40 (potentially oversold)
        'sma_50_200': ('>', 1.0),    # 50-day SMA > 200-day SMA (bullish)
        'volume_avg': ('>', 1000000) # Average volume > 1M
    }
    
    tech_results = screener.screen_by_technical(tech_criteria)
    
    print(f"\nFound {len(tech_results)} stocks that match the technical criteria:")
    for stock in tech_results:
        print(f"{stock['symbol']} - {stock['name']} (Current Price: ${stock['price']:.2f})")