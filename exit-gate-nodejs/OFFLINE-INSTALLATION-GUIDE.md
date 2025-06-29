# Offline Installation Guide

Panduan lengkap untuk membuat dan menginstall Exit Gate application tanpa koneksi internet.

## 📋 Prerequisites

### Untuk Development Machine (Windows)
- Windows 10/11
- PowerShell 5.1 atau lebih baru
- Node.js dan NPM terinstall
- Internet connection (untuk download dependencies)

### Untuk Raspberry Pi Target
- Raspberry Pi 3B+ atau lebih baru
- Raspbian/Raspberry Pi OS
- GPIO pins 24 dan 25 tersedia
- SD card dengan minimal 8GB free space

## 🚀 Cara Membuat Offline Bundle

### Opsi 1: Quick Bundle (Paling Mudah)

1. Buka PowerShell di folder project
2. Jalankan quick bundle:
   ```powershell
   .\quick-bundle.ps1
   ```
3. Script akan otomatis:
   - Download semua dependencies
   - Bundle Node.js ARM binary
   - Create installation scripts
   - Compress ke ZIP file

### Opsi 2: Custom Bundle

1. Jalankan script dengan opsi custom:
   ```cmd
   .\create-offline-bundle.bat
   ```
2. Atau langsung dengan PowerShell:
   ```powershell
   .\create-offline-bundle.ps1 -OutputDir "my-bundle" -IncludeSystemPackages -Verbose
   ```

### Opsi 3: Manual Dependencies

Jika bundling otomatis gagal:
```powershell
.\download-dependencies.ps1 -Packages @("express", "socket.io", "pouchdb-node") -DownloadNode
```

## 📦 Isi Bundle

Bundle yang dibuat akan berisi:

```
offline-bundle/
├── exit-gate-nodejs/
│   ├── package.json              # NPM dependencies
│   ├── server.js                 # Main application
│   ├── services/                 # App services
│   ├── routes/                   # API routes
│   ├── public/                   # Web interface
│   ├── npm-cache/                # Cached dependencies
│   ├── node-v20.11.0-linux-armv7l.tar.xz  # Node.js ARM
│   ├── install-offline.sh        # Pi installer
│   ├── install-test-windows.bat  # Windows tester
│   ├── .env.example              # Configuration template
│   ├── system-packages.txt       # Required system packages
│   └── README-BUNDLE.md          # Installation guide
└── exit-gate-nodejs-offline-bundle.zip  # Compressed bundle
```

## 🔧 Installation di Raspberry Pi

### 🚨 BENAR-BENAR TANPA INTERNET

Ada 2 skenario offline installation:

#### Skenario A: Pi Sudah Punya Build Tools
Jika Pi sudah pernah install `build-essential`, `python3-dev`, dll:

```bash
cd /path/to/bundle/exit-gate-nodejs
chmod +x install-offline.sh
sudo ./install-offline.sh
```

#### Skenario B: Pi Belum Pernah Install Development Tools  
Untuk Pi yang BENAR-BENAR bersih dan tidak pernah konek internet:

**Step 1: Download System Packages (Di Pi Lain yang Ada Internet)**
```bash
# Di Pi yang ada internet (model yang sama)
chmod +x download-system-packages.sh
./download-system-packages.sh
```

**Step 2: Copy ke Pi Offline**
```bash
# Copy folder system-packages ke Pi offline
scp -r system-packages/ pi@offline-pi-ip:/home/pi/exit-gate-nodejs/
```

**Step 3: Install di Pi Offline**
```bash
# Di Pi offline - sekarang ada folder system-packages dengan .deb files
sudo ./install-offline.sh
```

### Step 2: Transfer Bundle ke Pi Offline

**Opsi A - USB Drive:**
1. Copy folder `exit-gate-nodejs` ke USB drive
2. Mount USB di Pi: `sudo mkdir /mnt/usb && sudo mount /dev/sda1 /mnt/usb`
3. Copy ke Pi: `cp -r /mnt/usb/exit-gate-nodejs /home/pi/`

**Opsi B - SCP (jika ada network):**
```bash
scp -r exit-gate-nodejs/ pi@192.168.1.100:/home/pi/
```

**Opsi C - ZIP extraction:**
```bash
unzip exit-gate-nodejs-offline-bundle.zip
```

### Step 2: Install System Packages (HANYA JIKA DIPERLUKAN)

**SKIP STEP INI** jika Pi sudah ada build tools, atau jika Anda sudah download .deb packages di step sebelumnya.

Untuk Pi yang benar-benar bersih:
```bash
sudo apt update
sudo apt install build-essential python3-dev libasound2-dev git curl wget unzip
```

**Untuk instalasi truly offline**, download packages dulu di Pi yang ada internet:
```bash
./download-system-packages.sh
# Copy .deb files ke Pi offline
sudo dpkg -i *.deb
```

