#!/bin/bash

# GPIO Troubleshooting Script for Exit Gate System
# This script helps diagnose and fix GPIO issues on Raspberry Pi

echo "=========================================="
echo "  EXIT GATE GPIO TROUBLESHOOTING SCRIPT  "
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running on Raspberry Pi
echo -e "${BLUE}1. Checking if running on Raspberry Pi...${NC}"
if grep -q "Raspberry Pi\|BCM" /proc/cpuinfo 2>/dev/null; then
    echo -e "${GREEN}✓ Running on Raspberry Pi${NC}"
    IS_RPI=true
else
    echo -e "${RED}✗ Not running on Raspberry Pi${NC}"
    IS_RPI=false
fi
echo ""

# Check GPIO access
echo -e "${BLUE}2. Checking GPIO access permissions...${NC}"
if [ -e "/dev/gpiomem" ]; then
    echo -e "${GREEN}✓ /dev/gpiomem exists${NC}"
    ls -la /dev/gpiomem
    
    if [ -r "/dev/gpiomem" ]; then
        echo -e "${GREEN}✓ GPIO device is readable${NC}"
    else
        echo -e "${RED}✗ GPIO device is not readable${NC}"
        echo -e "${YELLOW}Fixing permissions...${NC}"
        sudo chmod 666 /dev/gpiomem
    fi
else
    echo -e "${RED}✗ /dev/gpiomem not found${NC}"
fi
echo ""

# Check user groups
echo -e "${BLUE}3. Checking user groups...${NC}"
current_user=$(whoami)
echo "Current user: $current_user"

if groups $current_user | grep -q gpio; then
    echo -e "${GREEN}✓ User is in gpio group${NC}"
else
    echo -e "${RED}✗ User is not in gpio group${NC}"
    echo -e "${YELLOW}Adding user to gpio group...${NC}"
    sudo usermod -a -G gpio $current_user
    echo -e "${YELLOW}Please logout and login again for group changes to take effect${NC}"
fi
echo ""

# Check GPIO libraries
echo -e "${BLUE}4. Checking GPIO libraries...${NC}"
cd /opt/exit-gate 2>/dev/null || cd $(dirname $0)

echo "Checking raspi-gpio..."
if npm list raspi-gpio &>/dev/null; then
    echo -e "${GREEN}✓ raspi-gpio is installed${NC}"
else
    echo -e "${YELLOW}○ raspi-gpio not found${NC}"
fi

echo "Checking rpi-gpio..."
if npm list rpi-gpio &>/dev/null; then
    echo -e "${GREEN}✓ rpi-gpio is installed${NC}"
else
    echo -e "${YELLOW}○ rpi-gpio not found${NC}"
fi

echo "Checking gpio..."
if npm list gpio &>/dev/null; then
    echo -e "${GREEN}✓ gpio is installed${NC}"
else
    echo -e "${YELLOW}○ gpio not found${NC}"
fi
echo ""

# Install missing GPIO libraries
echo -e "${BLUE}5. Installing missing GPIO libraries...${NC}"
if $IS_RPI; then
    echo "Installing GPIO libraries for Raspberry Pi..."
    
    echo "Installing raspi-gpio..."
    npm install raspi-gpio --save 2>/dev/null || echo -e "${YELLOW}Failed to install raspi-gpio${NC}"
    
    echo "Installing rpi-gpio..."
    npm install rpi-gpio --save 2>/dev/null || echo -e "${YELLOW}Failed to install rpi-gpio${NC}"
    
    echo "Installing gpio..."
    npm install gpio --save 2>/dev/null || echo -e "${YELLOW}Failed to install gpio${NC}"
else
    echo -e "${YELLOW}Skipping GPIO library installation (not on Raspberry Pi)${NC}"
fi
echo ""

# Test GPIO pins
echo -e "${BLUE}6. Testing GPIO pins...${NC}"
GATE_PIN=${GATE_GPIO_PIN:-24}
LED_PIN=${LED_GPIO_PIN:-25}

echo "Gate pin: $GATE_PIN"
echo "LED pin: $LED_PIN"

