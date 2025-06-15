import os

class Api:
    def __init__(self):
        self.window = None
        # Define la ruta a tus datasets por defecto
        self.default_data_path = os.path.join('data', 'default_datasets')

    def set_window(self, window):
        self.window = window

    def load_default_datasets(self):
        """
        Lee los nombres de los archivos en la carpeta de datasets por defecto
        y los devuelve a JavaScript.
        """
        try:
            files = [f for f in os.listdir(self.default_data_path) if f.endswith('.csv')]
            return files
        except FileNotFoundError:
            return [] # Devuelve una lista vacía si la carpeta no existe

    def process_files(self, files_to_process):
        """
        Recibe la lista de archivos desde JS y comienza el procesamiento.
        """
        print("Recibido para procesar:", files_to_process)
        
        # files_to_process es una lista de diccionarios, ej:
        # [{'name': 'season-2324.csv', 'path': None, 'type': 'default'},
        #  {'name': 'my_upload.csv', 'path': 'C:\\Users\\user\\Desktop\\my_upload.csv', 'type': 'uploaded'}]
        
        final_file_paths = []
        for file_info in files_to_process:
            if file_info['type'] == 'default':
                # Construye la ruta completa para los archivos por defecto
                path = os.path.join(self.default_data_path, file_info['name'])
                final_file_paths.append(path)
            elif file_info['type'] == 'uploaded' and file_info.get('path'):
                # Usa la ruta absoluta de los archivos subidos
                final_file_paths.append(file_info['path'])

        print("Rutas finales a procesar:", final_file_paths)
        
        # --- AQUÍ VA TU LÓGICA DE PROCESAMIENTO ---
        # Llama a tus funciones de data_processor.py y model_manager.py
        # usando `final_file_paths` como la lista de CSVs a combinar.
        
        return {"status": "success", "message": f"{len(final_file_paths)} archivos procesados con éxito."}