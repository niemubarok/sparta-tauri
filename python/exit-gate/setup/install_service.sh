#!/bin/bash

# Copy service file to systemd directory
sudo cp exit-gate.service /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable exit-gate.service

# Start the service
sudo systemctl start exit-gate.service

# Check status
sudo systemctl status exit-gate.service
