from trading.indicators.Indicator import Indicator


class TrueRange(Indicator):
    def __init__(self, strategy, **kwargs):
        super().__init__(self.__class__.__name__, strategy, **kwargs)

        # For true range, previous and current candles are enough
        self.candle_length = 2

    def calculate_lines(self, candle_time):
        df = self.get_data_from_ticks(candle_time)

        df['H-L'] = abs(df['high'] - df['low'])
        df['H-PC'] = abs(df['high'] - df['close'].shift(1))
        df['L-PC'] = abs(df['low'] - df['close'].shift(1))
        df[self.indicator_name] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)

        df.dropna(inplace=True)
        df.drop('H-L', axis=1, inplace=True)
        df.drop('H-PC', axis=1, inplace=True)
        df.drop('L-PC', axis=1, inplace=True)
        self.store_indicator_value(df.tail(1), candle_time)
