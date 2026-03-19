@echo off
setlocal
title AAMUSTED Counselling - NEW PC SETUP
cls

echo ===================================================
echo   AAMUSTED Counselling System - New PC Setup
echo ===================================================
echo.
echo Please ensure Python 3.8+ is installed on this PC
echo and "Add Python to PATH" was checked during setup.
echo.
pause

REM 1. Check Python
echo.
echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install it from https://www.python.org/
    pause
    exit /b 1
)

REM 2. Install Dependencies
echo.
echo [2/3] Installing Required Libraries (Pip)...
echo This might take a few moments depending on your internet.
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install libraries. Please check your internet connection.
    pause
    exit /b 1
)

REM 3. Run Autostart Setup
echo.
echo [3/3] Activating Background Autostart...
call ACTIVATE_AUTOSTART.bat
if errorlevel 1 goto :failed

echo.
echo ===================================================
echo   SETUP SUCCESSFUL! 
echo ===================================================
echo.
echo Port: 5050
echo Local Website: http://localhost:5050
echo.
echo [FINAL] Starting background server now... 
start START_SILENT.vbs

echo.
echo To INSTALL the system as an App (PWA):
echo 1. Wait for the browser to open (it will take a few seconds).
echo 2. Look at the URL address bar for an "Install" icon.
echo 3. Click "Install" - it will create a desktop icon.
echo.
echo Now you never have to come back here again! 
echo Just double click the newly installed App icon.
echo.
echo ===================================================
pause
exit /b 0

:failed
echo.
echo ERROR: One or more steps failed. Please review the output above.
pause
exit /b 1
