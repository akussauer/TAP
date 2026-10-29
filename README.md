# TAP — Teaching Analysis Program

A desktop application for instructors and assessors to structure, time, and export lesson observations in real time.

---

## Features

- **Lesson & subject timers** — A top-level lesson timer runs alongside a per-subject timer. Starting or stopping the lesson timer automatically starts or stops the active subject timer. Switching to a different subject hands the timer off seamlessly.
- **Subject navigator** — A panel lists all subjects in the current lesson. Subjects can be reordered by drag-and-drop and deleted via right-click.
- **Markdown note editor** — Each subject has a plain-text editor with live Markdown syntax highlighting, bracket auto-pairing, spell-check, and list editing (see [Writing notes](#writing-notes)).
- **Session types** — Every subject can be tagged with a session type (Lecture, Exercise, Demo, etc.) which is used in the breakdown charts.
- **Lesson breakdown charts** — On export, two charts are generated automatically:
  - *Pie chart* — time distribution across subjects (switches to a legend for 5+ subjects).
  - *Bar chart* — total minutes per session type, with each bar a distinct colour.
  - Charts scale dynamically with the number of subjects/types.
- **Multiple export formats** — HTML, PDF (via wkhtmltopdf), DOCX (via python-docx), and Markdown. All formats include the breakdown charts in a dedicated section at the start of the document.
- **`.tap` lesson files** — Lessons are saved as `.tap` files (SQLite), preserving all subject titles, content, session types, and elapsed times. Older `.json` lessons can still be opened.
- **Autosave & session restore** — The current lesson is continuously backed up, and reopened automatically the next time TAP starts — even after a crash.
- **Live settings** — Theme, style, hotkeys, spell-check language, Markdown colours, and tab size are changed in **Settings** and apply immediately, without restarting.

---

## Requirements

- Python 3.12+
- [wkhtmltopdf](https://wkhtmltopdf.org/) for PDF export — place `wkhtmltopdf.exe` at `Resources/wkhtmltopdf/wkhtmltopdf.exe` (not included in the repository)

Python dependencies are managed via `uv` (see `pyproject.toml`):

```
pyside6
markdown
matplotlib
seaborn
pdfkit
python-docx
pyenchant
platformdirs
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/akussauer/TAP.git
cd TAP

# Install dependencies
uv sync
```

---

## Running

```bash
uv run main.py

# Open a specific lesson
uv run main.py "path/to/lesson.tap"
```

Only one copy of TAP runs at a time. Launching it again (or double-clicking a `.tap` file) brings the open window to the front and opens the file there.

---

## Building

### Standalone executable

The project uses [cx_Freeze](https://cx-freeze.readthedocs.io/):

```bash
uv run python setup.py build
```

The output is placed in the `build/` directory.

### Windows installer

`Inno_setup.iss` is an [Inno Setup](https://jrsoftware.org/isinfo.php) script that packages the build into `TAP_installer.exe`. It also registers `.tap` files so that double-clicking a lesson opens it in TAP.

Update the `Source:` paths in the `[Files]` section and `OutputDir` to match your machine before compiling.

---

## Usage

### Starting a lesson
1. Enter a lesson name in the top bar.
2. Press **Play** (or `Ctrl+T`) to start the lesson timer.
3. The active subject timer starts automatically.

### Managing subjects
| Action | How |
|---|---|
| Add a subject | Click **New Subject** or press `Ctrl+N` |
| Switch subject | Click a row in the left-hand navigator panel |
| Rename | Type in the subject title field |
| Reorder | Drag rows in the navigator |
| Delete | Right-click a row → *Delete* |
| Reset subject timer | Click the **Reset** button on the subject — elapsed time is subtracted from the lesson timer |

### Timers
- The lesson timer and the focused subject timer are always in sync — pausing one pauses the other.
- Resetting the lesson timer also resets all subject timers.
- Resetting an individual subject timer deducts that time from the lesson total.

### Writing notes
The note editor helps with Markdown lists:

| Key | On a list item (`- `, `* `, `+ `, `1. `, `1) `, `- [ ] `) | Elsewhere |
|---|---|---|
| `Enter` | Starts the next item with the same indent — numbers count up, checkboxes start unticked. On an empty item, clears the row instead. | New line |
| `Tab` | Indents the whole line | Inserts spaces |
| `Shift+Tab` | Un-indents the line | Un-indents the line |

- Numbered lists renumber themselves as items are added or indented. Nested lists start at 1.
- With several lines selected, `Tab` / `Shift+Tab` indent or un-indent all of them.
- `Shift+Enter` always inserts a plain new line.

### Saving and opening
| Action | How |
|---|---|
| Save | **File → Save** or `Ctrl+S` — saves to the current `.tap` file, or asks for a location the first time |
| Open | **File → Open** or `Ctrl+O` — opens `.tap` files and legacy `.json` lessons |
| New | **File → New** |

- The title bar shows `•` when the lesson has unsaved changes.
- Saving a lesson opened from `.json` (or one whose file has been moved or deleted) asks for a new `.tap` location rather than overwriting.
- Save and Open dialogs start in the last folder you used.

### Autosave and restore
TAP keeps a backup of the current lesson in its app-data folder (`autosave.tap`). It's updated:
- 2 seconds after any change,
- every 30 seconds while a timer is running,
- when the window is closed.

When TAP starts, it reopens that lesson — still linked to its saved file, with timers paused. Closing TAP therefore never asks to save; your work will be there next time. Choosing **New**, or discarding changes when opening another lesson, replaces the backup.

### Exporting
Go to **File → Export** and choose a format:

| Format | What's included |
|---|---|
| **Markdown** | Lesson notes + chart images saved alongside the `.md` file |
| **HTML** | Self-contained file with embedded charts |
| **PDF** | Formatted document; breakdown charts on their own page |
| **DOCX** | Word document with embedded charts and styled headings |

### Settings
Open **Settings** to change:

| Setting | Notes |
|---|---|
| Theme | Light, Dark, or System (follows Windows) |
| Style | Default (native Windows) or Fusion |
| Spell-check language | English dictionaries (`en_GB`, `en_US`, …) |
| Tab size | Number of spaces per indent (default 4) |
| Markdown colours | A separate colour for headings, bold, italic, strikethrough, list markers, checkboxes, inline code, block quotes, line breaks, links, and horizontal rules |
| Hotkeys | Click a field and press the new key combination |

Changes apply as soon as you click **Save**. **Reset** restores the defaults.

### Hotkeys (defaults)

| Action | Key |
|---|---|
| New subject | `Ctrl+N` |
| Start / pause lesson timer | `Ctrl+T` |
| Save | `Ctrl+S` |
| Open | `Ctrl+O` |

### App data
Settings, logs, and the autosave backup are stored in the user's app-data folder — on Windows, `%LOCALAPPDATA%\MPS\TAP\`:

```
config.json     # Settings
autosave.tap    # Last session backup
Logs/app.log    # Application log
```

---

## Project structure

```
TAP/
├── main.py                   # Entry point (single-instance handling, appearance)
├── pyproject.toml
├── setup.py                  # cx_Freeze build
├── Inno_setup.iss            # Windows installer script
├── Examples/                 # Example lesson (.tap and .json) and exports
├── Functions/
│   ├── Appearance.py         # Theme and style switching
│   ├── FileFunctions.py      # Config, paths, logging
│   ├── LessonStore.py        # .tap (SQLite) and legacy .json lesson files
│   ├── Plotter.py            # Matplotlib/Seaborn chart generation
│   └── SingleInstance.py     # Hands files to an already-running TAP
├── Pages/
│   ├── Helpers/
│   │   ├── Main_Window.py    # Main application controller
│   │   └── Settings_Dialog.py
│   └── UI/                   # Auto-generated PySide6 UI modules
├── Widgets/
│   ├── subject_widget.py     # Per-subject editor + timer widget
│   ├── subject_navigator.py  # Left-panel subject list
│   ├── md_text_edit.py       # Note editor with list continuation and indenting
│   ├── md_highlighter.py     # Markdown syntax highlighter + spell-check
│   ├── colour_button.py
│   └── HotKeyLineEdit.py
├── Resources/
│   ├── Icons/
│   └── wkhtmltopdf/          # wkhtmltopdf binary (add manually)
└── UI (QtDesigner)/          # Source .ui files
```

---

## License

This project is not currently under an open-source licence. All rights reserved — Alex Kussauer.
