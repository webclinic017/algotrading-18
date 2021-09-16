from backtrader.feeds import GenericCSVData
from nsepy import get_history
from backtesting.data.historical.DataFetcher import DataFetcher


class NSEDataFetcher(DataFetcher):
    def __init__(self, store_helper):
        self.store_helper = store_helper

        super().__init__()

    def get_data(self, symbol, to_date, from_date):
        return get_history(symbol=symbol, start=from_date, end=to_date)

    def get_data_for_backtrader(self, symbol, to_date, from_date):
        history = self.get_data(symbol, to_date, from_date)
        data_name = self.store_helper.store_historical_ohlc_df_as_csv(history, symbol)

        return GenericCSVData(
            dataname=data_name,
            dtformat='%Y-%m-%d',
            datetime=0,
            high=5,
            low=6,
            open=4,
            close=8,
            volume=10,
            openinterest=-1,
            # fromdate=date(2017,1,1),
            # todate=date(2017,1,10)
        )

