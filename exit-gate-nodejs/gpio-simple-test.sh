#!/bin/bash
# Simple GPIO Test Script
# Tests GPIO pins used by the Exit Gate system

echo "🧪 GPIO Test Script for Exit Gate System"
echo "========================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    echo "Usage: sudo ./gpio-simple-test.sh"
    exit 1
fi

# GPIO pins used by the application
GATE_PIN=24
LED_PIN=25

echo "[INFO] Testing GPIO pins used by Exit Gate:"
echo "  - Gate Control Pin: $GATE_PIN"
echo "  - LED Indicator Pin: $LED_PIN"
echo ""

# Function to test a GPIO pin
test_gpio_pin() {
    local pin=$1
    local name=$2
    
    echo "Testing $name (GPIO $pin)..."
    
    # Clean up first
    echo $pin > /sys/class/gpio/unexport 2>/dev/null || true
    sleep 0.2
    
    # Export
    if echo $pin > /sys/class/gpio/export 2>/dev/null; then
        echo "  ✅ Export successful"
    else
        echo "  ❌ Export failed"
        return 1
    fi
    
    sleep 0.2
    
    # Set direction
    if echo "out" > /sys/class/gpio/gpio$pin/direction 2>/dev/null; then
        echo "  ✅ Direction set to output"
    else
        echo "  ❌ Failed to set direction"
        echo $pin > /sys/class/gpio/unexport 2>/dev/null || true
        return 1
    fi
    
    # Test high
    if echo "1" > /sys/class/gpio/gpio$pin/value 2>/dev/null; then
        echo "  ✅ Set to HIGH (1)"
    else
        echo "  ❌ Failed to set HIGH"
    fi
    
    sleep 0.5
    
    # Test low
    if echo "0" > /sys/class/gpio/gpio$pin/value 2>/dev/null; then
        echo "  ✅ Set to LOW (0)"
    else
        echo "  ❌ Failed to set LOW"
    fi
    
    # Clean up
    if echo $pin > /sys/class/gpio/unexport 2>/dev/null; then
        echo "  ✅ Cleanup successful"
    else
        echo "  ⚠️  Cleanup warning"
    fi
    
    echo ""
}

# Test each GPIO pin
test_gpio_pin $GATE_PIN "Gate Control"
test_gpio_pin $LED_PIN "LED Indicator"

# Check permissions
echo "📋 Permission Check:"
echo "  /dev/gpiomem:"
ls -la /dev/gpiomem 2>/dev/null || echo "    ❌ Not found"

echo "  /sys/class/gpio/export:"
ls -la /sys/class/gpio/export 2>/dev/null || echo "    ❌ Not found"

echo "  Current user groups:"
if [ -n "$SUDO_USER" ]; then
    groups $SUDO_USER | grep gpio && echo "    ✅ User in gpio group" || echo "    ❌ User not in gpio group"
else
    groups $USER | grep gpio && echo "    ✅ User in gpio group" || echo "    ❌ User not in gpio group"
fi

echo ""
echo "🏁 GPIO Test Complete!"
echo ""
echo "If any tests failed, run the GPIO permission fix script:"
echo "sudo ./gpio-permission-fix.sh"
