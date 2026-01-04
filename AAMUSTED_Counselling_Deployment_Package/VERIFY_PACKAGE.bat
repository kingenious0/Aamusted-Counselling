@echo off
echo ========================================
echo AAMUSTED Counselling System - Package Verification
echo ========================================
echo.

set "missing_files=0"
set "missing_dirs=0"

echo Checking required files...
echo.

REM Check core Python files
echo [ ] app.py
if exist "app.py" (
    echo   ✅ Found
) else (
    echo   ❌ Missing
    set /a missing_files+=1
)

echo [ ] auto_report_writer.py
if exist "auto_report_writer.py" (
    echo   ✅ Found
) else (
    echo   ❌ Missing
    set /a missing_files+=1
)

echo [ ] windows_service.py
if exist "windows_service.py" (
    echo   ✅ Found
) else (
    echo   ❌ Missing
    set /a missing_files+=1
)

echo [ ] check_service.py
if exist "check_service.py" (
    echo   ✅ Found
) else (
    echo   ❌ Missing
    set /a missing_files+=1
)

echo [ ] service_manager.py
if exist "service_manager.py" (
    echo   ✅ Found
) else (
    echo   ❌ Missing
    set /a missing_files+=1
)

REM Check batch files
echo [ ] install_dependencies.bat
if exist "install_dependencies.bat" (
    echo   ✅ Found
) else (
    echo   ❌ Missing
    set /a missing_files+=1
)

echo [ ] install_service_admin.bat
if exist "install_service_admin.bat" (
    echo   ✅ Found
) else (
    echo   ❌ Missing
    set /a missing_files+=1
)

echo [ ] QUICK_START.bat
if exist "QUICK_START.bat" (
    echo   ✅ Found
) else (
    echo   ❌ Missing
    set /a missing_files+=1
)

echo [ ] START_SYSTEM.bat
if exist "START_SYSTEM.bat" (
    echo   ✅ Found
) else (
    echo   ❌ Missing
    set /a missing_files+=1
)

REM Check database
echo [ ] counseling.db
if exist "counseling.db" (
    echo   ✅ Found
) else (
    echo   ❌ Missing
    set /a missing_files+=1
)

REM Check requirements
echo [ ] service_requirements.txt
if exist "service_requirements.txt" (
    echo   ✅ Found
) else (
    echo   ❌ Missing
    set /a missing_files+=1
)

echo [ ] requirements.txt
if exist "requirements.txt" (
    echo   ✅ Found
) else (
    echo   ❌ Missing
    set /a missing_files+=1
)

REM Check directories
echo.
echo Checking required directories...
echo [ ] static\
if exist "static\" (
    echo   ✅ Found
) else (
    echo   ❌ Missing
    set /a missing_dirs+=1
)

echo [ ] templates\
if exist "templates\" (
    echo   ✅ Found
) else (
    echo   ❌ Missing
    set /a missing_dirs+=1
)

REM Check documentation
echo.
echo Checking documentation...
echo [ ] INSTALLATION_GUIDE.md
if exist "INSTALLATION_GUIDE.md" (
    echo   ✅ Found
) else (
    echo   ❌ Missing
    set /a missing_files+=1
)

echo.
echo ========================================

if %missing_files% equ 0 (
    echo ✅ All files present!
) else (
    echo ❌ %missing_files% files missing!
)

if %missing_dirs% equ 0 (
    echo ✅ All directories present!
) else (
    echo ❌ %missing_dirs% directories missing!
)

echo.

if %missing_files% equ 0 if %missing_dirs% equ 0 (
    echo 🎉 Package is complete and ready for deployment!
    echo.
    echo Next steps:
    echo 1. Run: install_dependencies.bat
    echo 2. Run: QUICK_START.bat
    echo 3. Or install service: install_service_admin.bat (as admin)
) else (
    echo ⚠️  Package verification failed!
    echo Please ensure all files are present before deployment.
)

echo.
pause