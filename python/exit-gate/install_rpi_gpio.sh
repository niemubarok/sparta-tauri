#!/bin/bash
# Quick RPi.GPIO Installation Script

echo "🍓 Installing RPi.GPIO and dependencies..."

# Install RPi.GPIO
echo "Installing RPi.GPIO..."
sudo pip3 install RPi.GPIO

# Install other dependencies
echo "Installing other Python dependencies..."
sudo pip3 install pyserial requests pillow

# Fix GPIO permissions
echo "Setting up GPIO permissions..."
sudo usermod -a -G gpio pi
sudo chmod 666 /dev/gpiomem

# Test GPIO installation
echo "Testing RPi.GPIO installation..."
python3 -c "
import RPi.GPIO as GPIO
print('✅ RPi.GPIO imported successfully')
GPIO.setmode(GPIO.BCM)
print('✅ GPIO mode set successfully')
GPIO.cleanup()
print('✅ GPIO test completed')
"

echo "✅ Installation completed!"
echo "You may need to logout and login again for group changes to take effect"
