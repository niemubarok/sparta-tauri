#!/bin/bash
# Exit Gate GUI Startup Script
# Auto-start script untuk GUI Exit Gate System

# Set environment variables
export DISPLAY=:0.0
export HOME=/home/pi
export USER=pi

# Change to correct directory
cd /home/pi/exit-gate/python-app

echo "=== EXIT GATE GUI STARTUP ==="
echo "Date: $(date)"
echo "Display: $DISPLAY"
echo "User: $USER"
echo "Home: $HOME"
echo "Working Directory: $(pwd)"

# Wait for X server to be ready
echo "Waiting for X server..."
for i in {1..30}; do
    if xset q &>/dev/null; then
        echo "X server ready after $i seconds"
        break
    fi
    echo "Waiting for X server... ($i/30)"
    sleep 1
done

# Kill any existing instances
echo "Killing existing instances..."
pkill -f "python.*gui_exit_gate.py" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true

# Wait a moment
sleep 3

# Start GUI application with error handling
echo "Starting Exit Gate GUI..."
python gui_exit_gate.py 2>&1 | tee -a gui_startup.log

echo "Exit Gate GUI stopped at $(date)"
