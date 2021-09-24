import logging

from trading.errors.DataNotAvailableError import DataNotAvailableError
from trading.indicators.Indicator import Indicator


class TrueRange(Indicator):
    def __init__(self, **kwargs):
        columns = {self.__class__.__name__: "real(15,5)"}
        super().__init__(self.__class__.__name__, columns, **kwargs)

    def calculate_lines(self, candle_time):
        df = self.get_data_from_ticks(candle_time)

        logging.info("Obtained data for {} at {}".format(self.symbol, candle_time))
        print(df)

        df['H-L'] = abs(df['high'] - df['low'])
        df['H-PC'] = abs(df['high'] - df['close'].shift(1))
        df['L-PC'] = abs(df['low'] - df['close'].shift(1))
        df[self.__class__.__name__] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)

        df.dropna(inplace=True)

        for i, v in df[self.__class__.__name__].items():
            self.indicator_db.put_indicator_value(i, [v])

    def get_lines(self, candle_time):
        candle_sequence = self.get_candle_sequence(candle_time)
        start_time = candle_sequence[-1]
        df = self.indicator_db.get_indicator_value(start_time, candle_time)

        if df.empty:
            err_str = "Expecting {} number of {} {} candles, but found {} candles for indicator {}" \
                .format(self.candle_length, self.candle_interval, self.period.name, str(len(df)), self.indicator_name)
            logging.info(err_str)
            raise DataNotAvailableError(err_str)

        return df

