from abc import ABC, abstractmethod


class Strategy(ABC):
    def __init__(self, period, candle_interval, **kwargs):
        self.period = period
        self.candle_interval = candle_interval
        pass

    @abstractmethod
    def act(self, df):
        pass
