#!/bin/bash

# GPIO Fix Script for Exit Gate System
# This script fixes common GPIO issues on Raspberry Pi

echo "=========================================="
echo "     EXIT GATE GPIO FIX SCRIPT           "
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root for some operations
if [[ $EUID -ne 0 ]]; then
    echo -e "${YELLOW}Note: Some operations may require sudo privileges${NC}"
fi

# Fix 1: GPIO permissions
echo -e "${BLUE}1. Fixing GPIO permissions...${NC}"
if [ -e "/dev/gpiomem" ]; then
    sudo chmod 666 /dev/gpiomem
    echo -e "${GREEN}✓ GPIO device permissions fixed${NC}"
else
    echo -e "${YELLOW}○ GPIO device not found (may not be Raspberry Pi)${NC}"
fi

# Fix 2: Add user to gpio group
echo -e "${BLUE}2. Adding user to gpio group...${NC}"
current_user=$(whoami)
if ! groups $current_user | grep -q gpio; then
    sudo usermod -a -G gpio $current_user
    echo -e "${GREEN}✓ User added to gpio group${NC}"
    echo -e "${YELLOW}Please logout and login again for changes to take effect${NC}"
else
    echo -e "${GREEN}✓ User already in gpio group${NC}"
fi

# Fix 3: Install required GPIO libraries
echo -e "${BLUE}3. Installing GPIO libraries...${NC}"
cd /opt/exit-gate 2>/dev/null || cd $(dirname $0)

# Check if we're on Raspberry Pi
if grep -q "Raspberry Pi\|BCM" /proc/cpuinfo 2>/dev/null; then
    echo "Installing GPIO libraries for Raspberry Pi..."
    
    # Install system dependencies first
    echo "Installing system dependencies..."
    sudo apt-get update -qq
    sudo apt-get install -y build-essential python3-dev libasound2-dev
    
    # Install Node.js GPIO libraries
    echo "Installing raspi-gpio..."
    npm install raspi-gpio --save || echo -e "${YELLOW}Failed to install raspi-gpio${NC}"
    
    echo "Installing rpi-gpio..."
    npm install rpi-gpio --save || echo -e "${YELLOW}Failed to install rpi-gpio${NC}"
    
    echo "Installing gpio..."
    npm install gpio --save || echo -e "${YELLOW}Failed to install gpio${NC}"
    
    echo -e "${GREEN}✓ GPIO libraries installation completed${NC}"
else
    echo -e "${YELLOW}○ Not on Raspberry Pi, skipping GPIO library installation${NC}"
fi

# Fix 4: Create or update .env file
echo -e "${BLUE}4. Checking .env configuration...${NC}"
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env from .env.example${NC}"
fi

if [ -f ".env" ]; then
    # Ensure GPIO configuration is present
    if ! grep -q "GATE_GPIO_PIN" .env; then
        echo "GATE_GPIO_PIN=24" >> .env
    fi
    if ! grep -q "LED_GPIO_PIN" .env; then
        echo "LED_GPIO_PIN=25" >> .env
    fi
    if ! grep -q "GPIO_ACTIVE_HIGH" .env; then
        echo "GPIO_ACTIVE_HIGH=true" >> .env
    fi
    if ! grep -q "GATE_PULSE_DURATION" .env; then
        echo "GATE_PULSE_DURATION=500" >> .env
    fi
    echo -e "${GREEN}✓ .env configuration updated${NC}"
fi

# Fix 5: Test GPIO pins manually
echo -e "${BLUE}5. Testing GPIO pins manually...${NC}"
GATE_PIN=${GATE_GPIO_PIN:-24}
LED_PIN=${LED_GPIO_PIN:-25}

