import webview
import os
from app.api import Api

gui_dir = os.path.join('app', 'gui', 'templates')

if __name__ == '__main__':
    api = Api()

    window = webview.create_window(
        'Upload Files',
        os.path.join(gui_dir, 'layout.html'),
        js_api=api,
        min_size=(800, 650)
    )
    
    webview.start(debug=False)