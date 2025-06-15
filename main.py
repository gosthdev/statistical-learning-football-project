import webview
import os
from app.api import Api

gui_dir = os.path.join('app', 'gui', 'templates')

if __name__ == '__main__':
    api = Api()

    # Crea la ventana usando una ruta relativa.
    # pywebview iniciará automáticamente su servidor interno.
    window = webview.create_window(
        'Cargar Datos Históricos',
        os.path.join(gui_dir, 'upload.html'), # <- La ruta relativa
        js_api=api,
        min_size=(800, 650)
    )
    
    # No se necesitan argumentos especiales para el servidor
    webview.start(debug=True)