#!/bin/bash
# Exit Gate Offline Installer for Raspberry Pi

set -e

APP_NAME="exit-gate-nodejs"
INSTALL_DIR="/opt/$APP_NAME"
SERVICE_NAME="exit-gate"
USER="pi"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

echo "=== Exit Gate Offline Installer ==="
echo "Installing from offline bundle..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_status "Script directory: $SCRIPT_DIR"

# Install system packages if available
install_system_packages() {
    print_status "Installing system packages..."
    
    # Check for .deb packages directory
    if [ -d "system-packages" ] && [ "$(ls -A system-packages/*.deb 2>/dev/null)" ]; then
        print_status "Found offline .deb packages, installing..."
        cd system-packages
        
        # Install all .deb packages
        if dpkg -i *.deb 2>/dev/null; then
            print_success "System packages installed from .deb files"
        else
            print_warning "Some .deb packages failed, trying to fix dependencies"
            # Try to fix broken dependencies without internet
            dpkg --configure -a || true
        fi
        cd ..
    elif [ -f "system-packages.txt" ]; then
        print_warning "Found system packages list but no .deb files"
        print_warning "System packages need to be pre-downloaded for offline installation"
        print_status "Skipping system package installation"
        print_status "You may need to install these packages manually:"
        cat system-packages.txt
    else
        print_warning "No system packages found"
        print_status "Skipping system package installation"
        print_status "Assuming required packages are already installed"
    fi
    
    # Verify essential tools are available
    print_status "Checking essential tools..."
    for tool in gcc make python3; do
        if command -v $tool &> /dev/null; then
            print_success "$tool is available"
        else
            print_warning "$tool not found - some npm packages may fail to compile"
        fi
    done
}

# Install Node.js from bundle
install_nodejs() {
    print_status "Installing Node.js from bundle..."
    
    # Look for Node.js archive
    NODE_ARCHIVE=$(find . -name "node-v*.tar.xz" | head -1)
    
    if [ -n "$NODE_ARCHIVE" ] && [ -f "$NODE_ARCHIVE" ]; then
        print_status "Found Node.js archive: $NODE_ARCHIVE"
        
        # Remove existing Node.js
        rm -rf /usr/local/bin/node /usr/local/bin/npm /usr/local/bin/npx /usr/local/lib/node_modules
        
        # Extract Node.js
        print_status "Extracting Node.js..."
        tar -xf "$NODE_ARCHIVE" -C /usr/local --strip-components=1
        
        # Verify installation
        if command -v node &> /dev/null; then
            print_success "Node.js installed: $(node --version)"
            print_success "NPM installed: $(npm --version)"
        else
            print_error "Node.js installation failed"
            exit 1
        fi
    else
        print_warning "Node.js bundle not found, checking if Node.js is already installed"
        if command -v node &> /dev/null; then
            print_status "Node.js already installed: $(node --version)"
        else
            print_error "Node.js not found and no bundle available"
            print_error "Please install Node.js manually or provide the bundle"
            exit 1
        fi
    fi
}

# Create application directory and copy files
install_application() {
    print_status "Installing application..."
    
    # Backup existing installation
    if [ -d "$INSTALL_DIR" ]; then
        print_status "Backing up existing installation"
        mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Create application directory
    print_status "Creating application directory: $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
    
    # Copy application files
    print_status "Copying application files..."
    
    # List of files to copy
    FILES_TO_COPY=(
        "package.json"
        "package-lock.json"
        "server.js"
        "services"
        "routes"
        "public"
    )
    
    for file in "${FILES_TO_COPY[@]}"; do
        if [ -e "$file" ]; then
            cp -r "$file" "$INSTALL_DIR/"
            print_status "Copied: $file"
        else
            print_warning "File not found: $file"
        fi
    done
    
    # Copy environment file
    if [ -f ".env.example" ]; then
        cp ".env.example" "$INSTALL_DIR/.env"
        print_status "Created .env from .env.example"
    elif [ -f ".env" ]; then
        cp ".env" "$INSTALL_DIR/"
        print_status "Copied existing .env"
    fi
    
    # Copy documentation
    for doc in "README.md" "SETUP.md" "IMPLEMENTATION.md"; do
        if [ -f "$doc" ]; then
            cp "$doc" "$INSTALL_DIR/"
        fi
    done
    
    print_success "Application files copied"
}

