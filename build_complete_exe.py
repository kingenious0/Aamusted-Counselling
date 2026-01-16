#!/usr/bin/env python3
"""
COMPLETE Build Script for AAMUSTED Counselling Management System
Creates a standalone executable with ALL features included.
This script ensures EVERYTHING works in the final EXE.
"""

import PyInstaller.__main__
import os
import shutil
import sys
from pathlib import Path
import traceback

def check_dependencies():
    """Check if all required packages are installed"""
    required = ['PyInstaller', 'flask', 'jinja2', 'werkzeug']
    missing = []
    
    for package in required:
        try:
            if package == 'PyInstaller':
                __import__('PyInstaller')
            else:
                __import__(package.lower())
        except ImportError:
            missing.append(package)
    
    # Check for optional but important packages
    optional_important = {
        'python-docx': 'docx',
        'APScheduler': 'apscheduler'
    }
    
    missing_optional = []
    for package_name, import_name in optional_important.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_optional.append(package_name)
    
    if missing:
        print("[X] Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nInstall with: pip install " + " ".join(missing))
        return False
    
    if missing_optional:
        print("[!] Missing optional packages (features may not work):")
        for pkg in missing_optional:
            print(f"   - {pkg}")
        print("\nRecommended: pip install " + " ".join(missing_optional))
        # Skipping input check for automation
        # response = input("\nContinue anyway? (y/n): ")
        # if response.lower() != 'y':
        #     return False
    
    return True

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def build_complete_executable():
    """Build the complete executable with all features"""
    
    print("Starting build...")
    print("=" * 60)
    print("AAMUSTED COUNSELING SYSTEM - COMPLETE BUILD")
    print("=" * 60)
    print("\n[+] Building executable with ALL features included...")
    print("[.] This may take 3-5 minutes, please wait...\n")
    
    # Clean previous builds
    print("[.] Cleaning previous builds...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   [OK] Cleaned {folder}/")
    
    # Prepare data files
    datas = []
    
    # Templates folder
    if os.path.exists('templates'):
        datas.append('templates;templates')
        print(f"   [OK] Added templates/ ({len(list(Path('templates').glob('*.html')))} files)")
    
    # Static folder (CSS, JS, fonts)
    if os.path.exists('static'):
        datas.append('static;static')
        print(f"   [OK] Added static/ folder")
    
    # Logo file for reports
    if os.path.exists('aamusted system_logo.png'):
        datas.append('aamusted system_logo.png;.')
        print(f"   [OK] Added logo file")
    
    # Icon file
    icon_file = 'icon.ico' if os.path.exists('icon.ico') else None
    
    # Hidden imports - ALL modules needed
    hidden_imports = [
        'jinja2.ext',
        'jinja2.ext.do',
        'jinja2.ext.loopcontrols',
        'sqlite3',
        'flask',
        'werkzeug',
        'werkzeug.utils',
        'werkzeug.security',
        'datetime',
        'csv',
        'io',
        'json',
        'os',
        'sys',
        'functools',
    ]
    
    # Add report-related imports if available
    try:
        import docx
        hidden_imports.extend([
            'docx',
            'docx.shared',
            'docx.enum.text',
            'docx.enum.style',
        ])
        print(f"   [OK] Added python-docx support (for reports)")
    except ImportError:
        print("   [!] python-docx not found - report generation may not work")
    
    try:
        import apscheduler
        hidden_imports.extend([
            'apscheduler',
            'apscheduler.schedulers',
            'apscheduler.schedulers.background',
        ])
        print(f"   [OK] Added APScheduler support (for auto-reports)")
    except ImportError:
        print("   [!] APScheduler not found - auto-reports may not work")
    
    # Build PyInstaller command
    args = [
        'app.py',  # Main script
        '--name=AAMUSTED_Counseling_System',  # Executable name
        '--onefile',  # Single file
        '--windowed',  # No console window
        '--clean',  # Clean cache
        '--noconfirm',  # Overwrite without asking
    ]
    
    # DISABLED ICON TO PREVENT BUILD ERRORS/CHARMAP ERRORS
    # if icon_file and os.path.exists(icon_file):
    #     args.append(f'--icon={icon_file}')
    #     print(f"   [OK] Added icon: {icon_file}")
    
    # Add data files
    for data in datas:
        args.append(f'--add-data={data}')
    
    # Add hidden imports
    for imp in hidden_imports:
        args.append(f'--hidden-import={imp}')
    
    # Collect all dependencies (ensures everything is included)
    args.extend([
        '--collect-all=flask',
        '--collect-all=jinja2',
        '--collect-all=werkzeug',
    ])
    
    # Try to collect docx and apscheduler if available
    try:
        import docx
        args.append('--collect-all=docx')
    except:
        pass
    
    try:
        import apscheduler
        args.append('--collect-all=apscheduler')
    except:
        pass
    
    # Exclude unnecessary modules to reduce size
    excludes = [
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'tkinter',
    ]
    
    for exc in excludes:
        args.append(f'--exclude-module={exc}')
    
    # Build the executable
    print("\n[+] Building executable with PyInstaller...")
    print("   (This is the longest step - please be patient)\n")
    
    try:
        PyInstaller.__main__.run(args)
        
        exe_path = 'dist/AAMUSTED_Counseling_System.exe'
        
        if not os.path.exists(exe_path):
            print("\n[X] Build failed - executable not found!")
            return False
        
        exe_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
        print(f"\n[OK] Build completed successfully!")
        print(f"[I] Executable size: {exe_size:.1f} MB")
        print(f"[I] Location: {os.path.abspath(exe_path)}")
        
        # Create complete distribution package
        create_distribution_package(exe_path)
        
        return True
        
    except Exception as e:
        print(f"\n[X] Build failed with error:")
        print(f"   {str(e)}")
        os.system("pause") # Keep window open if it crashes
        return False

