from trading.indicators.AverageTrueRange import AverageTrueRange
from trading.indicators.TrueRange import TrueRange
from trading.strategies.Strategy import Strategy


class TestStrategy(Strategy):
    def __init__(self, **kwargs):
        super().__init__([TrueRange(**kwargs), AverageTrueRange(**kwargs)], **kwargs)

    def act(self, cash_available):
        pass

