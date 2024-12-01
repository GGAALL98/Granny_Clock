from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QListWidget, QListWidgetItem, QGridLayout, QGroupBox, QWidget
from PyQt6.QtGui import QFont
import json
import os
from datetime import datetime

TRANSLATIONS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "resources/translations_editor.json"
)

# Load translations from JSON file
def load_translations():
    with open(TRANSLATIONS_PATH, "r") as file:
        return json.load(file)

class MedicationManager(QDialog):
    def __init__(self, parent, language="en"):
        super().__init__(parent)

        self.parent = parent  # Parent (MedicationReminderApp)

        self.translations = load_translations()  # Load translations
        self.language = language  # Set language from argument
        
        self.medication_file = "medications.json"
        self.load_medications()  # Load medications on initialization

        self.setWindowTitle(self.translate("Medication Manager"))
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()  # Horizontal layout for side-by-side arrangement

        # Left group for Keyboard section
        keyboard_group = QGroupBox(self.translate("Keyboard"), self)
        keyboard_layout = QVBoxLayout()

        # Create keyboard layout
        self.create_keyboard(keyboard_layout)

        keyboard_group.setLayout(keyboard_layout)

        # Right group for App section (Medication Management)
        app_group = QGroupBox(self.translate("Medication Management"), self)
        app_layout = QVBoxLayout()

        # Medication List
        self.med_list_widget = QListWidget(self)
        self.med_list_widget.setFont(QFont("Arial", 12))
        self.refresh_medication_list()  # Initially populate the list
        app_layout.addWidget(self.med_list_widget)

        # Medication Name
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText(self.translate("Medication Name"))
        self.name_input.setFont(QFont("Arial", 12))
        app_layout.addWidget(self.name_input)

        # Controls: Hour, Minute, Day, and Buttons
        control_layout = QVBoxLayout()

        # Time selection: Hour, Minute, and Time Adjust buttons
        time_layout = QHBoxLayout()

        self.hour_input = QComboBox(self)
        self.hour_input.addItems([f"{i:02d}" for i in range(24)])  # Hours 00 to 23
        self.minute_input = QComboBox(self)
        self.minute_input.addItems([f"{i:02d}" for i in range(60)])  # Minutes 00 to 59

        time_adjust_layout = QHBoxLayout()
        self.add_time_button = QPushButton(self.translate("+20 Min"), self)
        self.add_time_button.clicked.connect(lambda: self.adjust_time(20))
        self.subtract_time_button = QPushButton(self.translate("-20 Min"), self)
        self.subtract_time_button.clicked.connect(lambda: self.adjust_time(-20))

        time_adjust_layout.addWidget(self.add_time_button)
        time_adjust_layout.addWidget(self.subtract_time_button)

        time_layout.addWidget(self.hour_input)
        time_layout.addWidget(self.minute_input)
        time_layout.addLayout(time_adjust_layout)

        control_layout.addLayout(time_layout)

        # Day Selection (Default to today)
        self.days_input = QComboBox(self)
        self.days_input.addItems(
            [
                self.translate("Monday"),
                self.translate("Tuesday"),
                self.translate("Wednesday"),
                self.translate("Thursday"),
                self.translate("Friday"),
                self.translate("Saturday"),
                self.translate("Sunday"),
            ]
        )
        today = self.translate(datetime.today().strftime('%A'))
        self.days_input.setCurrentText(today)  # Set default to today
        control_layout.addWidget(self.days_input)

        # Add/Remove Buttons in the same row
        action_buttons_layout = QHBoxLayout()

        self.add_button = QPushButton(self.translate("Add Medication"), self)
        self.add_button.clicked.connect(self.add_medication)
        self.remove_button = QPushButton(self.translate("Remove Medication"), self)
        self.remove_button.clicked.connect(self.remove_medication)

        action_buttons_layout.addWidget(self.add_button)
        action_buttons_layout.addWidget(self.remove_button)

        control_layout.addLayout(action_buttons_layout)

        # Add control layout to the app group layout
        app_layout.addLayout(control_layout)

        app_group.setLayout(app_layout)

        # Add the keyboard group and app group to the main layout (side-by-side)
        layout.addWidget(keyboard_group)
        layout.addWidget(app_group)

        self.setLayout(layout)

    def create_keyboard(self, parent_layout):
        """
        Create and display a keyboard with numbers followed by letters.
        """
        keyboard_layout = QVBoxLayout()

        # Letters section
        letter_layout = QGridLayout()
        letters = self.load_keyboard_layout("letters")  # Load letters from JSON
        for row_idx, row in enumerate(letters):
            for col_idx, letter in enumerate(row):
                button = QPushButton(letter, self)
                button.clicked.connect(lambda _, letter=letter: self.add_to_name(letter))
                button.setFixedSize(80, 80)  # Increase button size
                letter_layout.addWidget(button, row_idx, col_idx)
        keyboard_layout.addLayout(letter_layout)

        parent_layout.addLayout(keyboard_layout)

    def load_keyboard_layout(self, type_of_layout):
        """
        Load the keyboard layout from JSON file.
        Returns a list of rows (list of strings).
        """
        layout = {
            "letters": [
                ["a", "b", "c", "d", "e"],
                ["f", "g", "h", "i", "j"],
                ["k", "l", "m", "n", "o"],
                ["p", "q", "r", "s", "t"],
                ["u", "v", "w", "x", "y"],
                ["z", "1", "2", "3", "4"],
                ["5", "6", "7", "8", "9"] 
            ]
        }
        return layout.get(type_of_layout, [])

    def add_to_name(self, character):
        """
        Add a character to the medication name input.
        """
        current_text = self.name_input.text()
        self.name_input.setText(current_text + character)

    def adjust_time(self, delta):
        """
        Adjust the current time by the given delta in minutes (positive or negative).
        """
        hour = int(self.hour_input.currentText())
        minute = int(self.minute_input.currentText())

        # Adjust time by delta minutes
        minute += delta
        if minute >= 60:
            minute -= 60
            hour += 1
            if hour >= 24:
                hour = 0  # Wrap around to 00:00
        elif minute < 0:
            minute += 60
            hour -= 1
            if hour < 0:
                hour = 23  # Wrap around to 23:59

        # Update the hour and minute dropdowns
        self.hour_input.setCurrentText(f"{hour:02d}")
        self.minute_input.setCurrentText(f"{minute:02d}")

    def refresh_medication_list(self):
        """
        Refresh the list of medications displayed in the UI.
        """
        self.med_list_widget.clear()
        for med in self.medications:
            med_text = f"{med['name']} - {med['time']} ({', '.join([self.translate(day) for day in med['days']])})"
            item = QListWidgetItem(med_text)
            self.med_list_widget.addItem(item)

    def add_medication(self):
                """
                Add a new medication to the list or merge days if the medication already exists.
                """
                name = self.name_input.text().strip()
                hour = self.hour_input.currentText().strip()
                minute = self.minute_input.currentText().strip()
                time = f"{hour}:{minute}"
                day = self.reverse_translate(self.days_input.currentText())  # Translate day to original language
            
                if name and time:
                    # Check if the medication already exists (same name and time)
                    existing_medication = next((med for med in self.medications if med['name'] == name and med['time'] == time), None)
            
                    if existing_medication:
                        # Medication already exists, merge the days
                        if day not in existing_medication['days']:
                            existing_medication['days'].append(day)
                    else:
                        # New medication, no merge needed, just add
                        self.medications.append({"name": name, "time": time, "days": [day]})
            
                    # Save medications and update UI
                    self.save_medications()  # Save after adding/merging
                    self.parent.update_time()  # Ask parent to update UI with new medication list
                    self.refresh_medication_list()  # Refresh the list
            
                    self.name_input.clear()  # Clear the input field after adding/merging

    def remove_medication(self):
        """
        Remove a selected medication from the list.
        """
        selected_item = self.med_list_widget.currentItem()
        if selected_item:
            item_text = selected_item.text()
            name, time = (
                item_text.split(" - ")[0],
                item_text.split(" - ")[1].split(" ")[0],
            )
            self.medications = [
                med
                for med in self.medications
                if not (med["name"] == name and med["time"] == time)
            ]
            self.save_medications()  # Save after removal
            self.parent.load_medications()
            self.parent.update_time()  # Ask parent to update UI after removal
            self.refresh_medication_list()  # Refresh the list

    def load_medications(self):
        """
        Load medications from the JSON file.
        """
        if os.path.exists(self.medication_file):
            with open(self.medication_file, "r") as file:
                data = json.load(file)
                self.medications = data.get("medications", [])
        else:
            self.medications = []

    def save_medications(self):
        """
        Save medications to the JSON file.
        """
        with open(self.medication_file, "w") as file:
            json.dump({"medications": self.medications}, file, indent=4)
    
        self.parent.medications = self.parent.load_medications()
        self.parent.update_time()

    def translate(self, text):
            """Translate the text using the selected language."""
            return self.translations.get(self.language, {}).get(text, text)
            
    def reverse_translate(self, translated_text):
        """Reverse translate the text to the original language."""
        # Search for the translated_text in all language dictionaries
        for lang, translations in self.translations.items():
            # Check if the translated text is in the dictionary for the current language
            for key, value in translations.items():
                if value == translated_text:
                    return key  # Return the original text (key)
        return translated_text  # If no match found, return the original text
