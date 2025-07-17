#!/bin/bash

# Quick start script for development

echo "Starting Parking System Components..."

# Function to kill background processes on exit
cleanup() {
    echo "Stopping all components..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Start components in background
echo "Starting Server..."
python server/websocket_server.py &
SERVER_PID=$!

sleep 3

echo "Starting Entry Gate..."
python entry-gate/entry_gate.py &
ENTRY_PID=$!

echo "Starting Exit Gate..."
python exit-gate/exit_gate_gui.py &
EXIT_PID=$!

echo "Starting Admin Interface..."
python admin/app.py &
ADMIN_PID=$!

echo ""
echo "=== Parking System Started ==="
echo "Server PID: $SERVER_PID"
echo "Entry Gate PID: $ENTRY_PID"
echo "Exit Gate PID: $EXIT_PID"
echo "Admin PID: $ADMIN_PID"
echo ""
echo "Admin interface: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop all components"

# Wait for any component to exit
wait
