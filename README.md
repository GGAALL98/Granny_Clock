# Grandma Clock

<p align="center">
  <img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Linux">
  <img src="https://img.shields.io/badge/mac%20os-000000?style=for-the-badge&logo=apple&logoColor=white" alt="Mac OS">
  <img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/Raspberry%20Pi-A22846?style=for-the-badge&logo=Raspberry%20Pi&logoColor=white" alt="Raspberry Pi">
  <img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" alt="Python">
</p>

<p align="center">
    <img src="https://tokei.rs/b1/github/GGAALL98/Granny_Clock" alt="Total Lines">
</p>

Grandma Clock is a basic clock application designed primarily for 7-inch touch screens. It features a large font for easy readability and serves as a medication reminder and shuffle music player. With Grandma Clock, you can keep track of your medication schedule and enjoy your favorite tunes whenever you want!

## Features
- **Clock Functionality**: Displays the current time in a large, easy-to-read format and provides reminders for your medication schedule.
- **Medication Tracker**: Notifies you when it's time to take your medications, helping you stay on track.
- **Music Player**: Shuffle and play music from your designated music folder at any time.

## Installation (Cross-Platform)

To install Grandma Clock on your system, follow these steps. If you prefer, use the manual installation method.

### Installer Script

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/GGAALL98/Granny_Clock.git
   cd Granny_Clock
   ```

2. **Run the Installer**:
   ```bash
   chmod +x installer.sh  # Make the installer executable
   ./installer.sh          # Run the installer
   ```
   The installer will **automatically detect your package manager** (apt, pacman, dnf) and install all necessary packages, including MPV, copy the application files to `~/grandma_clock`, and create a startup script.

**Application files that will be copied to `~/grandma_clock` include**:
- `main.py`: The main application script.
- `medications.json`: The file for managing your medication schedule.
- `alarm.wav`: The sound file for notifications.
- Any additional resource files (e.g., images or configurations).

### Manual Installation Method

If you're using a different operating system, you'll need to manually install the required packages and set up the application files. This may include:
- **Installing Python 3, PyQt6, and MPV manually**:
    - **Debian/Ubuntu**:
      ```bash
      sudo apt update
      sudo apt install python3 python3-pyqt6 python3-pyqt6.qtmultimedia mpv
      ```
    - **Arch Linux**:
      ```bash
      sudo pacman -S python python-pyqt6 mpv
      ```
    - **Fedora**:
      ```bash
      sudo dnf install python3 python3-qt6 mpv
      ```
    - **Using Pip**:
      ```bash
      pip install PyQt6
      ```

**To manually set up Grandma Clock**:
1. Copy the application files mentioned above to `~/grandma_clock`.

**To auto-start Grandma Clock**, add a line in your `.bashrc` or use any other method suitable for your environment to run the application at login.

## Adding Medications

To set up your medication reminders, you'll need to edit the `medications.json` file located in `~/grandma_clock`. This file allows you to define your medication schedule in a structured format. Here’s how to do it:

1. **Open `medications.json`**: Use a text editor of your choice to edit the file. For example:
   ```bash
   nvim ~/grandma_clock/medications.json
   ```

2. **Edit the JSON Structure**: Replace the contents with your medication schedule. The structure should look like this:
   ```json
   {
       "medications": [
           {"name": "Medication 1", "time": "09:00"},
           {"name": "Medication 2", "time": "15:00"},
           {"name": "Medication 3", "time": "21:00"}
       ]
   }
   ```
   - Modify the `"name"` and `"time"` fields with your actual medication names and times. You can add or remove medication entries as needed.

## Adding Music

To play music with Grandma Clock, you need to have a designated music folder. By default, this folder will be located at `~/grandma_clock/music`. You can add your music files (e.g., MP3, WAV) to this folder. 

1. **Create the Music Directory** (if not created by the installer):
   ```bash
   mkdir -p ~/grandma_clock/music
   ```

2. **Add Your Music Files**: Simply copy or move your audio files into the `~/grandma_clock/music` directory. 

3. **File Formats**: Ensure your music files are in a compatible format, such as MP3 or WAV, so that they can be played using MPV.

## Uninstallation

If you wish to remove Grandma Clock, you can use the provided uninstaller script.

### Uninstallation Steps

1. **Make the uninstaller script executable**:
   ```bash
   chmod +x uninstaller.sh
   ```

2. **Run the uninstaller**:
   ```bash
   ./uninstaller.sh
   ```

This will remove the installation directory, startup script, and clean up your `.bashrc`.

## License

Feel free to edit and modify Grandma Clock to suit your needs, just credit the author GGAALL98 (goby98). The software is licensed under the MIT License.

## Star History

<a href="https://star-history.com/#GGAALL98/Granny_Clock&Timeline">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=GGAALL98/Granny_Clock&type=Timeline&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=GGAALL98/Granny_Clock&type=Timeline" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=GGAALL98/Granny_Clock&type=Timeline" />
 </picture>
</a>
