#!/bin/bash
# Separate GPIO package installer with better error handling

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

INSTALL_DIR="/opt/exit-gate-nodejs"

print_status "=== GPIO Package Installer ==="

# Check if we're in the right directory
if [ ! -d "$INSTALL_DIR" ]; then
    print_error "Application directory not found: $INSTALL_DIR"
    print_status "Run the main installer first"
    exit 1
fi

cd "$INSTALL_DIR"

# Function to install GPIO packages with timeout and retries
install_gpio_package() {
    local package_name="$1"
    local timeout=300  # 5 minutes
    local max_retries=3
    local retry=0
    
    print_status "Installing $package_name..."
    
    while [ $retry -lt $max_retries ]; do
        print_status "Attempt $((retry + 1)) of $max_retries for $package_name"
        
        if timeout $timeout npm install "$package_name" --save-optional --no-audit --no-fund --verbose; then
            print_success "Successfully installed $package_name"
            return 0
        else
            retry=$((retry + 1))
            if [ $retry -lt $max_retries ]; then
                print_warning "Retrying in 10 seconds..."
                sleep 10
            fi
        fi
    done
    
    print_error "Failed to install $package_name after $max_retries attempts"
    return 1
}

# List of GPIO packages to try
GPIO_PACKAGES=("raspi" "raspi-gpio" "rpi-gpio" "gpio")

print_status "Attempting to install GPIO packages..."

# Try each package individually
for package in "${GPIO_PACKAGES[@]}"; do
    install_gpio_package "$package" || print_warning "Skipping $package due to installation failure"
    echo ""
done

# Check what was actually installed
print_status "Checking installed GPIO packages..."
npm list --depth=0 | grep -E "(raspi|gpio)" || print_warning "No GPIO packages found in dependencies"

print_status "GPIO package installation completed"
print_status "Check the application logs to see which GPIO libraries are available"
