# -*- coding: utf-8 -*-
"""
main_window.py
--------------
Lesson controller.  Layout:
  Left  →  SubjectNavigator  (replaces SubjectPlaceholder)
  Right →  QStackedWidget    (one page per SubjectWidget, shown one at a time)

Subject lifecycle
-----------------
1.  App opens            → one blank SubjectWidget (index 0) created, navigator shows it.
2.  "New Subject"        → active subject is frozen + snapshotted, a new blank
                           SubjectWidget is pushed onto the stack and selected.
3.  Click navigator row  → stacked widget shows that subject's page.
4.  Frozen subject       → SubjectWidget shows an "Edit" button; clicking it
                           re-enables editing for that subject.
5.  Drag-drop in nav     → subject list is reordered in-place; stacked widget
                           pages are rearranged to match.
6.  Delete via nav       → subject removed from stack + internal list.
"""

import json
import os
import re

import pdfkit
import markdown as md_converter

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from Pages.UI.ui_Main_Window import Ui_Main_Window
from Widgets.md_highlighter import MarkdownHighlighter
from Widgets.subject_widget import SubjectWidget
from Widgets.subject_navigator import SubjectNavigator
from Functions.FileFunctions import FunctionsFile


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Main_Window()
        self.ui.setupUi(self)

        # ── External helpers ──────────────────────────────────────────
        self.file_func = FunctionsFile(parent=self)
        self.configs = self.file_func.get_configs()

        # ── Lesson-level timer ────────────────────────────────────────
        self.timer_running = False
        self.timer_time = 0
        self.qt_timer = QTimer(self)
        self.qt_timer.setInterval(1000)
        self.qt_timer.timeout.connect(self.timer_tick)

        # ── Subject management ────────────────────────────────────────
        # Parallel lists – index N in each list corresponds to subject N
        self._subject_widgets: list[SubjectWidget] = []
        self._subject_data_cache: list[dict] = []   # snapshots of frozen subjects
        self._active_index: int = 0                 # which subject is currently "live"

        # ── Replace placeholder widgets ───────────────────────────────
        self._setup_navigator()
        self._setup_stacked_area()

        # ── First blank subject ───────────────────────────────────────
        self._add_subject_widget(label="Subject 1", make_active=True)

        # ── Wiring ───────────────────────────────────────────────────
        self.connect_signals()
        self.ui.LCDDisplay_lesson.display(self._fmt_time(0))

    # ══════════════════════════════════════════════════════════════════
    # Layout setup
    # ══════════════════════════════════════════════════════════════════

    def _setup_navigator(self) -> None:
        """
        Replace the SubjectPlaceholder QWidget from the designer file with
        our SubjectNavigator, preserving its position in the grid.
        """
        placeholder = self.ui.SubjectPlaceholder
        parent_layout = self.ui.gridLayout_12   # top-level grid of centralwidget

        # Find which cell the placeholder occupies
        idx = parent_layout.indexOf(placeholder)
        row, col, rowspan, colspan = parent_layout.getItemPosition(idx)

        parent_layout.removeWidget(placeholder)
        placeholder.hide()

        self.navigator = SubjectNavigator(self.centralWidget())
        parent_layout.addWidget(self.navigator, row, col, rowspan, colspan)

    def _setup_stacked_area(self) -> None:
        """
        Replace ContainerSubject (the designer's single-subject placeholder)
        with a QStackedWidget that holds one SubjectWidget per subject.
        """
        container_subject = self.ui.ContainerSubject
        parent_layout = self.ui.gridLayout_11   # layout inside ContainerLesson

        idx = parent_layout.indexOf(container_subject)
        row, col, rowspan, colspan = parent_layout.getItemPosition(idx)

        parent_layout.removeWidget(container_subject)
        container_subject.hide()

        self.stack = QStackedWidget(self.ui.ContainerLesson)
        parent_layout.addWidget(self.stack, row, col, rowspan, colspan)

    # ══════════════════════════════════════════════════════════════════
    # Signal connections
    # ══════════════════════════════════════════════════════════════════

    def connect_signals(self) -> None:
        # Lesson timer
        self.ui.PBPPlayLesson.clicked.connect(self.StartStopTimer)
        self.ui.PBResetLesson.clicked.connect(self.timer_reset)

        # Subject management
        self.ui.PBNewSubject.clicked.connect(self.on_new_subject)
        self.ui.PBEndLesson.clicked.connect(self.on_end_lesson)

        # Navigator
        self.navigator.subject_selected.connect(self._on_navigator_select)
        self.navigator.order_changed.connect(self._on_order_changed)
        self.navigator.subject_deleted.connect(self._on_subject_deleted)

        # File menu
        self.ui.actionNew.triggered.connect(self.on_action_new)
        self.ui.actionSave.triggered.connect(self.save_lesson)
        self.ui.actionMarkdown.triggered.connect(self.export_to_markdown)
        self.ui.actionPDF_2.triggered.connect(self.export_to_pdf)
        self.ui.actionHTML.triggered.connect(self.save_as_html)

    # ══════════════════════════════════════════════════════════════════
    # Subject factory
    # ══════════════════════════════════════════════════════════════════

    def _make_subject_widget(self) -> SubjectWidget:
        """Build a SubjectWidget and wire up its dependencies."""
        widget = SubjectWidget(parent=self)

        MarkdownHighlighter(
            widget.te_content.document(),
            parent=self,
            language=self.configs.get("Language", "english").lower(),
        )

        widget.te_content.textChanged.connect(
            lambda w=widget: self._on_text_changed(w)
        )
        widget.te_content._last_text_length = 0

        # Live title → navigator label
        widget.le_title.textChanged.connect(
            lambda text, w=widget: self._on_title_changed(w, text)
        )

        # Focus on a frozen subject → unfreeze it
        widget.focused.connect(
            lambda w=widget: self._on_edit_requested(w)
        )

        return widget

    def _add_subject_widget(self, label: str = "", make_active: bool = True) -> SubjectWidget:
        """
        Create a new SubjectWidget, register it in the stack and navigator,
        optionally freeze the previously active subject first.
        """
        # Freeze the currently active subject before switching
        if make_active and self._subject_widgets:
            self._freeze_subject(self._active_index)

        widget = self._make_subject_widget()
        logical_index = len(self._subject_widgets)

        self._subject_widgets.append(widget)
        self._subject_data_cache.append({})         # placeholder; filled on freeze
        self.stack.addWidget(widget)

        nav_label = label or f"Subject {logical_index + 1}"
        self.navigator.add_subject(nav_label, is_active=make_active)

        if make_active:
            self._active_index = logical_index
            self.stack.setCurrentWidget(widget)

        return widget

    # ══════════════════════════════════════════════════════════════════
    # Freeze / unfreeze
    # ══════════════════════════════════════════════════════════════════

    def _freeze_subject(self, logical_index: int) -> None:
        """Snapshot and lock a subject widget."""
        if logical_index >= len(self._subject_widgets):
            return
        widget = self._subject_widgets[logical_index]
        snapshot = widget.to_dict()
        snapshot["index"] = logical_index
        self._subject_data_cache[logical_index] = snapshot
        widget.freeze()

    def _unfreeze_subject(self, logical_index: int) -> None:
        """Re-enable editing for a frozen subject."""
        if logical_index >= len(self._subject_widgets):
            return
        self._subject_widgets[logical_index].unfreeze()
        self._active_index = logical_index
        self.navigator.set_active_index(logical_index)

    # ══════════════════════════════════════════════════════════════════
    # Lesson timer
    # ══════════════════════════════════════════════════════════════════

    def StartStopTimer(self) -> None:
        if self.timer_running:
            self.timer_stop()
        else:
            self.timer_start()

    def timer_start(self) -> None:
        self.timer_running = True
        self.qt_timer.start()
        self.ui.PBPPlayLesson.setText("Stop")

    def timer_stop(self) -> None:
        self.timer_running = False
        self.qt_timer.stop()
        self.ui.PBPPlayLesson.setText("Play")

    def timer_reset(self) -> None:
        self.timer_stop()
        self.timer_time = 0
        self.ui.LCDDisplay_lesson.display("00:00:00")

    def timer_tick(self) -> None:
        self.timer_time += 1
        self.ui.LCDDisplay_lesson.display(self._fmt_time(self.timer_time))

    # ══════════════════════════════════════════════════════════════════
    # Subject management slots
    # ══════════════════════════════════════════════════════════════════

    def on_new_subject(self) -> None:
        count = len(self._subject_widgets)
        self._add_subject_widget(label=f"Subject {count + 1}", make_active=True)

    def _on_navigator_select(self, logical_index: int) -> None:
        """User clicked a row in the navigator — show that subject's page."""
        if logical_index < 0 or logical_index >= len(self._subject_widgets):
            return
        self.stack.setCurrentWidget(self._subject_widgets[logical_index])

    def _on_edit_requested(self, widget: SubjectWidget) -> None:
        """User clicked the Edit button on a frozen subject."""
        try:
            logical_index = self._subject_widgets.index(widget)
        except ValueError:
            return
        self._unfreeze_subject(logical_index)

    def _on_title_changed(self, widget: SubjectWidget, text: str) -> None:
        """Propagate title edits to the navigator label in real-time."""
        try:
            logical_index = self._subject_widgets.index(widget)
        except ValueError:
            return
        self.navigator.refresh_item(logical_index, text)

    def _on_order_changed(self, new_order: list[int]) -> None:
        """
        Drag-drop reordered the navigator rows.
        new_order[i] = old logical index now at visual position i.
        Reorder _subject_widgets and _subject_data_cache to match.
        """
        self._subject_widgets = [self._subject_widgets[i] for i in new_order]
        self._subject_data_cache = [self._subject_data_cache[i] for i in new_order]

        # Update stack order to match (rebuild by re-inserting pages)
        for i, widget in enumerate(self._subject_widgets):
            self.stack.removeWidget(widget)
        for widget in self._subject_widgets:
            self.stack.addWidget(widget)

        # Recalculate active index
        self._active_index = new_order.index(self._active_index) if self._active_index in new_order else 0
        self.stack.setCurrentWidget(self._subject_widgets[self._active_index])

    def _on_subject_deleted(self, logical_index: int) -> None:
        """Remove a subject entirely."""
        if len(self._subject_widgets) <= 1:
            QMessageBox.information(self, "Cannot Delete", "A lesson must have at least one subject.")
            return

        widget = self._subject_widgets.pop(logical_index)
        self._subject_data_cache.pop(logical_index)

        self.stack.removeWidget(widget)
        widget.deleteLater()
        self.navigator.remove_subject(logical_index)

        # Clamp active index and show the nearest subject
        self._active_index = min(self._active_index, len(self._subject_widgets) - 1)
        self.stack.setCurrentWidget(self._subject_widgets[self._active_index])
        self.navigator.set_active_index(self._active_index)

    def on_end_lesson(self) -> None:
        reply = QMessageBox.question(
            self,
            "End Lesson",
            "End the lesson and save?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.timer_stop()
        self.save_lesson()

    # ══════════════════════════════════════════════════════════════════
    # Data aggregation
    # ══════════════════════════════════════════════════════════════════

    def _build_lesson_dict(self) -> dict:
        """Collect live data from all subject widgets into a nested dict."""
        subjects = []
        for i, widget in enumerate(self._subject_widgets):
            snap = widget.to_dict()
            snap["index"] = i
            subjects.append(snap)

        return {
            "lesson_name": self.ui.LELessonName.text().strip(),
            "lesson_time": self._fmt_time(self.timer_time),
            "lesson_elapsed_seconds": self.timer_time,
            "subjects": subjects,
        }

    # ══════════════════════════════════════════════════════════════════
    # Persist / load
    # ══════════════════════════════════════════════════════════════════

    def save_lesson(self) -> None:
        lesson = self._build_lesson_dict()
        title = lesson["lesson_name"] or "lesson"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Lesson",
            os.path.join(self.file_func.downloads_path, f"{title}.json"),
            "JSON Files (*.json)",
        )
        if not file_path:
            return
        if not file_path.endswith(".json"):
            file_path += ".json"

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(lesson, f, indent=4, ensure_ascii=False)
        except OSError as e:
            QMessageBox.critical(self, "Save Failed", f"Could not save file:\n{e}")

    def load_from_file(self, path: str) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            QMessageBox.critical(self, "Load Error", str(e))
            return

        self._clear_all()

        self.ui.LELessonName.setText(data.get("lesson_name", ""))
        self.timer_time = int(data.get("lesson_elapsed_seconds", 0))
        self.ui.LCDDisplay_lesson.display(self._fmt_time(self.timer_time))

        subjects = data.get("subjects", [])
        for i, subj_data in enumerate(subjects):
            is_last = i == len(subjects) - 1
            widget = self._add_subject_widget(
                label=subj_data.get("title") or f"Subject {i + 1}",
                make_active=is_last,
            )
            widget.from_dict(subj_data)
            if not is_last:
                self._freeze_subject(i)

    def on_action_new(self) -> None:
        has_content = len(self._subject_widgets) > 1 or bool(
            self._subject_widgets and self._subject_widgets[0].le_title.text()
        )
        if has_content:
            reply = QMessageBox.question(
                self,
                "New Lesson",
                "Discard current lesson and start fresh?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self._clear_all()

    def _clear_all(self) -> None:
        self.timer_stop()
        self.timer_time = 0
        self.ui.LCDDisplay_lesson.display("00:00:00")
        self.ui.LELessonName.clear()

        for widget in self._subject_widgets:
            self.stack.removeWidget(widget)
            widget.deleteLater()
        self._subject_widgets.clear()
        self._subject_data_cache.clear()

        self.navigator.clear()
        self._active_index = 0
        self._add_subject_widget(label="Subject 1", make_active=True)

    # ══════════════════════════════════════════════════════════════════
    # Bracket auto-pairing
    # ══════════════════════════════════════════════════════════════════

    def _on_text_changed(self, widget: SubjectWidget) -> None:
        te = widget.te_content
        cursor = te.textCursor()
        position = cursor.position()
        text = te.toPlainText()
        current_length = len(text)

        if current_length <= te._last_text_length:
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

    # ══════════════════════════════════════════════════════════════════
    # Export helpers
    # ══════════════════════════════════════════════════════════════════

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
        return (
            f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
            f'<style>{self._HTML_CSS}</style></head><body>'
            f'<h1>{title}</h1>'
            f'<p class="meta">Total lesson time: {lesson["lesson_time"]}</p>'
            f'{self._render_subjects_html()}'
            f'</body></html>'
        )

    def export_to_markdown(self) -> None:
        lesson = self._build_lesson_dict()
        title  = lesson["lesson_name"] or "Untitled"
        lines  = [f"# {title}", f"**Total time:** {lesson['lesson_time']}", ""]
        for subj in lesson["subjects"]:
            elapsed = self._fmt_time(subj.get("elapsed_seconds", 0))
            lines += [
                f"## {subj.get('title') or 'Untitled Subject'}",
                f"**Session:** {subj.get('session_type', '')} | **Time:** {elapsed}",
                "", subj.get("content", ""), "",
            ]

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Export Markdown",
            os.path.join(self.file_func.downloads_path, f"{title}.md"),
            "Markdown Files (*.md)",
        )
        if not save_path:
            return
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except OSError as e:
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
            QMessageBox.critical(self, "Export Failed", f"Could not write PDF:\n{e}")
