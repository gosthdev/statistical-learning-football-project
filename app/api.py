import webview
import os

class API:
    """
    Contiene todos los métodos que queremos que sean accesibles desde JavaScript.
    """
    def __init__(self):
        self.window = None

    def select_file(self):
        """
        Abre un diálogo nativo para seleccionar un archivo.
        Está configurado para aceptar CSV, pero es fácil de extender.
        """
        if not self.window:
            self.window = webview.windows[0]

        # Definimos los tipos de archivo permitidos.
        # Para añadir más, simplemente expande la tupla.
        # Ej: ('Todos los archivos (*.*)', 'Archivos de Datos (*.csv;*.arff;*.xls)')
        file_types = ('Archivos CSV (*.csv)',)

        result = self.window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=file_types
        )

        # El diálogo devuelve una tupla. Si se selecciona un archivo,
        # devolvemos la ruta. Si se cancela, devolvemos None.
        if result:
            file_path = result[0]
            print(f"Archivo seleccionado con el botón: {file_path}")
            # Devolvemos un diccionario para que JS lo pueda interpretar fácilmente
            return {'status': 'success', 'path': file_path}
        else:
            return {'status': 'cancelled'}

    def process_dropped_file(self, file_path):
        """
        Esta función es llamada por JavaScript cuando un archivo es
        arrastrado y soltado en la ventana.
        """
        # Aquí es donde conectarías tu lógica de procesamiento principal
        print(f"Archivo recibido por drag & drop: {file_path}")
        
        # --- INICIO DE LA LÓGICA DE PROCESAMIENTO ---
        # from core_logic.data_processing import procesar_csv
        # from core_logic.model_management import entrenar_modelo
        # try:
        #     df = procesar_csv(file_path)
        #     entrenar_modelo(df)
        #     # Devuelve un mensaje de éxito a la interfaz
        #     return {'status': 'success', 'message': f'Modelo entrenado con {os.path.basename(file_path)}'}
        # except Exception as e:
        #     # Devuelve un mensaje de error a la interfaz
        #     return {'status': 'error', 'message': str(e)}
        # --- FIN DE LA LÓGICA DE PROCESAMIENTO ---
        
        # Por ahora, solo devolvemos éxito para el ejemplo.
        return {
            'status': 'success',
            'message': f"Archivo '{os.path.basename(file_path)}' listo para ser procesado."
        }