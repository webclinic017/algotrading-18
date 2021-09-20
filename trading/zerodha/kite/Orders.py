import pandas as pd
import logging
from trading.zerodha.kite.Retry import retry


class Orders:
    def __init__(self, kite, exchange):
        logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s', level=logging.INFO)
        self.kite = kite
        self.exchange = exchange

    def buy_intraday_with_stop_loss(self, symbol, quantity, sl_price, trade_value):
        self.place_mis_market_order(symbol, "buy", quantity, trade_value)
        self.place_mis_sl_order(symbol, "sell", quantity, sl_price)

    def sell_intraday_with_stop_loss(self, symbol, quantity, sl_price, trade_value):
        self.place_mis_market_order(symbol, "sell", quantity, trade_value)
        self.place_mis_sl_order(symbol, "buy", quantity, sl_price)

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
    def place_mis_market_order(self, symbol, transaction_type, quantity, trade_value):
        purchase_str = "{} {} quantities of {} scrip. Total trade value {}. Current price {}" \
            .format(transaction_type, quantity, symbol, trade_value, trade_value / quantity)

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
            t_type = self.kite.TRANSACTION_TYPE_BUY
        elif transaction_type == "sell":
            t_type = self.kite.TRANSACTION_TYPE_SELL

        return t_type
