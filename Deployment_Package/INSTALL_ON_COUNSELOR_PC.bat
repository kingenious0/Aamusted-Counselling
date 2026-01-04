@echo off
echo AAMUSTED Counselling System - Installation Script
echo =============================================
echo.
echo This script will install the counselling system on this PC.
echo.

REM Check for administrator rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ This script must be run as Administrator!
    echo Right-click on this file and select "Run as administrator"
    pause
    exit /b 1
)

echo ✅ Administrator rights confirmed
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
echo Script directory: %SCRIPT_DIR%

REM Create application directory
if not exist "C:\AAMUSTED Counselling" mkdir "C:\AAMUSTED Counselling"

REM Create service logs directory
if not exist "C:\AAMUSTED Counselling\service_logs" mkdir "C:\AAMUSTED Counselling\service_logs"

REM Copy files
echo Copying application files...
echo Copying from: %SCRIPT_DIR%
echo Copying to: C:\AAMUSTED Counselling\
echo.

xcopy /E /Y /I "%SCRIPT_DIR%templates" "C:\AAMUSTED Counselling\templates"
xcopy /E /Y /I "%SCRIPT_DIR%static" "C:\AAMUSTED Counselling\static"
copy /Y "%SCRIPT_DIR%app.py" "C:\AAMUSTED Counselling\"
copy /Y "%SCRIPT_DIR%counseling.db" "C:\AAMUSTED Counselling\"
copy /Y "%SCRIPT_DIR%windows_service.py" "C:\AAMUSTED Counselling\"
copy /Y "%SCRIPT_DIR%service_manager.py" "C:\AAMUSTED Counselling\"
copy /Y "%SCRIPT_DIR%check_service.py" "C:\AAMUSTED Counselling\"
copy /Y "%SCRIPT_DIR%create_shortcuts.py" "C:\AAMUSTED Counselling\"
copy /Y "%SCRIPT_DIR%service_requirements.txt" "C:\AAMUSTED Counselling\"

echo ✅ Files copied successfully
echo.

REM Install Python dependencies
echo Installing Python dependencies...
cd "C:\AAMUSTED Counselling"
echo Installing Flask and dependencies...
python -m pip install Flask==2.3.3 Werkzeug==2.3.7 Jinja2==3.1.2 MarkupSafe==2.1.3 itsdangerous==2.1.2 click==8.1.7 blinker==1.6.3 python-dateutil==2.8.2 six==1.16.0 openpyxl==3.1.2 pywin32==306
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies. Please install Python first!
    pause
    exit /b 1
)

echo ✅ Dependencies installed
echo.

REM Install the service
echo Installing Windows Service...
python windows_service.py install
if %errorlevel% neq 0 (
    echo ❌ Service installation failed!
    pause
    exit /b 1
)

echo ✅ Service installed successfully
echo.

REM Start the service
echo Starting the service...
echo Waiting 5 seconds before starting service...
timeout /t 5 /nobreak > nul
net start AAMUSTEDCounsellingService
if %errorlevel% neq 0 (
    echo ❌ Service failed to start!
    echo Checking service logs for details...
    if exist "C:\AAMUSTED Counselling\service_logs\" (
        echo Recent log entries:
        type "C:\AAMUSTED Counselling\service_logs\*.log" | findstr /c:"error" /i
    )
    echo.
    echo You can try starting the service manually later with: net start AAMUSTEDCounsellingService
    pause
    exit /b 1
)

echo ✅ Service started successfully
echo.

REM Create desktop shortcuts
echo Creating desktop shortcuts...
cd "C:\AAMUSTED Counselling"
python create_shortcuts.py

echo.
echo =============================================
echo 🎉 Installation Complete!
echo.
echo The AAMUSTED Counselling System is now running.
echo.
echo To verify:
echo 1. Open browser and go to: http://localhost:5000
echo 2. Or double-click "Check Counselling Service" on desktop
echo.
echo Service logs are located at: C:\AAMUSTED Counselling\service_logs\
echo For support, refer to the documentation files.
echo =============================================
pause