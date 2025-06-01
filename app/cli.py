

import argparse
import json
import sys
import logging
from datetime import datetime
from app.screener.screener import StockScreener

# show time, logger name, level and msg 
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# criteria_str could be like "market_cap>1000000000, pe_ratio<20, sector=Technology
# returns the criteria as a dictionary 

def parse_criteria(criteria_str):
    if not criteria_str:
        return {}
    
    criteria = {}
    parts = criteria_str.split(',')
    
    for part in parts:
        part = part.strip()
        
        for op in ['>=', '<=', '>', '<', '==', '!=']:
            if op in part:
                field, value_str = part.split(op, 1)
                field = field.strip()
                value_str = value_str.strip()
                
                # Convert value type (string -> number)
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
            # No operator found, check for exact match -> value directly 
            if '=' in part:
                field, value = part.split('=', 1)
                field = field.strip()
                value = value.strip()
                
                criteria[field] = value
    
    return criteria


def main():
    parser = argparse.ArgumentParser(description='Stock Screener CLI')
    parser.add_argument('--index', choices=['sp500', 'nasdaq100', 'dow30'], default='sp500',
                        help='Stock index to use')
    parser.add_argument('--criteria', type=str, default='',
                        help='Screening criteria in format "field>value, field2<value2"')
    parser.add_argument('--limit', type=int, default=20,
                        help='Maximum number of results to return')
    parser.add_argument('--output', type=str, default='console',
                        choices=['console', 'json', 'csv'],
                        help='Output format')
    parser.add_argument('--output-file', type=str,
                        help='Output file for JSON or CSV output')
    parser.add_argument('--reload', action='store_true',
                        help='Force reload of stock data')

    args = parser.parse_args()
    
    # Create stock screener
    screener = StockScreener()

    logger.info(f"Getting symbols from {args.index}")
    symbols = screener.data_fetcher.get_stock_symbols(index=args.index)
    
    # Load data
    logger.info(f"Loading data for {len(symbols)} symbols (reload={args.reload})")
    screener.load_data(symbols, reload=args.reload)
    
    # criteria
    criteria = parse_criteria(args.criteria)
    
    if not criteria:
        logger.warning("No criteria specified. Using default criteria.")
        criteria = {
            'market_cap': ('>', 1e9),  # Market cap > $1 billion
            'pe_ratio': ('<', 30)      # P/E ratio < 30
        }
    
    logger.info(f"Screening with criteria: {criteria}")
    

    results = screener.screen_stocks(criteria, limit=args.limit)
    
    logger.info(f"Found {len(results)} matching stocks")
    
   # output formats - console, json, csv
    if args.output == 'console':
        print(f"\nFound {len(results)} stocks matching criteria:")
        print("=" * 80)
        # columns header: 
        print(f"{'Symbol':<10} {'Name':<30} {'Sector':<20} {'Market Cap':>15} {'Price':>10}")
        print("-" * 80)
        for stock in results:
            market_cap_str = f"${stock['market_cap']:,.0f}" if 'market_cap' in stock else 'N/A'
            price_str = f"${stock['price']:.2f}" if 'price' in stock else 'N/A'
            print(f"{stock.get('symbol', 'N/A'):<10} {stock.get('name', 'N/A')[:30]:<30} "
                  f"{stock.get('sector', 'N/A')[:20]:<20} {market_cap_str:>15} {price_str:>10}")
    
    elif args.output == 'json':
        output = json.dumps(results, indent=2)
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(output)
            logger.info(f"Results written to {args.output_file}")
        else:
            print(output)
    
    elif args.output == 'csv':
        import csv
        
        if not results:
            logger.error("No results to output")
            return
        
        # Get all fields from first result
        fields = list(results[0].keys())
        
        output_file = args.output_file or sys.stdout
        
        with open(output_file, 'w', newline='') if isinstance(output_file, str) else output_file as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(results)
        
        if args.output_file:
            logger.info(f"Results written to {args.output_file}")

if __name__ == "__main__":
    main()