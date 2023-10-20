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
raw_tickers_folder = f"{cwd}\\ShortData\\RawTickers" # This folder will hold csv files, with just the tickers and no further information. 
historical_stock_prices_folder = f"{cwd}\\HistoricalStockPrices"
short_data_folder = f"{cwd}\\ShortData"
short_reports_dates_folder = f"{cwd}\\ShortData\\ShortReportingDates"
short_reports_data_folder = f"{cwd}\\ShortData\\ShortReports"



date_dict = {
    1: ["Jan", "January"],
    2: ["Feb", "February"],
    3: ["Mar", "March"],
    4: ["Apr", "April"],
    5: ["May", "May"],
    6: ["Jun", "June"],
    7: ["Jul","July"],
    8: ["Aug", "August"],
    9: ["Sep", "September"],
    10: ["Oct", "October"],
    11: ["Nov", "November"],
    12: ["Dec", "December"],
}



class ShortScraper(ScraperTemplate):
    def __init__(self, display_info: bool = True):
        self.marketwatch_url = "https://www.marketwatch.com/tools/screener/short-interest"
        self.yahoo_finance_url = "https://finance.yahoo.com/screener/predefined/most_shorted_stocks/?count=100&offset={}"
        self.finra_reporting_url = "https://www.finra.org/filing-reporting/regulatory-filing-systems/short-interest"
        self.browser = None    
        self.date_info = dt.date.today()
        self.date_format = "%Y-%m-%d"
        self.display_info = display_info
        self.current_date = dt.datetime.now().date()
        self.short_date = self.select_short_report_date()["settlementDate"]
        super().__init__() 

    '''-----------------------------------'''
    def set_short_date(self):
        self.short_date = self.select_short_report_date()["settlementDate"]
    '''-----------------------------------'''
    def get_short_date(self):
        if self.short_date == None:
            self.set_short_date()
        return self.short_date
        
    '''----------------------------------- Yahoo Finance -----------------------------------'''
    '''-----------------------------------'''
    def get_short_tickers(self, ticker_limit: int = 1000) -> list:
        """
        :param ticker_limit: The number of tickes to collect"""
          

        shorted_tickers_file_path = f"{raw_tickers_folder}\\{self.short_date}_raw_tickers.csv"
        # Boolean to track if the tickers need to be scraped for the current date
        scraping_needed = False

        try:
            df = pd.read_csv(shorted_tickers_file_path)
            ticker_list = df["ticker"].to_list()
            if self.display_info:
                print(f"[Shorted Tickers] Retrieved from local csv file: {shorted_tickers_file_path}")
            return ticker_list[:ticker_limit]
        except FileNotFoundError:
            scraping_needed = True

        if scraping_needed:
            df = self.scrape_new_short_tickers(ticker_limit=ticker_limit)
            # Write updated list to the csv file. 
            df.to_csv(shorted_tickers_file_path)
            ticker_list = df["tickers"].to_list()
            if self.display_info:
                print(f"[Shorted Tickers] Retrieved from scraper")
            return ticker_list[:ticker_limit]

    '''-----------------------------------'''
    def get_short_data(self, ticker: str) -> pd.DataFrame:
        """
        :param: String representing ticker to get data for. 

        Description: This function will take a ticker, and get the relevant data. 
        """

        shorted_data_file = f"{short_reports_data_folder}\\{self.short_date}_shorted_data.csv"

        # Boolean to track if the tickers need to be scraped for the current date
        scraping_needed = False

        try:
            df = pd.read_csv(shorted_data_file)
            ticker_data = df[df["ticker"] == ticker]
            return ticker_data
        except FileNotFoundError:
            scraping_needed = True


        if scraping_needed:
            df = self.scrape_new_short_data()
            df.to_csv(shorted_data_file, index=False)
            ticker_data = df[df["ticker"] == ticker]
            return ticker_data

    '''----------------------------------- Historical Stock Prices Utilities -----------------------------------'''
    def get_historical_stock_prices(self, ticker: str):
        """
        :param ticker: A string of the ticker to retrieve the data for.

        Description: This function will attempt to get the most recent stock price data locally from a csv file. 
                     If a file does not exist for the current date, it will be fetched from Yahoo Finance and a csv file will be created with the data.
        """
        # Get the current time 
        current_time = dt.datetime.now().time()
        
        # Since new stock data is not added on weekends, this logic will determine if the script is being run on a weekend. 
        # It will default the date to the most recent trading day, which should be the most recent Friday. 
        if self.is_weekend():
            # Get the date of the most recent friday.
            most_recent_trading_day = self.get_most_recent_friday()
        else: # If it is not the weekend use the current trading day.
            if current_time < dt.time(13, 0):
                most_recent_trading_day = self.current_date - dt.timedelta(days=1)
            else:
                most_recent_trading_day = self.current_date
            
        # Capitalize ticker to minimize case matching errors.
        ticker = ticker.upper()

        # Boolean to track if new data needs to be collected
        scraping_needed = False
        ticker_path = f"{historical_stock_prices_folder}\\{ticker}.csv" 

        try:
            df = pd.read_csv(ticker_path)
            most_recent_date_recorded = pd.to_datetime(df["Date"]).max()

            # If the most recent date recorded does not equal the most recent trading day. 
            if most_recent_date_recorded.date() != most_recent_trading_day:
                new_df = yf.download(ticker, period="Max")
                # Reverse dataframe so new entries are on top.
                new_df = new_df.iloc[::-1]
                # Write the merged data to the csv. 
                new_df.to_csv(ticker_path,index=True)
                if self.display_info:
                    print(f"[Historical Stock Price] Retrieved from Yahoo Finance: {ticker}")
                    print(f"MRTD: {most_recent_trading_day}     MRDR: {most_recent_date_recorded}")
                return new_df
            else:
                if self.display_info:
                    print(f"[Historical Stock Price] Retrieved from local csv: {ticker_path}")
                return df            
        # If the csv file does not exist. 
        except FileNotFoundError:
            df = yf.download(ticker, period="max")
            # Reverse the dataframes to put the newest entries on top. 
            df = df.iloc[::-1]
            df.to_csv(ticker_path) # Write the data to the csv file in the path.
            if self.display_info:
                    print(f"[Historical Stock Price] Retrieved from Yahoo Finance: {ticker}")
            return df
            



    '''-------------------------------'''
    def get_short_reporting_dates(self):

        current_year = self.date_info.year
        new_year_date = f"{current_year+1}-1-1"
        csv_file_path = f"{short_data_folder}\\ShortReportingDates\\short_reports_{current_year}.csv"

        scraping_needed = False

        try:
            reports_df = pd.read_csv(csv_file_path)
            if self.display_info:
                print(f"[Short Reports] Received via local csv: {csv_file_path}")
            return reports_df
        except FileNotFoundError:
            scraping_needed = True
        except pd.errors.EmptyDataError:
            scraping_needed = True


        if scraping_needed:
            # Create a browser for the finra url
            if self.browser == None:
                self.create_browser(url=self.finra_reporting_url)

            # Xpaths to elements
            settlement_date_xpath = "/html/body/div[1]/div/div/div[1]/div/div/main/section/div/div/article/div/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div/table/tbody/tr[{}]/td[1]/p/strong"
            due_date_xpath = "/html/body/div[1]/div/div/div[1]/div/div/main/section/div/div/article/div/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div/table/tbody/tr[{}]/td[2]/p/strong"
            publication_date_xpath = "/html/body/div[1]/div/div/div[1]/div/div/main/section/div/div/article/div/div/div/div/div[2]/div/div/div[1]/div/div/div/div/div/table/tbody/tr[{}]/td[3]/p/strong"
            # Variables for loop. 
            scraping = True
            error_count = 0
            index = 1
            report_dates_collected = []
            while scraping:

                try:
                    # Settlement Date
                    settlement_date = self.read_data(settlement_date_xpath.format(index))
                    print(f"Settlement: {settlement_date}")
                    set_month, set_day = settlement_date.split(" ")
                    set_month = self.month_str_to_int(set_month)
                    formatted_settlement_date = f"{current_year}-{set_month}-{set_day}"
                    # Due Date
                    # The due date usually comes in this format: January 18 – 6 p.m.  We only want the date portion, "January 14"
                    due_date = self.read_data(due_date_xpath.format(index))
                    due_date = due_date.split("–")[0]
                    due_date_space_split = due_date.split(" ")
                    due_month = due_date_space_split[0] 
                    due_day = due_date_space_split[1]
                    
                    due_month = self.month_str_to_int(due_month)
                    
                    if self.date_close_to(formatted_settlement_date, new_year_date, 10):
                        formatted_due_date = f"{current_year+1}-{due_month}-{due_day}"
                    else:
                        formatted_due_date = f"{current_year}-{due_month}-{due_day}"

                    # Publication Date
                    publication_date = self.read_data(publication_date_xpath.format(index))
                    pub_month, pub_day = publication_date.split(" ")
                    pub_month = self.month_str_to_int(pub_month)

                    if self.date_close_to(formatted_settlement_date, new_year_date, 10):
                        formatted_publication_date = f"{current_year+1}-{pub_month}-{pub_day}"
                    else:
                        formatted_publication_date = f"{current_year}-{pub_month}-{pub_day}"

                    report_dates_collected.append({
                        "settlementDate": formatted_settlement_date,
                        "dueDate": formatted_due_date,
                        "publicationDate": formatted_publication_date
                    })


                except Exception as e:
                    error_count += 1

                if error_count >= 3:
                    scraping = False

                index += 1

            reports_df = pd.DataFrame(report_dates_collected)
            reports_df.to_csv(csv_file_path, index=False)
            if self.display_info:
                print(f"[Short Reports] Received via scraper.")
            return reports_df
        
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
    """
    =======================================================================================================
    =======================================================================================================
    Utilities
    =======================================================================================================
    =======================================================================================================
    """
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
    def month_str_to_int(self, month: str) -> str:
        """
        :param month: The string of a month, like 'January' for example. 
        
        :returns: String of the month's numerical counterpart. 

        Description: Takes the string of a month and converts it to their integer counterpart. 
                     Using the same example of 'January', it will be converted to '1'. Then it will be converted to a string
                     where a leading zero will be added if it is less than ten. Ex: '1' -> '01'

        """
        for key, val in date_dict.items():
            if month in val:
                # Add leading zero to the key if it is less than 10. Ex: 1 -> 01
                if key < 10:
                    return f"0{key}"
                else:
                    return str(key)
    '''-----------------------------------'''
    def date_close_to(self, start_date: str, end_date: str, days_difference):
        """
        :param start_date: Start of the period. 
        :param end_date: End of the period. 
        :param days_difference: The amount of days to compare against the "difference" of the start_date & end_date. 

        :returns: Boolean if the difference between the dates is less than 'days_difference'. 

        """
        date_format = "%Y-%m-%d"
        start_obj = dt.datetime.strptime(start_date, date_format)
        end_obj = dt.datetime.strptime(end_date, date_format)

        difference = end_obj - start_obj

        if difference.days <= days_difference:
            return True
        else:
            return False
    
    '''-----------------------------------'''
    def select_short_report_date(self) -> pd.Series: 
        # Get the current date. 
        cur_date = self.date_info
        short_reports_path = f"{short_reports_dates_folder}\\short_reports_{cur_date.year}.csv"

        # Read the data from the short reports csv file
        short_reports = pd.read_csv(short_reports_path)

        index = 0 

        for i in short_reports["publicationDate"]:
            i_obj = dt.datetime.strptime(i, self.date_format)
            # Once we reach a publication date that is greater than our current date, we break the loop.
            if cur_date < i_obj.date():
                break
            index += 1
        
        report_dates = short_reports.iloc[index-1]
        return report_dates

    """
    =======================================================================================================
    =======================================================================================================
    Scraping 
    =======================================================================================================
    =======================================================================================================
    """
    '''-----------------------------------'''
    def scrape_new_short_tickers(self, ticker_limit: int = 1000) -> pd.DataFrame:
        """
        Description: Scrapes the yahoo finance url that displays the top shorted tickers. """
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
        symbol_dict = {"ticker": tickers}
        df = pd.DataFrame(symbol_dict)
        return df
    '''-----------------------------------'''
    def scrape_new_short_data(self): 
         # List to hold the dictionaries of the data. 
        data_collected = []

        raw_tickers_path = f"{short_data_folder}\\{self.short_date}_short_tickers.csv"

        # Get the list of tickers. 
        try:
            df = pd.read_csv(filepath_or_buffer)
            ticker_list = df["ticker"].to_list()
        except Exception:
            df = self.scrape_new_short_tickers()
            ticker_list = df["ticker"].to_list()




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
                trailing_eps = basic_info["trailingEps"]
                forward_eps = basic_info["forwardEps"]
            except KeyError:
                trailing_eps = np.nan 
                forward_eps = np.nan

            # Get sector and industry related details 
            try:
                sector = basic_info["sector"].strip(",") # Remove any commas that may interfere with csv file. 
                industry = basic_info["industryKey"].strip(",")
                country = basic_info["country"].strip(",")
            except KeyError:
                sector = ""
                industry = ""
                country = ""
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


                # Since not every stock has a dividend, we specifically handle a this case for the dividend field.
                try:
                    # Get the dividend yield. 
                    dividend_yield = basic_info["dividendYield"]
                except KeyError: 
                    dividend_yield = np.nan

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
                "sharesOutStanding": shares_outstanding,
                "averageVolume": average_volume,
                "marketcap": marketcap,
                "enterpriseValue": ev,
                "trailingPE": trailing_pe,
                "forwardPE": forward_pe,
                "trailingEPS": trailing_eps,
                "forwardEPS": forward_eps,
                "dividendYield": dividend_yield,
                "sector": sector,
                "industry": industry,
                "country": country
            })

        df = pd.DataFrame(data_collected)
        return df
    '''-----------------------------------'''
    