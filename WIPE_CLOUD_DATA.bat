@echo off
setlocal
title AAMUSTED Counselling - WIPE CLOUD TEST DATA
cls

echo ===================================================
echo   AAMUSTED Counselling System - Cloud Data Wipe
echo ===================================================
echo.
echo This tool will PERMANENTLY delete all test entries 
echo from the cloud (Students, Appointments, Sessions).
echo.
echo It will NOT touch your Local Computer folder.
echo It will NOT touch App Settings or User accounts.
echo.

python scripts\WIPE_CLOUD_TEST_DATA.py

echo.
pause
