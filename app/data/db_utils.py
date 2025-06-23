import pandas as pd
from datetime import datetime, timedelta
import logging
from app.database.models import Stock, HistoricalPrice

# for interacting with database 

logger = logging.getLogger(__name__)

def load_from_database(symbol, session_factory, max_age_days=7):
    session = session_factory()
    try:
        # make sure not expired 
        cutoff_date = datetime.now().date() - timedelta(days=max_age_days)
        recent_count = session.query(HistoricalPrice)\
            .filter(HistoricalPrice.symbol == symbol)\
            .filter(HistoricalPrice.date >= cutoff_date)\
            .count()
        
        if recent_count < 1:
            return None
        
        historical_prices = session.query(HistoricalPrice)\
            .filter(HistoricalPrice.symbol == symbol)\
            .order_by(HistoricalPrice.date)\
            .all()
        
        if not historical_prices:
            return None
        data = []
        # loads all info to a dataframe 
        for price in historical_prices:
            data.append({
                'Date': price.date,
                'Open': price.open,
                'High': price.high,
                'Low': price.low,
                'Close': price.close,
                'Volume': price.volume,
                'Adj Close': price.adj_close
            })

        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

   
        stock = session.query(Stock).filter(Stock.symbol == symbol).first()

        stock_info = {
            'symbol': symbol,
            'shortName': stock.name if stock else symbol,
            'sector': stock.sector if stock else 'Unknown',
            'industry': stock.industry if stock else None,
            'marketCap': stock.market_cap if stock else None,
            'currentPrice': stock.current_price if stock else None,
            'peRatio': stock.pe_ratio if stock else None,
            'dividendYield': stock.dividend_yield if stock else None,
            'beta': stock.beta if stock else None,
        }

        if stock and stock.info:
            stock_info.update(stock.info)

        return {
            'historical': df,
            'info': stock_info,
            'last_updated': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error loading {symbol} from database: {e}")
        return None
    
    finally:
        session.close()

def save_to_database(symbol, data, session_factory):
    session = session_factory()
    from app.database.models import Stock, HistoricalPrice
    try:
        info = data.get('info', {})
        stock = session.query(Stock).filter(Stock.symbol == symbol).first()

        # query from yfinance 
        stock_fields = dict(
            symbol=symbol,
            name=info.get('shortName', symbol),
            sector=info.get('sector', None),
            industry=info.get('industry', None),
            market_cap=info.get('marketCap', None),
            current_price=info.get('currentPrice', None),
            pe_ratio=info.get('trailingPE', None),
            dividend_yield=info.get('dividendYield', None),
            beta=info.get('beta', None),
            info=info
        )

        # if stock not exist, create the entry based on fetched from yfinance 
        if not stock:
            stock = Stock(**stock_fields)
            session.add(stock)

        # if exist, update the field with fetched from yfinance  
        else:
            for k, v in stock_fields.items():
                setattr(stock, k, v)

        session.query(HistoricalPrice).filter(HistoricalPrice.symbol == symbol).delete()

        if 'historical' in data and not data['historical'].empty:
            hist_df = data['historical'].reset_index()
            prices_to_add = []
            
            for _, row in hist_df.iterrows():
                date_val = row['Date'].iloc[0] if isinstance(row['Date'], pd.Series) else row['Date']
                date_obj = pd.to_datetime(date_val).date() if not isinstance(date_val, datetime) else date_val.date()
                historical_price = HistoricalPrice(
                    symbol=symbol,
                    date=date_obj,
                    open=float(row['Open']) if pd.notna(row['Open']) else None,
                    high=float(row['High']) if pd.notna(row['High']) else None,
                    low=float(row['Low']) if pd.notna(row['Low']) else None,
                    close=float(row['Close']) if pd.notna(row['Close']) else None,
                    volume=int(row['Volume']) if pd.notna(row['Volume']) else None,
                    adj_close=float(row['Adj Close']) if 'Adj Close' in row and pd.notna(row['Adj Close']) else None
                )
                prices_to_add.append(historical_price)
            session.add_all(prices_to_add)
        session.commit()
        
    except Exception as e:
        logger.error(f"Error saving {symbol} to database: {e}")
        session.rollback()
    finally:
        session.close()

def debug_print_stock_data(symbol, session_factory):
    session = session_factory()
    from app.database.models import Stock, HistoricalPrice
    try:
        stock = session.query(Stock).filter(Stock.symbol == symbol).first()
        if stock:
            logger.info(f"Stock in database: {stock.symbol}, {stock.name}, {stock.sector}")
        else:
            logger.warning(f"No stock found for symbol {symbol}")
        prices = session.query(HistoricalPrice).filter(HistoricalPrice.symbol == symbol).all()
        logger.info(f"Found {len(prices)} historical prices for {symbol}")
        if prices:
            logger.info(f"Most recent price: {prices[-1].date} - Close: {prices[-1].close}")
    finally:
        session.close() 