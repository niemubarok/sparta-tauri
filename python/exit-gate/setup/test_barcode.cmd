@echo off
echo ===============================================
echo     EXIT GATE - BARCODE SYSTEM TEST
echo ===============================================
echo.
echo Pattern: _id = transaction_{barcode}
echo          no_barcode = {barcode}
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

echo.
echo Running barcode logic test...
echo.

python test_barcode_logic.py

echo.
echo ===============================================
echo Test completed. Press any key to continue...
pause > nul
