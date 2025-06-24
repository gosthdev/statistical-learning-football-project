import os
import shutil
import json
from core.data_manager import DataManager, DataType
from core.models.multiple_linear_regression import MultipleLinearRegressionModel
import core.model_trainer
import core.data_holder

class Api:
    def __init__(self):
        self.window = None
        self.default_data_path = os.path.join('data', 'default_datasets')
        self.raw_data_output_path = os.path.join('data', 'raw')
        self._processed_data_cache = None

    def set_window(self, window):
        self.window = window

    def load_default_datasets(self):
        try:
            if not os.path.isdir(self.default_data_path):
                return []
            files = [f for f in os.listdir(self.default_data_path) if f.endswith('.csv')]
            return files
        except Exception as e:
            return []

    def process_files(self, files_to_process):
        print("Received for processing:", 
              [{'name': f.get('name'), 'type': f.get('type')} for f in files_to_process])

        # --- 1. Determinar el modo de operación ---
        has_uploaded_files = any(f.get('type') == 'uploaded' for f in files_to_process)
        has_default_files = any(f.get('type') == 'default' for f in files_to_process)
        
        data_manager_type = None

        # --- 2. Preparar los datos si es necesario ---
        if has_uploaded_files:
            print("Processing mode: RAW (uploaded files found).")
            files_to_write = [f for f in files_to_process if f.get('type') == 'uploaded' and f.get('content') is not None]
            if not files_to_write:
                return {"status": "error", "message": "Uploaded files were found, but they have no content to save."}
            try:
                os.makedirs(self.raw_data_output_path, exist_ok=True)
            except OSError as e:
                return {"status": "error", "message": f"Could not create destination directory: {e}"}
            for detail in files_to_write:
                dest_path = os.path.join(self.raw_data_output_path, detail['name'])
                try:
                    with open(dest_path, 'w', encoding='utf-8') as f:
                        f.write(detail['content'])
                    print(f"Content for '{detail['name']}' written to: '{dest_path}'")
                except Exception as e:
                    print(f"Error writing content for '{detail['name']}': {e}")
                    return {"status": "error", "message": f"Failed to write file {detail['name']}: {e}"}
            data_manager_type = DataType.RAW
        elif has_default_files:
            print("Processing mode: DEFAULT (no uploaded files, default files selected).")
            data_manager_type = DataType.DEFAULT
        
        # --- 3. Ejecutar el DataManager si se determinó un modo ---
        if data_manager_type:
            try:
                data_manager = DataManager(data_type=data_manager_type)
                data_manager.process_data()
                data_manager.save_data()

                # --- TRAIN AND SAVE THE MODEL ---
                model = MultipleLinearRegressionModel()
                model.train(data_manager.data) 
                model.save()

                # --- UPDATE ALL IN-MEMORY DATA ---
                data_loader = DataManager()
                core.data_holder.PROCESSED_DATA_JSON = data_loader.get_data_as_json()
                core.data_holder.TEST_DATA_JSON = data_loader.get_data_as_json(DataType.TEST)
                
                # --- KEY CHANGE ---
                # Replace the global model instance with our newly trained one.
                core.model_trainer.model_instance = model
                
                self._processed_data_cache = None 
                
                if self.window:
                    self.window.load_url('layout.html')
                return

            except Exception as e:
                print(f"An error occurred during data processing: {e}")
                return {"status": "error", "message": f"Data processing failed: {e}"}
        else:
            return {"status": "info", "message": "No files were selected for processing."}
        
    def get_data(self):
        try:
            print("API: get_data() called. Pushing pre-loaded data to dashboard.")
            if self.window:
                # KEY CHANGE: Always read the variable from the module's namespace.
                data_json = core.data_holder.PROCESSED_DATA_JSON
                
                if self._processed_data_cache is None:
                    self._processed_data_cache = json.loads(data_json)
                
                data = self._processed_data_cache
                
                if isinstance(data, list):
                    batch_size = 100
                    initial_batch = data[:batch_size]
                    initial_batch_json = json.dumps(initial_batch)
                    total_count = len(data)
                    print(f"Sending first {len(initial_batch)} rows of {total_count} total records")
                    self.window.evaluate_js(f'renderDashboardData({initial_batch_json}, {total_count})')
                else:
                    self.window.evaluate_js(f'renderDashboardData({data_json})')
        except Exception as e:
            print(f"API Error in get_data: {e}")
            if self.window:
                error_message = json.dumps(f"Error fetching data: {e}")
                self.window.evaluate_js(f'renderDashboardError({error_message})')

    def get_more_data(self, start_index, batch_size):
        try:
            print(f"API: get_more_data() called. Requesting rows {start_index} to {start_index + batch_size}")
            
            if self._processed_data_cache is None:
                # KEY CHANGE: Read from the module's namespace.
                self._processed_data_cache = json.loads(core.data_holder.PROCESSED_DATA_JSON)
                
            data = self._processed_data_cache
            
            if not isinstance(data, list):
                return []
                
            end_index = min(start_index + batch_size, len(data))
            next_batch = data[start_index:end_index]
            
            print(f"Returning {len(next_batch)} additional rows")
            return next_batch
            
        except Exception as e:
            print(f"API Error in get_more_data: {e}")
            return []
    
    def get_test_data(self):
        try:
            print("API: get_test_data() called. Pushing pre-loaded test data to predictions view.")
            if self.window:
                self.window.evaluate_js(f'renderPredictionsTable({core.data_holder.TEST_DATA_JSON})')
        except Exception as e:
            print(f"API Error in get_test_data: {e}")
            if self.window:
                error_message = json.dumps(f"Error fetching test data: {e}")
                self.window.evaluate_js(f'renderPredictionsError({error_message})')

    def get_prediction(self, home_team: str, away_team: str, date: str):
        # --- KEY CHANGE ---
        # Use the global instance from the module.
        if not core.model_trainer.model_instance:
            return {"error": "Prediction model is not available."}
        try:
            # Use the global instance from the module.
            pred_h, pred_a, real_h, real_a = core.model_trainer.model_instance.predict(home_team, away_team, date)
            if pred_h is None:
                return {"error": f"Match not found for {home_team} vs {away_team} on {date} in the test dataset."}
            result = {
                "predicted_home_goals": float(pred_h),
                "predicted_away_goals": float(pred_a),
                "actual_home_goals": int(real_h),
                "actual_away_goals": int(real_a)
            }
            return result
        except Exception as e:
            print(f"API Error in get_prediction: {e}")
            return {"error": "An unexpected error occurred during prediction."}

    def check_processed_data(self):
        return DataManager().check_file_exists()