@echo off
setlocal enabledelayedexpansion

echo =========================================
echo   Exit Gate Offline Bundle Creator
echo =========================================
echo.

:: Check if PowerShell is available
powershell -Command "Get-Host" >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: PowerShell is required but not found
    echo Please install PowerShell and try again
    pause
    exit /b 1
)

:: Set default output directory
set "OUTPUT_DIR=offline-bundle"

echo This script will create an offline installation bundle
echo that can be installed on Raspberry Pi without internet.
echo.
echo Default output directory: %OUTPUT_DIR%
echo.

set /p "CUSTOM_DIR=Enter custom output directory (or press Enter for default): "
if not "%CUSTOM_DIR%"=="" set "OUTPUT_DIR=%CUSTOM_DIR%"

echo.
echo Creating offline bundle in: %OUTPUT_DIR%
echo.

:: Ask for options
set /p "INCLUDE_SYSTEM=Include system packages list? (y/n): "
set /p "VERBOSE_MODE=Enable verbose output? (y/n): "

:: Build PowerShell command
set "PS_COMMAND=.\create-offline-bundle.ps1 -OutputDir '%OUTPUT_DIR%'"

if /i "%INCLUDE_SYSTEM%"=="y" (
    set "PS_COMMAND=!PS_COMMAND! -IncludeSystemPackages"
)

if /i "%VERBOSE_MODE%"=="y" (
    set "PS_COMMAND=!PS_COMMAND! -Verbose"
)

echo.
echo Running: powershell -ExecutionPolicy Bypass -File !PS_COMMAND!
echo.

:: Execute PowerShell script
powershell -ExecutionPolicy Bypass -File !PS_COMMAND!

if %errorlevel% equ 0 (
    echo.
    echo =========================================
    echo   Bundle creation completed successfully!
    echo =========================================
    echo.
    echo The offline bundle is ready in: %OUTPUT_DIR%
    echo.
    echo Next steps:
    echo 1. Copy the bundle folder to your Raspberry Pi
    echo 2. Run the installation script on Pi
    echo.
) else (
    echo.
    echo =========================================
    echo   Bundle creation failed!
    echo =========================================
    echo.
    echo Please check the error messages above
    echo.
)

pause
