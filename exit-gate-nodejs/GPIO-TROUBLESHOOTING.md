# GPIO Troubleshooting Guide - Exit Gate System

## Overview
GPIO (General Purpose Input/Output) pins pada Raspberry Pi digunakan untuk mengontrol gerbang dan LED indikator. Jika GPIO tidak bekerja, berikut adalah panduan lengkap untuk mengatasi masalah tersebut.

## Quick Fix Command
```bash
# Jalankan script perbaikan otomatis
sudo ./gpio-fix.sh

# Atau jalankan troubleshooting
./gpio-troubleshoot.sh
```

## Masalah Umum dan Solusi

### 1. Permission Error
**Gejala**: Error "Permission denied" saat mengakses GPIO
**Solusi**:
```bash
# Fix permissions
sudo chmod 666 /dev/gpiomem

# Tambah user ke grup gpio
sudo usermod -a -G gpio $USER

# Logout dan login kembali
```

### 2. GPIO Library Missing
**Gejala**: Error "Cannot find module 'raspi-gpio'" atau sejenisnya
**Solusi**:
```bash
# Install GPIO libraries
npm install raspi-gpio rpi-gpio gpio --save

# Atau install system dependencies
sudo apt-get install build-essential python3-dev
```

### 3. Pin Already in Use
**Gejala**: Error "Device or resource busy"
**Solusi**:
```bash
# Check pin usage
lsmod | grep gpio

# Unexport pin
echo 24 > /sys/class/gpio/unexport
echo 25 > /sys/class/gpio/unexport

# Restart service
sudo systemctl restart exit-gate
```

### 4. Wrong Pin Configuration
**Gejala**: GPIO tidak merespons
**Solusi**: Periksa file `.env`:
```bash
GATE_GPIO_PIN=24
LED_GPIO_PIN=25  
GPIO_ACTIVE_HIGH=true
GATE_PULSE_DURATION=500
```

## Manual Testing

### 1. Test GPIO dengan Command Line
```bash
# Export pin
echo 24 > /sys/class/gpio/export
echo 25 > /sys/class/gpio/export

# Set direction
echo "out" > /sys/class/gpio/gpio24/direction
echo "out" > /sys/class/gpio/gpio25/direction

# Test LED (pin 25)
echo "1" > /sys/class/gpio/gpio25/value  # LED ON
sleep 1
echo "0" > /sys/class/gpio/gpio25/value  # LED OFF

# Test Gate (pin 24)
echo "1" > /sys/class/gpio/gpio24/value  # Gate trigger
sleep 0.5
echo "0" > /sys/class/gpio/gpio24/value  # Gate release

# Cleanup
echo 24 > /sys/class/gpio/unexport
echo 25 > /sys/class/gpio/unexport
```

### 2. Test dengan Node.js
```bash
# Run GPIO test script
node gpio-test.js

# Check output untuk error messages
```

### 3. Test dengan Manual Script
```bash
# Run interactive GPIO test
./manual-gpio-test.sh

# Press 'l' untuk toggle LED
# Press 'g' untuk trigger gate
# Press 'q' untuk quit
```

## Hardware Checklist

### 1. Wiring Connections
- **GPIO 24** (Pin 18) → Gate Controller Signal Input
- **GPIO 25** (Pin 22) → LED Positive (+)
- **GND** (Pin 20) → Common Ground
- **3.3V/5V** (Pin 17/4) → Power Supply

### 2. Gate Controller
- ✅ Power supply connected dan ON
- ✅ Signal input terhubung ke GPIO 24
- ✅ Ground connection
- ✅ Gate controller berfungsi normal

### 3. LED Indicator  
- ✅ LED terhubung ke GPIO 25
- ✅ Resistor 220Ω terpasang (untuk LED protection)
- ✅ Ground connection

## Service Management

### Check Service Status
```bash
# Check if service running
sudo systemctl status exit-gate

# View logs
sudo journalctl -u exit-gate -f

# Restart service
sudo systemctl restart exit-gate
```

