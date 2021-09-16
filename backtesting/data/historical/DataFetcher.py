from abc import ABC, abstractmethod


class DataFetcher(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_data(self, symbol, to_date, from_date):
        pass

    @abstractmethod
    def get_data_for_backtrader(self, symbol, to_date, from_date):
        pass
