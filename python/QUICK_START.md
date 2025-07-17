# Quick Start Guide

## Immediate Testing (No Setup Required)

### 1. Test Admin Interface
```bash
# Windows
quick_test_admin.bat

# Or manually:
cd admin
python test_admin.py
```
Access: http://localhost:5000

### 2. Quick System Test
```bash
python quick_test.py
```

## Full Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database (Optional for testing)
- Install CouchDB
- Default: localhost:5984, admin/admin

### 3. Run All Components
```bash
# Windows
start_dev.bat

# Linux/Mac
chmod +x start_dev.sh
./start_dev.sh
```

## Components

- **Server**: WebSocket + ALPR processing
- **Entry Gate**: Vehicle entry management
- **Exit Gate**: Vehicle exit management  
- **Admin**: Web interface (port 5000)

## Configuration

Edit `config.ini` for:
- Database connection
- CCTV settings
- GPIO pins
- Network settings

## Troubleshooting

1. **Import Errors**: Run `pip install -r requirements.txt`
2. **Database Errors**: Install CouchDB or use test mode
3. **GPIO Errors**: Normal on desktop (simulation mode)
4. **Permission Errors**: Run as administrator/sudo

## Files Overview

- `admin/test_admin.py` - Admin interface with mock data
- `quick_test.py` - Component testing
- `test_system.py` - System validation
- `config.ini` - Main configuration
- `requirements.txt` - Python dependencies
