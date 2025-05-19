# indicators.py
"""
Technical indicators module for stock analysis.
"""

import numpy as np
import pandas as pd


class TechnicalIndicators:
    """Class to calculate various technical indicators for stock data."""
    
    @staticmethod
    def moving_average(data, window=20):
        """
        Calculate the simple moving average.
        
        Args:
            data (pd.Series): Price series data
            window (int): Window size for moving average
            
        Returns:
            pd.Series: Moving average series
        """
        return data.rolling(window=window).mean()
    
    @staticmethod
    def exponential_moving_average(data, span=20):
        """
        Calculate the exponential moving average.
        
        Args:
            data (pd.Series): Price series data
            span (int): Span for EMA calculation
            
        Returns:
            pd.Series: EMA series
        """
        return data.ewm(span=span, adjust=False).mean()
    
    @staticmethod
    def relative_strength_index(data, window=14):
        """
        Calculate the Relative Strength Index (RSI).
        
        Args:
            data (pd.Series): Price series data
            window (int): Window size for RSI
            
        Returns:
            pd.Series: RSI values
        """
        # Calculate price changes
        delta = data.diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        
        # Calculate RS
        rs = avg_gain / avg_loss
        
        # Calculate RSI
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(data, fast_period=12, slow_period=26, signal_period=9):
        """
        Calculate the Moving Average Convergence Divergence (MACD).
        
        Args:
            data (pd.Series): Price series data
            fast_period (int): Fast EMA period
            slow_period (int): Slow EMA period
            signal_period (int): Signal line period
            
        Returns:
            tuple: (MACD line, signal line, histogram)
        """
        # Calculate the fast and slow EMAs
        ema_fast = data.ewm(span=fast_period, adjust=False).mean()
        ema_slow = data.ewm(span=slow_period, adjust=False).mean()
        
        # Calculate the MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate the signal line
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # Calculate the histogram
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(data, window=20, num_std=2):
        """
        Calculate Bollinger Bands.
        
        Args:
            data (pd.Series): Price series data
            window (int): Window size for moving average
            num_std (float): Number of standard deviations
            
        Returns:
            tuple: (upper band, middle band, lower band)
        """
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
        """
        Calculate Average True Range (ATR).
        
        Args:
            high (pd.Series): High price series
            low (pd.Series): Low price series
            close (pd.Series): Close price series
            window (int): Window size for ATR
            
        Returns:
            pd.Series: ATR values
        """
        # Calculate true range
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
        """
        Calculate On-Balance Volume (OBV).
        
        Args:
            close (pd.Series): Close price series
            volume (pd.Series): Volume series
            
        Returns:
            pd.Series: OBV values
        """
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
        """
        Calculate Stochastic Oscillator.
        
        Args:
            high (pd.Series): High price series
            low (pd.Series): Low price series
            close (pd.Series): Close price series
            k_window (int): Window size for %K
            d_window (int): Window size for %D
            
        Returns:
            tuple: (%K, %D)
        """
        # Calculate %K
        lowest_low = low.rolling(window=k_window).min()
        highest_high = high.rolling(window=k_window).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        
        # Calculate %D (simple moving average of %K)
        d_percent = k_percent.rolling(window=d_window).mean()
        
        return k_percent, d_percent
    
    @staticmethod
    def rate_of_change(data, window=12):
        """
        Calculate Rate of Change (ROC).
        
        Args:
            data (pd.Series): Price series data
            window (int): Window size for ROC
            
        Returns:
            pd.Series: ROC values
        """
        return 100 * (data / data.shift(window) - 1)