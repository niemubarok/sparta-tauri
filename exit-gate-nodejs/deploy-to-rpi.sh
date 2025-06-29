#!/bin/bash

# Exit Gate System - Deployment Script
# This script deploys the application to Raspberry Pi via SSH

set -e

# Configuration
RPI_HOST=${1:-"192.168.1.100"}
RPI_USER=${2:-"pi"}
RPI_PASSWORD=${3:-"raspberry"}
LOCAL_DIR=$(pwd)
REMOTE_DIR="/home/pi/exit-gate-nodejs"

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

# Check if sshpass is available for password authentication
check_sshpass() {
    if ! command -v sshpass &> /dev/null; then
        print_warning "sshpass not found. Please install it or use SSH key authentication."
        print_status "On Ubuntu/Debian: sudo apt install sshpass"
        print_status "On macOS: brew install sshpass"
        return 1
    fi
    return 0
}

# Test SSH connection
test_connection() {
    print_status "Testing SSH connection to $RPI_USER@$RPI_HOST..."
    
    if check_sshpass; then
        if sshpass -p "$RPI_PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$RPI_USER@$RPI_HOST" "echo 'Connection successful'"; then
            print_success "SSH connection successful"
            return 0
        fi
    else
        if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$RPI_USER@$RPI_HOST" "echo 'Connection successful'"; then
            print_success "SSH connection successful"
            return 0
        fi
    fi
    
    print_error "SSH connection failed"
    return 1
}

# Create deployment package
create_package() {
    print_status "Creating deployment package..."
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    PACKAGE_DIR="$TEMP_DIR/exit-gate-nodejs"
    
    # Copy files
    mkdir -p "$PACKAGE_DIR"
    
    # Copy application files
    cp -r \
        server.js \
        package.json \
        .env.example \
        README.md \
        SETUP.md \
        exit-gate.service \
        install-rpi.sh \
        services/ \
        routes/ \
        public/ \
        "$PACKAGE_DIR/" 2>/dev/null || true
    
    # Copy .env if it exists
    if [ -f ".env" ]; then
        cp .env "$PACKAGE_DIR/"
    fi
    
    # Create archive
    PACKAGE_FILE="$TEMP_DIR/exit-gate-deployment.tar.gz"
    cd "$TEMP_DIR"
    tar -czf "$PACKAGE_FILE" exit-gate-nodejs/
    
    echo "$PACKAGE_FILE"
}

# Deploy to Raspberry Pi
deploy() {
    print_status "Deploying to Raspberry Pi..."
    
    # Create package
    PACKAGE_FILE=$(create_package)
    
    # Copy package to Raspberry Pi
    print_status "Uploading package..."
    if check_sshpass; then
        sshpass -p "$RPI_PASSWORD" scp "$PACKAGE_FILE" "$RPI_USER@$RPI_HOST:/tmp/"
    else
        scp "$PACKAGE_FILE" "$RPI_USER@$RPI_HOST:/tmp/"
    fi
    
    # Extract and install on Raspberry Pi
    print_status "Installing on Raspberry Pi..."
    
    REMOTE_COMMANDS="
        # Stop service if running
        sudo systemctl stop exit-gate || true
        
        # Backup existing installation
        if [ -d '$REMOTE_DIR' ]; then
            sudo mv '$REMOTE_DIR' '${REMOTE_DIR}.backup.\$(date +%Y%m%d_%H%M%S)' || true
        fi
        
        # Extract new version
        cd /tmp
        tar -xzf exit-gate-deployment.tar.gz
        sudo mv exit-gate-nodejs '$REMOTE_DIR'
        sudo chown -R pi:pi '$REMOTE_DIR'
        
        # Install dependencies
        cd '$REMOTE_DIR'
        npm install
        npm install raspi raspi-gpio rpi-gpio gpio --save-optional || true
        
        # Update systemd service
        sudo cp exit-gate.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable exit-gate
        
        # Start service
        sudo systemctl start exit-gate
        
        # Cleanup
        rm -f /tmp/exit-gate-deployment.tar.gz
        
        echo 'Deployment completed successfully!'
    "
    
    if check_sshpass; then
        sshpass -p "$RPI_PASSWORD" ssh "$RPI_USER@$RPI_HOST" "$REMOTE_COMMANDS"
    else
        ssh "$RPI_USER@$RPI_HOST" "$REMOTE_COMMANDS"
    fi
    
    # Cleanup local temp files
    rm -rf "$(dirname "$PACKAGE_FILE")"
    
    print_success "Deployment completed!"
}

# Check service status
check_status() {
    print_status "Checking service status..."
    
    STATUS_COMMANDS="
        echo '=== Service Status ==='
        sudo systemctl status exit-gate --no-pager
        
        echo ''
        echo '=== Service Logs (last 20 lines) ==='
        sudo journalctl -u exit-gate -n 20 --no-pager
        
        echo ''
        echo '=== Application URL ==='
        IP=\$(hostname -I | awk '{print \$1}')
        echo \"http://\$IP:3000\"
    "
    
    if check_sshpass; then
        sshpass -p "$RPI_PASSWORD" ssh "$RPI_USER@$RPI_HOST" "$STATUS_COMMANDS"
    else
        ssh "$RPI_USER@$RPI_HOST" "$STATUS_COMMANDS"
    fi
}

# Show usage
usage() {
    echo "Usage: $0 [RPI_HOST] [RPI_USER] [RPI_PASSWORD]"
    echo ""
    echo "Examples:"
    echo "  $0                                          # Use defaults (192.168.1.100, pi, raspberry)"
    echo "  $0 192.168.1.150                          # Custom IP"
    echo "  $0 192.168.1.150 pi mypassword            # Custom IP and password"
    echo ""
    echo "Environment variables:"
    echo "  RPI_HOST     - Raspberry Pi IP address (default: 192.168.1.100)"
    echo "  RPI_USER     - SSH username (default: pi)"
    echo "  RPI_PASSWORD - SSH password (default: raspberry)"
    echo ""
    echo "Note: For security, consider using SSH key authentication instead of passwords"
}

# Main function
main() {
    print_status "Exit Gate System - Deployment Script"
    print_status "====================================="
    
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        usage
        exit 0
    fi
    
    print_status "Target: $RPI_USER@$RPI_HOST"
    print_status "Remote directory: $REMOTE_DIR"
    print_status ""
    
    # Test connection
    if ! test_connection; then
        print_error "Cannot connect to Raspberry Pi"
        print_status "Please check:"
        print_status "1. Raspberry Pi is powered on and connected to network"
        print_status "2. SSH is enabled on Raspberry Pi"
        print_status "3. IP address, username, and password are correct"
        print_status "4. Network connectivity"
        exit 1
    fi
    
    # Deploy
    deploy
    
    # Check status
    sleep 3
    check_status
    
    print_success "Deployment completed successfully!"
    print_status ""
    print_status "Access the application at: http://$RPI_HOST:3000"
    print_status ""
    print_status "Useful commands:"
    print_status "  Check status: ssh $RPI_USER@$RPI_HOST 'sudo systemctl status exit-gate'"
    print_status "  View logs:    ssh $RPI_USER@$RPI_HOST 'sudo journalctl -u exit-gate -f'"
    print_status "  Restart:      ssh $RPI_USER@$RPI_HOST 'sudo systemctl restart exit-gate'"
}

# Run main function
main "$@"
