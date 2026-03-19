@echo off
setlocal
title AAMUSTED Counselling - Autostart Setup
cls

echo ===================================================
echo   AAMUSTED Counselling System - Autostart Setup
echo ===================================================
echo.
echo This tool will ensure the server starts automatically 
echo whenever the computer is turned on.
echo.

set "TARGET_FOLDER=%~dp0"
set "STARTUP_FOLDER=%appdata%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_SCRIPT=%temp%\CreateStartupShortcut.vbs"

echo [Process] Creating Startup Shortcut...
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%SHORTCUT_SCRIPT%"
echo sLinkFile = "%STARTUP_FOLDER%\AAMUSTED_Counselling_Background.lnk" >> "%SHORTCUT_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%SHORTCUT_SCRIPT%"
echo oLink.TargetPath = "%TARGET_FOLDER%START_SILENT.vbs" >> "%SHORTCUT_SCRIPT%"
echo oLink.WorkingDirectory = "%TARGET_FOLDER%" >> "%SHORTCUT_SCRIPT%"
echo oLink.Description = "AAMUSTED Counselling System Server" >> "%SHORTCUT_SCRIPT%"
echo oLink.Save >> "%SHORTCUT_SCRIPT%"

cscript /nologo "%SHORTCUT_SCRIPT%"
del "%SHORTCUT_SCRIPT%"

echo.
echo [Success] The system is now set to start automatically.
echo On every PC start, the server will run silently in the background.
echo.
echo You can now just open your installed PWA ("The App") 
echo at any time and it will work instantly!
echo.
echo ===================================================
pause
