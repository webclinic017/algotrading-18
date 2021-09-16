import datetime
import sqlite3
import traceback

import pandas as pd


class TicksDB:
    def __init__(self, db_path, instruments_db):
        self.db = sqlite3.connect(db_path)
        self.suffix = datetime.datetime.now().date()
        self.instruments_db = instruments_db

    def insert_ticks(self, ticks):
        c = self.db.cursor()
        for tick in ticks:
            try:
                tok = self.instruments_db.get_symbol_from_instrument_token(tick['instrument_token'])
                vals = [tick['timestamp'], tick['last_price'], tick['last_quantity']]
                query = "INSERT INTO {} (ts,price,volume) VALUES (?,?,?)".format(tok)
                c.execute(query, vals)
            except:
                # print("Exception while inserting ticks: " + traceback.format_exc())
                pass
        try:
            self.db.commit()
        except Exception as e:
            print("Exception while committing ticks: " + traceback.format_exc())
            self.db.rollback()

    def get_ticks(self, symbol, n):
        data = pd.read_sql_query(
            # "SELECT * FROM {} where ts >= datetime('now', 'localtime', '-10 minutes')".format(symbol),
            "SELECT * FROM {} ORDER BY ts DESC LIMIT 1000".format(symbol),
            self.db)
        data = data.set_index(['ts'])
        data.index = pd.to_datetime(data.index)
        return data

    def close(self):
        self.db.close()
