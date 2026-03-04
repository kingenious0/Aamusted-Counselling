@echo off
title AAMUSTED Counselling System - Python Version
color 0A
cls
echo.
echo ========================================
echo   AAMUSTED Counselling System
echo   Running from Python Source Code
echo ========================================
echo.
echo This version includes the latest updates
echo including the Statistics page!
echo.

REM Go to batch file's directory
cd /d "%~dp0"

REM Kill any processes using port 5000
echo [Step 1/3] Stopping old instances...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 >nul

echo [Step 2/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or later
    echo Or use START_HERE.bat for the EXE version
    pause
    exit /b 1
)

echo [Step 3/3] Starting server with Python...
echo.
echo ========================================
echo   SUCCESS! Starting server...
echo ========================================
echo.
echo The system will open in your browser.
echo.
echo Press Ctrl+C to stop the server
echo.
timeout /t 2 >nul

REM Start the Flask application directly from Python
python app.py

