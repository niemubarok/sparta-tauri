#!/bin/bash

# Exit Gate Compatibility Fix Script
# Fixes common compatibility issues on Raspberry Pi

set -e

echo "=== Exit Gate Compatibility Fix ==="
echo

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

# Check current Node.js version and compatibility
check_nodejs_compatibility() {
    print_status "Checking Node.js compatibility..."
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_status "Current Node.js version: $NODE_VERSION"
        
        # Try to run a simple Node.js command to test compatibility
        if node -e "console.log('Node.js working')" &> /dev/null; then
            print_success "Node.js is working correctly"
            return 0
        else
            print_error "Node.js compatibility issue detected"
            return 1
        fi
    else
        print_error "Node.js not found"
        return 1
    fi
}

# Check system libraries
check_system_libraries() {
    print_status "Checking system libraries..."
    
    # Check GLIBC version
    GLIBC_VERSION=$(ldd --version | head -1 | awk '{print $NF}')
    print_status "GLIBC version: $GLIBC_VERSION"
    
    # Check libstdc++ version
    if [ -f "/usr/lib/arm-linux-gnueabihf/libstdc++.so.6" ]; then
        LIBSTDCXX_VERSIONS=$(strings /usr/lib/arm-linux-gnueabihf/libstdc++.so.6 | grep GLIBCXX | tail -5)
        print_status "Available GLIBCXX versions:"
        echo "$LIBSTDCXX_VERSIONS"
    fi
}

# Fix Node.js compatibility by installing older version
fix_nodejs_compatibility() {
    print_status "Attempting to fix Node.js compatibility..."
    
    # Stop the service if running
    if systemctl is-active --quiet exit-gate; then
        print_status "Stopping exit-gate service..."
        systemctl stop exit-gate
    fi
    
    # Remove current Node.js installation
    print_status "Removing current Node.js installation..."
    rm -rf /usr/local/bin/node /usr/local/bin/npm /usr/local/bin/npx /usr/local/lib/node_modules
    
    # Install Node.js v18.19.1 (compatible with older systems)
    print_status "Installing Node.js v18.19.1 for better compatibility..."
    
    cd /tmp
    wget -q https://nodejs.org/dist/v18.19.1/node-v18.19.1-linux-armv7l.tar.xz
    
    if [ -f "node-v18.19.1-linux-armv7l.tar.xz" ]; then
        tar -xf node-v18.19.1-linux-armv7l.tar.xz -C /usr/local --strip-components=1
        rm node-v18.19.1-linux-armv7l.tar.xz
        
        # Verify installation
        if node -e "console.log('Node.js v18.19.1 installed successfully')" &> /dev/null; then
            print_success "Node.js v18.19.1 installed successfully"
            print_success "Node.js version: $(node --version)"
            print_success "NPM version: $(npm --version)"
            return 0
        else
            print_error "Node.js installation failed"
            return 1
        fi
    else
        print_error "Failed to download Node.js v18.19.1"
        return 1
    fi
}

# Update system packages for better compatibility
update_system_packages() {
    print_status "Updating system packages for better compatibility..."
    
    apt update
    
    # Install/update essential packages
    apt install -y \
        build-essential \
        python3-dev \
        libasound2-dev \
        libstdc++6 \
        libc6 \
        curl \
        wget
    
    print_success "System packages updated"
}

# Main execution
main() {
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        print_error "Please run as root (use sudo)"
        exit 1
    fi
    
    print_status "Starting compatibility check and fix..."
    echo
    
    # Check current compatibility
    if check_nodejs_compatibility; then
        print_success "No compatibility issues found!"
        exit 0
    fi
    
    echo
    print_warning "Compatibility issues detected. Attempting fixes..."
    echo
    
    # Show system info
    check_system_libraries
    echo
    
    # Update system packages
    update_system_packages
    echo
    
    # Fix Node.js compatibility
    if fix_nodejs_compatibility; then
        echo
        print_success "Compatibility fix completed successfully!"
        
        # Restart the service
        if systemctl is-enabled --quiet exit-gate; then
            print_status "Starting exit-gate service..."
            systemctl start exit-gate
            
            # Check service status
            sleep 2
            if systemctl is-active --quiet exit-gate; then
                print_success "Exit-gate service is running"
            else
                print_warning "Service may need manual restart"
                print_status "Check logs with: sudo journalctl -u exit-gate -f"
            fi
        fi
    else
        print_error "Compatibility fix failed"
        echo
        print_status "Manual steps to try:"
        print_status "1. Update Raspberry Pi OS: sudo apt update && sudo apt upgrade"
        print_status "2. Use Node.js v16 or v18 instead of v20"
        print_status "3. Check Raspberry Pi model compatibility"
        exit 1
    fi
}

# Run main function
main "$@"
