from sqlalchemy import Column, String, Float, Integer, Date, ForeignKey, JSON, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

# Create declarative base
Base = declarative_base()

class Stock(Base):
    __tablename__ = 'stocks'
    symbol = Column(String(10), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100), index=True)
    industry = Column(String(100))
    market_cap = Column(Float)
    current_price = Column(Float)
    pe_ratio = Column(Float)
    dividend_yield = Column(Float)
    beta = Column(Float)
    info = Column(JSON)  
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # one stock can have many historical prices (one to many )
    prices = relationship("HistoricalPrice", back_populates="stock", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Stock(symbol='{self.symbol}', name='{self.name}', sector='{self.sector}')>"

class HistoricalPrice(Base):
    __tablename__ = 'historical_prices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), ForeignKey('stocks.symbol', ondelete='CASCADE'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    adj_close = Column(Float)
    created_at = Column(DateTime, default=func.now())
    stock = relationship("Stock", back_populates="prices")
    
    # ensure no duplicate data 
    __table_args__ = (
        UniqueConstraint('symbol', 'date', name='uq_symbol_date'),
    )
    
    def __repr__(self):
        return f"<HistoricalPrice(symbol='{self.symbol}', date='{self.date}', close={self.close})>"

class ScreeningResult(Base):
    __tablename__ = 'screening_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    criteria_hash = Column(String(64), unique=True, index=True) 
    criteria = Column(JSON, nullable=False)  
    results = Column(JSON, nullable=False) 
    index_used = Column(String(20), nullable=False)
    execution_time = Column(Float)  
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)  
    
    def __repr__(self):
        return f"<ScreeningResult(criteria_hash='{self.criteria_hash}', index='{self.index_used}')>"

def create_tables(engine=None):
    if engine is None:
        from .connection import engine
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    # Only import engine when running directly
    from .connection import engine
    create_tables(engine)
    print("✅ Database tables created successfully!")