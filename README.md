# TAP — Teaching Analysis Program

A desktop application for instructors and assessors to structure, time, and export lesson observations in real time.

---

## Features

- **Lesson & subject timers** — A top-level lesson timer runs alongside a per-subject timer. Starting or stopping the lesson timer automatically starts or stops the active subject timer. Switching to a different subject hands the timer off seamlessly.
- **Subject navigator** — A collapsible panel lists all subjects in the current lesson. Subjects can be reordered by drag-and-drop, renamed inline, and deleted via right-click.
- **Markdown note editor** — Each subject has a rich plain-text editor with live Markdown syntax highlighting, bracket auto-pairing, and spell-check.
- **Session types** — Every subject can be tagged with a session type (Lecture, Exercise, Demo, etc.) which is used in the breakdown charts.
- **Lesson breakdown charts** — On export, two charts are generated automatically:
  - *Pie chart* — time distribution across subjects (switches to a legend for 5+ subjects).
  - *Bar chart* — total minutes per session type, with each bar a distinct colour.
  - Charts scale dynamically with the number of subjects/types.
- **Multiple export formats** — HTML, PDF (via wkhtmltopdf), DOCX (via python-docx), and Markdown. All formats include the breakdown charts in a dedicated section at the start of the document.
- **Persistent save/load** — Lessons are stored as `.json` files, preserving all subject titles, content, session types, and elapsed times.
- **Configurable hotkeys** — Key bindings are defined in `config.json` and can be changed without editing source code.

---

## Requirements

- Python 3.12+
- [wkhtmltopdf](https://wkhtmltopdf.org/) (bundled under `Resources/wkhtmltopdf/` for PDF export)

Python dependencies are managed via `uv` (or `pip`):

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

# Install dependencies (recommended: uv)
uv sync

# Or with pip
pip install -r requirements.txt
```

---

## Running

```bash
uv run main.py
# or
python main.py
```

---

## Building a standalone executable

The project uses [cx_Freeze](https://cx-freeze.readthedocs.io/):

```bash
uv run python setup.py build
```

The output is placed in the `build/` directory.

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
| Delete | Right-click a row → *Delete subject* |
| Reset subject timer | Click the **Reset** button on the subject — elapsed time is subtracted from the lesson timer |

### Timers
- The lesson timer and the focused subject timer are always in sync — pausing one pauses the other.
- Resetting the lesson timer also resets all subject timers.
- Resetting an individual subject timer deducts that time from the lesson total.

### Exporting
Go to **File → Export** and choose a format:

| Format | What's included |
|---|---|
| **JSON** | Full lesson data (save/reload) |
| **Markdown** | Lesson notes + chart images saved alongside the `.md` file |
| **HTML** | Self-contained file with embedded charts |
| **PDF** | Formatted document; breakdown charts on their own page |
| **DOCX** | Word document with embedded charts and styled headings |

### Hotkeys (defaults)

| Action | Key |
|---|---|
| New subject | `Ctrl+N` |
| Start / pause lesson timer | `Ctrl+T` |
| Save | `Ctrl+S` |
| Open | `Ctrl+O` |

Hotkeys can be customised in `config.json` under the `"Hotkeys"` key.

---

## Project structure

```
TAP/
├── main.py                   # Entry point
├── pyproject.toml
├── Functions/
│   ├── FileFunctions.py      # Config, paths, logging
│   └── Plotter.py            # Matplotlib/Seaborn chart generation
├── Pages/
│   ├── Helpers/
│   │   ├── Main_Window.py    # Main application controller
│   │   └── Settings_Dialog.py
│   └── UI/                   # Auto-generated PySide6 UI modules
├── Widgets/
│   ├── subject_widget.py     # Per-subject editor + timer widget
│   ├── subject_navigator.py  # Left-panel subject list
│   ├── md_highlighter.py     # Markdown syntax highlighter
│   ├── colour_button.py
│   └── HotKeyLineEdit.py
├── Resources/
│   ├── Icons/
│   └── wkhtmltopdf/          # Bundled wkhtmltopdf binary
└── UI (QtDesigner)/          # Source .ui files
```

---

## License

This project is not currently under an open-source licence. All rights reserved — Alex Kussauer.