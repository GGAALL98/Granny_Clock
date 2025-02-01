import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QLabel,
    QScrollArea
)
from PyQt6.QtCore import Qt

from clock import MedicationReminderApp
from medication_manager import MedicationManager


class NewsWidget(QWidget):
    """A placeholder widget for the News tab."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        # Here you might later add a QScrollArea with news content.
        label = QLabel("News and updates will appear here.\n(Coming soon!)", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)


class CreditsWidget(QWidget):
    """A simple widget that displays credits."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        credits_text = (
            "Granny's Clock, Meds, Music & More\n\n"
            "Developed by Your Name\n"
            "Special thanks to all the contributors\n"
            "© 2025 All rights reserved."
        )
        label = QLabel(credits_text, self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # If the credits text is long, you can place it inside a scroll area.
        scroll = QScrollArea(self)
        scroll.setWidget(label)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self, language="en"):
        super().__init__()
        self.setWindowTitle("Granny's Clock, Meds, Music & More")
        self.resize(800, 800)

        # Create a QTabWidget and place the tabs at the bottom.
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.South)

        # --- Tab 1: Clock ---
        # Use your MedicationReminderApp as the clock tab.
        self.clock_tab = MedicationReminderApp(language=language)
        self.tabs.addTab(self.clock_tab, "Clock")

        # --- Tab 2: News ---
        self.news_tab = NewsWidget()
        self.tabs.addTab(self.news_tab, "News")

        # --- Tab 3: Editor ---
        # For the editor, we use MedicationManager. Since it was originally a QDialog,
        # change its window flags so it acts as a normal widget.
        self.editor_tab = MedicationManager(self.clock_tab, language=language)
        self.editor_tab.setWindowFlags(Qt.WindowType.Widget)
        self.tabs.addTab(self.editor_tab, "Editor")

        # --- Tab 4: Credits ---
        self.credits_tab = CreditsWidget()
        self.tabs.addTab(self.credits_tab, "Credits")

        # Set the QTabWidget as the central widget.
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(language="en")
    window.show()
    sys.exit(app.exec())
