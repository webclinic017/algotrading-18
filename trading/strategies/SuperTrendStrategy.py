from trading.strategies.Strategy import Strategy
from trading.indicators.SuperTrend import SuperTrend


class SuperTrendStrategy(Strategy):
    def __init__(self, period, candle_interval, candle_length, **kwargs):
        super().__init__(period, candle_interval)

        self.candle_length = candle_length
        self.multiplier = kwargs['multiplier']
        self.super_trend = SuperTrend(self.period, self.candle_interval, self.candle_length, self.multiplier)

    def act(self, df_in):
        df = df_in.copy()
        lines = self.super_trend.calculate_lines(df)

        for l in lines:
            df[l.get_name()] = l.get_series()

        print(df.tail())
        return df
