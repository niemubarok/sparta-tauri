#!/bin/bash
set -e

echo "=== Building Exit Gate for Raspberry Pi 3 ==="

# Check if we're on the correct platform
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "This script should be run on a Linux system for cross-compilation"
    echo "For Windows, use WSL2 or a Linux VM"
    exit 1
fi

# Install dependencies for cross-compilation to ARMv7 (Raspberry Pi 3)
echo "Installing cross-compilation dependencies..."
sudo apt-get update
sudo apt-get install -y \
    gcc-arm-linux-gnueabihf \
    g++-arm-linux-gnueabihf \
    libc6-dev-armhf-cross \
    pkg-config \
    curl \
    build-essential

# Install Node.js if not present
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Install pnpm if not present
if ! command -v pnpm &> /dev/null; then
    echo "Installing pnpm..."
    npm install -g pnpm
fi

# Install Rust if not present
if ! command -v rustc &> /dev/null; then
    echo "Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
fi

# Ensure Rust is in PATH
export PATH="$HOME/.cargo/bin:$PATH"
source ~/.cargo/env 2>/dev/null || true

# Add Rust target for ARMv7 (Raspberry Pi 3)
echo "Adding Rust target for ARMv7..."
rustup target add armv7-unknown-linux-gnueabihf

# Set environment variables for cross-compilation
export CC_armv7_unknown_linux_gnueabihf=arm-linux-gnueabihf-gcc
export CXX_armv7_unknown_linux_gnueabihf=arm-linux-gnueabihf-g++
export AR_armv7_unknown_linux_gnueabihf=arm-linux-gnueabihf-ar
export CARGO_TARGET_ARMV7_UNKNOWN_LINUX_GNUEABIHF_LINKER=arm-linux-gnueabihf-gcc
export PKG_CONFIG_ALLOW_CROSS=1

echo "Building frontend..."
pnpm install
pnpm build

echo "Building Tauri application for Raspberry Pi 3..."
cd src-tauri

# Create .cargo/config.toml for cross-compilation
mkdir -p .cargo
cat > .cargo/config.toml << EOF
[target.armv7-unknown-linux-gnueabihf]
linker = "arm-linux-gnueabihf-gcc"

[env]
CC_armv7_unknown_linux_gnueabihf = "arm-linux-gnueabihf-gcc"
CXX_armv7_unknown_linux_gnueabihf = "arm-linux-gnueabihf-g++"
AR_armv7_unknown_linux_gnueabihf = "arm-linux-gnueabihf-ar"
EOF

# Build for ARMv7 (Raspberry Pi 3)
cargo build --target armv7-unknown-linux-gnueabihf --release

echo "=== Build completed ==="
echo "Binary location: src-tauri/target/armv7-unknown-linux-gnueabihf/release/exit-gate"
echo ""
echo "To deploy to Raspberry Pi:"
echo "1. Copy the binary to your Pi: scp target/armv7-unknown-linux-gnueabihf/release/exit-gate pi@your-pi-ip:~/"
echo "2. Make it executable: chmod +x ~/exit-gate"
echo "3. Install dependencies on Pi: sudo apt-get install -y libc6 libgcc1 libstdc++6"
echo "4. Run: ./exit-gate"
