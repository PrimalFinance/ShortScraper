import os
import sys

# Add path for scraper template. 
sys.path.append("D:\Coding\VisualStudioCode\Projects\Python\ScraperTemplate")

# Date & Time imports
import time
import datetime as dt

# Yahoo Finance imports
import yfinance as yf


# Pandas
import pandas as pd
import numpy as np

from scraper_template import ScraperTemplate



cwd = os.getcwd()
# Csv paths
raw_tickers_path = f"{cwd}\\YahooFinance\\RawTickers" # This folder will hold csv files, with just the tickers and no further information. 
shorted_data_path = f"{cwd}\\YahooFinance\\ShortData"
historical_stock_prices_folder = f"{cwd}\\YahooFinance\\HistoricalStockPrices"



class ShortScraper(ScraperTemplate):
    def __init__(self):
        self.marketwatch_url = "https://www.marketwatch.com/tools/screener/short-interest"
        self.yahoo_finance_url = "https://finance.yahoo.com/screener/predefined/most_shorted_stocks/?count=100&offset={}"
        self.browser = None    
        self.current_date = dt.datetime.now().date()
        self.date_info = dt.date.today()
        super().__init__() 

    '''----------------------------------- MarketWatch  -----------------------------------'''
    '''-----------------------------------'''
    def get_short_data_marketwatch(self) -> pd.DataFrame:

        if self.browser == None:
            self.create_browser(url=self.marketwatch_url)

        # Index to start scraping at. 
        index = 1
        error_count = 0

        symbol_xpath = "/html/body/div[3]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[1]/div"
        company_name_xpath = "/html/body/div[3]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[2]/div"
        price_xpath = "/html/body/div[3]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[3]/bg-quote"
        price_change_1day_xpath = "/html/body/div[3]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[4]/bg-quote"
        price_change_ytd_xpath = "/html/body/div[3]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[5]/div"
        short_interest_xpath = "/html/body/div[3]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[6]/div"
        short_date_xpath = "/html/body/div[3]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[7]/div"
        float_xpath = "/html/body/div[3]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[8]/div"
        float_shorted_xpath = "/html/body/div[3]/div[2]/div[2]/div/div[2]/div/table/tbody/tr[{}]/td[9]/div"
        close_button_xpath = "/html/body/footer/div[2]/div/div/button"
        try:
            self.click_button(xpath=close_button_xpath, wait=True)
        except Exception as e:
            print(f'[Xpath Failed] Failed to click button')
        scraping_marketwatch = True

        data_collected = []
        while scraping_marketwatch:
            
            try:
                symbol = self.read_data(xpath=symbol_xpath.format(index), wait=True)
                company_name = self.read_data(xpath=company_name_xpath.format(index), wait=True)
                price = self.read_data(xpath=price_xpath.format(index), wait=True)
                price_change_1day = self.read_data(xpath=price_change_1day_xpath.format(index), wait=True)
                price_change_ytd = self.read_data(xpath=price_change_ytd_xpath.format(index), wait=True)
                short_interest = self.read_data(xpath=short_interest_xpath.format(index), wait=True)
                short_date = self.read_data(xpath=short_date_xpath.format(index), wait=True)
                company_float = self.read_data(xpath=float_xpath.format(index), wait=True)
                float_shorted = self.read_data(xpath=float_shorted_xpath.format(index), wait=True)

                # Clean data.
                price = self.clean_number(data=price)
                price_change_1day = self.clean_number(data=price_change_1day)
                price_change_ytd = self.clean_number(data=price_change_ytd)
                short_interest = self.clean_number(data=short_interest)
                company_float = self.clean_number(data=company_float)
                float_shorted = self.clean_number(data=float_shorted)

                data_collected.append({
                    "symbol": symbol,
                    "company_name": company_name,
                    "price": price,
                    "day_change": price_change_1day,
                    "ytd_change": price_change_ytd,
                    "short_interest": short_interest,
                    "short_date": short_date,
                    "float": company_float,
                    "float_shorted": float_shorted
                })
            
            except Exception as e:
                print(f"Error Tag: {e}")
                error_count += 1

            index += 1

            if error_count >= 3:
                scraping_marketwatch = False
        # Convert list of dictionaries to dataframe. 
        df = pd.DataFrame(data_collected)
        return df
    '''----------------------------------- Yahoo Finance -----------------------------------'''
    '''-----------------------------------'''
    def get_short_tickers_yahoo_finance(self, ticker_limit: int = 1000) -> list:
        """
        :param ticker_limit: The number of tickes to collect"""
        

        shorted_tickers_file_path = f"{raw_tickers_path}\\{self.current_date}_shorted_tickers.csv"
        # Boolean to track if the tickers need to be scraped for the current date
        scraping_needed = False

        try:
            df = pd.read_csv(shorted_tickers_file_path)
            ticker_list = df["tickers"].to_list()
            return ticker_list[:ticker_limit]
        except FileNotFoundError:
            scraping_needed = True

        if scraping_needed:
            index = 1
            offset = 0
            error_count = 0
            
            if self.browser == None: 
                self.create_browser(url=self.yahoo_finance_url.format(offset))
            
            # Xpaths 
            symbol_xpath = "/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/section/div/div[2]/div[1]/table/tbody/tr[{}]/td[1]/a"
            tickers = []
            scraping = True
            while scraping:
                try:
                    symbol = self.read_data(xpath=symbol_xpath.format(index), wait=True)
                    tickers.append(symbol)
                except Exception as e:
                    print(f"Error tag: {e}")
                    error_count += 1
                
                if error_count >= 3:
                    # Increment the offset by 100.
                    offset += 100
                    # Reset the index to 1 since we are going to a new page.
                    index = 1
                    self.browser.get(self.yahoo_finance_url.format(offset))
                    # Reset the error count. 
                    error_count = 0
                    if offset == ticker_limit:
                        scraping = False
                else:
                    index += 1
            # Symbol 
            symbol_dict = {"tickers": tickers}
            df = pd.DataFrame(symbol_dict)
            df.to_csv(shorted_tickers_file_path, index=False)
            return tickers

    '''-----------------------------------'''
    def get_short_data_yahoo_finance(self, ticker_list: list) -> pd.DataFrame:
        """
        :param: List of tickers to get data for. 

        Description: This function will take the list of ticker, and get the relevant data for each one. 
                     *Unlike* the "MarketWatch" function, the tickers are not collected within this function, and instead need to be passed in the parameter.
        """

      
        shorted_data_file = f"{shorted_data_path}\\{self.current_date}_shorted_data.csv"

        # Boolean to track if the tickers need to be scraped for the current date
        scraping_needed = False

        try:
            df = pd.read_csv(shorted_data_file)
            return df
        except FileNotFoundError:
            scraping_needed = True


        if scraping_needed:
            # List to hold the dictionaries of the data. 
            data_collected = []

            for ticker in ticker_list:
                symbol = ticker
                ticker_obj = yf.Ticker(ticker=symbol)


                # Get the info for the company. 
                basic_info = ticker_obj.info

                """--- Short Data ---"""
                # Get number of shares short.
                try:
                    shares_short = basic_info["sharesShort"]
                    # Get the number of shares short from the prior month. 
                    shares_short_prior_month = basic_info["sharesShortPriorMonth"]
                    # Calculate the change in short interest from the current period to last month's period. 
                    short_change = ((shares_short - shares_short_prior_month)/abs(shares_short_prior_month)) * 100
                    """--- Shares Data ---"""
                    # Get the number of shares outstanding 
                    shares_outstanding = basic_info["sharesOutstanding"]
                    # Calculate the short interest.
                    short_interest = (shares_short / shares_outstanding) * 100
                    # Get the average volume of the stock traded. 
                    average_volume = basic_info["averageVolume"]
                except KeyError:
                    shares_short = np.nan
                    shares_short_prior_month = np.nan
                    short_change = np.nan
                """--- Ratio Data ---""" 
                # Get the short ratio. (# Shares sold short/Average trading volume)
                try:
                    short_ratio = basic_info["shortRatio"]
                except KeyError:
                    short_ratio = np.nan
                # Get the quick ratio. ((Current Assets - Inventory)/ Current Liabilities)
                try:
                    quick_ratio = basic_info["quickRatio"]
                except KeyError:
                    quick_ratio = np.nan
                
                # Get the current ratio. (Current Assets / Current Liabilities)
                try:
                    current_ratio = basic_info["currentRatio"]
                except KeyError:
                    current_ratio = np.nan
                # Get PE related data
                #print(f"Basic: {basic_info}")
                try:
                    trailing_pe = basic_info["trailingPE"]
                    forward_pe = basic_info["forwardPE"]
                except KeyError:
                    trailing_pe = np.nan
                    forward_pe = np.nan
                # Get Earnings-per-share related data.
                try:
                    trailing_eps = basic_info["trailingEPS"]
                    forward_eps = basic_info["forwardEPS"]
                except KeyError:
                    trailing_eps = np.nan
                    forward_eps = np.nan
                """--- Stock Price/Marketcap Data ---"""
                try:
                    # Get the current price
                    stock_price = basic_info["currentPrice"]
                    # Get the 52 week high.
                    high_52_week = basic_info["fiftyTwoWeekHigh"]
                    # Get the 52 week low.
                    low_52_week = basic_info["fiftyTwoWeekLow"]
                    # Get the enterprise value. (Marketcap + cash - debt) 
                    ev = basic_info["enterpriseValue"]
                    # Get the marketcap. 
                    marketcap = basic_info["marketCap"]
                except KeyError:
                    stock_price = np.nan
                    high_52_week = np.nan
                    low_52_week = np.nan
                    ev = np.nan
                    marketcap = np.nan


                data_collected.append({
                    "ticker": ticker,
                    "currentPrice": stock_price,
                    "low52Week": low_52_week,
                    "high52Week": high_52_week,
                    "sharesShort": shares_short,
                    "sharesShortPriorMonth": shares_short_prior_month,
                    "shortChange": short_change,
                    "shortInterest": short_interest,
                    "averageVolume": average_volume,
                    "marketcap": marketcap,
                    "enterpriseValue": ev,
                    "trailingPE": trailing_pe,
                    "forwardPE": forward_pe,
                    "trailingEPS": trailing_eps,
                    "forwardEPS": forward_eps
                })

            df = pd.DataFrame(data_collected)
            df.to_csv(shorted_data_file, index=False)
            return df

        
        



    '''----------------------------------- Historical Stock Prices Utilities -----------------------------------'''
    def get_stock_historical_stock_prices(self, ticker: str):
        """
        :param ticker: A string of the ticker to retrieve the data for.

        Description: This function will attempt to get the most recent stock price data locally from a csv file. 
                     If a file does not exist for the current date, it will be fetched from Yahoo Finance and a csv file will be created with the data.
        """
        # Since new stock data is not added on weekends, this logic will determine if the script is being run on a weekend. 
        # It will default the date to the most recent trading day, which should be the most recent Friday. 
        if self.is_weekend():
            # Get the date of the most recent friday.
            most_recent_trading_day = self.get_most_recent_friday()
        else: # If it is not the weekend use the current trading day. 
            most_recent_trading_day = self.current_date
        # Capitalize ticker to minimize case matching errors.
        ticker = ticker.upper()

        # Boolean to track if new data needs to be collected
        scraping_needed = False
        ticker_path = f"{historical_stock_prices_folder}\\{ticker}.csv" 

        try:
            print(f"Ticker path: {ticker_path}")
            df = pd.read_csv(ticker_path)
            most_recent_date_recorded = pd.to_datetime(df["Date"]).max()

            print(f"DF: {df}")

            print(f"MRD: {most_recent_date_recorded.date()}    MRTD: {most_recent_trading_day}")

            # If the most recent date recorded does not equal the most recent trading day. 
            if most_recent_date_recorded.date() != most_recent_trading_day:
                print("TAG1")
                new_df = yf.download(ticker, period="Max")
                # Reverse dataframe so new entries are on top.
                new_df = new_df.iloc[::-1]
                # Write the merged data to the csv. 
                new_df.to_csv(ticker_path,index=True)
                return new_df
            else:
                print("TAG2")
                return df            
        # If the csv file does not exist. 
        except FileNotFoundError:
            print("TAG3")
            df = yf.download(ticker, period="max")
            # Reverse the dataframes to put the newest entries on top. 
            df = df.iloc[::-1]
            df.to_csv(ticker_path) # Write the data to the csv file in the path.
            return df
            



    '''----------------------------------- CSV Utilities -----------------------------------'''
    '''-------------------------------'''
    def write_to_csv(self, file_path: str,  data_to_write: pd.DataFrame):
        # Read the dataframe.
        try:
            csv_data = pd.read_csv(file_path)

            if not csv_data.empty:
                data_to_write.to_csv(file_path, index=False)
        except FileNotFoundError:
            data_to_write.to_csv(file_path, index=False)     
        except pd.errors.EmptyDataError:
            data_to_write.to_csv(file_path, index=False)   
    '''----------------------------------- Data Cleaning Utilities -----------------------------------'''
    '''-------------------------------'''
    def clean_number(self, data: str, remove_comma: bool = True):
        '''
        :param data: The string of data to be "cleaned". Cleaning in this instance means removing any "$" or converting numbers in accounting format such as (100,000) to -100,000

        '''
        # Remove dollar sign and leading/trailing white spaces
        if "$" in data:
            data = data.replace("$", "").strip()
        
        if "(" in data:
            # Remove parentheses and add a "-" at the beginning
            data = "-" + data.replace("(", "").replace(")", "")

        if remove_comma:
            if "," in data:
                data = data.replace(",","")
        return data

    '''-----------------------------------'''
    '''----------------------------------- Date Utilities -----------------------------------'''
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