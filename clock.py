import os
import json
import subprocess
from PyQt6.QtCore import QTimer, QTime, Qt, QDate
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QListWidget,
    QFrame,
    QListWidgetItem,
    QGroupBox,
)

ALERT_SOUND_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "resources/alert.wav"
)

TRANSLATIONS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "resources/translations/clock.json"
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

class MedicationReminderApp(QWidget):
    def __init__(self, language="en"):
        super().__init__()

        self.translations = load_translations()  # Load translations
        self.language = language  # Set language from argument

        self.init_ui()

        self.medications = self.load_medications()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
        self.update_time()

    def init_ui(self):
        self.setWindowTitle(self.translate("Medication Reminder"))
        self.setGeometry(100, 100, 480, 800)

        # Main layout
        layout = QVBoxLayout()

        font = QFont()
        font.setPointSize(24)

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

        # Sort medications by time
        today_medications.sort(key=lambda med: QTime.fromString(med["time"], "hh:mm"))

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
