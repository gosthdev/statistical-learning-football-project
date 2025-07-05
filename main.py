import os
import platform
import argparse
import threading
import time

# Platform environment variables
if platform.system() == 'Windows':
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"
else:
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer --disable-dev-shm-usage"

import webview
import pandas as pd
import gc  # Garbage collection
from app.api import Api
from core.data_manager import DataManager
import core.data_holder


def cleanup():
    print("Cleaning up resources...")
    core.data_holder.PROCESSED_DATA_JSON = '{"error": "No processed data found."}'
    core.data_holder.TEST_DATA_JSON = '{"error": "No test data found."}'
    gc.collect()


def start_gui():
    """Función para iniciar la GUI (comportamiento original)"""
    api = Api()
    gui_dir = os.path.join('app', 'gui', 'templates')

    data_manager = DataManager()
    if data_manager.check_file_exists():
        initial_html_file = os.path.join(gui_dir, 'layout.html')
        window_title = 'Goal Predictor'
    else:
        initial_html_file = os.path.join(gui_dir, 'upload.html')
        window_title = 'Upload Initial Data'

    window = webview.create_window(
        window_title,
        initial_html_file,
        js_api=api,
        min_size=(900, 700)
    )

    # Register window close handler
    window.events.closed += lambda: (cleanup())

    webview.start(debug=False)


def start_api_mode(port: int = 8000):
    """Función para iniciar solo la API FastAPI"""
    from api.main import start_api_server

    print("Starting in API mode...")

    # Inicializar los mismos datos que usa la GUI
    print("MODEL_TRAINER: Initializing and loading the global prediction model...")
    import core.model_trainer

    print("MODEL_TRAINER: Global model instance created and loaded successfully.")

    print("DATA_HOLDER: Initializing and pre-loading data into memory...")
    import core.data_holder

    print("DATA_HOLDER: Data pre-loaded successfully.")

    # Verificar estado
    if core.model_trainer.model_instance:
        print("Model loaded successfully for API")
    else:
        print("Warning: No model loaded. API started without prediction capability.")

    # Iniciar el servidor API
    start_api_server(host="127.0.0.1", port=port, reload=False)


def start_hybrid_mode(port: int = 8000):
    """Función para iniciar GUI y API simultáneamente"""
    print(f"Starting in hybrid mode... API on port {port}")

    # Iniciar API en un hilo separado
    api_thread = threading.Thread(
        target=start_api_mode,
        args=(port,),
        daemon=True
    )
    api_thread.start()

    # Esperar un poco para que la API se inicie
    time.sleep(2)
    print(f"API started on http://127.0.0.1:{port}")

    # Iniciar GUI en el hilo principal
    start_gui()


def main():
    parser = argparse.ArgumentParser(description='Statistical Learning Football Project')
    parser.add_argument('--api', action='store_true',
                        help='Start only FastAPI server')
    parser.add_argument('--port', type=int, default=8000,
                        help='Port for FastAPI server (default: 8000)')
    parser.add_argument('--hybrid', action='store_true',
                        help='Start both GUI and API')

    args = parser.parse_args()

    if args.api:
        start_api_mode(args.port)
    elif args.hybrid:
        start_hybrid_mode(args.port)
    else:
        # Modo GUI por defecto (comportamiento original intacto)
        start_gui()


if __name__ == '__main__':
    main()