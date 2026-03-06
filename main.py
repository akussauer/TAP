# Package imports
import sys
import os
import platform
from platformdirs import user_data_dir
from pathlib import Path
import json

from PySide6.QtWidgets import QApplication

# Import 1st page
from Pages.Helpers.Main_Window import MainWindow

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
    config = load_config()

    if config is not None:
        # System Theme
        if platform.system() == "Windows":
            theme = config["theme"].lower()
            if theme == 'dark':
                sys.argv += ['-platform', 'windows:darkmode=2']
            elif theme == 'light':
                sys.argv += ['-platform', 'windows:darkmode=1']
            elif theme == 'system':
                sys.argv += ['-platform', 'windows:darkmode=0']
            else:
                sys.argv += ['-platform', 'windows:darkmode=2'] # Default to dark mode if invalid value

        app = QApplication(sys.argv)

        # System Style
        if config["style"].lower() != "default":
            # Set the style to the user's preference
            app.setStyle(config["style"])
        else:
            # Use system default
            system = system_style = app.style().objectName()
            app.setStyle(system_style)
    else:
        app = QApplication(sys.argv)
        sys.argv += ['-platform', 'windows:darkmode=0'] # Default to system theme
        system = system_style = app.style().objectName() # Default to system style
        app.setStyle(system_style)
    # Set application metadata
    app.setApplicationName("TAP")
    app.setOrganizationName("Maple Studios")
    app.setApplicationVersion("1.00")

    # Load the main window
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
# Use "uv run main.py" in the terminal to launch the application for the development environment