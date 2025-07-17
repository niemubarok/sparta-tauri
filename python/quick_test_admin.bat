@echo off
echo ===============================================
echo  PARKING SYSTEM ADMIN - QUICK TEST
echo ===============================================
echo.
echo Starting Admin Interface in Test Mode...
echo No database connection required
echo Using mock data for demonstration
echo.

cd /d "%~dp0admin"

echo Starting server...
python test_admin.py

pause
