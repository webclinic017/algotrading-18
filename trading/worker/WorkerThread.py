import threading

from trading.db.TicksDB import TicksDB


class WorkerThread(threading.Thread):
    def __init__(self, ticks_db_path, instruments_db, symbol, strategy):
        super().__init__()
        self.ticks_db_path = ticks_db_path
        self.instruments_db = instruments_db

        self.symbol = symbol
        self.strategy = strategy

        self.candle_interval = strategy.candle_interval
        self.candle_length = strategy.candle_length
        self.period = strategy.period

    def resample_data(self, df):
        ticks = df.loc[:, ['price']]
        resampled_df = ticks['price'].resample(str(self.candle_interval) + self.period).ohlc().dropna()
        return resampled_df

    def get_ticks(self):
        return self.ticks_db.get_ticks(self.symbol, self.candle_length * 70) # We get on an avg 60-70 ticks per second

    def get_data(self):
        ticks = self.get_ticks()
        return self.resample_data(ticks)

    def run(self):
        self.ticks_db = TicksDB(self.ticks_db_path, self.instruments_db)
        data = self.get_data()
        df = self.strategy.act(data)
        print("Done")
        self.ticks_db.close()
