from trading.indicators.Indicator import Indicator


class SuperTrend(Indicator):
    def __init__(self, strategy, **kwargs):
        self.st_band = strategy.get_super_trend_band_indicator()

        super().__init__(self.__class__.__name__, strategy, **kwargs)

    def calculate_lines(self, candle_time):
        st_df = self.values.tail(1)
        if st_df.empty:
            prev_indicator = 0.0
            prev_color = "na"
        else:
            prev_indicator = st_df[self.indicator_name][0]
            prev_color = st_df['color'][0]

        df = self.st_band.get_lines(2, candle_time)

        df[self.indicator_name] = 0.0
        df['color'] = "na"

        ind = df.index
        for i in range(1, len(df)):
            if (df['close'][i - 1] <= df['UB'][i - 1]) and (df['close'][i] > df['UB'][i]):
                df.loc[ind[i], self.indicator_name] = df['LB'][i]
                df.loc[ind[i], 'color'] = "green"
            elif (df['close'][i - 1] >= df['LB'][i - 1]) and (df['close'][i] < df['LB'][i]):
                df.loc[ind[i], self.indicator_name] = df['UB'][i]
                df.loc[ind[i], 'color'] = "red"
            else:
                df.loc[ind[i], self.indicator_name] = prev_indicator
                df.loc[ind[i], 'color'] = prev_color

        df = df[['open', 'high', 'low', 'close', self.indicator_name, 'color']]
        self.store_indicator_value(df.tail(1), candle_time)







