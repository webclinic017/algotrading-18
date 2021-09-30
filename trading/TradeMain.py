import logging
import sys
import time
from datetime import datetime
import pandas as pd

from kiteconnect import KiteTicker

from trading.db.AccessTokenDB import AccessTokenDB
from trading.db.InstrumentsDB import InstrumentsDB
from trading.db.SymbolsDB import SymbolsDB
from trading.db.TicksDB import TicksDB
from trading.strategies.TestStrategy import TestStrategy
from trading.workers.IndicatorRefreshThread import IndicatorRefreshThread
from trading.zerodha.auth.Authorizer import Authorizer
from trading.zerodha.kite.Orders import Orders
from trading.zerodha.kite.Period import Period
from trading.zerodha.kite.Ticks import Ticks


def listen_to_market(kite, on_ticks, on_connect):
    logging.info("Connecting to market")
    kite_ticker = KiteTicker(kite.api_key, kite.access_token)

    kite_ticker.on_ticks = on_ticks
    kite_ticker.on_connect = on_connect
    kite_ticker.connect(threaded=True)
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

        # We want to start at the strike of every minute
        init_time = datetime.now()
        logging.info("Sleeping {} seconds to synchronize with minutes".format(60 - init_time.second))
        time.sleep(60 - init_time.second)

        ticks = Ticks(symbols, ticks_db_path, instruments_db)
        on_ticks = ticks.on_ticks
        on_connect = ticks.on_connect
        # listen_to_market(kite, on_ticks, on_connect)

        period = Period.MIN  # Minutes
        candle_interval = 1  # 1 Minute or 5 Minute candle
        candle_length = 3  # How many number of candles required
        multiplier = 3

        logging.info("Available cash {}".format(kite.margins("equity")['net']))
        threads = []

        # self.get_ohlc_for_time(instruments_db, ticks_db_path)

        for symbol in symbols:
            strategy = TestStrategy(symbol=symbol,
                                    period=period,
                                    candle_length=candle_length,
                                    candle_interval=candle_interval,
                                    margin=margin,
                                    order_pct=order_pct,
                                    orders=orders,
                                    db_path=ticks_db_path,
                                    instruments_db=instruments_db,
                                    multiplier=multiplier)

            for ind in strategy.get_indicators():
                t = IndicatorRefreshThread(kite, indicator=ind)
                threads.append(t)

        # Start all threads
        for t in threads:
            t.start()

        # Wait for all of them to finish
        for t in threads:
            t.join()

    def get_ohlc_for_time(self, instruments_db, ticks_db_path):
        _db = TicksDB(ticks_db_path, instruments_db)
        _df = _db.get_ticks('APOLLOHOSP', '2021-09-28 12:35:00', '2021-09-28 12:39:00')
        _ticks = _df.loc[:, ['price']]
        resampled_df = _ticks['price'].resample('1Min').ohlc()
        resampled_df.index = pd.to_datetime(resampled_df.index)
        resampled_df = resampled_df.sort_index(ascending=True)
        print(resampled_df)
        sys.exit(0)
