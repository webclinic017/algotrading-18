from backtesting.tests.crossover.SMACrossOverTest import SMACrossOverTest
from backtesting.tests.trend.SuperTrendTest import SuperTrendTest
from trading.TradeMain import TradeMain

if __name__ == '__main__':
    # test = SuperTrendTest()
    # print("Running {}".format(test.__class__.__name__))
    # test.run()
    trade = TradeMain()
    trade.trade()