### Debug Service Issues
```bash
# Stop service
sudo systemctl stop exit-gate

# Run manually to see errors
cd /opt/exit-gate
node server.js

# Check for GPIO initialization errors
```

## Environment Variables

### Required GPIO Settings
```bash
# .env file contents
GATE_GPIO_PIN=24          # GPIO pin untuk gate control
LED_GPIO_PIN=25           # GPIO pin untuk LED indicator  
GPIO_ACTIVE_HIGH=true     # true jika active high, false jika active low
GATE_PULSE_DURATION=500   # Durasi pulse dalam milliseconds
GATE_AUTO_CLOSE_TIME=10   # Auto close time dalam detik
```

### Pin Mapping (BCM vs Physical)
| BCM | Physical | Function |
|-----|----------|----------|
| 24  | 18       | Gate Control |
| 25  | 22       | LED Indicator |
| GND | 20       | Ground |

## Troubleshooting Tools

### 1. GPIO Troubleshoot Script
```bash
./gpio-troubleshoot.sh
```
- Checks Raspberry Pi detection
- Verifies GPIO permissions
- Tests pin access
- Validates library installation

### 2. GPIO Fix Script  
```bash
sudo ./gpio-fix.sh
```
- Fixes common permission issues
- Installs missing libraries
- Updates configuration
- Tests GPIO functionality

### 3. Node.js Diagnostic
```bash
node gpio-test.js
```
- Tests direct GPIO control
- Validates GPIO service
- Simulates real operation

## Advanced Troubleshooting

### 1. Check GPIO Status
```bash
# Check GPIO usage
cat /sys/kernel/debug/gpio

# Check device tree
dtoverlay -l

# Check pin conflicts
sudo dtoverlay -r <overlay_name>
```

### 2. Library-specific Issues

#### raspi-gpio Issues
```bash
# Check raspi-io installation
npm list raspi-io

# Reinstall if needed
npm uninstall raspi-gpio
npm install raspi-gpio --save
```

#### rpi-gpio Issues
```bash
# Check python dependencies
sudo apt-get install python3-dev

# Check native compilation
npm rebuild
```

### 3. System-level Debug
```bash
# Check kernel modules
lsmod | grep gpio

# Check device tree
cat /boot/config.txt | grep gpio

# Check hardware info
cat /proc/device-tree/model
```

## Common Error Messages

### "GLIBCXX_3.4.26 not found"
**Solusi**: Use compatible Node.js version (v18.19.1 included in bundle)

### "Permission denied accessing /dev/gpiomem"
**Solusi**: Run `sudo ./gpio-fix.sh` to fix permissions

### "Device or resource busy"
**Solusi**: Another process using GPIO, restart system or find conflicting process

### "No such file or directory"
**Solusi**: GPIO not exported, check hardware detection

## Testing Checklist

- [ ] Raspberry Pi detected correctly
- [ ] User in gpio group
- [ ] GPIO permissions correct
- [ ] GPIO libraries installed
- [ ] .env configuration valid
- [ ] Hardware connections secure
- [ ] Gate controller powered
- [ ] LED indicator working
- [ ] Service starts without errors
- [ ] GPIO responds to commands

## Support

Jika masalah masih berlanjut setelah mengikuti panduan ini:

1. Run complete diagnostic: `./gpio-troubleshoot.sh`
2. Check service logs: `sudo journalctl -u exit-gate -f`
3. Test hardware manually: `./manual-gpio-test.sh`
4. Verify wiring connections
5. Check gate controller specifications
6. Contact system administrator

## Quick Reference

```bash
# Essential commands
sudo ./gpio-fix.sh                    # Fix common issues
./gpio-troubleshoot.sh               # Diagnose problems  
node gpio-test.js                    # Test GPIO functionality
./manual-gpio-test.sh                # Interactive GPIO test
sudo systemctl restart exit-gate     # Restart service
sudo journalctl -u exit-gate -f      # View logs
```
