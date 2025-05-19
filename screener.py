# screener.py
"""
Stock screener module with various screening strategies.
"""

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
    """Class for screening stocks with advanced filtering capabilities."""
    
    # Define comparison operators
    OPERATORS = {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne
    }
    
    def __init__(self):
        """Initialize the stock screener."""
        self.data_fetcher = DataFetcher()
        self.indicators = TechnicalIndicators()
        self.stock_data = {}
    
    def load_data(self, symbols=None, reload=False, period="1y", interval="1d"):
        """
        Load stock data for screening.
        
        Args:
            symbols (list): List of stock symbols. If None, will use S&P 500.
            reload (bool): Force reload of data even if in cache
            period (str): Time period for historical data
            interval (str): Data interval
            
        Returns:
            dict: Dictionary with stock data
        """
        # Use S&P 500 if no symbols provided
        if symbols is None:
            symbols = self.data_fetcher.get_stock_symbols(index="sp500")
            logger.info(f"Loaded {len(symbols)} symbols from S&P 500")
        
        # Check if we can load from cache
        cache_file = f"stock_data_{period}_{interval}.json"
        cache_metadata_file = f"stock_data_{period}_{interval}_metadata.json"
        
        if not reload:
            # Try to load data from cache
            metadata = self.data_fetcher.load_from_cache(cache_metadata_file)
            
            if metadata is not None:
                # Check if we have all the symbols we need
                cached_symbols = set(metadata.get('symbols', []))
                requested_symbols = set(symbols)
                
                if requested_symbols.issubset(cached_symbols):
                    # We have all the symbols in cache, load the data
                    self.stock_data = self.data_fetcher.load_from_cache(cache_file)
                    if self.stock_data is not None:
                        logger.info(f"Loaded {len(self.stock_data)} stocks from cache")
                        return self.stock_data
        
        # If we get here, we need to fetch the data
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
    
    def apply_criteria(self, stock_info, criteria):
        """
        Apply screening criteria to a stock.
        
        Args:
            stock_info (dict): Stock information dictionary
            criteria (dict): Dictionary of criteria with operators
                Example: {
                    'market_cap': ('>', 1e9),  # Market cap > $1 billion
                    'pe_ratio': ('<', 20),     # P/E ratio < 20
                    'dividend_yield': ('>=', 0.02)  # Dividend yield >= 2%
                }
                
        Returns:
            bool: True if stock meets all criteria, False otherwise
        """
        # Field mapping from criteria names to stock_info keys
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
            # Add more mappings as needed
        }
        
        # Special case for exact match fields
        exact_match_fields = ['sector', 'industry', 'country']
        
        for field, condition in criteria.items():
            # Handle exact match fields
            if field in exact_match_fields:
                expected_value = condition
                actual_value = stock_info.get(field, '')
                if actual_value != expected_value:
                    return False
                continue
            
            # Handle operator-based comparisons
            if isinstance(condition, tuple) and len(condition) == 2:
                op_symbol, threshold = condition
                
                # Get the actual field name in the stock_info dictionary
                info_field = field_mapping.get(field, field)
                actual_value = stock_info.get(info_field)
                
                # Skip if the field doesn't exist
                if actual_value is None:
                    return False
                
                # Get the operator function
                op_func = self.OPERATORS.get(op_symbol)
                if op_func is None:
                    logger.error(f"Unknown operator: {op_symbol}")
                    return False
                
                # Apply the comparison
                if not op_func(actual_value, threshold):
                    return False
        
        # If we get here, all criteria are satisfied
        return True
    
    def screen_stocks(self, criteria, limit=None):
        """
        Screen stocks based on the given criteria with flexible operators.
        
        Args:
            criteria (dict): Dictionary of criteria with operators
            limit (int): Maximum number of results to return
                
        Returns:
            list: List of stock symbols that meet the criteria
        """
        if not self.stock_data:
            raise ValueError("No stock data loaded. Call load_data first.")
        
        results = []
        
        for symbol, data in self.stock_data.items():
            info = data.get('info', {})
            
            # Apply the criteria
            if self.apply_criteria(info, criteria):
                results.append({
                    'symbol': symbol,
                    'name': info.get('shortName', 'Unknown'),
                    'sector': info.get('sector', 'Unknown'),
                    'market_cap': info.get('marketCap', 0),
                    'price': info.get('currentPrice', 0)
                })
        
        # Sort results by market cap (descending)
        results.sort(key=lambda x: x['market_cap'], reverse=True)
        
        # Limit the number of results if specified
        if limit is not None:
            results = results[:limit]
        
        return results
    
    def screen_by_technical(self, criteria):
        """
        Screen stocks by technical indicators.
        
        Args:
            criteria (dict): Dictionary of technical criteria
                Example: {
                    'rsi': ('<', 30),  # RSI < 30 (oversold)
                    'sma_50_200': ('>', 1.05),  # 50-day SMA > 1.05 * 200-day SMA (golden cross)
                    'volume_avg': ('>', 1000000)  # Average volume > 1M
                }
                
        Returns:
            list: List of stock symbols that meet the criteria
        """
        if not self.stock_data:
            raise ValueError("No stock data loaded. Call load_data first.")
        
        results = []
        
        for symbol, data in self.stock_data.items():
            # Skip if we don't have historical data
            if 'historical' not in data or data['historical'].empty:
                continue
            
            hist = data['historical']
            
            # Calculate all technical indicators we need
            tech_data = {}
            
            # Check each criterion
            meets_criteria = True
            
            for indicator, condition in criteria.items():
                op_symbol, threshold = condition
                op_func = self.OPERATORS.get(op_symbol)
                
                if indicator == 'rsi':
                    # Calculate RSI
                    rsi = self.indicators.relative_strength_index(hist['Close'])
                    # Get the latest value
                    value = rsi.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break
                
                elif indicator == 'sma_50_200':
                    # Calculate 50-day and 200-day SMAs
                    sma_50 = self.indicators.moving_average(hist['Close'], window=50)
                    sma_200 = self.indicators.moving_average(hist['Close'], window=200)
                    # Calculate the ratio of 50-day to 200-day SMA
                    ratio = sma_50.iloc[-1] / sma_200.iloc[-1]
                    if not op_func(ratio, threshold):
                        meets_criteria = False
                        break
                
                elif indicator == 'volume_avg':
                    # Calculate average volume
                    avg_volume = hist['Volume'].mean()
                    if not op_func(avg_volume, threshold):
                        meets_criteria = False
                        break
                
                elif indicator == 'price_to_sma_200':
                    # Calculate 200-day SMA
                    sma_200 = self.indicators.moving_average(hist['Close'], window=200)
                    # Calculate the ratio of current price to 200-day SMA
                    current_price = hist['Close'].iloc[-1]
                    ratio = current_price / sma_200.iloc[-1]
                    if not op_func(ratio, threshold):
                        meets_criteria = False
                        break
                
                # Add more technical indicators as needed
            
            if meets_criteria:
                info = data.get('info', {})
                results.append({
                    'symbol': symbol,
                    'name': info.get('shortName', 'Unknown'),
                    'sector': info.get('sector', 'Unknown'),
                    'price': hist['Close'].iloc[-1]
                })
        
        return results
    
    def create_combined_screen(self, fundamental_criteria, technical_criteria, limit=50):
        """
        Create a combined screen with both fundamental and technical criteria.
        
        Args:
            fundamental_criteria (dict): Fundamental criteria
            technical_criteria (dict): Technical criteria
            limit (int): Maximum number of results
            
        Returns:
            list: List of stocks meeting all criteria
        """
        # First screen by fundamental criteria
        fundamental_results = self.screen_stocks(fundamental_criteria)
        
        # Get symbols from fundamental results
        fundamental_symbols = [stock['symbol'] for stock in fundamental_results]
        
        # Filter the data to include only these symbols
        filtered_data = {symbol: self.stock_data[symbol] for symbol in fundamental_symbols if symbol in self.stock_data}
        
        # Create a temporary screener with only the filtered data
        temp_screener = StockScreener()
        temp_screener.stock_data = filtered_data
        
        # Apply technical criteria
        technical_results = temp_screener.screen_by_technical(technical_criteria)
        
        # Sort and limit results
        technical_results.sort(key=lambda x: x.get('market_cap', 0), reverse=True)
        
        if limit:
            return technical_results[:limit]
        # screener.py (continued)
        return technical_results

