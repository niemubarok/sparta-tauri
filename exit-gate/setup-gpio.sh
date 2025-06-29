#!/bin/bash

# GPIO Setup Script for Exit Gate System
# This script configures GPIO permissions and system settings for Raspberry Pi

echo "=== Exit Gate GPIO Setup Script ==="
echo "Configuring Raspberry Pi for Exit Gate GPIO operations"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)"
   exit 1
fi

# Function to add user to groups
setup_user_permissions() {
    local username=${1:-pi}
    
    echo "Setting up permissions for user: $username"
    
    # Add user to required groups
    usermod -a -G gpio $username
    usermod -a -G dialout $username
    usermod -a -G spi $username
    usermod -a -G i2c $username
    
    echo "✓ Added $username to gpio, dialout, spi, i2c groups"
}

# Function to configure GPIO permissions
setup_gpio_permissions() {
    echo "Configuring GPIO permissions..."
    
    # Set GPIO memory permissions
    chmod 666 /dev/gpiomem 2>/dev/null || echo "⚠ /dev/gpiomem not found"
    
    # Create GPIO udev rules
    cat > /etc/udev/rules.d/99-gpio.rules << 'EOF'
# GPIO permissions for exit gate system
KERNEL=="gpiomem", GROUP="gpio", MODE="0664"
KERNEL=="gpio*", GROUP="gpio", MODE="0664"
SUBSYSTEM=="gpio", GROUP="gpio", MODE="0664"
EOF
    
    echo "✓ Created GPIO udev rules"
    
    # Reload udev rules
    udevadm control --reload-rules
    udevadm trigger
    
    echo "✓ Reloaded udev rules"
}

# Function to enable required interfaces
enable_interfaces() {
    echo "Enabling required interfaces..."
    
    # Enable GPIO, SPI, I2C in /boot/config.txt
    CONFIG_FILE="/boot/config.txt"
    
    if [ -f "$CONFIG_FILE" ]; then
        # Backup original config
        cp $CONFIG_FILE ${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)
        
        # Enable GPIO
        if ! grep -q "^dtparam=spi=on" $CONFIG_FILE; then
            echo "dtparam=spi=on" >> $CONFIG_FILE
            echo "✓ Enabled SPI"
        fi
        
        if ! grep -q "^dtparam=i2c=on" $CONFIG_FILE; then
            echo "dtparam=i2c=on" >> $CONFIG_FILE
            echo "✓ Enabled I2C"
        fi
        
        # Add GPIO configuration
        if ! grep -q "# Exit Gate GPIO Configuration" $CONFIG_FILE; then
            cat >> $CONFIG_FILE << 'EOF'

# Exit Gate GPIO Configuration
# GPIO pins for exit gate system
# GPIO 18 = Gate Trigger (Pin 12)
# GPIO 24 = Power LED (Pin 18)  
# GPIO 23 = Busy LED (Pin 16)
# GPIO 25 = Live LED (Pin 22)
EOF
            echo "✓ Added GPIO configuration comments"
        fi
    else
        echo "⚠ /boot/config.txt not found, skipping interface setup"
    fi
}

# Function to install required packages
install_packages() {
    echo "Installing required packages..."
    
    apt-get update
    apt-get install -y \
        gpiod \
        libgpiod-dev \
        python3-gpiozero \
        wiringpi
    
    echo "✓ Installed GPIO packages"
}

# Function to create systemd service for GPIO setup
create_gpio_service() {
    echo "Creating GPIO initialization service..."
    
    cat > /etc/systemd/system/exit-gate-gpio-setup.service << 'EOF'
[Unit]
Description=Exit Gate GPIO Setup
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'echo "Exit Gate GPIO initialized"'
ExecStart=/bin/bash -c 'chown root:gpio /dev/gpiomem && chmod 664 /dev/gpiomem'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable exit-gate-gpio-setup.service
    
    echo "✓ Created and enabled GPIO setup service"
}

# Function to test GPIO functionality
test_basic_gpio() {
    echo "Testing basic GPIO functionality..."
    
    # Test GPIO 18 (Gate Trigger)
    echo 18 > /sys/class/gpio/export 2>/dev/null || echo "GPIO 18 already exported"
    echo out > /sys/class/gpio/gpio18/direction 2>/dev/null
    
    if echo 1 > /sys/class/gpio/gpio18/value 2>/dev/null; then
        echo "✓ GPIO 18 test successful"
        echo 0 > /sys/class/gpio/gpio18/value 2>/dev/null
    else
        echo "⚠ GPIO 18 test failed"
    fi
    
    echo 18 > /sys/class/gpio/unexport 2>/dev/null || true
}

# Main setup process
echo "Starting GPIO setup process..."
echo "════════════════════════════════════"

# Get username (default to pi)
USERNAME=${1:-pi}

# Run setup functions
setup_user_permissions $USERNAME
setup_gpio_permissions
enable_interfaces
install_packages
create_gpio_service
test_basic_gpio

echo ""
echo "════════════════════════════════════"
echo "✓ Exit Gate GPIO setup completed!"
echo ""
echo "Changes made:"
echo "- Added $USERNAME to gpio, dialout, spi, i2c groups"
echo "- Configured GPIO permissions and udev rules"
echo "- Enabled SPI and I2C interfaces"
echo "- Installed GPIO development packages"
echo "- Created GPIO initialization service"
echo ""
echo "⚠ Please reboot the system to apply all changes:"
echo "   sudo reboot"
echo ""
echo "After reboot, test GPIO with:"
echo "   ./test-gpio.sh"
