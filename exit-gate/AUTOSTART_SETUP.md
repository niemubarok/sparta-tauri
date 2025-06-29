# EXIT GATE GUI AUTOSTART SETUP

## Problem
GUI Exit Gate tidak otomatis terbuka setelah reboot Raspberry Pi.

## Solution
Setup autostart menggunakan systemd service dan desktop autostart sebagai backup.

## Files yang Dibuat/Diupdate

### 1. Service File: `exit-gate-gui.service`
```bash
[Unit]
Description=Exit Gate GUI System
After=graphical-session.target
Wants=graphical-session.target
After=network.target
After=multi-user.target

[Service]
Type=simple
User=pi
Group=pi
Environment=DISPLAY=:0.0
Environment=HOME=/home/pi
Environment=USER=pi
Environment=XDG_RUNTIME_DIR=/run/user/1000
WorkingDirectory=/home/pi/exit-gate/python-app
ExecStartPre=/bin/sleep 10
ExecStart=/bin/bash /home/pi/exit-gate/python-app/start_gui.sh
Restart=always
RestartSec=15
StandardOutput=journal
StandardError=journal
KillMode=mixed
TimeoutStopSec=30

[Install]
WantedBy=graphical-session.target
WantedBy=multi-user.target
```

### 2. Startup Script: `start_gui.sh`
- Menunggu X server ready
- Kill existing instances 
- Start GUI dengan error handling
- Logging ke file

### 3. Setup Script: `setup_autostart.sh`
- Install systemd service
- Create desktop autostart
- Enable services
- Test dependencies

### 4. Troubleshooting Script: `troubleshoot_autostart.sh`
- Check service status
- Check logs
- Check dependencies
- Provide solutions

## Installation Commands

### Option 1: Manual SSH
```bash
# Copy files ke Pi
scp -r python-app/* pi@192.168.1.100:/home/pi/exit-gate/python-app/

# SSH ke Pi dan setup
ssh pi@192.168.1.100
cd /home/pi/exit-gate/python-app
chmod +x *.sh
./setup_autostart.sh
sudo reboot
```

### Option 2: PowerShell Script (Windows)
```powershell
# Edit IP address di script jika perlu
.\setup-autostart-rpi.ps1

# Atau dengan custom IP
.\setup-autostart-rpi.ps1 -RpiIP "192.168.1.150"
```

### Option 3: Quick Install
```bash
# Di Raspberry Pi
cd /home/pi/exit-gate/python-app
./quick_install_autostart.sh
sudo reboot
```

## Verification

### Check if GUI is running
```bash
ps aux | grep gui_exit_gate
```

### Check service status
```bash
sudo systemctl status exit-gate-gui.service
```

### Check logs
```bash
# Service logs
sudo journalctl -u exit-gate-gui.service -f

# GUI startup logs
tail -f /home/pi/exit-gate/python-app/gui_startup.log
```

### Manual start (for testing)
```bash
cd /home/pi/exit-gate/python-app
python gui_exit_gate.py
```

## Troubleshooting

### GUI tidak muncul setelah reboot
1. Wait 2-3 minutes setelah boot
2. Run troubleshoot script:
   ```bash
   /home/pi/exit-gate/python-app/troubleshoot_autostart.sh
   ```
3. Check X server:
   ```bash
   echo $DISPLAY
   xset q
   ```

### Service gagal start
```bash
# Check service status
sudo systemctl status exit-gate-gui.service

# View logs
sudo journalctl -u exit-gate-gui.service -n 50

# Restart service
sudo systemctl restart exit-gate-gui.service
```

### Permission errors
```bash
# Fix permissions
sudo chown -R pi:pi /home/pi/exit-gate
chmod +x /home/pi/exit-gate/python-app/*.sh
```

### Python/Tkinter errors
```bash
# Test Python and Tkinter
python -c "import Tkinter; print('OK')"  # Python 2
python3 -c "import tkinter; print('OK')"  # Python 3

# Install if missing
sudo apt update
sudo apt install python-tk python3-tk
```

## Manual Control Commands

### Enable/Disable Autostart
```bash
# Enable
sudo systemctl enable exit-gate-gui.service

# Disable
sudo systemctl disable exit-gate-gui.service
```

### Start/Stop Service
```bash
# Start
sudo systemctl start exit-gate-gui.service

# Stop
sudo systemctl stop exit-gate-gui.service

# Restart
sudo systemctl restart exit-gate-gui.service
```

### Remove Autostart
```bash
# Disable service
sudo systemctl disable exit-gate-gui.service
sudo systemctl stop exit-gate-gui.service

# Remove desktop autostart
rm -f /home/pi/.config/autostart/exit-gate-gui.desktop

# Remove service file
sudo rm -f /etc/systemd/system/exit-gate-gui.service
sudo systemctl daemon-reload
```

## Expected Behavior

After successful setup:
1. Pi boots up
2. Wait ~30-60 seconds for services to start
3. GUI automatically appears on screen
4. Debug mode ON by default
5. Ready for barcode scanning

## Notes

- GUI akan restart otomatis jika crash (RestartSec=15)
- Dual setup: systemd service + desktop autostart
- Logging tersedia untuk debugging
- Debug mode default ON untuk testing
- Service menunggu 10 detik sebelum start (ExecStartPre)
