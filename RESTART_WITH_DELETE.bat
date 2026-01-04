@echo off
title RESTART - Enable Delete Features
color 0C
cls
echo.
echo ============================================================
echo   RESTARTING SERVER - Delete Features Required!
echo ============================================================
echo.
echo IMPORTANT: The server needs to restart to enable delete.
echo.
echo This will:
echo   1. Force stop ALL Flask/Python processes
echo   2. Clear port 5000 completely  
echo   3. Start fresh with delete functionality
echo.
echo ============================================================
echo.
pause

REM Go to project directory
cd /d "%~dp0"

echo [Step 1/4] Stopping ALL Python/Flask processes...
REM Kill all python processes (be careful!)
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr "PID"') do (
    echo    Stopping Python process %%a
    taskkill /F /PID %%a >nul 2>&1
)

REM Also check for the EXE
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq AAMUSTED_Counseling_System.exe" /FO LIST ^| findstr "PID"') do (
    echo    Stopping EXE process %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 >nul

echo [Step 2/4] Checking port 5000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" 2^>nul') do (
    echo    Found process %%a on port 5000, killing...
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 >nul

echo [Step 3/4] Verifying port is clear...
netstat -ano | findstr ":5000" >nul
if %errorlevel% equ 0 (
    echo    WARNING: Port still in use! Retrying...
    timeout /t 2 >nul
    goto :retry_kill
)

:retry_kill
REM Final check and kill
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo [Step 4/4] Starting server with DELETE functionality...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo You need to:
    echo   1. Install Python 3.8+
    echo   2. OR rebuild the EXE with delete routes included
    echo.
    pause
    exit /b 1
)

echo ============================================================
echo   SERVER STARTING WITH DELETE FEATURES
echo ============================================================
echo.
echo Delete buttons now available for:
echo   - Students
echo   - Appointments
echo   - Sessions  
echo   - Referrals
echo.
echo Browser will open automatically...
echo ============================================================
echo.

timeout /t 2 >nul

REM Start the server
start "" python app.py

timeout /t 5 >nul

REM Open browser
start http://127.0.0.1:5000

echo.
echo Server should be running now with delete functionality!
echo.
echo Press any key to see server window...
pause >nul

