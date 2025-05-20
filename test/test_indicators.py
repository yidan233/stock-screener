import pandas as pd
import numpy as np
from indicators import TechnicalIndicators

# Create example data
np.random.seed(0)
dates = pd.date_range('2023-01-01', periods=100)
close = pd.Series(np.random.normal(100, 2, size=100), index=dates)
high = close + np.random.uniform(0, 2, size=100)
low = close - np.random.uniform(0, 2, size=100)
volume = pd.Series(np.random.randint(1000, 5000, size=100), index=dates)

print("Moving Average:", TechnicalIndicators.moving_average(close).dropna().head())
print("Exponential Moving Average:", TechnicalIndicators.exponential_moving_average(close).dropna().head())
print("RSI:", TechnicalIndicators.relative_strength_index(close).dropna().head())
macd_line, signal_line, histogram = TechnicalIndicators.macd(close)
print("MACD line:", macd_line.dropna().head())
print("Signal line:", signal_line.dropna().head())
print("MACD Histogram:", histogram.dropna().head())
upper, middle, lower = TechnicalIndicators.bollinger_bands(close)
print("Bollinger Bands Upper:", upper.dropna().head())
print("ATR:", TechnicalIndicators.average_true_range(high, low, close).dropna().head())
print("OBV:", TechnicalIndicators.on_balance_volume(close, volume).dropna().head())
k, d = TechnicalIndicators.stochastic_oscillator(high, low, close)
print("Stochastic %K:", k.dropna().head())
print("Stochastic %D:", d.dropna().head())
print("ROC:", TechnicalIndicators.rate_of_change(close).dropna().head())