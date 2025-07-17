#!/bin/bash
# -*- coding: utf-8 -*-
"""
Deploy Exit Gate System to Raspberry Pi
Script untuk copy semua file ke pi@192.168.10.51
"""

# Configuration
PI_HOST="pi@192.168.10.51"
PI_PATH="/home/pi/exit-gate"
LOCAL_PATH="."

echo "🚀 EXIT GATE SYSTEM DEPLOYMENT"
echo "=============================="
echo "Target: $PI_HOST"
echo "Remote Path: $PI_PATH"
echo "Local Path: $LOCAL_PATH"
echo ""

# Function untuk log dengan timestamp
log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

# Test SSH connection
log "Testing SSH connection to $PI_HOST..."
if ssh -o ConnectTimeout=5 $PI_HOST "echo 'SSH connection successful'" > /dev/null 2>&1; then
    log "✅ SSH connection successful"
else
    log "❌ SSH connection failed"
    log "💡 Make sure:"
    log "   - Raspberry Pi is running"
    log "   - IP address is correct: 192.168.10.51"
    log "   - SSH is enabled on Pi"
    log "   - SSH keys are set up or password is ready"
    exit 1
fi

# Create remote directory
log "Creating remote directory structure..."
ssh $PI_HOST "mkdir -p $PI_PATH/app $PI_PATH/docs $PI_PATH/logs" 2>/dev/null
if [ $? -eq 0 ]; then
    log "✅ Remote directories created"
else
    log "❌ Failed to create remote directories"
    exit 1
fi

# Copy main application files
log "📁 Copying main application files..."
scp -r app/ $PI_HOST:$PI_PATH/
if [ $? -eq 0 ]; then
    log "✅ App directory copied"
else
    log "❌ Failed to copy app directory"
    exit 1
fi

# Copy diagnostic and test files
log "🔧 Copying diagnostic and test files..."
FILES_TO_COPY=(
    "test_gate_service_debug.py"
    "test_implementation.py" 
    "quick_gpio_fix.sh"
    "README_IMPLEMENTATION.md"
    "requirements_raspberry_pi.txt"
    "run_gui.py"
    "run_raspberry_pi.py"
)

for file in "${FILES_TO_COPY[@]}"; do
    if [ -f "$file" ]; then
        scp "$file" $PI_HOST:$PI_PATH/
        if [ $? -eq 0 ]; then
            log "✅ $file copied"
        else
            log "❌ Failed to copy $file"
        fi
    else
        log "⚠️ $file not found locally"
    fi
done

# Copy config files if they exist
log "⚙️ Copying configuration files..."
CONFIG_FILES=(
    "config.ini"
    "requirements.txt"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        scp "$file" $PI_HOST:$PI_PATH/
        log "✅ $file copied"
    elif [ -f "app/$file" ]; then
        scp "app/$file" $PI_HOST:$PI_PATH/
        log "✅ app/$file copied"
    else
        log "⚠️ $file not found"
    fi
done

# Set permissions for executable files
log "🔒 Setting permissions on remote files..."
ssh $PI_HOST "chmod +x $PI_PATH/quick_gpio_fix.sh $PI_PATH/test_gate_service_debug.py $PI_PATH/test_implementation.py $PI_PATH/run_*.py"
if [ $? -eq 0 ]; then
    log "✅ Permissions set"
else
    log "⚠️ Failed to set some permissions"
fi

# Create run script on Pi
log "📝 Creating run script on Pi..."
ssh $PI_HOST "cat > $PI_PATH/run_setup.sh << 'EOF'
#!/bin/bash
# Exit Gate System Setup Script for Raspberry Pi

echo '🍓 EXIT GATE SYSTEM - RASPBERRY PI SETUP'
echo '======================================='

cd /home/pi/exit-gate

# Install Python dependencies
echo '📦 Installing Python dependencies...'
pip3 install -r requirements_raspberry_pi.txt

# Run GPIO fix
echo '🔧 Running GPIO quick fix...'
sudo ./quick_gpio_fix.sh

# Test implementation
echo '🧪 Testing implementation...'
python3 test_implementation.py

echo ''
echo '✅ Setup completed!'
echo '💡 Next steps:'
echo '   1. Reboot if GPIO fixes were applied: sudo reboot'
echo '   2. Run diagnostics: python3 test_gate_service_debug.py'
echo '   3. Start GUI: python3 run_gui.py'
echo '   4. Check hardware connections'
EOF"

ssh $PI_HOST "chmod +x $PI_PATH/run_setup.sh"
log "✅ Setup script created"

# Verify deployment
log "🔍 Verifying deployment..."
REMOTE_FILES=$(ssh $PI_HOST "find $PI_PATH -type f | wc -l")
log "📊 Found $REMOTE_FILES files on remote Pi"

# Check key files
KEY_FILES=(
    "app/gate_service.py"
    "app/gui_exit_gate.py"
    "test_gate_service_debug.py"
    "quick_gpio_fix.sh"
    "run_setup.sh"
)

log "🔍 Checking key files..."
for file in "${KEY_FILES[@]}"; do
    if ssh $PI_HOST "test -f $PI_PATH/$file"; then
        log "✅ $file exists on Pi"
    else
        log "❌ $file missing on Pi"
    fi
done

# Show next steps
log ""
log "🎉 DEPLOYMENT COMPLETED!"
log "======================"
log ""
log "📋 Next steps on Raspberry Pi:"
log "1. SSH to Pi: ssh $PI_HOST"
log "2. Go to project: cd $PI_PATH"
log "3. Run setup: ./run_setup.sh"
log "4. Reboot if needed: sudo reboot"
log "5. Test system: python3 test_gate_service_debug.py"
log "6. Start GUI: python3 run_gui.py"
log ""
log "🔌 Hardware checklist:"
log "• Connect GPIO pin 24 to relay IN"
log "• Connect relay VCC to 5V (if needed)"
log "• Connect relay GND to GND"
log "• Connect relay COM/NO to gate motor"
log ""
log "🚀 Exit Gate System ready for testing on Pi!"

# Create deployment info file
cat > deployment_info.txt << EOF
Exit Gate System Deployment
===========================
Date: $(date)
Target: $PI_HOST
Remote Path: $PI_PATH
Files Copied: $REMOTE_FILES

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
EOF

log "📄 Deployment info saved to deployment_info.txt"
