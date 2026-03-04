@echo off
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
