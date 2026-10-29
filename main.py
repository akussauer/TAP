# Package imports
import sys
import os
from platformdirs import user_data_dir
from pathlib import Path
import json

from PySide6.QtWidgets import QApplication

# Import 1st page
from Pages.Helpers.Main_Window import MainWindow
from Functions.Appearance import apply_appearance

def load_config():
    # Get the app data path
    app_data_path = Path(user_data_dir("TAP", "MPS")) # app name + org (Maple Studios)
    app_data_path.mkdir(parents=True, exist_ok=True)

    # Get the config
    config_path = os.path.join(app_data_path, "config.json")
    if not os.path.exists(config_path):
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except (json.JSONDecodeError, OSError):
        return None

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # System theme and style (defaults to system theme / system style without a config)
    apply_appearance(app, load_config() or {})

    # Set application metadata
    app.setApplicationName("TAP")
    app.setOrganizationName("Maple Studios")
    app.setApplicationVersion("1.00")

    # Load the main window
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
# Use "uv run main.py" in the terminal to launch the application for the development environment
