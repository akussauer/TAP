import re
import enchant

from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

_DEFAULT_COLOUR = "#0E80A3"

# (colour key in config["markdown_colours"], pattern, bold, italic) — later rules paint over earlier ones
_RULES = [
    # --- Headings (# ## ###)
    ("heading",         r'^#{1,6} .+',                                 True,  False),
    # --- Italic (*text*) — single asterisks only, so bold isn't overridden
    ("italic",          r'(?<!\*)\*(?![\s*]).*?(?<![\s*])\*(?!\*)',    False, True),
    # --- Bold (**text**)
    ("bold",            r'\*\*.+?\*\*',                                True,  False),
    # --- Strikethrough (~~text~~)
    ("strikethrough",   r'~~.+?~~',                                    False, False),
    # --- Ordered (1. 2.) and unordered (- * +) list markers, indented or not
    ("list",            r'^\s*(?:[-*+]|\d+[.)])(?= )',                 False, False),
    # --- Checkboxes (- [ ] or - [x])
    ("checkbox",        r'^\s*[-*+] \[[ xX]\] ',                       False, False),
    # --- Inline code (`code`)
    ("code",            r'`.+?`',                                      False, False),
    # --- Block quote (>)
    ("blockquote",      r'^> .+',                                      False, False),
    # --- Breaking line (<br>)
    ("line_break",      r'<br\s*/?>',                                  False, False),
    # --- Links ([text](url))
    ("link",            r'\[.+?\]\(.+?\)',                             False, False),
    # --- Horizontal rule (--- or ***)
    ("horizontal_rule", r'^(\-{3,}|\*{3,})',                           False, False),
]

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

        # Spell checker
        try:
            self.spell = enchant.Dict(language) # Use the specified language dictionary
        except enchant.errors.DictNotFoundError:
            self.spell = None
            if self.file_func:
                self.file_func.log(f"No dictionary found for language '{language}'. Spell checking disabled.", level="warning")
            QMessageBox.warning(self.parent, "Spell Check Warning", f"No dictionary found for language '{language}'. Spell checking will be disabled.")

        # Spell check format — red underline
        self.spell_error_fmt = QTextCharFormat()
        self.spell_error_fmt.setUnderlineColor(QColor("#E06C6C"))
        self.spell_error_fmt.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)

        self._build_rules()

    def reload_colours(self) -> None:
        """Re-read colours from config and repaint the document."""
        self._build_rules()
        self.rehighlight()

    def _build_rules(self) -> None:
        colours = self.file_func.get_configs().get("markdown_colours", {}) if self.file_func else {}
        self.rules = []
        for key, pattern, bold, italic in _RULES:
            self._add_rule(pattern, colours.get(key, _DEFAULT_COLOUR), bold=bold, italic=italic)

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
