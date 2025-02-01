import os
import subprocess
import json
import requests
import time
from PyQt6.QtCore import QStringListModel
from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListView, QAbstractItemView
from PyQt6.QtGui import QFont


# Define paths
MUSIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources/music/files")
TRANSLATIONS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources/translations/music.json")
RADIO_STATIONS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources/music/radio_stations.json")
RADIO_STATIONS_CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources/music/radio_stations_cache.json")

# Load translations from JSON file
def load_translations():
    with open(TRANSLATIONS_PATH, "r") as file:
        return json.load(file)
        

def fetch_radio_stations_from_radio_browser(country):
    """Fetch radio stations for a specific country from RadioBrowser."""
    url = f"https://de1.api.radio-browser.info/json/stations/bycountry/{country}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # Return list of stations
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stations for {country}: {e}")
        return []

def is_cache_valid():
    """Check if the radio stations cache is valid (not older than a week)."""
    if not os.path.exists(RADIO_STATIONS_CACHE_PATH):
        return False
    
    with open(RADIO_STATIONS_CACHE_PATH, "r") as file:
        cache_data = json.load(file)
    
    last_update = cache_data.get("last_update", 0)
    one_week_in_seconds = 7 * 24 * 60 * 60  # 1 week in seconds
    current_time = time.time()
    
    return current_time - last_update < one_week_in_seconds

def remove_duplicates(stations):
    """Remove duplicates from the list of radio stations based on 'name' and save only necessary fields."""
    seen = set()
    unique_stations = []
    
    for station in stations:
        station_name = station.get('name')
        if station_name and station_name not in seen:
            # Only keep country, name, and url
            filtered_station = {
                "country": station.get("country", ""),
                "name": station_name,
                "url": station.get("url", "")
            }
            unique_stations.append(filtered_station)
            seen.add(station_name)
    
    return unique_stations

def load_radio_stations():
    """Load radio stations from cache or fetch them if the cache is outdated."""
    # Load local radio stations from the RADIO_STATIONS_PATH file
    if os.path.exists(RADIO_STATIONS_PATH):
        with open(RADIO_STATIONS_PATH, "r") as file:
            local_stations = json.load(file)
    else:
        local_stations = {}

    # If cache is valid, load data from the cache
    if is_cache_valid():
        with open(RADIO_STATIONS_CACHE_PATH, "r") as file:
            cached_data = json.load(file)
        return cached_data["stations"]
    
    # Fetch radio stations from RadioBrowser
    countries_to_fetch = ["Israel", "United Kingdom", "United States", "Canada"]
    merged_stations = {}

    # Add RadioBrowser stations to the local stations for each country
    for country in countries_to_fetch:
        stations = fetch_radio_stations_from_radio_browser(country)
        if country not in merged_stations:
            merged_stations[country] = []
        merged_stations[country].extend(stations)
    
    # Add local stations to merged_stations
    for country, stations in local_stations.items():
        if country not in merged_stations:
            merged_stations[country] = []
        merged_stations[country].extend(stations)
    
    # Remove duplicates and keep only necessary fields (country, name, url)
    for country in merged_stations:
        if isinstance(merged_stations[country], list):
            merged_stations[country] = remove_duplicates(merged_stations[country])

    # Sort the stations alphabetically by station name
    for country in merged_stations:
        if isinstance(merged_stations[country], list):
            merged_stations[country].sort(key=lambda station: station.get('name', '').lower())

    # Save the updated stations and the current time to the cache
    with open(RADIO_STATIONS_CACHE_PATH, "w") as file:
        json.dump({
            "stations": merged_stations,
            "last_update": time.time()
        }, file)

    return merged_stations

