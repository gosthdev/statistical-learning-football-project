import os
from enum import Enum
from pre_processor import PreProcessor
from features.feature_avg_goals import AvgGoalsCalculator
from features.feature_streaks import StreaksCalculator
from config import N
class DataType(Enum):
    RAW = 'raw'
    DEFAULT = 'default'
class DataManager: 

    def __init__(self, data_type=DataType.RAW):
        self.save_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
        self.data = None


        if data_type == DataType.RAW:
            self.working_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')
        elif data_type == DataType.DEFAULT:
            self.working_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'default_datasets')
        else:
            raise ValueError("data_type must be a DataType enum")


    def process_data(self):
        # Obtaining data
        self.data = PreProcessor(self.working_path).get_data()
        AvgGoalsCalculator().calculate(self.data, N)
        StreaksCalculator().calculate(self.data, N)
        pass

    def _save_data(self, path):
        if self.data is not None:
            self.data.to_csv(path, index=False)
        else:
            raise ValueError("No data to save. Please load or process data first.")
        
    def print_data(self):
        if self.data is not None:
            print(self.data.head())
        else:
            raise ValueError("No data to print. Please load or process data first.")


if __name__ == "__main__":
    # Example usage
    data_manager = DataManager(data_type=DataType.DEFAULT)
    data_manager.process_data()
    data_manager.print_data()