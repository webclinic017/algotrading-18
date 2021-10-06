import datetime
import logging
import threading
import time
from abc import ABC, abstractmethod


class WorkerThread(threading.Thread, ABC):
    def __init__(self, kite, **kwargs):
        super().__init__()
        logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s', level=logging.INFO)
        self.kite = kite

    def run(self):
        candle_time = datetime.datetime(2021, 9, 28, 12, 30, 0)

        start_time = time.time()

        while True:
            # candle_time = datetime.datetime.now().replace(microsecond=0)
            current_hour = candle_time.hour
            current_minute = candle_time.minute

            # cash_available = self.kite.margins("equity")['net']
            self.do_run(candle_time.replace(second=0))

            if current_hour == 15 and current_minute > 30:
                logging.info("Market close nearing. Current hour {} Current minute {}. "
                             "Exiting thread".format(current_hour, current_minute))
                break

            # self.sleep(start_time)
            candle_time = candle_time + datetime.timedelta(minutes=1)

    @abstractmethod
    def do_run(self, candle_time):
        pass

    def sleep(self, start_time):
        time.sleep(60.0 - ((time.time() - start_time) % 60.0))
