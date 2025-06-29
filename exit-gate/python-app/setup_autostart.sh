#!/bin/bash
# Exit Gate GUI Auto-start Script

# Create desktop entry for auto-start
cat > /home/pi/.config/autostart/exit-gate.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Exit Gate Control
Comment=Exit Gate Control System
Exec=/home/pi/exit-gate/python-app/start_gui.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

# Create start script
cat > /home/pi/exit-gate/python-app/start_gui.sh << 'EOF'
#!/bin/bash
cd /home/pi/exit-gate/python-app
export DISPLAY=:0
python exit_gate_gui.py >> gui.log 2>&1
EOF

chmod +x /home/pi/exit-gate/python-app/start_gui.sh

echo "Exit Gate GUI auto-start configured"
echo "GUI will start automatically on next boot"
echo ""
echo "Manual commands:"
echo "1. Start GUI: cd /home/pi/exit-gate/python-app && python exit_gate_gui.py"
echo "2. Check GUI log: tail -f /home/pi/exit-gate/python-app/gui.log"
echo "3. Test now: /home/pi/exit-gate/python-app/start_gui.sh"
