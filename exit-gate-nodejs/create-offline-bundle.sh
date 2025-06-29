#!/bin/bash

# Exit Gate System - Offline Bundle Creator
# This script creates a complete offline installation package

set -e

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

# Configuration
BUNDLE_DIR="exit-gate-offline-bundle"
APP_DIR="exit-gate-nodejs"
NODE_VERSION="18.17.1"
ARCH="armv7l"  # Raspberry Pi 3/4

# Create bundle directory
create_bundle_structure() {
    print_status "Creating bundle structure..."
    
    rm -rf "$BUNDLE_DIR"
    mkdir -p "$BUNDLE_DIR"
    mkdir -p "$BUNDLE_DIR/app"
    mkdir -p "$BUNDLE_DIR/node"
    mkdir -p "$BUNDLE_DIR/packages"
    mkdir -p "$BUNDLE_DIR/system-packages"
    mkdir -p "$BUNDLE_DIR/scripts"
    
    print_success "Bundle structure created"
}

# Download Node.js for Raspberry Pi
download_nodejs() {
    print_status "Downloading Node.js v${NODE_VERSION} for ARM..."
    
    NODE_FILENAME="node-v${NODE_VERSION}-linux-${ARCH}.tar.xz"
    NODE_URL="https://nodejs.org/dist/v${NODE_VERSION}/${NODE_FILENAME}"
    
    if [ ! -f "$BUNDLE_DIR/node/$NODE_FILENAME" ]; then
        wget -O "$BUNDLE_DIR/node/$NODE_FILENAME" "$NODE_URL"
        print_success "Node.js downloaded"
    else
        print_status "Node.js already downloaded"
    fi
}

# Bundle application files
bundle_application() {
    print_status "Bundling application files..."
    
    # Copy all application files except node_modules
    rsync -av \
        --exclude='node_modules' \
        --exclude='.git' \
        --exclude='*.log' \
        --exclude='tmp' \
        --exclude='*.backup.*' \
        ./ "$BUNDLE_DIR/app/"
    
    print_success "Application files bundled"
}

# Create offline npm cache
create_npm_cache() {
    print_status "Creating offline npm cache..."
    
    # Install dependencies and create cache
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    
    # Create npm cache directory
    NPM_CACHE_DIR="$BUNDLE_DIR/packages/npm-cache"
    mkdir -p "$NPM_CACHE_DIR"
    
    # Pack all dependencies
    print_status "Packing npm dependencies..."
    npm pack --pack-destination="$BUNDLE_DIR/packages" $(npm list --production --parseable --depth=0 | sed '1d' | awk '{gsub(/.*\/node_modules\//, ""); print}') 2>/dev/null || true
    
    # Create package-lock for offline use
    cp package-lock.json "$BUNDLE_DIR/app/" 2>/dev/null || true
    
    # Alternative: use npm-bundle for complete offline cache
    if command -v npm-bundle &> /dev/null; then
        print_status "Creating complete npm bundle..."
        npm-bundle
        mv npm-bundle.tgz "$BUNDLE_DIR/packages/"
    fi
    
    print_success "NPM cache created"
}

# Download system packages
download_system_packages() {
    print_status "Downloading system packages..."
    
    # Create a temporary directory for package downloads
    TEMP_PKG_DIR=$(mktemp -d)
    
    # List of required packages
    PACKAGES=(
        "alsa-utils"
        "git"
        "curl"
        "wget"
        "build-essential"
        "python3-gpiozero"
        "python3-rpi.gpio"
    )
    
    # Download packages using apt-get download
    cd "$TEMP_PKG_DIR"
    
    for package in "${PACKAGES[@]}"; do
        print_status "Downloading $package..."
        apt-get download "$package" 2>/dev/null || print_warning "Could not download $package"
        
        # Download dependencies
        apt-cache depends "$package" | grep "Depends:" | sed 's/.*Depends: //' | xargs apt-get download 2>/dev/null || true
    done
    
    # Move downloaded packages to bundle
    mv *.deb "$BUNDLE_DIR/system-packages/" 2>/dev/null || print_warning "No .deb packages found"
    
    # Cleanup
    rm -rf "$TEMP_PKG_DIR"
    
    print_success "System packages downloaded"
}

