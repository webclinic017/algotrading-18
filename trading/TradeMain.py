import logging

from kiteconnect import KiteTicker

from trading.db.AccessTokenDB import AccessTokenDB
from trading.db.InstrumentsDB import InstrumentsDB
from trading.db.SymbolsDB import SymbolsDB
from trading.strategies.SuperTrendStrategy import SuperTrendStrategy
from trading.worker.WorkerThread import WorkerThread
from trading.zerodha.auth.Authorizer import Authorizer
from trading.zerodha.kite.Orders import Orders
from trading.zerodha.kite.Ticks import Ticks


def listen_to_market(kite, on_ticks, on_connect):
    kite_ticker = KiteTicker(kite.api_key, kite.access_token)

    kite_ticker.on_ticks = on_ticks
    kite_ticker.on_connect = on_connect
    kite_ticker.connect()
    logging.info("Started listening to market")


class TradeMain:
    def __init__(self):
        logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s', level=logging.INFO)
        pass

    def trade(self):
        ticks_db_path = "trading/store/ticks.db"
        exchange = "NSE"
        margin = 0.20
        order_pct = 0.50
        symbols = ["APOLLOHOSP"]

        # All zerodha related objects initialise here
        authorizer = Authorizer(AccessTokenDB(ticks_db_path))
        kite = authorizer.get_authorized_kite_object()
        logging.info("Authorized with kite connect successfully")
        orders = Orders(kite, exchange)

        # All DBs initialise here
        instruments_db = InstrumentsDB(kite, exchange)
        SymbolsDB(symbols, ticks_db_path, instruments_db)

        ticks = Ticks(symbols, ticks_db_path, instruments_db)
        on_ticks = ticks.on_ticks
        on_connect = ticks.on_connect
        listen_to_market(kite, on_ticks, on_connect)

        period = 'Min'  # Minutes
        candle_interval = 1  # 1 Minute or 5 Minute candle
        candle_length = 6  # How many number of candles required
        multiplier = 3

        print(kite.margins("equity")['net'])
        threads = []

        for symbol in symbols:
            strategy = SuperTrendStrategy(period, candle_interval, candle_length, orders, multiplier=multiplier)
            t = WorkerThread(kite, ticks_db_path, instruments_db, symbol, strategy, margin, order_pct)
            threads.append(t)

        # Start all threads
        for t in threads:
            t.start()

        # Wait for all of them to finish
        for t in threads:
            t.join()

