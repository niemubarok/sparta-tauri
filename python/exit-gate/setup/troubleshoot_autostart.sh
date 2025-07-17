#!/bin/bash
# Troubleshoot Autostart untuk Exit Gate GUI
# Script untuk debugging masalah autostart

echo "=== EXIT GATE GUI AUTOSTART TROUBLESHOOTING ==="
echo "Date: $(date)"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}1. Checking systemd service status...${NC}"
sudo systemctl status exit-gate-gui.service --no-pager || echo "Service not found or not running"
echo ""

echo -e "${BLUE}2. Checking if service is enabled...${NC}"
sudo systemctl is-enabled exit-gate-gui.service || echo "Service not enabled"
echo ""

echo -e "${BLUE}3. Checking service logs...${NC}"
echo "Last 20 lines from service logs:"
sudo journalctl -u exit-gate-gui.service -n 20 --no-pager || echo "No logs available"
echo ""

echo -e "${BLUE}4. Checking desktop autostart...${NC}"
if [ -f "/home/pi/.config/autostart/exit-gate-gui.desktop" ]; then
    echo -e "${GREEN}Desktop autostart file exists${NC}"
    echo "Content:"
    cat /home/pi/.config/autostart/exit-gate-gui.desktop
else
    echo -e "${RED}Desktop autostart file NOT found${NC}"
fi
echo ""

echo -e "${BLUE}5. Checking startup script...${NC}"
if [ -f "/home/pi/exit-gate/python-app/start_gui.sh" ]; then
    echo -e "${GREEN}Startup script exists${NC}"
    ls -la /home/pi/exit-gate/python-app/start_gui.sh
    echo ""
    echo "Is executable: $([ -x /home/pi/exit-gate/python-app/start_gui.sh ] && echo 'YES' || echo 'NO')"
else
    echo -e "${RED}Startup script NOT found${NC}"
fi
echo ""

echo -e "${BLUE}6. Checking GUI application...${NC}"
if [ -f "/home/pi/exit-gate/python-app/gui_exit_gate.py" ]; then
    echo -e "${GREEN}GUI application exists${NC}"
    ls -la /home/pi/exit-gate/python-app/gui_exit_gate.py
else
    echo -e "${RED}GUI application NOT found${NC}"
fi
echo ""

echo -e "${BLUE}7. Checking Python and Tkinter...${NC}"
python --version 2>/dev/null || echo "Python 2 not available"
python3 --version 2>/dev/null || echo "Python 3 not available"
python -c "import Tkinter; print('Python 2 Tkinter: OK')" 2>/dev/null || echo "Python 2 Tkinter: Not available"
python3 -c "import tkinter; print('Python 3 tkinter: OK')" 2>/dev/null || echo "Python 3 tkinter: Not available"
echo ""

echo -e "${BLUE}8. Checking X server and display...${NC}"
echo "DISPLAY environment: $DISPLAY"
echo "X server status:"
ps aux | grep -v grep | grep -E "(Xorg|startx)" || echo "X server not found"
echo ""

echo -e "${BLUE}9. Checking running processes...${NC}"
echo "Exit Gate related processes:"
ps aux | grep -v grep | grep -E "(gui_exit_gate|exit.*gate)" || echo "No Exit Gate processes running"
echo ""

echo -e "${BLUE}10. Checking recent logs...${NC}"
if [ -f "/home/pi/exit-gate/python-app/gui_startup.log" ]; then
    echo "Last 10 lines from GUI startup log:"
    tail -10 /home/pi/exit-gate/python-app/gui_startup.log
else
    echo "No GUI startup log found"
fi
echo ""

echo -e "${YELLOW}=== TROUBLESHOOTING COMPLETE ===${NC}"
echo ""
echo "Common solutions:"
echo "1. Re-enable service: sudo systemctl enable exit-gate-gui.service"
echo "2. Restart service: sudo systemctl restart exit-gate-gui.service"
echo "3. Manual start: /home/pi/exit-gate/python-app/start_gui.sh"
echo "4. Re-run setup: /home/pi/exit-gate/python-app/setup_autostart.sh"
echo "5. Check logs: sudo journalctl -u exit-gate-gui.service -f"
echo ""
echo "If still not working, try:"
echo "- Check if GUI works manually: cd /home/pi/exit-gate/python-app && python gui_exit_gate.py"
echo "- Reboot and wait 2-3 minutes for services to start"
echo "- Check if X server is running: echo \$DISPLAY"
