import logging
from abc import ABC, abstractmethod

from trading.db.IndicatorDB import IndicatorDB
from trading.db.TicksDB import TicksDB
from trading.errors.DataNotAvailableError import DataNotAvailableError
from trading.zerodha.kite.Period import Period
from trading.zerodha.kite.TimeSequencer import get_previous_time, get_time_sequence


class Indicator(ABC):
    def __init__(self, name, columns, **kwargs):
        self.symbol = kwargs['symbol']
        self.period = kwargs['period']
        self.candle_length = kwargs['candle_length']
        self.candle_interval = kwargs['candle_interval']
        self.db_path = kwargs['db_path']
        self.instruments_db = kwargs['instruments_db']
        self.indicator_name = name
        self.indicator_columns = columns
        self.indicator_table_name = self.indicator_name + "_" + self.symbol + "_" + str(self.candle_interval) + "_" + self.period.name
        self.indicator_db = IndicatorDB(name=self.indicator_table_name, columns=self.indicator_columns)

        if self.period == Period.MIN:
            self.resample_time = str(self.candle_interval) + 'Min'

    @abstractmethod
    def calculate_lines(self, candle_time):
        pass

    def get_previous_indicator_time(self, candle_time):
        return get_previous_time(self.period, self.candle_interval, candle_time)

    def get_previous_indicator_value(self, candle_time):
        candle_time = self.get_previous_indicator_time(candle_time)
        return self.indicator_db.get_indicator_value(candle_time)

    def resample_data(self, df):
        ticks = df.loc[:, ['price']]
        resampled_df = ticks['price'].resample(self.resample_time).ohlc()
        # resampled_df.dropna(inplace=True)
        return resampled_df

    def get_ticks(self, start_time, end_time):
        logging.info("Fetching ticks data for {} from {} till {}".format(self.symbol, start_time, end_time))
        ticks_db = TicksDB(self.db_path, self.instruments_db)
        df = ticks_db.get_ticks(self.symbol, start_time, end_time)
        ticks_db.close()

        return df

    def get_data_from_ticks(self, candle_end_time):
        candle_sequence = self.get_candle_sequence(candle_end_time)
        candle_start_time = candle_sequence[-1]

        print(candle_sequence)

        ticks = self.get_ticks(candle_start_time, candle_end_time)

        if ticks.empty:
            err_str = "No ticks available for indicator {}".format(self.indicator_name)
            logging.info(err_str)
            raise DataNotAvailableError(err_str)

        df = self.resample_data(ticks)
        print(df)

        if len(df) != len(candle_sequence):
            err_str = "Expecting {} number of {} {} candles, but found {} candles for indicator {}"\
                .format(self.candle_length, self.candle_interval, self.period.name, str(len(df)), self.indicator_name)
            logging.info(err_str)
            raise DataNotAvailableError(err_str)

        return df

    def get_candle_sequence(self, candle_end_time):
        return get_time_sequence(self.period, self.candle_interval, self.candle_length, candle_end_time)


