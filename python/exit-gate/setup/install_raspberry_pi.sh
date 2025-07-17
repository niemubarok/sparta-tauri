#!/bin/bash
# Installation script for Raspberry Pi with Python 2.7
# Handles PIL/Pillow compatibility issues

echo "=== Exit Gate System - Raspberry Pi Installation ==="
echo "Python 2.7 compatible installation"

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "Warning: This script is optimized for Raspberry Pi"
fi

# Update system
echo "Updating system packages..."
sudo apt-get update

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y python-pip python-dev python-setuptools
sudo apt-get install -y python-rpi.gpio python-serial
sudo apt-get install -y libjpeg-dev zlib1g-dev libpng-dev libfreetype6-dev

# Install PIL/Pillow system package (recommended approach)
echo "Installing PIL system package..."
sudo apt-get install -y python-pil python-pil.imagetk python-imaging-tk

# Install pygame for audio
echo "Installing pygame..."
sudo apt-get install -y python-pygame

# Install other system packages
sudo apt-get install -y python-flask python-requests

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    virtualenv .venv -p python2.7
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip==20.3.4  # Last version supporting Python 2.7

# Function to install package with fallback
install_with_fallback() {
    package=$1
    echo "Installing $package..."
    
    if ! pip install "$package"; then
        echo "Failed to install $package via pip, trying alternatives..."
        
        # Try with --no-deps
        if ! pip install --no-deps "$package"; then
            echo "Warning: Could not install $package"
            return 1
        fi
    fi
    return 0
}

# Install core packages
echo "Installing core Python packages..."
install_with_fallback "flask==1.0.4"
install_with_fallback "werkzeug==0.16.1"
install_with_fallback "jinja2==2.10.3"
install_with_fallback "markupsafe==1.1.1"
install_with_fallback "requests==2.25.1"
install_with_fallback "couchdb==1.2"
install_with_fallback "pyserial==3.4"
install_with_fallback "configparser==4.0.2"
install_with_fallback "enum34==1.1.10"

# Try to install Pillow as fallback (if system PIL doesn't work)
echo "Checking PIL/Pillow installation..."
python -c "from PIL import Image; print('PIL/Pillow is working')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "System PIL not working, trying to install Pillow..."
    
    # Try different Pillow versions
    for version in "5.1.0" "4.3.0" "3.4.2"; do
        echo "Trying Pillow version $version..."
        if pip install "pillow==$version"; then
            echo "Successfully installed Pillow $version"
            break
        fi
    done
    
    # Test again
    python -c "from PIL import Image; print('PIL/Pillow is working')" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "Warning: PIL/Pillow installation failed. Camera features may not work."
        echo "You can try manually: sudo apt-get install python-pil python-pil.imagetk"
    fi
else
    echo "PIL/Pillow is working correctly"
fi

# Create a simple test script
echo "Creating test script..."
cat > test_installation.py << 'EOF'
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test installation on Raspberry Pi"""

print("Testing Exit Gate System installation...")

# Test basic imports
try:
    import flask
    print("✓ Flask: OK")
except ImportError as e:
    print("✗ Flask: FAILED - {}".format(e))

try:
    import couchdb
    print("✓ CouchDB: OK")
except ImportError as e:
    print("✗ CouchDB: FAILED - {}".format(e))

try:
    import serial
    print("✓ PySerial: OK")
except ImportError as e:
    print("✗ PySerial: FAILED - {}".format(e))

# Test PIL/Pillow
try:
    from PIL import Image
    print("✓ PIL/Pillow: OK")
except ImportError as e:
    print("✗ PIL/Pillow: FAILED - {}".format(e))
    print("  Try: sudo apt-get install python-pil python-pil.imagetk")

# Test GPIO (only on Raspberry Pi)
try:
    import RPi.GPIO as GPIO
    print("✓ RPi.GPIO: OK")
except ImportError as e:
    print("✗ RPi.GPIO: FAILED - {}".format(e))
    print("  Try: sudo apt-get install python-rpi.gpio")

# Test pygame
try:
    import pygame
    print("✓ Pygame: OK")
except ImportError as e:
    print("✗ Pygame: FAILED - {}".format(e))
    print("  Try: sudo apt-get install python-pygame")

print("\nInstallation test completed!")
EOF

# Make test script executable
chmod +x test_installation.py

# Run test
echo "Running installation test..."
python test_installation.py

echo ""
echo "=== Installation completed ==="
echo "To start the application:"
echo "  cd app"
echo "  python gui_exit_gate.py"
echo ""
echo "To test the installation:"
echo "  python test_installation.py"
echo ""
echo "If you encounter PIL/Pillow issues, try:"
echo "  sudo apt-get install python-pil python-pil.imagetk python-imaging-tk"
