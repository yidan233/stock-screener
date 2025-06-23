from typing import Dict, Any, List
import logging
import operator
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

OPERATORS = {
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne
}

def screen_by_technical(stock_data: Dict[str, Any], indicators, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not stock_data:
        raise ValueError("No stock data loaded. Call load_data first.")

    results = []

    for symbol, data in stock_data.items():
        if 'historical' not in data or data['historical'].empty:
            continue

        hist = data['historical']
        meets_criteria = True

        for indicator, condition in criteria.items():
            op_symbol, threshold = condition
            op_func = OPERATORS.get(op_symbol)

            try:
                if indicator == 'ma':
                    ma = indicators.moving_average(hist['Close'])
                    if ma is None or ma.empty or pd.isna(ma.iloc[-1]):
                        meets_criteria = False
                        break
                    value = ma.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                elif indicator == 'ema':
                    ema = indicators.exponential_moving_average(hist['Close'])
                    if ema is None or ema.empty or pd.isna(ema.iloc[-1]):
                        meets_criteria = False
                        break
                    value = ema.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                elif indicator == 'rsi':
                    rsi = indicators.relative_strength_index(hist['Close'])
                    if rsi is None or rsi.empty or pd.isna(rsi.iloc[-1]):
                        meets_criteria = False
                        break
                    value = rsi.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                elif indicator == 'macd_hist':
                    macd_line, signal_line, histogram = indicators.macd(hist['Close'])
                    if histogram is None or histogram.empty or pd.isna(histogram.iloc[-1]):
                        meets_criteria = False
                        break
                    value = histogram.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                elif indicator == 'boll_upper':
                    upper, middle, lower = indicators.bollinger_bands(hist['Close'])
                    if upper is None or upper.empty or pd.isna(upper.iloc[-1]):
                        meets_criteria = False
                        break
                    price = hist['Close'].iloc[-1]
                    value = price - upper.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                elif indicator == 'boll_lower':
                    upper, middle, lower = indicators.bollinger_bands(hist['Close'])
                    if lower is None or lower.empty or pd.isna(lower.iloc[-1]):
                        meets_criteria = False
                        break
                    price = hist['Close'].iloc[-1]
                    value = price - lower.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                elif indicator == 'atr':
                    atr = indicators.average_true_range(hist['High'], hist['Low'], hist['Close'])
                    if atr is None or atr.empty or pd.isna(atr.iloc[-1]):
                        meets_criteria = False
                        break
                    value = atr.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                elif indicator == 'obv':
                    obv = indicators.on_balance_volume(hist['Close'], hist['Volume'])
                    if obv is None or obv.empty or pd.isna(obv.iloc[-1]):
                        meets_criteria = False
                        break
                    value = obv.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                elif indicator == 'stoch_k':
                    k, d = indicators.stochastic_oscillator(hist['High'], hist['Low'], hist['Close'])
                    if k is None or k.empty or pd.isna(k.iloc[-1]):
                        meets_criteria = False
                        break
                    value = k.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                elif indicator == 'stoch_d':
                    k, d = indicators.stochastic_oscillator(hist['High'], hist['Low'], hist['Close'])
                    if d is None or d.empty or pd.isna(d.iloc[-1]):
                        meets_criteria = False
                        break
                    value = d.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

                elif indicator == 'roc':
                    roc = indicators.rate_of_change(hist['Close'])
                    if roc is None or roc.empty or pd.isna(roc.iloc[-1]):
                        meets_criteria = False
                        break
                    value = roc.iloc[-1]
                    if not op_func(value, threshold):
                        meets_criteria = False
                        break

            except Exception as e:
                logger.warning(f"Error calculating {indicator} for {symbol}: {e}")
                meets_criteria = False
                break

        if meets_criteria:
            info = data.get('info', {})
            results.append({
                'symbol': symbol,
                'name': info.get('shortName', 'Unknown'),
                'sector': info.get('sector', 'Unknown'),
                'price': hist['Close'].iloc[-1],
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE')
            })

    return results 