#!/bin/bash
# Exit Gate System - Quick Start Script for Raspberry Pi

set -e  # Exit on error

echo "=========================================="
echo "Exit Gate System - Quick Start"
echo "=========================================="

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

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

# Check if on Raspberry Pi
check_raspberry_pi() {
    if grep -q "Raspberry\|BCM" /proc/cpuinfo 2>/dev/null; then
        print_success "Raspberry Pi detected"
        return 0
    else
        print_warning "Not running on Raspberry Pi - some features may be limited"
        return 1
    fi
}

# Check Python version
check_python() {
    if command -v python >/dev/null 2>&1; then
        PYTHON_VERSION=$(python -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))")
        print_status "Python version: $PYTHON_VERSION"
        
        if python -c "import sys; sys.exit(0 if sys.version_info >= (2, 7) else 1)" 2>/dev/null; then
            print_success "Python version compatible"
            return 0
        else
            print_error "Python 2.7 or higher required"
            return 1
        fi
    else
        print_error "Python not found"
        return 1
    fi
}

# Install system dependencies
install_dependencies() {
    print_status "Installing system dependencies..."
    
    # Update package list
    sudo apt-get update -y
    
    # Install required packages
    sudo apt-get install -y \
        python-pip \
        python-dev \
        build-essential \
        git \
        curl \
        wget \
        ffmpeg \
        portaudio19-dev \
        alsa-utils \
        pulseaudio \
        libjpeg-dev \
        libpng-dev \
        libfreetype6-dev \
        libffi-dev \
        libssl-dev \
        python-setuptools
    
    # Install GPIO support for Raspberry Pi
    if check_raspberry_pi; then
        sudo pip install RPi.GPIO==0.7.0
        sudo usermod -a -G gpio,audio $USER
    fi
    
    print_success "System dependencies installed"
}

# Setup Python environment
setup_python() {
    print_status "Setting up Python environment..."
    
    # Upgrade pip
    python -m pip install --user --upgrade "pip<21.0"
    
    # Install Python dependencies
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python packages from requirements.txt..."
        pip install --user -r requirements.txt
        print_success "Python packages installed"
    else
        print_error "requirements.txt not found"
        return 1
    fi
}

# Create directories
setup_directories() {
    print_status "Setting up directories..."
    
    mkdir -p sounds
    mkdir -p database
    mkdir -p logs
    
    print_success "Directories created"
}

# Create configuration
setup_config() {
    print_status "Setting up configuration..."
    
    if [ ! -f "config.ini" ]; then
        python -c "from config import Config; Config().save()" 2>/dev/null || {
            print_error "Failed to create configuration"
            return 1
        }
        print_success "Default configuration created"
    else
        print_status "Configuration file already exists"
    fi
}

# Create systemd service
setup_service() {
    if ! check_raspberry_pi; then
        print_warning "Skipping service setup (not on Raspberry Pi)"
        return 0
    fi
    
    print_status "Setting up systemd service..."
    
    SERVICE_FILE="/etc/systemd/system/exit-gate.service"
    WORK_DIR=$(pwd)
    
    cat > /tmp/exit-gate.service << EOF
[Unit]
Description=Exit Gate System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORK_DIR
ExecStart=/usr/bin/python $WORK_DIR/main.py
Restart=always
RestartSec=10
Environment=PATH=/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=$WORK_DIR

[Install]
WantedBy=multi-user.target
EOF
    
    sudo mv /tmp/exit-gate.service $SERVICE_FILE
    sudo systemctl daemon-reload
    
    print_success "Systemd service created"
    print_status "To enable auto-start: sudo systemctl enable exit-gate"
    print_status "To start service: sudo systemctl start exit-gate"
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    # Test Python imports
    python -c "
import sys
modules = ['flask', 'couchdb', 'pygame', 'PIL', 'requests']
if sys.version_info.major == 2:
    modules.append('ConfigParser')
else:
    modules.append('configparser')

failed = []
for module in modules:
    try:
        __import__(module)
        print('✓ ' + module)
    except ImportError:
        print('✗ ' + module)
        failed.append(module)

if failed:
    print('Failed imports: ' + ', '.join(failed))
    sys.exit(1)
else:
    print('All modules imported successfully')
" || {
        print_error "Module import test failed"
        return 1
    }
    
    # Test configuration
    python -c "from config import Config; print('✓ Configuration test passed')" || {
        print_error "Configuration test failed"
        return 1
    }
    
    print_success "Installation test passed"
}

# Create start script
create_start_script() {
    print_status "Creating start script..."
    
    cat > start.sh << 'EOF'
#!/bin/bash
# Exit Gate System Launcher

cd "$(dirname "$0")"

echo "Starting Exit Gate System..."
echo "Python version: $(python --version 2>&1)"
echo "Working directory: $(pwd)"

# Check if config exists
if [ ! -f "config.ini" ]; then
    echo "Creating default configuration..."
    python -c "from config import Config; Config().save()"
fi

# Start the application
echo "Starting web server on http://localhost:5000"
python main.py
EOF
    
    chmod +x start.sh
    print_success "Start script created"
}

# Main installation function
main() {
    # Change to script directory
    cd "$(dirname "$0")"
    WORK_DIR=$(pwd)
    
    print_status "Working directory: $WORK_DIR"
    
    # Check prerequisites
    check_python || exit 1
    
    # Run installation steps
    print_status "Starting installation process..."
    
    install_dependencies || exit 1
    setup_python || exit 1
    setup_directories || exit 1
    setup_config || exit 1
    create_start_script || exit 1
    setup_service
    test_installation || exit 1
    
    print_success "Installation completed successfully!"
    
    echo ""
    echo "=========================================="
    echo "Next Steps:"
    echo "=========================================="
    echo "1. Configure the system:"
    echo "   nano config.ini"
    echo ""
    echo "2. Start the application:"
    echo "   ./start.sh"
    echo "   OR"
    echo "   python main.py"
    echo ""
    echo "3. Access web interface:"
    echo "   http://localhost:5000"
    echo "   http://$(hostname -I | awk '{print $1}'):5000"
    echo ""
    
    if check_raspberry_pi; then
        echo "4. Enable auto-start (optional):"
        echo "   sudo systemctl enable exit-gate"
        echo "   sudo systemctl start exit-gate"
        echo ""
        echo "5. Check service status:"
        echo "   sudo systemctl status exit-gate"
        echo ""
    fi
    
    echo "For support and documentation, check README.md"
    echo "=========================================="
}

# Run main function
main "$@"
