#!/bin/bash

# GPIO Test Script for Exit Gate System
# Run this script on Raspberry Pi to test GPIO functionality

echo "=== Exit Gate GPIO Test Script ==="
echo "This script will test all GPIO pins used by the exit gate system"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "Warning: Running as root. GPIO operations may work but user permissions won't be tested."
   echo ""
fi

# Default GPIO pins (can be modified)
GATE_TRIGGER_PIN=${1:-18}
POWER_LED_PIN=${2:-24}
BUSY_LED_PIN=${3:-23}
LIVE_LED_PIN=${4:-25}

echo "Testing GPIO pins:"
echo "- Gate Trigger: GPIO $GATE_TRIGGER_PIN (Pin 12)"
echo "- Power LED: GPIO $POWER_LED_PIN (Pin 18)"
echo "- Busy LED: GPIO $BUSY_LED_PIN (Pin 16)"
echo "- Live LED: GPIO $LIVE_LED_PIN (Pin 22)"
echo ""

# Function to test individual GPIO pin
test_gpio_pin() {
    local pin=$1
    local name=$2
    local duration=${3:-1}
    
    echo "Testing $name (GPIO $pin)..."
    
    # Export GPIO
    if ! echo $pin > /sys/class/gpio/export 2>/dev/null; then
        echo "  GPIO $pin already exported or export failed"
    fi
    
    # Set direction to output
    if echo out > /sys/class/gpio/gpio$pin/direction 2>/dev/null; then
        echo "  ✓ Set GPIO $pin to output mode"
    else
        echo "  ✗ Failed to set GPIO $pin direction"
        return 1
    fi
    
    # Test ON
    if echo 1 > /sys/class/gpio/gpio$pin/value 2>/dev/null; then
        echo "  ✓ GPIO $pin set to HIGH"
    else
        echo "  ✗ Failed to set GPIO $pin to HIGH"
        return 1
    fi
    
    sleep $duration
    
    # Test OFF
    if echo 0 > /sys/class/gpio/gpio$pin/value 2>/dev/null; then
        echo "  ✓ GPIO $pin set to LOW"
    else
        echo "  ✗ Failed to set GPIO $pin to LOW"
        return 1
    fi
    
    # Unexport GPIO
    if echo $pin > /sys/class/gpio/unexport 2>/dev/null; then
        echo "  ✓ GPIO $pin unexported"
    else
        echo "  ⚠ Failed to unexport GPIO $pin (may still be in use)"
    fi
    
    echo "  → $name test completed successfully"
    echo ""
    return 0
}

# Function to cleanup all GPIO pins
cleanup_gpio() {
    echo "Cleaning up GPIO pins..."
    for pin in $GATE_TRIGGER_PIN $POWER_LED_PIN $BUSY_LED_PIN $LIVE_LED_PIN; do
        echo $pin > /sys/class/gpio/unexport 2>/dev/null || true
    done
    echo "GPIO cleanup completed"
}

# Trap cleanup on script exit
trap cleanup_gpio EXIT

# Check GPIO availability
echo "Checking GPIO system availability..."
if [ -d "/sys/class/gpio" ]; then
    echo "✓ GPIO sysfs interface is available"
else
    echo "✗ GPIO sysfs interface not found"
    echo "Make sure you're running on a Raspberry Pi with GPIO support"
    exit 1
fi

# Check user permissions
echo ""
echo "Checking user permissions..."
if groups | grep -q gpio; then
    echo "✓ User is in gpio group"
else
    echo "⚠ User not in gpio group. Run: sudo usermod -a -G gpio $USER"
fi

if [ -w /dev/gpiomem ]; then
    echo "✓ GPIO memory is writable"
else
    echo "⚠ GPIO memory not writable. May need root privileges"
fi

echo ""
echo "Starting GPIO tests..."
echo "═══════════════════════════════════════"

# Test each GPIO pin
success_count=0
total_tests=4

# Test Gate Trigger GPIO
if test_gpio_pin $GATE_TRIGGER_PIN "Gate Trigger" 2; then
    ((success_count++))
fi

# Test Power LED GPIO
if test_gpio_pin $POWER_LED_PIN "Power LED" 1; then
    ((success_count++))
fi

# Test Busy LED GPIO (blink pattern)
echo "Testing Busy LED (GPIO $BUSY_LED_PIN) with blink pattern..."
echo $BUSY_LED_PIN > /sys/class/gpio/export 2>/dev/null || true
echo out > /sys/class/gpio/gpio$BUSY_LED_PIN/direction 2>/dev/null

blink_success=true
for i in {1..3}; do
    echo 1 > /sys/class/gpio/gpio$BUSY_LED_PIN/value 2>/dev/null || blink_success=false
    sleep 0.3
    echo 0 > /sys/class/gpio/gpio$BUSY_LED_PIN/value 2>/dev/null || blink_success=false
    sleep 0.3
done

echo $BUSY_LED_PIN > /sys/class/gpio/unexport 2>/dev/null || true

if $blink_success; then
    echo "  → Busy LED blink test completed successfully"
    ((success_count++))
else
    echo "  → Busy LED blink test failed"
fi
echo ""

# Test Live LED GPIO
if test_gpio_pin $LIVE_LED_PIN "Live LED" 1; then
    ((success_count++))
fi

# Summary
echo "═══════════════════════════════════════"
echo "GPIO Test Summary:"
echo "Successful tests: $success_count/$total_tests"

if [ $success_count -eq $total_tests ]; then
    echo "✓ All GPIO tests passed! Exit gate hardware is ready."
    exit 0
else
    echo "⚠ Some GPIO tests failed. Check connections and permissions."
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Check physical connections"
    echo "2. Verify GPIO pin numbers"
    echo "3. Run: sudo usermod -a -G gpio $USER && sudo reboot"
    echo "4. Test with: sudo $0"
    exit 1
fi
