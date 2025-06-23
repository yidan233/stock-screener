import argparse
import json
import sys
import logging
import csv
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.screener import StockScreener
from app.data import get_stock_symbols

# level is set to info! 
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_criteria(criteria_str: str) -> Dict[str, Any]:
    """
        
    Examples:
        input should be like "market_cap>1000000000,pe_ratio<20,sector=Technology"
        expected output: 
        {'market_cap': ('>', 1000000000), 'pe_ratio': ('<', 20), 'sector': 'Technology'}
    """
    if not criteria_str:
        return {}
    
    criteria = {}
    parts = criteria_str.split(',')
    
    for part in parts:
        part = part.strip()
        
        for op in ['>=', '<=', '>', '<', '==', '!=']:
            if op in part:
                field, value_str = part.split(op, 1) # split at the first occurance of op
                field = field.strip()
                value_str = value_str.strip()
                
               # convert type from string to int 
                try:
                    if '.' in value_str:
                        value = float(value_str)
                    else:
                        value = int(value_str)
                except ValueError:
                    value = value_str
                
                criteria[field] = (op, value)
                break
        else:
            if '=' in part:
                field, value = part.split('=', 1)
                field = field.strip()
                value = value.strip()
                criteria[field] = value
    
    return criteria


def display_console_results(results: List[Dict[str, Any]], criteria: Dict[str, Any]) -> None:
    print(f"\nFound {len(results)} stocks matching criteria:")
    print("=" * 100)
    
    # Column headers
    print(f"{'Symbol':<8} {'Name':<25} {'Sector':<15} {'Market Cap':>15} {'Price':>10} {'P/E':>8}")
    print("-" * 100)
    
    for stock in results:
        symbol = stock.get('symbol', 'N/A')
        name = (stock.get('name') or 'N/A')[:25]  
        sector = (stock.get('sector') or 'N/A')[:15]  
        
      
        market_cap = stock.get('market_cap', 0)
        market_cap_str = f"${market_cap:,.0f}" if market_cap else 'N/A'
        

        price = stock.get('price', 0)
        price_str = f"${price:.2f}" if price else 'N/A'
        

        pe_ratio = stock.get('pe_ratio', 0)
        pe_str = f"{pe_ratio:.1f}" if pe_ratio else 'N/A'
        
        print(f"{symbol:<8} {name:<25} {sector:<15} {market_cap_str:>15} {price_str:>10} {pe_str:>8}")


def save_json_results(results: List[Dict[str, Any]], output_file: Optional[str]) -> None:
    output = json.dumps(results, indent=2)
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output)
        logger.info(f"Results written to {output_file}")
    else:
        print(output)


def save_csv_results(results: List[Dict[str, Any]], output_file: Optional[str]) -> None:
    if not results:
        logger.error("No results to output")
        return
    
    # Filter out any None or invalid results
    valid_results = [r for r in results if r and isinstance(r, dict)]
    
    if not valid_results:
        logger.error("No valid results to output")
        return
    
    fields = list(valid_results[0].keys())
    
    if output_file:
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(valid_results)
        logger.info(f"Results written to {output_file}")
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(valid_results)


def main():
   
    parser = argparse.ArgumentParser(
        description='Stock Screener CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fundamental screening
  python -m app.main --mode cli --fundamental "market_cap>1000000000,pe_ratio<20"
  
  # Technical screening  
  python -m app.main --mode cli --technical "rsi<30,ma>100"
  
  # Combined screening
  python -m app.main --mode cli --fundamental "sector=Technology" --technical "rsi>0"
  
  # Save to file
  python -m app.main --mode cli --fundamental "market_cap>1000000000" --output json --output-file results.json
  
  # Different indices
  python -m app.main --mode cli --fundamental "market_cap>1000000000" --index dow30

        """
    )
    
    # Index selection
    parser.add_argument(
        '--index', 
        choices=['sp500', 'nasdaq100', 'dow30'], 
        default='sp500',
        help='Stock index to use (default: sp500)'
    )
    
    # Screening criteria
    parser.add_argument(
        '--fundamental', 
        type=str, 
        default='',
        help='Fundamental screening criteria (e.g., "market_cap>1000000000,pe_ratio<20")'
    )
    parser.add_argument(
        '--technical', 
        type=str, 
        default='',
        help='Technical screening criteria (e.g., "rsi<30,ma>100")'
    )
    
    # Output options
    parser.add_argument(
        '--limit', 
        type=int, 
        default=20,
        help='Maximum number of results to return (default: 20)'
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default='console',
        choices=['console', 'json', 'csv'],
        help='Output format (default: console)'
    )
    parser.add_argument(
        '--output-file', 
        type=str,
        help='Output file for JSON or CSV output'
    )
    
    # Data options
    parser.add_argument(
        '--reload', 
        action='store_true',
        help='Force reload of stock data (ignore cached data)'
    )
    parser.add_argument(
        '--period', 
        type=str, 
        default='1mo',
        choices=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
        help='Data period to fetch (default: 1mo)'
    )
    parser.add_argument(
        '--interval', 
        type=str, 
        default='1d',
        choices=['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'],
        help='Data interval (default: 1d)'
    )

    args = parser.parse_args()
    
    try:
      
        screener = StockScreener()
        
       
        logger.info(f"Getting symbols from {args.index}")
        symbols = get_stock_symbols(index=args.index)
        logger.info(f"Found {len(symbols)} symbols")
        
      
        logger.info(f"Loading data for {len(symbols)} symbols (reload={args.reload})")
        screener.load_data(
            symbols=symbols, 
            reload=args.reload,
            period=args.period,
            interval=args.interval
        )
        
      
        fundamental_criteria = parse_criteria(args.fundamental)
        technical_criteria = parse_criteria(args.technical)
        
       
        # Initialize results
        results = []
        
        if fundamental_criteria and technical_criteria:
            # Combined screening
            logger.info(f"Performing combined screening")
            logger.info(f"Fundamental criteria: {fundamental_criteria}")
            logger.info(f"Technical criteria: {technical_criteria}")
            
            results = screener.create_combined_screen(
                fundamental_criteria, 
                technical_criteria, 
                limit=args.limit
            )
            
        elif technical_criteria:
            logger.info(f"Performing technical screening with criteria: {technical_criteria}")
            results = screener.screen_by_technical(technical_criteria)
            if args.limit and results:
                results = results[:args.limit]
                
        elif fundamental_criteria:
            logger.info(f"Performing fundamental screening with criteria: {fundamental_criteria}")
            results = screener.screen_stocks(fundamental_criteria, limit=args.limit)
            
        else:
            # Default criteria
            logger.warning("No criteria specified. Using default fundamental criteria.")
            default_criteria = {
                'market_cap': ('>', 1e9),  # Market cap > $1 billion
                'pe_ratio': ('<', 30)      # P/E ratio < 30
            }
            results = screener.screen_stocks(default_criteria, limit=args.limit)
        
        # Ensure results is a list and filter out None values
        if results is None:
            results = []
        else:
            results = [r for r in results if r is not None]
        
        logger.info(f"Found {len(results)} matching stocks")
        
        # Output results
        if args.output == 'console':
            display_console_results(results, fundamental_criteria or technical_criteria)
        elif args.output == 'json':
            save_json_results(results, args.output_file)
        elif args.output == 'csv':
            save_csv_results(results, args.output_file)
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error("Please check your criteria and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()