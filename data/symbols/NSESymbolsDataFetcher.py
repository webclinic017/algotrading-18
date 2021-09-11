import random
import pandas as pd

from data.symbols.SymbolsDataFetcher import SymbolsDataFetcher


class NSESymbolsDataFetcher(SymbolsDataFetcher):
    def __init__(self, store_helper):
        super().__init__()

        self.df = store_helper.read_csv_as_df('All_Equity_Symbols_NSE.csv')
        self.df[' DATE OF LISTING'] = pd.to_datetime(self.df[' DATE OF LISTING']).dt.date

    def get_all_symbols(self):
        return self.df['SYMBOL'].toList()

    def get_n_symbols(self, n):
        symbols_list = self.df['SYMBOL'].tolist()
        return random.sample(symbols_list, n)

    def get_n_symbols_with_listing_newer_than_date(self, n, d):
        _df = self.df[self.df[' DATE OF LISTING'] < d]
        symbols_list = _df['SYMBOL'].tolist()
        return random.sample(symbols_list, n)
