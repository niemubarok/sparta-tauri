#!/bin/bash

# Setup script for Parking System on Raspberry Pi

echo "=== Parking System Setup for Raspberry Pi ==="

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and pip
echo "Installing Python and pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libv4l-dev

# Install CouchDB
echo "Installing CouchDB..."
curl -fsSL https://couchdb.apache.org/repo/bintray-pubkey.asc | sudo apt-key add -
echo "deb https://apache.bintray.com/couchdb-deb/ $(lsb_release -c -s) main" | sudo tee -a /etc/apt/sources.list.d/couchdb.list
sudo apt-get update
sudo apt-get install -y couchdb

# Setup CouchDB
echo "Setting up CouchDB..."
sudo systemctl enable couchdb
sudo systemctl start couchdb

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements_raspberry_pi.txt

# Setup GPIO permissions
echo "Setting up GPIO permissions..."
sudo usermod -a -G gpio $USER

# Create directories
echo "Creating directories..."
mkdir -p logs
mkdir -p sounds

# Copy configuration
echo "Setting up configuration..."
if [ ! -f config.ini ]; then
    cp config.ini.example config.ini
    echo "Please edit config.ini with your settings"
fi

# Create systemd services
echo "Creating systemd services..."

# Parking Server Service
sudo tee /etc/systemd/system/parking-server.service > /dev/null <<EOF
[Unit]
Description=Parking System Server
After=network.target couchdb.service

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python server/websocket_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Entry Gate Service
sudo tee /etc/systemd/system/parking-entry.service > /dev/null <<EOF
[Unit]
Description=Parking Entry Gate
After=network.target parking-server.service

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python entry-gate/entry_gate.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Exit Gate Service
sudo tee /etc/systemd/system/parking-exit.service > /dev/null <<EOF
[Unit]
Description=Parking Exit Gate
After=network.target parking-server.service

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python exit-gate/exit_gate_gui.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Admin Web Service
sudo tee /etc/systemd/system/parking-admin.service > /dev/null <<EOF
[Unit]
Description=Parking Admin Web Interface
After=network.target parking-server.service

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python admin/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable services
echo "Enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable parking-server
sudo systemctl enable parking-entry
sudo systemctl enable parking-exit
sudo systemctl enable parking-admin

# Create startup script
echo "Creating startup script..."
tee start_parking_system.sh > /dev/null <<EOF
#!/bin/bash
sudo systemctl start parking-server
sleep 5
sudo systemctl start parking-entry
sudo systemctl start parking-exit
sudo systemctl start parking-admin
echo "Parking system started"
systemctl status parking-*
EOF

chmod +x start_parking_system.sh

# Create stop script
tee stop_parking_system.sh > /dev/null <<EOF
#!/bin/bash
sudo systemctl stop parking-entry
sudo systemctl stop parking-exit
sudo systemctl stop parking-admin
sudo systemctl stop parking-server
echo "Parking system stopped"
EOF

chmod +x stop_parking_system.sh

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit config.ini with your CCTV and database settings"
echo "2. Add audio files to sounds/ directory"
echo "3. Test the system: ./start_parking_system.sh"
echo "4. Check status: systemctl status parking-*"
echo "5. View logs: journalctl -u parking-server -f"
echo ""
echo "Admin interface will be available at: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Reboot recommended to ensure all permissions are applied."
