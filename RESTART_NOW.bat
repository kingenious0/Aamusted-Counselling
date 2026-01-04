@echo off
title Restart Server - Delete Features
color 0B
cls
echo.
echo ===============================================
echo   RESTARTING - Delete Features Will Work!
echo ===============================================
echo.

cd /d "%~dp0"

echo Stopping old server...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 >nul

echo Starting new server with delete routes...
echo.
echo IMPORTANT: Wait for "Running on http://127.0.0.1:5000"
echo Then refresh your browser!
echo.
pause

python app.py

