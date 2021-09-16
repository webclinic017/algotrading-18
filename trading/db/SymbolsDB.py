import sqlite3
import sys
import traceback


class SymbolsDB:
    def __init__(self, symbols, db_path, instruments_db):
        self.symbols = symbols
        self.instruments_db = instruments_db
        self.db = sqlite3.connect(db_path)

        for symbol in symbols:
            c = self.db.cursor()
            table_name = symbol  # + "-" + str(self.suffix)
            c.execute(
                "CREATE TABLE IF NOT EXISTS {} (ts datetime primary key, price real(15,5), volume integer)".format(
                    table_name))
            try:
                self.db.commit()
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                sys.exit(1)

        self.db.close()


