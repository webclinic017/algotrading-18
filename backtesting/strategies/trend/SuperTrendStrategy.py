import math

import backtrader as bt
from backtesting.indicators.SuperTrend import SuperTrend


class SuperTrendStrategy(bt.Strategy):
    def __init__(self, **kwargs):
        self.ticker = kwargs['ticker']
        self.atr_period = kwargs['atr_period']
        self.atr_multiplier = kwargs['atr_multiplier']
        self.order_pct = kwargs['order_pct']

        self.super_trend = SuperTrend(period=self.atr_period, multiplier=self.atr_multiplier)

    def notify_order(self, order):
        if not order.status == order.Completed:
            return  # discard any other notification

        if not self.position:  # we left the market
            # print('SELL@price: {:.2f}'.format(order.executed.price))
            return

        stop_price = order.executed.price * (1.0 - 0.15)
        self.sell(exectype=bt.Order.Stop, price=stop_price)

    def next(self):
        if self.super_trend.upper_to_lower_crossover > 0:
            amount_to_invest = (self.order_pct * self.broker.cash)
            self.size = math.floor(amount_to_invest / self.data.close)

            # print("Buy {} shares of {} at {} on {}".format(self.size, self.ticker, self.data.close[0],
            #                                               self.data.datetime.date()))
            self.buy(size=self.size)

    def stop(self):
        # Close all open positions
        target_size = 0
        self.order = self.order_target_size(target=target_size)