### Step 3: Fix Line Endings (Jika Ada Error)

Jika mendapat error seperti `/bin/bash^M: bad interpreter`:

```bash
# Fix line endings untuk semua script
bash fix-line-endings.sh

# Atau manual fix untuk install-offline.sh
sed -i 's/\r$//' install-offline.sh
chmod +x install-offline.sh
```

### Step 4: Run Installer

```bash
cd /home/pi/exit-gate-nodejs
chmod +x install-offline.sh
sudo ./install-offline.sh
```

Installer akan:
- Extract Node.js ARM binary ke `/usr/local`
- Install npm dependencies dari cache
- Create app directory di `/opt/exit-gate-nodejs`
- Setup systemd service
- Configure permissions

### Step 5: Configure Application

Edit configuration file:
```bash
sudo nano /opt/exit-gate-nodejs/.env
```

Contoh konfigurasi:
```env
NODE_ENV=production
PORT=3000
GPIO_GATE_PIN=24
GPIO_LED_PIN=25
GATE_PULSE_DURATION=2000
DB_NAME=exit_gate_db
COUCH_URL=http://localhost:5984
```

### Step 6: Start Service

```bash
# Start service
sudo systemctl start exit-gate

# Enable auto-start
sudo systemctl enable exit-gate

# Check status
sudo systemctl status exit-gate

# View logs
sudo journalctl -u exit-gate -f
```

## 🧪 Testing Installation

### Test di Windows (Development)

1. Navigate ke bundle folder
2. Run: `install-test-windows.bat`
3. Start: `npm start`
4. Browse: `http://localhost:3000`

### Test di Raspberry Pi

1. Check service status:
   ```bash
   sudo systemctl status exit-gate
   ```

2. Test GPIO (if hardware connected):
   ```bash
   cd /opt/exit-gate-nodejs
   sudo node -e "
   const gpio = require('./services/gpioService');
   gpio.openGate();
   setTimeout(() => process.exit(), 3000);
   "
   ```

3. Test web interface:
   ```bash
   curl http://localhost:3000
   ```

## 🔍 Troubleshooting

### Common Issues

**1. Node.js tidak terdeteksi:**
```bash
# Check Node.js installation
which node
node --version

# Manual extraction jika installer gagal
sudo tar -xf node-v*.tar.xz -C /usr/local --strip-components=1
```

**2. NPM dependencies gagal install:**
```bash
# Clear npm cache
npm cache clean --force

# Install with verbose output
npm ci --verbose

# Install individual packages
npm install express socket.io pouchdb-node
```

**3. GPIO permission error:**
```bash
# Add user to gpio group
sudo usermod -a -G gpio pi

# Check GPIO permissions
ls -la /dev/gpiomem
```

**4. Service gagal start:**
```bash
# Check detailed logs
sudo journalctl -u exit-gate --no-pager

# Check working directory
sudo systemctl cat exit-gate

# Test manual start
cd /opt/exit-gate-nodejs
sudo -u pi node server.js
```

### Recovery Commands

```bash
# Reinstall service
sudo systemctl stop exit-gate
sudo systemctl disable exit-gate
sudo rm /etc/systemd/system/exit-gate.service
sudo systemctl daemon-reload

# Re-run installer
cd /home/pi/exit-gate-nodejs
sudo ./install-offline.sh

# Check application files
ls -la /opt/exit-gate-nodejs/
sudo chown -R pi:pi /opt/exit-gate-nodejs/
```

## 📊 Monitoring

### Service Monitoring
```bash
# Real-time logs
sudo journalctl -u exit-gate -f

# System resources
htop

# GPIO status
gpio readall  # jika wiringpi terinstall
```

### Application Monitoring
```bash
# Check web interface
curl -I http://localhost:3000

# Check API endpoints
curl http://localhost:3000/api/status

# Check database
curl http://localhost:3000/api/test-db
```

## 🔄 Updates

Untuk update aplikasi tanpa internet:

1. Create bundle baru di development machine
2. Stop service di Pi: `sudo systemctl stop exit-gate`
3. Backup current: `sudo cp -r /opt/exit-gate-nodejs /opt/exit-gate-nodejs.backup`
4. Transfer dan install bundle baru
5. Start service: `sudo systemctl start exit-gate`

## 📞 Support

Jika ada masalah:
1. Check logs: `sudo journalctl -u exit-gate -n 50`
2. Check system: `dmesg | tail`
3. Check network: `ip addr show`
4. Check GPIO: `cat /sys/kernel/debug/gpio`

## 📄 File Locations

- **Application**: `/opt/exit-gate-nodejs/`
- **Service file**: `/etc/systemd/system/exit-gate.service`
- **Logs**: `journalctl -u exit-gate`
- **Configuration**: `/opt/exit-gate-nodejs/.env`
- **Database**: `/opt/exit-gate-nodejs/data/` (local)
