#!/bin/bash
# Exit Gate GUI Startup Script
# Auto-start script untuk GUI Exit Gate System

export DISPLAY=:0.0
cd /home/pi/exit-gate/python-app

echo "Starting Exit Gate GUI System..."
echo "Date: $(date)"
echo "Display: $DISPLAY"

# Kill any existing instances
pkill -f "python.*gui_exit_gate.py" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true

# Wait a moment
sleep 2

# Start GUI application
python gui_exit_gate.py 2>&1 | tee -a gui_startup.log

echo "Exit Gate GUI stopped at $(date)"
