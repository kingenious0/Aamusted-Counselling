@echo off
echo ========================================
echo AAMUSTED Counselling System - Quick Start
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

echo ✅ Python found

REM Check if dependencies are installed
echo.
echo Checking dependencies...
python -c "import flask" >nul 2>&1
if %errorLevel% neq 0 (
    echo 📦 Installing dependencies...
    pip install -r service_requirements.txt
    if %errorLevel% neq 0 (
        echo ❌ Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo ✅ Dependencies ready

REM Test the application
echo.
echo Testing application...
echo Starting Flask server on http://localhost:5000
python app.py

if %errorLevel% neq 0 (
    echo ❌ Application failed to start!
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo 🎉 Application started successfully!
echo Open your browser and go to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
pause