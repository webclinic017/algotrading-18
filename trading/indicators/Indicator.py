import logging
from abc import ABC, abstractmethod

import pandas as pd

from trading.db.IndicatorDB import IndicatorDB
from trading.db.TicksDB import TicksDB
from trading.errors.DataNotAvailableError import DataNotAvailableError
from trading.zerodha.kite.Period import Period
from trading.zerodha.kite.Retry import retry
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
        if df.empty:
            return df

        ticks = df.loc[:, ['price']]
        resampled_df = ticks['price'].resample(self.resample_time).ohlc()
        resampled_df.index = pd.to_datetime(resampled_df.index)
        resampled_df = resampled_df.sort_index(ascending=True)
        # resampled_df.dropna(inplace=True)
        return resampled_df

    @retry(tries=5, delay=2, backoff=1)
    def get_lines(self, n, candle_time):
        candle_sequence = self.get_n_candle_sequence(n, candle_time)
        start_time = candle_sequence[-1]
        df = self.indicator_db.get_indicator_values(start_time, candle_time)
        self.validate_candles(df, reversed(candle_sequence))
        return df

    def get_ticks(self, start_time, end_time):
        logging.info("Fetching ticks data for {} from {} till {}".format(self.symbol, start_time, end_time))
        ticks_db = TicksDB(self.db_path, self.instruments_db)
        df = ticks_db.get_ticks(self.symbol, start_time, end_time)
        ticks_db.close()

        return df

    def get_data_from_ticks(self, candle_end_time):
        candle_sequence = self.get_candle_sequence(candle_end_time)
        candle_start_time = candle_sequence[-1]

        ticks = self.get_ticks(candle_start_time, candle_end_time)
        df = self.resample_data(ticks)

        self.validate_candles(df, reversed(candle_sequence))

        return df

    def get_candle_sequence(self, candle_end_time):
        return get_time_sequence(self.period, self.candle_interval, self.candle_length, candle_end_time)

    def get_n_candle_sequence(self, n, candle_end_time):
        return get_time_sequence(self.period, self.candle_interval, n, candle_end_time)

    def validate_candles(self, actual_candles_in, expected_candles):
        actual_candles = []
        for i in range(len(actual_candles_in)):
            actual_candles.append(str(actual_candles_in.index[i]))

        expected_candles = [str(i) for i in expected_candles]

        if actual_candles != expected_candles:
            logging.info("Expected candles: {} for indicator: {}".format(expected_candles, self.indicator_name))
            logging.info("Actual candles: {} for indicator: {}".format(str(actual_candles), self.indicator_name))

            raise DataNotAvailableError("Data not available")






