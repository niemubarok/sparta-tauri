#!/bin/bash
# Quick install script untuk autostart Exit Gate GUI
# Jalankan script ini di Raspberry Pi untuk setup autostart

echo "=== QUICK AUTOSTART SETUP FOR EXIT GATE GUI ==="
echo ""

# Make all scripts executable
chmod +x /home/pi/exit-gate/python-app/*.sh

# Run setup
echo "Running autostart setup..."
/home/pi/exit-gate/python-app/setup_autostart.sh

echo ""
echo "=== SETUP COMPLETE ==="
echo ""
echo "Testing GUI manually in background..."
cd /home/pi/exit-gate/python-app
nohup python gui_exit_gate.py > test_gui.log 2>&1 &
GUI_PID=$!

echo "GUI started with PID: $GUI_PID"
echo "Waiting 5 seconds to check if GUI is running..."
sleep 5

if kill -0 $GUI_PID 2>/dev/null; then
    echo "✅ GUI is running successfully!"
    echo "Stopping test GUI..."
    kill $GUI_PID 2>/dev/null
    sleep 2
    pkill -f "python.*gui_exit_gate.py" 2>/dev/null || true
else
    echo "❌ GUI failed to start. Check test_gui.log for errors:"
    cat test_gui.log
fi

echo ""
echo "Next steps:"
echo "1. Reboot Raspberry Pi: sudo reboot"
echo "2. Wait 2-3 minutes after boot"
echo "3. Check if GUI is running automatically"
echo ""
echo "If problems occur, run troubleshooting:"
echo "/home/pi/exit-gate/python-app/troubleshoot_autostart.sh"
