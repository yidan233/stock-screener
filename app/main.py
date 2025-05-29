# main.py
"""
Main entry point for the stock screener application.
"""

import argparse
import logging
import sys
from app.api import app

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Stock Screener')
    parser.add_argument('--mode', choices=['cli', 'api'], default='cli',
                        help='Running mode (cli or api)')
    
    # First parse just the mode
    args, remaining_argv = parser.parse_known_args()
    
    if args.mode == 'cli':
        logger.info("Starting in CLI mode")
        # Import the CLI module only if needed
        from cli import main as cli_main
        # Pass remaining arguments to the CLI
        sys.argv[1:] = remaining_argv
        cli_main()
    elif args.mode == 'api':
        logger.info("Starting in API mode")
        app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()