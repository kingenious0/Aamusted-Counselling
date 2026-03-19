@echo off
set "self=%~f0"
if "%1"=="--silent" goto :run_server

REM Check if we should run silently
echo ========================================
echo   AAMUSTED Counselling System Launcher
echo ========================================
echo.
echo [1] Start Normal (With Terminal)
echo [2] Start Silent (In Background)
echo.
set /p choice="Select mode [1/2, default 1]: "

if "%choice%"=="2" (
    echo.
    echo Launching system in background... 
    echo Browser will open in a few seconds.
    powershell -WindowStyle Hidden -Command "Start-Process cmd -ArgumentList '/c ^\"%self%^\" --silent' -WindowStyle Hidden"
    timeout /t 3 >nul
    exit
)

:run_server
title AAMUSTED Counselling System - Background Engine
REM Go to batch file's directory
cd /d "%~dp0"

REM 1. Kill any processes using port 5050
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5050" ^| findstr "LISTENING" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM 2. Start Flask directly from Python
set USTED_AUTO_OPEN_BROWSER=1
python app.py

if NOT "%1"=="--silent" pause
