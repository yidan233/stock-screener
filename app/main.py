import os
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root) 

import argparse
import logging
from app.database.setup import setup_database


logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        setup_database()
        logger.info("✅ Database initialized successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        sys.exit(1)

    # help argument 
    if '-h' in sys.argv or '--help' in sys.argv:
        from app.cli import main as cli_main
        cli_main()
        return

    parser = argparse.ArgumentParser(description='Stock Screener')
   
    parser.add_argument('--mode', choices=['cli', 'api'], default='cli',
                        help='Running mode (cli or api)')
    
  
    args, remaining = parser.parse_known_args()
    

    # mode 1: command line interface 
    if args.mode == 'cli':
        logger.info("Starting in CLI mode")
        from app.cli import main as cli_main
     
        sys.argv = [sys.argv[0]] + remaining
        cli_main()

    # mode 2: API 
    elif args.mode == 'api':
        logger.info("Starting in API mode")
        from app.api import app 
        app.run(debug=True, host='0.0.0.0', port=5000) # running at port 5000!


if __name__ == "__main__":
    main()