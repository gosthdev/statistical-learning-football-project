import os
import webview
from app.api import Api
from core.data_manager import DataManager # Importa DataManager

if __name__ == '__main__':
    api = Api()
    gui_dir = os.path.join('app', 'gui', 'templates')

    # --- LÓGICA DE ARRANQUE INTELIGENTE ---
    # 1. Comprueba si existen datos procesados antes de crear la ventana
    data_manager = DataManager()
    if data_manager.check_file_exists():
        # Si hay datos, carga el layout principal de la aplicación
        initial_html_file = os.path.join(gui_dir, 'layout.html')
        window_title = 'Goal Predictor'
    else:
        # Si NO hay datos, carga la pantalla de subida de archivos
        initial_html_file = os.path.join(gui_dir, 'upload.html')
        window_title = 'Upload Initial Data'

    # 2. Crea la ventana con el archivo HTML decidido
    window = webview.create_window(
        window_title,
        initial_html_file,
        js_api=api,
        min_size=(900, 700) # Ajustado para el layout de subida
    )
    api.set_window(window)
    webview.start(debug=False)