import numpy as np
import pandas as pd

# current indicators are
# 1. Moving Average
# 2. Exponential Moving Average
# 3. Relative Strength Index (RSI)
# 4. Moving Average Convergence Divergence (MACD)
# 5. Bollinger Bands
# 6. Average True Range (ATR)
# 7. On-Balance Volume (OBV)
# 8. Stochastic Oscillator
# 9. Rate of Change (ROC)


# TASK TO COMPLETE: currently we are using the default parameter
# should allows user to input their own parameter 
class TechnicalIndicators:
  
    @staticmethod
    def moving_average(data, window=20):
        return data.rolling(window=window).mean()
    
    @staticmethod
    def exponential_moving_average(data, span=20):
        return data.ewm(span=span, adjust=False).mean()
    
    @staticmethod
    def relative_strength_index(data, window=14):
        delta = data.diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
       
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
       
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(data, fast_period=12, slow_period=26, signal_period=9):
        ema_fast = data.ewm(span=fast_period, adjust=False).mean()
        ema_slow = data.ewm(span=slow_period, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(data, window=20, num_std=2):
        # Calculate middle band (SMA)
        middle_band = data.rolling(window=window).mean()
        
        # Calculate standard deviation
        std = data.rolling(window=window).std()
        
        # Calculate upper and lower bands
        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def average_true_range(high, low, close, window=14):
        prev_close = close.shift(1)
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR
        atr = tr.rolling(window=window).mean()
        
        return atr
    
    @staticmethod
    def on_balance_volume(close, volume):
        price_change = close.diff()
        
        # OBV calculation
        obv = pd.Series(index=close.index)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if price_change.iloc[i] > 0:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif price_change.iloc[i] < 0:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    
    @staticmethod
    def stochastic_oscillator(high, low, close, k_window=14, d_window=3):
        lowest_low = low.rolling(window=k_window).min()
        highest_high = high.rolling(window=k_window).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_window).mean()
        
        return k_percent, d_percent
    
    @staticmethod
    def rate_of_change(data, window=12):
        return 100 * (data / data.shift(window) - 1)