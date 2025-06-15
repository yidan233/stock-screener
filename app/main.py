import os
import sys

# Add the project root to the Python path
# This ensures that modules within the 'app' directory can be imported correctly.
current_dir = os.path.dirname(os.path.abspath(__file__)) # Gets the directory of main.py (app/)
project_root = os.path.dirname(current_dir) # Goes up one level to the project root
sys.path.insert(0, project_root) # Inserts the project root at the beginning of sys.path

import argparse
import logging
# from app.api.routes import app # This import might cause issues if not available when starting
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
    # MODIFIED LINE: Added 'web' to the choices
    parser.add_argument('--mode', choices=['cli', 'api', 'web'], default='cli',
                        help='Running mode (cli, api, or web)')
    
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
        # Ensure this import is only done when in API mode to avoid issues
        from app.api.routes import app 
        app.run(debug=True, host='0.0.0.0', port=5000) # running at port 5000!
    # ADDED WEB MODE LOGIC
    elif args.mode == 'web':
        logger.info("Starting in Web mode (Streamlit)")
        import streamlit.web.cli as stcli
        # We need to set sys.argv to tell Streamlit which script to run
        # 'app/interface.py' will be the Streamlit application file
        sys.argv = ["streamlit", "run", "app/interface.py"] + remaining 
        stcli.main()

if __name__ == "__main__":
    main()