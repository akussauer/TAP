from Pages.UI.ui_Settings_Dialog import Ui_SettingsDialog
from Widgets.HotKeyLineEdit import HotkeyLineEdit
from Widgets.colour_button import ColourButton

from PySide6.QtGui import QFont
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QDialog, QLabel, QSpinBox

# Maps config key → (combo display text → stored value)
_THEME_OPTIONS  = {"Light": "light", "Dark": "dark", "System": "system"}
_STYLE_OPTIONS  = {"Default": "default", "Fusion": "fusion"}

# Reverse maps for populating the UI from stored values
_THEME_DISPLAY  = {v: k for k, v in _THEME_OPTIONS.items()}
_STYLE_DISPLAY  = {v: k for k, v in _STYLE_OPTIONS.items()}

_MARKDOWN_COLOUR = "#0E80A3" # Fallback for colour buttons; matches default style's markdown colour
_TAB_SIZE        = 4

# config["markdown_colours"] key → label shown in the dialog
_MARKDOWN_ELEMENTS = [
    ("heading",         "Headings"),
    ("bold",            "Bold"),
    ("italic",          "Italic"),
    ("strikethrough",   "Strikethrough"),
    ("list",            "List Markers"),
    ("checkbox",        "Checkboxes"),
    ("code",            "Inline Code"),
    ("blockquote",      "Block Quotes"),
    ("line_break",      "Line Breaks"),
    ("link",            "Links"),
    ("horizontal_rule", "Horizontal Rules"),
]

_HOTKEY_FIELDS = [
    ("LE_NewSubject", "new_subject"),
    ("LE_LessTimer",  "lesson_timer"),
    ("LE_Save",       "save")
]

_LANG_OPTIONS = [
    'en_AU', 'en_AG', 'en_BS', 'en_BW', 'en_BZ', 'en_CA',
    'en_DK', 'en_GB', 'en_GH', 'en_HK', 'en_IE', 'en_IN',
    'en_JM', 'en_NA', 'en_NG', 'en_NZ', 'en_PH', 'en_SG',
    'en_TT', 'en_US', 'en_ZA', 'en_ZW',
]

class SettingsDialog(QDialog):
    def __init__(self, parent=None, file_func=None):
        super().__init__(parent)
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

        self.file_func = file_func

        self._replace_hotkey_edits()
        self._build_colour_buttons()
        self._build_tab_size_spin()
        self._populate_combos()
        self._load_current_settings()
        self._connect_signals()

    ## Setup
    def _replace_hotkey_edits(self) -> None:
        """Swap plain QLineEdits for HotkeyLineEdit instances."""
        replacements = [
            ("LE_NewSubject", self.ui.gridLayout_7),
            ("LE_LessTimer",  self.ui.gridLayout_8),
            ("LE_Save",       self.ui.gridLayout_10),
        ]
        for attr, layout in replacements:
            old = getattr(self.ui, attr)
            new = HotkeyLineEdit(old.parent())
            layout.replaceWidget(old, new)
            setattr(self.ui, attr, new)
            new.show()
            old.hide()
            old.deleteLater()

    def _build_colour_buttons(self) -> None:
        """Replace the placeholder QPushButton with one ColourButton per markdown element."""
        old = self.ui.PHColour
        parent = old.parent()
        layout = self.ui.gridLayout_12
        layout.removeWidget(old)
        old.hide()
        old.deleteLater()

        # Existing label becomes the section header
        self.ui.label_9.setText("Markdown Colours")
        header_font = QFont(self.ui.label_9.font())
        header_font.setBold(True)
        self.ui.label_9.setFont(header_font)
        layout.addWidget(self.ui.label_9, 0, 0, 1, 2)

        self.colour_btns: dict[str, ColourButton] = {}
        for row, (key, text) in enumerate(_MARKDOWN_ELEMENTS, start=1):
            btn = ColourButton(colour=_MARKDOWN_COLOUR, parent=parent)
            layout.addWidget(QLabel(text, parent), row, 0, 1, 1)
            layout.addWidget(btn, row, 1, 1, 1)
            self.colour_btns[key] = btn

    def _build_tab_size_spin(self) -> None:
        """Add a tab-size spin box beneath the spell-check language row."""
        parent = self.ui.widget_5
        self.tab_spin = QSpinBox(parent)
        self.tab_spin.setRange(1, 16)
        self.tab_spin.setSuffix(" spaces")
        self.tab_spin.setValue(_TAB_SIZE)
        self.tab_spin.setMaximumSize(QSize(150, 16777215))
        self.ui.gridLayout_6.addWidget(QLabel("Tab Size", parent), 1, 0, 1, 1)
        self.ui.gridLayout_6.addWidget(self.tab_spin, 1, 1, 1, 1)

    def _populate_combos(self) -> None:
        """Fill combo boxes with available options."""
        self.ui.CBTheme.addItems(list(_THEME_OPTIONS.keys()))
        self.ui.CBStyle.addItems(list(_STYLE_OPTIONS.keys()))
        self.ui.CBLang.addItems(_LANG_OPTIONS)

    def _load_current_settings(self) -> None:
        """Read config.json and pre-fill every widget with the current value."""
        if not self.file_func:
            return

        cfg = self.file_func.get_configs()

        # Combo boxes — fall back to first item if stored value isn't recognised
        theme_display = _THEME_DISPLAY.get(cfg.get("theme", "system"), "System")
        style_display = _STYLE_DISPLAY.get(cfg.get("style", "default"), "Default")
        lang = cfg.get("Language", "en_GB")

        self._set_combo(self.ui.CBTheme, theme_display)
        self._set_combo(self.ui.CBStyle, style_display)
        self._set_combo(self.ui.CBLang, lang)

        # Hotkey fields
        hotkeys = cfg.get("Hotkeys", {})
        for ui_name, cfg_key in _HOTKEY_FIELDS:
            if hasattr(self.ui, ui_name):
                getattr(self.ui, ui_name).setText(hotkeys.get(cfg_key, ""))

        self.tab_spin.setValue(int(cfg.get("tab_size", _TAB_SIZE)))

        # Markdown colours
        colours = cfg.get("markdown_colours", {})
        for key, btn in self.colour_btns.items():
            btn.set_colour(colours.get(key, _MARKDOWN_COLOUR))

    def _connect_signals(self) -> None:
        self.ui.ButtonSave.clicked.connect(self.save_settings)
        self.ui.ButtonReset.clicked.connect(self.reset_settings)

    ## Slots
    def save_settings(self) -> None:
        settings = {
            "theme":            _THEME_OPTIONS.get(self.ui.CBTheme.currentText(), "system"),
            "style":            _STYLE_OPTIONS.get(self.ui.CBStyle.currentText(), "default"),
            "Language":         self.ui.CBLang.currentText(),
            "tab_size":         self.tab_spin.value(),
            "markdown_colours": {key: btn.colour() for key, btn in self.colour_btns.items()},
            "Hotkeys":          self._read_hotkeys(),
        }

        if self.file_func:
            self.file_func.save_configs(settings)
        self.accept()

    def reset_settings(self) -> None:
        if self.file_func:
            self.file_func.reset_configs(defaults=True)
        self.accept()

    ## Helpers
    def _read_hotkeys(self) -> dict:
        result = {}
        for ui_name, cfg_key in _HOTKEY_FIELDS:
            if hasattr(self.ui, ui_name):
                result[cfg_key] = getattr(self.ui, ui_name).text()
        return result

    @staticmethod
    def _set_combo(combo, value: str) -> None:
        idx = combo.findText(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)