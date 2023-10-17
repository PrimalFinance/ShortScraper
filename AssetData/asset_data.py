

# Pandas 
import pandas as pd
import numpy as np
import pandas_ta as pta


class AssetData:
    def __init__(self, df: pd.DataFrame):
        self.data = df
        # Column labels
        self.returns_col_label = "Returns"
        self.uptrend_col_label = "Uptrend"
        self.downtrend_col_label = "Downtrend"

        # Recent trend lengths
        self.recent_uptrend_length = None
        self.recent_downtrend_length = None
        
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''----------------------------------- Trend-Following -----------------------------------'''
    

    '''-----------------------------------'''
    def apply_uptrend(self):
        if self.uptrend_col_label not in self.data.columns:
            # Apply the returns column. 
            self.apply_returns_col()
            self.data[self.uptrend_col_label] = self.data[self.returns_col_label] > 0 # Boolean marked True when Returns column is positive. 
    '''-----------------------------------'''
    def apply_downtrend(self):
        if self.downtrend_col_label not in self.data.columns:
            # Apply the returns column.
            self.apply_returns_col()
            self.data[self.downtrend_col_label] = self.data[self.returns_col_label] < 0 # Boolean marked True when Returns column is negative.
    '''-----------------------------------'''
    def apply_returns_col(self):
        
        if self.returns_col_label not in self.data.columns:
            self.data[self.returns_col_label] = self.data["Close"].pct_change(-1) * 100# Make the pct change be calculated in ascending order

        return self
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''----------------------------------- Momentum -----------------------------------'''
    '''-----------------------------------'''
    def apply_rsi(self, rsi_period: int = 14):
        '''
        Description: Calculate the Relative Strength Index (RSI) from the price data.
                 RSI >= 70 is overbought
                 RSI <= 30 is oversold  
        '''
        if "RSI" not in self.data.columns:
            self.data["RSI"] = pta.rsi(self.data["Close"],  length=rsi_period)
            
        return self
    '''-----------------------------------'''
    '''-----------------------------------'''
    def apply_macd(self, short_period: int = 12, long_period: int = 26, macd_period: int = 9):
        '''
        short_period: Number of candles to use for the short term exponential moving average.
        long_period: Number of candles to use for the long term exponential moving average.
        macd_period: Number of periods to use for the MACD exponential moving average.
        '''
        if "MACD_Over" not in self.data.columns:
            # Calculate the macd and signal. 
            macd_results = pta.macd(self.data['Close'], fast=short_period, slow=long_period, signal=macd_period)
            
            # Assign values to new columns.
            macd_col = f"MACD_{short_period}_{long_period}_{macd_period}"
            signal_col = f"MACDs_{short_period}_{long_period}_{macd_period}"
            histogram_col = f"MACDh_{short_period}_{long_period}_{macd_period}"
            self.data["MACD"] = macd_results[macd_col]
            self.data["MACD_Signal"] = macd_results[signal_col]
            self.data["Histogram"] = macd_results[histogram_col]
            self.data["MACD_Over"] = self.data["MACD"] > self.data["MACD_Signal"]
    '''-----------------------------------'''
    def get_volatility(self) -> float:
        
        # Check if the "Returns" column has already been calculated. 
        if self.returns_col_label not in self.data.columns:
            # Add the daily returns column. 
            self.apply_returns_col()
            
        # Calculate the volatility 
        volatility = self.data[self.returns_col_label].std()
        # Annulualize the volatility (assuming 252 trading days).
        annualized_volatility = (volatility * np.sqrt(252)) * 100
        return annualized_volatility
    '''----------------------------------- Method Implementations -----------------------------------'''
    '''-----------------------------------'''
    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.data)
    '''-----------------------------------'''
    def __str__(self) -> str:
        return f"{self.data}"