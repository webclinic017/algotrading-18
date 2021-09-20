class AutoSquareOff:
    def __init__(self, orders):
        self.orders = orders

    def close_open_positions(self):
        long_positions, short_positions = self.orders.open_positions()
        long_positions.apply(lambda r: self.orders.place_mis_market_order(r['tradingsymbol'], "sell", r['quantity']))
        short_positions.apply(lambda r: self.orders.place_mis_market_order(r['tradingsymbol'], "buy", r['quantity']))

    def cancel_open_orders(self):
        open_orders = self.orders.open_orders()
        for order_id in open_orders:
            self.orders.cancel_order(order_id)

    def square_off(self):
        self.close_open_positions()
        self.cancel_open_orders()
