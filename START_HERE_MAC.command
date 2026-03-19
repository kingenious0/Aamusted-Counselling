#!/bin/bash
clear
echo "==================================================="
echo "   AAMUSTED Counselling System - MAC LAUNCHER"
echo "==================================================="
echo

# Move to the script's directory
cd "$(dirname "$0")"

# Start the server and open browser
export USTED_AUTO_OPEN_BROWSER=1
python3 app.py

echo
echo "==================================================="
echo "   System is running! "
echo "==================================================="
echo "To stop the server, press: Ctrl + C"
echo "==================================================="
