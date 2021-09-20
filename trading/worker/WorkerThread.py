import datetime
import logging
import threading
import time

from trading.db.TicksDB import TicksDB


class WorkerThread(threading.Thread):
    def __init__(self, kite, ticks_db_path, instruments_db, symbol, strategy, margin, order_pct):
        super().__init__()
        logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s', level=logging.INFO)
        self.kite = kite
        self.ticks_db_path = ticks_db_path
        self.instruments_db = instruments_db

        self.symbol = symbol
        self.strategy = strategy
        self.margin = margin
        self.order_pct = order_pct

        self.candle_interval = strategy.candle_interval
        self.candle_length = strategy.candle_length
        self.period = strategy.period

    def resample_data(self, df):
        ticks = df.loc[:, ['price']]
        resampled_df = ticks['price'].resample(str(self.candle_interval) + self.period).ohlc().dropna()
        resampled_df.drop(resampled_df.tail(1).index,
                          inplace=True)  # Drop the last row since we could have half candles
        return resampled_df

    def get_ticks(self):
        return self.ticks_db.get_ticks(self.symbol, self.candle_length * 70)  # We get on an avg 60-70 ticks per second

    def get_data(self):
        ticks = self.get_ticks()
        return self.resample_data(ticks)

    def run(self):
        self.ticks_db = TicksDB(self.ticks_db_path, self.instruments_db)
        start_time = time.time()

        while True:
            now = datetime.datetime.now()
            current_hour = now.hour
            current_minute = now.minute

            data = self.get_data()
            cash_available = self.kite.margins("equity")['net']

            logging.info(
                "Starting run for {} for hour {} for minute {} with strategy {}".format(self.symbol, current_hour,
                                                                                        current_minute,
                                                                                        self.strategy.__class__.__name__))
            self.strategy.act(self.symbol, cash_available, self.margin, self.order_pct, data)
            logging.info(
                "Ending run for {} for hour {} for minute {} with strategy {}".format(self.symbol, current_hour,
                                                                                      current_minute,
                                                                                      self.strategy.__class__.__name__))

            if current_hour == 15 and current_minute > 10:
                logging.info("Market close nearing. Current hour {} Current minute {}. "
                             "Exiting thread".format(current_hour, current_minute))
                break

            time.sleep(60.0 - ((time.time() - start_time) % 60.0))

        print("Done")
        self.ticks_db.close()
