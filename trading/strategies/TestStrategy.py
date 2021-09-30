from trading.indicators.AverageTrueRange import AverageTrueRange
from trading.indicators.SuperTrend import SuperTrend
from trading.indicators.TrueRange import TrueRange
from trading.strategies.Strategy import Strategy


class TestStrategy(Strategy):
    def __init__(self, **kwargs):
        super().__init__([SuperTrend(**kwargs), AverageTrueRange(**kwargs), TrueRange(**kwargs)], **kwargs)

    def act(self, cash_available):
        pass

