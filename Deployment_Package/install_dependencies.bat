@echo off
echo Installing Python Dependencies for AAMUSTED Counselling System
echo ==================================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Install pip if not available
echo Checking pip installation...
python -m ensurepip --upgrade
if %errorlevel% neq 0 (
    echo ERROR: Could not install pip
    pause
    exit /b 1
)

echo Installing required packages...
echo This may take a few minutes...

REM Install each package individually with error handling
echo Installing Flask...
python -m pip install Flask==2.3.3
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Flask
    pause
    exit /b 1
)

echo Installing Werkzeug...
python -m pip install Werkzeug==2.3.7
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Werkzeug
    pause
    exit /b 1
)

echo Installing Jinja2...
python -m pip install Jinja2==3.1.2
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Jinja2
    pause
    exit /b 1
)

echo Installing MarkupSafe...
python -m pip install MarkupSafe==2.1.3
if %errorlevel% neq 0 (
    echo ERROR: Failed to install MarkupSafe
    pause
    exit /b 1
)

echo Installing itsdangerous...
python -m pip install itsdangerous==2.1.2
if %errorlevel% neq 0 (
    echo ERROR: Failed to install itsdangerous
    pause
    exit /b 1
)

echo Installing click...
python -m pip install click==8.1.7
if %errorlevel% neq 0 (
    echo ERROR: Failed to install click
    pause
    exit /b 1
)

echo Installing blinker...
python -m pip install blinker==1.6.2
if %errorlevel% neq 0 (
    echo ERROR: Failed to install blinker
    pause
    exit /b 1
)

echo Installing python-dateutil...
python -m pip install python-dateutil==2.8.2
if %errorlevel% neq 0 (
    echo ERROR: Failed to install python-dateutil
    pause
    exit /b 1
)

echo Installing six...
python -m pip install six==1.16.0
if %errorlevel% neq 0 (
    echo ERROR: Failed to install six
    pause
    exit /b 1
)

echo Installing openpyxl...
python -m pip install openpyxl==3.1.2
if %errorlevel% neq 0 (
    echo ERROR: Failed to install openpyxl
    pause
    exit /b 1
)

echo Installing python-dotenv...
python -m pip install python-dotenv==1.0.0
if %errorlevel% neq 0 (
    echo ERROR: Failed to install python-dotenv
    pause
    exit /b 1
)

echo Installing python-docx...
python -m pip install python-docx==0.8.11
if %errorlevel% neq 0 (
    echo ERROR: Failed to install python-docx
    pause
    exit /b 1
)

echo Installing APScheduler...
python -m pip install APScheduler==3.10.4
if %errorlevel% neq 0 (
    echo ERROR: Failed to install APScheduler
    pause
    exit /b 1
)

echo Installing pywin32 (for Windows Service)...
python -m pip install pywin32==306
if %errorlevel% neq 0 (
    echo ERROR: Failed to install pywin32
    pause
    exit /b 1
)

echo.
echo ==================================================================
echo All dependencies installed successfully!
echo ==================================================================
echo.

REM Test the installation
echo Testing Flask installation...
python -c "import flask; print('Flask version:', flask.__version__)"
if %errorlevel% equ 0 (
    echo Flask installation verified!
) else (
    echo WARNING: Flask installation test failed
)

echo.
echo Installation complete! You can now run the counselling system.
echo.
echo To run manually: python app.py
echo To install as service: python windows_service.py install
echo.
pause