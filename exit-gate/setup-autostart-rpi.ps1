#!/usr/bin/env pwsh
# PowerShell script untuk copy files dan setup autostart di Raspberry Pi

param(
    [string]$RpiIP = "192.168.1.100",
    [string]$RpiUser = "pi"
)

Write-Host "=== SETUP AUTOSTART EXIT GATE GUI DI RASPBERRY PI ===" -ForegroundColor Green
Write-Host "Target: $RpiUser@$RpiIP" -ForegroundColor Yellow
Write-Host ""

# Set variables
$LocalPath = "E:\DEVS\spartakuler\exit-gate\python-app"
$RemotePath = "/home/pi/exit-gate/python-app"

Write-Host "Copying files to Raspberry Pi..." -ForegroundColor Blue

# Copy semua file python dan script
$FilesToCopy = @(
    "gui_exit_gate.py",
    "gate_service.py", 
    "usb_barcode_scanner.py",
    "database_service.py",
    "config.py",
    "start_gui.sh",
    "setup_autostart.sh", 
    "troubleshoot_autostart.sh",
    "quick_install_autostart.sh",
    "exit-gate-gui.service"
)

foreach ($File in $FilesToCopy) {
    $LocalFile = Join-Path $LocalPath $File
    if (Test-Path $LocalFile) {
        Write-Host "Copying $File..." -ForegroundColor Gray
        scp $LocalFile "${RpiUser}@${RpiIP}:${RemotePath}/"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $File copied successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to copy $File" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️ $File not found locally" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Setting up autostart on Raspberry Pi..." -ForegroundColor Blue

# SSH ke Pi dan jalankan setup
$SetupCommands = @"
cd /home/pi/exit-gate/python-app
chmod +x *.sh
echo 'Running autostart setup...'
./quick_install_autostart.sh
echo ''
echo 'Checking service status:'
sudo systemctl status exit-gate-gui.service --no-pager || true
echo ''
echo 'Setup complete! Ready to reboot.'
"@

ssh "${RpiUser}@${RpiIP}" $SetupCommands

Write-Host ""
Write-Host "=== SETUP COMPLETE ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Reboot Raspberry Pi: ssh $RpiUser@$RpiIP 'sudo reboot'"
Write-Host "2. Wait 2-3 minutes after reboot"
Write-Host "3. Check if GUI started: ssh $RpiUser@$RpiIP 'ps aux | grep gui_exit_gate'"
Write-Host ""
Write-Host "Troubleshooting:" -ForegroundColor Cyan
Write-Host "ssh $RpiUser@$RpiIP '/home/pi/exit-gate/python-app/troubleshoot_autostart.sh'"
Write-Host ""
Write-Host "Manual commands:" -ForegroundColor Magenta
Write-Host "- Start service: ssh $RpiUser@$RpiIP 'sudo systemctl start exit-gate-gui.service'"
Write-Host "- Check logs: ssh $RpiUser@$RpiIP 'sudo journalctl -u exit-gate-gui.service -f'"
Write-Host "- Test GUI: ssh $RpiUser@$RpiIP 'cd /home/pi/exit-gate/python-app && python gui_exit_gate.py'"
