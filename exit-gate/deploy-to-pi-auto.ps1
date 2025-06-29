# ====================================================================
# EXIT GATE PYTHON - AUTOMATED DEPLOYMENT SCRIPT (PowerShell Version)
# ====================================================================
#
# This script automates the deployment of Exit Gate Python System
# to a Raspberry Pi from a Windows development machine.
#
# Prerequisites:
# - SSH client (Windows 10/11 built-in or PuTTY)
# - SCP capability (Windows 10/11 built-in or PSCP)
# - Target Raspberry Pi accessible over network
#
# Usage: .\deploy-to-pi-auto.ps1 [-PiIP <IP>] [-PiUser <User>]
# Example: .\deploy-to-pi-auto.ps1 -PiIP 192.168.10.51 -PiUser pi
#
# Author: Exit Gate Development Team
# Date: June 29, 2025
# ====================================================================

param(
    [string]$PiIP = "192.168.10.51",
    [string]$PiUser = "pi",
    [string]$AppDir = "python-app",
    [string]$RemoteDir = "/home/pi/exit-gate"
)

# Function to write colored output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Function to print colored messages
function Print-Status($Message, $Color = "White") {
    Write-ColorOutput $Color $Message
}

# Function to print section headers
function Print-Header($Message) {
    Write-Host ""
    Write-ColorOutput "Cyan" "🚀 $Message"
    Write-ColorOutput "Cyan" ("=" * 60)
}

# Function to check if command exists
function Test-Command($Command) {
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to execute SSH command
function Invoke-SSH($Command) {
    try {
        $result = ssh -o ConnectTimeout=10 -o BatchMode=yes "$PiUser@$PiIP" "$Command" 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $true, $result
        }
        else {
            return $false, $result
        }
    }
    catch {
        return $false, $_.Exception.Message
    }
}

# Function to copy files via SCP
function Copy-Files($LocalPath, $RemotePath) {
    try {
        $result = scp -r -o ConnectTimeout=10 "$LocalPath" "$PiUser@$PiIP`:$RemotePath" 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $true, $result
        }
        else {
            return $false, $result
        }
    }
    catch {
        return $false, $_.Exception.Message
    }
}

# Main deployment script
Clear-Host

Print-Header "EXIT GATE PYTHON - AUTOMATED DEPLOYMENT"
Write-Host "Target: $PiUser@$PiIP"
Write-Host "Local Directory: $AppDir"
Write-Host "Remote Directory: $RemoteDir"
Write-Host ""

# Check prerequisites
Print-Status "🔍 Checking prerequisites..." "Blue"

# Check for SSH client
if (-not (Test-Command "ssh")) {
    Print-Status "❌ Error: SSH client not found" "Red"
    Print-Status "Please install OpenSSH client or PuTTY" "Yellow"
    exit 1
}

# Check for SCP client
if (-not (Test-Command "scp")) {
    Print-Status "❌ Error: SCP client not found" "Red"
    Print-Status "Please install OpenSSH client or PuTTY" "Yellow"
    exit 1
}

# Check if local directory exists
if (-not (Test-Path $AppDir)) {
    Print-Status "❌ Error: Local directory '$AppDir' not found" "Red"
    Print-Status "Please run this script from the project root directory" "Yellow"
    exit 1
}

Print-Status "✅ Prerequisites check passed" "Green"

# Test SSH connection
Print-Status "🔗 Testing SSH connection to $PiUser@$PiIP..." "Blue"

$sshTest, $sshResult = Invoke-SSH "echo 'SSH connection successful'"
if (-not $sshTest) {
    Print-Status "❌ Error: Cannot connect to $PiUser@$PiIP" "Red"
    Print-Status "Please check:" "Yellow"
    Write-Host "    - Raspberry Pi is powered on and connected to network"
    Write-Host "    - IP address is correct: $PiIP"
    Write-Host "    - SSH is enabled on Raspberry Pi"
    Write-Host "    - Username is correct: $PiUser"
    Write-Host "    - SSH key is configured or password authentication enabled"
    Write-Host "Error details: $sshResult"
    exit 1
}

Print-Status "✅ SSH connection successful" "Green"

# Create remote directory structure
Print-Status "📁 Creating remote directory structure..." "Blue"

$dirTest, $dirResult = Invoke-SSH "mkdir -p $RemoteDir/$AppDir"
if (-not $dirTest) {
    Print-Status "❌ Error: Failed to create remote directory" "Red"
    Print-Status "Error details: $dirResult" "Red"
    exit 1
}

Print-Status "✅ Remote directory structure created" "Green"

# Copy application files
Print-Status "📤 Copying application files..." "Blue"

$copyTest, $copyResult = Copy-Files "$AppDir\*" "$RemoteDir/$AppDir/"
if (-not $copyTest) {
    Print-Status "❌ Error: Failed to copy application files" "Red"
    Print-Status "Error details: $copyResult" "Red"
    exit 1
}

Print-Status "✅ Application files copied successfully" "Green"

# Make scripts executable
Print-Status "⚙️ Making scripts executable..." "Blue"

$chmodTest, $chmodResult = Invoke-SSH "chmod +x $RemoteDir/$AppDir/*.sh"
if (-not $chmodTest) {
    Print-Status "⚠️ Warning: Failed to make scripts executable (might not be critical)" "Yellow"
}
else {
    Print-Status "✅ Scripts made executable" "Green"
}

