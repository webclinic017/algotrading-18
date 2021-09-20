from trading.strategies.Strategy import Strategy
from trading.indicators.SuperTrend import SuperTrend


class SuperTrendStrategy(Strategy):
    def __init__(self, period, candle_interval, candle_length, orders, **kwargs):
        super().__init__(period, candle_interval, candle_length, orders)

        self.multiplier = kwargs['multiplier']
        self.super_trend = SuperTrend(self.period, self.candle_interval, self.candle_length, self.multiplier)

    def act(self, symbol, cash_available, margin, order_pct, df_in):
        df = df_in.copy()
        lines = self.super_trend.calculate_lines(df)

        for l in lines:
            df[l.get_name()] = l.get_series()

        current_price = df['close'][-1]
        cash_required_for_one_stock = current_price * margin
        disposable_cash = cash_available * order_pct
        quantity = disposable_cash / cash_required_for_one_stock
        total_cash_needed = quantity * current_price
        margin_available = cash_available * (1 / margin)

        if margin_available < total_cash_needed:
            raise ValueError(
                "Stock is too expensive. Investment is {}, margin available {}, current price {}, "
                "quantity {} ".format(total_cash_needed, margin_available, current_price, quantity))

        if df['color'][-1] == "red" and df['color'][-2] == "green":
            self.take_short_position(symbol, quantity, df['SuperTrend'][-1], current_price, cash_available,
                                    margin, order_pct, df)
        elif df['color'][-1] == "green" and df['color'][-2] == "red":
            self.take_long_position(symbol, quantity, df['SuperTrend'][-1], current_price, cash_available,
                                     margin, order_pct, df)

        return df