def create_distribution_package(exe_path):
    """Create a complete distribution package ready for deployment"""
    
    print("\n[+] Creating distribution package...")
    
    dist_folder = "AAMUSTED_Counseling_System_Distribution"
    
    # Clean and create folder
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)
    os.makedirs(dist_folder)
    
    # Copy executable
    shutil.copy(exe_path, dist_folder)
    print(f"   [OK] Copied executable")
    
    # Create app_data folder structure
    os.makedirs(f'{dist_folder}/app_data/reports', exist_ok=True)
    print(f"   [OK] Created app_data/reports folder")
    
    # Copy logo if exists (for reports)
    if os.path.exists('aamusted system_logo.png'):
        shutil.copy('aamusted system_logo.png', dist_folder)
        print(f"   [OK] Copied logo file")
    
    # Create simple README
    readme_content = """AAMUSTED COUNSELING MANAGEMENT SYSTEM
=======================================

1. Double-click "AAMUSTED_Counseling_System.exe" to start.
2. The system works completely offline.
3. Database is created automatically.
    """
    
    with open(f'{dist_folder}/START_HERE.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"   [OK] Created START_HERE.txt")
    
    # Create desktop shortcut script
    shortcut_script = """@echo off
echo Creating desktop shortcut...
set SCRIPT="%TEMP%\\create_shortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = "%USERPROFILE%\\Desktop\\AAMUSTED Counseling System.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%~dp0AAMUSTED_Counseling_System.exe" >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0" >> %SCRIPT%
echo oLink.Description = "AAMUSTED Counseling Management System" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript /nologo %SCRIPT%
del %SCRIPT%
echo Shortcut created!
pause
"""
    
    with open(f'{dist_folder}/Create_Desktop_Shortcut.bat', 'w') as f:
        f.write(shortcut_script)
    print(f"   [OK] Created Create_Desktop_Shortcut.bat")
    
    print(f"\n[OK] Distribution package created successfully!")
    print(f"\n[+] Package location: {os.path.abspath(dist_folder)}")

def main():
    """Main function"""
    print("\nAAMUSTED COUNSELING SYSTEM - COMPLETE BUILD\n")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Build
    success = build_complete_executable()
    
    if success:
        print("\n[OK] BUILD SUCCESSFUL!")
        print("\n[+] Your complete executable is ready in:")
        print(f"   AAMUSTED_Counseling_System_Distribution/")
    else:
        print("\n[X] BUILD FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
