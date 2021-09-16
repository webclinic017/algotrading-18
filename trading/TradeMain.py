from kiteconnect import KiteTicker

from trading.db.AccessTokenDB import AccessTokenDB
from trading.db.InstrumentsDB import InstrumentsDB
from trading.db.SymbolsDB import SymbolsDB
from trading.db.TicksDB import TicksDB
from trading.strategies.SuperTrendStrategy import SuperTrendStrategy
from trading.worker.WorkerThread import WorkerThread
from trading.zerodha.auth.Authorizer import Authorizer
from trading.zerodha.kite.Ticks import Ticks


def listen_to_market(kite, on_ticks, on_connect):
    kite_ticker = KiteTicker(kite.api_key, kite.access_token)

    kite_ticker.on_ticks = on_ticks
    kite_ticker.on_connect = on_connect
    kite_ticker.connect()



class TradeMain:
    def __init__(self):
        pass

    def trade(self):
        ticks_db_path = "trading/store/ticks.db"

        authorizer = Authorizer(AccessTokenDB(ticks_db_path))
        kite = authorizer.get_authorized_kite_object()

        symbols = ["TCS", "APOLLOHOSP"]

        instruments_db = InstrumentsDB(kite, "NSE")
        SymbolsDB(symbols, ticks_db_path, instruments_db)

        ticks = Ticks(symbols, ticks_db_path, instruments_db)
        on_ticks = ticks.on_ticks
        on_connect = ticks.on_connect
        # listen_to_market(kite, on_ticks, on_connect)

        period = 'Min'  # Minutes
        candle_interval = 1  # 1 Minute or 5 Minute candle
        candle_length = 10  # How many number of candles required
        multiplier = 3

        for symbol in symbols:
            strategy = SuperTrendStrategy(period, candle_interval, candle_length, multiplier=multiplier)
            t = WorkerThread(ticks_db_path, instruments_db, symbol, strategy)
            t.start()

        '''
        while True:
            now = datetime.now()
            if now.hour >= 9 and now.minute >= 15:
                kite_ticker.on_ticks = ticks.on_ticks
                kite_ticker.on_connect = ticks.on_connect
                kite_ticker.connect()
            if now.hour >= 15 and now.minute >= 30:
                sys.exit()
        '''
