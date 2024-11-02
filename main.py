#!/usr/bin/env python3
import os
import sys
import json
import random
import subprocess
from PyQt6.QtCore import Qt, QTimer, QTime, QDateTime
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QHBoxLayout
from PyQt6.QtGui import QFont, QPalette, QColor
from datetime import datetime, timedelta

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
music_dir = os.path.join(script_dir, "music")
alert_sound = os.path.join(script_dir, "alert.wav")

# Global variables
is_playing = False
music_process = None
notified_meds = set()
current_theme = 'light'  # Default theme
medication_status = {}  # Track medication completion status

# Load medication reminders from JSON
def load_medications():
    try:
        with open("medications.json", "r", encoding="utf-8") as file:
            meds = json.load(file)
            return meds.get("medications", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Main Window Class
class MedicationReminderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("תזכורת תרופות")
        self.setGeometry(100, 100, 400, 600)
        
        # Load medications
        self.medications = load_medications()
        
        # Initialize medication status
        for med in self.medications:
            medication_status[med["time"]] = False
        
        # Create UI Elements
        self.create_widgets()
        self.create_layout()
        
        # Timers
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)
        
        # Update initial display
        self.update_display()
    
    def create_widgets(self):
        # Display current date and time
        self.date_label = QLabel()
        self.date_label.setFont(QFont("Arial", 40, QFont.Weight.Bold))
        
        # Clock label
        self.clock_label = QLabel()
        self.clock_label.setFont(QFont("Arial", 64, QFont.Weight.Bold))
        
        # Countdown display for the next medication
        self.countdown_label = QLabel("זמן לתרופה הבאה: ")
        self.countdown_label.setFont(QFont("Arial", 20))
        
        # Medications display
        self.medication_labels = []
        self.display_medications()

        # Play music button
        self.play_button = QPushButton("נגן מוזיקה")
        self.play_button.setFont(QFont("Arial", 20))
        self.play_button.setFixedHeight(60)
        self.play_button.clicked.connect(self.toggle_music)
        
        # Theme toggle button
        self.theme_button = QPushButton("מעבר למצב כהה")
        self.theme_button.setFont(QFont("Arial", 20))
        self.theme_button.setFixedHeight(60)
        self.theme_button.clicked.connect(self.toggle_theme)

        # Apply theme on startup
        self.apply_theme()

    def create_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.date_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.clock_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.countdown_label, alignment=Qt.AlignmentFlag.AlignCenter)  # Add countdown label
        
        # Add medication labels to layout
        for label in self.medication_labels:
            layout.addWidget(label)
        
        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.theme_button)
        
        layout.addLayout(button_layout)  # Add button layout to main layout
        self.setLayout(layout)

    def display_medications(self):
        self.medication_labels.clear()  # Clear existing labels
        current_time = QTime.currentTime()
        cutoff_time = current_time.addSecs(-3600)  # 1 hour before current time
        
        for med in self.medications:
            med_time = QTime.fromString(med["time"], "HH:mm")
            if med_time > cutoff_time:  # Only display medications in the future
                label = QLabel(f"{med['name']} - {med['time']}")
                label.setFont(QFont("Arial", 20))
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("padding: 10px;")
                self.medication_labels.append(label)

    def update_display(self):
        # Update date and time display
        current_datetime = QDateTime.currentDateTime()
        date_str = datetime.now().strftime("%A, %d %B %Y")
        hebrew_months = {
            "January": "ינואר",
            "February": "פברואר",
            "March": "מרץ",
            "April": "אפריל",
            "May": "מאי",
            "June": "יוני",
            "July": "יולי",
            "August": "אוגוסט",
            "September": "ספטמבר",
            "October": "אוקטובר",
            "November": "נובמבר",
            "December": "דצמבר",
        }
        hebrew_days = {
            "Monday": "שני",
            "Tuesday": "שלישי",
            "Wednesday": "רביעי",
            "Thursday": "חמישי",
            "Friday": "שישי",
            "Saturday": "שבת",
            "Sunday": "ראשון",
        }

        # Translate to Hebrew
        for eng_day, heb_day in hebrew_days.items():
            date_str = date_str.replace(eng_day, heb_day)

        for eng_month, heb_month in hebrew_months.items():
            date_str = date_str.replace(eng_month, heb_month)

        self.date_label.setText(date_str)

        # Update the clock label
        time_str = current_datetime.toString("HH:mm:ss")
        self.clock_label.setText(time_str)  # Update the clock label

        # Check if medication time has arrived
        self.check_medication_alerts(current_datetime.time().toString("HH:mm"))

        # Update countdown for next medication
        self.update_countdown(current_datetime.time())

        # Reset medications at midnight
        if current_datetime.time() == QTime(0, 0):
            self.reset_medications()

    def check_medication_alerts(self, current_time):
        for med in self.medications:
            if med["time"] == current_time:
                if not medication_status[med["time"]]:  # If not taken
                    self.play_alert_sound()
                medication_status[med["time"]] = True  # Mark as taken
                self.update_medication_display()

    def update_medication_display(self):
        for index, med in enumerate(self.medications):
            if medication_status[med["time"]]:
                self.medication_labels[index].setStyleSheet("color: white; background-color: green; padding: 10px;")  # Mark as finished
            else:
                self.medication_labels[index].setStyleSheet("color: black; background-color: white; padding: 10px;")  # Default style

    def update_countdown(self, current_time):
        next_time = None
        for med in self.medications:
            med_time = QTime.fromString(med["time"], "HH:mm")
            if med_time > current_time and (next_time is None or med_time < next_time):
                next_time = med_time
        
        if next_time:
            time_diff = QTime.currentTime().secsTo(next_time)
            hours, remainder = divmod(time_diff, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.countdown_label.setText(f"זמן לתרופה הבאה: {hours} שעות {minutes} דקות {seconds} שניות")
        else:
            self.countdown_label.setText("אין תרופות נוספות היום.")
    
    def reset_medications(self):
        for med in self.medications:
            medication_status[med["time"]] = False  # Reset medication status
        self.update_medication_display()

    def play_alert_sound(self):
        if os.path.exists(alert_sound):
            subprocess.Popen(['mpv', '--no-video', alert_sound], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print("Alert sound file not found!")
    
    def toggle_music(self):
        global is_playing, music_process
        if is_playing:
            if music_process:
                music_process.terminate()
                music_process = None
            self.play_button.setText("נגן מוזיקה")
            is_playing = False
        else:
            music_files = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.wav'))]
            if music_files:
                random.shuffle(music_files)  # Shuffle music files
                # Play all files in the folder sequentially
                music_command = ['mpv', '--no-video', '--loop', '--shuffle'] + [os.path.join(music_dir, f) for f in music_files]
                music_process = subprocess.Popen(music_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.play_button.setText("עצור מוזיקה")
                is_playing = True
            else:
                QMessageBox.warning(self, "שגיאה", "אין קבצי מוזיקה בתיקייה.")

    def toggle_theme(self):
        global current_theme
        palette = self.palette()
        if current_theme == 'light':
            current_theme = 'dark'
            palette.setColor(QPalette.ColorRole.Window, QColor(40, 40, 40))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
            self.theme_button.setText("מעבר למצב בהיר")
        else:
            current_theme = 'light'
            palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
            self.theme_button.setText("מעבר למצב כהה")
        
        self.setPalette(palette)

    def apply_theme(self):
        # Apply the current theme at startup
        palette = self.palette()
        if current_theme == 'dark':
            palette.setColor(QPalette.ColorRole.Window, QColor(40, 40, 40))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
            self.theme_button.setText("מעבר למצב בהיר")
        else:
            palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
            self.theme_button.setText("מעבר למצב כהה")
        
        self.setPalette(palette)

# Main execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MedicationReminderApp()
    window.show()
    sys.exit(app.exec())

