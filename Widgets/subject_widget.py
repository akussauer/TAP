from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox, QGridLayout, QLabel, QLCDNumber, QLineEdit,
    QPushButton, QSizePolicy, QWidget,
    )

from Widgets.md_text_edit import MarkdownTextEdit

class SubjectWidget(QWidget):
    # Emitted when the subject timer is reset; carries the seconds that were discarded
    timer_reset_requested = Signal(int)

    DEFAULT_SESSION_TYPES = [
        "Lecture", "Exercise", "Discussion",
        "Break", "Demo", "Group Work",
        "Other",
    ]

    def __init__(self, session_types=None, parent=None):
        super().__init__(parent)
        self._elapsed_seconds: int = 0
        self._timer_running: bool = False

        self._qt_timer = QTimer(self)
        self._qt_timer.setInterval(1000)
        self._qt_timer.timeout.connect(self._tick)

        self._build_ui(session_types or self.DEFAULT_SESSION_TYPES)

    ## UI

    def _build_ui(self, session_types: list) -> None:
        root = QGridLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setHorizontalSpacing(0)
        root.setVerticalSpacing(2)

        sp_max = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        # Top bar
        top = QWidget(self)
        top_layout = QGridLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setHorizontalSpacing(4)
        top_layout.setVerticalSpacing(0)
        top.setSizePolicy(sp_max)

        # Title + session-type column
        title_container = QWidget(top)
        title_container.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        )
        title_layout = QGridLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setHorizontalSpacing(4)
        title_layout.setVerticalSpacing(0)

        self.le_title = QLineEdit(title_container)
        font_title = QFont()
        font_title.setPointSize(16)
        font_title.setBold(True)
        self.le_title.setFont(font_title)
        self.le_title.setPlaceholderText("## Subject Title…")
        self.le_title.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        )
        title_layout.addWidget(self.le_title, 0, 0, 1, 1, Qt.AlignmentFlag.AlignBottom)

        session_container = QWidget(title_container)
        session_layout = QGridLayout(session_container)
        session_layout.setContentsMargins(0, 0, 0, 0)
        session_layout.setSpacing(0)

        self.lbl_session = QLabel("Session Type", session_container)
        session_layout.addWidget(self.lbl_session, 0, 0, 1, 1)

        self.cb_session = QComboBox(session_container)
        self.cb_session.setMinimumWidth(125)
        font_cb = QFont()
        font_cb.setPointSize(9)
        self.cb_session.setFont(font_cb)
        self.cb_session.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.cb_session.setEditable(True)
        self.cb_session.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self.cb_session.setPlaceholderText("Type…")
        for st in session_types:
            self.cb_session.addItem(st)
        session_layout.addWidget(self.cb_session, 1, 0, 1, 1)

        title_layout.addWidget(session_container, 0, 1, 1, 1)
        top_layout.addWidget(title_container, 0, 0, 1, 1)

        # Timer column
        timer_container = QWidget(top)
        timer_container.setSizePolicy(sp_max)
        timer_layout = QGridLayout(timer_container)
        timer_layout.setContentsMargins(0, 0, 0, 0)
        timer_layout.setSpacing(0)

        self.lcd = QLCDNumber(timer_container)
        self.lcd.setDigitCount(8)
        self.lcd.setSegmentStyle(QLCDNumber.SegmentStyle.Flat)
        self.lcd.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        )
        self._update_lcd()
        timer_layout.addWidget(self.lcd, 0, 0, 1, 1)

        btn_container = QWidget(timer_container)
        btn_container.setSizePolicy(sp_max)
        btn_layout = QGridLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)

        self.btn_reset = QPushButton("Reset", btn_container)
        self.btn_reset.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_reset.clicked.connect(self.reset_timer)
        btn_layout.addWidget(self.btn_reset, 0, 0, 1, 1)

        timer_layout.addWidget(btn_container, 0, 1, 1, 1)
        top_layout.addWidget(timer_container, 0, 1, 1, 1)

        root.addWidget(top, 0, 0, 1, 1)

        # Notes text-edit
        self.te_content = MarkdownTextEdit(self)
        font_te = QFont()
        font_te.setPointSize(12)
        self.te_content.setFont(font_te)
        self.te_content.setSizePolicy(
            QSizePolicy(
                QSizePolicy.Policy.MinimumExpanding,
                QSizePolicy.Policy.MinimumExpanding,
            )
        )
        root.addWidget(self.te_content, 1, 0, 1, 1)

    ## Timer
    def start_timer(self) -> None:
        if not self._timer_running:
            self._qt_timer.start()
            self._timer_running = True

    def stop_timer(self) -> None:
        if self._timer_running:
            self._qt_timer.stop()
            self._timer_running = False

    def toggle_timer(self) -> None:
        if self._timer_running:
            self.stop_timer()
        else:
            self.start_timer()

    def reset_timer(self) -> None:
        """Reset elapsed time to zero; running state is unchanged.
        Emits timer_reset_requested with the discarded seconds so the lesson
        timer can stay in sync."""
        discarded = self._elapsed_seconds
        self._elapsed_seconds = 0
        self._update_lcd()
        if discarded:
            self.timer_reset_requested.emit(discarded)

    def _tick(self) -> None:
        self._elapsed_seconds += 1
        self._update_lcd()

    def _update_lcd(self) -> None:
        h = self._elapsed_seconds // 3600
        m = (self._elapsed_seconds % 3600) // 60
        s = self._elapsed_seconds % 60
        self.lcd.display(f"{h:02d}:{m:02d}:{s:02d}")

    ## Serialisation
    def to_dict(self) -> dict:
        return {
            "title": self.le_title.text(),
            "session_type": self.cb_session.currentText(),
            "content": self.te_content.toPlainText(),
            "elapsed_seconds": self._elapsed_seconds,
            "timer_was_running": self._timer_running,
        }

    def from_dict(self, data: dict) -> None:
        self.le_title.setText(data.get("title", ""))

        session = data.get("session_type", "")
        idx = self.cb_session.findText(session)
        if idx >= 0:
            self.cb_session.setCurrentIndex(idx)
        else:
            self.cb_session.setCurrentText(session)

        self.te_content.setPlainText(data.get("content", ""))
        self._elapsed_seconds = int(data.get("elapsed_seconds", 0))
        self._update_lcd()

    ## Properties
    @property
    def title(self) -> str:
        return self.le_title.text()

    @property
    def elapsed_seconds(self) -> int:
        return self._elapsed_seconds