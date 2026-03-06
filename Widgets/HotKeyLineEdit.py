from PySide6.QtWidgets import QLineEdit, QSizePolicy
from PySide6.QtCore import Qt

class HotkeyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)  # optional: prevents typing
        # Set the size policy to be preferred
        self.setSizePolicy(QSizePolicy.Preferred, self.sizePolicy().verticalPolicy())
        self.setFocusPolicy(Qt.StrongFocus)

    def mousePressEvent(self, event):
        # Mouse press should be ignored to allow keyPressEvent to capture the hotkey
        if event.button() == Qt.LeftButton:
            return
        elif event.button() == Qt.RightButton:
            return
        elif event.button() == Qt.MiddleButton:
            return

    def keyPressEvent(self, event):
        # Ignore the meta key (OS key)
        if event.key() in [Qt.Key_Meta, Qt.Key_Escape]:
            return
        # Ignore the number keys
        if Qt.Key_0 <= event.key() <= Qt.Key_9:
            return

        # Ignore modifier-only presses
        if event.key() in (Qt.Key_Shift, Qt.Key_Control):
            return

        # Define desired modifier order
        modifier_order = [
            ("Ctrl", Qt.ControlModifier),
            ("Shift", Qt.ShiftModifier),
            ("Alt", Qt.AltModifier),
            ("Meta", Qt.MetaModifier),
        ]

        # Collect pressed modifiers in the desired order
        mods = [name for name, qtmod in modifier_order if event.modifiers() & qtmod]

        # Map special keys
        special_keys = {
            Qt.Key_Delete: "Delete",
            Qt.Key_Backspace: "Backspace",
            Qt.Key_Return: "Enter",
            Qt.Key_Enter: "Enter",
            Qt.Key_Escape: "Esc",
            Qt.Key_Tab: "Tab",
            Qt.Key_Space: "Space",
            Qt.Key_Left: "Left",
            Qt.Key_Right: "Right",
            Qt.Key_Up: "Up",
            Qt.Key_Down: "Down"
        }

        # Determine the key name
        if event.key() in special_keys:
            key_name = special_keys[event.key()]
        else:
            key_name = Qt.Key(event.key()).name.replace("Key_", "")

        # Drop any duplicate
        if key_name in mods:
            # Drop the modifier if it's the same as the key
            mods = [m for m in mods if m != key_name]
        # Combine modifiers + key
        hotkey = "+".join(mods + [key_name])

        # Block certain combinations
        if hotkey in ("Ctrl+Alt+Delete", "Ctrl+Alt+Esc", "Ctrl+V", "Ctrl+C", "Ctrl+X"):
            return
        
        # Block Shift+{letter} to avoid conflicts with capital letters
        if hotkey.startswith("Shift+") and len(key_name) == 1 and key_name.isalpha():
            return
        self.setText(hotkey)
