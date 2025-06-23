import os
import webview
from app.api import Api
from core.data_manager import DataManager # Importa DataManager
from core.models.multiple_linear_regression import MultipleLinearRegressionModel
import pandas as pd
# ¡NUEVO! Importa el data_holder para ejecutar la precarga de datos
import core.data_holder

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


    # df = pd.read_csv('/home/eddu/upao/statistical-learning-football-project/data/processed/2025-06-22_15-29-16.csv')
    # model = MultipleLinearRegressionModel(df)
    # # model.train()
    # # model.save()
    # model.load_models()
    # model.load_test_data()
    # print(model.predict("Eibar", "Betis", "13/05/2021"))

    # # --- INICIALIZACIÓN DE LA APLICACIÓN ---
    # exit()