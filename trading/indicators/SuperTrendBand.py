from trading.indicators.Indicator import Indicator


class SuperTrendBand(Indicator):
    def __init__(self, strategy, **kwargs):
        self.average_true_range = strategy.get_average_true_range_indicator()
        self.atr_name = self.average_true_range.__class__.__name__

        self.multiplier = kwargs['multiplier']

        super().__init__(self.__class__.__name__, strategy, **kwargs)

    def calculate_lines(self, candle_time):
        st_band_df = self.values.tail(1)
        if st_band_df.empty:
            self.calculate_super_trend_band(candle_time)
            return

        self.calculate_super_trend_from_previous_super_trend(st_band_df, candle_time)

    def calculate_super_trend_band(self, candle_time):
        df = self.average_true_range.get_lines(1, candle_time)

        df = self.init_bands(df)
        df = self.calculate_bands(df)

        df.drop(self.atr_name, axis=1, inplace=True)

        self.store_indicator_value(df.tail(1), candle_time)

    def calculate_super_trend_from_previous_super_trend(self, st_band_df, candle_time):
        _df = self.average_true_range.get_lines(1, candle_time)
        _df = self.init_bands(_df)

        _df.drop(self.atr_name, axis=1, inplace=True)
        df = st_band_df.append(_df)
        df.dropna(inplace=True)
        df = df.sort_index(ascending=True)
        df = self.calculate_bands(df)

        self.store_indicator_value(df.tail(1), candle_time)

    def init_bands(self, df_in):
        df = df_in.copy()

        # Basic upper and lower bands
        df['BU'] = ((df['high'] + df['low']) / 2) + (df[self.atr_name] * self.multiplier)
        df['BL'] = ((df['high'] + df['low']) / 2) - (df[self.atr_name] * self.multiplier)

        # Initialise final upper and lower bands
        df['UB'] = df['BU']
        df['LB'] = df['BL']

        return df

    def calculate_bands(self, df_in):
        df = df_in.copy()
        ind = df.index
        for i in range(1, len(df)):
            if df['close'][i - 1] > df['UB'][i - 1]:
                df.loc[ind[i], 'UB'] = df['BU'][i]
            else:
                df.loc[ind[i], 'UB'] = min(df['BU'][i], df['UB'][i - 1])

        for i in range(1, len(df)):
            if df['close'][i - 1] < df['LB'][i - 1]:
                df.loc[ind[i], 'LB'] = df['BL'][i]
            else:
                df.loc[ind[i], 'LB'] = max(df['BL'][i], df['LB'][i - 1])

        return df








