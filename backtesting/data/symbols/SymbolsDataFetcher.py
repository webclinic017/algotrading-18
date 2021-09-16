from abc import ABC, abstractmethod


class SymbolsDataFetcher(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_all_symbols(self):
        pass

    @abstractmethod
    def get_n_symbols(self):
        pass

    @abstractmethod
    def get_n_symbols_with_listing_newer_than_date(self):
        pass
