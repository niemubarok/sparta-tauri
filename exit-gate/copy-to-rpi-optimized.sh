#!/bin/bash
# Optimized copy script from Windows/Linux to Raspberry Pi
# Only copies essential files needed for building

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

echo "🚀 Copying Exit Gate Project (Optimized) to Raspberry Pi"
echo "========================================================"
echo "Source: $(pwd)"
echo "Target: $PI_USER@$PI_IP:$REMOTE_DIR"
echo

# Check if we're in the correct directory
if [[ ! -f "package.json" ]] || [[ ! -d "src-tauri" ]]; then
    print_error "This script must be run from the exit-gate directory!"
    print_status "Current directory: $(pwd)"
    exit 1
fi

# Test SSH connection with fallback
print_status "Testing SSH connection to $PI_USER@$PI_IP..."

if ssh -o ConnectTimeout=10 -o BatchMode=yes "$PI_USER@$PI_IP" exit 2>/dev/null; then
    print_success "SSH connection successful (key-based)"
elif ssh -o ConnectTimeout=10 "$PI_USER@$PI_IP" exit; then
    print_success "SSH connection successful (password)"
else
    print_error "SSH connection failed!"
    print_status "Please ensure SSH is working: ssh $PI_USER@$PI_IP"
    exit 1
fi

# Create remote directory
print_status "Creating remote directory structure..."
ssh "$PI_USER@$PI_IP" "mkdir -p $REMOTE_DIR"

# Use rsync with optimized exclusions
print_status "Copying essential files using rsync..."

# Comprehensive exclude patterns
EXCLUDE_PATTERNS=(
    "node_modules/"
    ".quasar/"
    "dist/"
    "target/"
    ".git/"
    ".vscode/"
    ".github/"
    "*.log"
    "*.tmp"
    "*.swp"
    "*.swo"
    ".DS_Store"
    "Thumbs.db"
    "deploy-*/"
    "scripts/"
    "../parkir_awal.sql"
    "../*.xlsx"
    "*.xlsx"
    ".env"
    ".env.local"
    "coverage/"
    ".nyc_output/"
    ".cache/"
)

# Build exclude arguments
EXCLUDE_ARGS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude=$pattern"
done

# Execute rsync with progress
if rsync -avz --progress $EXCLUDE_ARGS ./ "$PI_USER@$PI_IP:$REMOTE_DIR/"; then
    print_success "Essential files copied successfully!"
else
    print_error "Failed to copy files!"
    exit 1
fi

# Make scripts executable
print_status "Setting up permissions on Pi..."
ssh "$PI_USER@$PI_IP" "
    cd $REMOTE_DIR
    chmod +x *.sh 2>/dev/null || true
    echo 'Scripts made executable'
"

# Create optimized setup script
print_status "Creating optimized setup script on Pi..."
ssh "$PI_USER@$PI_IP" "cat > $REMOTE_DIR/setup-environment.sh << 'EOF'
#!/bin/bash

set -e

echo '🔧 Setting up Exit Gate build environment (Optimized)'
echo '=================================================='

# Install only essential packages for building
echo '📦 Installing essential build dependencies...'
sudo apt-get update

# Core development tools
sudo apt-get install -y \\
    curl wget git \\
    build-essential pkg-config \\
    libssl-dev

# Tauri runtime dependencies (minimal set)
sudo apt-get install -y \\
    libgtk-3-dev \\
    libwebkit2gtk-4.0-dev \\
    libappindicator3-dev \\
    librsvg2-dev \\
    libdbus-1-dev \\
    libudev-dev

# GPIO and serial communication
sudo apt-get install -y \\
    libv4l-dev \\
    v4l-utils

# Node.js (if not present)
if ! command -v node &> /dev/null; then
    echo '📦 Installing Node.js LTS...'
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# pnpm (faster than npm)
if ! command -v pnpm &> /dev/null; then
    echo '📦 Installing pnpm...'
    npm install -g pnpm
fi

# Rust (latest stable)
if ! command -v rustc &> /dev/null; then
    echo '🦀 Installing Rust...'
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
    source ~/.cargo/env
    echo 'export PATH=\"\$HOME/.cargo/bin:\$PATH\"' >> ~/.bashrc
fi

# Source Rust environment
source ~/.cargo/env 2>/dev/null || true

# Tauri CLI (latest)
echo '🔧 Installing Tauri CLI...'
cargo install tauri-cli --locked

# Setup permissions for GPIO/Serial
echo '⚡ Setting up hardware permissions...'
sudo usermod -a -G gpio,dialout \$USER

echo '✅ Environment setup completed!'
echo '🏗️ Ready to build! Run: ./quick-build.sh'
EOF"

