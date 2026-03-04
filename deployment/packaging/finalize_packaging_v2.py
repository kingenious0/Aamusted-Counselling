
import os
import shutil
import zipfile

def create_zip():
    print("Creating final distribution...")
    
    base_dir = r"c:\Users\kinge\Documents\Counselling System -FULL VERSION\Counselling System -Remade"
    dist_dir = os.path.join(base_dir, "AAMUSTED_Universal_Distribution")
    win_dir = os.path.join(dist_dir, "AAMUSTED_Windows_Installer")
    exe_source = os.path.join(base_dir, "dist", "AAMUSTED_Counseling_System.exe")
    
    # 1. Prepare Directory
    if os.path.exists(win_dir):
        try:
            shutil.rmtree(win_dir)
        except:
            print("Could not delete existing dir, trying to continue")
            
    os.makedirs(win_dir, exist_ok=True)
    
    # 2. Copy EXE
    shutil.copy(exe_source, win_dir)
    print("Copied EXE")
    
    # 3. Create Batch Script
    bat_content = r"""@echo off
echo Installing AAMUSTED Counseling System...
echo.

:: Create proper directory in Documents
set "INSTALL_DIR=%USERPROFILE%\Documents\AAMUSTED_Counseling_System"

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: Copy executable
copy /Y "AAMUSTED_Counseling_System.exe" "%INSTALL_DIR%\"

:: Create Startup Shortcut logic
set "SHORTCUT_SCRIPT=%TEMP%\create_startup.vbs"
set "STARTUP_DIR=%appdata%\Microsoft\Windows\Start Menu\Programs\Startup"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%SHORTCUT_SCRIPT%"
echo sLinkFile = "%STARTUP_DIR%\AAMUSTED System.lnk" >> "%SHORTCUT_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%SHORTCUT_SCRIPT%"
echo oLink.TargetPath = "%INSTALL_DIR%\AAMUSTED_Counseling_System.exe" >> "%SHORTCUT_SCRIPT%"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%SHORTCUT_SCRIPT%"
echo oLink.Description = "AAMUSTED Counseling System" >> "%SHORTCUT_SCRIPT%"
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
    with open(os.path.join(win_dir, "INSTALL_AND_RUN.bat"), "w") as f:
        f.write(bat_content)
        
    # 4. Zip it
    zip_path = os.path.join(dist_dir, "AAMUSTED_Windows_Installer.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(win_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, win_dir)
                zipf.write(file_path, arcname)
                
    print(f"Created ZIP: {zip_path}")

try:
    create_zip()
except Exception as e:
    print(e)
