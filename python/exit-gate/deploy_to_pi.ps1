# Exit Gate System Deployment to Raspberry Pi
# PowerShell script untuk copy file ke pi@192.168.10.51

# Configuration
$PI_HOST = "pi@192.168.10.51"
$PI_PATH = "/home/pi/app"
$LOCAL_PATH = "."

function Write-Log {
    param($Message)
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message"
}

Write-Host "🚀 EXIT GATE SYSTEM DEPLOYMENT" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
Write-Host "Target: $PI_HOST" -ForegroundColor Yellow
Write-Host "Remote Path: $PI_PATH" -ForegroundColor Yellow
Write-Host "Local Path: $LOCAL_PATH" -ForegroundColor Yellow
Write-Host ""

# Test SSH connection
Write-Log "Testing SSH connection to $PI_HOST..."
try {
    $result = ssh -o ConnectTimeout=5 $PI_HOST "echo 'SSH connection successful'" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Log "✅ SSH connection successful" -ForegroundColor Green
    } else {
        throw "SSH connection failed"
    }
} catch {
    Write-Log "❌ SSH connection failed" -ForegroundColor Red
    Write-Log "💡 Make sure:" -ForegroundColor Yellow
    Write-Log "   - Raspberry Pi is running"
    Write-Log "   - IP address is correct: 192.168.10.51"
    Write-Log "   - SSH is enabled on Pi"
    Write-Log "   - SSH keys are set up or password is ready"
    exit 1
}

# Create remote directory
Write-Log "Creating remote directory structure..."
ssh $PI_HOST "mkdir -p $PI_PATH/app $PI_PATH/docs $PI_PATH/logs" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Log "✅ Remote directories created" -ForegroundColor Green
} else {
    Write-Log "❌ Failed to create remote directories" -ForegroundColor Red
    exit 1
}

# Copy main application files
Write-Log "📁 Copying main application files..."
scp -r app/ "$PI_HOST`:$PI_PATH/"
if ($LASTEXITCODE -eq 0) {
    Write-Log "✅ App directory copied" -ForegroundColor Green
} else {
    Write-Log "❌ Failed to copy app directory" -ForegroundColor Red
    exit 1
}

# Copy diagnostic and test files
Write-Log "🔧 Copying diagnostic and test files..."
$FilesToCopy = @(
    "test_gate_service_debug.py",
    "test_implementation.py", 
    "quick_gpio_fix.sh",
    "README_IMPLEMENTATION.md",
    "requirements_raspberry_pi.txt",
    "run_gui.py",
    "run_raspberry_pi.py"
)

foreach ($file in $FilesToCopy) {
    if (Test-Path $file) {
        scp $file "$PI_HOST`:$PI_PATH/"
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✅ $file copied" -ForegroundColor Green
        } else {
            Write-Log "❌ Failed to copy $file" -ForegroundColor Red
        }
    } else {
        Write-Log "⚠️ $file not found locally" -ForegroundColor Yellow
    }
}

# Copy config files if they exist
Write-Log "⚙️ Copying configuration files..."
$ConfigFiles = @("config.ini", "requirements.txt")

foreach ($file in $ConfigFiles) {
    if (Test-Path $file) {
        scp $file "$PI_HOST`:$PI_PATH/"
        Write-Log "✅ $file copied" -ForegroundColor Green
    } elseif (Test-Path "app/$file") {
        scp "app/$file" "$PI_HOST`:$PI_PATH/"
        Write-Log "✅ app/$file copied" -ForegroundColor Green
    } else {
        Write-Log "⚠️ $file not found" -ForegroundColor Yellow
    }
}

# Set permissions for executable files
Write-Log "🔒 Setting permissions on remote files..."
ssh $PI_HOST "chmod +x $PI_PATH/quick_gpio_fix.sh $PI_PATH/test_gate_service_debug.py $PI_PATH/test_implementation.py $PI_PATH/run_*.py"
if ($LASTEXITCODE -eq 0) {
    Write-Log "✅ Permissions set" -ForegroundColor Green
} else {
    Write-Log "⚠️ Failed to set some permissions" -ForegroundColor Yellow
}

