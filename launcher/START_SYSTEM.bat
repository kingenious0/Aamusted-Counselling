@echo off
title AAMUSTED Counselling System - Latest Version
color 0A
cls
echo.
echo ========================================
echo   AAMUSTED Counselling System
echo   Latest Version with ALL Features!
echo ========================================
echo.
echo Features Available:
echo   - Statistics and Analytics
echo   - Delete Students, Appointments, Sessions, Referrals
echo   - Mrs. Gertrude Effeh Brew as sole counsellor
echo.

REM Go to batch file's directory
cd /d "%~dp0"

REM Kill any processes using port 5000
echo [Step 1/3] Stopping old instances...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING" 2^>nul') do (
    echo    Stopping process on port 5000 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 >nul

echo [Step 2/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ or use the EXE version
    pause
    exit /b 1
)

echo [Step 3/3] Starting server with ALL features including Statistics...
echo.
echo ========================================
echo   Server Starting...
echo ========================================
echo.
echo The Statistics page is now available!
echo Browser will open automatically.
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

timeout /t 2 >nul

REM Start Flask directly from Python
python app.py

