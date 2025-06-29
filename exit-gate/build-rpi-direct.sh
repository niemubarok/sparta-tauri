#!/bin/bash
# filepath: e:\DEVS\spartakuler\exit-gate\build-rpi-direct.sh

set -e  # Exit on any error

echo "🚪 Building Exit Gate System directly on Raspberry Pi"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if we're in the correct directory
if [[ ! -f "package.json" ]] || [[ ! -d "src-tauri" ]]; then
    print_error "This script must be run from the exit-gate directory!"
    print_status "Current directory: $(pwd)"
    print_status "Expected files: package.json, src-tauri/"
    exit 1
fi

# Check if running on ARM architecture
ARCH=$(uname -m)
print_status "Detected architecture: $ARCH"

if [[ "$ARCH" != "aarch64" && "$ARCH" != "armv7l" && "$ARCH" != "arm64" ]]; then
    print_warning "Not running on ARM architecture ($ARCH). This script is optimized for Raspberry Pi."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system dependencies
print_status "Checking system dependencies..."

# Update system packages
print_status "Updating system packages..."
sudo apt-get update

# Install build dependencies specific for Exit Gate System
print_status "Installing build dependencies for Exit Gate System..."
sudo apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    pkg-config \
    libssl-dev \
    libgtk-3-dev \
    libwebkit2gtk-4.0-dev \
    libappindicator3-dev \
    librsvg2-dev \
    libdbus-1-dev \
    libudev-dev \
    libv4l-dev \
    v4l-utils \
    ffmpeg

# Check and install Node.js
if ! command_exists node; then
    print_status "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    NODE_VERSION=$(node --version)
    print_success "Node.js already installed: $NODE_VERSION"
fi

# Check and install pnpm
if ! command_exists pnpm; then
    print_status "Installing pnpm..."
    npm install -g pnpm
else
    PNPM_VERSION=$(pnpm --version)
    print_success "pnpm already installed: $PNPM_VERSION"
fi

# Check and install Rust
if ! command_exists rustc; then
    print_status "Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
else
    RUST_VERSION=$(rustc --version)
    print_success "Rust already installed: $RUST_VERSION"
fi

# Update Rust to latest stable
print_status "Updating Rust to latest stable..."
rustup update stable
rustup default stable

# Install Tauri CLI
print_status "Installing/Updating Tauri CLI..."
cargo install tauri-cli --locked

