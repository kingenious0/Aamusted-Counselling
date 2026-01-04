@echo off
echo AAMUSTED Counselling System - Manual Startup
echo ==================================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Flask is not installed
    echo Please run install_dependencies.bat first
    pause
    exit /b 1
)

REM Set environment variables
set FLASK_APP=app.py
set FLASK_ENV=production
set FLASK_DEBUG=0

echo Starting AAMUSTED Counselling System...
echo The system will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ==================================================================
echo.

REM Start the Flask application
python app.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start the application
    echo Please check the error messages above
    pause
)

echo.
echo Application stopped.
pause