#!/bin/bash
# filepath: e:\DEVS\spartakuler\exit-gate\copy-to-rpi.sh

set -e

# Configuration
PI_IP="192.168.10.51"
PI_USER="pi"
PROJECT_NAME="exit-gate"
REMOTE_DIR="/home/pi/sparta-exit-gate"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo "🚀 Copying Exit Gate Project to Raspberry Pi"
echo "============================================="
echo "Target: $PI_USER@$PI_IP:$REMOTE_DIR"
echo

# Check if we're in the correct directory
if [[ ! -f "package.json" ]] || [[ ! -d "src-tauri" ]]; then
    print_error "This script must be run from the exit-gate directory!"
    print_status "Current directory: $(pwd)"
    exit 1
fi

# Function to test SSH connection
test_ssh_connection() {
    print_status "Testing SSH connection to $PI_USER@$PI_IP..."
    if ssh -o ConnectTimeout=10 -o BatchMode=yes "$PI_USER@$PI_IP" exit 2>/dev/null; then
        print_success "SSH connection successful"
        return 0
    else
        print_error "SSH connection failed!"
        print_status "Please ensure:"
        print_status "1. Raspberry Pi is powered on and connected to network"
        print_status "2. SSH is enabled on the Pi"
        print_status "3. SSH key is configured or you can enter password"
        print_status "4. IP address $PI_IP is correct"
        return 1
    fi
}

# Test SSH connection first
if ! test_ssh_connection; then
    exit 1
fi

# Create remote directory
print_status "Creating remote directory structure..."
ssh "$PI_USER@$PI_IP" "mkdir -p $REMOTE_DIR"

# Exclude patterns for rsync
EXCLUDE_PATTERNS=(
    "node_modules/"
    ".quasar/"
    "dist/"
    "target/"
    ".git/"
    ".vscode/"
    "*.log"
    "*.tmp"
    "*.swp"
    "*.swo"
    ".DS_Store"
    "Thumbs.db"
    ".github/"
)

# Build exclude arguments for rsync
EXCLUDE_ARGS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude=$pattern"
done

# Copy project files using rsync
print_status "Copying project files (excluding build artifacts)..."
rsync -avz --progress \
    $EXCLUDE_ARGS \
    ./ "$PI_USER@$PI_IP:$REMOTE_DIR/"

if [[ $? -eq 0 ]]; then
    print_success "Project files copied successfully!"
else
    print_error "Failed to copy project files!"
    exit 1
fi

# Copy additional required files that might be in parent directory
print_status "Checking for additional required files..."

# Check if database schema exists in parent directory
if [[ -f "../parkir_awal.sql" ]]; then
    print_status "Copying database schema..."
    scp "../parkir_awal.sql" "$PI_USER@$PI_IP:$REMOTE_DIR/"
fi

# Check if master data exists
if [[ -f "../master parkir.xlsx" ]]; then
    print_status "Copying master data..."
    scp "../master parkir.xlsx" "$PI_USER@$PI_IP:$REMOTE_DIR/"
fi

# Make scripts executable on remote
print_status "Making scripts executable on remote Pi..."
ssh "$PI_USER@$PI_IP" "
    cd $REMOTE_DIR
    chmod +x *.sh 2>/dev/null || true
    chmod +x build-rpi-direct.sh 2>/dev/null || true
    chmod +x setup-gpio.sh 2>/dev/null || true
    chmod +x test-gpio.sh 2>/dev/null || true
"

# Create setup script on Pi
print_status "Creating setup script on Pi..."
ssh "$PI_USER@$PI_IP" "cat > $REMOTE_DIR/setup-environment.sh << 'EOF'
#!/bin/bash

set -e

echo '🔧 Setting up Exit Gate development environment on Raspberry Pi'
echo '============================================================='

# Update system
echo '📦 Updating system packages...'
sudo apt-get update

# Install basic development tools
echo '🛠️ Installing development tools...'
sudo apt-get install -y \\
    curl \\
    wget \\
    git \\
    build-essential \\
    pkg-config \\
    libssl-dev

# Install Tauri dependencies
echo '📱 Installing Tauri dependencies...'
sudo apt-get install -y \\
    libgtk-3-dev \\
    libwebkit2gtk-4.0-dev \\
    libappindicator3-dev \\
    librsvg2-dev \\
    libdbus-1-dev \\
    libudev-dev

# Install multimedia dependencies
echo '🎬 Installing multimedia dependencies...'
sudo apt-get install -y \\
    libv4l-dev \\
    v4l-utils \\
    ffmpeg

# Install Node.js if not present
if ! command -v node &> /dev/null; then
    echo '📦 Installing Node.js...'
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo '✅ Node.js already installed: \$(node --version)'
fi

# Install pnpm if not present
if ! command -v pnpm &> /dev/null; then
    echo '📦 Installing pnpm...'
    npm install -g pnpm
else
    echo '✅ pnpm already installed: \$(pnpm --version)'
fi

