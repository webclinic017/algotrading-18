import logging

from trading.errors.DataNotAvailableError import DataNotAvailableError
from trading.indicators.Indicator import Indicator


class TrueRange(Indicator):
    def __init__(self, **kwargs):
        columns = {self.__class__.__name__: "real(15,5)"}
        super().__init__(self.__class__.__name__, columns, **kwargs)

    def calculate_lines(self, candle_time):
        df = self.get_data_from_ticks(candle_time)

        df['H-L'] = abs(df['high'] - df['low'])
        df['H-PC'] = abs(df['high'] - df['close'].shift(1))
        df['L-PC'] = abs(df['low'] - df['close'].shift(1))
        df[self.indicator_name] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)

        df.dropna(inplace=True)

        for i, v in df[self.indicator_name].items():
            self.indicator_db.put_indicator_value(i, [v])

    def get_lines(self, candle_time):
        candle_sequence = self.get_candle_sequence(candle_time)
        start_time = candle_sequence[-1]
        df = self.indicator_db.get_indicator_value(start_time, candle_time)

        return df
