import logging

from trading.errors.DataNotAvailableError import DataNotAvailableError
from trading.workers.WorkerThread import WorkerThread


class StrategyRunner(WorkerThread):
    def __init__(self, kite, **kwargs):
        super().__init__(kite, **kwargs)

        self.strategy = kwargs['strategy']

    def do_run(self, candle_time):
        logging.info(
            "Running strategy {} for symbol {}".format(self.strategy.__class__.__name__, self.strategy.symbol))
        try:
            for ind in self.strategy.get_indicators():
                logging.info(
                    "Running indicator {} for symbol {}".format(ind.__class__.__name__, self.strategy.symbol))
                ind.calculate_lines(candle_time)

            self.strategy.act(candle_time)
        except DataNotAvailableError as e:
            pass



