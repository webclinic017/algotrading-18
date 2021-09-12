import os
import glob
import pandas as pd


class StoreHelper:
    def __init__(self, store_path):
        self.store_path = store_path
        self.temp_dir = 'temp/'
        self.results_dir = 'results/'

    def remove_temp_files(self):
        # Clean the store by removing any temp files
        files = glob.glob(self.store_path + self.temp_dir + '*')
        for f in files:
            os.remove(f)

    # Returns a pandas data frame
    def read_csv_as_df(self, file_name):
        return pd.read_csv(self.store_path + 'csv/' + file_name)

    def store_historical_ohlc_df_as_csv(self, df, file_name):
        file_name = self.store_path + self.temp_dir + file_name
        df.to_csv(file_name)
        return file_name

    def write_results_to_store(self, df, file_name):
        file_name = self.store_path + self.results_dir + file_name
        df.to_csv(file_name)
        return file_name

