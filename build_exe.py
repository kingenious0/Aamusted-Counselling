#!/usr/bin/env python3
"""
Build script for creating a standalone executable of the AAMUSTED Counselling Management System
Run this script to create the .exe file for distribution
"""

import subprocess
import os
import shutil
import sys

def build_executable():
    """Build the executable using PyInstaller"""
    
    # Clean previous builds
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    # PyInstaller arguments
    args = [
        'app.py',  # Main script
        '--name=AAMUSTED_Counseling_System',  # Name of the executable
        '--onefile',  # Create a single executable file
        '--windowed',  # Hide console window (use --console for debugging)
        '--icon=icon.ico',  # Icon file (create this if needed)
        '--add-data=templates;templates',  # Include templates folder
        '--add-data=static;static',  # Include static folder with Chart.js
        '--hidden-import=jinja2.ext',  # Include Jinja2 extensions
        '--hidden-import=sqlite3',  # Ensure sqlite3 is included
        '--collect-all=flask',  # Collect all Flask dependencies
        '--collect-all=jinja2',  # Collect all Jinja2 dependencies
        '--collect-all=werkzeug',  # Collect all Werkzeug dependencies
        '--exclude-module=matplotlib',  # Exclude unnecessary modules
        '--exclude-module=numpy',  # Exclude unnecessary modules
        '--clean',  # Clean PyInstaller cache
        '--noconfirm',  # Overwrite output without confirmation
    ]
    
    print("Building AAMUSTED Counselling Management System executable...")
    print("This may take a few minutes...")
    
    try:
        # Use python -m PyInstaller for better compatibility
        cmd = [sys.executable, '-m', 'PyInstaller'] + args
        subprocess.run(cmd, check=True)
        print("\n✅ Build completed successfully!")
        print(f"\nExecutable location: dist\\AAMUSTED_Counseling_System.exe")
        print(f"\nFile size: {os.path.getsize('dist\\AAMUSTED_Counseling_System.exe') / (1024*1024):.1f} MB")
        
        # Create distribution folder
        dist_folder = "AAMUSTED_Counseling_System_Distribution"
        if os.path.exists(dist_folder):
            shutil.rmtree(dist_folder)
        
        os.makedirs(dist_folder)
        
        # Copy executable and documentation
        shutil.copy('dist\\AAMUSTED_Counseling_System.exe', dist_folder)
        shutil.copy('README.md', dist_folder)
        
        # Create database initialization script
        with open(f'{dist_folder}\\Initialize_Database.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('title Initialize AAMUSTED Counselling System\n')
            f.write('echo Initializing database for AAMUSTED Counselling System...\n')
            f.write('echo.\n')
            f.write('echo This will create the counselling.db file\n')
            f.write('echo.\n')
            f.write('pause\n')
            f.write('AAMUSTED_Counseling_System.exe --init-db\n')
            f.write('echo.\n')
            f.write('echo Database initialized successfully!\n')
            f.write('pause\n')
        
        # Create quick start guide
        with open(f'{dist_folder}\\Quick_Start_Guide.txt', 'w') as f:
            f.write('AAMUSTED Counselling Management System\n')
            f.write('Quick Start Guide\n')
            f.write('=' * 40 + '\n\n')
            f.write('1. Double-click "AAMUSTED_Counseling_System.exe"\n')
            f.write('2. Wait for the browser to open automatically\n')
            f.write('3. If browser doesn\'t open, visit: http://localhost:5000\n')
            f.write('4. The system is ready to use!\n\n')
            f.write('First-time setup:\n')
            f.write('- Database will be created automatically\n')
            f.write('- Sample Counsellors are pre-loaded\n')
            f.write('- You can add your own Counsellors through the system\n\n')
            f.write('For detailed instructions, see README.md\n')
        
        print(f"\n📦 Distribution package created: {dist_folder}")
        print("\nFiles included:")
        print("- AAMUSTED_Counseling_System.exe (main application)")
        print("- README.md (complete documentation)")
        print("- Initialize_Database.bat (database setup)")
        print("- Quick_Start_Guide.txt (quick reference)")
        
    except Exception as e:
        print(f"\n❌ Build failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    # Check if PyInstaller is available
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found. Please install it:")
        print("pip install pyinstaller")
        sys.exit(1)
    
    # Build the executable
    success = build_executable()
    
    if success:
        print("\n🎉 AAMUSTED Counselling Management System is ready for distribution!")
    else:
        print("\n💡 Check the error messages above and try again.")
        sys.exit(1)