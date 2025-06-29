#!/bin/bash

# Deploy script for Raspberry Pi
# Usage: ./deploy-to-pi.sh [pi-ip-address] [username]

PI_IP=${1:-raspberrypi.local}
PI_USER=${2:-pi}
BINARY_PATH="src-tauri/target/armv7-unknown-linux-gnueabihf/release/exit-gate"

echo "=== Deploying Exit Gate to Raspberry Pi ==="
echo "Target: $PI_USER@$PI_IP"

# Check if binary exists
if [ ! -f "$BINARY_PATH" ]; then
    echo "Error: Binary not found at $BINARY_PATH"
    echo "Please run build-rpi.sh first"
    exit 1
fi

echo "Copying binary and GPIO scripts to Pi..."
scp "$BINARY_PATH" "$PI_USER@$PI_IP:~/exit-gate"
scp "setup-gpio.sh" "$PI_USER@$PI_IP:~/setup-gpio.sh"
scp "test-gpio.sh" "$PI_USER@$PI_IP:~/test-gpio.sh"

echo "Setting up permissions and dependencies on Pi..."
ssh "$PI_USER@$PI_IP" << 'EOF'
    # Make binary executable
    chmod +x ~/exit-gate
    
    # Make GPIO scripts executable
    chmod +x ~/setup-gpio.sh
    chmod +x ~/test-gpio.sh
    
    # Install required dependencies
    sudo apt-get update
    sudo apt-get install -y libc6 libgcc1 libstdc++6
    
    echo "=== GPIO Setup ==="
    echo "Run GPIO setup: sudo ~/setup-gpio.sh"
    echo "Test GPIO: ~/test-gpio.sh"
    echo ""
    
    # Create systemd service (optional)
    sudo tee /etc/systemd/system/exit-gate.service > /dev/null << 'SERVICE'
[Unit]
Description=Exit Gate System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/home/pi/exit-gate
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE
    
    echo "Setup completed!"
    echo "To start the service: sudo systemctl start exit-gate"
    echo "To enable auto-start: sudo systemctl enable exit-gate"
    echo "To run manually: ./exit-gate"
EOF

echo "=== Deployment completed ==="
