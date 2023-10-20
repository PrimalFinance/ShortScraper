




class ShortPicker:
    def __init__(self, max_short_interest: float = 20.0):
        # List that holds "AssetData" objects
        self.short_list = []

        # Settings for data. 
        self.max_short_interest = max_short_interest
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
            asset_short_data = asset.short_data
            asset_price_data = asset.price_data
            short_interest = asset_short_data["shortInterest"].iloc[0]
            # Only view tickers with a short interest less than 'max_short_interest'.
            if short_interest <= self.max_short_interest:
                #print(f"{asset.ticker}\n\n{asset_price_data}")
                current_rsi = asset_price_data["RSI"].iloc[0]
                if current_rsi >= self.rsi_overbought:
                    print(f"{asset.ticker} Overbought")
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''