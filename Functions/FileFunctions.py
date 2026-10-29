import json
import os
import logging
from logging.handlers import RotatingFileHandler

from PySide6.QtWidgets import QMessageBox

from platformdirs import user_data_dir
from pathlib import Path

_DEFAULT_MARKDOWN_COLOUR = "#0E80A3"

DEFAULT_CONFIG = {
    "theme": "system",
    "style": "default",
    "markdown_colours": {
        "heading":         _DEFAULT_MARKDOWN_COLOUR,
        "bold":            _DEFAULT_MARKDOWN_COLOUR,
        "italic":          _DEFAULT_MARKDOWN_COLOUR,
        "strikethrough":   _DEFAULT_MARKDOWN_COLOUR,
        "list":            _DEFAULT_MARKDOWN_COLOUR,
        "checkbox":        _DEFAULT_MARKDOWN_COLOUR,
        "code":            _DEFAULT_MARKDOWN_COLOUR,
        "blockquote":      _DEFAULT_MARKDOWN_COLOUR,
        "line_break":      _DEFAULT_MARKDOWN_COLOUR,
        "link":            _DEFAULT_MARKDOWN_COLOUR,
        "horizontal_rule": _DEFAULT_MARKDOWN_COLOUR,
    },
    "Language": "en_GB",
    "tab_size": 4,
    "last_folder": "",   # where Save As / Open start; empty = Downloads
    "Hotkeys": {
        "new_subject":   "Ctrl+N",
        "lesson_timer":  "Ctrl+T",
        "subject_timer": "Ctrl+Shift+T",
        "save":          "Ctrl+S",
        "open":          "Ctrl+O",
    }
}

class FunctionsFile:
    def __init__(self, parent=None):
        self.parent = parent

        self.app_data_path = self.create_appdata_repo()
        self.downloads_path = os.path.join(Path.home(), "Downloads")
        self.backup_path = os.path.join(self.app_data_path, "autosave.tap")   # last session, restored on launch

        self.initialize_all_paths()
        self.setup_logging()

        # Log startup
        self.log("Application started.")

    ## Directory setup
    def create_appdata_repo(self):
        app_data_path = Path(user_data_dir("TAP", "MPS"))
        app_data_path.mkdir(parents=True, exist_ok=True)
        return str(app_data_path)

    def initialize_all_paths(self):
        required_structure = ["Logs"]
        try:
            for sub_dir in required_structure:
                path = os.path.join(self.app_data_path, sub_dir)
                if os.path.exists(path):
                    if sub_dir == "Logs":
                        self.log_path = path
                    continue
                else:
                    dir_path = self.create_new_path(sub_dir)
                    os.makedirs(dir_path, exist_ok=True)
                    if sub_dir == "Logs":
                        self.log_path = dir_path

            # Write default config if absent
            config_path = os.path.join(self.app_data_path, "config.json")
            if not os.path.exists(config_path):
                self._write_config(DEFAULT_CONFIG)

        except Exception as e:
            if hasattr(self, 'log'):
                self.log(f"Failed to initialize application paths: {e}", level="error")
            QMessageBox.critical(
                self.parent, "Initialization Error",
                f"An error occurred while initializing application paths: {e}"
            )

    def create_new_path(self, relative_path):
        if not hasattr(self, 'app_data_path'):
            self.app_data_path = self.create_appdata_repo()
        full_path = os.path.join(self.app_data_path, relative_path)
        os.makedirs(full_path, exist_ok=True)
        return full_path
    
    ## Logging Setup
    def setup_logging(self):
        if not hasattr(self, 'log_path'):
            self.initialize_all_paths()
        log_file = os.path.join(self.log_path, "app.log")
        handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

    def log(self, message: str, level: str = "info") -> None:
        logger = logging.getLogger()
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(message)

    ## Config helpers
    @property
    def _config_path(self) -> str:
        return os.path.join(self.app_data_path, "config.json")

    def _write_config(self, data: dict) -> None:
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def get_configs(self) -> dict:
        """
        Return the current config as a plain dict.
        Missing keys are filled in from DEFAULT_CONFIG so the app never
        crashes on an older config file that predates a new setting.
        """
        if not os.path.exists(self._config_path):
            self._write_config(DEFAULT_CONFIG)
            return dict(DEFAULT_CONFIG)

        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            if hasattr(self, 'log'):
                self.log("Failed to read config file; using defaults.", level="error")
            return dict(DEFAULT_CONFIG)

        # Merge defaults for any keys absent in the saved file
        merged = {**DEFAULT_CONFIG, **data}
        # Deep-merge Hotkeys so individual missing hotkeys also fall back
        merged["Hotkeys"] = {**DEFAULT_CONFIG["Hotkeys"], **data.get("Hotkeys", {})}

        # Deep-merge markdown colours; older configs stored a single "markdown_colour"
        legacy = merged.pop("markdown_colour", None)
        base_colours = DEFAULT_CONFIG["markdown_colours"]
        if legacy:
            base_colours = {k: legacy for k in base_colours}
        merged["markdown_colours"] = {**base_colours, **data.get("markdown_colours", {})}
        return merged

    def save_configs(self, settings: dict) -> None:
        """
        Merge incoming settings over the current config and persist.
        Only keys present in settings are updated; everything else is kept.
        """
        current = self.get_configs()

        # Top-level merge
        nested = ("Hotkeys", "markdown_colours")
        current.update({k: v for k, v in settings.items() if k not in nested})

        # Deep-merge nested sections
        for key in nested:
            if key in settings:
                current[key] = {**current.get(key, {}), **settings[key]}

        try:
            self._write_config(current)
        except OSError as e:
            self.log(f"Failed to save config: {e}", level="error")
            QMessageBox.critical(
                self.parent, "Save Failed",
                f"Could not save settings:\n{e}"
            )

    def reset_configs(self, defaults: bool = False) -> dict:
        """
        Return (and optionally write) the default config.
        Pass defaults=True to also persist the reset to disk.
        """
        if defaults:
            try:
                self._write_config(DEFAULT_CONFIG)
            except OSError as e:
                self.log(f"Failed to reset config: {e}", level="error")
                QMessageBox.critical(
                    self.parent, "Reset Failed",
                    f"Could not reset settings:\n{e}"
                )
        return dict(DEFAULT_CONFIG)