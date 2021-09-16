import json
from abc import ABC, abstractmethod
from datetime import timedelta

import backtrader as bt
import pandas as pd

from backtesting.data.historical.DataFetcherFactory import DataFetcherFactory
from backtesting.data.symbols.SymbolsDataFetcherFactory import SymbolsDataFetcherFactory
from backtesting.helpers.StoreHelper import StoreHelper


class Test(ABC):
    def __init__(self, name, strategies):
        self.name = name
        self.strategies = strategies

        f = open('backtesting/config/tests_config.json')
        self.config = json.load(f)
        f.close()

        self.store_helper = StoreHelper('backtesting/store/')

        self.to_date = self.get_to_date()
        self.from_date = (self.to_date - timedelta(days=self.get_max_candles()))
        self.start_cash = self.get_start_cash()

        symbols_data_fetcher = SymbolsDataFetcherFactory(self.store_helper).get_object(self.get_exchange())
        self.symbols = symbols_data_fetcher.get_n_symbols_with_listing_newer_than_date(
            self.get_total_symbols_to_test(), self.from_date)
        self.historical_data_fetcher = DataFetcherFactory(self.store_helper).get_object(self.get_exchange())
        # self.symbols = ["ARIES"]

    def get_start_cash(self):
        return self.config['cash']

    def get_total_symbols_to_test(self):
        return self.config['total_symbols']

    def get_exchange(self):
        return self.config['exchange']

    def get_order_percent(self):
        return self.config['order_pct']

    def get_name(self):
        return self.name

    @abstractmethod
    def add_strategy(self, cerebro, strategy, symbol):
        pass

    def run(self):
        results = []
        for strategy in self.strategies:
            profitable_trades = 0
            loss_making_trades = 0
            total_cash_made = 0
            total_cash_invested = 0
            neutral_trades = 0
            error_trades = 0
            total_trades = 0
            money_made = 0.0
            money_lost = 0.0

            result = dict()

            for symbol in self.symbols:
                # print(total_trades)
                data = self.historical_data_fetcher.get_data_for_backtrader(symbol, self.to_date, self.from_date)

                try:
                    end_cash = self.do_run(data, self.start_cash, strategy, symbol)
                    total_cash_invested = total_cash_invested + self.start_cash
                    total_cash_made = total_cash_made + end_cash

                    if end_cash > self.start_cash:
                        profitable_trades = profitable_trades + 1
                        money_made = money_made + (end_cash - self.start_cash)
                    elif self.start_cash > end_cash:
                        loss_making_trades = loss_making_trades + 1
                        money_lost = money_lost + (self.start_cash - end_cash)
                    else:
                        neutral_trades = neutral_trades + 1

                    total_trades = total_trades + 1
                except IndexError:
                    print(symbol + " does not have data from NSE")
                    error_trades = error_trades + 1

                # time.sleep(5)

            result['Strategy'] = strategy.__name__
            result['TotalTrades'] = total_trades
            result['ProfitableTrades'] = profitable_trades
            result['LossMakingTrades'] = loss_making_trades
            # results['MoneyMade'] = money_made
            # results['MoneyLost'] = money_lost
            result['TotalCashInvested'] = total_cash_invested
            result['TotalCashInHand'] = total_cash_made
            result['NeutralTrades'] = neutral_trades
            result['NetReturn'] = ((total_cash_made - total_cash_invested) / total_cash_invested) * 100.0

            results.append(result)

        df = pd.DataFrame(results)
        df.set_index('Strategy', inplace=True)

        self.store_helper.write_results_to_store(df, self.__class__.__name__ + '.csv')
        self.store_helper.remove_temp_files()

    def do_run(self, data, cash, strategy, symbol):
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(cash)
        cerebro.adddata(data)
        self.add_strategy(cerebro, strategy, symbol)

        # print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.run()
        # print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
        return cerebro.broker.getvalue()
