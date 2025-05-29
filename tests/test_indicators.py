import unittest
import sys
import os

# Add the parent directory to the Python path so that app/ is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.indicators.indicators import TechnicalIndicators
import pandas as pd
import numpy as np

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

class TestTechnicalIndicators(unittest.TestCase):
    def test_moving_average(self):
        self.assertIsNotNone(TechnicalIndicators.moving_average(close))

    def test_exponential_moving_average(self):
        self.assertIsNotNone(TechnicalIndicators.exponential_moving_average(close))

    def test_relative_strength_index(self):
        self.assertIsNotNone(TechnicalIndicators.relative_strength_index(close))

    def test_macd(self):
        macd_line, signal_line, histogram = TechnicalIndicators.macd(close)
        self.assertIsNotNone(macd_line)
        self.assertIsNotNone(signal_line)
        self.assertIsNotNone(histogram)

    def test_bollinger_bands(self):
        upper, middle, lower = TechnicalIndicators.bollinger_bands(close)
        self.assertIsNotNone(upper)
        self.assertIsNotNone(middle)
        self.assertIsNotNone(lower)

    def test_average_true_range(self):
        self.assertIsNotNone(TechnicalIndicators.average_true_range(high, low, close))

    def test_on_balance_volume(self):
        self.assertIsNotNone(TechnicalIndicators.on_balance_volume(close, volume))

    def test_stochastic_oscillator(self):
        k, d = TechnicalIndicators.stochastic_oscillator(high, low, close)
        self.assertIsNotNone(k)
        self.assertIsNotNone(d)

    def test_rate_of_change(self):
        self.assertIsNotNone(TechnicalIndicators.rate_of_change(close))

if __name__ == '__main__':
    unittest.main()