#!/bin/bash

# Define variables
INSTALL_DIR="$HOME/grandma_clock"
MUSIC_DIR="$INSTALL_DIR/music"
SOUND_FILE="$INSTALL_DIR/alarm.wav"
MAIN_PY_FILE="$INSTALL_DIR/main.py"
STARTUP_SCRIPT="$HOME/start_grandma_clock.sh"

# Create the installation directory (if it doesn't already exist)
mkdir -p "$INSTALL_DIR"

# Update the package list and install required packages
echo "Installing Python and necessary packages..."
sudo apt update
sudo apt install -y python3 python3-pyqt6 python3-pyqt6.qtmultimedia python3-pip mpv cage

# Copy application files to the installation directory
echo "Copying application files..."
cp -r ~/grandma_clock/* "$INSTALL_DIR/"

# Check if the music directory exists; if not, create it
if [ ! -d "$MUSIC_DIR" ]; then
    echo "Music directory not found. Creating $MUSIC_DIR..."
    mkdir -p "$MUSIC_DIR"
fi

# Create a startup script in the home directory
echo "Creating startup script..."
cat <<EOF > "$STARTUP_SCRIPT"
#!/bin/bash

# Check if the user is not on SSH
if [ -z "\$SSH_CLIENT" ] && [ -z "\$SSH_TTY" ]; then
    echo "Press 'q' within 3 seconds to cancel launching grandma_clock..."
    
    # Start a background process to read input
    ( read -t 3 -n 1 key && [[ \$key == "q" ]] && exit 1 ) &

    # Save the PID of the background process
    wait \$!

    # If the wait completes without 'q' being pressed
    echo "Launching grandma_clock..."
    cage python3 "$MAIN_PY_FILE"
else
    echo "Running in SSH session, not starting grandma_clock."
fi
EOF

# Make the startup script executable
chmod +x "$STARTUP_SCRIPT"

# Add the startup script to the .bashrc to run on login
if ! grep -q "start_grandma_clock.sh" "$HOME/.bashrc"; then
    echo "Executing startup script on login..."
    echo "$STARTUP_SCRIPT" >> "$HOME/.bashrc"
fi

echo "Setup complete! The grandma_clock application will start automatically after login."
