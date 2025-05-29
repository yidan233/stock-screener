from app.database.models import Base
from app.database.models import engine
from sqlalchemy import text

def setup_database():
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create indexes for better query performance
    with engine.connect() as conn:
        # Index on historical_prices date for faster date-based queries
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_historical_prices_date 
            ON historical_prices (date);
        """))
        
        # Index on historical_prices symbol for faster symbol-based queries
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_historical_prices_symbol 
            ON historical_prices (symbol);
        """))
        
        # Index on stocks sector for faster sector-based queries
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_stocks_sector 
            ON stocks (sector);
        """))
        
        conn.commit()

if __name__ == "__main__":
    try:
        setup_database()
        print("✅ Database and tables created successfully!")
    except Exception as e:
        print("❌ Error setting up database:", e) 