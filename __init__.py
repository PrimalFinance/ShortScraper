# Operating system imports
import os
cwd = os.getcwd()

# Date & Time imports
import time
import datetime as dt

import yfinance as yf

import pprint

from Scrapers.short_scraper import ShortScraper

# Import the Asset Data class
from AssetData.asset_data import AssetData

# Import the short picker class
from ShortPicker.short_picker import ShortPicker

import matplotlib.pyplot as plt 







'''----------------------------------- Short Picking -----------------------------------'''
def pick_shorts(strategy: int, number_of_tickers: int = 100):
    short_scraper = ShortScraper()

    ticker_list = short_scraper.get_short_tickers()

    # If the number of tickers is greater than length of the list, default to the length of the list 
    if number_of_tickers > len(ticker_list):
        num_of_tickers = len(ticker_list)

    ticker_list = ticker_list[:number_of_tickers]

    asset_data_list = [AssetData(i, display_info=False).apply_rsi().apply_macd().apply_uptrend().apply_downtrend() for i in ticker_list]
    short_picker = ShortPicker()
    short_picker.set_short_list(asset_data_list)
    if strategy == 1:
        # Set the rsi settings 
        short_picker.rsi_overbought = 60
        # Set the short settings 
        short_picker.max_short_interest = 30
        short_picker.strategy_recently_overbought()







'''----------------------------------- Graph Plotting -----------------------------------'''
def plot_graph(asset, candle_limit: int = 100, include_rsi: bool = False):

    asset.apply_rsi()
    df = asset.data.head(candle_limit)

    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

    # Plot the "Close" values
    ax1.plot(df.index, df['Close'], label='Close', color='blue', linewidth=2)
    ax1.set_ylabel('Close Price')
    ax1.grid(True)
    ax1.legend()

    
    if include_rsi:
        # Plot the "RSI" values with a custom range from 0 to 100
        ax2.plot(df.index, df['RSI'], label='RSI', color='orange', linewidth=2)
        ax2.set_xlabel('Date')
        ax2.set_ylabel('RSI (0-100)')
        ax2.set_ylim(0, 100)  # Set the y-axis range for RSI
        ax2.grid(True)
        ax2.legend()

    # Customize the plot
    plt.suptitle(f'Close Price and RSI (First {candle_limit} Rows)')

    # Show the plot
    plt.tight_layout()
    plt.show()






'''-----------------------------------'''
'''-----------------------------------'''
'''-----------------------------------'''
if __name__ == "__main__":
    



    start = time.time()

    pick_shorts(strategy=1, number_of_tickers=1000)

    end = time.time()


    elapsed = end - start

    print(f"Elapsed: {elapsed}")
    #short_date = asset_data.short_scraper.get_short_date()

    #print(f"Short: {short_date}   type: {type(short_date)}")


    #aapl = yf.Ticker("AAPL")


    #pprint.pprint(aapl.info, width=1)

    #df = short_scraper.get_stock_historical_stock_prices("AAL")
    #print(f"Tickerlist: {tickers_list}  Length: {len(tickers_list)}")
    #short_scraper.get_short_data_yahoo_finance(tickers_list)
    #mw_df = short_scraper.get_short_data_marketwatch()
    #short_scraper.write_to_csv(marketwatch_csv_path, data_to_write=mw_df)