# Play local music
def play_music(music_files):
    if music_files:
        music_command = ["mpv", "--no-video", "--loop", "--shuffle"] + music_files
        subprocess.Popen(music_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Play radio stream
def play_radio(station_url):
    radio_command = ["mpv", "--no-video", station_url]
    subprocess.Popen(radio_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

class MusicWidget(QWidget):
    def __init__(self, parent=None, language="en"):
        super().__init__(parent)

        self.language = language  # Set language from argument
        self.translations = load_translations()  # Load translations
        self.translations_for_language = self.translations.get(self.language, self.translations["en"])

        # Now that translations are loaded, you can safely call translate
        self.setWindowTitle(self.translate("Music Player"))
        self.setGeometry(100, 100, 480, 800)  # Set window size to 480x800 pixels

        # Main layout
        layout = QVBoxLayout()

        font = QFont()
        font.setPointSize(17)

        # Tabs
        self.tabs = QTabWidget(self)

        # Local music tab
        local_music_tab = QWidget()
        local_music_tab.setFont(font)
        local_music_layout = QVBoxLayout(local_music_tab)

        # Playlist display
        self.playlist_view = QListView(self)
        self.playlist_model = QStringListModel([])
        self.playlist_view.setModel(self.playlist_model)
        local_music_layout.addWidget(self.playlist_view)

        # Play/Pause button for local music
        self.play_pause_button_local = QPushButton(self.translate("Play Music"), self)
        self.play_pause_button_local.clicked.connect(self.toggle_local_music)
        local_music_layout.addWidget(self.play_pause_button_local)

        # Radio tab
        radio_tab = QWidget()
        radio_tab.setFont(font)
        radio_stations = QWidget()  # This is the container for the country and station lists
        radio_layout = QVBoxLayout(radio_tab)
        radio_stations_layout = QHBoxLayout(radio_stations)  # Horizontal layout for country and station lists

        # Vertical split for radio: Countries list and Stations list
        self.radio_stations = load_radio_stations()
        countries = sorted(self.radio_stations.keys())
        self.country_model = QStringListModel(countries)
        self.country_list_view = QListView(self)
        self.country_list_view.setModel(self.country_model)
        self.country_list_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.country_list_view.clicked.connect(self.on_country_selected)

        # Station list for the selected country
        self.station_list_view = QListView(self)
        self.station_model = QStringListModel([])
        self.station_list_view.setModel(self.station_model)
        self.station_list_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Unified Play/Pause button for radio
        self.play_pause_button_radio = QPushButton(self.translate("Play Station"), self)
        self.play_pause_button_radio.clicked.connect(self.play_pause_radio)

        # Add the country and station lists to the radio_stations_layout
        radio_stations_layout.addWidget(self.country_list_view)
        radio_stations_layout.addWidget(self.station_list_view)

        # Add the radio_stations widget (containing the two lists) to the radio_layout
        radio_layout.addWidget(radio_stations)

        # Add the play/pause button to the radio_layout
        radio_layout.addWidget(self.play_pause_button_radio)

        # Add tabs to tab widget
        self.tabs.addTab(local_music_tab, self.translate("Local Music"))
        self.tabs.addTab(radio_tab, self.translate("Radio Stations"))

        # Main layout
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        # State tracking
        self.radio_playing = False
        self.local_music_playing = False
        self.music_files = [f for f in os.listdir(MUSIC_DIR) if f.endswith((".mp3", ".wav", ".flac"))]
        self.music_files.sort()  # Sort the files alphabetically
        self.playlist = self.music_files
        self.current_station_url = None

        # Handle empty music or radio stations
        if not self.music_files and not self.radio_stations:
            self.current_song_label.setText(self.translate("No local music or radio stations available. Please add music files or select radio stations."))
        elif not self.music_files:
            self.tabs.removeTab(0)  # Remove the local music tab if no music files are present
        elif not self.radio_stations:
            self.tabs.removeTab(1)  # Remove the radio tab if no radio stations are present

        # Initialize the playlist view with all songs
        self.update_playlist_view()

    def translate(self, text):
        """Translate the text using the selected language."""
        return self.translations.get(self.language, {}).get(text, text)

    def update_playlist_view(self):
        """Update the playlist view to show the list of upcoming songs."""
        if self.music_files:
            self.playlist_model.setStringList(self.playlist)

    def play_pause_radio(self): #BROKEN, DOES NOT SWITCH
        """Play or pause the selected radio station."""
        if self.radio_playing:
            subprocess.Popen(["pkill", "mpv"])  # Kill the radio stream
            self.play_pause_button_radio.setText(self.translate("Play Station"))
            self.radio_playing = False
            self.play_pause_button_local.setText(self.translate("Play Music"))
        else:
            # If local music is playing, stop it first
            if self.local_music_playing:
                subprocess.Popen(["pkill", "mpv"])  # Kill local music
                self.local_music_playing = False
                self.play_pause_button_local.setText(self.translate("Play Music"))
            
            # Play the radio stream
            if self.current_station_url:
                play_radio(self.current_station_url)
                self.play_pause_button_radio.setText(self.translate("Stop Station"))
                self.radio_playing = True

    def toggle_local_music(self): #BROKEN, DOES NOT SWITCH
        """Toggle between playing and stopping local music."""
        if self.local_music_playing:
            subprocess.Popen(["pkill", "mpv"])  # Kill local music
            self.play_pause_button_local.setText(self.translate("Play Music"))
            self.local_music_playing = False
            self.play_pause_button_radio.setText(self.translate("Play Station"))
        else:
            # If radio is playing, stop it first
            if self.radio_playing:
                subprocess.Popen(["pkill", "mpv"])  # Kill radio
                self.radio_playing = False
                self.play_pause_button_radio.setText(self.translate("Play Station"))
            
            # Play local music
            play_music([os.path.join(MUSIC_DIR, song) for song in self.playlist])
            self.play_pause_button_local.setText(self.translate("Stop Music"))
            self.local_music_playing = True
        
    def on_country_selected(self, index):
        """Update the station list when a country is selected."""
        country = self.country_model.data(index)
        stations = self.radio_stations.get(country, [])
        station_names = [station["name"] for station in stations]
        self.station_model.setStringList(station_names)
    
        # Reset station selection and update current station URL
        self.station_list_view.selectionModel().clearSelection()
        self.current_station_url = None
    
        # Update the station list view to handle selection
        self.station_list_view.clicked.connect(self.on_station_selected)

    def on_station_selected(self, index):
        """Update the current station URL when a station is selected."""
        country = self.country_list_view.selectionModel().currentIndex().data()
        station_name = self.station_model.data(index)
        stations = self.radio_stations.get(country, [])
        station_url = next(station["url"] for station in stations if station["name"] == station_name)
        self.current_station_url = station_url

        if self.radio_playing:
            self.play_pause_button_radio.setText(self.translate("Pause Station"))
        else:
            self.play_pause_button_radio.setText(self.translate("Play Station"))
