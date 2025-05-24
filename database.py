from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Use your actual password below
DATABASE_URL = "postgresql+psycopg2://postgres:Dd123546879@localhost/stock_screener"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            print("✅ Connected to the database successfully!")
    except Exception as e:
        print("❌ Connection failed:", e)

from sqlalchemy import Column, String, Float, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship

class Stock(Base):
    __tablename__ = 'stocks'
    symbol = Column(String, primary_key=True)
    name = Column(String)
    sector = Column(String)

class HistoricalPrice(Base):
    __tablename__ = 'historical_prices'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, ForeignKey('stocks.symbol'))
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    stock = relationship("Stock", back_populates="prices")

Stock.prices = relationship("HistoricalPrice", order_by=HistoricalPrice.date, back_populates="stock")