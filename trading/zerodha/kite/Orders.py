class Orders:
    def __init__(self, kite, exchange):
        self.kite = kite
        self.exchange = exchange

    def place_mis_market_order(self, symbol, transaction_type, quantity):
        transaction_type = self.get_transaction_type(transaction_type)

        self.kite.place_order(tradingsymbol=symbol,
                              exchange=self.exchange,
                              transation_type=transaction_type,
                              quantity=quantity,
                              order_type=self.kite.ORDER_TYPE_MARKET,
                              product=self.kite.PRODUCT_MIS,
                              variety=self.kite.VARIETY_REGULAR)

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

    def get_transaction_type(self, transaction_type):
        if transaction_type == "buy":
            t_type = self.kite.TRANSACTION_TYPE_BUY
        elif transaction_type == "sell":
            t_type = self.kite.TRANSACTION_TYPE_SELL

        return t_type
