import os
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from app.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# only WARNING log will be printed 
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# check crendials 
def get_database_url():
    if DB_PASSWORD:
        return f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        return "sqlite:///./stock_screener.db"

# Configuration 
engine = create_engine(
    get_database_url(),
    echo=False, # true for debugging 
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True, 
    pool_recycle=3600,   
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()

def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful!")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection() 