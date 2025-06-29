#!/bin/bash

# Make all scripts executable
echo "Making scripts executable..."

chmod +x build-rpi.sh
chmod +x deploy-to-pi.sh 
chmod +x test-rpi.sh
chmod +x test-gpio.sh
chmod +x setup-gpio.sh

echo "✓ All scripts are now executable"
echo ""
echo "Available scripts:"
echo "- build-rpi.sh      : Build for Raspberry Pi 3"
echo "- deploy-to-pi.sh   : Deploy to Raspberry Pi"
echo "- test-rpi.sh       : Test system on Pi"
echo "- setup-gpio.sh     : Setup GPIO permissions (run on Pi with sudo)"
echo "- test-gpio.sh      : Test GPIO functionality (run on Pi)"
echo ""
echo "Usage examples:"
echo "  ./build-rpi.sh"
echo "  ./deploy-to-pi.sh 192.168.1.100 pi"
echo "  # On Raspberry Pi:"
echo "  sudo ./setup-gpio.sh"
echo "  ./test-gpio.sh"
