import backtrader as bt

class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        """ Logging function for this strategy """
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.lc = self.data0_1
        self.data_close = self.datas[0].close
        self.volume = self.data1.volume

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.data_close[0] + ' Volume ' + str(self.volume[0])
                 + 'CloseLines, %.2f' % self.lc[0])
