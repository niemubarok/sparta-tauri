# Exit Gate GPIO Setup Guide

Berdasarkan konfigurasi pin yang Anda berikan, berikut adalah panduan lengkap untuk setup GPIO Exit Gate.

## Pin Configuration

### INPUT PINS (Active Low):
- **GPIO 18** = LOOP 1 (Loop detector 1)
- **GPIO 27** = LOOP 2 (Loop detector 2)  
- **GPIO 4**  = STRUK (Structure/Receipt sensor)
- **GPIO 17** = EMERGENCY (Emergency button)

### OUTPUT PINS (Active High):
- **GPIO 24** = TRIGGER 1 (Gate trigger 1)
- **GPIO 23** = TRIGGER 2 (Gate trigger 2)
- **GPIO 25** = LED LIVE (LED Live indicator)

## Cara Mengatasi Error GPIO

### Problem:
```bash
echo "1" > /sys/class/gpio/gpio18/value  # Error: No such file or directory
echo "1" > /sys/class/gpio/gpio27/value  # Error: No such file or directory
echo "1" > /sys/class/gpio/gpio4/value   # Error: No such file or directory
```

### Solution:

#### 1. Transfer bundle terbaru ke Raspberry Pi
```bash
# Bundle terbaru: exit-gate-offline-20250629-171155.zip
scp exit-gate-offline-20250629-171155.zip pi@your-pi-ip:~/Desktop/
```

#### 2. Extract dan install
```bash
ssh pi@your-pi-ip
cd ~/Desktop
unzip exit-gate-offline-20250629-171155.zip
cd exit-gate-offline-20250629-171155
chmod +x *.sh
sudo ./install-offline.sh
```

#### 3. Setup GPIO pins khusus Exit Gate
```bash
sudo ./gpio-setup-exit-gate.sh
```

#### 4. Test semua pin
```bash
./gpio-test-exit-gate.sh
```

#### 5. Test manual individual pins

**Test INPUT pins (baca nilai):**
```bash
cat /sys/class/gpio/gpio18/value  # LOOP 1
cat /sys/class/gpio/gpio27/value  # LOOP 2
cat /sys/class/gpio/gpio4/value   # STRUK
cat /sys/class/gpio/gpio17/value  # EMERGENCY
```

**Test OUTPUT pins (tulis nilai):**
```bash
# Test TRIGGER 1 (GPIO 24)
echo "1" > /sys/class/gpio/gpio24/value  # HIGH
echo "0" > /sys/class/gpio/gpio24/value  # LOW

# Test TRIGGER 2 (GPIO 23)
echo "1" > /sys/class/gpio/gpio23/value  # HIGH
echo "0" > /sys/class/gpio/gpio23/value  # LOW

# Test LED LIVE (GPIO 25)
echo "1" > /sys/class/gpio/gpio25/value  # LED ON
echo "0" > /sys/class/gpio/gpio25/value  # LED OFF
```

## Scripts Available

1. **gpio-setup-exit-gate.sh** - Setup semua pin Exit Gate
2. **gpio-test-exit-gate.sh** - Test quick semua pin
3. **gpio-permission-fix.sh** - Fix permission issues
4. **gpio-simple-test.sh** - Test basic GPIO

## Troubleshooting

### Jika masih ada error permission:
```bash
sudo ./gpio-permission-fix.sh
sudo systemctl restart exit-gate
```

### Jika pin tidak bisa diakses:
```bash
# Manual export pin
sudo -s
echo 18 > /sys/class/gpio/export
echo 27 > /sys/class/gpio/export  
echo 4 > /sys/class/gpio/export
echo 17 > /sys/class/gpio/export
echo 24 > /sys/class/gpio/export
echo 23 > /sys/class/gpio/export
echo 25 > /sys/class/gpio/export

# Set directions
echo "in" > /sys/class/gpio/gpio18/direction
echo "in" > /sys/class/gpio/gpio27/direction
echo "in" > /sys/class/gpio/gpio4/direction
echo "in" > /sys/class/gpio/gpio17/direction
echo "out" > /sys/class/gpio/gpio24/direction
echo "out" > /sys/class/gpio/gpio23/direction
echo "out" > /sys/class/gpio/gpio25/direction

# Fix permissions
chown root:gpio /sys/class/gpio/gpio*/direction /sys/class/gpio/gpio*/value
chmod 660 /sys/class/gpio/gpio*/direction /sys/class/gpio/gpio*/value
```

### Check service status:
```bash
sudo systemctl status exit-gate
sudo journalctl -u exit-gate -f
```

### Web interface:
```
http://your-pi-ip:3000
```

## Expected Results

Setelah setup berhasil, semua pin harus bisa diakses:
- **INPUT pins**: Bisa dibaca nilai current (0 atau 1)
- **OUTPUT pins**: Bisa ditulis nilai (0 atau 1)
- **Web interface**: Button GPIO test berfungsi
- **LED heartbeat**: Berkedip setiap detik

Pin 24 yang sudah berhasil sebelumnya menunjukkan bahwa sistem GPIO berfungsi, hanya perlu setup untuk pin lainnya.
