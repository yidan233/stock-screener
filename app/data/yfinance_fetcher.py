import pandas as pd
import yfinance as yf
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

# use yfinance to fetech data info 
# default: period = 1 year, interval = 1d 
def fetch_yfinance_data(symbols, period="1y", interval="1d", reload=False, load_from_db=None, save_to_db=None):

    result = {}
    symbols_to_fetch = []

    if isinstance(symbols, str):
        symbols = [symbols]

    # if reload == True, I will need to fetch the fresh stock symbol 
    if reload:
        symbols_to_fetch = symbols

    else:
        for symbol in symbols:
            # could find the symbol from the cache -> load and add to result 
            cached_data = load_from_db(symbol) if load_from_db else None
            if cached_data:
                result[symbol] = cached_data
            # couldnt? -> fetch !
            else:
                symbols_to_fetch.append(symbol)
    
    if symbols_to_fetch:
        logger.info(f"Fetching fresh data for {len(symbols_to_fetch)} symbols: {symbols_to_fetch}")
        fresh_data = _fetch_fresh_data(symbols_to_fetch, period, interval)
        for symbol, data in fresh_data.items():
            if data:
                if 'historical' in data and isinstance(data['historical'], pd.DataFrame):
                    if not isinstance(data['historical'].index, pd.DatetimeIndex):
                        data['historical'].index = pd.to_datetime(data['historical'].index)
                    result[symbol] = data
                    if save_to_db:
                        save_to_db(symbol, data)
    return result

def _fetch_fresh_data(symbols, period="1y", interval="1d"):
    result = {}

    if isinstance(symbols, str):
        symbols = [symbols]
    
    # split the fresh data from yfinance into batches of size 20 
    batch_size = 20
    symbol_batches = [symbols[i:i + batch_size] for i in range(0, len(symbols), batch_size)]

    for batch in symbol_batches:
        try:
            tickers_str = batch[0] if len(batch) == 1 else batch

            data = yf.download(
                tickers=tickers_str,
                period=period,
                interval=interval,
                group_by='ticker',
                auto_adjust=True,
                prepost=False,
                threads=True
            )

            for symbol in batch:
                try:
                    symbol_data = data if len(batch) == 1 else data[symbol]
                    if symbol_data.empty:
                        logger.warning(f"No data available for {symbol}")
                        continue

                    symbol_data = symbol_data.dropna()
                    if symbol_data.empty:
                        logger.warning(f"No valid data available for {symbol} after removing NaN values")
                        continue
                    
                    # standarlize the return result 
                    # if return (APPL, OPEN) -> APPL_OPEN
                    # join with underscore like APPL_open 
                    if isinstance(symbol_data.columns, pd.MultiIndex):
                        symbol_data.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in symbol_data.columns.values]
                        logger.info(f"Flattened MultiIndex columns for {symbol}: {symbol_data.columns.tolist()}")
                    column_rename_map = {}

                    # creae a dict {APPL_Open: Open}
                    for col in symbol_data.columns:
                        if col.startswith(f'{symbol}_'):
                            standard_col_name = col[len(f'{symbol}_'):]
                            column_rename_map[col] = standard_col_name
                    # rename it 
                    if column_rename_map:
                        symbol_data = symbol_data.rename(columns=column_rename_map)
                        logger.info(f"Renamed symbol-prefixed columns for {symbol}: {symbol_data.columns.tolist()}")

                    result[symbol] = {
                        'historical': symbol_data,
                        'last_updated': datetime.now().isoformat()
                    }

                    try:
                        ticker = yf.Ticker(symbol)
                        info = ticker.info
                        if info:
                            result[symbol]['info'] = info
                    except Exception as e:
                        logger.warning(f"Could not fetch info for {symbol}: {e}")
                        result[symbol]['info'] = {'symbol': symbol}
                    try:
                        ticker = yf.Ticker(symbol)
                        result[symbol]['financials'] = {
                            'income_statement': ticker.income_stmt,
                            'balance_sheet': ticker.balance_sheet,
                            'cash_flow': ticker.cashflow
                        }
                    except Exception as e:
                        logger.warning(f"Could not fetch financial statements for {symbol}: {e}")
                except Exception as e:
                    logger.error(f"Error processing data for {symbol}: {e}")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error fetching data for batch {batch}: {e}")
    return result 