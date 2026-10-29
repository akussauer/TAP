import os
import re
import pdfkit
import markdown as md_converter

from docx import Document
from docx.shared import Inches

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QMainWindow, QMessageBox, QStackedWidget,
    QWidget
    )

from Pages.UI.ui_Main_Window import Ui_Main_Window
from Pages.Helpers.Settings_Dialog import SettingsDialog

from Widgets.md_highlighter import MarkdownHighlighter
from Widgets.subject_widget import SubjectWidget
from Widgets.subject_navigator import SubjectNavigator

from Functions.Appearance import apply_appearance
from Functions.FileFunctions import FunctionsFile
from Functions.LessonStore import LESSON_EXT, LessonFileError, now_iso, read_lesson, write_lesson
from Functions.Plotter import Plotter

class MainWindow(QMainWindow):
    def __init__(self, open_path: str | None = None):
        super().__init__()
        self.ui = Ui_Main_Window()
        self.ui.setupUi(self)

        # Exclude hidden placeholder widgets and toolbar buttons from tab chain
        for w in (
            self.ui.LELessonTitle_0,
            self.ui.CBSessionType_0,
            self.ui.TEContent_0,
            self.ui.PBNewSubject,
            self.ui.PBEndLesson,
        ):
            w.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # External helpers 
        self.file_func = FunctionsFile(parent=self)
        self.configs = self.file_func.get_configs()
        self.plotter = Plotter(file_func=self.file_func)

        # Lesson-level timer
        self.timer_running = False
        self.timer_time = 0
        self.qt_timer = QTimer(self)
        self.qt_timer.setInterval(1000)
        self.qt_timer.timeout.connect(self.timer_tick)

        # Subject management
        self._subject_widgets: list[SubjectWidget] = []
        self._active_index: int = 0
        self._current_file_path: str | None = None   # set after save/open

        # Unsaved-changes tracking and autosave backup
        self._dirty: bool = False
        self._loading: bool = False            # suppress dirty-marking while populating widgets
        self._created_at: str | None = None    # kept across saves of the same lesson
        self._autosave_failed: bool = False

        self._autosave_timer = QTimer(self)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.setInterval(2000)   # back up 2 s after the last change
        self._autosave_timer.timeout.connect(self._write_backup)

        # Replace placeholder widgets
        self._setup_navigator()
        self._setup_stacked_area()

        # First blank subject
        self._add_subject_widget(label="Subject 1")

        # Connect signals
        self.connect_signals()
        self.ui.LCDDisplay_lesson.display(self._fmt_time(0))

        # Bring back the last session, then open any file we were launched with
        self._update_title_bar()
        self._restore_backup()
        if open_path:
            QTimer.singleShot(0, lambda: self.open_file_request(open_path))

    ## Layout setup
    def _setup_navigator(self) -> None:
        placeholder = self.ui.SubjectPlaceholder
        parent_layout = self.ui.gridLayout_12

        idx = parent_layout.indexOf(placeholder)
        row, col, rowspan, colspan = parent_layout.getItemPosition(idx)

        parent_layout.removeWidget(placeholder)
        placeholder.hide()

        self.navigator = SubjectNavigator(self.centralWidget())
        parent_layout.addWidget(self.navigator, row, col, rowspan, colspan)

    def _setup_stacked_area(self) -> None:
        container_subject = self.ui.ContainerSubject
        parent_layout = self.ui.gridLayout_11

        idx = parent_layout.indexOf(container_subject)
        row, col, rowspan, colspan = parent_layout.getItemPosition(idx)

        parent_layout.removeWidget(container_subject)
        container_subject.hide()

        self.stack = QStackedWidget(self.ui.ContainerLesson)
        parent_layout.addWidget(self.stack, row, col, rowspan, colspan)

    ## Signal connections
    def connect_signals(self) -> None:
        self.ui.PBPPlayLesson.clicked.connect(self.StartStopTimer)
        self.ui.PBResetLesson.clicked.connect(self.timer_reset)

        self.ui.PBNewSubject.clicked.connect(self.on_new_subject)
        self.ui.PBEndLesson.clicked.connect(self.on_end_lesson)

        self.navigator.subject_selected.connect(self._on_navigator_select)
        self.navigator.order_changed.connect(self._on_order_changed)
        self.navigator.subject_deleted.connect(self._on_subject_deleted)

        self.ui.action_New.triggered.connect(self.on_action_new)
        self.ui.action_Open.triggered.connect(self.on_action_open)
        self.ui.actionSave_2.triggered.connect(self.save_lesson)
        self.ui.action_Markdown.triggered.connect(self.export_to_markdown)
        self.ui.action_PDF.triggered.connect(self.export_to_pdf)
        self.ui.action_HTML.triggered.connect(self.save_as_html)
        self.ui.actionDOCX.triggered.connect(self.export_to_docx)
        self.ui.actionSettings.triggered.connect(self.open_settings)

        self.ui.LELessonName.textChanged.connect(self._mark_dirty)

        self._setup_hotkeys()

    def _setup_hotkeys(self) -> None:
        """
        Register QShortcuts from the 'Hotkeys' block in config.json.

        Default config block (add this to your config.json if absent):
        "Hotkeys": {
            "new_subject":      "Ctrl+N",
            "lesson_timer":     "Ctrl+T",
            "save":             "Ctrl+S"
        }
        """
        defaults = {
            "new_subject":   "Ctrl+N",
            "lesson_timer":  "Ctrl+T",
            "save":          "Ctrl+S",
            "open":          "Ctrl+O",
        }
        hk = {**defaults, **self.configs.get("Hotkeys", {})}

        actions = {
            "new_subject":   self.on_new_subject,
            "lesson_timer":  self.StartStopTimer,
            "save":          self.save_lesson,
            "open":          self.on_action_open,
        }

        # Drop any shortcuts from a previous call (settings re-applied at runtime)
        for sc in getattr(self, "_shortcuts", []):
            sc.setEnabled(False)
            sc.setParent(None)

        self._shortcuts: list[QShortcut] = []   # keep references alive
        for key, slot in actions.items():
            sequence = hk.get(key, defaults[key])
            sc = QShortcut(QKeySequence(sequence), self)
            sc.activated.connect(slot)
            self._shortcuts.append(sc)

    ## Subject factory and management
    def _make_subject_widget(self) -> SubjectWidget:
        widget = SubjectWidget(parent=self)

        widget.highlighter = MarkdownHighlighter(
            widget.te_content.document(),
            parent=self,
            file_func=self.file_func,
            language=self.configs.get("Language", "english").lower(),
        )

        widget.te_content.set_tab_size(self.configs.get("tab_size", 4))

        widget.te_content.textChanged.connect(
            lambda w=widget: self._on_text_changed(w)
        )
        widget.te_content._last_text_length = 0

        widget.le_title.textChanged.connect(
            lambda text, w=widget: self._on_title_changed(w, text)
        )

        widget.timer_reset_requested.connect(self._on_subject_timer_reset)

        # Any edit marks the lesson unsaved and schedules a backup.
        # textChanged also fires on re-highlighting, so only count real edits
        # (the document's modified flag), then reset the flag for the next one.
        doc = widget.te_content.document()
        def on_content_changed(doc=doc):
            if doc.isModified():
                doc.setModified(False)
                self._mark_dirty()
        widget.te_content.textChanged.connect(on_content_changed)
        widget.le_title.textChanged.connect(self._mark_dirty)
        widget.cb_session.currentTextChanged.connect(self._mark_dirty)
        widget.timer_reset_requested.connect(self._mark_dirty)

        return widget

    def _add_subject_widget(self, label: str = "") -> SubjectWidget:
        # Stop the current subject's timer before switching away from it
        if self.timer_running and self._subject_widgets:
            self._subject_widgets[self._active_index].stop_timer()

        widget = self._make_subject_widget()
        logical_index = len(self._subject_widgets)

        self._subject_widgets.append(widget)
        self.stack.addWidget(widget)

        self.navigator.add_subject(label or f"Subject {logical_index + 1}", is_active=True)

        self._active_index = logical_index
        self.stack.setCurrentWidget(widget)
        QWidget.setTabOrder(self.ui.LELessonName, widget.le_title)
        QWidget.setTabOrder(widget.le_title, widget.cb_session)
        QWidget.setTabOrder(widget.cb_session, widget.te_content)

        # Start the new subject's timer if the lesson is running
        if self.timer_running:
            widget.start_timer()
        return widget

    ## Lesson timer
    def StartStopTimer(self) -> None:
        if self.timer_running:
            self.timer_stop()
        else:
            self.timer_start()

    def timer_start(self) -> None:
        self.timer_running = True
        self.qt_timer.start()
        self.ui.PBPPlayLesson.setText("Pause")
        if self._subject_widgets:
            self._subject_widgets[self._active_index].start_timer()

    def timer_stop(self) -> None:
        self.timer_running = False
        self.qt_timer.stop()
        self.ui.PBPPlayLesson.setText("Play")
        if self._subject_widgets:
            self._subject_widgets[self._active_index].stop_timer()

    def timer_reset(self) -> None:
        self.timer_stop()
        self.timer_time = 0
        self.ui.LCDDisplay_lesson.display("00:00:00")
        for widget in self._subject_widgets:
            widget._elapsed_seconds = 0
            widget._update_lcd()
        self._mark_dirty()

    def _on_subject_timer_reset(self, discarded_seconds: int) -> None:
        """Subtract the reset subject's discarded seconds from the lesson timer."""
        self.timer_time = max(0, self.timer_time - discarded_seconds)
        self.ui.LCDDisplay_lesson.display(self._fmt_time(self.timer_time))

    def timer_tick(self) -> None:
        self.timer_time += 1
        self.ui.LCDDisplay_lesson.display(self._fmt_time(self.timer_time))

        # Keep the backup's elapsed times current while timers run
        if self.timer_time % 30 == 0:
            self._write_backup()

    ## Subject management slots
    def on_new_subject(self) -> None:
        count = len(self._subject_widgets)
        self._add_subject_widget(label=f"Subject {count + 1}")
        self._mark_dirty()

    def _on_navigator_select(self, logical_index: int) -> None:
        if logical_index < 0 or logical_index >= len(self._subject_widgets):
            return
        # Stop the previously active subject timer when switching
        if self.timer_running and logical_index != self._active_index:
            self._subject_widgets[self._active_index].stop_timer()
        self._active_index = logical_index
        widget = self._subject_widgets[logical_index]
        self.stack.setCurrentWidget(widget)
        QWidget.setTabOrder(self.ui.LELessonName, widget.le_title)
        QWidget.setTabOrder(widget.le_title, widget.cb_session)
        QWidget.setTabOrder(widget.cb_session, widget.te_content)
        # Start the newly focused subject's timer if the lesson is running
        if self.timer_running:
            widget.start_timer()

    def _on_title_changed(self, widget: SubjectWidget, text: str) -> None:
        try:
            logical_index = self._subject_widgets.index(widget)
        except ValueError:
            return
        self.navigator.refresh_item(logical_index, text)

    def _on_order_changed(self, new_order: list[int]) -> None:
        self._subject_widgets = [self._subject_widgets[i] for i in new_order]

        for widget in self._subject_widgets:
            self.stack.removeWidget(widget)
        for widget in self._subject_widgets:
            self.stack.addWidget(widget)

        self._active_index = new_order.index(self._active_index) if self._active_index in new_order else 0
        self.stack.setCurrentWidget(self._subject_widgets[self._active_index])
        self._mark_dirty()

    def _on_subject_deleted(self, logical_index: int) -> None:
        if len(self._subject_widgets) <= 1:
            QMessageBox.information(self, "Cannot Delete", "A lesson must have at least one subject.")
            return

        # Stop the active subject's timer before removing it
        if self.timer_running and logical_index == self._active_index:
            self._subject_widgets[logical_index].stop_timer()

        widget = self._subject_widgets.pop(logical_index)
        self.stack.removeWidget(widget)
        widget.deleteLater()
        self.navigator.remove_subject(logical_index)

        self._active_index = min(self._active_index, len(self._subject_widgets) - 1)
        self.stack.setCurrentWidget(self._subject_widgets[self._active_index])
        self.navigator.set_active_index(self._active_index)

        # Start the replacement subject's timer if the lesson is running
        if self.timer_running:
            self._subject_widgets[self._active_index].start_timer()
        self._mark_dirty()

    def on_end_lesson(self) -> None:
        reply = QMessageBox.question(
            self, "End Lesson", "End the lesson and save?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.timer_stop()
        self.save_lesson()

    ## Data aggregation
    def _build_lesson_dict(self) -> dict:
        subjects = []
        for i, widget in enumerate(self._subject_widgets):
            snap = widget.to_dict()
            snap["index"] = i
            subjects.append(snap)

        return {
            "lesson_name": self.ui.LELessonName.text().strip(),
            "lesson_time": self._fmt_time(self.timer_time),
            "lesson_elapsed_seconds": self.timer_time,
            "created_at": self._created_at,
            "subjects": subjects,
        }

    ## Persist / load
    def save_lesson(self) -> bool:
        """
        Save to the current file if it's a .tap that still exists, otherwise
        fall through to save-as (e.g. new lessons, opened .json files, or a file
        that was moved/deleted). Returns True if the lesson was saved.
        """
        path = self._current_file_path
        if path and path.lower().endswith(LESSON_EXT) and os.path.exists(path):
            return self._write_lesson(path)
        return self.save_lesson_as()

    def save_lesson_as(self) -> bool:
        """Always prompt for a new file location. Returns True if the lesson was saved."""
        path = self._current_file_path
        if path:
            name   = os.path.splitext(os.path.basename(path))[0]
            folder = os.path.dirname(path) if os.path.isdir(os.path.dirname(path)) else self._last_folder()
        else:
            name   = self.ui.LELessonName.text().strip() or "lesson"
            folder = self._last_folder()

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Lesson",
            os.path.join(folder, name + LESSON_EXT),
            f"TAP Lessons (*{LESSON_EXT})",
        )
        if not file_path:
            return False
        if not file_path.lower().endswith(LESSON_EXT):
            file_path += LESSON_EXT

        return self._write_lesson(file_path)

    def _write_lesson(self, path: str) -> bool:
        self._created_at = self._created_at or now_iso()
        try:
            write_lesson(path, self._build_lesson_dict())
        except LessonFileError as e:
            self.file_func.log(f"Failed to save lesson file '{path}': {e}", level="error")
            QMessageBox.critical(self, "Save Failed", f"Could not save file:\n{e}")
            return False

        self._current_file_path = path
        self._remember_folder(path)
        self._set_dirty(False)
        self._write_backup()
        return True

    def _confirm_discard(self, title: str, question: str) -> bool:
        """If there are unsaved changes, ask Save / Discard / Cancel. Returns False to abort."""
        if not self._dirty:
            return True

        reply = QMessageBox.question(
            self, title, question,
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Cancel:
            return False
        if reply == QMessageBox.StandardButton.Save:
            return self.save_lesson()
        return True

    def on_action_open(self) -> None:
        # Prompt for a lesson file, offer to save current work first.
        if not self._confirm_discard("Open Lesson", "Save current lesson before opening another?"):
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Lesson",
            self._last_folder(),
            f"Lessons (*{LESSON_EXT} *.json);;TAP Lessons (*{LESSON_EXT});;JSON Lessons (*.json)",
        )
        if not file_path:
            return

        self.load_from_file(file_path)

    def open_file_request(self, path: str) -> None:
        """Open a lesson passed in from outside (command line / another launch)."""
        name = os.path.basename(path)
        if self._confirm_discard("Open Lesson", f'Save current lesson before opening "{name}"?'):
            self.load_from_file(path)

    def handle_external_open(self, path: str) -> None:
        """Slot for a second TAP launch: come to the front, then open its file (if any)."""
        if self.isMinimized():
            self.showNormal()
        self.raise_()
        self.activateWindow()
        if path:
            self.open_file_request(path)

    def load_from_file(self, path: str) -> None:
        try:
            data, _ = read_lesson(path)
        except LessonFileError as e:
            QMessageBox.critical(self, "Load Error", str(e))
            self.file_func.log(f"Failed to load lesson file '{path}': {e}", level="error")
            return

        self._populate(data)
        self._current_file_path = path
        self._remember_folder(path)
        self._set_dirty(False)
        self._write_backup()

    def _populate(self, data: dict) -> None:
        """Replace the current lesson with data. Timers come back paused."""
        self._loading = True
        try:
            self._clear_all(skip_default=True)

            self.ui.LELessonName.setText(data.get("lesson_name", ""))
            self.timer_time = int(data.get("lesson_elapsed_seconds", 0))
            self.ui.LCDDisplay_lesson.display(self._fmt_time(self.timer_time))

            for i, subj_data in enumerate(data.get("subjects") or [{}]):
                widget = self._add_subject_widget(
                    label=subj_data.get("title") or f"Subject {i + 1}",
                )
                widget.from_dict(subj_data)

            self._created_at = data.get("created_at")
        finally:
            self._loading = False

    def _update_title_bar(self) -> None:
        # Show the open filename in the window title, with • for unsaved changes.
        if self._current_file_path:
            title = f"{os.path.basename(self._current_file_path)} — Lesson Notes"
        else:
            title = "Lesson Notes"
        self.setWindowTitle(f"• {title}" if self._dirty else title)

    def on_action_new(self) -> None:
        if self._dirty:
            reply = QMessageBox.question(
                self, "New Lesson", "Discard current lesson and start fresh?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self._clear_all()
        self._write_backup()

    def _clear_all(self, skip_default: bool = False) -> None:
        self.timer_stop()
        self.timer_time = 0
        self.ui.LCDDisplay_lesson.display("00:00:00")
        self.ui.LELessonName.clear()

        for widget in self._subject_widgets:
            self.stack.removeWidget(widget)
            widget.deleteLater()
        self._subject_widgets.clear()

        self.navigator.clear()
        self._active_index = 0
        self._current_file_path = None
        self._created_at = None
        self._dirty = False
        self._update_title_bar()

        if not skip_default:
            self._add_subject_widget(label="Subject 1")

    ## Unsaved changes / autosave backup
    def _mark_dirty(self, *_) -> None:
        if self._loading:
            return
        if not self._dirty:
            self._set_dirty(True)
        self._autosave_timer.start()   # restarts the 2 s countdown on every change

    def _set_dirty(self, dirty: bool) -> None:
        self._dirty = dirty
        self._update_title_bar()

    def _write_backup(self) -> None:
        """Snapshot the current lesson to appdata so it survives a crash or close."""
        self._autosave_timer.stop()
        self._created_at = self._created_at or now_iso()
        meta = {
            "source_path": self._current_file_path or "",
            "dirty":       int(self._dirty),
        }
        try:
            write_lesson(self.file_func.backup_path, self._build_lesson_dict(), meta)
        except LessonFileError as e:
            self.file_func.log(f"Autosave failed: {e}", level="error")
            if not self._autosave_failed:
                self._autosave_failed = True
                self.statusBar().showMessage("Autosave failed — see log")
            return

        if self._autosave_failed:
            self._autosave_failed = False
            self.statusBar().clearMessage()

    def _restore_backup(self) -> None:
        """Reopen the last session from the appdata backup, if there is one."""
        path = self.file_func.backup_path
        if not os.path.exists(path):
            return
        try:
            data, meta = read_lesson(path)
        except LessonFileError as e:
            self.file_func.log(f"Could not restore last session: {e}", level="warning")
            return

        self._populate(data)
        self._current_file_path = meta.get("source_path") or None
        self._set_dirty(meta.get("dirty") == "1")

    def closeEvent(self, event) -> None:
        # No "save changes?" prompt — the backup brings this session back next launch
        self._write_backup()
        super().closeEvent(event)

    ## Last-used folder
    def _last_folder(self) -> str:
        folder = self.configs.get("last_folder", "")
        return folder if folder and os.path.isdir(folder) else self.file_func.downloads_path

    def _remember_folder(self, path: str) -> None:
        folder = os.path.dirname(os.path.abspath(path))
        if folder != self.configs.get("last_folder"):
            self.configs["last_folder"] = folder
            self.file_func.save_configs({"last_folder": folder})

    ## Bracket auto-pairing
    def _on_text_changed(self, widget: SubjectWidget) -> None:
        te = widget.te_content
        cursor = te.textCursor()
        position = cursor.position()
        text = te.toPlainText()
        current_length = len(text)

        # List continuation / indenting edits aren't typed characters — don't auto-pair
        if current_length <= te._last_text_length or te.structural_edit:
            te._last_text_length = current_length
            return
        te._last_text_length = current_length

        if position == 0:
            return

        typed = text[position - 1]
        PAIRS = {'{': '}', '[': ']', '(': ')', '<': '>', '"': '"'}
        CLOSERS = {v: k for k, v in PAIRS.items() if v != k}

        if typed in CLOSERS:
            opener = CLOSERS[typed]
            if position < len(text) and text[position] == typed:
                new_text = text[:position - 1] + text[position:]
                te.blockSignals(True)
                te.setPlainText(new_text)
                cursor.setPosition(position)
                te.setTextCursor(cursor)
                te.blockSignals(False)
                return

            line_start = text.rfind('\n', 0, position - 1) + 1
            line_so_far = text[line_start:position - 1]
            if opener not in line_so_far:
                new_text = text[:line_start] + opener + text[line_start:]
                te.blockSignals(True)
                te.setPlainText(new_text)
                cursor.setPosition(position + 1)
                te.setTextCursor(cursor)
                te.blockSignals(False)
            return

        if typed not in PAIRS:
            return

        if typed == '[':
            line_start = text.rfind('\n', 0, position) + 1
            line_so_far = text[line_start:position]
            if re.match(r'^\s*-\s+\[$', line_so_far):
                return

        if position < len(text) and text[position] == PAIRS[typed]:
            return

        closing = PAIRS[typed]
        new_text = text[:position] + closing + text[position:]
        te.blockSignals(True)
        te.setPlainText(new_text)
        cursor.setPosition(position)
        te.setTextCursor(cursor)
        te.blockSignals(False)

    ## Export helpers
    @staticmethod
    def _fmt_time(seconds: int) -> str:
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def clean_markdown(self, text: str) -> str:
        text = re.sub(r'\\([#\.\*])', r'\1', text)
        text = re.sub(r'\\-(?!\s*\[)', r'-', text)
        text = text.replace("<br>", "  \n")
        return text

    _HTML_CSS = """
    body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }
    h1 { font-size: 2em; border-bottom: 2px solid #333; padding-bottom: 8px; }
    h2 { font-size: 1.5em; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-top: 2em; }
    h3 { font-size: 1.2em; margin-top: 1.2em; }
    .meta { color: #888; font-size: 0.9em; margin-bottom: 24px; }
    pre { background: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto; }
    code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-family: monospace; }
    blockquote { border-left: 4px solid #ccc; padding-left: 12px; color: #555; margin: 0; }
    ul, ol { padding-left: 24px; margin: 8px 0; }
    li { margin: 4px 0; }
    p { margin: 8px 0; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
    th { background: #f4f4f4; }
    """

    def _render_breakdown_html(self) -> str:
        lesson = self._build_lesson_dict()
        subjects = lesson["subjects"]

        pie_uri = self.plotter.build_pie_uri(subjects)
        bar_uri = self.plotter.build_bar_uri(subjects)
        if not pie_uri and not bar_uri:
            return ""

        parts = [
            '<div class="breakdown" style="page-break-after:always;">',
            '<h2>Lesson Breakdown</h2>',
            '<div class="charts" style="display:flex;flex-direction:column;align-items:center;gap:24px;">',
        ]
        if pie_uri:
            parts.append(f'<img src="{pie_uri}" alt="Time by Subject" style="max-height:320px;">')
        if bar_uri:
            parts.append(f'<img src="{bar_uri}" alt="Time by Session Type" style="max-height:320px;">')
        parts += ['</div>', '</div>']
        return '\n'.join(parts)

    def _render_subjects_html(self) -> str:
        blocks = []
        for subj in self._build_lesson_dict()["subjects"]:
            raw_md = self.clean_markdown(subj.get("content", ""))
            converted = md_converter.markdown(
                raw_md, extensions=["extra", "nl2br", "sane_lists", "tables"]
            )
            converted = re.sub(r'<li>\s*\[ \]', '<li>☐', converted)
            converted = re.sub(r'<li>\s*\[[xX]\]', '<li>☑', converted)

            subj_title = subj.get("title") or "Untitled Subject"
            session    = subj.get("session_type", "")
            elapsed    = self._fmt_time(subj.get("elapsed_seconds", 0))

            blocks.append(
                f'<h2>{subj_title}</h2>'
                f'<p class="meta">{session} | Time: {elapsed}</p>'
                f'{converted}'
            )
        return "\n".join(blocks)

    def _build_full_html(self) -> str:
        lesson = self._build_lesson_dict()
        title  = lesson["lesson_name"] or "Untitled Lesson"
        breakdown = self._render_breakdown_html()
        return (
            f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
            f'<style>{self._HTML_CSS}</style></head><body>'
            f'<h1>{title}</h1>'
            f'<p class="meta">Total lesson time: {lesson["lesson_time"]}</p>'
            f'{breakdown}'
            f'{self._render_subjects_html()}'
            f'</body></html>'
        )

    def export_to_markdown(self) -> None:
        lesson = self._build_lesson_dict()
        title  = lesson["lesson_name"] or "Untitled"

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Export Markdown",
            os.path.join(self.file_func.downloads_path, f"{title}.md"),
            "Markdown Files (*.md)",
        )
        if not save_path:
            return

        # Generate chart images alongside the markdown file
        base = os.path.splitext(save_path)[0]
        subjects = lesson["subjects"]

        breakdown_lines = ["## Lesson Breakdown", ""]
        pie_path = base.replace(" ", "_").replace("'", "") + "_pie.png"
        if self.plotter.save_pie(subjects, pie_path):
            breakdown_lines += [f"![Time by Subject]({os.path.basename(pie_path)})", ""]
        bar_path = base.replace(" ", "_").replace("'", "") + "_bar.png"
        if self.plotter.save_bar(subjects, bar_path):
            breakdown_lines += [f"![Time by Session Type]({os.path.basename(bar_path)})", ""]
        breakdown_lines.append("")

        lines = [f"# {title}", f"**Total time:** {lesson['lesson_time']}", ""] + breakdown_lines
        for subj in subjects:
            elapsed = self._fmt_time(subj.get("elapsed_seconds", 0))
            lines += [
                f"## {subj.get('title') or 'Untitled Subject'}",
                f"**Session:** {subj.get('session_type', '')} | **Time:** {elapsed}",
                "", subj.get("content", ""), "",
            ]

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except OSError as e:
            self.file_func.log(f"Failed to export Markdown: {e}", level="error")
            QMessageBox.critical(self, "Export Failed", f"Could not write file:\n{e}")

    def save_as_html(self) -> None:
        title = self.ui.LELessonName.text().strip() or "lesson"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save as HTML",
            os.path.join(self.file_func.downloads_path, f"{title}.html"),
            "HTML Files (*.html)",
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self._build_full_html())
        except OSError as e:
            self.file_func.log(f"Failed to save HTML: {e}", level="error")
            QMessageBox.critical(self, "Save Failed", f"Could not save file:\n{e}")

    def export_to_pdf(self) -> None:
        title = self.ui.LELessonName.text().strip() or "lesson"
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF",
            os.path.join(self.file_func.downloads_path, f"{title}.pdf"),
            "PDF Files (*.pdf)",
        )
        if not save_path:
            return

        wkhtmltopdf_path = r"Resources\wkhtmltopdf\wkhtmltopdf.exe"
        config  = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        options = {"enable-local-file-access": "", "encoding": "UTF-8"}
        try:
            pdfkit.from_string(self._build_full_html(), save_path, configuration=config, options=options)
        except Exception as e:
            self.file_func.log(f"Failed to export PDF: {e}", level="error")
            QMessageBox.critical(self, "Export Failed", f"Could not write PDF:\n{e}")

    ## Settings dialog
    def open_settings(self):
        dialog = SettingsDialog(self, file_func=self.file_func)
        if dialog.exec():
            self._apply_settings()

    def _apply_settings(self) -> None:
        """Re-apply the saved config to the running app — no relaunch needed."""
        self.configs = self.file_func.get_configs()

        apply_appearance(QApplication.instance(), self.configs)
        self.navigator.refresh_style()
        self._setup_hotkeys()

        tab_size = self.configs.get("tab_size", 4)
        for widget in self._subject_widgets:
            widget.highlighter.reload_config()
            widget.te_content.set_tab_size(tab_size)

    ## DOCX export
    def export_to_docx(self) -> None:
        lesson = self._build_lesson_dict()
        title  = lesson["lesson_name"] or "Untitled"

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Export DOCX",
            os.path.join(self.file_func.downloads_path, f"{title}.docx"),
            "Word Documents (*.docx)",
        )
        if not save_path:
            return

        subjects = lesson["subjects"]
        doc = Document()

        # Title & meta
        doc.add_heading(title, 0)
        doc.add_paragraph(f"Total lesson time: {lesson['lesson_time']}")

        # Breakdown section
        doc.add_page_break()
        doc.add_heading("Lesson Breakdown", 1)
        pie_stream = self.plotter.build_pie_stream(subjects)
        if pie_stream:
            doc.add_picture(pie_stream, width=Inches(5))
        bar_stream = self.plotter.build_bar_stream(subjects)
        if bar_stream:
            doc.add_picture(bar_stream, width=Inches(5))

        # Subject sections
        doc.add_page_break()
        for subj in subjects:
            elapsed = self._fmt_time(subj.get("elapsed_seconds", 0))
            doc.add_heading(subj.get("title") or "Untitled Subject", 1)
            meta_p = doc.add_paragraph()
            meta_run = meta_p.add_run(f"{subj.get('session_type', '')} | Time: {elapsed}")
            meta_run.italic = True
            self._docx_add_markdown(doc, subj.get("content", ""))

        try:
            doc.save(save_path)
        except OSError as e:
            QMessageBox.critical(self, "Export Failed", f"Could not write file:\n{e}")

    def _docx_add_markdown(self, doc: Document, text: str) -> None:
        """Append markdown content to a Document with basic structure & inline formatting."""
        for line in text.splitlines():
            stripped = line.rstrip()
            if not stripped:
                continue
            if stripped.startswith('### '):
                doc.add_heading(stripped[4:], level=3)
            elif stripped.startswith('## '):
                doc.add_heading(stripped[3:], level=2)
            elif stripped.startswith('# '):
                doc.add_heading(stripped[2:], level=1)
            elif re.match(r'^[-*•]\s', stripped):
                self._docx_add_inline(doc.add_paragraph(style='List Bullet'), stripped[2:])
            elif re.match(r'^\d+\.\s', stripped):
                self._docx_add_inline(doc.add_paragraph(style='List Number'),
                                      re.sub(r'^\d+\.\s', '', stripped))
            else:
                self._docx_add_inline(doc.add_paragraph(), stripped)

    @staticmethod
    def _docx_add_inline(para, text: str) -> None:
        """Write text into a paragraph run, handling **bold** and *italic* markers."""
        for part in re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)', text):
            if part.startswith('**') and part.endswith('**') and len(part) > 4:
                para.add_run(part[2:-2]).bold = True
            elif part.startswith('*') and part.endswith('*') and len(part) > 2:
                para.add_run(part[1:-1]).italic = True
            else:
                para.add_run(part)