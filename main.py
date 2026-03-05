# Package imports
import sys
from PySide6.QtWidgets import QApplication

# Import 1st page
from Pages.Helpers.Main_Window import MainWindow

if __name__ == "__main__":
    # Set the application style to match the system theme
    app = QApplication(sys.argv)
    sys.argv += ['-platform', 'windows:darkmode=0'] # Default to system theme
    system = system_style = app.style().objectName() # Default to system style
    app.setStyle(system_style)

    # Set application metadata
    app.setApplicationName("TAP")
    app.setOrganizationName("Maple Studios")
    app.setApplicationVersion("1.00")

    # Load the main window
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
# Use "uv run main.py" in the terminal to launch the application for the development environment