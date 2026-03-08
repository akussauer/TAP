from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton

class ColourButton(QPushButton):
    # Emitted whenever the user confirms a new colour
    colour_changed = Signal(str)   # hex string e.g. "#9B4A1C"

    def __init__(self, colour: str = "#ffffff", parent=None):
        super().__init__(parent)
        self._colour = QColor(colour)
        self.clicked.connect(self._open_dialog)
        self._refresh()

    # Public API
    def colour(self) -> str:
        """Return the current colour as a lowercase hex string."""
        return self._colour.name()

    def set_colour(self, colour: str) -> None:
        """Set the colour programmatically without opening the dialog."""
        c = QColor(colour)
        if c.isValid():
            self._colour = c
            self._refresh()

    # Internal logic
    def _open_dialog(self) -> None:
        chosen = QColorDialog.getColor(
            self._colour,
            self,
            "Choose Colour",
            QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if chosen.isValid():
            self._colour = chosen
            self._refresh()
            self.colour_changed.emit(self._colour.name())

    def _refresh(self) -> None:
        """Update button text and stylesheet to reflect the current colour."""
        self.setText(self._colour.name())

        # Pick a label colour (black or white) that contrasts with the background.
        # Uses the standard relative-luminance formula (WCAG).
        r, g, b = self._colour.red(), self._colour.green(), self._colour.blue()
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        text_colour = "#000000" if luminance > 0.5 else "#ffffff"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._colour.name()};
                color: {text_colour};
                border: 1px solid palette(mid);
                border-radius: 3px;
                padding: 3px 8px;
            }}
            QPushButton:hover {{
                border: 1px solid palette(highlight);
            }}
        """)