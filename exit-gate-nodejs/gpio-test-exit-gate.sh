#!/bin/bash
# Quick GPIO Test for Exit Gate Pins
# Tests all pins mentioned in the configuration

echo "🧪 Exit Gate GPIO Quick Test"
echo "============================"

# Define all pins based on your configuration
INPUT_PINS=(18 27 4 17)
OUTPUT_PINS=(24 23 25)

echo "[INFO] Testing INPUT pins (should be readable):"
for pin in "${INPUT_PINS[@]}"; do
    echo -n "GPIO $pin: "
    if [ -f "/sys/class/gpio/gpio$pin/value" ]; then
        value=$(cat /sys/class/gpio/gpio$pin/value 2>/dev/null)
        direction=$(cat /sys/class/gpio/gpio$pin/direction 2>/dev/null)
        echo "✅ direction=$direction, value=$value"
    else
        echo "❌ NOT ACCESSIBLE - needs setup"
    fi
done

echo ""
echo "[INFO] Testing OUTPUT pins (should be writable):"
for pin in "${OUTPUT_PINS[@]}"; do
    echo -n "GPIO $pin: "
    if [ -f "/sys/class/gpio/gpio$pin/value" ]; then
        direction=$(cat /sys/class/gpio/gpio$pin/direction 2>/dev/null)
        current_value=$(cat /sys/class/gpio/gpio$pin/value 2>/dev/null)
        
        # Try to write to it
        if echo "1" > /sys/class/gpio/gpio$pin/value 2>/dev/null; then
            echo "✅ direction=$direction, writable (set to 1, was $current_value)"
            # Set back to 0
            echo "0" > /sys/class/gpio/gpio$pin/value 2>/dev/null
        else
            echo "⚠️  direction=$direction, READ-ONLY (value=$current_value)"
        fi
    else
        echo "❌ NOT ACCESSIBLE - needs setup"
    fi
done

echo ""
echo "[SUMMARY] Pin Status:"
echo "INPUT (Active Low):  GPIO 18=LOOP1, 27=LOOP2, 4=STRUK, 17=EMERGENCY"
echo "OUTPUT (Active High): GPIO 24=TRIGGER1, 23=TRIGGER2, 25=LED_LIVE"
echo ""

# Count accessible pins
accessible_count=0
total_pins=$((${#INPUT_PINS[@]} + ${#OUTPUT_PINS[@]}))

for pin in "${INPUT_PINS[@]}" "${OUTPUT_PINS[@]}"; do
    if [ -f "/sys/class/gpio/gpio$pin/value" ]; then
        ((accessible_count++))
    fi
done

echo "Accessible pins: $accessible_count/$total_pins"

if [ $accessible_count -eq $total_pins ]; then
    echo "🎉 ALL GPIO PINS ARE ACCESSIBLE!"
    echo "You can now use the exit gate application normally."
else
    echo "⚠️  Some pins need setup. Run:"
    echo "sudo ./gpio-setup-exit-gate.sh"
    echo "or"  
    echo "sudo ./gpio-permission-fix.sh"
fi