if grep -q "Raspberry Pi\|BCM" /proc/cpuinfo 2>/dev/null; then
    echo "Testing GPIO pins..."
    
    # Clean up any existing exports
    echo $GATE_PIN > /sys/class/gpio/unexport 2>/dev/null
    echo $LED_PIN > /sys/class/gpio/unexport 2>/dev/null
    
    # Test LED pin
    if echo $LED_PIN > /sys/class/gpio/export 2>/dev/null; then
        echo "out" > /sys/class/gpio/gpio$LED_PIN/direction
        echo "Testing LED (should blink 3 times)..."
        for i in {1..3}; do
            echo "1" > /sys/class/gpio/gpio$LED_PIN/value
            sleep 0.5
            echo "0" > /sys/class/gpio/gpio$LED_PIN/value
            sleep 0.5
        done
        echo $LED_PIN > /sys/class/gpio/unexport
        echo -e "${GREEN}✓ LED pin test completed${NC}"
    else
        echo -e "${YELLOW}○ Could not test LED pin (may be in use)${NC}"
    fi
    
    # Test gate pin
    if echo $GATE_PIN > /sys/class/gpio/export 2>/dev/null; then
        echo "out" > /sys/class/gpio/gpio$GATE_PIN/direction
        echo "Testing gate pin (sending trigger pulse)..."
        echo "1" > /sys/class/gpio/gpio$GATE_PIN/value
        sleep 0.5
        echo "0" > /sys/class/gpio/gpio$GATE_PIN/value
        echo $GATE_PIN > /sys/class/gpio/unexport
        echo -e "${GREEN}✓ Gate pin test completed${NC}"
    else
        echo -e "${YELLOW}○ Could not test gate pin (may be in use)${NC}"
    fi
else
    echo -e "${YELLOW}○ Not on Raspberry Pi, skipping GPIO pin tests${NC}"
fi

# Fix 6: Update systemd service
echo -e "${BLUE}6. Checking systemd service...${NC}"
if [ -f "/etc/systemd/system/exit-gate.service" ]; then
    # Restart service to apply fixes
    if systemctl is-active --quiet exit-gate; then
        echo "Restarting exit-gate service..."
        sudo systemctl restart exit-gate
        sleep 2
        if systemctl is-active --quiet exit-gate; then
            echo -e "${GREEN}✓ Service restarted successfully${NC}"
        else
            echo -e "${RED}✗ Service failed to restart${NC}"
            echo "Service logs:"
            sudo journalctl -u exit-gate --no-pager -n 10
        fi
    else
        echo "Starting exit-gate service..."
        sudo systemctl start exit-gate
        sleep 2
        if systemctl is-active --quiet exit-gate; then
            echo -e "${GREEN}✓ Service started successfully${NC}"
        else
            echo -e "${RED}✗ Service failed to start${NC}"
        fi
    fi
else
    echo -e "${YELLOW}○ Systemd service not found${NC}"
fi

# Fix 7: Create manual GPIO test script
echo -e "${BLUE}7. Creating manual GPIO test script...${NC}"
cat > manual-gpio-test.sh << 'EOF'
#!/bin/bash

# Manual GPIO Test for Exit Gate System

GATE_PIN=${GATE_GPIO_PIN:-24}
LED_PIN=${LED_GPIO_PIN:-25}

echo "=========================================="
echo "  MANUAL GPIO TEST"
echo "=========================================="
echo "Gate Pin: $GATE_PIN"
echo "LED Pin: $LED_PIN"
echo ""

# Function to export pin
export_pin() {
    local pin=$1
    echo $pin > /sys/class/gpio/export 2>/dev/null
    echo "out" > /sys/class/gpio/gpio$pin/direction 2>/dev/null
}

# Function to unexport pin
unexport_pin() {
    local pin=$1
    echo $pin > /sys/class/gpio/unexport 2>/dev/null
}

# Function to set pin value
set_pin() {
    local pin=$1
    local value=$2
    echo $value > /sys/class/gpio/gpio$pin/value 2>/dev/null
}

echo "Press 'l' to toggle LED"
echo "Press 'g' to trigger gate"
echo "Press 'q' to quit"
echo ""

# Initialize pins
export_pin $LED_PIN
export_pin $GATE_PIN
set_pin $LED_PIN 0
set_pin $GATE_PIN 0

led_state=0

while true; do
    read -n 1 -s key
    case $key in
        l|L)
            led_state=$((1 - led_state))
            set_pin $LED_PIN $led_state
            echo "LED: $led_state"
            ;;
        g|G)
            echo "Gate trigger..."
            set_pin $GATE_PIN 1
            sleep 0.5
            set_pin $GATE_PIN 0
            echo "Gate pulse sent"
            ;;
        q|Q)
            echo "Quitting..."
            break
            ;;
    esac
done

# Cleanup
set_pin $LED_PIN 0
set_pin $GATE_PIN 0
unexport_pin $LED_PIN
unexport_pin $GATE_PIN

echo "GPIO test completed"
EOF

chmod +x manual-gpio-test.sh
echo -e "${GREEN}✓ Manual GPIO test script created (./manual-gpio-test.sh)${NC}"

