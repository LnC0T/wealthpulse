import os
import sys


def main():
    app_path = os.path.join(os.path.dirname(__file__), "wealth_tracker.py")
    if not os.path.exists(app_path):
        raise FileNotFoundError(f"App not found at {app_path}")
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.headless=true",
        "--server.port=8501"
    ]
    from streamlit.web import cli as stcli
    stcli.main()


if __name__ == "__main__":
    main()
