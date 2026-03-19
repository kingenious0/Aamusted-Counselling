@echo off
setlocal
title AAMUSTED Counselling - Project Link Packager
cls

echo ===================================================
echo   AAMUSTED Counselling System - HYBRID PACKAGE (Win/Mac)
echo ===================================================
echo.
echo This tool will create a "Clean Version" of your 
echo project on your Desktop, perfect for copying to 
echo other staff PCs (Windows OR Mac).
echo.
echo It EXCLUDES all large junk files (like Lib, Git, 
echo and old backups) to keep the file size tiny.
echo.

set "SOURCE_DIR=%~dp0"
set "DEST_DIR=%USERPROFILE%\Desktop\AAMUSTED_DISTRIBUTION"

if exist "%DEST_DIR%" (
    echo [Check] Desktop folder already exists. Deleting it to start fresh...
    rmdir /s /q "%DEST_DIR%"
)

echo.
echo [1/3] Creating folder structure: %DEST_DIR%
mkdir "%DEST_DIR%"
mkdir "%DEST_DIR%\core"
mkdir "%DEST_DIR%\static"
mkdir "%DEST_DIR%\templates"
mkdir "%DEST_DIR%\assets"
mkdir "%DEST_DIR%\scripts"

echo [2/3] Copying vital files (Fast)...

REM Core logic files
copy "%SOURCE_DIR%app.py" "%DEST_DIR%\" >nul
copy "%SOURCE_DIR%sync_engine.py" "%DEST_DIR%\" >nul
copy "%SOURCE_DIR%node_config.py" "%DEST_DIR%\" >nul
copy "%SOURCE_DIR%node_config.json" "%DEST_DIR%\" >nul
copy "%SOURCE_DIR%version.txt" "%DEST_DIR%\" >nul
copy "%SOURCE_DIR%requirements.txt" "%DEST_DIR%\" >nul

REM Windows Launchers
copy "%SOURCE_DIR%START_HERE.bat" "%DEST_DIR%\" >nul
copy "%SOURCE_DIR%START_SILENT.vbs" "%DEST_DIR%\" >nul
copy "%SOURCE_DIR%FIRST_TIME_SETUP.bat" "%DEST_DIR%\" >nul
copy "%SOURCE_DIR%ACTIVATE_AUTOSTART.bat" "%DEST_DIR%\" >nul
copy "%SOURCE_DIR%CLEANUP_OLD_SERVER.bat" "%DEST_DIR%\" >nul
copy "%SOURCE_DIR%WIPE_CLOUD_DATA.bat" "%DEST_DIR%\" >nul

REM Mac Launchers (NEW)
copy "%SOURCE_DIR%FIRST_TIME_SETUP_MAC.command" "%DEST_DIR%\" >nul
copy "%SOURCE_DIR%START_HERE_MAC.command" "%DEST_DIR%\" >nul

REM Directories
xcopy "%SOURCE_DIR%core\*" "%DEST_DIR%\core\" /E /I /H /Y /Q >nul
xcopy "%SOURCE_DIR%static\*" "%DEST_DIR%\static\" /E /I /H /Y /Q >nul
xcopy "%SOURCE_DIR%templates\*" "%DEST_DIR%\templates\" /E /I /H /Y /Q >nul
xcopy "%SOURCE_DIR%assets\*" "%DEST_DIR%\assets\" /E /I /H /Y /Q >nul
xcopy "%SOURCE_DIR%scripts\*" "%DEST_DIR%\scripts\" /E /I /H /Y /Q >nul

echo [3/3] Final Cleaning...
REM Skip DB copy because they will sync fresh from cloud!

echo.
echo ===================================================
echo   SUCCESS! "AAMUSTED_DISTRIBUTION" is on your Desktop.
echo ===================================================
echo.
echo This folder is now very small and ready for ANY PC!
echo.
echo - For Windows: Run "FIRST_TIME_SETUP.bat"
echo - For Mac: Run "FIRST_TIME_SETUP_MAC.command"
echo.
echo No more "No matching version" errors!
echo ===================================================
pause
