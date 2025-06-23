import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from sqlalchemy import text
from .connection import engine, get_db_session
from .models import Base, Stock, HistoricalPrice, ScreeningResult

logger = logging.getLogger(__name__)
def reset_database():
    try:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        logger.info("✅ Database reset successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        return False

def backup_database(backup_dir="backups"):
    try:
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"stock_screener_backup_{timestamp}.json")
        
        with get_db_session() as db:
            # export stock 
            stocks = db.query(Stock).all()
            stocks_data = []
            for stock in stocks:
                stock_dict = {
                    'symbol': stock.symbol,
                    'name': stock.name,
                    'sector': stock.sector,
                    'industry': stock.industry,
                    'market_cap': stock.market_cap,
                    'current_price': stock.current_price,
                    'pe_ratio': stock.pe_ratio,
                    'dividend_yield': stock.dividend_yield,
                    'beta': stock.beta,
                    'info': stock.info
                }
                stocks_data.append(stock_dict)
            
            # Export historical prices
            prices = db.query(HistoricalPrice).all()
            prices_data = []
            for price in prices:
                price_dict = {
                    'symbol': price.symbol,
                    'date': price.date.isoformat() if price.date else None,
                    'open': price.open,
                    'high': price.high,
                    'low': price.low,
                    'close': price.close,
                    'volume': price.volume,
                    'adj_close': price.adj_close
                }
                prices_data.append(price_dict)
            
   
            backup_data = {
                'timestamp': timestamp,
                'stocks_count': len(stocks_data),
                'prices_count': len(prices_data),
                'stocks': stocks_data,
                'historical_prices': prices_data
            }
            
            # Write to file
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            logger.info(f"✅ Database backup created: {backup_file}")
            return backup_file
            
    except Exception as e:
        logger.error(f"❌ Database backup failed: {e}")
        return None

def restore_database(backup_file):
    try:
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        with get_db_session() as db:
            db.query(HistoricalPrice).delete()
            db.query(Stock).delete()
            
            for stock_data in backup_data['stocks']:
                stock = Stock(**stock_data)
                db.add(stock)
            
            for price_data in backup_data['historical_prices']:
                if price_data['date']:
                    price_data['date'] = datetime.fromisoformat(price_data['date']).date()
                price = HistoricalPrice(**price_data)
                db.add(price)
            
            db.commit()
            
        logger.info(f"✅ Database restored from: {backup_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database restore failed: {e}")
        return False

def cleanup_expired_cache():
    try:
        with get_db_session() as db:
            expired_results = db.query(ScreeningResult).filter(
                ScreeningResult.expires_at < datetime.now()
            ).all()
            
            count = len(expired_results)
            for result in expired_results:
                db.delete(result)
            
            db.commit()
            logger.info(f"✅ Cleaned up {count} expired cache entries")
            return count
            
    except Exception as e:
        logger.error(f"❌ Cache cleanup failed: {e}")
        return 0

def get_database_stats():
    try:
        with get_db_session() as db:
            stats = {
                'stocks_count': db.query(Stock).count(),
                'prices_count': db.query(HistoricalPrice).count(),
                'cache_count': db.query(ScreeningResult).count(),
                'oldest_price': db.query(HistoricalPrice.date).order_by(HistoricalPrice.date).first(),
                'newest_price': db.query(HistoricalPrice.date).order_by(HistoricalPrice.date.desc()).first(),
            }
            
            sector_counts = db.query(Stock.sector, db.func.count(Stock.symbol)).group_by(Stock.sector).all()
            stats['sector_distribution'] = dict(sector_counts)
            
            return stats
            
    except Exception as e:
        logger.error(f"❌ Failed to get database stats: {e}")
        return None

def optimize_database():
    try:
        with engine.connect() as conn:
            if 'postgresql' in str(engine.url):
                conn.execute(text("VACUUM ANALYZE;")) # clean up deleted data and update stats
                conn.execute(text("REINDEX DATABASE stock_screener;")) # rebuild the idx 
            elif 'sqlite' in str(engine.url):
                conn.execute(text("VACUUM;"))
                conn.execute(text("ANALYZE;"))
            
            conn.commit()
            logger.info("✅ Database optimization completed!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Database optimization failed: {e}")
        return False

if __name__ == "__main__":
    print("Database Statistics:")
    stats = get_database_stats()
    if stats:
        print(json.dumps(stats, indent=2, default=str))
    
    print("\nCleaning up expired cache...")
    cleanup_expired_cache() 