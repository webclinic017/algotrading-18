import pandas as pd

from trading.indicators.AverageTrueRange import AverageTrueRange
from trading.indicators.Indicator import Indicator


class SuperTrend(Indicator):
    def __init__(self, **kwargs):
        self.average_true_range = AverageTrueRange(**kwargs)
        self.multiplier = kwargs['multiplier']
        self.color_column_name = self.__class__.__name__ + "_Color"

        columns = {
            self.__class__.__name__: "real(15,5)",
            self.color_column_name: "text"
        }
        super().__init__(self.__class__.__name__, columns, **kwargs)

    def calculate_lines(self, candle_time):
        self.calculate_super_trend(candle_time)

    def calculate_super_trend(self, candle_time):
        ticks_df = self.get_data_from_ticks(candle_time)
        atr_df = self.average_true_range.get_lines(2, candle_time)

        # By now, we should have both the ticks and average true range values for the given candle length
        df = pd.concat([ticks_df, atr_df])

        atr_name = self.average_true_range.__class__.__name__
        st_name = self.indicator_name

        # Basic upper and lower bands
        df['B-U'] = ((df['high'] + df['low']) / 2) + (df[atr_name] * self.multiplier)
        df['B-L'] = ((df['high'] + df['low']) / 2) - (df[atr_name] * self.multiplier)

        # Initialise final upper and lower bands
        df['U-B'] = df['B-U']
        df['L-B'] = df['B-L']

        # Iterate the dataframe
        ind = df.index
        for i in range(len(df)):
            if df['close'][i - 1] > df['U-B'][i - 1] or df['B-U'][i] < df['U-B'][i - 1]:
                df.loc[ind[i], 'U-B'] = df['B-U'][i]
            else:
                df.loc[ind[i], 'U-B'] = min(df['B-U'][i], df['U-B'][i - 1])

        for i in range(self.candle_length + 1, len(df)):
            if df['close'][i - 1] < df['L-B'][i - 1] or df['B-L'][i] > df['L-B'][i - 1]:
                df.loc[ind[i], 'L-B'] = df['B-L'][i]
            else:
                df.loc[ind[i], 'L-B'] = max(df['B-L'][i], df['L-B'][i - 1])

        df[st_name] = 0
        df[self.color_column_name] = "na"

        # We have to iterate and find the first super trend
        # We cannot simply assume the first super trend to be upper or lower band value. This will give wrong signals
        # Once we find the first super trend, which is the correct one, then we can extend it easily
        for s in range(len(df)):
            if (df['close'][s - 1] <= df['U-B'][s - 1]) and (df['close'][s] > df['U-B'][s]):
                df.loc[ind[s], st_name] = df['L-B'][s]
                df.loc[ind[s], self.color_column_name] = "green"
                break
            if (df['close'][s - 1] >= df['L-B'][s - 1]) and (df['close'][s] < df['L-B'][s]):
                df.loc[ind[s], st_name] = df['U-B'][s]
                df.loc[ind[s], self.color_column_name] = "red"
                break

        if s + 1 >= len(df):
            # We did not find a cross over
            pass
        else:
            for i in range(s + 1, len(df)):
                if (df[st_name][i - 1] == df['U-B'][i - 1]) and (df['close'][i] > df['U-B'][i]):
                    df.loc[ind[i], st_name] = df['L-B'][i]
                    df.loc[ind[i], self.color_column_name] = "green"
                elif (df[st_name][i - 1] == df['U-B'][i - 1]) and (df['close'][i] <= df['U-B'][i]):
                    df.loc[ind[i], st_name] = df['U-B'][i]
                    df.loc[ind[i], self.color_column_name] = df[self.color_column_name][i - 1]
                elif (df[st_name][i - 1] == df['L-B'][i - 1]) and (df['close'][i] < df['L-B'][i]):
                    df.loc[ind[i], st_name] = df['U-B'][i]
                    df.loc[ind[i], self.color_column_name] = "red"
                elif (df[st_name][i - 1] == df['L-B'][i - 1]) and (df['close'][i] >= df['L-B'][i]):
                    df.loc[ind[i], st_name] = df['L-B'][i]
                    df.loc[ind[i], self.color_column_name] = df[self.color_column_name][i - 1]
                else:
                    df.loc[ind[i], st_name] = df[st_name][i - 1]
                    df.loc[ind[i], self.color_column_name] = df[self.color_column_name][i - 1]

        self.store_super_trend_values(df)

    def store_super_trend_values(self, df):
        for i in range(len(df)):
            self.indicator_db.put_indicator_value(df.index[i], [df[self.indicator_name][i], df[self.color_column_name][i]])






