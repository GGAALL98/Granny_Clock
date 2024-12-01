#!/bin/bash

# Define variables
INSTALL_DIR="$HOME/grandma_clock"
STARTUP_SCRIPT="$HOME/start_grandma_clock.sh"

# Remove the installation directory and its contents
echo "Removing installation directory..."
rm -rf "$INSTALL_DIR"

# Remove the startup script
if [ -f "$STARTUP_SCRIPT" ]; then
    echo "Removing startup script..."
    rm "$STARTUP_SCRIPT"
fi

# Remove the line from .bashrc
echo "Cleaning up .bashrc..."
sed -i "\|$STARTUP_SCRIPT|d" "$HOME/.bashrc"

echo "Uninstallation complete!"
