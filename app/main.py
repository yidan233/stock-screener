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

    # Check if help is requested
    if '-h' in sys.argv or '--help' in sys.argv:
        from app.cli import main as cli_main
        cli_main()
        return

    parser = argparse.ArgumentParser(description='Stock Screener')
    parser.add_argument('--mode', choices=['cli', 'api'], default='cli',
                        help='Running mode (cli or api)')
    
    # Parse only the mode argument, ignore the rest
    args, remaining = parser.parse_known_args()
    
    if args.mode == 'cli':
        logger.info("Starting in CLI mode")
        from app.cli import main as cli_main
        # Pass remaining arguments to cli_main
        sys.argv = [sys.argv[0]] + remaining
        cli_main()
    elif args.mode == 'api':
        logger.info("Starting in API mode")
        app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()