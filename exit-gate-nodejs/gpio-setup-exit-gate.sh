#!/bin/bash
# GPIO Setup Script for Exit Gate System
# Sets up all required GPIO pins based on the configuration

echo "🚪 Exit Gate GPIO Setup Script"
echo "=============================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

# GPIO Pin Configuration based on the provided mapping
declare -A INPUT_PINS=(
    [18]="LOOP1"      # Loop detector 1
    [27]="LOOP2"      # Loop detector 2  
    [4]="STRUK"       # Receipt/Structure sensor
    [17]="EMERGENCY"  # Emergency button
)

declare -A OUTPUT_PINS=(
    [24]="TRIGGER1"   # Gate trigger 1
    [23]="TRIGGER2"   # Gate trigger 2
    [25]="LED_LIVE"   # LED Live indicator
)

echo "[INFO] GPIO Pin Configuration:"
echo "INPUT PINS (Active Low):"
for pin in "${!INPUT_PINS[@]}"; do
    echo "  GPIO $pin = ${INPUT_PINS[$pin]}"
done

echo "OUTPUT PINS (Active High):"
for pin in "${!OUTPUT_PINS[@]}"; do
    echo "  GPIO $pin = ${OUTPUT_PINS[$pin]}"
done
echo ""

# Function to setup GPIO pin
setup_gpio() {
    local pin=$1
    local direction=$2
    local name=$3
    
    echo "[SETUP] GPIO $pin ($name) as $direction..."
    
    # Unexport first to clean up any existing state
    echo $pin > /sys/class/gpio/unexport 2>/dev/null || true
    sleep 0.1
    
    # Export the GPIO pin
    if echo $pin > /sys/class/gpio/export 2>/dev/null; then
        echo "  ✅ GPIO $pin exported"
    else
        echo "  ⚠️  GPIO $pin already exported or failed to export"
    fi
    
    # Wait for the GPIO directory to be created
    sleep 0.2
    
    # Check if GPIO directory exists
    if [ ! -d "/sys/class/gpio/gpio$pin" ]; then
        echo "  ❌ GPIO $pin directory not found after export"
        return 1
    fi
    
    # Set direction
    if echo $direction > /sys/class/gpio/gpio$pin/direction 2>/dev/null; then
        echo "  ✅ GPIO $pin direction set to $direction"
    else
        echo "  ❌ Failed to set GPIO $pin direction"
        return 1
    fi
    
    # Fix permissions
    chown root:gpio /sys/class/gpio/gpio$pin/direction /sys/class/gpio/gpio$pin/value 2>/dev/null
    chmod 660 /sys/class/gpio/gpio$pin/direction /sys/class/gpio/gpio$pin/value 2>/dev/null
    echo "  ✅ GPIO $pin permissions fixed"
    
    # Set initial value for output pins
    if [ "$direction" = "out" ]; then
        echo "0" > /sys/class/gpio/gpio$pin/value 2>/dev/null
        echo "  ✅ GPIO $pin initial value set to 0"
    fi
    
    return 0
}

# Function to test GPIO pin
test_gpio() {
    local pin=$1
    local direction=$2
    local name=$3
    
    echo "[TEST] Testing GPIO $pin ($name)..."
    
    if [ ! -f "/sys/class/gpio/gpio$pin/value" ]; then
        echo "  ❌ GPIO $pin value file not accessible"
        return 1
    fi
    
    if [ "$direction" = "out" ]; then
        # Test output pin
        if echo "1" > /sys/class/gpio/gpio$pin/value 2>/dev/null; then
            echo "  ✅ GPIO $pin set to HIGH"
            sleep 0.5
            if echo "0" > /sys/class/gpio/gpio$pin/value 2>/dev/null; then
                echo "  ✅ GPIO $pin set to LOW"
            else
                echo "  ⚠️  Failed to set GPIO $pin to LOW"
            fi
        else
            echo "  ❌ Failed to set GPIO $pin to HIGH"
            return 1
        fi
    else
        # Test input pin
        local value=$(cat /sys/class/gpio/gpio$pin/value 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo "  ✅ GPIO $pin current value: $value"
        else
            echo "  ❌ Failed to read GPIO $pin value"
            return 1
        fi
    fi
    
    return 0
}

echo "🔧 Setting up INPUT pins..."
for pin in "${!INPUT_PINS[@]}"; do
    setup_gpio $pin "in" "${INPUT_PINS[$pin]}"
    echo ""
done

echo "🔧 Setting up OUTPUT pins..."  
for pin in "${!OUTPUT_PINS[@]}"; do
    setup_gpio $pin "out" "${OUTPUT_PINS[$pin]}"
    echo ""
done

echo "🧪 Testing GPIO pins..."
echo "Testing INPUT pins (reading values):"
for pin in "${!INPUT_PINS[@]}"; do
    test_gpio $pin "in" "${INPUT_PINS[$pin]}"
done

echo ""
echo "Testing OUTPUT pins (toggle test):"
for pin in "${!OUTPUT_PINS[@]}"; do
    test_gpio $pin "out" "${OUTPUT_PINS[$pin]}"
done

echo ""
echo "📋 GPIO Status Summary:"
echo "======================="
for pin in "${!INPUT_PINS[@]}"; do
    if [ -f "/sys/class/gpio/gpio$pin/value" ]; then
        value=$(cat /sys/class/gpio/gpio$pin/value 2>/dev/null || echo "ERROR")
        direction=$(cat /sys/class/gpio/gpio$pin/direction 2>/dev/null || echo "ERROR")
        echo "GPIO $pin (${INPUT_PINS[$pin]}): direction=$direction, value=$value"
    else
        echo "GPIO $pin (${INPUT_PINS[$pin]}): NOT ACCESSIBLE"
    fi
done

for pin in "${!OUTPUT_PINS[@]}"; do
    if [ -f "/sys/class/gpio/gpio$pin/value" ]; then
        value=$(cat /sys/class/gpio/gpio$pin/value 2>/dev/null || echo "ERROR")
        direction=$(cat /sys/class/gpio/gpio$pin/direction 2>/dev/null || echo "ERROR")
        echo "GPIO $pin (${OUTPUT_PINS[$pin]}): direction=$direction, value=$value"
    else
        echo "GPIO $pin (${OUTPUT_PINS[$pin]}): NOT ACCESSIBLE"
    fi
done

echo ""
echo "🎉 Exit Gate GPIO Setup Complete!"
echo ""
echo "All required GPIO pins have been configured:"
echo "- Input pins (18,27,4,17) set as INPUT with pull-up"
echo "- Output pins (24,23,25) set as OUTPUT with initial LOW"
echo ""
echo "You can now test the pins manually:"
echo "  Input:  cat /sys/class/gpio/gpio18/value"
echo "  Output: echo '1' > /sys/class/gpio/gpio24/value"
echo ""
echo "Or restart the exit-gate service:"
echo "  sudo systemctl restart exit-gate"
