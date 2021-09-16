import numpy as np

from trading.indicators.AverageTrueRange import AverageTrueRange
from trading.indicators.Indicator import Indicator
from trading.lines.Line import Line


class SuperTrend(Indicator):
    def __init__(self, period, candle_interval, candle_length, multiplier):
        super().__init__(period, candle_interval, candle_length)

        self.atr = AverageTrueRange(period, candle_interval, candle_length)
        self.multiplier = multiplier

    def calculate_lines(self, df_in):
        df = df_in.copy()
        atr_name = self.atr.__class__.__name__
        st_name = self.__class__.__name__

        atr_line = self.atr.calculate_lines(df_in)[0]
        df[atr_name] = atr_line.get_series()

        # Basic upper and lower bands
        df['B-U'] = ((df['high'] + df['low']) / 2) + (df[atr_name] * self.multiplier)
        df['B-L'] = ((df['high'] + df['low']) / 2) - (df[atr_name] * self.multiplier)

        # Initialise final upper and lower bands
        df['U-B'] = df['B-U']
        df['L-B'] = df['B-L']

        # Iterate the dataframe
        ind = df.index
        for i in range(self.candle_length, len(df)):
            if df['close'][i - 1] > df['U-B'][i - 1]:
                df.loc[ind[i], 'U-B'] = df['B-U'][i]
            else:
                df.loc[ind[i], 'U-B'] = min(df['B-U'][i], df['U-B'][i - 1])

        for i in range(self.candle_length, len(df)):
            if df['close'][i - 1] < df['L-B'][i - 1]:
                df.loc[ind[i], 'L-B'] = df['B-L'][i]
            else:
                df.loc[ind[i], 'L-B'] = max(df['B-L'][i], df['L-B'][i - 1])

        df[st_name] = np.NaN
        df['crossover'] = 0

        # We have to iterate and find the first super trend
        # We cannot simply assume the first super trend to be upper or lower band value. This will give wrong signals
        # Once we find the first super trend, which is the correct one, then we can extend it easily
        for s in range(self.candle_length, len(df)):
            if (df['close'][s - 1] <= df['U-B'][s - 1]) and (df['close'][s] > df['U-B'][s]):
                df.loc[ind[s], st_name] = df['L-B'][s]
                df['crossover'] = 1
                break
            if (df['close'][s - 1] >= df['L-B'][s - 1]) and (df['close'][s] < df['L-B'][s]):
                df.loc[ind[s], st_name] = df['U-B'][s]
                df['crossover'] = -1
                break

        for i in range(s, len(df)):
            if (df[st_name][i - 1] == df['U-B'][i - 1]) and (df['close'][i] > df['U-B'][i]):
                df.loc[ind[i], st_name] = df['L-B'][i]
                df['crossover'] = 1
            elif (df[st_name][i - 1] == df['U-B'][i - 1]) and (df['close'][i] <= df['U-B'][i]):
                df.loc[ind[i], st_name] = df['U-B'][i]
                df['crossover'] = 0
            elif (df[st_name][i - 1] == df['L-B'][i - 1]) and (df['close'][i] < df['L-B'][i]):
                df.loc[ind[i], st_name] = df['U-B'][i]
                df['crossover'] = -1
            elif (df[st_name][i - 1] == df['L-B'][i - 1]) and (df['close'][i] >= df['L-B'][i]):
                df.loc[ind[i], st_name] = df['L-B'][i]
                df['crossover'] = 0

        return [Line(st_name, df[st_name]), Line('crossover', df['crossover'])]