# Create offline installer script
create_offline_installer() {
    print_status "Creating offline installer..."
    
    cat > "$BUNDLE_DIR/install-offline.sh" << 'EOF'
#!/bin/bash

# Exit Gate System - Offline Installer
set -e

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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="/home/pi/exit-gate-nodejs"
NODE_DIR="/opt/nodejs"

print_status "Starting offline installation..."

# Install system packages
install_system_packages() {
    print_status "Installing system packages..."
    
    if [ -d "$SCRIPT_DIR/system-packages" ] && [ "$(ls -A $SCRIPT_DIR/system-packages)" ]; then
        cd "$SCRIPT_DIR/system-packages"
        dpkg -i *.deb || apt-get install -f -y
        print_success "System packages installed"
    else
        print_warning "No system packages found, skipping..."
    fi
}

# Install Node.js
install_nodejs() {
    print_status "Installing Node.js..."
    
    # Remove existing Node.js
    rm -rf "$NODE_DIR"
    mkdir -p "$NODE_DIR"
    
    # Extract Node.js
    NODE_ARCHIVE=$(ls "$SCRIPT_DIR/node/"*.tar.xz 2>/dev/null | head -1)
    if [ -n "$NODE_ARCHIVE" ]; then
        tar -xf "$NODE_ARCHIVE" -C "$NODE_DIR" --strip-components=1
        
        # Create symlinks
        ln -sf "$NODE_DIR/bin/node" /usr/local/bin/node
        ln -sf "$NODE_DIR/bin/npm" /usr/local/bin/npm
        ln -sf "$NODE_DIR/bin/npx" /usr/local/bin/npx
        
        print_success "Node.js installed: $(node --version)"
    else
        print_error "Node.js archive not found"
        exit 1
    fi
}

# Install application
install_application() {
    print_status "Installing application..."
    
    # Backup existing installation
    if [ -d "$APP_DIR" ]; then
        mv "$APP_DIR" "${APP_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Copy application files
    cp -r "$SCRIPT_DIR/app" "$APP_DIR"
    chown -R pi:pi "$APP_DIR"
    
    print_success "Application files copied"
}

# Install dependencies offline
install_dependencies() {
    print_status "Installing dependencies offline..."
    
    cd "$APP_DIR"
    
    # Method 1: Use local packages
    if [ -d "$SCRIPT_DIR/packages" ] && [ "$(ls -A $SCRIPT_DIR/packages)" ]; then
        print_status "Installing from local packages..."
        
        # Create local npm registry
        mkdir -p npm-cache
        cp "$SCRIPT_DIR/packages"/*.tgz npm-cache/ 2>/dev/null || true
        
        # Install from cache
        npm install --cache ./npm-cache --offline --no-audit 2>/dev/null || \
        npm install --prefer-offline --no-audit
    fi
    
    # Method 2: Install specific packages manually if needed
    print_status "Installing optional GPIO packages..."
    
    # Try to install GPIO packages (these might fail, that's ok)
    npm install raspi raspi-gpio --save-optional --no-audit 2>/dev/null || print_warning "Some GPIO packages not available"
    npm install rpi-gpio gpio --save-optional --no-audit 2>/dev/null || print_warning "Some GPIO packages not available"
    
    print_success "Dependencies installed"
}

# Setup GPIO permissions
setup_gpio() {
    print_status "Setting up GPIO permissions..."
    
    # Add pi user to gpio group
    usermod -a -G gpio pi
    
    # Set GPIO permissions
    chmod 666 /dev/gpiomem 2>/dev/null || true
    
    # Create udev rule
    cat > /etc/udev/rules.d/99-gpio.rules << 'UDEV_RULE'
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys/class/gpio/export /sys/class/gpio/unexport ; chmod 220 /sys/class/gpio/export /sys/class/gpio/unexport'"
UDEV_RULE
    
    print_success "GPIO permissions configured"
}

# Setup systemd service
setup_service() {
    print_status "Setting up systemd service..."
    
    # Copy service file
    cp "$APP_DIR/exit-gate.service" /etc/systemd/system/
    
    # Update service file paths
    sed -i "s|WorkingDirectory=.*|WorkingDirectory=$APP_DIR|" /etc/systemd/system/exit-gate.service
    sed -i "s|ExecStart=.*|ExecStart=/usr/local/bin/node $APP_DIR/server.js|" /etc/systemd/system/exit-gate.service
    
    # Enable and start service
    systemctl daemon-reload
    systemctl enable exit-gate.service
    
    print_success "Service configured"
}

# Main installation flow
main() {
    print_status "Exit Gate System - Offline Installation"
    print_status "======================================"
    
    install_system_packages
    install_nodejs
    install_application
    install_dependencies
    setup_gpio
    setup_service
    
    print_success "Installation completed!"
    print_status ""
    print_status "Next steps:"
    print_status "1. Reboot the system: reboot"
    print_status "2. Start the service: systemctl start exit-gate"
    print_status "3. Check status: systemctl status exit-gate"
    print_status "4. Access web interface: http://$(hostname -I | awk '{print $1}'):3000"
    print_status ""
    print_status "GPIO Configuration:"
    print_status "- Gate control: Pin 24"
    print_status "- LED indicator: Pin 25"
}

# Run installation
main "$@"
EOF

    chmod +x "$BUNDLE_DIR/install-offline.sh"
    print_success "Offline installer created"
}

# Create README for offline bundle
create_bundle_readme() {
    print_status "Creating bundle documentation..."
    
    cat > "$BUNDLE_DIR/README.md" << 'EOF'
# Exit Gate System - Offline Installation Bundle

This package contains everything needed to install the Exit Gate System on Raspberry Pi without internet connection.

## Contents

- `app/` - Complete application source code
- `node/` - Node.js runtime for ARM/Raspberry Pi
- `packages/` - NPM packages and dependencies
- `system-packages/` - System .deb packages
- `install-offline.sh` - Offline installation script

## Installation

1. Copy this entire folder to Raspberry Pi (via USB, SD card, or local network)

2. Run the offline installer:
   ```bash
   sudo ./install-offline.sh
   ```

3. Reboot the system:
   ```bash
   sudo reboot
   ```

4. Check service status:
   ```bash
   sudo systemctl status exit-gate
   ```

5. Access web interface:
   ```
   http://raspberry-pi-ip:3000
   ```

## System Requirements

- Raspberry Pi 3B+ or newer
- Raspberry Pi OS (Debian-based)
- At least 1GB free space
- GPIO pins 24 and 25 available

## Hardware Connections

- **Pin 24**: Gate control output
- **Pin 25**: LED live indicator

## Troubleshooting

### Check logs:
```bash
sudo journalctl -u exit-gate -f
```

### Test GPIO:
```bash
cd /home/pi/exit-gate-nodejs
npm run test-gpio
```

### Manual service control:
```bash
sudo systemctl start exit-gate    # Start
sudo systemctl stop exit-gate     # Stop
sudo systemctl restart exit-gate  # Restart
```

## Features

- Web-based interface (accessible via browser)
- Real-time WebSocket communication
- GPIO control for gate and LED
- Barcode scanner support
- Audio feedback system
- Transaction processing
- Database sync capability (when internet available)

## Support

Check the main README.md in the app directory for detailed documentation.
EOF

    print_success "Bundle documentation created"
}

# Create bundle info file
create_bundle_info() {
    print_status "Creating bundle info..."
    
    cat > "$BUNDLE_DIR/bundle-info.txt" << EOF
Exit Gate System - Offline Bundle
Created: $(date)
Node.js Version: ${NODE_VERSION}
Architecture: ${ARCH}
Platform: Raspberry Pi

Bundle Contents:
- Application: $(du -sh app/ | cut -f1)
- Node.js: $(du -sh node/ | cut -f1) 
- Packages: $(du -sh packages/ | cut -f1)
- System Packages: $(du -sh system-packages/ | cut -f1)

Total Size: $(du -sh . | cut -f1)

Installation: sudo ./install-offline.sh
EOF

    print_success "Bundle info created"
}

# Create compressed archive
create_archive() {
    print_status "Creating compressed archive..."
    
    ARCHIVE_NAME="exit-gate-offline-$(date +%Y%m%d).tar.gz"
    
    tar -czf "$ARCHIVE_NAME" "$BUNDLE_DIR"
    
    ARCHIVE_SIZE=$(du -sh "$ARCHIVE_NAME" | cut -f1)
    print_success "Archive created: $ARCHIVE_NAME ($ARCHIVE_SIZE)"
    
    # Create checksum
    sha256sum "$ARCHIVE_NAME" > "${ARCHIVE_NAME}.sha256"
    print_success "Checksum created: ${ARCHIVE_NAME}.sha256"
}

# Main function
main() {
    print_status "Exit Gate System - Offline Bundle Creator"
    print_status "========================================"
    
    # Check requirements
    if ! command -v npm &> /dev/null; then
        print_error "npm is required to create bundle"
        exit 1
    fi
    
    if ! command -v wget &> /dev/null; then
        print_error "wget is required to download Node.js"
        exit 1
    fi
    
    # Create bundle
    create_bundle_structure
    download_nodejs
    bundle_application
    create_npm_cache
    download_system_packages
    create_offline_installer
    create_bundle_readme
    create_bundle_info
    create_archive
    
    print_success "Offline bundle creation completed!"
    print_status ""
    print_status "Bundle created: $ARCHIVE_NAME"
    print_status "Transfer this file to Raspberry Pi and extract:"
    print_status "  tar -xzf $ARCHIVE_NAME"
    print_status "  cd $BUNDLE_DIR"
    print_status "  sudo ./install-offline.sh"
    print_status ""
    print_warning "Note: Transfer bundle via USB drive, SD card, or local network"
}

# Run main function
main "$@"
EOF
