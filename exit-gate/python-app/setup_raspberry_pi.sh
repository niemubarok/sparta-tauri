#!/bin/bash
# Raspberry Pi Setup Script for Exit Gate System
# For Python 3.10+ on Raspberry Pi OS

echo "🍓 Setting up Exit Gate System on Raspberry Pi..."

# Check if running on Raspberry Pi
if [ ! -f /proc/cpuinfo ] || ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "❌ This script is designed for Raspberry Pi only"
    exit 1
fi

echo "✅ Detected Raspberry Pi"

# Update system packages
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-picamera2 \
    python3-libcamera \
    python3-rpi.gpio \
    python3-opencv \
    python3-numpy \
    python3-pil \
    python3-pygame \
    libcamera-apps \
    git

# Enable camera interface
echo "📷 Enabling camera interface..."
sudo raspi-config nonint do_camera 0

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
cd /home/pi
python3 -m venv exit-gate-env
source exit-gate-env/bin/activate

# Install Python packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements_raspberry_pi.txt

# Create app directory
echo "📁 Setting up application directory..."
sudo mkdir -p /opt/exit-gate
sudo chown pi:pi /opt/exit-gate
cp -r app/* /opt/exit-gate/

# Create systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/exit-gate.service > /dev/null <<EOF
[Unit]
Description=Exit Gate System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/exit-gate
Environment=PATH=/home/pi/exit-gate-env/bin
ExecStart=/home/pi/exit-gate-env/bin/python gui_exit_gate.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable exit-gate.service

# Test camera
echo "🧪 Testing camera..."
if [ -x "$(command -v libcamera-still)" ]; then
    libcamera-still --preview -t 1000 --nopreview -o /tmp/test.jpg 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Camera test successful"
        rm -f /tmp/test.jpg
    else
        echo "⚠️ Camera test failed - please check camera connection"
    fi
else
    echo "⚠️ libcamera-still not found"
fi

# Test GPIO
echo "🔌 Testing GPIO..."
python3 -c "
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(24, GPIO.OUT)
    print('✅ GPIO test successful')
    GPIO.cleanup()
except Exception as e:
    print('⚠️ GPIO test failed:', e)
"

echo ""
echo "🎉 Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit configuration: nano /opt/exit-gate/config.ini"
echo "2. Test camera: cd /opt/exit-gate && python3 camera_service.py"
echo "3. Start service: sudo systemctl start exit-gate"
echo "4. Check status: sudo systemctl status exit-gate"
echo "5. View logs: sudo journalctl -u exit-gate -f"
echo ""
echo "🔧 Configuration tips:"
echo "- Enable Raspberry Pi camera in camera section of config.ini"
echo "- Set control_mode to 'gpio' in gate section"
echo "- Configure GPIO pins as needed"
echo ""
echo "⚠️ Remember to reboot if camera was just enabled!"
