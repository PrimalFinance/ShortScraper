




class ShortPicker:
    def __init__(self, max_short_interest: float = 20.0, min_short_interest: float = 0.0):
        # List that holds "AssetData" objects
        self.short_list = []

        # Settings for data. 
        self.max_short_interest = max_short_interest
        self.min_short_interest = min_short_interest
        self.rsi_overbought = 70
        self.rsi_oversold = 30

    '''-----------------------------------'''
    def set_short_list(self, short_list: list) -> None:
        self.short_list = short_list
    '''-----------------------------------'''
    def get_short_list(self) -> list:
        return self.short_list
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    """
    =======================================================================================================
    =======================================================================================================
    Strategies
    =======================================================================================================
    =======================================================================================================
    """
    '''-----------------------------------'''
    def strategy_recently_overbought(self): 

        for asset in self.short_list:
            #print(f"Asset: {asset}")
            asset_short_data = asset.short_data
            asset_price_data = asset.price_data
            try:
                short_interest = asset_short_data["shortInterest"].iloc[0]
            except IndexError:
                short_interest = 0
            # Only view tickers with a short interest less than 'max_short_interest'.
            if short_interest > self.min_short_interest and short_interest <= self.max_short_interest:
                #print(f"{asset.ticker}\n\n{asset_price_data}")
                current_rsi = asset_price_data["RSI"].iloc[0]
                if current_rsi >= self.rsi_overbought:
                    if asset.recent_downtrend_length >= 2:
                        self.dispaly_asset(asset, list_format=True, list_length=5)
                        #print(f"---------------------------------------\n{asset.ticker}\nRSI: {current_rsi}\n30dayReturn: {asset.returns['30day']}\nShort Interest: {short_interest}%")
    '''-----------------------------------'''
    def dispaly_asset(self, asset, list_format: bool = False, list_length: int = 5):

        if list_format:
            rsi_list = asset.price_data["RSI"].to_list()
            rsi_list = rsi_list[:list_length]
            rsi_list = ["{:.2f}".format(num) for num in rsi_list]
            price_list= asset.price_data["Close"].to_list()
            price_list = price_list[:list_length]
            price_list = ["{:.2f}".format(num) for num in price_list]
            try:
                short_interest = asset.short_data["shortInterest"].iloc[0]
                short_interest = "{:.2f}".format(short_interest)
            except IndexError:
                short_interest = np.nan
            try:
                asset_30_returns = asset.returns["30day"]
                asset_30_returns = "{:.2f}".format(asset_30_returns)
            except IndexError:
                asset_30_returns = np.nan
            print(f"---------------------------------------\n{asset.ticker}\nRSI: {rsi_list}\nPrice: {price_list}\n30dayReturn: {asset_30_returns}%\nShort Interest: {short_interest}%")


        else:
            pass

    '''-----------------------------------'''
    '''-----------------------------------'''