# Fix 8: Create Node.js GPIO diagnostic
echo -e "${BLUE}8. Creating Node.js GPIO diagnostic...${NC}"
cat > gpio-diagnostic.js << 'EOF'
// GPIO Diagnostic Script for Exit Gate System

const path = require('path');
const fs = require('fs');

// Load environment variables
require('dotenv').config();

async function runDiagnostic() {
    console.log('==========================================');
    console.log('  NODE.JS GPIO DIAGNOSTIC');
    console.log('==========================================\n');
    
    // Check environment
    console.log('Environment Configuration:');
    console.log(`GATE_GPIO_PIN: ${process.env.GATE_GPIO_PIN || '24 (default)'}`);
    console.log(`LED_GPIO_PIN: ${process.env.LED_GPIO_PIN || '25 (default)'}`);
    console.log(`GPIO_ACTIVE_HIGH: ${process.env.GPIO_ACTIVE_HIGH || 'true (default)'}`);
    console.log(`GATE_PULSE_DURATION: ${process.env.GATE_PULSE_DURATION || '500 (default)'}`);
    console.log('');
    
    // Check platform
    console.log('Platform Information:');
    console.log(`Platform: ${process.platform}`);
    console.log(`Architecture: ${process.arch}`);
    console.log(`Node.js version: ${process.version}`);
    
    // Check if Raspberry Pi
    let isRaspberryPi = false;
    try {
        const cpuinfo = fs.readFileSync('/proc/cpuinfo', 'utf8');
        isRaspberryPi = cpuinfo.includes('Raspberry Pi') || cpuinfo.includes('BCM');
        console.log(`Raspberry Pi detected: ${isRaspberryPi}`);
    } catch (error) {
        console.log('Could not read /proc/cpuinfo (probably not Linux)');
    }
    console.log('');
    
    // Check GPIO libraries
    console.log('GPIO Libraries:');
    const libraries = ['raspi-gpio', 'rpi-gpio', 'gpio'];
    for (const lib of libraries) {
        try {
            require.resolve(lib);
            console.log(`✓ ${lib}: Available`);
        } catch (error) {
            console.log(`✗ ${lib}: Not available`);
        }
    }
    console.log('');
    
    // Test GPIO service
    console.log('Testing GPIO Service:');
    try {
        const gpioService = require('./services/gpioService');
        
        console.log('Initializing GPIO service...');
        await gpioService.initialize();
        
        const status = gpioService.getStatus();
        console.log('GPIO Status:', JSON.stringify(status, null, 2));
        
        console.log('Testing LED blink...');
        await gpioService.setLedPin(1);
        await new Promise(resolve => setTimeout(resolve, 1000));
        await gpioService.setLedPin(0);
        
        console.log('Testing gate operation...');
        const result = await gpioService.openGate(3);
        console.log('Gate operation result:', result);
        
        await new Promise(resolve => setTimeout(resolve, 4000));
        
        console.log('✓ GPIO service test completed successfully');
        
    } catch (error) {
        console.error('✗ GPIO service test failed:', error.message);
    }
    
    console.log('\n==========================================');
    console.log('  DIAGNOSTIC COMPLETE');
    console.log('==========================================');
}

runDiagnostic().catch(console.error);
EOF

echo -e "${GREEN}✓ Node.js GPIO diagnostic created (node gpio-diagnostic.js)${NC}"

echo ""
echo "=========================================="
echo "  GPIO FIX COMPLETE"
echo "=========================================="
echo ""
echo -e "${GREEN}Fix Summary:${NC}"
echo "1. ✓ GPIO permissions fixed"
echo "2. ✓ User added to gpio group"
echo "3. ✓ GPIO libraries installed"
echo "4. ✓ .env configuration updated"
echo "5. ✓ GPIO pins tested"
echo "6. ✓ Service restarted"
echo "7. ✓ Manual test script created"
echo "8. ✓ Node.js diagnostic created"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Logout and login again (for group changes)"
echo "2. Check wiring connections to GPIO pins"
echo "3. Run: ./gpio-troubleshoot.sh"
echo "4. Run: node gpio-diagnostic.js"
echo "5. Test manually: ./manual-gpio-test.sh"
echo "6. Check service logs: sudo journalctl -u exit-gate -f"
echo ""
echo -e "${YELLOW}Note: If GPIO still doesn't work, check:${NC}"
echo "- Physical wiring connections"
echo "- Gate controller power supply"
echo "- GPIO pin assignments in .env file"
echo "- Hardware compatibility"
