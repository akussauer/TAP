import re
import enchant

from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, document, parent=None, file_func=None, language="en_GB"):
        super().__init__(document)
        self.parent = parent
        self.file_func = file_func
        self.rules = []

        if self.file_func:
            config = self.file_func.get_configs()
            if config and "Language" in config:
                language = config["Language"]
                colour = config["markdown_colour"]
            else:
                colour ="#0E80A3"
        else:
            colour = "#0E80A3"

        # Spell checker
        try:
            self.spell = enchant.Dict(language) # Use the specified language dictionary
        except enchant.errors.DictNotFoundError:
            self.spell = None
            QMessageBox.Warning(self.parent, "Spell Check Warning", f"No dictionary found for language '{language}'. Spell checking will be disabled.")

        # Spell check format — red underline
        self.spell_error_fmt = QTextCharFormat()
        self.spell_error_fmt.setUnderlineColor(QColor("#E06C6C"))
        self.spell_error_fmt.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)

        # --- Headings (# ## ###) — orange/gold
        self._add_rule(r'^#{1,6} .+', colour, bold=True)

        # --- Bold (**text**) — white/bright
        self._add_rule(r'\*\*.+?\*\*', colour, bold=True)

        # --- Italic (*text*) — light grey
        self._add_rule(r'\*.+?\*', colour, italic=True)

        # --- Strikethrough (~~text~~) — muted red
        self._add_rule(r'~~.+?~~', colour)

        # --- Ordered list (1. 2. etc) — light blue
        self._add_rule(r'^\d+\.', colour)

        # --- Unordered list (- or *) — light blue
        self._add_rule(r'^[\-\*] ', colour)

        # --- Inline code (`code`) — green
        self._add_rule(r'`.+?`', colour)

        # --- Block quote (>) — muted purple
        self._add_rule(r'^> .+', colour)

        # --- Breaking line (<br>) — muted red
        self._add_rule(r'<br\s*/?>', colour)

        # --- Checkboxes (- [ ] or - [x]) — light blue
        self._add_rule(r'^- \[[ xX]\] ', colour)

        # --- Links ([text](url)) — blue
        self._add_rule(r'\[.+?\]\(.+?\)', colour)

        # --- Horizontal rule (--- or ***) — muted red
        self._add_rule(r'^(\-{3,}|\*{3,})', colour)

    def _add_rule(self, pattern, color, bold=False, italic=False):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        if italic:
            fmt.setFontItalic(True)
        self.rules.append((re.compile(pattern), fmt))

    def highlightBlock(self, text):
        # Apply spell check first (so syntax highlighting renders on top)
        if self.spell:
            self._check_spelling(text)

        # Apply markdown syntax rules
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)

    def _check_spelling(self, text):
         # Find all plain words, skipping URLs and markdown syntax
        for match in re.finditer(r'\b[a-zA-Z]+\b', text):
            word = match.group()

            # Skip short words, URLs, and markdown-stripped tokens
            if len(word) < 2:
                continue

            if not self.spell.check(word):
                self.setFormat(match.start(), len(word), self.spell_error_fmt)