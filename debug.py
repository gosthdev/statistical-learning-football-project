import os
import platform
import shutil

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
    # remove models, processed data, raw data, and test data folders
    model_dir = os.path.join('data', 'models')
    processed_data_dir = os.path.join('data', 'processed')
    raw_data_dir = os.path.join('data', 'raw')  
    test_data_dir = os.path.join('data', 'test')

    for directory in [model_dir, processed_data_dir, raw_data_dir, test_data_dir]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Removed directory: {directory}")

    gc.collect()

if __name__ == '__main__':

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

    webview.start(debug=True)