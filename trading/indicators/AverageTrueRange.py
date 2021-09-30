import pandas as pd

from trading.indicators.Indicator import Indicator
from trading.indicators.TrueRange import TrueRange


class AverageTrueRange(Indicator):
    def __init__(self, **kwargs):
        super().__init__(self.__class__.__name__, {self.__class__.__name__: "real(15,5)"}, **kwargs)

        self.true_range = TrueRange(**kwargs)

    def calculate_lines(self, candle_time):
        atr_df = self.indicator_db.get_indicator_value(self.get_n_candle_sequence(2, candle_time)[-1])
        if atr_df.empty:
            self.calculate_atr(candle_time)
            return

        self.calculate_atr_from_previous_value(atr_df, candle_time)

    def calculate_atr(self, candle_time):
        true_range_df = self.true_range.get_lines(3, candle_time)

        true_range_df[self.indicator_name] = \
            true_range_df[self.true_range.__class__.__name__].rolling(self.candle_length).mean()

        true_range_df.dropna(inplace=True)

        self.store_indicator_value(true_range_df)

    def calculate_atr_from_previous_value(self, atr_df, candle_time):
        prev_time = str(self.get_n_candle_sequence(2, candle_time)[-1])
        prev_atr_time = str(atr_df.index[0])

        if prev_time != prev_atr_time:
            raise ValueError("Previous ST for expected time not found. Actual time {}, Expected time {}".format(prev_st_time, prev_time))

        tr_df = self.true_range.get_lines(1, candle_time)
        curr_time = str(self.get_previous_indicator_time(candle_time))

        if curr_time != str(tr_df.index[0]):
            raise ValueError("TR for expected time not found. Actual time {}, Expected time {}".format(tr_df.index[0], curr_time))

        if len(atr_df) != 1 or len(tr_df) != 1:
            raise ValueError("Data frame contains too many records. atr_df: {}, tr_df: {}".format(len(atr_df), len(tr_df)))

        df = pd.DataFrame()
        prev_atr = atr_df[self.indicator_name][0]
        tr = tr_df[self.true_range.indicator_name][0]
        new_atr = ((prev_atr * (self.candle_length - 1)) + tr) / self.candle_length

        df.loc[tr_df.index[0], self.indicator_name] = new_atr

        self.store_indicator_value(df)

    def store_indicator_value(self, df):
        for i, v in df[self.indicator_name].items():
            self.indicator_db.put_indicator_value(i, [v])

