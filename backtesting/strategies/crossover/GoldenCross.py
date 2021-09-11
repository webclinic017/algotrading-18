import math

import backtrader as bt


class GoldenCross(bt.Strategy):
    def __init__(self, **kwargs):
        self.ticker = kwargs['ticker']
        self.fast_period = kwargs['fast_period']
        self.slow_period = kwargs['slow_period']
        self.order_pct = 1.0

        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close,
            period=self.fast_period
        )

        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close,
            period=self.slow_period
        )

        self.crossover = bt.indicators.CrossOver(
            self.fast_ma,
            self.slow_ma
        )

    def next(self):
        if self.position.size == 0:
            if self.crossover > 0:
                amount_to_invest = (self.order_pct * self.broker.cash)
                self.size = math.floor(amount_to_invest / self.data.close)

                # print("Buy {} shares of {} at {} on {}".format(self.size, self.ticker, self.data.close[0],
                #                                               self.data.datetime.date()))
                self.buy(size=self.size)

        if self.position.size > 0:
            if self.crossover < 0:
                # print("Sell {} shares of {} at {} on {}".format(self.size, self.ticker, self.data.close[0],
                #                                                self.data.datetime.date()))
                self.close()

    def get_name(self):
        return self.__class__.__name__

    def stop(self):
        # Close all open positions
        target_size = 0
        self.order = self.order_target_size(target=target_size)
