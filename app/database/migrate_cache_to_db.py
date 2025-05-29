import os
import json
import pandas as pd
from datetime import datetime
import logging
from data_fetcher import DataFetcher
from database import SessionLocal, Stock, HistoricalPrice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_cache_to_db():
    """Migrate existing cache data to PostgreSQL database"""
    data_fetcher = DataFetcher()
    session = SessionLocal()
    
    try:
        # Get all cache files
        cache_files = [f for f in os.listdir('data') if f.startswith('stock_data_') and f.endswith('.json')]
        
        for cache_file in cache_files:
            logger.info(f"Processing cache file: {cache_file}")
            
            # Load cache data
            with open(os.path.join('data', cache_file), 'r') as f:
                cache_data = json.load(f)
            
            # Process each stock in the cache
            for symbol, stock_data in cache_data.items():
                try:
                    # Get stock info
                    info = stock_data.get('info', {})
                    
                    # Store stock info
                    stock = session.query(Stock).filter(Stock.symbol == symbol).first()
                    if not stock:
                        stock = Stock(
                            symbol=symbol,
                            name=info.get('shortName', ''),
                            sector=info.get('sector', '')
                        )
                        session.add(stock)
                    else:
                        stock.name = info.get('shortName', '')
                        stock.sector = info.get('sector', '')
                    
                    # Store historical prices
                    if 'historical' in stock_data:
                        hist_data = stock_data['historical']
                        for date_str, price_data in hist_data.items():
                            try:
                                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                                
                                # Check if we already have this data point
                                existing_price = session.query(HistoricalPrice).filter(
                                    HistoricalPrice.symbol == symbol,
                                    HistoricalPrice.date == date
                                ).first()
                                
                                if not existing_price:
                                    price = HistoricalPrice(
                                        symbol=symbol,
                                        date=date,
                                        open=float(price_data['Open']),
                                        high=float(price_data['High']),
                                        low=float(price_data['Low']),
                                        close=float(price_data['Close']),
                                        volume=int(price_data['Volume'])
                                    )
                                    session.add(price)
                            except Exception as e:
                                logger.error(f"Error processing historical data for {symbol} on {date_str}: {e}")
                                continue
                    
                    # Commit changes for this stock
                    session.commit()
                    logger.info(f"Successfully migrated data for {symbol}")
                    
                except Exception as e:
                    logger.error(f"Error processing stock {symbol}: {e}")
                    session.rollback()
                    continue
        
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    migrate_cache_to_db() 