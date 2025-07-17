#!/bin/bash
# -*- coding: utf-8 -*-
"""
Quick GPIO Fix Script untuk Exit Gate System
Memperbaiki permission dan setup GPIO dengan cepat
"""

echo "🔧 EXIT GATE GPIO QUICK FIX"
echo "=========================="

# Function untuk log dengan timestamp
log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

log "Starting GPIO quick fix..."

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi\|BCM" /proc/cpuinfo 2>/dev/null; then
    log "❌ Not running on Raspberry Pi"
    log "💡 GPIO fixes only work on Raspberry Pi"
    exit 1
fi

log "✅ Raspberry Pi detected"

# Fix 1: Add user to gpio group
log "🔒 Adding user to gpio group..."
if groups | grep -q gpio; then
    log "✅ User already in gpio group"
else
    log "Adding user to gpio group..."
    sudo usermod -a -G gpio $USER
    if [ $? -eq 0 ]; then
        log "✅ User added to gpio group"
        REBOOT_REQUIRED=1
    else
        log "❌ Failed to add user to gpio group"
    fi
fi

# Fix 2: Fix GPIO device permissions
log "📁 Fixing GPIO device permissions..."

# Fix /dev/gpiomem
if [ -e /dev/gpiomem ]; then
    sudo chmod 666 /dev/gpiomem
    log "✅ Fixed /dev/gpiomem permissions"
else
    log "⚠️ /dev/gpiomem not found"
fi

# Fix GPIO export/unexport
if [ -e /sys/class/gpio/export ]; then
    sudo chmod 666 /sys/class/gpio/export
    sudo chmod 666 /sys/class/gpio/unexport
    log "✅ Fixed GPIO export permissions"
else
    log "⚠️ GPIO export files not found"
fi

# Fix 3: Create udev rules
log "📝 Creating GPIO udev rules..."
cat > /tmp/99-gpio-exit-gate.rules << 'EOF'
# GPIO permissions for exit gate system
KERNEL=="gpiomem", GROUP="gpio", MODE="0666"
KERNEL=="gpio*", GROUP="gpio", MODE="0666" 
SUBSYSTEM=="gpio", GROUP="gpio", MODE="0666"
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys/class/gpio/export /sys/class/gpio/unexport; chmod 666 /sys/class/gpio/export /sys/class/gpio/unexport'"
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys%p/direction /sys%p/value; chmod 666 /sys%p/direction /sys%p/value'"
EOF

if sudo mv /tmp/99-gpio-exit-gate.rules /etc/udev/rules.d/; then
    log "✅ Created udev rules"
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    log "✅ Reloaded udev rules"
else
    log "❌ Failed to create udev rules"
fi

# Fix 4: Install required packages
log "📦 Checking required packages..."

# Check RPi.GPIO
if python3 -c "import RPi.GPIO" 2>/dev/null; then
    log "✅ RPi.GPIO already installed"
else
    log "Installing RPi.GPIO..."
    if sudo apt-get update && sudo apt-get install -y python3-rpi.gpio; then
        log "✅ RPi.GPIO installed"
    else
        log "❌ Failed to install RPi.GPIO"
    fi
fi

# Check if serial package is available
if python3 -c "import serial" 2>/dev/null; then
    log "✅ pyserial already available"
else
    log "Installing pyserial..."
    if pip3 install pyserial; then
        log "✅ pyserial installed"
    else
        log "❌ Failed to install pyserial"
    fi
fi

# Fix 5: Test GPIO functionality
log "🧪 Testing GPIO functionality..."

# Quick GPIO test script
cat > /tmp/gpio_test.py << 'EOF'
#!/usr/bin/env python3
import sys
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Test pin 24 (common gate pin)
    test_pin = 24
    GPIO.setup(test_pin, GPIO.OUT)
    
    # Quick test
    GPIO.output(test_pin, GPIO.HIGH)
    GPIO.output(test_pin, GPIO.LOW)
    
    GPIO.cleanup()
    print("✅ GPIO test passed")
    sys.exit(0)
except ImportError:
    print("❌ RPi.GPIO not available")
    sys.exit(1)
except Exception as e:
    print(f"❌ GPIO test failed: {e}")
    sys.exit(1)
EOF

if python3 /tmp/gpio_test.py; then
    log "✅ GPIO functionality test passed"
else
    log "⚠️ GPIO functionality test failed"
fi

# Clean up
rm -f /tmp/gpio_test.py

# Fix 6: Check config file
CONFIG_FILE="/path/to/your/app/config.ini"
log "📄 Checking configuration..."

# Create default config if needed
if [ ! -f "app/config.ini" ]; then
    log "Creating default config.ini..."
    cat > app/config.ini << 'EOF'
[gate]
control_mode = gpio
serial_port = /dev/ttyUSB0
baud_rate = 9600
timeout = 5

[gpio]
gate_pin = 24
active_high = true
power_pin = 16
busy_pin = 20
live_pin = 21
pulse_duration = 0.5

[database]
local_db = transactions
remote_url = http://localhost:5984
username = admin
password = password
auto_sync = true

[audio]
enabled = true
volume = 0.7

[camera]
enabled = true
auto_configure = true
EOF
    log "✅ Created default config.ini"
else
    log "✅ config.ini already exists"
fi

# Summary
log ""
log "🎉 GPIO Quick Fix Completed!"
log "=========================="

if [ -n "$REBOOT_REQUIRED" ]; then
    log "⚠️  REBOOT REQUIRED for group changes to take effect"
    log "💡 Run: sudo reboot"
    log ""
fi

log "✅ Next steps:"
log "   1. Reboot if required: sudo reboot"
log "   2. Test implementation: python3 test_implementation.py"
log "   3. Run diagnostic: python3 test_gate_service_debug.py"
log "   4. Start GUI: python3 run_gui.py"
log ""
log "🔌 Hardware checklist:"
log "   • GPIO pin 24 connected to relay IN"
log "   • Relay VCC connected to 5V (if needed)"
log "   • Relay GND connected to GND"
log "   • Relay COM/NO connected to gate motor"
log ""
log "🚀 Exit Gate System should be ready!"
