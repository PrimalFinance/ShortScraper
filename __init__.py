# Operating system imports
import os
cwd = os.getcwd()

# Date & Time imports
import time
import datetime as dt


from Scrapers.short_scraper import ShortScraper



'''-----------------------------------'''
'''-----------------------------------'''
'''-----------------------------------'''
if __name__ == "__main__":
    short_scraper = ShortScraper()

    current_date = dt.datetime.now().date()
    formatted_date = current_date.strftime("%Y-%m-%d")
    
    marketwatch_csv_path = f"{cwd}\\Marketwatch\\mw_{formatted_date}.csv"
    #short_scraper.get_short_data_yahoo_finance()
    tickers_list = short_scraper.get_short_tickers_yahoo_finance(1000)
    
    index = 1
    for t in tickers_list:
        print(f"{index}: {t}")
        short_scraper.get_stock_historical_stock_prices(t)
        index += 1
    #print(f"Tickerlist: {tickers_list}  Length: {len(tickers_list)}")
    #short_scraper.get_short_data_yahoo_finance(tickers_list)
    #mw_df = short_scraper.get_short_data_marketwatch()
    #short_scraper.write_to_csv(marketwatch_csv_path, data_to_write=mw_df)
