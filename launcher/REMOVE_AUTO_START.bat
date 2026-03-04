@echo off
REM ================================================================
REM AAMUSTED Counselling System - Remove Auto-Start Service
REM ================================================================

echo.
echo ================================================================
echo AAMUSTED Counselling System - Remove Auto-Start
echo ================================================================
echo.
echo This will stop and uninstall the Windows Service.
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script must be run as ADMINISTRATOR!
    echo.
    echo Please:
    echo   1. Right-click this file
    echo   2. Select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [OK] Running with administrator privileges
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if service exists
sc query AAMUSTEDCounsellingService >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Service is not installed.
    echo Nothing to remove.
    echo.
    pause
    exit /b 0
)

echo [STEP 1/2] Stopping service...
net stop AAMUSTEDCounsellingService
echo.

echo [STEP 2/2] Uninstalling service...
python windows_service.py uninstall

if %errorLevel% equ 0 (
    echo.
    echo ================================================================
    echo SUCCESS! Service removed.
    echo ================================================================
    echo.
    echo The counselling system will no longer start automatically.
    echo You can still run it manually using START_SYSTEM.bat
    echo.
) else (
    echo.
    echo [ERROR] Failed to uninstall service.
    echo.
)

echo Press any key to exit...
pause >nul