# Add cargo bin to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.cargo/bin:"* ]]; then
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Set Rust flags for Raspberry Pi optimization
if [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
    export RUSTFLAGS="-C target-cpu=cortex-a72"  # For RPi 4
    print_status "Using Cortex-A72 optimization for Raspberry Pi 4"
elif [[ "$ARCH" == "armv7l" ]]; then
    export RUSTFLAGS="-C target-cpu=cortex-a53"  # For RPi 3
    print_status "Using Cortex-A53 optimization for Raspberry Pi 3"
fi

# Set memory limit for Node.js to prevent OOM on Pi
export NODE_OPTIONS="--max-old-space-size=2048"

# Check package.json for project info
if [[ -f "package.json" ]]; then
    PROJECT_NAME=$(node -p "require('./package.json').name" 2>/dev/null || echo "exit-gate-system")
    PROJECT_VERSION=$(node -p "require('./package.json').version" 2>/dev/null || echo "1.0.0")
    print_status "Building $PROJECT_NAME v$PROJECT_VERSION"
fi

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
pnpm install

# Build the Exit Gate System
print_status "Building Exit Gate System with Tauri..."
print_status "This may take several minutes on Raspberry Pi..."

# Show memory usage before build
print_status "Memory status before build:"
free -h

# Run the build with verbose output
if command_exists pnpm; then
    pnpm tauri build --verbose
else
    npm run tauri:build -- --verbose
fi

if [[ $? -eq 0 ]]; then
    print_success "Exit Gate System build completed successfully!"
    
    # Show build artifacts
    if [[ -d "src-tauri/target/release" ]]; then
        print_status "Generated executable:"
        ls -la src-tauri/target/release/tauri-quasar 2>/dev/null || ls -la src-tauri/target/release/
        
        # Show file size
        if [[ -f "src-tauri/target/release/tauri-quasar" ]]; then
            BINARY_SIZE=$(ls -lh src-tauri/target/release/tauri-quasar | awk '{print $5}')
            print_status "Binary size: $BINARY_SIZE"
        fi
    fi
    
    # Show bundle files if exist
    if [[ -d "src-tauri/target/release/bundle" ]]; then
        print_status "Bundle files:"
        find src-tauri/target/release/bundle -type f -name "*.deb" -o -name "*.AppImage" 2>/dev/null | head -5
    fi
    
else
    print_error "Exit Gate System build failed!"
    print_status "Check the error messages above for details"
    exit 1
fi

# Create deployment package
DEPLOY_DIR="exit-gate-deploy-$(date +%Y%m%d-%H%M%S)"
print_status "Creating deployment package: $DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"/{bin,scripts,config,services}

# Copy binary
if [[ -f "src-tauri/target/release/tauri-quasar" ]]; then
    cp "src-tauri/target/release/tauri-quasar" "$DEPLOY_DIR/bin/exit-gate"
    print_success "Binary copied to deployment package"
fi

# Copy scripts
for script in setup-gpio.sh test-gpio.sh; do
    if [[ -f "$script" ]]; then
        cp "$script" "$DEPLOY_DIR/scripts/"
        chmod +x "$DEPLOY_DIR/scripts/$script"
    fi
done

# Create systemd service
cat > "$DEPLOY_DIR/services/exit-gate.service" << 'EOF'
[Unit]
Description=Sparta Exit Gate System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/exit-gate
ExecStart=/opt/exit-gate/bin/exit-gate
Restart=always
RestartSec=5
Environment=DISPLAY=:0
Environment=RUST_LOG=info

[Install]
WantedBy=multi-user.target
EOF

# Create installation script
cat > "$DEPLOY_DIR/install.sh" << 'EOF'
#!/bin/bash

set -e

echo "🔧 Installing Exit Gate System on Raspberry Pi"
echo "=============================================="

# Create installation directory
sudo mkdir -p /opt/exit-gate/{bin,logs,config}
sudo mkdir -p /var/log/exit-gate

# Copy files
echo "📋 Installing application files..."
sudo cp bin/exit-gate /opt/exit-gate/bin/
sudo cp -r scripts/* /opt/exit-gate/ 2>/dev/null || true

# Set permissions
echo "🔐 Setting permissions..."
sudo chown -R pi:pi /opt/exit-gate
sudo chown -R pi:pi /var/log/exit-gate
sudo chmod +x /opt/exit-gate/bin/exit-gate
sudo chmod +x /opt/exit-gate/*.sh 2>/dev/null || true

# Setup GPIO permissions
echo "⚡ Setting up GPIO permissions..."
sudo usermod -a -G gpio pi
sudo usermod -a -G dialout pi

# Create udev rules for serial ports
sudo tee /etc/udev/rules.d/99-exit-gate-serial.rules > /dev/null << 'EOFUDEV'
SUBSYSTEM=="tty", ATTRS{idVendor}=="*", MODE="0666", GROUP="dialout"
KERNEL=="ttyUSB*", MODE="0666", GROUP="dialout"
KERNEL=="ttyACM*", MODE="0666", GROUP="dialout"
EOFUDEV

# Install systemd service
echo "🔧 Installing systemd service..."
sudo cp services/exit-gate.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable exit-gate.service

# Setup GPIO if script exists
if [[ -f "/opt/exit-gate/setup-gpio.sh" ]]; then
    echo "⚙️ Running GPIO setup..."
    sudo /opt/exit-gate/setup-gpio.sh
fi

echo "✅ Exit Gate System installation completed!"
echo ""
echo "🚀 To start the service:"
echo "  sudo systemctl start exit-gate"
echo ""
echo "📊 To check status:"
echo "  sudo systemctl status exit-gate"
echo "  sudo journalctl -u exit-gate -f"
echo ""
echo "🔧 GPIO test (if available):"
echo "  /opt/exit-gate/test-gpio.sh"
echo ""
echo "🔄 Please reboot for GPIO permissions to take effect"
EOF

chmod +x "$DEPLOY_DIR/install.sh"

# Create README for deployment
cat > "$DEPLOY_DIR/README.md" << 'EOF'
# Exit Gate System Deployment Package

This package contains the compiled Exit Gate System for Raspberry Pi.

## Installation

1. Run the installation script:
   ```bash
   ./install.sh
   ```

2. Reboot the system:
   ```bash
   sudo reboot
   ```

3. Start the service:
   ```bash
   sudo systemctl start exit-gate
   ```

## Configuration

- Application files: `/opt/exit-gate/`
- Logs: `/var/log/exit-gate/`
- Service logs: `sudo journalctl -u exit-gate -f`

## GPIO Configuration

The Exit Gate System supports both Serial and GPIO control modes:

- **Serial Mode**: Traditional relay control via serial commands
- **GPIO Mode**: Direct GPIO pin control (Raspberry Pi only)

Configure the mode in the application settings UI.

## Testing

Test GPIO functionality (if configured):
```bash
/opt/exit-gate/test-gpio.sh
```

## Troubleshooting

1. Check service status:
   ```bash
   sudo systemctl status exit-gate
   ```

2. View logs:
   ```bash
   sudo journalctl -u exit-gate -f
   ```

3. Check GPIO permissions:
   ```bash
   groups pi | grep gpio
   ```

4. Test serial ports:
   ```bash
   ls -la /dev/ttyUSB* /dev/ttyACM*
   ```
EOF

# Show deployment summary
echo
print_success "Exit Gate System build and packaging completed!"
echo "======================================================="
print_status "Deployment package created: $DEPLOY_DIR"
print_status "Binary location: $DEPLOY_DIR/bin/exit-gate"
print_status "Installation script: $DEPLOY_DIR/install.sh"
echo
print_status "To install on this Raspberry Pi:"
echo "  cd $DEPLOY_DIR"
echo "  ./install.sh"
echo
print_status "To copy to another Raspberry Pi:"
echo "  scp -r $DEPLOY_DIR pi@target-pi-ip:~/"
echo "  ssh pi@target-pi-ip"
echo "  cd $DEPLOY_DIR && ./install.sh"
echo
print_status "System information:"
echo "  Architecture: $ARCH"
echo "  Rust version: $(rustc --version 2>/dev/null || echo 'Not detected')"
echo "  Node.js version: $(node --version 2>/dev/null || echo 'Not detected')"
echo "  Build completed: $(date)"

# Show memory usage after build
print_status "Memory status after build:"
free -h

echo
print_success "🎉 Exit Gate System ready for deployment!"