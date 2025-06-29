# Exit Gate Node.js Application

Aplikasi Exit Gate menggunakan Node.js yang berjalan di Raspberry Pi untuk sistem parkir.

## Features

- ✅ Web-based interface yang dapat diakses melalui browser
- ✅ GPIO control untuk membuka gate menggunakan pin 24
- ✅ LED live indicator pada pin 25
- ✅ Real-time communication dengan WebSocket
- ✅ Database PouchDB untuk sync dengan CouchDB
- ✅ CCTV camera integration
- ✅ Barcode scanner support
- ✅ Audio feedback system
- ✅ Auto-close gate timer
- ✅ Transaction processing
- ✅ Statistics and reporting

## Hardware Requirements

- Raspberry Pi (3B+ atau lebih baru)
- GPIO connection untuk gate control (Pin 24)
- LED indicator (Pin 25)
- USB Barcode Scanner (optional)
- CCTV Camera dengan RTSP stream (optional)
- Speaker untuk audio feedback (optional)

## GPIO Pin Configuration

- **Pin 24**: Gate Control Output (Data)
- **Pin 25**: LED Live Indicator

## Installation

### 🌐 Online Installation (Recommended)

### 1. Clone dan Setup Project

```bash
cd /home/pi
git clone <repository-url> exit-gate-nodejs
cd exit-gate-nodejs
```

### 2. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Raspberry Pi specific GPIO libraries
npm run install-rpi
```

### 3. Configuration

Copy `.env.example` ke `.env` dan sesuaikan konfigurasi:

```bash
cp .env.example .env
nano .env
```

### 4. Test GPIO

```bash
npm run test-gpio
```

### 5. Start Application

```bash
# Production mode
npm start

# Development mode
npm run dev
```

### 📦 Offline Installation (No Internet Required)

Untuk instalasi tanpa koneksi internet, gunakan offline bundle:

#### Windows Development Machine:
```cmd
# Buat offline bundle
.\create-offline-bundle.bat

# Atau gunakan quick bundle
.\quick-bundle.ps1
```

#### Transfer ke Raspberry Pi:
1. Copy folder bundle ke Raspberry Pi (via USB/SD card)
2. Extract dan install:
```bash
cd /path/to/bundle/exit-gate-nodejs
chmod +x install-offline.sh
sudo ./install-offline.sh
```

📖 **Panduan lengkap**: [OFFLINE-INSTALLATION-GUIDE.md](./OFFLINE-INSTALLATION-GUIDE.md)

## Usage

1. Buka browser dan akses `http://raspberry-pi-ip:3000`
2. System akan menampilkan interface exit gate
3. Scan barcode atau input manual license plate
4. System akan memproses transaksi dan membuka gate
5. Gate akan otomatis tertutup setelah waktu yang ditentukan

## API Endpoints

### Gate Control
- `POST /api/gate/open` - Membuka gate
- `POST /api/gate/close` - Menutup gate
- `GET /api/gate/status` - Status gate saat ini
- `POST /api/gate/test` - Test gate operation

### Transaction
- `POST /api/transaction/process` - Proses exit transaction
- `GET /api/transaction/search/:query` - Cari transaksi
- `GET /api/transaction/stats` - Statistik hari ini

### Settings
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings

## WebSocket Events

### Client to Server
- `gate:open` - Request open gate
- `gate:close` - Request close gate
- `transaction:process` - Process transaction
- `scanner:scan` - Barcode scan result

### Server to Client
- `gate:status` - Gate status update
- `transaction:result` - Transaction processing result
- `stats:update` - Statistics update
- `error` - Error messages

## Configuration

Konfigurasi utama di file `.env`:

```env
# Server Configuration
PORT=3000
NODE_ENV=production

# Database Configuration
COUCHDB_URL=http://admin:password@localhost:5984
DATABASE_NAME=parking_system

# GPIO Configuration
GATE_GPIO_PIN=24
LED_GPIO_PIN=25
GPIO_ACTIVE_HIGH=true

# Gate Timing
GATE_AUTO_CLOSE_TIME=10
GATE_PULSE_DURATION=500

# Camera Configuration
PLATE_CAMERA_IP=192.168.1.100
PLATE_CAMERA_USERNAME=admin
PLATE_CAMERA_PASSWORD=admin123
DRIVER_CAMERA_IP=192.168.1.101
DRIVER_CAMERA_USERNAME=admin
DRIVER_CAMERA_PASSWORD=admin123

# Audio Configuration
ENABLE_AUDIO=true
AUDIO_VOLUME=80
```

## File Structure

```
exit-gate-nodejs/
├── server.js              # Main server file
├── package.json           # NPM dependencies
├── .env                   # Environment configuration
├── config/
│   └── database.js        # Database configuration
├── controllers/
│   ├── gateController.js  # Gate control logic
│   ├── transactionController.js # Transaction processing
│   └── settingsController.js    # Settings management
├── services/
│   ├── gpioService.js     # GPIO control service
│   ├── databaseService.js # Database operations
│   ├── cameraService.js   # Camera integration
│   └── audioService.js    # Audio feedback
├── routes/
│   ├── api.js            # API routes
│   └── web.js            # Web routes
├── public/
│   ├── index.html        # Main web interface
│   ├── css/
│   ├── js/
│   └── assets/
├── views/               # HTML templates
└── utils/              # Utility functions
```

## Troubleshooting

### GPIO Permission Issues

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Set GPIO permissions
sudo chmod 666 /dev/gpiomem
```

### Service Setup (Auto-start)

```bash
# Create systemd service
sudo nano /etc/systemd/system/exit-gate.service

# Enable service
sudo systemctl enable exit-gate.service
sudo systemctl start exit-gate.service
```

### Camera Connection Issues

1. Check camera IP dan network connectivity
2. Verify RTSP stream URL
3. Test dengan VLC atau ffplay

### Database Sync Issues

1. Check CouchDB server status
2. Verify network connectivity
3. Check authentication credentials

## Development

### Adding New Features

1. Create controller dalam `controllers/`
2. Add routes dalam `routes/`
3. Update client-side JavaScript dalam `public/js/`
4. Test functionality

### Testing

```bash
# Test GPIO functionality
npm run test-gpio

# Test API endpoints
curl http://localhost:3000/api/gate/status
```

## Support

Untuk support dan bug reports, silakan hubungi tim development atau buat issue di repository.

## License

MIT License - Lihat file LICENSE untuk detail.
