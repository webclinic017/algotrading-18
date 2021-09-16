from abc import ABC, abstractmethod


class Indicator(ABC):
    def __init__(self, period, candle_interval, candle_length):
        self.period = period
        self.candle_interval = candle_interval
        self.candle_length = candle_length

    @abstractmethod
    def calculate_lines(self, df):
        pass


