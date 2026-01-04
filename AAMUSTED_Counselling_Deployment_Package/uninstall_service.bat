@echo off
echo.
echo ================================================
echo AAMUSTED Counselling System - Service Uninstaller
echo ================================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This uninstaller requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo This will completely remove the AAMUSTED Counselling System Windows Service.
echo.
echo Are you sure you want to continue? (Y/N)
set /p CONFIRM=

if /i not "%CONFIRM%"=="Y" (
    echo Uninstallation cancelled.
    pause
    exit /b 0
)

REM Get current directory
set INSTALL_DIR=%~dp0
echo.
echo Uninstalling from: %INSTALL_DIR%

REM Change to installation directory
cd /d "%INSTALL_DIR%"

echo.
echo ================================================
echo Stopping service...
echo ================================================
echo.

REM Stop the service first
echo Stopping AAMUSTEDCounsellingService...
net stop AAMUSTEDCounsellingService
if %errorLevel% neq 0 (
    echo Service might not be running or already stopped.
)

echo.
echo Waiting for service to stop...
timeout /t 3 /nobreak >nul

echo.
echo ================================================
echo Uninstalling service...
echo ================================================
echo.

REM Uninstall the service
python windows_service.py uninstall
if %errorLevel% neq 0 (
    echo WARNING: Service uninstallation encountered issues.
    echo The service might have been removed already.
)

echo.
echo ================================================
echo Cleaning up...
echo ================================================
echo.

REM Remove log files (optional)
echo Removing service logs...
if exist "service_logs" (
    rmdir /s /q "service_logs"
    echo Service logs removed.
) else (
    echo No service logs found.
)

echo.
echo ================================================
echo Uninstallation complete!
echo ================================================
echo.
echo The AAMUSTED Counselling System service has been removed.
echo You can now safely delete the application files if desired.
echo.
pause