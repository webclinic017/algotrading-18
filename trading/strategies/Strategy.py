from abc import ABC, abstractmethod


class Strategy(ABC):
    def __init__(self, period, candle_interval, candle_length, orders, **kwargs):
        self.period = period
        self.candle_length = candle_length
        self.candle_interval = candle_interval
        self.orders = orders
        pass

    @abstractmethod
    def act(self, symbol, cash_available, margin, order_pct, df):
        pass

    def take_long_position(self, symbol, quantity, sl_price, current_price, cash_available, margin, order_pct, data):
        self.validate_transaction(cash_available, margin, order_pct, data)
        self.orders.buy_intraday_with_stop_loss(symbol, quantity, sl_price, quantity * current_price)
        pass

    def take_short_position(self, symbol, quantity, sl_price, current_price, cash_available, margin, order_pct, data):
        self.validate_transaction(cash_available, margin, order_pct, data)
        self.orders.sell_intraday_with_stop_loss(symbol, quantity, sl_price, quantity * current_price)
        pass

    def validate_transaction(self, cash_available, margin, order_pct, df):
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