# Install Rust if not present
if ! command -v rustc &> /dev/null; then
    echo '🦀 Installing Rust...'
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
    echo 'export PATH=\"\$HOME/.cargo/bin:\$PATH\"' >> ~/.bashrc
else
    echo '✅ Rust already installed: \$(rustc --version)'
fi

# Install Tauri CLI
echo '🔧 Installing Tauri CLI...'
source ~/.cargo/env 2>/dev/null || true
cargo install tauri-cli --locked

echo '✅ Environment setup completed!'
echo '🚀 You can now run: ./build-rpi-direct.sh'
EOF"

# Make setup script executable
ssh "$PI_USER@$PI_IP" "chmod +x $REMOTE_DIR/setup-environment.sh"

# Create quick build script
print_status "Creating quick build script on Pi..."
ssh "$PI_USER@$PI_IP" "cat > $REMOTE_DIR/quick-build.sh << 'EOF'
#!/bin/bash

set -e

echo '🚀 Quick build for Exit Gate System'
echo '=================================='

# Ensure we're in the right directory
cd \$(dirname \"\$0\")

# Check if environment is set up
if ! command -v pnpm &> /dev/null || ! command -v cargo &> /dev/null; then
    echo '⚠️ Development environment not set up!'
    echo 'Run: ./setup-environment.sh'
    exit 1
fi

# Source cargo environment
source ~/.cargo/env 2>/dev/null || true

# Set memory limit for Node.js
export NODE_OPTIONS=\"--max-old-space-size=2048\"

# Set optimization flags for Raspberry Pi
ARCH=\$(uname -m)
if [[ \"\$ARCH\" == \"aarch64\" || \"\$ARCH\" == \"arm64\" ]]; then
    export RUSTFLAGS=\"-C target-cpu=cortex-a72\"
elif [[ \"\$ARCH\" == \"armv7l\" ]]; then
    export RUSTFLAGS=\"-C target-cpu=cortex-a53\"
fi

echo '📦 Installing Node.js dependencies...'
pnpm install

echo '🏗️ Building Exit Gate System...'
pnpm tauri build --verbose

if [[ \$? -eq 0 ]]; then
    echo '✅ Build completed successfully!'
    echo ''
    echo '📁 Binary location:'
    ls -la src-tauri/target/release/tauri-quasar 2>/dev/null || echo 'Binary not found'
    echo ''
    echo '🚀 To install system-wide, run:'
    echo '  sudo cp src-tauri/target/release/tauri-quasar /usr/local/bin/exit-gate'
else
    echo '❌ Build failed!'
    exit 1
fi
EOF"

ssh "$PI_USER@$PI_IP" "chmod +x $REMOTE_DIR/quick-build.sh"

# Show project structure on remote
print_status "Verifying copied files on Pi..."
ssh "$PI_USER@$PI_IP" "
    cd $REMOTE_DIR
    echo 'Project structure:'
    ls -la
    echo ''
    echo 'src-tauri structure:'
    ls -la src-tauri/ 2>/dev/null || echo 'src-tauri directory not found'
"

# Show next steps
echo
print_success "Exit Gate project copied successfully to Raspberry Pi!"
echo "======================================================"
print_status "Project location on Pi: $REMOTE_DIR"
print_status "SSH to Pi: ssh $PI_USER@$PI_IP"
echo
print_status "Next steps on Raspberry Pi:"
echo "1. ssh $PI_USER@$PI_IP"
echo "2. cd $REMOTE_DIR"
echo "3. ./setup-environment.sh  # First time only"
echo "4. ./quick-build.sh        # Quick build"
echo "   OR"
echo "4. ./build-rpi-direct.sh   # Full build with deployment package"
echo
print_status "Available scripts on Pi:"
echo "• setup-environment.sh  - Install all dependencies"
echo "• quick-build.sh        - Fast build without packaging"
echo "• build-rpi-direct.sh   - Full build with deployment package"
echo "• setup-gpio.sh         - Setup GPIO permissions"
echo "• test-gpio.sh          - Test GPIO functionality"
echo
print_status "Files copied:"
echo "• Source code (src/, src-tauri/)"
echo "• Configuration files (package.json, Cargo.toml, etc.)"
echo "• Build scripts"
echo "• Documentation"
echo "• GPIO setup scripts"

# Optional: Automatically run setup if requested
echo
read -p "Do you want to automatically run environment setup on Pi? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Running environment setup on Pi..."
    ssh "$PI_USER@$PI_IP" "cd $REMOTE_DIR && ./setup-environment.sh"
    
    if [[ $? -eq 0 ]]; then
        print_success "Environment setup completed!"
        echo
        read -p "Do you want to start the build process now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Starting build process on Pi..."
            ssh "$PI_USER@$PI_IP" "cd $REMOTE_DIR && ./quick-build.sh"
        fi
    fi
fi

echo
print_success "🎉 Copy process completed successfully!"
print_status "The Exit Gate project is now ready for building on Raspberry Pi."