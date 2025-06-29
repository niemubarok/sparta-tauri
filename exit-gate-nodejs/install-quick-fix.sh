#!/bin/bash
# Quick fix for stuck GPIO installation

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

print_status "=== Exit Gate Quick Fix ==="

# Kill any hanging npm processes
print_status "Killing any hanging npm processes..."
killall npm 2>/dev/null || true
killall node 2>/dev/null || true

# Navigate to application directory
INSTALL_DIR="/opt/exit-gate-nodejs"
if [ -d "$INSTALL_DIR" ]; then
    cd "$INSTALL_DIR"
    print_status "Working in: $INSTALL_DIR"
else
    print_error "Application directory not found: $INSTALL_DIR"
    exit 1
fi

# Skip GPIO packages and complete installation
print_status "Completing installation without problematic GPIO packages..."

# Set up basic GPIO permissions
print_status "Setting up basic GPIO permissions..."
usermod -a -G gpio pi 2>/dev/null || print_warning "Could not add pi user to gpio group"

if [ -e "/dev/gpiomem" ]; then
    chmod 666 /dev/gpiomem
    print_success "GPIO memory permissions set"
fi

# Create udev rule for GPIO
cat > /etc/udev/rules.d/99-gpio.rules << 'EOF'
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys/class/gpio/export /sys/class/gpio/unexport ; chmod 220 /sys/class/gpio/export /sys/class/gpio/unexport'"
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value ; chmod 660 /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value'"
EOF

# Create minimal service
cat > "/etc/systemd/system/exit-gate.service" << 'EOF'
[Unit]
Description=Exit Gate Node.js Application
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/exit-gate-nodejs
ExecStart=/usr/local/bin/node server.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production
StandardOutput=journal
StandardError=journal
SyslogIdentifier=exit-gate

[Install]
WantedBy=multi-user.target
EOF

# Set ownership
chown -R pi:pi "$INSTALL_DIR"

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable exit-gate

print_success "Quick fix completed!"
print_status ""
print_status "=== Service Management ==="
print_status "Start service: sudo systemctl start exit-gate"
print_status "Check status: sudo systemctl status exit-gate"
print_status "View logs: sudo journalctl -u exit-gate -f"
print_status ""
print_status "=== Web Interface ==="
print_status "Access at: http://$(hostname -I | awk '{print $1}'):3000"
print_status ""
print_warning "GPIO packages were skipped - GPIO functionality may be limited"
print_status "You can try installing GPIO packages manually later if needed"
