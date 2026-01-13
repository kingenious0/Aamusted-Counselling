#!/bin/bash

echo "==================================================="
echo "  AAMUSTED Counselling System - Mac Builder"
echo "==================================================="

# Ensure we are in the right directory
cd "$(dirname "$0")"

# Fix for "ProxyError: Cannot connect to proxy" on some Mac systems
export no_proxy='*'

echo "1. Installing Dependencies..."
pip3 install -r requirements.txt
pip3 install pyinstaller

echo "2. Cleaning previous builds..."
rm -rf build dist

echo "3. Building Mac Application..."
# We use a slightly modified command for Mac to avoid icon issues if .ico is Windows-only
# and to ensure windowed mode works.

pyinstaller --noconfirm --clean \
    --name "AAMUSTED_Counseling_System" \
    --add-data "templates:templates" \
    --add-data "static:static" \
    --hidden-import "jinja2.ext" \
    --hidden-import "sqlite3" \
    --hidden-import "requests" \
    --hidden-import "uuid" \
    --hidden-import "json" \
    --hidden-import "node_config" \
    --hidden-import "sync_engine" \
    --hidden-import "apscheduler" \
    --hidden-import "apscheduler.schedulers.background" \
    --collect-all "flask" \
    --collect-all "jinja2" \
    --collect-all "werkzeug" \
    --collect-all "requests" \
    --collect-all "docx" \
    --windowed \
    app.py

echo "==================================================="
echo "  BUILD COMPLETE!"
echo "==================================================="
echo "The application is in dist/AAMUSTED_Counseling_System.app"
