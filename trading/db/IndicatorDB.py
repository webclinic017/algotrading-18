import sqlite3
import sys
import traceback
import pandas as pd

from trading.zerodha.kite.Retry import retry


class IndicatorDB:
    def __init__(self, **kwargs):
        self.db_path = "trading/store/indicators.db"
        self.name = kwargs['name']

        self.columns = []
        create_str = ""

        for k in kwargs['columns']:
            self.columns.append(k)
            create_str = create_str + k + " " + kwargs['columns'][k] + " "

        self.columns = kwargs['columns']
        self.db = sqlite3.connect(self.db_path)

        c = self.db.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS {} (ts datetime primary key, {})".format(self.name, create_str[:-1]))
        try:
            self.db.commit()
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            sys.exit(1)

        self.db.close()

    @retry(tries=5, delay=0.02, backoff=2)
    def get_indicator_value(self, start_time, end_time):
        query = "SELECT * FROM {} where ts >= '{}' and ts < '{}'".format(self.name, start_time, end_time)

        self.db = sqlite3.connect(self.db_path)
        data = pd.read_sql_query(query, self.db)

        if data.empty:
            return data

        data = data.set_index(['ts'])
        data.index = pd.to_datetime(data.index)

        self.db.close()
        return data

    @retry(tries=5, delay=0.02, backoff=2)
    def put_indicator_value(self, candle_time, vals):
        candle_time = str(candle_time)
        self.db = sqlite3.connect(self.db_path)
        c = self.db.cursor()
        try:
            query = "INSERT OR REPLACE INTO {} (ts,{}) VALUES (?,?)".format(self.name, ','.join(self.columns))
            values = [candle_time]
            values.extend(vals)

            print(query)
            print(values)
            c.execute(query, values)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            self.db.close()
            raise ValueError("Unable to insert indicator value")

        try:
            self.db.commit()
        except Exception as e:
            print("Exception while committing indicator value: " + traceback.format_exc())
            self.db.rollback()

        self.db.close()

