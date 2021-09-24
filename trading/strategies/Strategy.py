import logging

from abc import ABC, abstractmethod


class Strategy(ABC):
    def __init__(self, indicators, **kwargs):
        logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s', level=logging.INFO)
        self.indicators = indicators
        self.symbol = kwargs['symbol']
        self.period = kwargs['period']
        self.candle_length = kwargs['candle_length']
        self.candle_interval = kwargs['candle_interval']
        self.margin = kwargs['margin']
        self.order_pct = kwargs['order_pct']
        self.orders = kwargs['orders']

    @abstractmethod
    def act(self, cash_available):
        pass

    def take_long_position(self, quantity, sl_price, current_price, cash_available):
        self.validate_transaction(cash_available, current_price)
        self.orders.buy_intraday_with_stop_loss(self.symbol, quantity, sl_price, quantity * current_price)
        pass

    def take_short_position(self, quantity, sl_price, current_price, cash_available):
        self.validate_transaction(cash_available, current_price)
        self.orders.sell_intraday_with_stop_loss(self.symbol, quantity, sl_price, quantity * current_price)
        pass

    def get_indicators(self):
        return self.indicators

    def validate_transaction(self, cash_available, current_price):
        cash_required_for_one_stock = current_price * self.margin
        disposable_cash = cash_available * self.order_pct
        quantity = disposable_cash / cash_required_for_one_stock
        total_cash_needed = quantity * current_price
        margin_available = cash_available * (1 / self.margin)

        if margin_available < total_cash_needed:
            raise ValueError(
                "Stock is too expensive. Investment is {}, margin available {}, current price {}, "
                "quantity {} ".format(total_cash_needed, margin_available, current_price, quantity))
