from enum import Enum
from glob import glob
import os
import pandas as pd

from config import ESSENTIAL_COLUMNS



class PreProcessor:
    def __init__(self, working_path):
        self.working_path = working_path
        self.data = None

    def _normalize(self):
        data_files = glob(os.path.join(self.working_path, "*.csv"))

        if not data_files:
            raise FileNotFoundError(f"No data files found in {self.working_path}")
        dataframes = []
        for file in data_files: 
            df = pd.read_csv(file)
            dataframes.append(df)

        full_dataframe = pd.concat(dataframes, ignore_index=True)
        proccessed_dataframe = full_dataframe[ESSENTIAL_COLUMNS].copy()

        proccessed_dataframe['Date'] = pd.to_datetime(proccessed_dataframe['Date'], format='%d/%m/%y')
        proccessed_dataframe = proccessed_dataframe.sort_values(by='Date')
        proccessed_dataframe = proccessed_dataframe.reset_index(drop=True)
        self.data = proccessed_dataframe

    def get_data(self):
        if self.data is None:
            self._normalize()
        return self.data
