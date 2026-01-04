@echo off
echo.
echo ================================================
echo AAMUSTED Counselling System - Service Installer
echo ================================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This installer requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Get current directory
set INSTALL_DIR=%~dp0
echo Installation directory: %INSTALL_DIR%

REM Check if Python is installed
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo Python found. Checking version...
python --version

REM Install required Python packages
echo.
echo Installing required Python packages...
echo.

pip install pywin32
if %errorLevel% neq 0 (
    echo ERROR: Failed to install pywin32 package
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo Installing Windows Service...
echo ================================================
echo.

REM Change to installation directory
cd /d "%INSTALL_DIR%"

REM Install the service
python windows_service.py install
if %errorLevel% neq 0 (
    echo ERROR: Failed to install Windows Service
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo Service installed successfully!
echo ================================================
echo.
echo The AAMUSTED Counselling System service has been installed with the following features:
echo.
echo - Automatic startup on system boot
echo - Automatic restart on failure (up to 3 times)
echo - Recovery after 60 seconds if crashed
echo - Comprehensive logging to service_logs directory
echo.
echo To start the service now, type: net start AAMUSTEDCounsellingService
echo To stop the service, type: net stop AAMUSTEDCounsellingService
echo To check status, type: sc query AAMUSTEDCounsellingService
echo.
echo The counselling system will be available at: http://localhost:5000
echo.
echo ================================================
echo Installation complete!
echo ================================================
echo.

REM Optionally start the service
echo Would you like to start the service now? (Y/N)
set /p START_SERVICE=
if /i "%START_SERVICE%"=="Y" (
    echo Starting service...
    net start AAMUSTEDCounsellingService
    echo.
    echo Service started! The counselling system should now be accessible.
)

echo.
pause