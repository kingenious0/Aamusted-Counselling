#!/bin/bash
cd "$(dirname "$0")"

echo "==================================================="
echo "  AAMUSTED Counselling System - Setup & Start"
echo "==================================================="

APP_NAME="com.aamusted.counseling"
PLIST_PATH="$HOME/Library/LaunchAgents/$APP_NAME.plist"
INSTALL_DIR="$HOME/Applications/AAMUSTED_Counseling"
CURRENT_DIR=$(pwd)

# 1. Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo "Please download Python from python.org"
    read -p "Press ENTER to exit..."
    exit 1
fi

# 2. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo "⚙️  Initializing system..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    echo "📦 Installing dependencies (this requires internet)..."
    pip install -r requirements_mac.txt || { echo "❌ Failed to install dependencies. Check your internet connection."; read -p "Press ENTER to exit..." ; exit 1; }
else
    source venv/bin/activate
fi

# 3. Setup Auto-Start (Persistence)
if [ ! -f "$PLIST_PATH" ]; then
    echo "🔄 Configuring Auto-Start..."
    
    # We need to run from the CURRENT location or move it? 
    # User said "Just send one file... double click and everything installs"
    # So we should probably treat this folder as the permanent home or move it.
    # Let's run from HERE to avoid permission/path confusion, assuming user put it in a safe place.
    
    cat << EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$APP_NAME</string>
    <key>ProgramArguments</key>
    <array>
        <string>$CURRENT_DIR/venv/bin/python3</string>
        <string>$CURRENT_DIR/app.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/$APP_NAME.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/$APP_NAME.err</string>
</dict>
</plist>
EOF
    
    # Enable the service
    launchctl bootstrap gui/$(id -u) "$PLIST_PATH" 2>/dev/null || launchctl load "$PLIST_PATH"
    echo "✅ Auto-start enabled! System will restart automatically if PC reboots."
fi

# 4. Launch App
echo "🚀 Starting System..."
echo ""
echo "IMPORTANT: The system is starting."
echo "1. The browser should open automatically."
echo "2. If you see 'Sync failed: No peer IP', go to Admin -> Settings in the app"
echo "   and enter the IP address of the OTHER computer."
echo "3. Default Login Credentials:"
echo "   - Username: admin"
echo "   - Password: Admin123"
echo "   - Username: counsellor"
echo "   - Password: Counsellor123"
echo "   - Username: secretary"
echo "   - Password: Secretary123"
echo ""
echo "4. YOUR IP ADDRESS (Enter this on the Windows machine):"
ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print "   - " $2}'
echo ""

# 3b. Run Database Migration (Fix Schema)
if [ -f "add_sync_columns.py" ]; then
    echo "Running database migration..."
    python3 add_sync_columns.py
fi

export AAMUSTED_AUTO_OPEN_BROWSER=1
python3 app.py
