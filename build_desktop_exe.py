#!/usr/bin/env python3
"""
Build script for AAMUSTED Counselling Management System - Desktop Edition
Creates a standalone executable for the native desktop application
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_desktop_exe():
    """Build the desktop application executable"""
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=AAMUSTED_Desktop_Counselling_System',
        '--icon=icon.ico',
        '--add-data=counseling.db;.',  # Include database
        'desktop_app.py'
    ]
    
    print("Building desktop executable...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Desktop executable built successfully!")
        
        # Create distribution folder
        dist_folder = "AAMUSTED_Desktop_Counselling_System_Distribution"
        if os.path.exists(dist_folder):
            shutil.rmtree(dist_folder)
        
        os.makedirs(dist_folder)
        
        # Copy executable
        exe_name = "AAMUSTED_Desktop_Counselling_System.exe"
        shutil.copy2(f"dist/{exe_name}", f"{dist_folder}/{exe_name}")
        
        # Create README for desktop version
        readme_content = """# AAMUSTED Counselling Management System - Desktop Edition

## Quick Start
1. Run `AAMUSTED_Desktop_Counselling_System.exe`
2. The application will open as a native desktop window
3. No browser required - works like WhatsApp, Microsoft Word, etc.

## Features
- Native desktop interface (no browser needed)
- Student management
- Appointment scheduling
- Dashboard with statistics
- Modern, responsive UI

## System Requirements
- Windows 10 or later
- No additional software required

## Database
- Uses `counseling.db` in the same folder
- Database is created automatically on first run

## Troubleshooting
- If the application doesn't start, ensure all files are in the same folder
- Database will be created automatically if missing
"""
        
        with open(f"{dist_folder}/README.md", "w") as f:
            f.write(readme_content)
        
        print(f"📁 Distribution package created: {dist_folder}")
        print(f"📊 Executable size: {os.path.getsize(f'{dist_folder}/{exe_name}'):,} bytes")
        
    else:
        print("❌ Build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

if __name__ == "__main__":
    build_desktop_exe()