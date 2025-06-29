#!/bin/bash

# Exit Gate GPIO Web Interface Test Script
# This script tests the GPIO web interface functionality

echo "🔧 Exit Gate GPIO Web Interface Test"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js first.${NC}"
    exit 1
fi

# Check if the test file exists
TEST_FILE="./test-gpio-web-interface.js"
if [ ! -f "$TEST_FILE" ]; then
    echo -e "${RED}❌ Test file not found: $TEST_FILE${NC}"
    exit 1
fi

# Install chalk if not available (for colored output)
if ! node -e "require('chalk')" 2>/dev/null; then
    echo -e "${YELLOW}📦 Installing chalk for colored output...${NC}"
    npm install chalk --no-save
fi

echo -e "${BLUE}🚀 Starting GPIO Web Interface Test Suite...${NC}"
echo ""

# Run the test
node "$TEST_FILE"

echo ""
echo -e "${BLUE}📋 Additional manual tests you can perform:${NC}"
echo ""
echo "1. Open browser: http://192.168.10.51:3000"
echo "2. Check GPIO Controls section"
echo "3. Test individual output pins:"
echo "   - TRIGGER1 (GPIO 24)"
echo "   - TRIGGER2 (GPIO 23)" 
echo "   - LED_LIVE (GPIO 25)"
echo "4. Monitor input pin status (should update automatically):"
echo "   - LOOP1 (GPIO 18)"
echo "   - LOOP2 (GPIO 27)"
echo "   - STRUK (GPIO 4)"
echo "   - EMERGENCY (GPIO 17)"
echo "5. Test 'Test All Pins' button"
echo ""
echo -e "${GREEN}✨ Test completed!${NC}"
