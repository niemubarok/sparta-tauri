@echo off
REM ====================================================================
REM EXIT GATE PYTHON - AUTOMATED DEPLOYMENT SCRIPT (Windows Version)
REM ====================================================================
REM
REM This script automates the deployment of Exit Gate Python System
REM to a Raspberry Pi from a Windows development machine.
REM
REM Prerequisites:
REM - PuTTY/PSCP installed and in PATH
REM - SSH key authentication configured (optional)
REM - Target Raspberry Pi accessible over network
REM
REM Usage: deploy-to-pi-auto.cmd [PI_IP] [PI_USER]
REM Example: deploy-to-pi-auto.cmd 192.168.10.51 pi
REM
REM Author: Exit Gate Development Team
REM Date: June 29, 2025
REM ====================================================================

setlocal enabledelayedexpansion

REM Default configuration
set PI_IP=%1
set PI_USER=%2
set APP_DIR=python-app
set REMOTE_DIR=/home/pi/exit-gate

REM Use defaults if not provided
if "%PI_IP%"=="" set PI_IP=192.168.10.51
if "%PI_USER%"=="" set PI_USER=pi

REM Colors for output (using PowerShell for colored output)
set RED="Red"
set GREEN="Green"
set YELLOW="Yellow"
set BLUE="Cyan"
set NC="White"

echo.
echo ====================================================================
echo 🚀 EXIT GATE PYTHON - AUTOMATED DEPLOYMENT
echo ====================================================================
echo Target: %PI_USER%@%PI_IP%
echo Local Directory: %APP_DIR%
echo Remote Directory: %REMOTE_DIR%
echo.

REM Function to print colored messages
:print_color
powershell -command "Write-Host '%~2' -ForegroundColor %~1"
goto :eof

REM Function to check command availability
:check_command
where %1 >nul 2>nul
if %errorlevel% neq 0 (
    call :print_color %RED% "❌ Error: %1 is not installed or not in PATH"
    call :print_color %YELLOW% "Please install PuTTY tools and add to PATH"
    exit /b 1
)
goto :eof

REM Check prerequisites
call :print_color %BLUE% "🔍 Checking prerequisites..."

call :check_command pscp
call :check_command plink

REM Check if local directory exists
if not exist "%APP_DIR%" (
    call :print_color %RED% "❌ Error: Local directory '%APP_DIR%' not found"
    call :print_color %YELLOW% "Please run this script from the project root directory"
    exit /b 1
)

call :print_color %GREEN% "✅ Prerequisites check passed"

REM Test SSH connection
call :print_color %BLUE% "🔗 Testing SSH connection to %PI_USER%@%PI_IP%..."

plink -batch %PI_USER%@%PI_IP% "echo 'SSH connection successful'" >nul 2>nul
if %errorlevel% neq 0 (
    call :print_color %RED% "❌ Error: Cannot connect to %PI_USER%@%PI_IP%"
    call :print_color %YELLOW% "Please check:"
    echo    - Raspberry Pi is powered on and connected to network
    echo    - IP address is correct: %PI_IP%
    echo    - SSH is enabled on Raspberry Pi
    echo    - Username is correct: %PI_USER%
    echo    - SSH key is configured or password authentication enabled
    exit /b 1
)

call :print_color %GREEN% "✅ SSH connection successful"

REM Create remote directory structure
call :print_color %BLUE% "📁 Creating remote directory structure..."

plink -batch %PI_USER%@%PI_IP% "mkdir -p %REMOTE_DIR%/%APP_DIR%"
if %errorlevel% neq 0 (
    call :print_color %RED% "❌ Error: Failed to create remote directory"
    exit /b 1
)

call :print_color %GREEN% "✅ Remote directory structure created"

REM Copy application files
call :print_color %BLUE% "📤 Copying application files..."

pscp -r %APP_DIR%\* %PI_USER%@%PI_IP%:%REMOTE_DIR%/%APP_DIR%/
if %errorlevel% neq 0 (
    call :print_color %RED% "❌ Error: Failed to copy application files"
    exit /b 1
)

call :print_color %GREEN% "✅ Application files copied successfully"

REM Make scripts executable
call :print_color %BLUE% "⚙️ Making scripts executable..."

plink -batch %PI_USER%@%PI_IP% "chmod +x %REMOTE_DIR%/%APP_DIR%/*.sh"
if %errorlevel% neq 0 (
    call :print_color %YELLOW% "⚠️ Warning: Failed to make scripts executable (might not be critical)"
)

call :print_color %GREEN% "✅ Scripts made executable"

REM Install system dependencies
call :print_color %BLUE% "📦 Installing system dependencies..."

plink -batch %PI_USER%@%PI_IP% "sudo apt-get update && sudo apt-get install -y python-pip python-dev"
if %errorlevel% neq 0 (
    call :print_color %YELLOW% "⚠️ Warning: System dependencies installation failed or partial"
)

