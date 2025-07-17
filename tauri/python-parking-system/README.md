# Python Parking System

Sistem parkir Python yang lengkap dengan dukungan ALPR menggunakan fast-alpr library, pemisahan mode manual/manless, dan pemisahan gate entry/exit.

## 📁 Struktur Project

```
python-parking-system/
├── main.py                 # Main entry point
├── cli.py                  # Command line interface
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration example
├── config/                # Configuration files
├── src/                   # Source code
│   ├── core/              # Core models and config
│   ├── services/          # Service layer
│   └── gates/            # Gate implementations
└── tests/                # Test files
```

## 🚀 Cara Menjalankan

### 1. Persiapan Environment

```bash
# Clone atau copy folder ini
cd python-parking-system

# Buat virtual environment
python -m venv venv

# Aktivasi virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Konfigurasi

```bash
# Copy file konfigurasi
copy .env.example .env

# Edit .env sesuai kebutuhan
# Terutama untuk database dan ALPR model paths
```

### 3. Jalankan Sistem

#### Menggunakan Python langsung:
```bash
python main.py
```

#### Menggunakan CLI:
```bash
# Start sistem
python cli.py start

# Cek status
python cli.py status

# List gates yang tersedia
python cli.py list-gates

# Test gate spesifik
python cli.py test-gate entry_manual

# Initialize database
python cli.py init-db
```

#### Menggunakan sebagai Module:
```python
import asyncio
from main import system_manager

# Initialize dan start
async def run_system():
    await system_manager.initialize()
    await system_manager.start()

# Jalankan
asyncio.run(run_system())
```

## 🎯 Gate Types yang Tersedia

### Entry Gates:
1. **Manual Entry Gate** (`entry_manual`)
   - Operator-controlled entry
   - Manual plate input dan auto ALPR
   - Member checking
   - Gate control

2. **Manless Entry Gate** (`entry_manless`)
   - Automatic monitoring (5 detik interval)
   - Auto-processing untuk member
   - Non-member detection dengan alert

### Exit Gates:
1. **Manual Exit Gate** (`exit_manual`)
   - Barcode/transaction ID scanning
   - Plate number search
   - Fee calculation
   - Manual override

2. **Manless Exit Gate** (`exit_manless`)
   - Automatic exit monitoring (3 detik interval)
   - Member auto-processing
   - Non-member payment verification

## 🔧 Fitur Utama

### ALPR Integration
- Fast-ALPR library support
- Confidence thresholding
- Multiple detection attempts
- Base64 image handling

### Camera Support
- USB camera integration
- CCTV camera support (HTTP snapshots)
- Dual camera setup (plate + driver)
- Image capture dan storage

### Hardware Control
- GPIO control (Raspberry Pi)
- Serial communication
- Simulation mode untuk testing

### Database Integration
- SQLAlchemy ORM
- PostgreSQL dan SQLite support
- Transaction management
- Member system integration
- Activity logging

## 💻 Penggunaan sebagai Module

```python
from src.gates import create_gate
from src.services.database import database_service

# Create specific gate
entry_gate = create_gate("entry", "manual", "my_entry_gate")

# Process entry
result = entry_gate.manual_plate_entry("B1234ABC", "operator_01")

# Get status
status = entry_gate.get_status()

# Cleanup
entry_gate.cleanup()
```

## 🔌 API Integration (Future)

Sistem ini dirancang untuk mudah diintegrasikan dengan:
- FastAPI REST endpoints
- WebSocket connections
- Web dashboard
- Mobile applications

## 📊 Database Schema

Sistem menggunakan skema database yang kompatibel dengan sistem Tauri existing:
- `parking_transactions` - Transaksi parkir
- `gate_settings` - Konfigurasi gate
- `activity_logs` - Log aktivitas
- `members` - Data member
- `membership_types` - Tipe membership

## 🛠️ Development

### Testing
```bash
# Run tests
python -m pytest tests/

# Test specific gate
python cli.py test-gate entry_manual
```

### Configuration
Semua konfigurasi dapat diatur melalui file `.env` atau environment variables.

## 📋 Requirements

- Python 3.8+
- fast-alpr library
- OpenCV
- SQLAlchemy
- Pydantic
- (Opsional) PostgreSQL untuk production

## 🎉 Status

✅ **Lengkap dan siap digunakan:**
- Semua 4 gate types implemented
- ALPR integration dengan fast-alpr
- Database services
- Camera services  
- Gate control services
- Main entry point
- CLI interface
- Module structure

Sistem dapat dijalankan baik sebagai standalone application maupun sebagai module untuk integrasi dengan sistem lain.
