@echo off
title AAMUSTED Counselling Management System
echo Starting AAMUSTED Counselling Management System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or later from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Initialize database if it doesn't exist
if not exist "counseling.db" (
    echo Initializing database...
    python db_setup.py
    echo Database initialized successfully!
    echo.
)

echo Starting web server...
echo.
echo The system will open in your web browser automatically
echo If it doesn't open, visit: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask application
python app.py

pause