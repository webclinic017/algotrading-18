from trading.indicators.Indicator import Indicator
from trading.indicators.TrueRange import TrueRange
from trading.lines.Line import Line


class AverageTrueRange(Indicator):
    def __init__(self, period, candle_interval, candle_length):
        super().__init__(period, candle_interval, candle_length)
        self.true_range = TrueRange(period, candle_interval, candle_length)

    def calculate_lines(self, df_in):
        df = df_in.copy()
        true_range_line = self.true_range.calculate_lines(df_in)[0]
        df[self.true_range.__class__.__name__] = true_range_line.get_series()
        df[self.__class__.__name__] = df[self.true_range.__class__.__name__].rolling(self.candle_length).mean()
        return [Line(self.__class__.__name__, df[self.__class__.__name__])]
