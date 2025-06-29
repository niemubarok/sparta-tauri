#!/bin/bash

# Exit Gate System - Raspberry Pi Installation Script
# This script installs and configures the Exit Gate system on Raspberry Pi

set -e

echo "🚀 Starting Exit Gate System installation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Raspberry Pi
check_raspberry_pi() {
    print_status "Checking if running on Raspberry Pi..."
    
    if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
        print_success "Raspberry Pi detected"
        return 0
    else
        print_warning "Not running on Raspberry Pi - some features may not work"
        return 1
    fi
}

# Update system
update_system() {
    print_status "Updating system packages..."
    sudo apt update
    sudo apt upgrade -y
}

# Install Node.js
install_nodejs() {
    print_status "Installing Node.js..."
    
    # Check if Node.js is already installed
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_status "Node.js already installed: $NODE_VERSION"
        
        # Check if version is acceptable (v16 or higher)
        if [[ $(echo $NODE_VERSION | sed 's/v//') < "16.0.0" ]]; then
            print_warning "Node.js version is too old, updating..."
        else
            return 0
        fi
    fi
    
    # Install Node.js 18.x
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
    
    print_success "Node.js installed: $(node --version)"
}

# Install system dependencies
install_dependencies() {
    print_status "Installing system dependencies..."
    
    # Audio dependencies
    sudo apt install -y alsa-utils pulseaudio
    
    # GPIO dependencies
    sudo apt install -y python3-gpiozero python3-rpi.gpio
    
    # Development tools
    sudo apt install -y git curl wget build-essential
    
    print_success "System dependencies installed"
}

# Setup GPIO permissions
setup_gpio() {
    print_status "Setting up GPIO permissions..."
    
    # Add user to gpio group
    sudo usermod -a -G gpio $USER
    
    # Set GPIO permissions
    sudo chmod 666 /dev/gpiomem 2>/dev/null || true
    
    # Create udev rule for GPIO access
    echo 'SUBSYSTEM=="gpio", KERNEL=="gpiochip*", ACTION=="add", PROGRAM="/bin/sh -c '\''chown root:gpio /sys/class/gpio/export /sys/class/gpio/unexport ; chmod 220 /sys/class/gpio/export /sys/class/gpio/unexport'\''"' | sudo tee /etc/udev/rules.d/99-gpio.rules
    
    print_success "GPIO permissions configured"
}

# Install application
install_application() {
    print_status "Installing Exit Gate application..."
    
    # Create application directory
    APP_DIR="/home/pi/exit-gate-nodejs"
    
    if [ -d "$APP_DIR" ]; then
        print_warning "Application directory exists, backing up..."
        sudo mv "$APP_DIR" "${APP_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Copy application files (assuming they're in current directory)
    sudo mkdir -p "$APP_DIR"
    sudo cp -r . "$APP_DIR/"
    sudo chown -R pi:pi "$APP_DIR"
    
    # Install npm dependencies
    cd "$APP_DIR"
    npm install
    
    # Install Raspberry Pi specific dependencies
    npm install raspi raspi-gpio rpi-gpio gpio --save-optional || print_warning "Some GPIO libraries may not be available"
    
    print_success "Application installed in $APP_DIR"
}

# Configure environment
configure_environment() {
    print_status "Configuring environment..."
    
    APP_DIR="/home/pi/exit-gate-nodejs"
    cd "$APP_DIR"
    
    # Copy environment file if it doesn't exist
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_status "Environment file created from template"
    fi
    
    # Update environment for production
    sed -i 's/NODE_ENV=development/NODE_ENV=production/' .env
    sed -i 's/DEBUG_MODE=true/DEBUG_MODE=false/' .env
    
    print_success "Environment configured"
}

# Setup systemd service
setup_service() {
    print_status "Setting up systemd service..."
    
    APP_DIR="/home/pi/exit-gate-nodejs"
    
    # Copy service file
    sudo cp "$APP_DIR/exit-gate.service" /etc/systemd/system/
    
    # Update service file with correct paths
    sudo sed -i "s|WorkingDirectory=.*|WorkingDirectory=$APP_DIR|" /etc/systemd/system/exit-gate.service
    sudo sed -i "s|ExecStart=.*|ExecStart=$(which node) $APP_DIR/server.js|" /etc/systemd/system/exit-gate.service
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable exit-gate.service
    
    print_success "Systemd service configured"
}

# Configure network
configure_network() {
    print_status "Configuring network settings..."
    
    # Enable SSH (if not already enabled)
    sudo systemctl enable ssh
    sudo systemctl start ssh
    
    # Configure WiFi hotspot (optional)
    read -p "Do you want to configure WiFi hotspot? (y/N): " configure_hotspot
    if [[ $configure_hotspot =~ ^[Yy]$ ]]; then
        setup_wifi_hotspot
    fi
    
    print_success "Network configured"
}

# Setup WiFi hotspot
setup_wifi_hotspot() {
    print_status "Setting up WiFi hotspot..."
    
    # Install hostapd and dnsmasq
    sudo apt install -y hostapd dnsmasq
    
    # Configure hostapd
    sudo tee /etc/hostapd/hostapd.conf > /dev/null <<EOF
interface=wlan0
driver=nl80211
ssid=ExitGate-System
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=parking123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF
    
    # Configure dnsmasq
    sudo tee -a /etc/dnsmasq.conf > /dev/null <<EOF
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOF
    
    # Configure network interface
    sudo tee -a /etc/dhcpcd.conf > /dev/null <<EOF
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
EOF
    
    print_success "WiFi hotspot configured"
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    APP_DIR="/home/pi/exit-gate-nodejs"
    cd "$APP_DIR"
    
    # Test GPIO
    timeout 10s npm run test-gpio || print_warning "GPIO test failed or timed out"
    
    # Test application start
    print_status "Testing application startup..."
    timeout 15s npm start &
    APP_PID=$!
    
    sleep 10
    
    if kill -0 $APP_PID 2>/dev/null; then
        print_success "Application started successfully"
        kill $APP_PID
    else
        print_error "Application failed to start"
        return 1
    fi
    
    print_success "Installation test completed"
}

# Main installation flow
main() {
    print_status "Exit Gate System Installation Script"
    print_status "=================================="
    
    # Pre-installation checks
    check_raspberry_pi
    
    # System setup
    update_system
    install_nodejs
    install_dependencies
    setup_gpio
    
    # Application setup
    install_application
    configure_environment
    setup_service
    configure_network
    
    # Test installation
    test_installation
    
    print_success "Installation completed successfully!"
    print_status ""
    print_status "Next steps:"
    print_status "1. Reboot the system: sudo reboot"
    print_status "2. Start the service: sudo systemctl start exit-gate"
    print_status "3. Check service status: sudo systemctl status exit-gate"
    print_status "4. Access the web interface: http://$(hostname -I | awk '{print $1}'):3000"
    print_status ""
    print_status "GPIO Configuration:"
    print_status "- Gate control: Pin 24"
    print_status "- LED indicator: Pin 25"
    print_status ""
    print_warning "Note: Some changes require a reboot to take effect."
}

# Run main installation
main "$@"