# Example usage
if __name__ == "__main__":
    # Create a stock screener instance
    screener = StockScreener()
    
    # Define a list of stock symbols or load from an index
    symbols = screener.data_fetcher.get_stock_symbols(index="sp500")[:50]  # First 50 S&P 500 stocks for quick testing
    
    # Load data for these symbols
    screener.load_data(symbols)
    
    # Define screening criteria with operators
    criteria = {
        'market_cap': ('>', 10e9),      # Market cap > $10 billion
        'pe_ratio': ('<', 20),          # P/E ratio < 20
        'dividend_yield': ('>', 0.02),  # Dividend yield > 2%
        'sector': 'Technology'          # In the Technology sector
    }
    
    # Screen stocks based on the criteria
    results = screener.screen_stocks(criteria)
    
    print(f"Found {len(results)} stocks that match the criteria:")
    for stock in results:
        print(f"{stock['symbol']} - {stock['name']} (Market Cap: ${stock['market_cap']:,.0f})")
    
    # Example of technical screening
    tech_criteria = {
        'rsi': ('<', 40),            # RSI < 40 (potentially oversold)
        'sma_50_200': ('>', 1.0),    # 50-day SMA > 200-day SMA (bullish)
        'volume_avg': ('>', 1000000) # Average volume > 1M
    }
    
    tech_results = screener.screen_by_technical(tech_criteria)
    
    print(f"\nFound {len(tech_results)} stocks that match the technical criteria:")
    for stock in tech_results:
        print(f"{stock['symbol']} - {stock['name']} (Current Price: ${stock['price']:.2f})")