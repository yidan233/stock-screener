import argparse
import logging
import sys
from app.api.routes import app
from app.database.setup import setup_database

# Set up logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Initialize database first
    try:
        setup_database()
        logger.info("✅ Database initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Stock Screener')
    parser.add_argument('--mode', choices=['cli', 'api'], default='cli',
                        help='Running mode (cli or api)')
    
    # Add CLI arguments to main parser
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
    
    if args.mode == 'cli':
        logger.info("Starting in CLI mode")
        from app.cli import main as cli_main
        cli_main(args)  # Pass the parsed args to CLI
    elif args.mode == 'api':
        logger.info("Starting in API mode")
        app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()