@echo off
REM ================================================================
REM AAMUSTED Counselling System - Auto-Start Setup
REM This will install the system as a Windows Service that:
REM   - Runs in the background (no visible window)
REM   - Starts automatically when Windows boots
REM   - Restarts automatically if it crashes
REM ================================================================

echo.
echo ================================================================
echo AAMUSTED Counselling System - Auto-Start Setup
echo ================================================================
echo.
echo This will install the counselling system as a Windows Service.
echo.
echo The service will:
echo   * Run silently in the background (no CMD window)
echo   * Start automatically when your PC boots
echo   * Restart automatically if it crashes
echo.
echo ================================================================
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
echo Working directory: %CD%
echo.

REM Check if service is already installed
sc query AAMUSTEDCounsellingService >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] Service is already installed.
    echo.
    choice /C YN /M "Do you want to reinstall the service"
    if errorlevel 2 goto :skip_install
    if errorlevel 1 goto :uninstall_first
)

:uninstall_first
echo.
echo [STEP 1/3] Stopping and uninstalling existing service...
net stop AAMUSTEDCounsellingService >nul 2>&1
python windows_service.py uninstall
timeout /t 2 /nobreak >nul
echo [OK] Old service removed
echo.

:install_service
echo [STEP 2/3] Installing Windows Service...
python windows_service.py install

if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Service installation failed!
    echo Please check that Python and all dependencies are installed.
    echo.
    pause
    exit /b 1
)

echo [OK] Service installed successfully!
echo.

:skip_install
echo [STEP 3/3] Starting the service...
net start AAMUSTEDCounsellingService

if %errorLevel% equ 0 (
    echo [OK] Service started successfully!
    echo.
    echo ================================================================
    echo SUCCESS! The counselling system is now running.
    echo ================================================================
    echo.
    echo The system will now:
    echo   * Run in the background (no visible window)
    echo   * Start automatically when Windows boots
    echo   * Be accessible at: http://localhost:5000
    echo.
    echo To manage the service later:
    echo   * Stop:      net stop AAMUSTEDCounsellingService
    echo   * Start:     net start AAMUSTEDCounsellingService
    echo   * Uninstall: Run uninstall_service.bat as administrator
    echo.
    echo ================================================================
) else (
    echo [WARNING] Service installed but failed to start.
    echo.
    echo You can try starting it manually with:
    echo   net start AAMUSTEDCounsellingService
    echo.
    echo Or check the service logs in the service_logs folder.
)

echo.
echo Press any key to exit...
pause >nul
