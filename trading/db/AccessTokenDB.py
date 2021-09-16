import datetime
import sqlite3
import sys
import traceback

import pandas as pd


class AccessTokenDB:
    def __init__(self, db_path):
        self.db = sqlite3.connect(db_path)
        self.table_name = "AccessToken"

        c = self.db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS {} (ts date primary key, token varchar)".format(self.table_name))

        try:
            self.db.commit()
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            sys.exit(1)

    def get_access_token(self):
        return pd.read_sql_query("SELECT * FROM {} where ts = date('now')".format(self.table_name), self.db)

    def put_access_token(self, token):
        c = self.db.cursor()
        vals = [datetime.date.today(), token]
        query = "INSERT OR REPLACE INTO {} (ts,token) VALUES (?,?)".format(self.table_name)
        c.execute(query, vals)

        try:
            self.db.commit()
        except:
            print("Exception while committing token: " + traceback.format_exc())
            self.db.rollback()
