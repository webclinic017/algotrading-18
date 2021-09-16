from trading.indicators.Indicator import Indicator
from trading.lines.Line import Line


class TrueRange(Indicator):
    def __init__(self, period, candle_interval, candle_length):
        super().__init__(period, candle_interval, candle_length)

    def calculate_lines(self, df_in):
        df = df_in.copy()
        df['H-L'] = abs(df['high'] - df['low'])
        df['H-PC'] = abs(df['high'] - df['close'].shift(1))
        df['L-PC'] = abs(df['low'] - df['close'].shift(1))
        df[self.__class__.__name__] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
        return [Line(self.__class__.__name__, df[self.__class__.__name__])]
