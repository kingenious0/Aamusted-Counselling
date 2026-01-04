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

def check_dependencies():
    """Check if all required packages are installed"""
    required = ['PyInstaller', 'flask', 'jinja2', 'werkzeug']
    missing = []
    
    for package in required:
        try:
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
        print("❌ Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nInstall with: pip install " + " ".join(missing))
        return False
    
    if missing_optional:
        print("⚠️  Missing optional packages (features may not work):")
        for pkg in missing_optional:
            print(f"   - {pkg}")
        print("\nRecommended: pip install " + " ".join(missing_optional))
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return False
    
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
    
    print("=" * 60)
    print("AAMUSTED COUNSELING SYSTEM - COMPLETE BUILD")
    print("=" * 60)
    print("\n📦 Building executable with ALL features included...")
    print("⏳ This may take 3-5 minutes, please wait...\n")
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   ✓ Cleaned {folder}/")
    
    # Prepare data files
    datas = []
    
    # Templates folder
    if os.path.exists('templates'):
        datas.append('templates;templates')
        print(f"   ✓ Added templates/ ({len(list(Path('templates').glob('*.html')))} files)")
    
    # Static folder (CSS, JS, fonts)
    if os.path.exists('static'):
        datas.append('static;static')
        print(f"   ✓ Added static/ folder")
    
    # Logo file for reports
    if os.path.exists('aamusted system_logo.png'):
        datas.append('aamusted system_logo.png;.')
        print(f"   ✓ Added logo file")
    
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
        print("   ✓ Added python-docx support (for reports)")
    except ImportError:
        print("   ⚠️  python-docx not found - report generation may not work")
    
    try:
        import apscheduler
        hidden_imports.extend([
            'apscheduler',
            'apscheduler.schedulers',
            'apscheduler.schedulers.background',
        ])
        print("   ✓ Added APScheduler support (for auto-reports)")
    except ImportError:
        print("   ⚠️  APScheduler not found - auto-reports may not work")
    
    # Build PyInstaller command
    args = [
        'app.py',  # Main script
        '--name=AAMUSTED_Counseling_System',  # Executable name
        '--onefile',  # Single file
        '--windowed',  # No console window (use --console for debugging)
        '--clean',  # Clean cache
        '--noconfirm',  # Overwrite without asking
    ]
    
    # Add icon if available
    if icon_file and os.path.exists(icon_file):
        args.append(f'--icon={icon_file}')
        print(f"   ✓ Added icon: {icon_file}")
    
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
    print("\n🔨 Building executable with PyInstaller...")
    print("   (This is the longest step - please be patient)\n")
    
    try:
        PyInstaller.__main__.run(args)
        
        exe_path = 'dist/AAMUSTED_Counseling_System.exe'
        
        if not os.path.exists(exe_path):
            print("\n❌ Build failed - executable not found!")
            return False
        
        exe_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
        print(f"\n✅ Build completed successfully!")
        print(f"📊 Executable size: {exe_size:.1f} MB")
        print(f"📍 Location: {os.path.abspath(exe_path)}")
        
        # Create complete distribution package
        create_distribution_package(exe_path)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Build failed with error:")
        print(f"   {str(e)}")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print(f"   2. Check if PyInstaller is up to date: pip install --upgrade pyinstaller")
        print(f"   3. Try running as administrator")
        return False

