import os
import sys
import threading
import time
import socket
import webbrowser


def wait_for_port(host, port, timeout=10.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def main():
    app_path = os.path.join(os.path.dirname(__file__), "wealth_tracker.py")
    if not os.path.exists(app_path):
        raise FileNotFoundError(f"App not found at {app_path}")
    port = int(os.environ.get("WEALTHPULSE_PORT", "8501"))
    args = [
        "streamlit",
        "run",
        app_path,
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ]
    sys.argv = args

    if os.environ.get("WEALTHPULSE_NO_BROWSER", "").strip() != "1":
        def _open():
            wait_for_port("localhost", port, timeout=12.0)
            webbrowser.open_new_tab(f"http://localhost:{port}")
        threading.Thread(target=_open, daemon=True).start()

    from streamlit.web import cli as stcli
    stcli.main()


if __name__ == "__main__":
    main()
