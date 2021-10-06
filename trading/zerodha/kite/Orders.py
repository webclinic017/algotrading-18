import logging
from math import floor

import pandas as pd

from trading.zerodha.kite.Retry import retry


class Orders:
    def __init__(self, kite, leverage, order_pct, exchange):
        logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s', level=logging.INFO)
        self.kite = kite
        self.leverage = leverage
        self.order_pct = order_pct
        self.exchange = exchange

    def buy_intraday_with_stop_loss(self, symbol, sl_price, current_price):
        quantity = self.get_quantity(symbol, current_price)
        self.place_mis_market_order(symbol, "buy", quantity, current_price)
        self.place_mis_sl_order(symbol, "sell", quantity, sl_price)

    def sell_intraday_with_stop_loss(self, symbol, sl_price, current_price):
        quantity = self.get_quantity(symbol, current_price)
        self.place_mis_market_order(symbol, "sell", quantity, current_price)
        self.place_mis_sl_order(symbol, "buy", quantity, sl_price)

    def get_quantity(self, symbol, current_price):
        # cash_available = self.kite.margins("equity")['net']
        cash_available = 3000
        total_margin = cash_available * self.leverage
        disposable_margin = total_margin * self.order_pct
        quantity = floor(disposable_margin / current_price)

        if quantity <= 0:
            raise ValueError(
                "Stock {} is too expensive. Margin available {}, Cash available {}, Cash needed {}, current price {}, "
                .format(symbol, disposable_margin, cash_available, current_price - disposable_margin, current_price))

        return quantity

    @retry(tries=5, delay=2, backoff=2)
    def open_positions(self):
        df = pd.DataFrame(self.kite.positions()["day"])
        long_positions = df[df.quantity > 0]
        short_positions = df[df.quantity < 0]
        return long_positions, short_positions

    @retry(tries=5, delay=2, backoff=2)
    def open_orders(self):
        ord_df = pd.DataFrame(self.kite.orders())
        return ord_df[ord_df['status'].isin(["TRIGGER PENDING", "OPEN"])]["order_id"].tolist()

    @retry(tries=5, delay=2, backoff=2)
    def place_mis_market_order(self, symbol, transaction_type, quantity, current_price):
        purchase_str = "{} {} quantities of {} scrip. Total trade value {}. Current price {}" \
            .format(transaction_type, quantity, symbol, quantity * current_price, current_price)

        logging.info(purchase_str)

        '''
        transaction_type = self.get_transaction_type(transaction_type)

        self.kite.place_order(tradingsymbol=symbol,
                              exchange=self.exchange,
                              transation_type=transaction_type,
                              quantity=quantity,
                              order_type=self.kite.ORDER_TYPE_MARKET,
                              product=self.kite.PRODUCT_MIS,
                              variety=self.kite.VARIETY_REGULAR)
        '''

    @retry(tries=5, delay=2, backoff=2)
    def place_mis_sl_order(self, symbol, transaction_type, quantity, sl_price):
        purchase_str = "Setting {} stop loss for {} {} at price {}" \
            .format(transaction_type, quantity, symbol, sl_price)

        logging.info(purchase_str)

        '''
        transaction_type = self.get_transaction_type(transaction_type)

        self.kite.place_order(tradingsymbol=symbol,
                              exchange=self.exchange,
                              transation_type=transaction_type,
                              quantity=quantity,
                              order_type=self.kite.ORDER_TYPE_SLM,
                              price=sl_price,
                              trigger_price=sl_price,
                              product=self.kite.PRODUCT_MIS,
                              variety=self.kite.VARIETY_REGULAR)
        '''

    @retry(tries=5, delay=2, backoff=2)
    def cancel_order(self, order_id):
        self.kite.cancel_order(order_id=order_id, variety=self.kite.VARIETY_REGULAR)

    @retry(tries=5, delay=2, backoff=2)
    def place_bracket_order(self, symbol, transaction_type, quantity, atr, price):
        transaction_type = self.get_transaction_type(transaction_type)

        self.kite.place_order(tradingsymbol=symbol,
                              exchange=self.exchange,
                              transaction_type=transaction_type,
                              quantity=quantity,
                              order_type=self.kite.ORDER_TYPE_LIMIT,
                              price=price,  # BO has to be a limit order, set a low price threshold
                              product=self.kite.PRODUCT_MIS,
                              variety=self.kite.VARIETY_BO,
                              squareoff=int(6 * atr),
                              stoploss=int(3 * atr),
                              trailing_stoploss=2)

    @retry(tries=5, delay=2, backoff=2)
    def get_available_cash(self):
        return self.kite.margins("equity")['available']['cash']

    def get_transaction_type(self, transaction_type):
        if transaction_type == "buy":
            return self.kite.TRANSACTION_TYPE_BUY
        elif transaction_type == "sell":
            return self.kite.TRANSACTION_TYPE_SELL
        else:
            raise ValueError("Unknown transaction type {}".format(transaction_type))

