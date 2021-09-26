import logging

from trading.errors.DataNotAvailableError import DataNotAvailableError
from trading.workers.WorkerThread import WorkerThread


class IndicatorRefreshThread(WorkerThread):
    def __init__(self, kite, **kwargs):
        super().__init__(kite, **kwargs)

        self.indicator = kwargs['indicator']

    def do_run(self, candle_time):
        logging.info(
            "Fetching {} values for symbol {}".format(self.indicator.__class__.__name__, self.indicator.symbol))
        try:
            self.indicator.calculate_lines(candle_time)
        except DataNotAvailableError as e:
            pass



