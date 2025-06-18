import os
from enum import Enum
from .pre_processor import PreProcessor
from .features import (
    AvgGoalsCalculator,
    StreaksCalculator,
    AvgShotsCalculator,
    AvgCornersCalculator,
    AvgPointsCalculator,
    EfficiencyCalculator
)
from datetime import datetime
from .config import N
class DataType(Enum):
    RAW = 'raw'
    DEFAULT = 'default'
class DataManager: 

    def __init__(self, data_type=DataType.RAW):
        date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.save_data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed', (date + '.csv'))

        if data_type == DataType.RAW:
            self.working_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')
        elif data_type == DataType.DEFAULT:
            self.working_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'default_datasets')
        else:
            raise ValueError("data_type must be a DataType enum")


    def process_data(self):
        try:
            self.data = PreProcessor(self.working_path).get_data()
            self.data = AvgGoalsCalculator().calculate(self.data, N)
            self.data = StreaksCalculator().calculate(self.data, N)
            self.data = AvgShotsCalculator().calculate(self.data, N)
            self.data = AvgCornersCalculator().calculate(self.data, N)
            self.data = AvgPointsCalculator().calculate(self.data, N)
            self.data = EfficiencyCalculator().calculate(self.data, N)
        except Exception as e:
            print(f"Error processing data: {e}")

    def save_data(self):
        if self.data is not None:
            self.data.to_csv(self.save_data_path, index=False)
        else:
            raise ValueError("No data to save. Please load or process data first.")
        
    def print_data(self):
        if self.data is not None:
            print(self.data.head())
        else:
            raise ValueError("No data to print. Please load or process data first.")


if __name__ == "__main__":
    # Example usage
    data_manager = DataManager(data_type=DataType.RAW)
    data_manager.process_data()
    data_manager.print_data()
    data_manager.save_data()