# Create run script on Pi
Write-Log "📝 Creating run script on Pi..."

# Create setup script content
$setupScriptContent = @'
#!/bin/bash
# Exit Gate System Setup Script for Raspberry Pi

echo "🍓 EXIT GATE SYSTEM - RASPBERRY PI SETUP"
echo "======================================="

cd /home/pi/app

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements_raspberry_pi.txt

# Run GPIO fix
echo "🔧 Running GPIO quick fix..."
sudo ./quick_gpio_fix.sh

# Test implementation
echo "🧪 Testing implementation..."
python3 test_implementation.py

echo ""
echo "✅ Setup completed!"
echo "💡 Next steps:"
echo "   1. Reboot if GPIO fixes were applied: sudo reboot"
echo "   2. Run diagnostics: python3 test_gate_service_debug.py"
echo "   3. Start GUI: python3 run_gui.py"
echo "   4. Check hardware connections"
'@

# Write script to Pi using proper escaping
ssh $PI_HOST @"
cat > $PI_PATH/run_setup.sh << 'SCRIPT_EOF'
$setupScriptContent
SCRIPT_EOF
"@

ssh $PI_HOST "chmod +x $PI_PATH/run_setup.sh"
Write-Log "✅ Setup script created" -ForegroundColor Green

# Verify deployment
Write-Log "🔍 Verifying deployment..."
$RemoteFiles = ssh $PI_HOST "find $PI_PATH -type f | wc -l"
Write-Log "📊 Found $RemoteFiles files on remote Pi"

# Check key files
Write-Log "🔍 Checking key files..."
$KeyFiles = @(
    "app/gate_service.py",
    "app/gui_exit_gate.py", 
    "test_gate_service_debug.py",
    "quick_gpio_fix.sh",
    "run_setup.sh"
)

foreach ($file in $KeyFiles) {
    ssh $PI_HOST "test -f $PI_PATH/$file"
    if ($LASTEXITCODE -eq 0) {
        Write-Log "✅ $file exists on Pi" -ForegroundColor Green
    } else {
        Write-Log "❌ $file missing on Pi" -ForegroundColor Red
    }
}

# Show next steps
Write-Log ""
Write-Host "🎉 DEPLOYMENT COMPLETED!" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps on Raspberry Pi:" -ForegroundColor Yellow
Write-Host "1. SSH to Pi: ssh $PI_HOST"
Write-Host "2. Go to project: cd $PI_PATH"
Write-Host "3. Run setup: ./run_setup.sh"
Write-Host "4. Reboot if needed: sudo reboot"
Write-Host "5. Test system: python3 test_gate_service_debug.py"
Write-Host "6. Start GUI: python3 run_gui.py"
Write-Host ""
Write-Host "🔌 Hardware checklist:" -ForegroundColor Yellow
Write-Host "• Connect GPIO pin 24 to relay IN"
Write-Host "• Connect relay VCC to 5V (if needed)"
Write-Host "• Connect relay GND to GND"
Write-Host "• Connect relay COM/NO to gate motor"
Write-Host ""
Write-Host "🚀 Exit Gate System ready for testing on Pi!" -ForegroundColor Green

# Create deployment info file
$deploymentInfo = @"
Exit Gate System Deployment
===========================
Date: $(Get-Date)
Target: $PI_HOST
Remote Path: $PI_PATH
Files Copied: $RemoteFiles

Next Steps:
1. ssh $PI_HOST
2. cd $PI_PATH
3. ./run_setup.sh
4. sudo reboot (if needed)
5. python3 test_gate_service_debug.py
6. python3 run_gui.py

Hardware Connections:
- GPIO 24 → Relay IN
- 5V → Relay VCC (if needed)
- GND → Relay GND
- Relay COM/NO → Gate Motor
"@

$deploymentInfo | Out-File -FilePath "deployment_info.txt" -Encoding UTF8
Write-Log "📄 Deployment info saved to deployment_info.txt"
