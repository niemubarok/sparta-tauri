#!/bin/bash

# =============================================================================
# Exit Gate Python System - Auto Deployment Script
# =============================================================================
# This script automatically deploys the exit gate system to Raspberry Pi
# Compatible with Python 2.7 and Raspberry Pi 3/4
#
# Usage: ./deploy-to-pi.sh <pi-ip-address>
# Example: ./deploy-to-pi.sh 192.168.10.51
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PI_USER="pi"
PI_IP="$1"
APP_DIR="/home/pi/exit-gate"
SERVICE_NAME="exit-gate-python"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if IP provided
if [ -z "$PI_IP" ]; then
    log_error "Usage: $0 <raspberry-pi-ip>"
    log_info "Example: $0 192.168.10.51"
    exit 1
fi

log_info "Starting deployment to Raspberry Pi at $PI_IP"

# Test SSH connection
log_info "Testing SSH connection..."
if ! ssh -o ConnectTimeout=5 ${PI_USER}@${PI_IP} "echo 'SSH connection successful'"; then
    log_error "Cannot connect to ${PI_USER}@${PI_IP}"
    log_info "Please ensure:"
    log_info "  1. Raspberry Pi is powered on and connected to network"
    log_info "  2. SSH is enabled on Raspberry Pi"
    log_info "  3. IP address is correct"
    log_info "  4. SSH key is configured or password is available"
    exit 1
fi
log_success "SSH connection established"

# Create directories on Pi
log_info "Creating application directories..."
ssh ${PI_USER}@${PI_IP} "mkdir -p ${APP_DIR}"
log_success "Directories created"

# Copy application files
log_info "Copying application files to Raspberry Pi..."
scp -r python-app/ ${PI_USER}@${PI_IP}:${APP_DIR}/
log_success "Application files copied"

# Make scripts executable
log_info "Setting up file permissions..."
ssh ${PI_USER}@${PI_IP} "chmod +x ${APP_DIR}/python-app/quick-setup.sh"
ssh ${PI_USER}@${PI_IP} "chmod +x ${APP_DIR}/python-app/*.py"
log_success "File permissions set"

# Run installation script
log_info "Running installation script on Raspberry Pi..."
ssh ${PI_USER}@${PI_IP} "cd ${APP_DIR}/python-app && ./quick-setup.sh"
log_success "Installation completed"

# Install dependencies manually if needed
log_info "Installing additional dependencies..."
ssh ${PI_USER}@${PI_IP} "python -m pip install --user couchdb==1.2" || log_warning "CouchDB install may have failed"
log_success "Dependencies installation completed"

# Create systemd service
log_info "Creating systemd service..."
ssh ${PI_USER}@${PI_IP} "sudo tee /etc/systemd/system/${SERVICE_NAME}.service << 'EOF'
[Unit]
Description=Exit Gate Python System
After=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=${APP_DIR}/python-app
ExecStart=/usr/bin/python main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

Environment=PYTHONPATH=${APP_DIR}/python-app
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF"
log_success "Systemd service created"

# Enable and start service
log_info "Enabling auto-start service..."
ssh ${PI_USER}@${PI_IP} "sudo systemctl daemon-reload"
ssh ${PI_USER}@${PI_IP} "sudo systemctl enable ${SERVICE_NAME}"
ssh ${PI_USER}@${PI_IP} "sudo systemctl start ${SERVICE_NAME}"
log_success "Service enabled and started"

# Wait for service to start
log_info "Waiting for service to start..."
sleep 10

# Check service status
log_info "Checking service status..."
if ssh ${PI_USER}@${PI_IP} "sudo systemctl is-active --quiet ${SERVICE_NAME}"; then
    log_success "Service is running successfully"
else
    log_warning "Service may not be running properly"
    log_info "Checking service logs..."
    ssh ${PI_USER}@${PI_IP} "sudo journalctl -u ${SERVICE_NAME} -n 10 --no-pager"
fi

# Test API endpoint
log_info "Testing API endpoint..."
sleep 5
if ssh ${PI_USER}@${PI_IP} "curl -s http://localhost:5001/api/status | grep -q success"; then
    log_success "API is responding correctly"
else
    log_warning "API may not be responding. Checking logs..."
    ssh ${PI_USER}@${PI_IP} "sudo journalctl -u ${SERVICE_NAME} -n 5 --no-pager"
