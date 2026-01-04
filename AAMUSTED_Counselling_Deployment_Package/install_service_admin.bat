@echo off
echo Installing AAMUSTED Counselling Service...
echo This script requires administrator privileges.
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script must be run as administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Change to the service directory
cd /d "C:\AAMUSTED Counselling"

REM Install the service
echo Installing service...
python windows_service.py install

if %errorLevel% equ 0 (
    echo.
    echo Service installed successfully!
    echo Starting service...
    net start AAMUSTEDCounsellingService
    
    if %errorLevel% equ 0 (
        echo Service started successfully!
    ) else (
        echo Failed to start service. You may need to start it manually.
        echo Use: net start AAMUSTEDCounsellingService
    )
) else (
    echo Service installation failed!
)

echo.
echo Press any key to exit...
pause > nul