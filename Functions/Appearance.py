from PySide6.QtCore import Qt

# config["theme"] → Qt colour scheme ("system" follows the OS setting)
_THEMES = {
    "light":  Qt.ColorScheme.Light,
    "dark":   Qt.ColorScheme.Dark,
    "system": Qt.ColorScheme.Unknown,
}

_default_style: str | None = None   # platform style, captured before the first override

def apply_appearance(app, config: dict) -> None:
    """Apply theme and style from config. Safe to call again at runtime."""
    global _default_style
    if _default_style is None:
        _default_style = app.style().name()

    # Style first — setting a style resets the palette
    style = str(config.get("style", "default")).lower()
    app.setStyle(_default_style if style == "default" else style)

    theme = str(config.get("theme", "system")).lower()
    app.styleHints().setColorScheme(_THEMES.get(theme, Qt.ColorScheme.Dark)) # Default to dark mode if invalid value