def create_distribution_package(exe_path):
    """Create a complete distribution package ready for deployment"""
    
    print("\n📦 Creating distribution package...")
    
    dist_folder = "AAMUSTED_Counseling_System_Distribution"
    
    # Clean and create folder
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)
    os.makedirs(dist_folder)
    
    # Copy executable
    shutil.copy(exe_path, dist_folder)
    print(f"   ✓ Copied executable")
    
    # Create app_data folder structure
    os.makedirs(f'{dist_folder}/app_data/reports', exist_ok=True)
    print(f"   ✓ Created app_data/reports folder")
    
    # Copy logo if exists (for reports)
    if os.path.exists('aamusted system_logo.png'):
        shutil.copy('aamusted system_logo.png', dist_folder)
        print(f"   ✓ Copied logo file")
    
    # Create comprehensive README
    readme_content = """🎓 AAMUSTED COUNSELING MANAGEMENT SYSTEM
═════════════════════════════════════════════════════════

📋 QUICK START
──────────────

1. DOUBLE-CLICK "AAMUSTED_Counseling_System.exe"
   
2. Wait 10-15 seconds for the system to start
   (A browser window will open automatically)
   
3. If browser doesn't open automatically:
   → Open your browser (Chrome, Firefox, Edge)
   → Go to: http://localhost:5000

4. START USING THE SYSTEM! 

═════════════════════════════════════════════════════════

📝 FIRST TIME SETUP
───────────────────

✓ Database is created automatically on first run
✓ Sample data is included
✓ No configuration needed

═════════════════════════════════════════════════════════

💾 DATA STORAGE
───────────────

• Database: counseling.db (created automatically)
• Reports: app_data/reports/ folder
• All data stays on YOUR computer - nothing is sent online

🔒 SECURITY
───────────

• All data is stored locally
• No internet connection required
• No data transmitted to external servers
• Keep this folder secure and make regular backups

═════════════════════════════════════════════════════════

❓ TROUBLESHOOTING
──────────────────

Problem: Windows security warning appears
Solution: Click "More info" → "Run anyway"
          (This is normal for unsigned executables)

Problem: Application won't start
Solution: 
  → Right-click the .exe → "Run as Administrator"
  → Check if antivirus is blocking it
  → Try disabling antivirus temporarily

Problem: Browser doesn't open automatically
Solution: 
  → Wait 15-20 seconds
  → Manually open browser and go to: http://localhost:5000
  → Check Windows Firewall settings

Problem: "Port already in use" error
Solution: 
  → Close any other instances of the application
  → Restart your computer
  → Check if another application is using port 5000

═════════════════════════════════════════════════════════

📞 SUPPORT
──────────

For technical support, contact your IT administrator.

═════════════════════════════════════════════════════════

📋 SYSTEM FEATURES
──────────────────

✓ Student Management
✓ Appointment Scheduling
✓ Session Tracking
✓ Counseling Reports (Word documents)
✓ DASS-21 Assessment
✓ Outcome Questionnaire (OQ-45.2)
✓ Referral Management
✓ Case Notes
✓ Dashboard with Statistics
✓ Data Export (CSV)
✓ Print Reports

═════════════════════════════════════════════════════════

💡 TIPS
───────

• Create a desktop shortcut for easy access
• Make regular backups of the counseling.db file
• Keep this folder in a safe location
• Don't delete any files in this folder

═════════════════════════════════════════════════════════

Version: 1.0.0
Build Date: """ + __import__('datetime').datetime.now().strftime("%Y-%m-%d") + """
"""
    
    with open(f'{dist_folder}/START_HERE.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"   ✓ Created START_HERE.txt")
    
    # Create installation guide
    install_guide = """INSTALLATION GUIDE
═════════════════════════════════════════════════════════

🎯 EASIEST METHOD (RECOMMENDED):
─────────────────────────────────

1. Copy this ENTIRE folder to where you want it
   (Example: C:\\AAMUSTED_Counseling)

2. Double-click "AAMUSTED_Counseling_System.exe"

3. That's it! The system will start automatically.

═════════════════════════════════════════════════════════

💻 SYSTEM REQUIREMENTS:
───────────────────────

✓ Windows 10 or later
✓ 200MB free disk space
✓ Any modern web browser (Chrome, Firefox, Edge)
✓ 2GB RAM (4GB recommended)

═════════════════════════════════════════════════════════

📦 WHAT'S INCLUDED:
───────────────────

• AAMUSTED_Counseling_System.exe - Main application
• app_data/ - Folder for reports (auto-created)
• START_HERE.txt - Quick start guide
• This file - Installation instructions

═════════════════════════════════════════════════════════

🔄 TRANSFERRING TO ANOTHER COMPUTER:
──────────────────────────────────────

Method 1: USB Drive (Recommended)
──────────────────────────────────
1. Copy this entire folder to a USB drive
2. Plug USB into the other computer
3. Copy folder from USB to the computer
4. Double-click the .exe file

Method 2: Network/Cloud
────────────────────────
1. Compress this folder to a ZIP file
2. Upload to OneDrive, Google Drive, or email
3. Download on the other computer
4. Extract the ZIP file
5. Double-click the .exe file

═════════════════════════════════════════════════════════

⚠️  IMPORTANT NOTES:
────────────────────

• The .exe file contains EVERYTHING - no installation needed
• Don't separate files - keep everything together
• Database (counseling.db) will be created automatically
• All data stays on the computer where it runs

═════════════════════════════════════════════════════════

✅ VERIFICATION:
────────────────

After first run, you should see:
✓ counseling.db file created in the same folder
✓ app_data/reports/ folder created
✓ Browser window opens with the dashboard

═════════════════════════════════════════════════════════
"""
    
    with open(f'{dist_folder}/INSTALLATION.txt', 'w', encoding='utf-8') as f:
        f.write(install_guide)
    print(f"   ✓ Created INSTALLATION.txt")
    
    # Create desktop shortcut script
    shortcut_script = """@echo off
echo Creating desktop shortcut...
echo.

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

echo.
echo ✓ Desktop shortcut created successfully!
echo.
pause
"""
    
    with open(f'{dist_folder}/Create_Desktop_Shortcut.bat', 'w') as f:
        f.write(shortcut_script)
    print(f"   ✓ Created Create_Desktop_Shortcut.bat")
    
    # Calculate total size
    total_size = sum(
        os.path.getsize(os.path.join(dirpath, filename))
        for dirpath, dirnames, filenames in os.walk(dist_folder)
        for filename in filenames
    ) / (1024 * 1024)
    
    print(f"\n✅ Distribution package created successfully!")
    print(f"\n📁 Package location: {os.path.abspath(dist_folder)}")
    print(f"📊 Total package size: {total_size:.1f} MB")
    print(f"\n📦 Package contents:")
    print(f"   • AAMUSTED_Counseling_System.exe ({os.path.getsize(exe_path) / (1024*1024):.1f} MB)")
    print(f"   • app_data/ folder (for reports)")
    print(f"   • START_HERE.txt")
    print(f"   • INSTALLATION.txt")
    print(f"   • Create_Desktop_Shortcut.bat")
    
    print(f"\n🎉 Ready for distribution!")
    print(f"\n💡 Next steps:")
    print(f"   1. Test the EXE on your computer first")
    print(f"   2. Copy the entire '{dist_folder}' folder to a USB drive")
    print(f"   3. Transfer to your mom's laptop")
    print(f"   4. Extract/copy to a permanent location")
    print(f"   5. Double-click the .exe to run")

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("AAMUSTED COUNSELING SYSTEM - COMPLETE BUILD")
    print("=" * 60 + "\n")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("\n✓ All dependencies satisfied\n")
    
    # Build
    success = build_complete_executable()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ BUILD SUCCESSFUL!")
        print("=" * 60)
        print("\n📦 Your complete executable is ready in:")
        print(f"   AAMUSTED_Counseling_System_Distribution/")
        print("\n🚀 You can now distribute this folder to other computers!")
    else:
        print("\n" + "=" * 60)
        print("❌ BUILD FAILED")
        print("=" * 60)
        print("\n💡 Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()


