#!/bin/bash
cd "$(dirname "$0")"

echo "==================================================="
echo "  USTED Counselling System - Setup & Start (Mac)"
echo "==================================================="

APP_NAME="com.aamusted.counseling"
PLIST_PATH="$HOME/Library/LaunchAgents/$APP_NAME.plist"
CURRENT_DIR=$(pwd)

# ─── 1. Check for Python 3 ───────────────────────────────────────────────────
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "❌  Python 3 is not installed."
    echo ""
    echo "Please download and install Python from:"
    echo "   https://www.python.org/downloads/"
    echo ""
    read -p "Press ENTER to exit..."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "✅  Found: $PYTHON_VERSION"

# ─── 2. Setup Virtual Environment ───────────────────────────────────────────
if [ ! -d "venv" ]; then
    echo ""
    echo "⚙️   First-time setup: creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip -q
    echo "📦  Installing dependencies (requires internet)..."
    pip install -r requirements_mac.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌  Failed to install dependencies."
        echo "    Please check your internet connection and try again."
        read -p "Press ENTER to exit..."
        exit 1
    fi
    echo "✅  Dependencies installed."
else
    source venv/bin/activate
fi

# ─── 3. Configure Auto-Start (LaunchAgent) ───────────────────────────────────
if [ ! -f "$PLIST_PATH" ]; then
    echo ""
    echo "🔄  Configuring auto-start on login..."
    mkdir -p "$HOME/Library/LaunchAgents"

    cat <<EOF > "$PLIST_PATH"
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
    <key>EnvironmentVariables</key>
    <dict>
        <key>AAMUSTED_AUTO_OPEN_BROWSER</key>
        <string>1</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/$APP_NAME.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/$APP_NAME.err</string>
    <key>WorkingDirectory</key>
    <string>$CURRENT_DIR</string>
</dict>
</plist>
EOF

    launchctl bootstrap gui/$(id -u) "$PLIST_PATH" 2>/dev/null || launchctl load "$PLIST_PATH"
    echo "✅  Auto-start enabled. System will launch automatically on login."
fi

# ─── 4. Print Startup Information ────────────────────────────────────────────
echo ""
echo "==================================================="
echo "  🚀  USTED Counselling System is starting..."
echo "==================================================="
echo ""
echo "  📖  Default Login Credentials:"
echo "      Admin      →  admin       / Admin123"
echo "      Counsellor →  counsellor  / Counsellor123"
echo "      Secretary  →  secretary   / Secretary123"
echo ""
echo "  🌐  The browser will open automatically."
echo "      If it doesn't, visit: http://127.0.0.1:5000"
echo ""
echo "  🔗  YOUR IP ADDRESS (enter this on the partner machine):"
ifconfig 2>/dev/null | grep "inet " | grep -v 127.0.0.1 | awk '{print "      " $2}'
echo ""
echo "  ℹ️   If you see 'Sync failed: No peer IP', go to:"
echo "      Admin → Settings → enter the other machine's IP."
echo ""
echo "==================================================="
echo ""

# ─── 5. Launch Application ───────────────────────────────────────────────────
export AAMUSTED_AUTO_OPEN_BROWSER=1
python3 app.py
