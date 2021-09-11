from data.historical.NSEDataFetcher import NSEDataFetcher


class DataFetcherFactory:
    def __init__(self, store_helper):
        self.store_helper = store_helper

    def get_object(self, exchange):
        if exchange == "NSE":
            return NSEDataFetcher(self.store_helper)
