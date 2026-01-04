@echo off
REM ================================================================
REM AAMUSTED Counselling System - First Time Setup
REM Run this ONCE on a new PC to set up everything automatically
REM ================================================================

color 0A
echo.
echo ================================================================
echo    AAMUSTED COUNSELLING SYSTEM - FIRST TIME SETUP
echo ================================================================
echo.
echo This will set up the counselling system on this PC.
echo.
echo What this script does:
echo   1. Check Python installation
echo   2. Install required packages
echo   3. Reset password to default (Counsellor123)
echo   4. Install Windows Service for auto-start
echo   5. Start the service
echo.
echo ================================================================
echo.
pause

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo.
    echo [ERROR] This script must be run as ADMINISTRATOR!
    echo.
    echo Please:
    echo   1. Right-click this file (FIRST_TIME_SETUP.bat)
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

REM ================================================================
REM STEP 1: Check Python
REM ================================================================
echo ================================================================
echo STEP 1/5: Checking Python installation...
echo ================================================================
echo.

python --version >nul 2>&1
if %errorLevel% neq 0 (
    color 0C
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python first:
    echo   1. Go to: https://www.python.org/downloads/
    echo   2. Download Python 3.11 or newer
    echo   3. Run installer and CHECK "Add Python to PATH"
    echo   4. After installation, run this script again
    echo.
    pause
    exit /b 1
)

python --version
echo [OK] Python is installed
echo.

REM ================================================================
REM STEP 2: Install Dependencies
REM ================================================================
echo ================================================================
echo STEP 2/5: Installing required packages...
echo ================================================================
echo.
echo This may take 2-5 minutes. Please wait...
echo.

python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt

if %errorLevel% neq 0 (
    color 0E
    echo.
    echo [WARNING] Some packages may have failed to install.
    echo Continuing anyway...
    echo.
    timeout /t 3 /nobreak >nul
) else (
    echo.
    echo [OK] All packages installed successfully
    echo.
)

REM ================================================================
REM STEP 3: Reset Password
REM ================================================================
echo ================================================================
echo STEP 3/5: Setting up default password...
echo ================================================================
echo.

python reset_password.py

if %errorLevel% neq 0 (
    color 0E
    echo.
    echo [WARNING] Password reset had issues, but continuing...
    echo You may need to run: python reset_password.py manually
    echo.
    timeout /t 3 /nobreak >nul
)

echo.

REM ================================================================
REM STEP 4: Uninstall Old Service (if exists)
REM ================================================================
echo ================================================================
echo STEP 4/5: Checking for existing service...
echo ================================================================
echo.

sc query AAMUSTEDCounsellingService >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] Found existing service. Removing it first...
    net stop AAMUSTEDCounsellingService >nul 2>&1
    python windows_service.py uninstall >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo [OK] Old service removed
) else (
    echo [INFO] No existing service found
)
echo.

REM ================================================================
REM STEP 5: Install and Start Service
REM ================================================================
echo ================================================================
echo STEP 5/5: Installing Windows Service...
echo ================================================================
echo.

python windows_service.py install

if %errorLevel% neq 0 (
    color 0C
    echo.
    echo [ERROR] Service installation failed!
    echo.
    echo Possible reasons:
    echo   - Not running as Administrator
    echo   - Missing dependencies
    echo   - Port 5000 already in use
    echo.
    echo Check the error messages above for details.
    echo.
    pause
    exit /b 1
)

echo [OK] Service installed successfully!
echo.

echo Starting the service...
net start AAMUSTEDCounsellingService

if %errorLevel% neq 0 (
    color 0E
    echo.
    echo [WARNING] Service installed but failed to start automatically.
    echo.
    echo Please check:
    echo   1. Is port 5000 already in use?
    echo   2. Check service_logs folder for error details
    echo.
    echo You can try starting manually:
    echo   net start AAMUSTEDCounsellingService
    echo.
    pause
    exit /b 1
)

REM ================================================================
REM SUCCESS!
REM ================================================================
color 0A
cls
echo.
echo ================================================================
echo              ✓✓✓ SETUP COMPLETE! ✓✓✓
echo ================================================================
echo.
echo The AAMUSTED Counselling System is now installed and running!
echo.
echo ================================================================
echo IMPORTANT INFORMATION:
echo ================================================================
echo.
echo 🌐 ACCESS THE SYSTEM:
echo    Open your web browser and go to:
echo    http://localhost:5000
echo.
echo 🔑 LOGIN PASSWORD:
echo    Counsellor123
echo    (Capital C, double L)
echo.
echo ✅ AUTO-START:
echo    The system will now start automatically when Windows boots
echo    It runs in the background (no visible window)
echo.
echo 📁 LOCATION:
echo    %CD%
echo.
echo ================================================================
echo SERVICE MANAGEMENT:
echo ================================================================
echo.
echo To manage the service later, open Command Prompt as Admin:
echo.
echo   Start:     net start AAMUSTEDCounsellingService
echo   Stop:      net stop AAMUSTEDCounsellingService
echo   Status:    sc query AAMUSTEDCounsellingService
echo   Uninstall: Run REMOVE_AUTO_START.bat as administrator
echo.
echo ================================================================
echo NEXT STEPS:
echo ================================================================
echo.
echo 1. Open your web browser
echo 2. Go to: http://localhost:5000
echo 3. Enter password: Counsellor123
echo 4. Start using the system!
echo.
echo The system is now running and will start automatically
echo every time this PC boots up.
echo.
echo ================================================================
echo.
echo Press any key to open the system in your default browser...
pause >nul

REM Try to open in default browser
start http://localhost:5000

echo.
echo Browser opened. If it didn't work, manually go to:
echo http://localhost:5000
echo.
pause
