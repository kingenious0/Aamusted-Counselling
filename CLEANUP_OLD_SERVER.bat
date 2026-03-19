==================================================
  AAMUSTED Counselling System - Cloud Data Wipe
===================================================

This tool will PERMANENTLY delete all test entries
from the cloud (Students, Appointments, Sessions).

It will NOT touch your Local Computer folder.
It will NOT touch App Settings or User accounts.

Traceback (most recent call last):
  File "C:\Users\kinge\Documents\Counselling System -FULL VERSION\Counselling System -Remade\scripts\WIPE_CLOUD_TEST_DATA.py", line 10, in <module>
    import node_config
ModuleNotFoundError: No module named 'node_config'

Press any key to continue . . .
@echo off
setlocal
title AAMUSTED Counselling - Old Server Cleanup
cls

echo ===================================================
echo   AAMUSTED Counselling System - Cleanup Utility
echo ===================================================
echo.
echo This tool will find and stop any old counselling 
echo servers running on Port 5000 and remove them from 
echo your Windows Startup folder.
echo.

REM 1. Kill any existing process on 5000 and 5050
echo [1/3] Searching for old processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000 :5050" ^| findstr "LISTENING" 2^>nul') do (
    echo    Stopping blocking process (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

REM 2. Remove old startup shortcuts
echo [2/3] Searching for old startup shortcuts...
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM Look for any shortcuts starting with "Counseling" or "AAMUSTED"
del /q "%STARTUP_FOLDER%\Counseling*.lnk" 2>nul
del /q "%STARTUP_FOLDER%\AAMUSTED*.lnk" 2>nul
del /q "%STARTUP_FOLDER%\USTED*.lnk" 2>nul

echo [3/3] Finalizing cleanup...
echo    Ports 5000 and 5050 are now free.
echo    Old autostart shortcuts removed.

echo.
echo ===================================================
echo   CLEANUP SUCCESSFUL! 
echo ===================================================
echo.
echo You can now run the NEW system on Port 5050.
echo.
echo To start the new system, run: START_HERE.bat
echo ===================================================
pause
