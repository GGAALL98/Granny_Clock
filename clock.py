import sys
import os
import json
import random
import subprocess
import argparse
from PyQt6.QtCore import QTimer, QTime, Qt, QDate
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QListWidget,
    QFrame,
    QListWidgetItem,
    QGroupBox,
)

from medication_manager import MedicationManager

# Define the music directory and alert sound path
MUSIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources/music")
ALERT_SOUND_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "resources/alert.wav"
)
TRANSLATIONS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "resources/translations.json"
)

# Load translations from JSON file
def load_translations():
    with open(TRANSLATIONS_PATH, "r") as file:
        return json.load(file)

# Play alert sound
def play_alert_sound():
    if os.path.exists(ALERT_SOUND_PATH):
        subprocess.Popen(
            ["mpv", "--no-video", ALERT_SOUND_PATH],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        print("Alert sound file not found!")

# Play music
def play_music():
    music_files = [f for f in os.listdir(MUSIC_DIR) if f.endswith((".mp3", ".wav"))]
    if music_files:
        random.shuffle(music_files)  # Shuffle the playlist
        music_command = ["mpv", "--no-video", "--loop", "--shuffle"] + [
            os.path.join(MUSIC_DIR, f) for f in music_files
        ]
        subprocess.Popen(
            music_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    else:
        print("No music files found!")

class MedicationReminderApp(QWidget):
    def __init__(self, language="en"):
        super().__init__()

        self.translations = load_translations()  # Load translations
        self.language = language  # Set language from argument

        self.dark_mode = False  # Default to light mode

        self.init_ui()

        self.medications = self.load_medications()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
        self.update_time()

        # Set up an auto theme switch timer to check the time every minute
        self.theme_timer = QTimer(self)
        self.theme_timer.timeout.connect(self.auto_toggle_theme)
        self.theme_timer.start(60000)  # Check every minute

        self.medications_editor = MedicationManager(self, language)

    def init_ui(self):
        self.setWindowTitle(self.translate("Medication Reminder"))
        self.setGeometry(100, 100, 480, 800)
        self.setStyleSheet("background-color: white; color: black;")  # Default Light Theme

        # Main layout
        layout = QVBoxLayout()

        font = QFont()
        font.setPointSize(24)

        # Top-left editor button (removed the divider from this layout)
        top_left_layout = QHBoxLayout()
        self.editor_button = QPushButton(self.translate("Editor"), self)
        self.editor_button.setFont(font)
        self.editor_button.clicked.connect(self.open_medication_editor)
        top_left_layout.addWidget(self.editor_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(top_left_layout)

        # Top section for Time and Date
        top_layout = QVBoxLayout()
        self.time_label = QLabel(self.translate("Current Time: --:--:--"))
        self.full_date_label = QLabel(self.translate("Date: --/--/----"))

        # Set larger fonts for time and date
        self.full_date_label.setFont(font)
        clock_font = QFont()
        clock_font.setPointSize(55)
        self.time_label.setFont(clock_font)

        # Center the time and date
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.full_date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top_layout.addWidget(self.time_label)
        top_layout.addWidget(self.full_date_label)

        layout.addLayout(top_layout)

        # Divider Line after the time and date
        divider2 = QFrame(self)
        divider2.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(divider2)

        # Middle section for Medications
        meds_layout = QHBoxLayout()

        # Create Group Boxes for Future and Past Medications
        list_font = QFont()
        list_font.setPointSize(17)
        self.med_list_widget_future = QListWidget(self)
        self.med_list_widget_future.setFont(list_font)
        self.med_list_widget_past = QListWidget(self)
        self.med_list_widget_past.setFont(list_font)

        # Group for Future Medications
        future_group = QGroupBox(self)
        future_group.setStyleSheet("QGroupBox { margin: 0px; border: none; padding: 0px; }")
        future_layout = QVBoxLayout()
        future_title = QLabel(self.translate("Future Medications"), self)
        future_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        future_title.setFont(QFont(future_title.font().family(), 14, QFont.Weight.Bold))
        future_layout.addWidget(future_title)
        future_layout.addWidget(self.med_list_widget_future)
        future_group.setLayout(future_layout)

        # Group for Past Medications
        past_group = QGroupBox(self)
        past_group.setStyleSheet("QGroupBox { margin: 0px; border: none; padding: 0px; }")
        past_layout = QVBoxLayout()
        past_title = QLabel(self.translate("Past Medications"), self)
        past_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        past_title.setFont(QFont(past_title.font().family(), 14, QFont.Weight.Bold))
        past_layout.addWidget(past_title)
        past_layout.addWidget(self.med_list_widget_past)
        past_group.setLayout(past_layout)

        meds_layout.addWidget(future_group)
        meds_layout.addWidget(past_group)

        layout.addLayout(meds_layout)

        # Timer for next medication
        self.countdown_label = QLabel(self.translate("Next medication in: --:--:--"))
        self.countdown_label.setFont(font)
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.countdown_label)

        # Divider Line
        divider3 = QFrame(self)
        divider3.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(divider3)

        # Bottom section for Controls
        button_layout = QHBoxLayout()
        self.play_music_button = QPushButton(self.translate("Play Music"), self)
        self.play_music_button.clicked.connect(play_music)
        self.play_music_button.setFont(font)
        self.theme_toggle_button = QPushButton(self.translate("Toggle Dark Mode"), self)
        self.theme_toggle_button.clicked.connect(self.toggle_theme)
        self.theme_toggle_button.setFont(font)

        button_layout.addWidget(self.play_music_button)
        button_layout.addWidget(self.theme_toggle_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    # Load medications from JSON file
    def load_medications(self):
        with open("medications.json", "r") as file:
            data = json.load(file)
        return data["medications"]

    def translate(self, text):
        """Translate the text using the selected language."""
        return self.translations.get(self.language, {}).get(text, text)

    def update_time(self):
        current_time = QTime.currentTime().toString("hh:mm:ss")
        current_date = QDate.currentDate().toString("MM/dd/yyyy")
        self.time_label.setText(f"{current_time}")
        self.full_date_label.setText(f"{current_date}")

        # Current time and day
        current_day = QDate.currentDate().toString("dddd").lower()
        today_medications = [
            med
            for med in self.medications
            if any(day.lower() == current_day for day in med["days"])
        ]

        self.med_list_widget_future.clear()
        self.med_list_widget_past.clear()

        next_medication_time = None
        for med in today_medications:
            med_time = QTime.fromString(med["time"], "hh:mm")
            item_text = f"{med['name']} - {med['time']}"
            item = QListWidgetItem(item_text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if med_time > QTime.currentTime():
                self.med_list_widget_future.addItem(item)
                if not next_medication_time or med_time < next_medication_time:
                    next_medication_time = med_time
            else:
                item_text = f"{med['name']}"
                item = QListWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.med_list_widget_past.addItem(item)

        # Countdown to next medication
        if next_medication_time:
            remaining_time = QTime.currentTime().secsTo(next_medication_time)
            if remaining_time > 0:
                hours, remainder = divmod(remaining_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                self.countdown_label.setText(
                    f"{self.translate('Next medication in:')} {hours:02}:{minutes:02}:{seconds:02}"
                )
            else:
                play_alert_sound()
                self.countdown_label.setText(
                    f"{self.translate('Next medication in:')} --:--:--"
                )

    def toggle_theme(self):
        if self.dark_mode:
            self.setStyleSheet("background-color: white; color: black;")
            self.theme_toggle_button.setText(self.translate("Toggle Dark Mode"))
        else:
            self.setStyleSheet("background-color: black; color: white;")
            self.theme_toggle_button.setText(self.translate("Toggle Light Mode"))
        self.dark_mode = not self.dark_mode

    def auto_toggle_theme(self):
        current_time = QTime.currentTime()
        if current_time >= QTime(18, 0) or current_time < QTime(7, 0):
            if not self.dark_mode:
                self.toggle_theme()
        else:
            if self.dark_mode:
                self.toggle_theme()

    def open_medication_editor(self):
        """Open the editor window when the button is clicked."""
        self.medications_editor.exec()  # Show the popup as a modal dialog


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Medication Reminder App")
    parser.add_argument(
        "--lang",
        default="en",
        help="Language code for the app (e.g., 'en', 'es', 'fr')",
    )
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = MedicationReminderApp(language=args.lang)
    window.show()
    sys.exit(app.exec())
