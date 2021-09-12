from datetime import datetime

from backtesting.strategies.trend.SuperTrendStrategy import SuperTrendStrategy
from backtesting.tests.Test import Test


class SuperTrendTest(Test):
    def __init__(self):
        self.strategies = [SuperTrendStrategy]

        super().__init__(self.__class__.__name__, self.strategies)

    def get_atr_period(self):
        return self.config['SuperTrend']['atr_period']

    def get_atr_multiplier(self):
        return self.config['SuperTrend']['atr_multiplier']

    def get_to_date(self):
        d = self.config['SuperTrend']['to_date']

        if d == "now":
            return datetime.now().date()
        else:
            return datetime.strptime(d, '%b-%d-%Y').date()

    def get_max_candles(self):
        return self.config['SuperTrend']['max_candles']

    def add_strategy(self, cerebro, strategy, symbol):
        cerebro.addstrategy(strategy, ticker=symbol,
                            atr_period=self.get_atr_period(), atr_multiplier=self.get_atr_multiplier(),
                            order_pct=self.get_order_percent())



