from enum import Enum
from glob import glob
import os
import pandas as pd

from config import ESSENTIAL_COLUMNS

class DataType(Enum):
    RAW = 'raw'
    DEFAULT = 'default'

class PreProcessor:
    def __init__(self, data_type=DataType.RAW):
        self.default_datasets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'default_datasets')
        self.raw_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')
        self.processed_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
        
        if data_type == DataType.RAW:
            self.working_path = self.raw_data_path
        elif data_type == DataType.DEFAULT:
            self.working_path = self.default_datasets_path
        else:
            raise ValueError("data_type must be a DataType enum")
            
        self.data = None

    def normalize(self):
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
            self.normalize()
        return self.data
