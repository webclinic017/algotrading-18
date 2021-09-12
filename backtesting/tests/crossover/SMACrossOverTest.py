import json
from datetime import datetime

from backtesting.strategies.crossover.GoldenCross import GoldenCross
from backtesting.strategies.crossover.GoldenCrossWithStopLoss import GoldenCrossWithStopLoss
from backtesting.strategies.crossover.GoldenCrossWithTrailingStopLoss import GoldenCrossWithTrailingStopLoss

from backtesting.tests.Test import Test


class SMACrossOverTest(Test):
    def __init__(self):
        self.strategies = [GoldenCross, GoldenCrossWithStopLoss, GoldenCrossWithTrailingStopLoss]

        super().__init__(self.__class__.__name__, self.strategies)

    def get_fast_period(self):
        return self.config['GoldenCross']['fast_period']

    def get_slow_period(self):
        return self.config['GoldenCross']['slow_period']

    def get_to_date(self):
        d = self.config['GoldenCross']['to_date']

        if d == "now":
            return datetime.now().date()
        else:
            return datetime.strptime(d, '%b-%d-%Y').date()

    def get_max_candles(self):
        return self.config['GoldenCross']['max_candles']

    def add_strategy(self, cerebro, strategy, symbol):
        cerebro.addstrategy(strategy, ticker=symbol,
                            fast_period=self.get_fast_period(), slow_period=self.get_slow_period(),
                            order_pct=self.get_order_percent())



