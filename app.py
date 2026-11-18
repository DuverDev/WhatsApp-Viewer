import sys
import os
import threading
import time

if getattr(sys, "frozen", False):
    _BASE = os.path.dirname(sys.executable)
    _BUNDLE = sys._MEIPASS
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))
    _BUNDLE = _BASE

os.environ["APP_BASE"] = _BASE
os.environ["APP_BUNDLE"] = _BUNDLE

from server import app


def start_server():
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    try:
        import webview
        time.sleep(0.5)
        webview.create_window(
            "WhatsApp Backup Viewer",
            "http://127.0.0.1:5000",
            width=1200,
            height=800,
            min_size=(800, 500),
        )
        webview.start()
    except ImportError:
        import webbrowser
        time.sleep(1.5)
        webbrowser.open("http://127.0.0.1:5000")
        print("Abre http://127.0.0.1:5000 en tu navegador")
        print("Presiona Ctrl+C para detener")
        try:
            t.join()
        except KeyboardInterrupt:
            pass
