@echo off
title Restart AAMUSTED Counselling System
color 0C
echo.
echo ============================================================
echo   RESTARTING AAMUSTED COUNSELLING SYSTEM
echo ============================================================
echo.
echo This will:
echo   1. Stop any running instances
echo   2. Clear port 5000
echo   3. Start the server with latest code
echo.
echo ============================================================
echo.

REM Kill any existing processes on port 5000
echo [Step 1/3] Stopping existing server instances...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING" 2^>nul') do (
    echo    Stopping process on port 5000 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 >nul

echo [Step 2/3] Port cleared
echo [Step 3/3] Starting server with updated code...
echo.

REM Start the Flask application
python app.py

