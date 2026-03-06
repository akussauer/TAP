# -*- coding: utf-8 -*-
"""
Widgets/subject_navigator.py
-----------------------------
A compact navigation panel that lists all subjects in the current lesson.

Features
--------
• Drag-and-drop reordering of rows
• Live title updates (MainWindow calls refresh_item() on text change)
• Visual distinction between the active (editable) subject and frozen ones
• Emits  subject_selected(index)   when the user clicks a row
• Emits  order_changed(new_order)  after a drag-drop with the new index mapping
• Right-click → Delete (with confirmation)
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)


class SubjectNavigator(QWidget):
    # Emitted when the user clicks a different subject row
    subject_selected = Signal(int)          # logical subject index
    # Emitted after drag-drop; payload is the new logical order
    # e.g. [2, 0, 1] means "what was index 2 is now first" etc.
    order_changed = Signal(list)
    # Emitted when the user deletes a subject via the context menu
    subject_deleted = Signal(int)           # logical subject index

    def __init__(self, parent=None):
        super().__init__(parent)
        self._building = False          # guard against recursive drop signals
        self._active_index: int = 0     # which logical index is "live"

        self.setMaximumWidth(200)
        self._build_ui()

    # ──────────────────────────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        header = QLabel("Subjects", self)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        header.setFont(font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        self.list_widget = QListWidget(self)
        self.list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.setSpacing(1)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: palette(base);
                border: 1px solid palette(mid);
                outline: none;
            }
            QListWidget::item {
                color: palette(text);
                background: palette(base);
                padding: 4px 6px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background: palette(highlight);
                color: palette(highlighted-text);
                outline: none;
            }
            QListWidget::item:focus {
                outline: none;
                border: none;
            }
        """)

        # Signals
        self.list_widget.currentRowChanged.connect(self._on_row_changed)
        self.list_widget.currentRowChanged.connect(self._on_selection_style_changed)
        self.list_widget.model().rowsMoved.connect(self._on_rows_moved)
        self.list_widget.customContextMenuRequested.connect(self._on_context_menu)

        layout.addWidget(self.list_widget)

    # ──────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────

    def add_subject(self, title: str, is_active: bool = True) -> None:
        """Append a new entry. Pass is_active=True for the live subject."""
        self._building = True
        item = QListWidgetItem(title or "Untitled")
        item.setData(Qt.ItemDataRole.UserRole, self.list_widget.count())
        self._style_item(item, is_active)
        self.list_widget.addItem(item)
        if is_active:
            # Mark previous active item as frozen
            prev = self._active_index
            self._active_index = self.list_widget.count() - 1
            self._restyle_item_at(prev, frozen=True)
            self.list_widget.setCurrentRow(self._active_index)
        self._building = False

    def refresh_item(self, logical_index: int, title: str) -> None:
        """Update the display title for a subject (called as the user types)."""
        row = self._logical_to_row(logical_index)
        if row < 0:
            return
        item = self.list_widget.item(row)
        if item:
            item.setText(title or "Untitled")

    def set_active_index(self, logical_index: int) -> None:
        """Mark a different subject as the active (editable) one."""
        old_row = self._logical_to_row(self._active_index)
        self._restyle_item_at(old_row, frozen=True)
        self._active_index = logical_index
        new_row = self._logical_to_row(logical_index)
        self._restyle_item_at(new_row, frozen=False)
        self._building = True
        self.list_widget.setCurrentRow(new_row)
        self._building = False

    def current_logical_index(self) -> int:
        row = self.list_widget.currentRow()
        return self._row_to_logical(row)

    def count(self) -> int:
        return self.list_widget.count()

    def remove_subject(self, logical_index: int) -> None:
        """Remove an entry by logical index and renumber the rest."""
        row = self._logical_to_row(logical_index)
        if row < 0:
            return
        self.list_widget.takeItem(row)
        self._renumber_items()

    def clear(self) -> None:
        self.list_widget.clear()
        self._active_index = 0

    # ──────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────

    def _style_item(self, item: QListWidgetItem, is_active: bool) -> None:
        font = QFont()
        font.setBold(is_active)
        item.setFont(font)

    def _restyle_item_at(self, row: int, frozen: bool) -> None:
        if row < 0 or row >= self.list_widget.count():
            return
        item = self.list_widget.item(row)
        if item:
            self._style_item(item, is_active=not frozen)

    def _logical_to_row(self, logical_index: int) -> int:
        """Find the current visual row that holds a given logical index."""
        for r in range(self.list_widget.count()):
            item = self.list_widget.item(r)
            if item and item.data(Qt.ItemDataRole.UserRole) == logical_index:
                return r
        return -1

    def _row_to_logical(self, row: int) -> int:
        item = self.list_widget.item(row)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return 0

    def _renumber_items(self) -> None:
        """Re-assign UserRole logical indices after a deletion."""
        for r in range(self.list_widget.count()):
            item = self.list_widget.item(r)
            if item:
                item.setData(Qt.ItemDataRole.UserRole, r)
        self._active_index = self.list_widget.currentRow()

    # ──────────────────────────────────────────────────────────────────
    # Slots
    # ──────────────────────────────────────────────────────────────────

    def _on_row_changed(self, row: int) -> None:
        if self._building or row < 0:
            return
        logical = self._row_to_logical(row)
        self.subject_selected.emit(logical)

    def _on_selection_style_changed(self, current_row: int) -> None:
        """Bold the newly selected row, unbold all others."""
        for r in range(self.list_widget.count()):
            item = self.list_widget.item(r)
            if item:
                self._style_item(item, is_active=(r == current_row))

    def _on_rows_moved(self, *_) -> None:
        """Fire order_changed after a drag-drop reorder."""
        if self._building:
            return
        new_order = [
            self.list_widget.item(r).data(Qt.ItemDataRole.UserRole)
            for r in range(self.list_widget.count())
        ]
        # Renumber so logical indices match visual order
        for r in range(self.list_widget.count()):
            self.list_widget.item(r).setData(Qt.ItemDataRole.UserRole, r)
        # Re-sync active index to its new visual row
        self._active_index = self.list_widget.currentRow()
        self.order_changed.emit(new_order)

    def _on_context_menu(self, pos) -> None:
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        logical = item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu(self)
        delete_action = menu.addAction("🗑  Delete subject")
        action = menu.exec(self.list_widget.mapToGlobal(pos))

        if action == delete_action:
            reply = QMessageBox.question(
                self,
                "Delete Subject",
                f'Delete "{item.text()}"? This cannot be undone.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.subject_deleted.emit(logical)