# Create optimized build script
ssh "$PI_USER@$PI_IP" "cat > $REMOTE_DIR/quick-build.sh << 'EOF'
#!/bin/bash

set -e

echo '🚀 Quick Build for Exit Gate System (Optimized)'
echo '=============================================='

cd \$(dirname \"\$0\")

# Environment check
if ! command -v pnpm &> /dev/null; then
    echo '❌ pnpm not found! Run: ./setup-environment.sh'
    exit 1
fi

if ! command -v cargo &> /dev/null; then
    echo '❌ Rust not found! Run: ./setup-environment.sh'
    exit 1
fi

# Source Rust environment
source ~/.cargo/env 2>/dev/null || true

# Memory optimization for Pi
export NODE_OPTIONS=\"--max-old-space-size=2048\"

# CPU optimization based on Pi model
ARCH=\$(uname -m)
case \"\$ARCH\" in
    \"aarch64\"|\"arm64\")
        export RUSTFLAGS=\"-C target-cpu=cortex-a72\"
        echo '🔧 Optimizing for Raspberry Pi 4 (Cortex-A72)'
        ;;
    \"armv7l\")
        export RUSTFLAGS=\"-C target-cpu=cortex-a53\"
        echo '🔧 Optimizing for Raspberry Pi 3 (Cortex-A53)'
        ;;
    *)
        echo '🔧 Using default optimization for \$ARCH'
        ;;
esac

# Show system info
echo \"📊 System: \$(uname -a)\"
echo \"💾 Memory: \$(free -h | grep Mem)\"
echo \"🔧 Node: \$(node --version)\"
echo \"🦀 Rust: \$(rustc --version)\"
echo

# Install dependencies (with cache optimization)
echo '📦 Installing Node.js dependencies...'
pnpm install --frozen-lockfile

# Build with progress indication
echo '🏗️ Building Exit Gate System...'
echo 'This typically takes 10-30 minutes on Raspberry Pi...'

start_time=\$(date +%s)

# Build with detailed output
if pnpm tauri build --verbose; then
    end_time=\$(date +%s)
    build_time=\$((end_time - start_time))
    
    echo
    echo '✅ Build completed successfully!'
    echo \"⏱️ Build time: \${build_time} seconds\"
    echo
    
    # Show binary info
    if [[ -f \"src-tauri/target/release/tauri-quasar\" ]]; then
        binary_path=\"src-tauri/target/release/tauri-quasar\"
        binary_size=\$(ls -lh \"\$binary_path\" | awk '{print \$5}')
        echo \"📁 Binary: \$binary_path\"
        echo \"📊 Size: \$binary_size\"
        echo
        echo '🚀 To install system-wide:'
        echo \"  sudo cp '\$binary_path' /usr/local/bin/exit-gate\"
        echo \"  sudo chmod +x /usr/local/bin/exit-gate\"
        echo
        echo '▶️ To run directly:'
        echo \"  ./\$binary_path\"
    else
        echo '⚠️ Binary not found at expected location'
        find src-tauri/target -name \"*tauri*\" -type f 2>/dev/null | head -5
    fi
else
    echo '❌ Build failed!'
    echo '💾 Memory status:'
    free -h
    exit 1
fi
EOF"

# Make scripts executable
ssh "$PI_USER@$PI_IP" "cd $REMOTE_DIR && chmod +x setup-environment.sh quick-build.sh"

# Show transfer summary
print_status "Verifying copied files on Pi..."
ssh "$PI_USER@$PI_IP" "
    cd $REMOTE_DIR
    echo 'Project structure:'
    ls -la | head -20
    echo
    echo 'Total size:'
    du -sh .
"

# Show completion summary
echo
print_success "Optimized Exit Gate project copied successfully!"
echo "=============================================="
print_status "Project location: $REMOTE_DIR"
print_status "Transfer optimized: Skipped unnecessary files"
echo
print_status "What was copied:"
echo "✅ Source code (src/, src-tauri/)"
echo "✅ Build configs (package.json, quasar.config.ts, etc.)"
echo "✅ Static assets (public/)"
echo "✅ Essential scripts"
echo
print_status "What was skipped:"
echo "⏭️ node_modules/ (will install fresh)"
echo "⏭️ target/ (Rust build artifacts)"
echo "⏭️ dist/ (Quasar output)"
echo "⏭️ Git history and IDE settings"
echo "⏭️ Database files (not needed for build)"
echo
print_status "Next steps:"
echo "1. ssh $PI_USER@$PI_IP"
echo "2. cd $REMOTE_DIR"
echo "3. ./setup-environment.sh  # One-time setup"
echo "4. ./quick-build.sh        # Build the app"
echo
print_success "🎉 Ready for building on Raspberry Pi!"
