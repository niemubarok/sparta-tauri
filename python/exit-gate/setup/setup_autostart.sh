#!/bin/bash
# Setup Autostart untuk Exit Gate GUI
# Script untuk mengkonfigurasi autostart di Raspberry Pi

echo "=== EXIT GATE GUI AUTOSTART SETUP ==="
echo "Date: $(date)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up autostart for Exit Gate GUI...${NC}"

# 1. Make scripts executable
echo "Making scripts executable..."
sudo chmod +x /home/pi/exit-gate/python-app/start_gui.sh
sudo chmod +x /home/pi/exit-gate/python-app/setup_autostart.sh

# 2. Copy systemd service file
echo "Installing systemd service..."
sudo cp /home/pi/exit-gate/python-app/exit-gate-gui.service /etc/systemd/system/

# 3. Reload systemd and enable service
echo "Enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable exit-gate-gui.service

# 4. Check service status
echo "Checking service status..."
sudo systemctl status exit-gate-gui.service --no-pager || true

# 5. Alternative: Desktop autostart (backup method)
echo "Setting up desktop autostart as backup..."
mkdir -p /home/pi/.config/autostart

cat > /home/pi/.config/autostart/exit-gate-gui.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Exit Gate GUI
Comment=Exit Gate System GUI Application
Exec=/bin/bash /home/pi/exit-gate/python-app/start_gui.sh
Icon=application-x-executable
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Terminal=false
StartupNotify=false
EOF

echo "Desktop autostart file created"

# 6. Create startup log directory
echo "Creating log directory..."
mkdir -p /home/pi/exit-gate/logs
sudo chown pi:pi /home/pi/exit-gate/logs

# 7. Test GUI can run
echo "Testing GUI dependencies..."
cd /home/pi/exit-gate/python-app
python -c "import Tkinter; print('Tkinter OK')" 2>/dev/null || python -c "import tkinter; print('tkinter OK')" || echo "WARNING: Tkinter not available"

echo -e "${GREEN}=== AUTOSTART SETUP COMPLETE ===${NC}"
echo ""
echo "Services configured:"
echo "1. Systemd service: exit-gate-gui.service"
echo "2. Desktop autostart: ~/.config/autostart/exit-gate-gui.desktop"
echo ""
echo "To test manually:"
echo "sudo systemctl start exit-gate-gui.service"
echo "sudo systemctl status exit-gate-gui.service"
echo ""
echo "To check logs:"
echo "sudo journalctl -u exit-gate-gui.service -f"
echo "tail -f /home/pi/exit-gate/python-app/gui_startup.log"
echo ""
echo "To disable autostart:"
echo "sudo systemctl disable exit-gate-gui.service"
echo ""
echo -e "${YELLOW}Please reboot to test autostart: sudo reboot${NC}"
