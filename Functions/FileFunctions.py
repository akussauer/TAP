import json
import os
import pandas as pd

from PySide6.QtWidgets import QMessageBox

from platformdirs import user_data_dir
from pathlib import Path

class FunctionsFile:
    def __init__(self, parent=None):
        self.parent = parent

        # 1. Create the application data directory
        self.app_data_path = self.create_appdata_repo()
        self.downloads_path = os.path.join(Path.home(), "Downloads")

        # 2. Initialize paths
        self.initialize_all_paths()

    def create_appdata_repo(self):
        # Create the application data directory if it doesn't exist
        # if hasattr(self, "info_logger"):
        #    self.info_logger.info("Creating application data repository.", exc_info=False)

        app_data_path = Path(user_data_dir("TAP", "MPS"))  # app name + org (Maple Studios)
        app_data_path.mkdir(parents=True, exist_ok=True)
        return str(app_data_path)
    
    def initialize_all_paths(self):
        # All required directories for the application
        required_structure = [
            "Session Data",
            "Logs"
        ]
        try:

            for sub_dir in required_structure:
                # Create each subdirectory in the app data path
                path = os.path.join(self.app_data_path, sub_dir)
                if os.path.exists(path):  
                    if sub_dir == "Session Data":
                        self.session_data_path = path
                    continue
                # Create the subdirectory if it doesn't exist
                else:
                    # if hasattr(self, "info_logger"):
                        # self.info_logger.info("Creating all paths for the application.", exc_info=False)
                    # Create the new path relative to the app data directory
                    dir_path = self.create_new_path(sub_dir)
                    os.makedirs(dir_path, exist_ok=True)
                    if sub_dir == "Session Data":
                        self.session_data_path = dir_path
            
            # Establish JSON config file
            config_path = os.path.join(self.app_data_path, "config.json")
            if not os.path.exists(config_path):
                with open(config_path, "w") as f:
                    json.dump({
                        "theme": "system",
                        "style": "default",
                        "file_location": "default",
                        "Language": "en_GB"
                    }, f)
                    
        except Exception as e:
            # if hasattr(self, "error_logger"):
                # self.error_logger.error(f"Error initializing paths: {e}", exc_info=True)
            QMessageBox.critical(self.parent, "Initialization Error", f"An error occurred while initializing application paths: {e}")
            print(f"Error initializing paths: {e}")

    def create_new_path(self, relative_path):
        # Create a new path relative to the app data directory if it doesn't exist
        if not hasattr(self, 'app_data_path'):
            self.app_data_path = self.create_appdata_repo()
            # if hasattr(self, "info_logger"): # Log the creation of the AppData directory
                # self.info_logger.info(f"AppData directory created: {self.app_data_path}", exc_info=False)

            if not os.path.exists(os.path.join(self.app_data_path, relative_path)):
                full_path = os.path.join(self.app_data_path, relative_path)
                os.makedirs(full_path, exist_ok=True)

                # if hasattr(self, "info_logger"): # Log the creation of the new directory
                    # self.info_logger.info(f"Created new directory: {full_path}", exc_info=False)
        else:
            full_path = os.path.join(self.app_data_path, relative_path)
            if not os.path.exists(full_path):
                os.makedirs(full_path, exist_ok=True)

                # if hasattr(self, "info_logger"): # Log the creation of the new directory
                    # self.info_logger.info(f"Created new directory: {full_path}", exc_info=False)
        return full_path
    
    def get_configs(self):
        config_path = os.path.join(self.app_data_path, "config.json")
        if not os.path.exists(config_path):
            with open(config_path, "w") as f:
                json.dump({
                    "theme": "system",
                    "style": "default",
                    "file_location": "default",
                    "Language": "en_GB"
                }, f)
        return pd.read_json(config_path, orient="records", lines=True).iloc[0]