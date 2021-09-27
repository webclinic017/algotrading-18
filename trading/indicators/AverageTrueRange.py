from trading.indicators.Indicator import Indicator
from trading.indicators.TrueRange import TrueRange


class AverageTrueRange(Indicator):
    def __init__(self, **kwargs):
        super().__init__(self.__class__.__name__, {self.__class__.__name__: "real(15,5)"}, **kwargs)

        self.true_range = TrueRange(**kwargs)

    def calculate_lines(self, candle_time):
        true_range_df = self.true_range.get_lines(3, candle_time)

        true_range_df[self.indicator_name] = \
            true_range_df[self.true_range.__class__.__name__].rolling(self.candle_length).mean()

        true_range_df.dropna(inplace=True)

        for i, v in true_range_df[self.indicator_name].items():
            self.indicator_db.put_indicator_value(i, [v])
