from trading.db.TicksDB import TicksDB


class Ticks:
    def __init__(self, symbols, ticks_db_path, instruments_db):
        self.tokens = instruments_db.get_instrument_tokens(symbols)
        self.ticks_db = TicksDB(ticks_db_path, instruments_db)

    def on_ticks(self, ws, ticks):
        self.ticks_db.insert_ticks(ticks)

    def on_connect(self, ws, response):
        ws.subscribe(self.tokens)
