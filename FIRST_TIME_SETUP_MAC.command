#!/bin/bash
clear
echo "==================================================="
echo "   AAMUSTED Counselling System - MAC SETUP"
echo "==================================================="
echo

# 1. Check Python
echo "[1/2] Checking Python..."
if ! command -v python3 &> /dev/null
then
    echo "ERROR: Python3 is not installed."
    echo "Please download it from https://www.python.org/"
    exit
fi

# 2. Install dependencies
echo "[2/2] Installing Required Libraries..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo
echo "==================================================="
echo "   SETUP SUCCESSFUL! "
echo "==================================================="
echo "To run the system in the future, just double-click:"
echo "START_HERE_MAC.command"
echo
echo "To install as a PWA (The App):"
echo "1. Run the system and wait for the browser to open."
echo "2. Click the 'Install' icon in the URL bar."
echo "==================================================="
read -p "Press Enter to close..."
