
# Operating System imports
import os 

# Pandas 
import pandas as pd
import numpy as np
import pandas_ta as pta

# Date & Time imports
import time
import datetime as dt


# Import the short scraper
import Scrapers.short_scraper


# Get the current working directory.
cwd = os.getcwd()


# Paths to folders 
historical_prices_folder = f"{cwd}\\HistoricalStockPrices" 
short_data_folder_path = f"{cwd}\\ShortData"


class AssetData:
    def __init__(self, ticker: str, preset_data: bool = True, display_info: bool = True):
        self.ticker = ticker.upper()

        # Get the current date as an object
        self.date_info = dt.date.today()

        # Column labels
        self.returns_col_label = "Returns"
        self.uptrend_col_label = "Uptrend"
        self.downtrend_col_label = "Downtrend"

        # Recent trend lengths
        self.recent_uptrend_length = None
        self.recent_downtrend_length = None


        # Short scraper 
        self.short_scraper = Scrapers.short_scraper.ShortScraper(display_info=display_info)

        # Get the current date as an object
        self.date_info = dt.date.today()

        # If true, class variables will be loaded with data. 
        # NOTE: The preset data should be called after the other class variables have been initialized (i.e. at the bottom of the init function).
        if preset_data:
            self.set_historical_prices()
            self.set_short_data()
        else:
            self.price_data = pd.DataFrame()
            self.short_data = pd.DataFrame()

        
    """
    =======================================================================================================
    =======================================================================================================
    Data Collection
    =======================================================================================================
    =======================================================================================================
    """
    '''-----------------------------------'''
    def set_historical_prices(self): 
        # Get the data from the short scraper
        self.price_data = self.short_scraper.get_historical_stock_prices(self.ticker)
        try:
            self.price_data["Date"] = pd.to_datetime(self.price_data["Date"])
            # Set the date column as the index 
            self.price_data = self.price_data.set_index("Date")
        # Occurs if the date is already set as the index. 
        except KeyError: 
            pass
       
        
    '''-----------------------------------'''
    def get_historical_prices(self) -> pd.DataFrame:
        if self.price_data.empty:
            self.set_historical_prices()
        return self.price_data
    '''-----------------------------------'''
    def set_short_data(self) -> None:
        self.short_data = self.short_scraper.get_short_data(self.ticker)
    '''-----------------------------------'''
    def get_short_data(self) -> pd.DataFrame:
        if self.short_data.empty:
            self.set_short_data()
        return self.short_data
    '''-----------------------------------'''
    """
    =======================================================================================================
    =======================================================================================================
    Technical Analysis
    =======================================================================================================
    =======================================================================================================
    """
    '''----------------------------------- Trend-Following -----------------------------------'''
    

    '''-----------------------------------'''
    def apply_uptrend(self):
        if self.uptrend_col_label not in self.price_data.columns:
            # Apply the returns column. 
            self.apply_returns_col()
            self.price_data[self.uptrend_col_label] = self.price_data[self.returns_col_label] > 0 # Boolean marked True when Returns column is positive. 
            
            # Uptrend length logic
            uptrend_length = 0 
            i = 0
            while i < len(self.price_data):
                uptrend = self.price_data[self.uptrend_col_label].iloc[i]
                if uptrend:
                    uptrend_length += 1
                else:
                    break
                i += 1
            self.recent_uptrend_length = uptrend_length
        return self
    '''-----------------------------------'''
    def apply_downtrend(self):
        if self.downtrend_col_label not in self.price_data.columns:
            # Apply the returns column.
            self.apply_returns_col()
            self.price_data[self.downtrend_col_label] = self.price_data[self.returns_col_label] < 0 # Boolean marked True when Returns column is negative.

            # Downtrend length logic. 
            downward_length = 0
            i = 0
            while i < len(self.price_data):
                downtrend = self.price_data[self.downtrend_col_label].iloc[i]
                if downtrend:
                    downward_length += 1
                else: 
                    break
                i += 1
            self.recent_downtrend_length = downward_length
        return self    
    '''-----------------------------------'''
    def apply_returns_col(self):
        
        if self.returns_col_label not in self.price_data.columns:
            self.price_data[self.returns_col_label] = self.price_data["Close"].pct_change(-1) * 100# Make the pct change be calculated in ascending order

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
        if "RSI" not in self.price_data.columns:
            if self.returns_col_label not in self.price_data.columns:
                self.apply_returns_col()

            # If the data is in a descending order, reverse it to ascending temporarily. 
            if self.is_descending():
                temp_df = self.price_data[::-1] # Reverse the dataframe to now be in ascending order. (Largest on bottom). 
                rsi = pta.rsi(temp_df["Close"], length=rsi_period)
                self.price_data["RSI"] = rsi[::-1] # Reverse dataframe to its original state, descending order (Largest at top). 
            else:
                temp_df = self.price_data
                rsi = pta.rsi(temp_df["Close"], length=rsi_period)
                self.price_data["RSI"] = rsi
            
        return self
    '''-----------------------------------'''
    def apply_vwap(self): 
        """

        Description: This function calculates the Volume Weighted Average Price (VWAP). 
                     The way VWAP can be calculated is by multiplying items in the "Close" column by the values in the "Volume" column. 
                     Then take the sum of the product (Close x Volume), and divide it by the sum of the "Volume" column. 
                     This can be expressed like this: 
                     df['Price x Volume'] = df['Price'] * df['Volume']
                     vwap = df['Price x Volume'].sum() / df['Volume'].sum()


        """
        # Check if "VWAP" is not already a column in the dataframe. 
        if "VWAP" not in self.price_data.columns:
            temp_df = self.price_data
            temp_df["VWAP"] = pta.vwap(high=temp_df["High"], low=temp_df["Low"], close=temp_df["Close"], volume=temp_df["Volume"])

            self.price_data["VWAP"] = temp_df["VWAP"]
        return self
    '''-----------------------------------'''
    def apply_macd(self, short_period: int = 12, long_period: int = 26, macd_period: int = 9):
        '''
        short_period: Number of candles to use for the short term exponential moving average.
        long_period: Number of candles to use for the long term exponential moving average.
        macd_period: Number of periods to use for the MACD exponential moving average.
        '''
        if "MACD_Over" not in self.price_data.columns:

            if self.is_descending():
                # Reverse the data
                df = self.price_data[::-1]
            else:
                df = self.price_data
            # Calculate the short term exponential moving average (EMA).
            short_ema = df["Close"].ewm(span=short_period, adjust=False).mean()
            # Calculate the long term EMA. 
            long_ema = df["Close"].ewm(span=long_period, adjust=False).mean()

            # Calculate the MACD
            macd_line = short_ema - long_ema

            # Calculate the signal line. 
            signal_line = macd_line.ewm(span=macd_period, adjust=False).mean()

            # Calculate the histogram
            histogram = macd_line - signal_line 



            if self.is_descending():
                # Assign data to columns 
                self.price_data["MACD"] = macd_line[::-1]
                self.price_data["MACD_Signal"] = signal_line[::-1]
                self.price_data["MACD_Histogram"] = histogram [::-1]
                self.price_data["MACD_Over"] = self.price_data["MACD"] > self.price_data["MACD_Signal"]
            else:
                # Assign data to columns 
                self.price_data["MACD"] = macd_line
                self.price_data["MACD_Signal"] = signal_line
                self.price_data["MACD_Histogram"] = histogram 
                self.price_data["MACD_Over"] = self.price_data["MACD"] > self.price_data["MACD_Signal"]
        
        return self
    '''-----------------------------------'''
    def get_volatility(self) -> float:
        
        # Check if the "Returns" column has already been calculated. 
        if self.returns_col_label not in self.price_data.columns:
            # Add the daily returns column. 
            self.apply_returns_col()
            
        # Calculate the volatility 
        volatility = self.price_data[self.returns_col_label].std()
        # Annulualize the volatility (assuming 252 trading days).
        annualized_volatility = (volatility * np.sqrt(252)) * 100
        return annualized_volatility

    """
    =======================================================================================================
    =======================================================================================================
    Utilities
    =======================================================================================================
    =======================================================================================================
    """
    '''----------------------------------- Date & Time -----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    def is_weekend(self) -> bool:
        weekday = self.date_info.weekday()
        return weekday == 5 or weekday == 6 # Returns a boolean if the weekday is Saturday(5), or Sunday(6)
    '''-----------------------------------'''
    def get_most_recent_friday(self):
        date = self.date_info
        weekday = self.date_info.weekday()
        if weekday == 5: # Saturday
            days_to_subtract = 1
        elif weekday == 6: # Sunday
            days_to_subtract = 2
        date -= dt.timedelta(days=days_to_subtract)
        return date
    '''-----------------------------------'''
    def is_descending(self) -> bool:
        """
        Description: This function will take data from 'self.price_data' and check if the date in the first row, is greater than the date in the last row. 
                     If these conditions are met, this indicates the data is ordered in a descending fashion. With the newer entries on top, and the old entries are at the bottom in a descending order. 
        """
        
        # Check if the date in row 1 is greater than the date in the last row. 
        if self.price_data.index[1] > self.price_data.index[-1]:
            return True
        else: 
            return False


    '''-----------------------------------'''
    '''----------------------------------- Method Implementations -----------------------------------'''
    '''-----------------------------------'''
    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.price_data)
    '''-----------------------------------'''
    def __str__(self) -> str:
        return f"{self.price_data}"