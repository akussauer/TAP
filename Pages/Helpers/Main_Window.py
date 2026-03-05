from Pages.UI.ui_Main_Window import Ui_Main_Window
from Widgets.md_highlighter import MarkdownHighlighter
from Functions.FileFunctions import FunctionsFile

from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PySide6.QtCore import QTimer

import os
import json
import re
import pdfkit
import markdown as md_converter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Main_Window()
        self.ui.setupUi(self)

        # Init Functions
        self.file_func = FunctionsFile(parent=self)

        # Setup the preferences file if it doesn't exist
        self.configs = self.file_func.get_configs()

        # Qt timer that fires every 1000ms (1 second)
        self.timer_running = False
        self.timer_time = 0
        self.qt_timer = QTimer(self)
        self.qt_timer.setInterval(1000)
        self.qt_timer.timeout.connect(self.timer_tick)

        # Connect Signals and Slots
        self.connect_signals()

        # Extras
        self._last_text_length = 0

    def connect_signals(self):
        # Connect buttons
        self.ui.PBPPlayLesson.clicked.connect(self.StartStopTimer)
        self.ui.PBResetLesson.clicked.connect(self.timer_reset)
        self.ui.actionSave.triggered.connect(self.save_section)
        self.ui.actionMarkdown.triggered.connect(self.export_to_markdown)
        self.ui.actionPDF_2.triggered.connect(self.export_to_pdf)
        self.ui.actionHTML.triggered.connect(self.save_as_html)

        # Fill the first combobox with session options
        options = ['Lecture', 'Exercise', 'Discussion', 'Break', 'Other']
        self.ui.CBSessionType_0.addItems(options)

        # Initialise teh first display
        self.ui.LCDDisplay_lesson.display(self.print_time(return_time=True))

        # Initialise the first markdown highlighter
        self.highlighter = MarkdownHighlighter(
            self.ui.TEContent_0.document(),
            parent=self,
            language=self.configs['Language'].lower()
            )

        # Connect the text changed signal for {}, [], and ()
        self.ui.TEContent_0.textChanged.connect(self.on_text_changed)
    
    def StartStopTimer(self):
        if self.timer_running:
            self.timer_stop()
        else:
            self.timer_start()

    def timer_start(self):
        self.timer_running = True
        self.qt_timer.start()
        self.ui.PBPPlayLesson.setText("Stop")

    def timer_stop(self):
        self.timer_running = False
        self.qt_timer.stop()
        self.ui.PBPPlayLesson.setText("Play")

    def timer_reset(self):
        self.timer_stop()
        self.timer_time = 0
        self.ui.LCDDisplay_lesson.display("00:00:00")

    def timer_tick(self):
        self.timer_time += 1
        # Display the time in HH:MM:SS format on the LCD display
        hours = self.timer_time // 3600
        minutes = (self.timer_time % 3600) // 60
        seconds = self.timer_time % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.ui.LCDDisplay_lesson.display(time_str)

    def print_time(self, return_time=False):
        hours = self.timer_time // 3600
        minutes = (self.timer_time % 3600) // 60
        seconds = self.timer_time % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        if return_time:
            return time_str
        else:
            print(time_str)
    
    def on_text_changed(self):
        cursor = self.ui.TEContent_0.textCursor()
        position = cursor.position()
        text = self.ui.TEContent_0.toPlainText()
        current_length = len(text)

        if current_length <= self._last_text_length:
            self._last_text_length = current_length
            return
        self._last_text_length = current_length

        if position == 0:
            return

        typed = text[position - 1]

        PAIRS = {'{': '}', '[': ']', '(': ')', '<': '>', '"': '"'}  # ' removed entirely
        CLOSERS = {v: k for k, v in PAIRS.items() if v != k}

        # --- Handle closing characters
        if typed in CLOSERS:
            opener = CLOSERS[typed]

            if position < len(text) and text[position] == typed:
                new_text = text[:position - 1] + text[position:]
                self.ui.TEContent_0.blockSignals(True)
                self.ui.TEContent_0.setPlainText(new_text)
                cursor.setPosition(position)
                self.ui.TEContent_0.setTextCursor(cursor)
                self.ui.TEContent_0.blockSignals(False)
                return

            line_start = text.rfind('\n', 0, position - 1) + 1
            line_so_far = text[line_start:position - 1]

            if opener not in line_so_far:
                new_text = text[:line_start] + opener + text[line_start:]
                self.ui.TEContent_0.blockSignals(True)
                self.ui.TEContent_0.setPlainText(new_text)
                cursor.setPosition(position + 1)
                self.ui.TEContent_0.setTextCursor(cursor)
                self.ui.TEContent_0.blockSignals(False)
            return

        if typed not in PAIRS:
            return

        # --- Don't auto-close [ for markdown task lists
        if typed == '[':
            line_start = text.rfind('\n', 0, position) + 1
            line_so_far = text[line_start:position]
            if re.match(r'^\s*-\s+\[$', line_so_far):
                return

        # " is now treated like any other opener — no special mid-word check

        if position < len(text) and text[position] == PAIRS[typed]:
            return

        closing = PAIRS[typed]
        new_text = text[:position] + closing + text[position:]
        self.ui.TEContent_0.blockSignals(True)
        self.ui.TEContent_0.setPlainText(new_text)
        cursor.setPosition(position)
        self.ui.TEContent_0.setTextCursor(cursor)
        self.ui.TEContent_0.blockSignals(False)

    def get_current_file(self):
        # Helper function to get the current file data from the UI
        title = self.ui.LELessonName.text().strip()
        session_type = self.ui.CBSessionType_0.currentText()

        return {
            "lesson_title": title,
            "lesson_time": self.print_time(return_time=True),
            "session_type": session_type,
            "content_html": self.ui.TEContent_0.toHtml(),
            "content_plain": self.ui.TEContent_0.toPlainText(),
            "content_md": self.ui.TEContent_0.toMarkdown()
        }
    
    def clean_markdown(self, text: str) -> str:
        # Only remove backslash escapes that aren't part of task list syntax
        text = re.sub(r'\\([#\.\*])', r'\1', text)  # removed \- from the pattern
        
        # Remove escaped dashes only when they're NOT task list items
        text = re.sub(r'\\-(?!\s*\[)', r'-', text)
        
        # Replace <br> tags with a proper markdown line break
        text = text.replace("<br>", "  \n")
        return text
    
    def save_section(self):
        file = self.get_current_file()
        title = file.get("lesson_title", "")

        if not title:
            QMessageBox.warning(self, "Missing Title", "Please enter a title before saving.")
            return

        # Open a Save As dialog defaulting to .json
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Section", os.path.join(self.file_func.downloads_path, f"{title}.json"), "JSON Files (*.json)"
        )

        if not file_path:
            return  # User cancelled

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(file, f, indent=4, ensure_ascii=False)
            # print(f"Section saved to: {file_path}")
        except OSError as e:
            QMessageBox.critical(self, "Save Failed", f"Could not save file:\n{e}")

    def export_to_markdown(self):
        data = self.get_current_file()
        title = data.get("lesson_title", "Untitled")

        md_lines = [
            f"# {title}",
            f"**Session:** {data.get('session_type', '')} | **Time:** {data.get('lesson_time', '')}",
            "",
            data.get("content_plain", "") # The raw text is written in md
        ]
        markdown_output = "\n".join(md_lines)

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Export Markdown", os.path.join(self.file_func.downloads_path, f"{title}.md"), "Markdown Files (*.md)"
        )
        if not save_path:
            return

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(markdown_output)
            # print(f"Markdown exported to: {save_path}")
        except OSError as e:
            QMessageBox.critical(self, "Export Failed", f"Could not write file:\n{e}")

    def md_to_html(self, data: dict) -> str:
        """Shared method to convert markdown content to a styled HTML document."""
        title = data.get("lesson_title", "Untitled")
        raw_md = self.clean_markdown(data.get("content_plain", ""))

        converted_html = md_converter.markdown(
            raw_md,
            extensions=["extra", "nl2br", "sane_lists", "tables"]
        )

        # Manually replace task list items since wkhtmltopdf doesn't render checkboxes
        converted_html = re.sub(
            r'<li>\s*\[ \]', 
            '<li>☐', 
            converted_html
        )
        converted_html = re.sub(
            r'<li>\s*\[[xX]\]', 
            '<li>☑', 
            converted_html
        )

        return f"""<!DOCTYPE html>
            <html lang="en"><head><meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }}
                h1 {{ font-size: 2em; border-bottom: 2px solid #333; padding-bottom: 8px; }}
                h2 {{ font-size: 1.5em; border-bottom: 1px solid #ccc; padding-bottom: 4px; }}
                h3 {{ font-size: 1.2em; margin-top: 1.2em; }}
                .meta {{ color: #888; font-size: 0.9em; margin-bottom: 24px; }}
                pre {{ background: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto; }}
                code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-family: monospace; }}
                blockquote {{ border-left: 4px solid #ccc; padding-left: 12px; color: #555; margin: 0; }}
                ul, ol {{ padding-left: 24px; margin: 8px 0; }}
                li {{ margin: 4px 0; }}
                p {{ margin: 8px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ccc; padding: 8px 12px; text-align: left; }}
                th {{ background: #f4f4f4; }}
            </style></head>
            <body>
                <h1>{title}</h1>
                <p class="meta">{data.get('session_type', '')} | Time: {data.get('lesson_time', '')}</p>
                {converted_html}
            </body></html>"""

    def save_as_html(self):
        data = self.get_current_file()
        title = data.get("lesson_title", "Untitled")

        if not title:
            QMessageBox.warning(self, "Missing Title", "Please enter a lesson title before saving.")
            return

        # Open a Save As dialog defaulting to .html and in the downloads folder
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save as HTML", os.path.join(self.file_func.downloads_path, f"{title}.html"), "HTML Files (*.html)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.md_to_html(data))
        except OSError as e:
            QMessageBox.critical(self, "Save Failed", f"Could not save file:\n{e}")

    def export_to_pdf(self):
        data = self.get_current_file()
        title = data.get("lesson_title", "Untitled")

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", os.path.join(self.file_func.downloads_path, f"{title}.pdf"), "PDF Files (*.pdf)"
        )
        if not save_path:
            return

        wkhtmltopdf_path = r"Resources\wkhtmltopdf\wkhtmltopdf.exe"
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        options = {"enable-local-file-access": "", "encoding": "UTF-8"}

        try:
            pdfkit.from_string(self.md_to_html(data), save_path, configuration=config, options=options)
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Could not write PDF:\n{e}")