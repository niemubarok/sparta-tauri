# Python Parking System - Standalone Applications

Sistem parking dengan aplikasi terpisah untuk setiap mode gate yang dapat dijalankan di device terpisah.

## Struktur Aplikasi Standalone

```
python-parking-system/
├── src/                          # Shared source code
├── entry-manual/                 # Entry Manual Gate App
│   ├── main.py                   # Standalone entry manual app
│   ├── requirements.txt          # Dependencies
│   ├── .env                      # Configuration
│   ├── start.bat                 # Windows batch starter
│   └── README.md                 # Documentation
├── entry-manless/                # Entry Manless Gate App
│   ├── main.py                   # Standalone entry manless app
│   ├── requirements.txt          # Dependencies
│   ├── .env                      # Configuration
│   ├── start.bat                 # Windows batch starter
│   └── README.md                 # Documentation
├── exit-manual/                  # Exit Manual Gate App
│   ├── main.py                   # Standalone exit manual app
│   ├── requirements.txt          # Dependencies
│   ├── .env                      # Configuration
│   ├── start.bat                 # Windows batch starter
│   └── README.md                 # Documentation
└── exit-manless/                 # Exit Manless Gate App
    ├── main.py                   # Standalone exit manless app
    ├── requirements.txt          # Dependencies
    ├── .env                      # Configuration
    ├── start.bat                 # Windows batch starter
    └── README.md                 # Documentation
```

## Device Allocation

| Device Type | Folder | Port | Mode | Function |
|-------------|--------|------|------|----------|
| Entry Manual | `entry-manual/` | 8001 | Manual | Gate masuk dengan operator |
| Entry Manless | `entry-manless/` | 8002 | Manless | Gate masuk otomatis |
| Exit Manual | `exit-manual/` | 8003 | Manual | Gate keluar dengan operator |
| Exit Manless | `exit-manless/` | 8004 | Manless | Gate keluar otomatis |

## Quick Start

### 1. Entry Manual Gate (Device 1)
```bash
cd entry-manual
python main.py
# atau double-click start.bat
```

### 2. Entry Manless Gate (Device 2)
```bash
cd entry-manless
python main.py
# atau double-click start.bat
```

### 3. Exit Manual Gate (Device 3)
```bash
cd exit-manual
python main.py
# atau double-click start.bat
```

### 4. Exit Manless Gate (Device 4)
```bash
cd exit-manless
python main.py
# atau double-click start.bat
```

## Deployment Strategy

### Untuk Setiap Device:

1. **Copy Folder Aplikasi**
   - Copy folder yang sesuai (entry-manual, entry-manless, dll) ke device target
   - Copy folder `src/` ke level yang sama

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Konfigurasi Environment**
   - Edit file `.env` sesuai device
   - Set DEVICE_ID unik untuk setiap device
   - Konfigurasi database, camera, dll

4. **Jalankan Aplikasi**
   ```bash
   python main.py
   ```

## Shared Components

Semua aplikasi menggunakan shared components dari folder `src/`:
- `src/services/` - Database, ALPR, Camera services
- `src/gates/` - Gate implementations
- `src/core/` - Configuration and models

## Network Configuration

Setiap device menggunakan port yang berbeda:
- Entry Manual: Port 8001
- Entry Manless: Port 8002  
- Exit Manual: Port 8003
- Exit Manless: Port 8004

## Database

Semua device terhubung ke database CouchDB yang sama:
- Host: configurable per device
- Database: `parking_system`
- Fallback: JSON files jika CouchDB tidak tersedia

## Features per Device

### Entry Manual (8001)
- ✅ Operator interface
- ✅ Manual scan ALPR
- ✅ Manual gate control
- ✅ Real-time monitoring

### Entry Manless (8002)
- 🤖 Automatic vehicle detection
- 🤖 Automatic ALPR scanning
- 🤖 Automatic gate control
- 🤖 24/7 monitoring

### Exit Manual (8003)
- ✅ Operator interface
- ✅ Payment validation
- ✅ Manual gate control
- ✅ Exit processing

### Exit Manless (8004)
- 🤖 Automatic vehicle detection
- 🤖 Automatic payment validation
- 🤖 Automatic gate control
- 🤖 24/7 exit processing

## Monitoring

Setiap aplikasi menyediakan:
- Console logging real-time
- File logging (`*_gate.log`)
- Status monitoring setiap 30 detik
- Error handling dengan graceful degradation

## System Requirements

- Python 3.8+
- Windows/Linux support
- Camera device (USB/IP Camera)
- Network connectivity untuk database
- Minimum 4GB RAM per device
- SSD storage recommended

## Troubleshooting

1. **Database Connection Issues**
   - Check CouchDB service
   - Verify network connectivity
   - System falls back to JSON files

2. **Camera Issues**
   - Check camera permissions
   - Verify camera source in `.env`
   - System continues in simulation mode

3. **ALPR Issues**
   - Check model files download
   - Verify GPU/CPU resources
   - System continues with manual input

## Production Deployment

Untuk deployment production, jalankan sebagai service:

### Windows Service
```bash
# Install as Windows service using nssm atau sc
nssm install EntryManualGate python main.py
```

### Linux Systemd
```bash
# Create systemd service
sudo systemctl enable entry-manual-gate.service
sudo systemctl start entry-manual-gate.service
```

Setiap aplikasi dirancang untuk standalone operation dan dapat dijalankan terpisah di device yang berbeda sesuai kebutuhan sistem parking.
