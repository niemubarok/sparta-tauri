@echo off
echo === Testing Bundle Creation ===
echo.

REM Check if exit-gate-nodejs directory exists
if not exist "%cd%" (
    echo Error: Please run this from the exit-gate-nodejs directory
    pause
    exit /b 1
)

echo Current directory: %cd%
echo.

REM Check for required files
echo Checking required files...
if not exist "package.json" (
    echo ❌ package.json not found
    pause
    exit /b 1
)
echo ✓ package.json found

if not exist "server.js" (
    echo ❌ server.js not found  
    pause
    exit /b 1
)
echo ✓ server.js found

if not exist "simple-bundle-creator.ps1" (
    echo ❌ simple-bundle-creator.ps1 not found
    pause
    exit /b 1
)
echo ✓ simple-bundle-creator.ps1 found

echo.
echo Creating test bundle...
echo ==============================
powershell.exe -ExecutionPolicy Bypass -File "simple-bundle-creator.ps1"

echo.
echo ==============================
echo Bundle test complete!
echo Check the created bundle and ZIP file.
pause
