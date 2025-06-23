import pandas as pd
import logging

logger = logging.getLogger(__name__)

# default to be sp500
def get_stock_symbols(index="sp500"):
    try:
        if index == "sp500":
            table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
            df = table[0]
            symbols = df['Symbol'].str.replace('.', '-').tolist()
            return symbols
        elif index == "nasdaq100":
            table = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')
            df = table[4]
            symbols = df['Ticker'].tolist()
            return symbols
        elif index == "dow30":
            table = pd.read_html('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average')
            df = table[2]
            symbols = df['Symbol'].tolist()
            return symbols
        else:
            logger.error(f"Unknown index: {index}, try sp500/dow30/nasdaq100")
            return []
    except Exception as e:
        logger.error(f"Error fetching symbols for {index}: {e}")
        raise  