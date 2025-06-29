#!/bin/bash
# Manual GPIO Setup untuk Pin yang Bermasalah
# Khusus untuk GPIO 24 dan 25 yang masih tidak accessible

echo "🔧 Manual GPIO Setup - Pin 24 & 25"
echo "=================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

# Function to manually setup a specific GPIO pin
manual_setup_pin() {
    local pin=$1
    local direction=$2
    local name=$3
    
    echo "[MANUAL] Setting up GPIO $pin ($name)..."
    
    # Force unexport first
    echo $pin > /sys/class/gpio/unexport 2>/dev/null || true
    echo "  - Unexported GPIO $pin"
    
    # Wait a bit
    sleep 0.5
    
    # Force export
    echo $pin > /sys/class/gpio/export 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "  ✅ GPIO $pin exported successfully"
    else
        echo "  ⚠️  GPIO $pin export may have failed, but continuing..."
    fi
    
    # Wait for filesystem to catch up
    sleep 1
    
    # Check if directory exists
    if [ -d "/sys/class/gpio/gpio$pin" ]; then
        echo "  ✅ GPIO $pin directory exists"
        
        # Set direction
        echo $direction > /sys/class/gpio/gpio$pin/direction 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "  ✅ GPIO $pin direction set to $direction"
        else
            echo "  ❌ Failed to set GPIO $pin direction"
            return 1
        fi
        
        # Fix permissions aggressively
        chown root:gpio /sys/class/gpio/gpio$pin/direction 2>/dev/null
        chown root:gpio /sys/class/gpio/gpio$pin/value 2>/dev/null
        chmod 660 /sys/class/gpio/gpio$pin/direction 2>/dev/null
        chmod 660 /sys/class/gpio/gpio$pin/value 2>/dev/null
        echo "  ✅ GPIO $pin permissions fixed"
        
        # Set initial value for output pins
        if [ "$direction" = "out" ]; then
            echo "0" > /sys/class/gpio/gpio$pin/value 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "  ✅ GPIO $pin initial value set to 0"
            else
                echo "  ⚠️  Could not set initial value for GPIO $pin"
            fi
        fi
        
        # Test the pin
        if [ "$direction" = "out" ]; then
            # Test write capability
            echo "1" > /sys/class/gpio/gpio$pin/value 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "  ✅ GPIO $pin write test successful"
                echo "0" > /sys/class/gpio/gpio$pin/value 2>/dev/null
            else
                echo "  ❌ GPIO $pin write test failed"
                return 1
            fi
        else
            # Test read capability
            local value=$(cat /sys/class/gpio/gpio$pin/value 2>/dev/null)
            if [ $? -eq 0 ]; then
                echo "  ✅ GPIO $pin read test successful (value: $value)"
            else
                echo "  ❌ GPIO $pin read test failed"
                return 1
            fi
        fi
        
    else
        echo "  ❌ GPIO $pin directory does not exist after export"
        return 1
    fi
    
    echo "  🎉 GPIO $pin ($name) setup complete!"
    echo ""
    return 0
}

# Setup the problematic pins
echo "Setting up problematic GPIO pins..."
echo ""

# GPIO 24 - TRIGGER1 (Output)
manual_setup_pin 24 out "TRIGGER1"

# GPIO 25 - LED_LIVE (Output) 
manual_setup_pin 25 out "LED_LIVE"

echo "🧪 Testing all pins after setup..."
echo ""

# Test all pins
declare -A ALL_PINS=(
    [18]="LOOP1:in"
    [27]="LOOP2:in"
    [4]="STRUK:in"
    [17]="EMERGENCY:in"
    [24]="TRIGGER1:out"
    [23]="TRIGGER2:out"
    [25]="LED_LIVE:out"
)

accessible_count=0
total_count=0

for pin in "${!ALL_PINS[@]}"; do
    ((total_count++))
    IFS=':' read -r name direction <<< "${ALL_PINS[$pin]}"
    
    echo -n "GPIO $pin ($name): "
    
    if [ -f "/sys/class/gpio/gpio$pin/value" ]; then
        current_direction=$(cat /sys/class/gpio/gpio$pin/direction 2>/dev/null)
        
        if [ "$direction" = "out" ]; then
            # Test write
            if echo "1" > /sys/class/gpio/gpio$pin/value 2>/dev/null; then
                echo "✅ writable (direction=$current_direction)"
                echo "0" > /sys/class/gpio/gpio$pin/value 2>/dev/null
                ((accessible_count++))
            else
                echo "⚠️  read-only (direction=$current_direction)"
            fi
        else
            # Test read
            value=$(cat /sys/class/gpio/gpio$pin/value 2>/dev/null)
            if [ $? -eq 0 ]; then
                echo "✅ readable (direction=$current_direction, value=$value)"
                ((accessible_count++))
            else
                echo "❌ not readable"
            fi
        fi
    else
        echo "❌ NOT ACCESSIBLE"
    fi
done

echo ""
echo "📊 Final Status: $accessible_count/$total_count pins accessible"

if [ $accessible_count -eq $total_count ]; then
    echo "🎉 ALL GPIO PINS ARE NOW ACCESSIBLE!"
    echo ""
    echo "You can now:"
    echo "1. Test the web interface at http://your-pi-ip:3000"
    echo "2. Use the GPIO test buttons in the web interface"
    echo "3. Restart the exit-gate service: sudo systemctl restart exit-gate"
else
    echo "⚠️  Some pins still need attention. Check individual pin status above."
fi

echo ""
echo "Manual GPIO setup complete!"
