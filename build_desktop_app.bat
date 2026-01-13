@echo off
echo ===================================================
echo   AAMUSTED Counselling System - Desktop Builder
echo ===================================================
echo.
echo 1. Ensuring Database Schema is Up-to-Date...
python add_sync_columns.py
echo.

echo 2. Cleaning previous builds...
rmdir /s /q build
rmdir /s /q dist
echo.

echo 3. Building Desktop Application (This may take a minute)...
echo    - Packaging Flask Server
echo    - Packaging Sync Engine
echo    - Creating Standalone EXE
echo.
python -m PyInstaller AAMUSTED_Counseling_System.spec --clean --noconfirm

echo.
echo ===================================================
echo   BUILD COMPLETE!
echo ===================================================
echo.
echo The executable is located in the "dist" folder.
echo You can copy the "dist/AAMUSTED_Counseling_System" folder to any Windows PC.
echo.
pause
