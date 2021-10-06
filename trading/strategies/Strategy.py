import logging
from abc import ABC, abstractmethod

from trading.zerodha.kite.Orders import Orders
from trading.zerodha.kite.Period import Period


class Strategy(ABC):
    def __init__(self, kite, indicators, **kwargs):
        logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s', level=logging.INFO)
        self.kite = kite
        self.indicators = indicators

        self.exchange = kwargs['exchange']
        self.symbol = kwargs['symbol']

        self.period = Period.MIN
        self.candle_length = 7
        self.candle_interval = 1
        self.leverage = 5
        self.order_pct = 0.50

        self.orders = Orders(self.kite, self.leverage, self.order_pct, self.exchange)

    @abstractmethod
    def act(self, candle_time):
        pass

    def get_symbol(self):
        return self.symbol

    def get_period(self):
        return self.period

    def get_candle_length(self):
        return self.candle_length

    def get_candle_interval(self):
        return self.candle_interval

    def get_indicators(self):
        return self.indicators
