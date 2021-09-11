import math

import backtrader as bt


class GoldenCrossWithStopLoss(bt.Strategy):
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

    def notify_order(self, order):
        if not order.status == order.Completed:
            return  # discard any other notification

        if not self.position:  # we left the market
            # print('SELL@price: {:.2f}'.format(order.executed.price))
            return

        # We have entered the market
        # print('BUY @price: {:.2f}'.format(order.executed.price))

        stop_price = order.executed.price * (1.0 - 0.15)
        self.sell(exectype=bt.Order.Stop, price=stop_price)

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

    def stop(self):
        # Close all open positions
        target_size = 0
        self.order = self.order_target_size(target=target_size)

    def get_name(self):
        return self.__class__.__name__
