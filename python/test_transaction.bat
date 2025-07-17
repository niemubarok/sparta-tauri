@echo off
echo Testing New Transaction Structure...
cd /d "%~dp0"
python test_transaction_structure.py
echo.
echo Test completed. Press any key to continue...
pause
