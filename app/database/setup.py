import logging
from sqlalchemy import text
from .connection import engine, test_connection
from .models import Base, create_tables

logger = logging.getLogger(__name__)

def setup_database():
    try:
        if not test_connection():
            raise Exception("Database connection failed")
        
        create_tables(engine)
        logger.info("✅ Database tables created successfully!")
        
        create_indexes()
        logger.info("✅ Database indexes created successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        raise

def create_indexes():
    try:
        with engine.connect() as conn:
           # find prices by date quickly 
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_historical_prices_date 
                ON historical_prices (date);
            """))
            
            # stock sybol 
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_historical_prices_symbol 
                ON historical_prices (symbol);
            """))
            
            # symbol + date queries
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_historical_prices_symbol_date 
                ON historical_prices (symbol, date);
            """))
            
            # sector 
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_stocks_sector 
                ON stocks (sector);
            """))
            
            # industryy 
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_stocks_industry 
                ON stocks (industry);
            """))
            
            # screening results
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_screening_results_criteria_hash 
                ON screening_results (criteria_hash);
            """))
            
            # result expire 
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_screening_results_expires_at 
                ON screening_results (expires_at);
            """))
            
            conn.commit()
            logger.info("✅ Database indexes created successfully!")
            
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {e}")
        raise

def validate_database():
    try:
        if not test_connection():
            return False, "Database connection failed"
       
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'stocks'
            """))
            if result.scalar() == 0:
                return False, "Stocks table not found"
            
            
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'historical_prices'
            """))
            if result.scalar() == 0:
                return False, "Historical_prices table not found"
            
           
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'screening_results'
            """))
            if result.scalar() == 0:
                return False, "Screening_results table not found"
        
        return True, "Database validation successful"
        
    except Exception as e:
        return False, f"Database validation failed: {e}"

if __name__ == "__main__":
    try:
        success = setup_database()
        if success:
            print("✅ Database setup completed successfully!")
            
            is_valid, message = validate_database()
            if is_valid:
                print("✅ Database validation passed!")
            else:
                print(f"❌ Database validation failed: {message}")
        else:
            print("❌ Database setup failed!")
    except Exception as e:
        print(f"❌ Error during database setup: {e}") 