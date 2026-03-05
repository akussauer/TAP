import re
import enchant
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont


class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        # Spell checker
        try:
            self.spell = enchant.Dict("en_GB") # Use British English dictionary
        except enchant.errors.DictNotFoundError:
            self.spell = None
            print("Spell check dictionary not found, spell check disabled.")

        # Spell check format — red underline
        self.spell_error_fmt = QTextCharFormat()
        self.spell_error_fmt.setUnderlineColor(QColor("#E06C6C"))
        self.spell_error_fmt.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)

        # --- Headings (# ## ###) — orange/gold
        self._add_rule(r'^#{1,6} .+', "#E5A00D", bold=True)

        # --- Bold (**text**) — white/bright
        self._add_rule(r'\*\*.+?\*\*', "#FFFFFF", bold=True)

        # --- Italic (*text*) — light grey
        self._add_rule(r'\*.+?\*', "#BBBBBB", italic=True)

        # --- Ordered list (1. 2. etc) — light blue
        self._add_rule(r'^\d+\.', "#6FC3E0")

        # --- Unordered list (- or *) — light blue
        self._add_rule(r'^[\-\*] ', "#6FC3E0")

        # --- Inline code (`code`) — green
        self._add_rule(r'`.+?`', "#4EC994")

        # --- Block quote (>) — muted purple
        self._add_rule(r'^> .+', "#9B8FD4")

        # --- Breaking line (<br>) — muted red
        self._add_rule(r'<br\s*/?>', "#E06C6C")

        # --- Checkboxes (- [ ] or - [x]) — light blue
        self._add_rule(r'^- \[[ xX]\] ', "#6FC3E0")

        # --- Links ([text](url)) — blue
        self._add_rule(r'\[.+?\]\(.+?\)', "#4A9EE0")

        # --- Horizontal rule (--- or ***) — muted red
        self._add_rule(r'^(\-{3,}|\*{3,})', "#E06C6C")

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