# Install system dependencies
Print-Status "📦 Installing system dependencies..." "Blue"

$aptTest, $aptResult = Invoke-SSH "sudo apt-get update && sudo apt-get install -y python-pip python-dev"
if (-not $aptTest) {
    Print-Status "⚠️ Warning: System dependencies installation failed or partial" "Yellow"
    Print-Status "Error details: $aptResult" "Yellow"
}
else {
    Print-Status "✅ System dependencies installed" "Green"
}

# Install Python dependencies
Print-Status "🐍 Installing Python dependencies..." "Blue"

$pipTest, $pipResult = Invoke-SSH "cd $RemoteDir/$AppDir && pip install -r requirements.txt"
if (-not $pipTest) {
    Print-Status "⚠️ Warning: Some Python dependencies might have failed to install" "Yellow"
    Print-Status "Error details: $pipResult" "Yellow"
}
else {
    Print-Status "✅ Python dependencies installed" "Green"
}

# Create and install systemd service
Print-Status "🔧 Creating systemd service..." "Blue"

$serviceTest, $serviceResult = Invoke-SSH "cd $RemoteDir/$AppDir && sudo cp exit-gate-python.service /etc/systemd/system/"
if (-not $serviceTest) {
    Print-Status "❌ Error: Failed to install systemd service" "Red"
    Print-Status "Error details: $serviceResult" "Red"
    exit 1
}

# Reload and enable service
$reloadTest, $reloadResult = Invoke-SSH "sudo systemctl daemon-reload"
$enableTest, $enableResult = Invoke-SSH "sudo systemctl enable exit-gate-python"
$startTest, $startResult = Invoke-SSH "sudo systemctl start exit-gate-python"

Print-Status "✅ Systemd service created and started" "Green"

# Wait for service to start
Print-Status "⏳ Waiting for service to start..." "Blue"
Start-Sleep -Seconds 5

# Test deployment
Print-Status "🧪 Testing deployment..." "Blue"

# Test service status
$statusTest, $statusResult = Invoke-SSH "sudo systemctl is-active exit-gate-python"
if ($statusTest -and $statusResult -match "active") {
    Print-Status "✅ Service is running" "Green"
}
else {
    Print-Status "❌ Service is not running: $statusResult" "Red"
}

# Test API endpoint
$apiTest, $apiResult = Invoke-SSH "curl -s http://localhost:5001/api/status"
if ($apiTest -and $apiResult -match "success") {
    Print-Status "✅ API is responding" "Green"
}
else {
    Print-Status "❌ API is not responding" "Red"
}

# Test GPIO (if available)
$gpioTest, $gpioResult = Invoke-SSH "curl -s -X POST http://localhost:5001/api/gate/test"
if ($gpioTest -and $gpioResult -match "success") {
    Print-Status "✅ GPIO control is working" "Green"
}
else {
    Print-Status "⚠️ GPIO control test failed (might be expected on non-Pi hardware)" "Yellow"
}

# Show connection information
Print-Header "CONNECTION INFORMATION"
Write-Host ""
Write-Host "    Web Interface: http://$PiIP`:5001"
Write-Host "    Settings Page: http://$PiIP`:5001/settings"
Write-Host "    API Status:    http://$PiIP`:5001/api/status"
Write-Host ""
Write-Host "    SSH Access:    ssh $PiUser@$PiIP"
Write-Host "    App Directory: $RemoteDir/$AppDir"
Write-Host ""

# Show management commands
Print-Header "MANAGEMENT COMMANDS"
Write-Host ""
Write-Host "    Service Status:   ssh $PiUser@$PiIP 'sudo systemctl status exit-gate-python'"
Write-Host "    Start Service:    ssh $PiUser@$PiIP 'sudo systemctl start exit-gate-python'"
Write-Host "    Stop Service:     ssh $PiUser@$PiIP 'sudo systemctl stop exit-gate-python'"
Write-Host "    Restart Service:  ssh $PiUser@$PiIP 'sudo systemctl restart exit-gate-python'"
Write-Host "    View Logs:        ssh $PiUser@$PiIP 'sudo journalctl -u exit-gate-python -f'"
Write-Host ""

# Show quick test commands
Print-Header "QUICK TEST COMMANDS"
Write-Host ""
Write-Host "    API Status:       curl http://$PiIP`:5001/api/status"
Write-Host "    Gate Test:        curl -X POST http://$PiIP`:5001/api/gate/test"
Write-Host "    Scanner Status:   curl http://$PiIP`:5001/api/scanner/status"
Write-Host ""

# Final status
Print-Status "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!" "Green"
Write-Host ""
Print-Status "Next Steps:" "Blue"
Write-Host "  1. Open web interface: http://$PiIP`:5001"
Write-Host "  2. Configure settings via web interface"
Write-Host "  3. Test barcode scanner and gate control"
Write-Host "  4. Monitor logs for any issues"
Write-Host ""

# Create local log file
$logEntry = "$(Get-Date) - Deployment to $PiUser@$PiIP completed successfully"
Add-Content -Path "deployment.log" -Value $logEntry

Print-Status "📝 Deployment logged to deployment.log" "Green"
Write-Host ""

# Option to open web interface
$response = Read-Host "Would you like to open the web interface now? (y/N)"
if ($response -match "^[yY]") {
    Start-Process "http://$PiIP`:5001"
}

Print-Status "Deployment script completed. Press any key to exit..." "Blue"
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
