import os
import glob
import pandas as pd
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

        self.processed_data_path = os.path.join('data', 'processed')
        self.raw_data_path = os.path.join('data', 'raw')
        self.default_data_path = os.path.join('data', 'default_datasets')
        # Asegurarse de que los directorios existan al iniciar
        os.makedirs(self.processed_data_path, exist_ok=True)
        os.makedirs(self.raw_data_path, exist_ok=True)


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
    
    def get_data_as_json(self):
        """ Returns the processed data as a JSON string."""
        self.load_data()
        if self.data is not None:
            return self.data.to_json(orient='records')
        else:
            return '{"error": "No data available. Please load or process data first."}'
        
    def load_data(self):
        """ Loads the most recent processed data file."""
        processed_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
        
        try:
            if not os.path.isdir(processed_folder) or not os.listdir(processed_folder):
                print(f"Processed data directory is empty or not found: {processed_folder}")
                self.data = None
                return

            csv_files = [f for f in os.listdir(processed_folder) if f.endswith('.csv')]
            if not csv_files:
                print(f"No CSV files found in {processed_folder}")
                self.data = None
                return

            latest_file = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(processed_folder, f)))
            latest_file_path = os.path.join(processed_folder, latest_file)
            
            print(f"Loading latest processed file: {latest_file_path}")
            self.data = pd.read_csv(latest_file_path)

        except Exception as e:
            print(f"Error loading latest data file: {e}")
            self.data = None

    def save_data(self):
        if self.data is not None:
            self.data.to_csv(self.save_data_path, index=False)
        else:
            raise ValueError("No data to save. Please load or process data first.")
        
    def check_file_exists(self):
        """
        Checks if any .csv file exists in the processed data directory.
        This is a robust way to check for processed data.
        """
        # Comprueba si el directorio existe
        if not os.path.isdir(self.processed_data_path):
            return False
        
        # Busca cualquier archivo que termine en .csv en el directorio
        csv_files = glob.glob(os.path.join(self.processed_data_path, '*.csv'))
        
        # Si la lista de archivos CSV no está vacía, significa que hay datos.
        if csv_files:
            print(f"DataManager: Found processed files: {csv_files}. Starting main app.")
            return True
        else:
            print("DataManager: No processed files found. Starting upload screen.")
            return False

    def print_data(self):
        if self.data is not None:
            print(self.data.head())
        else:
            raise ValueError("No data to print. Please load or process data first.")


if __name__ == "__main__":
    # Example usage
    data_manager = DataManager(data_type=DataType.RAW)
    print(data_manager.check_file_exists())
    data_manager.load_data()
    data_manager.print_data()