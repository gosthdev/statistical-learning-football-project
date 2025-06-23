import os
import shutil
import json
from core.data_manager import DataManager, DataType
from core.model_trainer import model_instance
# ¡NUEVO! Importamos los datos ya cargados en memoria
from core.data_holder import PROCESSED_DATA_JSON, TEST_DATA_JSON

class Api:
    def __init__(self):
        self.window = None
        self.default_data_path = os.path.join('data', 'default_datasets')
        self.raw_data_output_path = os.path.join('data', 'raw')


    def set_window(self, window):
        self.window = window

    def load_default_datasets(self):
        try:
            if not os.path.isdir(self.default_data_path):
                print(f"Error: Default dataset directory not found at '{self.default_data_path}'.")
                return []
            files = [f for f in os.listdir(self.default_data_path) if f.endswith('.csv')]
            return files
        except Exception as e:
            print(f"Error listing default datasets: {e}")
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
            # Filtrar solo los archivos subidos para escribirlos en disco
            files_to_write = [f for f in files_to_process if f.get('type') == 'uploaded' and f.get('content') is not None]

            if not files_to_write:
                return {"status": "error", "message": "Uploaded files were found, but they have no content to save."}

            # Asegurarse de que el directorio 'raw' exista
            try:
                os.makedirs(self.raw_data_output_path, exist_ok=True)
            except OSError as e:
                return {"status": "error", "message": f"Could not create destination directory: {e}"}

            # Escribir los archivos en 'data/raw'
            for detail in files_to_write:
                dest_path = os.path.join(self.raw_data_output_path, detail['name'])
                try:
                    with open(dest_path, 'w', encoding='utf-8') as f:
                        f.write(detail['content'])
                    print(f"Content for '{detail['name']}' written to: '{dest_path}'")
                except Exception as e:
                    print(f"Error writing content for '{detail['name']}': {e}")
                    return {"status": "error", "message": f"Failed to write file {detail['name']}: {e}"}
            
            # Si todo salió bien, establecer el tipo para el DataManager
            data_manager_type = DataType.RAW

        elif has_default_files:
            print("Processing mode: DEFAULT (no uploaded files, default files selected).")
            # No se necesita escribir archivos, solo establecer el tipo
            data_manager_type = DataType.DEFAULT
        
        # --- 3. Ejecutar el DataManager si se determinó un modo ---
        if data_manager_type:
            try:
                print(f"Initializing DataManager with type: {data_manager_type.name}")
                data_manager = DataManager(data_type=data_manager_type)
                data_manager.process_data()
                saved_path = data_manager.save_data()
                
                if self.window:
                    print(f"Data processed. Navigating to layout.html...")
                    self.window.load_url('layout.html')

                return {
                    "status": "success", 
                    "message": f"Data processed from '{data_manager_type.name}' source. Processed file saved to: {saved_path}"
                }
            except Exception as e:
                print(f"An error occurred during data processing: {e}")
                return {"status": "error", "message": f"Data processing failed: {e}"}
        else:
            return {"status": "info", "message": "No files were selected for processing."}
        
    def get_data(self):
        """
        SUPER RÁPIDO: Ya no lee del disco. Solo devuelve el JSON precargado.
        """
        try:
            print("API: get_data() called. Pushing pre-loaded data to dashboard.")
            if self.window:
                # Usa directamente la variable importada
                self.window.evaluate_js(f'renderDashboardData({PROCESSED_DATA_JSON})')
        except Exception as e:
            print(f"API Error in get_data: {e}")
            if self.window:
                error_message = json.dumps(f"Error fetching data: {e}")
                self.window.evaluate_js(f'renderDashboardError({error_message})')
    
    def get_test_data(self):
        """
        SUPER RÁPIDO: Ya no lee del disco. Solo devuelve el JSON precargado.
        """
        try:
            print("API: get_test_data() called. Pushing pre-loaded test data to predictions view.")
            if self.window:
                # Usa directamente la variable importada
                self.window.evaluate_js(f'renderPredictionsTable({TEST_DATA_JSON})')
        except Exception as e:
            print(f"API Error in get_test_data: {e}")
            if self.window:
                error_message = json.dumps(f"Error fetching test data: {e}")
                self.window.evaluate_js(f'renderPredictionsError({error_message})')

    def get_prediction(self, home_team: str, away_team: str, date: str):
        """
        Endpoint de la API para obtener una predicción para un partido específico.
        """
        # ¡CAMBIADO! Usamos la instancia global importada desde model_trainer.
        if not model_instance:
            return {"error": "Prediction model is not available."}

        try:
            # ¡CAMBIADO! Usamos la instancia global importada.
            pred_h, pred_a, real_h, real_a = model_instance.predict(home_team, away_team, date)

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