if $IS_RPI; then
    echo "Testing GPIO pin access..."
    
    # Test using GPIO sysfs interface
    if [ -w "/sys/class/gpio/export" ]; then
        echo -e "${GREEN}✓ GPIO sysfs interface is writable${NC}"
        
        # Test gate pin
        echo "Testing gate pin $GATE_PIN..."
        if echo $GATE_PIN > /sys/class/gpio/export 2>/dev/null; then
            echo "out" > /sys/class/gpio/gpio$GATE_PIN/direction 2>/dev/null
            echo "0" > /sys/class/gpio/gpio$GATE_PIN/value 2>/dev/null
            echo -e "${GREEN}✓ Gate pin $GATE_PIN is working${NC}"
            echo $GATE_PIN > /sys/class/gpio/unexport 2>/dev/null
        else
            echo -e "${YELLOW}Gate pin $GATE_PIN may already be in use or unavailable${NC}"
        fi
        
        # Test LED pin
        echo "Testing LED pin $LED_PIN..."
        if echo $LED_PIN > /sys/class/gpio/export 2>/dev/null; then
            echo "out" > /sys/class/gpio/gpio$LED_PIN/direction 2>/dev/null
            echo "1" > /sys/class/gpio/gpio$LED_PIN/value 2>/dev/null
            sleep 1
            echo "0" > /sys/class/gpio/gpio$LED_PIN/value 2>/dev/null
            echo -e "${GREEN}✓ LED pin $LED_PIN is working (should have blinked)${NC}"
            echo $LED_PIN > /sys/class/gpio/unexport 2>/dev/null
        else
            echo -e "${YELLOW}LED pin $LED_PIN may already be in use or unavailable${NC}"
        fi
    else
        echo -e "${RED}✗ GPIO sysfs interface is not writable${NC}"
        echo "Running with sudo to test GPIO access..."
        sudo echo "Testing sudo access..."
    fi
else
    echo -e "${YELLOW}Skipping GPIO pin testing (not on Raspberry Pi)${NC}"
fi
echo ""

# Check environment variables
echo -e "${BLUE}7. Checking environment configuration...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓ .env file found${NC}"
    echo "GPIO configuration:"
    grep -E "^(GATE_GPIO_PIN|LED_GPIO_PIN|GPIO_ACTIVE_HIGH|GATE_PULSE_DURATION)" .env || echo "No GPIO configuration found in .env"
else
    echo -e "${YELLOW}○ No .env file found${NC}"
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created${NC}"
    fi
fi
echo ""

# Check Node.js GPIO test
echo -e "${BLUE}8. Running Node.js GPIO test...${NC}"
cat > gpio_test.js << 'EOF'
const gpioService = require('./services/gpioService');

async function testGpio() {
    try {
        console.log('Initializing GPIO service...');
        await gpioService.initialize();
        
        console.log('GPIO Status:', gpioService.getStatus());
        
        console.log('Testing LED blink...');
        await gpioService.setLedPin(1);
        await new Promise(resolve => setTimeout(resolve, 1000));
        await gpioService.setLedPin(0);
        
        console.log('Testing gate pulse...');
        await gpioService.openGate();
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        console.log('GPIO test completed successfully');
        process.exit(0);
    } catch (error) {
        console.error('GPIO test failed:', error);
        process.exit(1);
    }
}

testGpio();
EOF

if [ -f "services/gpioService.js" ]; then
    echo "Running GPIO test..."
    node gpio_test.js
    rm gpio_test.js
else
    echo -e "${RED}✗ GPIO service not found${NC}"
    rm gpio_test.js
fi
echo ""

# Check system services
echo -e "${BLUE}9. Checking system services...${NC}"
if systemctl is-active --quiet exit-gate; then
    echo -e "${GREEN}✓ exit-gate service is running${NC}"
    echo "Service status:"
    systemctl status exit-gate --no-pager -l
else
    echo -e "${YELLOW}○ exit-gate service is not running${NC}"
    if systemctl is-enabled --quiet exit-gate; then
        echo "Service is enabled but not running. Starting..."
        sudo systemctl start exit-gate
    else
        echo "Service is not enabled."
    fi
fi
echo ""

# Final recommendations
echo -e "${BLUE}10. Recommendations:${NC}"
echo ""
if $IS_RPI; then
    echo -e "${GREEN}✓ Running on Raspberry Pi - GPIO should work${NC}"
    echo "1. Make sure user is in gpio group (logout/login required)"
    echo "2. Check GPIO pin connections:"
    echo "   - Gate control: GPIO $GATE_PIN (Physical pin $(((GATE_PIN == 24 ? 18 : (GATE_PIN == 25 ? 22 : GATE_PIN)))))"
    echo "   - LED indicator: GPIO $LED_PIN (Physical pin $(((LED_PIN == 24 ? 18 : (LED_PIN == 25 ? 22 : LED_PIN)))))"
    echo "3. Verify gate controller is connected and powered"
    echo "4. Check wiring and connections"
    echo "5. Test with manual GPIO commands if needed"
else
    echo -e "${YELLOW}○ Not on Raspberry Pi - GPIO will run in simulation mode${NC}"
fi

echo ""
echo "=========================================="
echo "  TROUBLESHOOTING COMPLETE"
echo "=========================================="
