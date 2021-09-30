import pandas as pd

from trading.indicators.AverageTrueRange import AverageTrueRange
from trading.indicators.Indicator import Indicator


class SuperTrend(Indicator):
    def __init__(self, **kwargs):
        self.average_true_range = AverageTrueRange(**kwargs)
        self.multiplier = kwargs['multiplier']
        self.color_column_name = self.__class__.__name__ + "_Color"
        self.atr_name = self.average_true_range.__class__.__name__

        columns = {
            "open": "real(15,5)",
            "high": "real(15,5)",
            "low": "real(15,5)",
            "close": "real(15,5)",
            "AverageTrueRange": "real(15,5)",
            "BU": "real(15,5)",
            "BL": "real(15,5)",
            "UB": "real(15,5)",
            "LB": "real(15,5)",
            self.__class__.__name__: "real(15,5)",
            self.color_column_name: "varchar"
        }
        super().__init__(self.__class__.__name__, columns, **kwargs)

    def calculate_lines(self, candle_time):
        print(str(candle_time))
        st_df = self.indicator_db.get_indicator_value(self.get_n_candle_sequence(2, candle_time)[-1])
        if st_df.empty:
            self.calculate_super_trend(candle_time)
            return

        self.calculate_super_trend_from_previous_super_trend(st_df, candle_time)

    def calculate_super_trend(self, candle_time):
        ticks_df = self.get_data_from_ticks(candle_time)
        atr_df = self.average_true_range.get_lines(2, candle_time)

        # By now, we should have both the ticks and average true range values for the given candle length
        df = pd.concat([ticks_df, atr_df], axis=1)
        df.dropna(inplace=True)
        df = df.sort_index(ascending=True)

        # Basic upper and lower bands
        df['BU'] = ((df['high'] + df['low']) / 2) + (df[self.atr_name] * self.multiplier)
        df['BL'] = ((df['high'] + df['low']) / 2) - (df[self.atr_name] * self.multiplier)

        # Initialise final upper and lower bands
        df['UB'] = df['BU']
        df['LB'] = df['BL']

        df = self.calculate_bands(df)

        print(df)

        df[self.indicator_name] = 0.0
        df[self.color_column_name] = "na"

        # We have to iterate and find the first super trend
        # We cannot simply assume the first super trend to be upper or lower band value. This will give wrong signals
        # Once we find the first super trend, which is the correct one, then we can extend it easily
        ind = df.index
        for i in range(1, len(df)):
            if (df['close'][i - 1] <= df['UB'][i - 1]) and (df['close'][i] > df['UB'][i]):
                df.loc[ind[i], self.indicator_name] = df['LB'][i]
                df.loc[ind[i], self.color_column_name] = "green"
                break
            if (df['close'][i - 1] >= df['LB'][i - 1]) and (df['close'][i] < df['LB'][i]):
                df.loc[ind[i], self.indicator_name] = df['UB'][i]
                df.loc[ind[i], self.color_column_name] = "red"
                break

        self.store_super_trend_values(df)

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

    def calculate_super_trend_from_previous_super_trend(self, st_df, candle_time):
        print(st_df)
        ticks_df = self.get_data_from_ticks(candle_time)
        ticks_df = ticks_df.tail(1)

        curr_time = str(self.get_previous_indicator_time(candle_time))
        prev_time = str(self.get_n_candle_sequence(2, candle_time)[-1])
        prev_st_time = str(st_df.index[0])

        if prev_time != prev_st_time:
            raise ValueError("Previous ST for expected time not found. Actual time {}, Expected time {}".format(prev_st_time, prev_time))

        atr_df = self.average_true_range.get_lines(1, candle_time)
        if curr_time != str(atr_df.index[0]) or curr_time != str(ticks_df.index[0]):
            raise ValueError("ATR for expected time not found. Actual time {}, Expected time {}".format(atr_df.index[0], curr_time))

        _df = pd.concat([ticks_df, atr_df], axis=1)

        # Basic upper and lower bands
        _df['BU'] = ((_df['high'] + _df['low']) / 2) + (_df[self.atr_name] * self.multiplier)
        _df['BL'] = ((_df['high'] + _df['low']) / 2) - (_df[self.atr_name] * self.multiplier)

        # Initialise defaults
        _df['UB'] = _df['BU']
        _df['LB'] = _df['BL']
        _df[self.indicator_name] = 0.0
        _df[self.color_column_name] = "na"

        df = st_df.append(_df)
        df.dropna(inplace=True)
        df = df.sort_index(ascending=True)
        df = self.calculate_bands(df)

        ind = df.index
        for i in range(1, len(df)):
            if (df['close'][i - 1] <= df['UB'][i - 1]) and (df['close'][i] > df['UB'][i]):
                df.loc[ind[i], self.indicator_name] = df['LB'][i]
                df.loc[ind[i], self.color_column_name] = "green"
            elif (df['close'][i - 1] <= df['UB'][i - 1]) and (df['close'][i] <= df['UB'][i]) and (df[self.color_column_name][i - 1] == "red"):
                df.loc[ind[i], self.indicator_name] = df['UB'][i]
                df.loc[ind[i], self.color_column_name] = "red"
            elif (df['close'][i - 1] >= df['LB'][i - 1]) and (df['close'][i] < df['LB'][i]):
                df.loc[ind[i], self.indicator_name] = df['UB'][i]
                df.loc[ind[i], self.color_column_name] = "red"
            elif (df['close'][i - 1] >= df['LB'][i - 1]) and (df['close'][i] >= df['LB'][i]) and (df[self.color_column_name][i - 1] == "green"):
                df.loc[ind[i], self.indicator_name] = df['LB'][i]
                df.loc[ind[i], self.color_column_name] = "green"
            else:
                df.loc[ind[i], self.indicator_name] = df[self.indicator_name][i - 1]
                df.loc[ind[i], self.color_column_name] = df[self.color_column_name][i - 1]

        self.store_super_trend_values(df)


    def store_super_trend_values(self, df):
        for i in range(1, len(df)):
            self.indicator_db.put_indicator_value(df.index[i],
                                                  [df['open'][i],
                                                   df['high'][i],
                                                   df['low'][i],
                                                   df['close'][i],
                                                   df['AverageTrueRange'][i],
                                                   df['BU'][i],
                                                   df['BL'][i],
                                                   df['UB'][i],
                                                   df['LB'][i],
                                                   df[self.indicator_name][i],
                                                   df[self.color_column_name][i]])






