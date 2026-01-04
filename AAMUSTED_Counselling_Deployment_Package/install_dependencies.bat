@echo off
echo ========================================
echo Installing AAMUSTED Counselling Dependencies
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found: 
python --version

REM Install pip if not available
python -m pip --version >nul 2>&1
if %errorLevel% neq 0 (
    echo 📦 Installing pip...
    python -m ensurepip --upgrade
)

echo.
echo 📦 Installing required packages...
echo This may take a few minutes...

REM Install all dependencies
pip install flask==2.3.3
pip install werkzeug==2.3.7
pip install jinja2==3.1.2
pip install markupsafe==2.1.3
pip install itsdangerous==2.1.2
pip install click==8.1.7
pip install blinker==1.6.3
pip install python-dateutil==2.8.2
pip install six==1.16.0
pip install openpyxl==3.1.2
pip install python-dotenv==1.0.0
pip install python-docx==0.8.11
pip install apscheduler==3.10.4
pip install pywin32

if %errorLevel% equ 0 (
    echo.
    echo ✅ All dependencies installed successfully!
    echo.
    echo You can now:
    echo 1. Run the application: python app.py
    echo 2. Install the service: install_service_admin.bat (as admin)
    echo 3. Quick start: QUICK_START.bat
) else (
    echo.
    echo ❌ Some dependencies failed to install!
    echo Please check the error messages above
)

echo.
pause