import sys
import argparse
import json
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
from music import MusicWidget

# Load translations from JSON file
TRANSLATIONS_PATH = "resources/translations/main.json"

def load_translations():
    """Load translations from JSON file."""
    with open(TRANSLATIONS_PATH, "r") as file:
        return json.load(file)

class TranslatableWidget(QWidget):
    """Base class for widgets that support translations."""
    def __init__(self, language="en", parent=None):
        super().__init__(parent)
        self.language = language
        self.translations = load_translations()
    
    def translate(self, text):
        """Translate the text using the selected language."""
        return self.translations.get(self.language, {}).get(text, text)

    def reverse_translate(self, translated_text):
        """Reverse translate the text to the original language."""
        for lang, translations in self.translations.items():
            for key, value in translations.items():
                if value == translated_text:
                    return key
        return translated_text


class NewsWidget(TranslatableWidget):
    """A placeholder widget for the News tab."""
    def __init__(self, language="en", parent=None):
        super().__init__(language, parent)
        layout = QVBoxLayout(self)
        label_text = self.translate("news_placeholder")
        label = QLabel(label_text, self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)


class CreditsWidget(TranslatableWidget):
    """A simple widget that displays credits."""
    def __init__(self, language="en", parent=None):
        super().__init__(language, parent)
        layout = QVBoxLayout(self)
        credits_text =  """
        Granny's Clock, Meds, Music & More
        
        Developed by Goby
        Special thanks to all the contributors
        Open Source Project under the NO License, do whatever you want, just credit the original devs
        
        
        GitHub Project URL: https://github.com/GGAALL98/Granny_Clock
        
        This application uses RadioBrowser API (https://www.radio-browser.info/).
        The RadioBrowser API provides access to a vast collection of radio stations, and we thank them for their free service.
        """
        label = QLabel(credits_text, self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll = QScrollArea(self)
        scroll.setWidget(label)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self, language="en"):
        super().__init__()
        self.language = language
        self.setWindowTitle("Granny's Clock, Meds, Music & More")
        self.resize(800, 800)

        # Create a QTabWidget and place the tabs at the bottom.
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.South)

        # --- Tab 1: Clock ---
        self.clock_tab = MedicationReminderApp(language=self.language)
        self.tabs.addTab(self.clock_tab, self.translate("Clock"))

        # --- Tab 2: News ---
        self.news_tab = NewsWidget(language=self.language)
        self.tabs.addTab(self.news_tab, self.translate("News"))

        # --- Tab 3: Music ---
        self.music_tab = MusicWidget(language=self.language)  # Add the MusicWidget here
        self.tabs.addTab(self.music_tab, self.translate("Music"))

        # --- Tab 4: Editor ---
        self.editor_tab = MedicationManager(self.clock_tab, language=self.language)
        self.editor_tab.setWindowFlags(Qt.WindowType.Widget)
        self.tabs.addTab(self.editor_tab, self.translate("Editor"))

        # --- Tab 5: Credits ---
        self.credits_tab = CreditsWidget(language=self.language)
        self.tabs.addTab(self.credits_tab, self.translate("Credits"))

        # Set the QTabWidget as the central widget.
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)

    def translate(self, text):
        """Translate the text using the selected language."""
        return load_translations().get(self.language, {}).get(text, text)


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Granny's Clock, Meds, Music & More App")
    parser.add_argument(
        "--lang",
        default="en",
        help="Language code for the app (e.g., 'en', 'es', 'fr')",
    )
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    window = MainWindow(language=args.lang)
    window.show()
    sys.exit(app.exec())