fi

# Test GPIO (if available)
log_info "Testing GPIO functionality..."
if ssh ${PI_USER}@${PI_IP} "curl -s -X POST http://localhost:5001/api/gate/test | grep -q success"; then
    log_success "GPIO gate control is working"
else
    log_warning "GPIO test may have failed"
fi

# Create management aliases
log_info "Setting up management commands..."
ssh ${PI_USER}@${PI_IP} "cat >> ~/.bashrc << 'EOF'

# Exit Gate Management Commands
alias exit-gate-status='sudo systemctl status ${SERVICE_NAME}'
alias exit-gate-stop='sudo systemctl stop ${SERVICE_NAME}'
alias exit-gate-start='sudo systemctl start ${SERVICE_NAME}'
alias exit-gate-restart='sudo systemctl restart ${SERVICE_NAME}'
alias exit-gate-logs='sudo journalctl -u ${SERVICE_NAME} -f'
alias exit-gate-test='curl -X POST http://localhost:5001/api/gate/test'
EOF"
log_success "Management commands created"

# Final status check
log_info "Performing final system check..."
echo ""
echo "==================================="
echo "       DEPLOYMENT SUMMARY"
echo "==================================="

# Get system info
SYSTEM_INFO=$(ssh ${PI_USER}@${PI_IP} "curl -s http://localhost:5001/api/status 2>/dev/null" || echo "{}")

if echo "$SYSTEM_INFO" | grep -q "success"; then
    echo -e "${GREEN}✅ Application Status: RUNNING${NC}"
    echo -e "${GREEN}✅ Web Interface: http://${PI_IP}:5001${NC}"
    echo -e "${GREEN}✅ API Endpoint: http://${PI_IP}:5001/api/status${NC}"
    
    # Extract key info
    VERSION=$(echo "$SYSTEM_INFO" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('version', 'Unknown'))" 2>/dev/null || echo "Unknown")
    SCANNER_ENABLED=$(echo "$SYSTEM_INFO" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('scanner', {}).get('enabled', False))" 2>/dev/null || echo "Unknown")
    CONTROL_MODE=$(echo "$SYSTEM_INFO" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('system', {}).get('control_mode', 'Unknown'))" 2>/dev/null || echo "Unknown")
    
    echo -e "${BLUE}📋 System Info:${NC}"
    echo "   • Version: $VERSION"
    echo "   • Scanner: $SCANNER_ENABLED"
    echo "   • Control Mode: $CONTROL_MODE"
    echo "   • Service: $SERVICE_NAME"
else
    echo -e "${RED}❌ Application Status: NOT RESPONDING${NC}"
    log_warning "Application may not be running properly"
fi

echo ""
echo -e "${BLUE}🎛 Management Commands:${NC}"
echo "   • ssh ${PI_USER}@${PI_IP}"
echo "   • exit-gate-status    # Check service status"
echo "   • exit-gate-restart   # Restart service"
echo "   • exit-gate-logs      # View logs"
echo "   • exit-gate-test      # Test gate"

echo ""
echo -e "${BLUE}🌐 Access Points:${NC}"
echo "   • Main UI: http://${PI_IP}:5001"
echo "   • Settings: http://${PI_IP}:5001/settings"
echo "   • API Status: http://${PI_IP}:5001/api/status"

echo ""
echo -e "${BLUE}🔧 Next Steps:${NC}"
echo "   1. Configure GPIO pin in settings if needed"
echo "   2. Test with real barcode scanner"
echo "   3. Configure camera endpoints if using CCTV"
echo "   4. Set up database sync if needed"

echo ""
if echo "$SYSTEM_INFO" | grep -q "success"; then
    echo -e "${GREEN}🎉 DEPLOYMENT SUCCESSFUL!${NC}"
    echo -e "${GREEN}Exit Gate Python System is ready for use.${NC}"
else
    echo -e "${YELLOW}⚠️  DEPLOYMENT COMPLETED WITH WARNINGS${NC}"
    echo -e "${YELLOW}Please check the logs and troubleshoot any issues.${NC}"
fi

echo ""
echo "==================================="

# Exit with appropriate code
if echo "$SYSTEM_INFO" | grep -q "success"; then
    exit 0
else
    exit 1
fi
