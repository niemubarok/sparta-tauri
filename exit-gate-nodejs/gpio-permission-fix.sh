#!/bin/bash
# GPIO Permission Fix Script
# Fixes GPIO permissions and access issues for Exit Gate system

echo "🔧 GPIO Permission Fix Script"
echo "============================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

echo "[INFO] Checking current GPIO permissions..."

# Get the actual user (not root when using sudo)
ACTUAL_USER=${SUDO_USER:-$USER}
echo "[INFO] Fixing permissions for user: $ACTUAL_USER"

# 1. Fix /dev/gpiomem permissions
echo "[1] Fixing /dev/gpiomem permissions..."
if [ -e /dev/gpiomem ]; then
    chmod 660 /dev/gpiomem
    chown root:gpio /dev/gpiomem
    echo "✅ /dev/gpiomem permissions fixed"
else
    echo "⚠️  /dev/gpiomem not found"
fi

# 2. Fix /sys/class/gpio permissions
echo "[2] Fixing /sys/class/gpio permissions..."
if [ -d /sys/class/gpio ]; then
    # Make gpio directory accessible
    chmod 755 /sys/class/gpio
    
    # Fix export/unexport permissions
    if [ -f /sys/class/gpio/export ]; then
        chmod 660 /sys/class/gpio/export
        chown root:gpio /sys/class/gpio/export
    fi
    
    if [ -f /sys/class/gpio/unexport ]; then
        chmod 660 /sys/class/gpio/unexport
        chown root:gpio /sys/class/gpio/unexport
    fi
    
    echo "✅ /sys/class/gpio permissions fixed"
else
    echo "⚠️  /sys/class/gpio not found"
fi

# 3. Add user to gpio group (if not already)
echo "[3] Ensuring user is in gpio group..."
if groups $ACTUAL_USER | grep -q '\bgpio\b'; then
    echo "✅ User $ACTUAL_USER is already in gpio group"
else
    usermod -a -G gpio $ACTUAL_USER
    echo "✅ Added user $ACTUAL_USER to gpio group"
fi

# 4. Create udev rules for persistent permissions
echo "[4] Creating udev rules for persistent GPIO access..."
cat > /etc/udev/rules.d/99-gpio.rules << 'EOF'
# GPIO permissions for exit-gate application
KERNEL=="gpiomem", GROUP="gpio", MODE="0660"
SUBSYSTEM=="gpio", GROUP="gpio", MODE="0660"
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys/class/gpio/export /sys/class/gpio/unexport; chmod 220 /sys/class/gpio/export /sys/class/gpio/unexport'"
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys%p/direction /sys%p/value; chmod 660 /sys%p/direction /sys%p/value'"
EOF

echo "✅ udev rules created"

# 5. Reload udev rules
echo "[5] Reloading udev rules..."
udevadm control --reload-rules
udevadm trigger
echo "✅ udev rules reloaded"

# 6. Test GPIO access
echo "[6] Testing GPIO access..."
echo "Testing GPIO 25 export..."

# Clean up any existing gpio25
echo 25 > /sys/class/gpio/unexport 2>/dev/null || true

# Test export
if echo 25 > /sys/class/gpio/export 2>/dev/null; then
    echo "✅ GPIO 25 export successful"
    
    # Test direction setting
    if echo "out" > /sys/class/gpio/gpio25/direction 2>/dev/null; then
        echo "✅ GPIO 25 direction setting successful"
        
        # Test value setting
        if echo "1" > /sys/class/gpio/gpio25/value 2>/dev/null; then
            echo "✅ GPIO 25 value setting successful"
            
            # Clean up
            echo "0" > /sys/class/gpio/gpio25/value 2>/dev/null
            echo 25 > /sys/class/gpio/unexport 2>/dev/null
            echo "✅ GPIO 25 cleanup successful"
        else
            echo "❌ GPIO 25 value setting failed"
        fi
    else
        echo "❌ GPIO 25 direction setting failed"
    fi
else
    echo "❌ GPIO 25 export failed"
fi

# 7. Create GPIO helper script for the application
echo "[7] Creating GPIO helper script..."
cat > /usr/local/bin/gpio-helper.sh << 'EOF'
#!/bin/bash
# GPIO Helper Script for Exit Gate Application

setup_gpio() {
    local pin=$1
    local direction=${2:-out}
    
    # Export GPIO pin
    echo $pin > /sys/class/gpio/export 2>/dev/null || true
    
    # Wait a moment for the GPIO to be available
    sleep 0.1
    
    # Set direction
    if [ -f /sys/class/gpio/gpio$pin/direction ]; then
        echo $direction > /sys/class/gpio/gpio$pin/direction
        # Fix permissions after export
        chown root:gpio /sys/class/gpio/gpio$pin/direction /sys/class/gpio/gpio$pin/value
        chmod 660 /sys/class/gpio/gpio$pin/direction /sys/class/gpio/gpio$pin/value
        echo "GPIO $pin setup complete (direction: $direction)"
    else
        echo "Failed to setup GPIO $pin"
        return 1
    fi
}

cleanup_gpio() {
    local pin=$1
    echo $pin > /sys/class/gpio/unexport 2>/dev/null || true
    echo "GPIO $pin cleaned up"
}

case "$1" in
    setup)
        setup_gpio $2 $3
        ;;
    cleanup)
        cleanup_gpio $2
        ;;
    *)
        echo "Usage: $0 {setup|cleanup} <pin> [direction]"
        exit 1
        ;;
esac
EOF

chmod +x /usr/local/bin/gpio-helper.sh
echo "✅ GPIO helper script created"

# 8. Setup application GPIO pins
echo "[8] Setting up application GPIO pins..."

# Exit Gate GPIO Configuration
# INPUT PINS (Active Low)
/usr/local/bin/gpio-helper.sh setup 18 in   # LOOP 1
/usr/local/bin/gpio-helper.sh setup 27 in   # LOOP 2
/usr/local/bin/gpio-helper.sh setup 4 in    # STRUK
/usr/local/bin/gpio-helper.sh setup 17 in   # EMERGENCY

# OUTPUT PINS (Active High)
/usr/local/bin/gpio-helper.sh setup 24 out  # TRIGGER 1
/usr/local/bin/gpio-helper.sh setup 23 out  # TRIGGER 2
/usr/local/bin/gpio-helper.sh setup 25 out  # LED LIVE

echo "✅ All Exit Gate GPIO pins configured"

echo ""
echo "🎉 GPIO Permission Fix Complete!"
echo ""
echo "Next steps:"
echo "1. Restart the exit-gate service: sudo systemctl restart exit-gate"
echo "2. Test the web interface at http://your-pi-ip:3000"
echo "3. Try the GPIO test buttons in the web interface"
echo ""
echo "If issues persist, check the service logs:"
echo "sudo journalctl -u exit-gate -f"