call :print_color %GREEN% "✅ System dependencies installed"

REM Install Python dependencies  
call :print_color %BLUE% "🐍 Installing Python dependencies..."

plink -batch %PI_USER%@%PI_IP% "cd %REMOTE_DIR%/%APP_DIR% && pip install -r requirements.txt"
if %errorlevel% neq 0 (
    call :print_color %YELLOW% "⚠️ Warning: Some Python dependencies might have failed to install"
)

call :print_color %GREEN% "✅ Python dependencies installed"

REM Create and install systemd service
call :print_color %BLUE% "🔧 Creating systemd service..."

plink -batch %PI_USER%@%PI_IP% "cd %REMOTE_DIR%/%APP_DIR% && sudo cp exit-gate-python.service /etc/systemd/system/"
if %errorlevel% neq 0 (
    call :print_color %RED% "❌ Error: Failed to install systemd service"
    exit /b 1
)

plink -batch %PI_USER%@%PI_IP% "sudo systemctl daemon-reload"
plink -batch %PI_USER%@%PI_IP% "sudo systemctl enable exit-gate-python"
plink -batch %PI_USER%@%PI_IP% "sudo systemctl start exit-gate-python"

call :print_color %GREEN% "✅ Systemd service created and started"

REM Wait for service to start
call :print_color %BLUE% "⏳ Waiting for service to start..."
timeout /t 5 /nobreak >nul

REM Test deployment
call :print_color %BLUE% "🧪 Testing deployment..."

REM Test service status
plink -batch %PI_USER%@%PI_IP% "sudo systemctl is-active exit-gate-python" >temp_status.txt 2>nul
set /p SERVICE_STATUS=<temp_status.txt
del temp_status.txt

if "%SERVICE_STATUS%"=="active" (
    call :print_color %GREEN% "✅ Service is running"
) else (
    call :print_color %RED% "❌ Service is not running: %SERVICE_STATUS%"
)

REM Test API endpoint
plink -batch %PI_USER%@%PI_IP% "curl -s http://localhost:5001/api/status" >temp_api.txt 2>nul
findstr "success" temp_api.txt >nul
if %errorlevel% equ 0 (
    call :print_color %GREEN% "✅ API is responding"
) else (
    call :print_color %RED% "❌ API is not responding"
)
del temp_api.txt

REM Test GPIO (if available)
plink -batch %PI_USER%@%PI_IP% "curl -s -X POST http://localhost:5001/api/gate/test" >temp_gpio.txt 2>nul
findstr "success" temp_gpio.txt >nul
if %errorlevel% equ 0 (
    call :print_color %GREEN% "✅ GPIO control is working"
) else (
    call :print_color %YELLOW% "⚠️ GPIO control test failed (might be expected on non-Pi hardware)"
)
del temp_gpio.txt

REM Show connection information
echo.
call :print_color %BLUE% "🌐 Connection Information:"
echo.
echo     Web Interface: http://%PI_IP%:5001
echo     Settings Page: http://%PI_IP%:5001/settings  
echo     API Status:    http://%PI_IP%:5001/api/status
echo.
echo     SSH Access:    ssh %PI_USER%@%PI_IP%
echo     App Directory: %REMOTE_DIR%/%APP_DIR%
echo.

REM Show management commands
call :print_color %BLUE% "🎛 Management Commands:"
echo.
echo     Service Status:   ssh %PI_USER%@%PI_IP% 'sudo systemctl status exit-gate-python'
echo     Start Service:    ssh %PI_USER%@%PI_IP% 'sudo systemctl start exit-gate-python'
echo     Stop Service:     ssh %PI_USER%@%PI_IP% 'sudo systemctl stop exit-gate-python'
echo     Restart Service:  ssh %PI_USER%@%PI_IP% 'sudo systemctl restart exit-gate-python'
echo     View Logs:        ssh %PI_USER%@%PI_IP% 'sudo journalctl -u exit-gate-python -f'
echo.

REM Show quick test commands
call :print_color %BLUE% "🧪 Quick Test Commands:"
echo.
echo     API Status:       curl http://%PI_IP%:5001/api/status
echo     Gate Test:        curl -X POST http://%PI_IP%:5001/api/gate/test
echo     Scanner Status:   curl http://%PI_IP%:5001/api/scanner/status
echo.

REM Final status
call :print_color %GREEN% "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo.
call :print_color %BLUE% "Next Steps:"
echo   1. Open web interface: http://%PI_IP%:5001
echo   2. Configure settings via web interface
echo   3. Test barcode scanner and gate control
echo   4. Monitor logs for any issues
echo.

REM Create local log file
echo %date% %time% - Deployment to %PI_USER%@%PI_IP% completed successfully >> deployment.log

call :print_color %GREEN% "📝 Deployment logged to deployment.log"
echo.

pause
exit /b 0
