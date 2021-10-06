import pandas as pd

from trading.indicators.Indicator import Indicator


class AverageTrueRange(Indicator):
    def __init__(self, strategy, **kwargs):
        super().__init__(self.__class__.__name__, strategy, **kwargs)

        self.true_range = strategy.get_true_range_indicator()

        if not self.true_range:
            raise ValueError("True range indicator is not initialised")

    def calculate_lines(self, candle_time):
        atr_df = self.values.tail(1)
        if atr_df.empty:
            self.calculate_atr(candle_time)
            return

        self.calculate_atr_from_previous_value(atr_df, candle_time)

    def calculate_atr(self, candle_time):
        df = self.true_range.get_lines(self.candle_length, candle_time)

        df[self.indicator_name] = \
            df[self.true_range.__class__.__name__].rolling(self.candle_length).mean()

        df.dropna(inplace=True)
        df.drop(self.true_range.__class__.__name__, axis=1, inplace=True)

        self.store_indicator_value(df.tail(1), candle_time)

    def calculate_atr_from_previous_value(self, atr_df, candle_time):
        tr_df = self.true_range.get_lines(1, candle_time)

        df = pd.DataFrame()
        prev_atr = atr_df[self.indicator_name][0]
        tr = tr_df[self.true_range.indicator_name][0]
        new_atr = ((prev_atr * (self.candle_length - 1)) + tr) / self.candle_length

        df.loc[tr_df.index[0], 'open'] = tr_df['open'][0]
        df.loc[tr_df.index[0], 'high'] = tr_df['high'][0]
        df.loc[tr_df.index[0], 'low'] = tr_df['low'][0]
        df.loc[tr_df.index[0], 'close'] = tr_df['close'][0]
        df.loc[tr_df.index[0], self.indicator_name] = new_atr

        self.store_indicator_value(df.tail(1), candle_time)