# Install npm dependencies from cache
install_dependencies() {
    print_status "Installing npm dependencies..."
    
    cd "$INSTALL_DIR"
    
    # Check for npm cache
    if [ -d "$SCRIPT_DIR/npm-cache" ]; then
        print_status "Using local npm cache"
        export NPM_CONFIG_CACHE="$SCRIPT_DIR/npm-cache"
        
        # Try offline installation first
        if npm ci --offline --no-audit 2>/dev/null; then
            print_success "Dependencies installed from cache"
        elif npm ci --prefer-offline --no-audit 2>/dev/null; then
            print_success "Dependencies installed (some from cache)"
        else
            print_warning "Cache installation failed, trying online"
            npm ci --no-audit || print_error "Dependency installation failed"
        fi
    else
        print_warning "No npm cache found, installing online"
        if npm ci --no-audit; then
            print_success "Dependencies installed online"
        else
            print_error "Failed to install dependencies"
            print_status "Trying alternative installation..."
            npm install --no-audit --production || print_error "Alternative installation also failed"
        fi
    fi
    
    # Try to install GPIO packages (optional with timeout)
    print_status "Installing optional GPIO packages..."
    
    # Function to run npm install with timeout
    install_with_timeout() {
        local packages="$1"
        local timeout=300  # 5 minutes timeout
        
        print_status "Attempting to install: $packages"
        if timeout $timeout npm install $packages --save-optional --no-audit --no-fund 2>/dev/null; then
            print_success "Successfully installed: $packages"
            return 0
        else
            print_warning "Failed or timed out installing: $packages"
            return 1
        fi
    }
    
    # Try each GPIO package with timeout
    install_with_timeout "raspi raspi-gpio" || true
    install_with_timeout "rpi-gpio" || true
    install_with_timeout "gpio" || true
    
    print_success "Dependencies installation completed"
}

# Set up GPIO permissions
setup_gpio() {
    print_status "Setting up GPIO permissions..."
    
    # Add pi user to gpio group
    if id "$USER" &>/dev/null; then
        usermod -a -G gpio "$USER"
        print_status "Added $USER to gpio group"
    fi
    
    # Set GPIO permissions
    if [ -e "/dev/gpiomem" ]; then
        chmod 666 /dev/gpiomem
        print_status "Set GPIO memory permissions"
    fi
    
    # Create udev rule for GPIO
    cat > /etc/udev/rules.d/99-gpio.rules << 'EOF'
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys/class/gpio/export /sys/class/gpio/unexport ; chmod 220 /sys/class/gpio/export /sys/class/gpio/unexport'"
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value ; chmod 660 /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value'"
EOF
    
    print_success "GPIO permissions configured"
}

# Create systemd service
setup_service() {
    print_status "Setting up systemd service..."
    
    # Create service file
    cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=Exit Gate Node.js Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/local/bin/node server.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production
StandardOutput=journal
StandardError=journal
SyslogIdentifier=exit-gate

[Install]
WantedBy=multi-user.target
EOF
    
    # Set ownership
    chown -R "$USER:$USER" "$INSTALL_DIR"
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    
    print_success "Service configured and enabled"
    
    # Fix GPIO permissions and setup
    print_status "Setting up GPIO permissions..."
    chmod +x "$INSTALL_DIR/gpio-fix.sh" "$INSTALL_DIR/gpio-troubleshoot.sh" "$INSTALL_DIR/gpio-test.js" 2>/dev/null || true
    
    # Add user to gpio group
    usermod -a -G gpio "$USER" 2>/dev/null || {
        print_warning "Could not add user to gpio group"
    }
    
    # Fix GPIO device permissions
    if [ -e "/dev/gpiomem" ]; then
        chmod 666 /dev/gpiomem
        print_success "GPIO permissions configured"
    else
        print_warning "GPIO device not found (may not be Raspberry Pi)"
    fi
}

# Main installation flow
main() {
    print_status "Starting offline installation..."
    
    install_system_packages
    install_nodejs
    install_application
    install_dependencies
    setup_gpio
    setup_service
    
    print_success "Installation completed successfully!"
    echo ""
    print_status "=== Next Steps ==="
    print_status "1. Configure the application:"
    print_status "   sudo nano $INSTALL_DIR/.env"
    print_status ""
    print_status "2. Start the service:"
    print_status "   sudo systemctl start $SERVICE_NAME"
    print_status ""
    print_status "3. Check service status:"
    print_status "   sudo systemctl status $SERVICE_NAME"
    print_status ""
    print_status "4. View logs:"
    print_status "   sudo journalctl -u $SERVICE_NAME -f"
    print_status ""
    print_status "5. Access web interface:"
    print_status "   http://$(hostname -I | awk '{print $1}'):3000"
    print_status ""
    print_status "=== GPIO Configuration ==="
    print_status "Gate control: Pin 24"
    print_status "LED indicator: Pin 25"
    print_status ""
    print_warning "You may need to reboot for GPIO permissions to take effect"
    print_status "Reboot command: sudo reboot"
}

# Run installation
main "$@"
