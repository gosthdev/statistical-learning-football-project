import os
import shutil
from core.data_manager import DataManager, DataType

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
                saved_path = data_manager.save_data() # Guardamos la ruta para el mensaje
                
                # --- ¡AQUÍ ESTÁ LA MAGIA! ---
                # Después de procesar y guardar, le decimos a la ventana que navegue.
                if self.window:
                    print(f"Data processed. Navigating to layout.html...")
                    self.window.load_url('layout.html')

                # Devolvemos el mensaje de éxito. La navegación ocurrirá casi al mismo tiempo.
                return {
                    "status": "success", 
                    "message": f"Data processed from '{data_manager_type.name}' source. Processed file saved to: {saved_path}"
                }
            except Exception as e:
                print(f"An error occurred during data processing: {e}")
                return {"status": "error", "message": f"Data processing failed: {e}"}
        else:
            # Este caso se da si la lista está vacía o no contiene tipos válidos
            return {"status": "info", "message": "No files were selected for processing."}
        
    def get_data(self):
        data_loader = DataManager(data_type=DataType.RAW)
        return data_loader.get_data_as_json()
    def check_processed_data(self):
        return DataManager().check_file_exists()