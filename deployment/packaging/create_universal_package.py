import os
import shutil
import sys
import subprocess
from pathlib import Path

def create_mac_distribution(source_dir, output_dir):
    """Create a Mac-ready distribution package"""
    
    mac_dist = os.path.join(output_dir, "USTED_Mac_Version")
    if os.path.exists(mac_dist):
        shutil.rmtree(mac_dist)
    os.makedirs(mac_dist)
    
    print("📦 Preparing USTED Mac Distribution...")
    
    # 1. Copy Source Files
    # Exclude build artifacts, git, venv, huge files not needed
    ignore_patterns = shutil.ignore_patterns(
        "__pycache__", ".git", ".venv", "venv", "build", "dist", "*.exe", "*.spec",
        "service_logs", "USTED_*_Distribution", "app_data"
    )
    
    # We need to copy manually to control what goes in
    files_to_copy = [
        "app.py", "db_setup.py", "auto_report_writer.py", "node_config.py", "sync_engine.py",
        "windows_service.py", "service_manager.py", "desktop_app.py", 
        "requirements.txt",
        "icon.png", "icon.ico"
    ]
    
    dirs_to_copy = ["templates", "static", "assets"]
    
    print("   ✓ Copying source files...")
    for f in files_to_copy:
        src = os.path.join(source_dir, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(mac_dist, f))
            
    for d in dirs_to_copy:
        src = os.path.join(source_dir, d)
        if os.path.exists(src):
            shutil.copytree(src, os.path.join(mac_dist, d))

    # 2. Create requirements_mac.txt (exclude pywin32)
    print("   ✓ Creating requirements_mac.txt...")
    mac_reqs = []
    if os.path.exists(os.path.join(source_dir, "requirements.txt")):
        with open(os.path.join(source_dir, "requirements.txt"), 'r') as f:
            for line in f:
                if "pywin32" not in line.lower() and "pyinstaller" not in line.lower():
                    mac_reqs.append(line)
    
    # Add mac specific if needed (usually none for this stack)
    with open(os.path.join(mac_dist, "requirements_mac.txt"), 'w') as f:
        f.writelines(mac_reqs)

    # 3. Create the Launcher Script (.command) - WITH AUTO-START
    print("   ✓ Creating Intelligent Mac Installer...")
    launcher_script = """#!/bin/bash
cd "$(dirname "$0")"

echo "==================================================="
echo "  USTED Counselling System - Setup & Start"
echo "==================================================="

APP_NAME="com.usted.counseling"
PLIST_PATH="$HOME/Library/LaunchAgents/$APP_NAME.plist"
INSTALL_DIR="$HOME/Applications/USTED_Counseling"
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
    pip install --upgrade pip > /dev/null
    pip install -r requirements_mac.txt > /dev/null
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
export USTED_AUTO_OPEN_BROWSER=1
python3 app.py
"""
    
    launcher_path = os.path.join(mac_dist, "INSTALL_AND_RUN.command")
    with open(launcher_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(launcher_script)
        
    # Make executable logic isn't needed here as we are on Windows, user will simple double click or chmod if needed
    
    # 5. Zip it (SINGLE FILE)
    print("   ✓ Zipping Mac Package (Single File)...")
    shutil.make_archive(
        os.path.join(output_dir, "USTED_Mac_Installer"),
        'zip',
        mac_dist
    )
    
    return mac_dist

def main():
    print("="*60)
    print("USTED UNIVERSAL PACKAGER")
    print("="*60)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_root = os.path.join(base_dir, "USTED_Universal_Distribution")
    
    if os.path.exists(dist_root):
        try:
            shutil.rmtree(dist_root)
        except:
            print("⚠️  Warning: Could not clean Previous distribution folder. Please close any open files.")
    
    os.makedirs(dist_root, exist_ok=True)
    
    # --- WINDOWS BUILD ---
    print("\n🖥️  Step 1: Building Windows Executable...")
    try:
        # We call the existing build logic via subprocess to ensure clean state
        subprocess.run([sys.executable, "build_complete_exe.py"], check=True)
        
        # Define Paths
        exe_source = os.path.join(base_dir, "dist", "USTED_Counseling_System.exe")
        win_pkg_dir = os.path.join(dist_root, "USTED_Windows_Installer")
        
        if os.path.exists(win_pkg_dir):
            shutil.rmtree(win_pkg_dir)
        os.makedirs(win_pkg_dir)
        
        if os.path.exists(exe_source):
            # 1. Copy Executable
            shutil.copy2(exe_source, win_pkg_dir)
            print("   ✓ Copied Windows Executable")
            
            # 2. Create Intelligent Batch Installer
            bat_content = r"""@echo off
echo Installing USTED Counseling System...
echo.

:: Create proper directory in Documents
set "INSTALL_DIR=%USERPROFILE%\Documents\USTED_Counseling_System"

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Copy executable
copy /Y "USTED_Counseling_System.exe" "%INSTALL_DIR%\"

:: Create Startup Shortcut logic
set "SHORTCUT_SCRIPT=%TEMP%\create_startup.vbs"
set "STARTUP_DIR=%appdata%\Microsoft\Windows\Start Menu\Programs\Startup"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%SHORTCUT_SCRIPT%"
echo sLinkFile = "%STARTUP_DIR%\USTED System.lnk" >> "%SHORTCUT_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%SHORTCUT_SCRIPT%"
echo oLink.TargetPath = "%INSTALL_DIR%\USTED_Counseling_System.exe" >> "%SHORTCUT_SCRIPT%"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%SHORTCUT_SCRIPT%"
echo oLink.Description = "USTED Counseling System" >> "%SHORTCUT_SCRIPT%"
echo oLink.Save >> "%SHORTCUT_SCRIPT%"

cscript /nologo "%SHORTCUT_SCRIPT%"
del "%SHORTCUT_SCRIPT%"

echo.
echo Installation Complete!
echo application will start automatically when you login.
echo Starting application now...
start "" "%INSTALL_DIR%\AAMUSTED_Counseling_System.exe"
pause
"""
            with open(os.path.join(win_pkg_dir, "INSTALL_AND_RUN.bat"), "w") as f:
                f.write(bat_content)
            print("   ✓ Created INSTALL_AND_RUN.bat")
            
            # 3. Zip Windows Package
            shutil.make_archive(
                os.path.join(dist_root, "USTED_Windows_Installer"),
                'zip',
                win_pkg_dir
            )
            print("   ✅ Windows Installer Zipped.")
            
        else:
            print("❌ Windows Build Missing (EXE not found).")
            
    except subprocess.CalledProcessError:
        print("❌ Windows Build Failed.")
    except Exception as e:
        print(f"❌ Error handling Windows build: {e}")

    # --- MAC BUILD ---
    print("\n🍎 Step 2: Creating Mac Distribution...")
    try:
        mac_dist = create_mac_distribution(base_dir, dist_root)
        print(f"✅ Mac Distribution Created at: {mac_dist}")
    except Exception as e:
        print(f"❌ Error creating Mac distribution: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print(f"🎉 PACKAGING COMPLETE!")
    print(f"Files are located in: {dist_root}")
    print("="*60)
    print("1. Copy 'Windows_Version' to Windows PC -> Run .exe")
    print("2. Copy 'Mac_Version' to iMac -> Run .command")
    print("="*60)

if __name__ == "__main__":
    main()
