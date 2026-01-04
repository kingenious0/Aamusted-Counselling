@echo off
title Restart Server - Delete Features Added
color 0A
cls
echo.
echo ============================================================
echo   RESTARTING SERVER - Delete Features Now Available!
echo ============================================================
echo.
echo This will restart the server to enable delete functionality.
echo.
echo ============================================================
echo.

REM Go to project directory
cd /d "%~dp0"

REM Kill any existing processes on port 5000
echo [1/3] Stopping old server instances...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING" 2^>nul') do (
    echo    Stopping process on port 5000 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 >nul

echo [2/3] Port cleared
echo [3/3] Starting server with delete functionality...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please use START_HERE.bat from the Distribution folder instead.
    pause
    exit /b 1
)

echo Server starting with new delete routes...
echo.
echo ============================================================
echo   Delete Features Available:
echo   - Delete Students
echo   - Delete Appointments  
echo   - Delete Sessions
echo   - Delete Referrals
echo ============================================================
echo.

timeout /t 2 >nul

python app.py

