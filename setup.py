from cx_Freeze import setup, Executable
import sys

build_options = {
    'packages': [
        "PySide6.QtCore",
        "PySide6.QtGui", 
        "PySide6.QtWidgets",
        "PySide6.QtNetwork", # QLocalServer/QLocalSocket keep TAP to a single instance
        "sqlite3", # .tap lesson files are SQLite databases
        "seaborn",
        "matplotlib",
        "platformdirs",
        "pdfkit",
        "markdown",
        "enchant", # pyenchant is a dependency of markdown-it-py, which is used for spellchecking in the Notes page
        "docx" # python-docx is used for DOCX report generation
    ],
    'excludes': ['tkinter'],
    'include_files': [
        ('Resources/', 'Resources/')
    ]
}

# GUI applications require a different base on Windows (the default is for a console application).
if sys.platform == 'win32':
    base = 'Win32GUI'
elif sys.platform == 'darwin':
    base = 'Console'
else:
    base = None

executables = [
    Executable(
        'main.py',
        base=base,
        target_name='TAP.exe',
        icon="Resources/Icons/write.ico",
        shortcut_name="TAP"
    )
]

setup(
    name='TAP',
    version='1.00',
    description='A program designed for analyzing teaching sessions and generating reports.',
    author='Alex Kussauer',
    author_email='akussauer@gmail.com',
    options={'build_exe': build_options},
    executables=executables
)

# Run with "uv run python setup.py build"
# py2app needs to be removed for the build to work