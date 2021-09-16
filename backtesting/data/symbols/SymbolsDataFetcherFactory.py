from backtesting.data.symbols.NSESymbolsDataFetcher import NSESymbolsDataFetcher


class SymbolsDataFetcherFactory:
    def __init__(self, store_helper):
        self.store_helper = store_helper

    def get_object(self, exchange):
        if exchange == "NSE":
            return NSESymbolsDataFetcher(self.store_helper)
