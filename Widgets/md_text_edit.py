import re
from contextlib import contextmanager

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QTextEdit

# indent, list marker (-, *, +, 1. or 1)), spacing, optional checkbox, item text
_LIST_ITEM = re.compile(
    r'^(?P<indent>\s*)(?P<marker>[-*+]|\d+[.)])(?P<space>\s+)(?P<check>\[[ xX]\]\s*)?(?P<body>.*)$'
)

_PLAIN = (Qt.KeyboardModifier.NoModifier, Qt.KeyboardModifier.KeypadModifier)

class MarkdownTextEdit(QTextEdit):
    """QTextEdit with markdown list editing: continue/renumber on Enter, indent with Tab/Shift+Tab."""

    def __init__(self, parent=None, tab_size: int = 4):
        super().__init__(parent)
        # True while this widget makes its own multi-step edits, so textChanged
        # listeners (e.g. bracket auto-pairing) can ignore them
        self.structural_edit = False
        self.set_tab_size(tab_size)

    ## Tab size
    def set_tab_size(self, size: int) -> None:
        self._tab_size = max(1, int(size))
        self._update_tab_stop()

    def _update_tab_stop(self) -> None:
        # Literal tab characters render at the same width as the space indent
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * self._tab_size)

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.FontChange:
            self._update_tab_stop()

    ## Key handling
    def keyPressEvent(self, event) -> None:
        key  = event.key()
        mods = event.modifiers()

        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and mods in _PLAIN:
            if self._continue_list():
                return
        elif key == Qt.Key.Key_Tab and mods in _PLAIN:
            self._indent()
            return
        elif key == Qt.Key.Key_Backtab:     # Shift+Tab
            self._outdent()
            return
        super().keyPressEvent(event)

    @contextmanager
    def _edit(self, cursor: QTextCursor):
        """Group edits into a single undo step and flag them as structural."""
        self.structural_edit = True
        cursor.beginEditBlock()
        try:
            yield
        finally:
            cursor.endEditBlock()
            self.structural_edit = False

    ## Enter
    def _continue_list(self) -> bool:
        """Handle Enter on a list item. Returns False to fall back to a normal newline."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            return False

        block = cursor.block()
        match = _LIST_ITEM.match(block.text())
        if not match or cursor.positionInBlock() < match.start("body"):
            return False

        with self._edit(cursor):
            if not match.group("body").strip():
                # Empty item — clear the whole row, indentation included
                cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()
            else:
                cursor.insertText("\n" + self._next_prefix(match))
                self._renumber(cursor.block())

        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        return True

    @staticmethod
    def _next_prefix(match: re.Match) -> str:
        marker = match.group("marker")
        if marker[0].isdigit():
            marker = f"{int(marker[:-1]) + 1}{marker[-1]}"

        prefix = match.group("indent") + marker + match.group("space")
        if match.group("check"):
            prefix += "[ ] "
        return prefix

    ## Tab / Shift+Tab
    def _indent(self) -> None:
        cursor = self.textCursor()
        blocks = self._selected_blocks(cursor)
        indent = " " * self._tab_size

        with self._edit(cursor):
            if len(blocks) == 1 and not _LIST_ITEM.match(blocks[0].text()):
                # Ordinary text — insert spaces at the cursor
                cursor.insertText(indent)
                return

            # List item (or multi-line selection) — indent the whole line(s)
            for block in blocks:
                QTextCursor(block).insertText(indent)
            for block in blocks:
                self._renumber(block)

    def _outdent(self) -> None:
        cursor = self.textCursor()
        blocks = self._selected_blocks(cursor)

        with self._edit(cursor):
            for block in blocks:
                text = block.text()
                if text.startswith("\t"):
                    remove = 1
                else:
                    remove = min(self._tab_size, len(text) - len(text.lstrip(" ")))
                if remove:
                    c = QTextCursor(block)
                    c.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, remove)
                    c.removeSelectedText()
            for block in blocks:
                self._renumber(block)

    @staticmethod
    def _selected_blocks(cursor: QTextCursor) -> list:
        doc   = cursor.document()
        first = doc.findBlock(cursor.selectionStart())
        last  = doc.findBlock(cursor.selectionEnd())
        # A selection ending at the very start of a line doesn't include that line
        if last != first and cursor.selectionEnd() == last.position():
            last = last.previous()

        blocks = [first]
        while blocks[-1] != last:
            blocks.append(blocks[-1].next())
        return blocks

    ## Numbering
    def _renumber(self, block) -> None:
        """Renumber ordered items in the contiguous list containing block.
        The top level keeps its first number; nested levels start at 1."""
        if not _LIST_ITEM.match(block.text()):
            return

        start = block
        while start.previous().isValid() and _LIST_ITEM.match(start.previous().text()):
            start = start.previous()

        levels = []   # stack of [indent width, last number used (None for bullets)]
        b = start
        while b.isValid():
            match = _LIST_ITEM.match(b.text())
            if not match:
                break

            width = len(match.group("indent").expandtabs(self._tab_size))
            while levels and levels[-1][0] > width:
                levels.pop()
            if not levels or levels[-1][0] != width:
                levels.append([width, None])
            level = levels[-1]

            marker = match.group("marker")
            if not marker[0].isdigit():
                level[1] = None
            else:
                if level[1] is not None:
                    number = level[1] + 1
                elif len(levels) == 1:
                    number = int(marker[:-1])
                else:
                    number = 1
                level[1] = number

                wanted = f"{number}{marker[-1]}"
                if wanted != marker:
                    c = QTextCursor(b)
                    c.setPosition(b.position() + match.start("marker"))
                    c.setPosition(b.position() + match.end("marker"), QTextCursor.MoveMode.KeepAnchor)
                    c.insertText(wanted)
            b = b.next()
