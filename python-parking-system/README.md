# Python Parking System

A complete Python implementation of the Sparta Parking System with support for both manless and manual gate operations, ALPR (Automatic License Plate Recognition), and comprehensive parking management.

## Features

- **Dual Mode Operation**: Supports both manless (automatic) and manual gate operations
- **Separate Entry/Exit Gates**: Independent systems for entry and exit processing
- **ALPR Integration**: Built-in license plate recognition using fast-alpr library
- **Camera Support**: USB and IP camera integration for plate and driver monitoring
- **Member Management**: Support for member-based parking with prepaid/postpaid modes
- **Transaction Management**: Complete transaction lifecycle with database persistence
- **WebSocket Communication**: Real-time communication between components
- **Hardware Integration**: Serial port communication for gate control and sensors
- **Web Interface**: Modern web-based control panels for each gate type

## Architecture

```
python-parking-system/
├── core/                   # Core business logic and shared components
│   ├── alpr/              # ALPR engine and processing
│   ├── camera/            # Camera management and capture
│   ├── database/          # Database models and operations
│   ├── hardware/          # Serial port and hardware control
│   └── models/            # Data models and schemas
├── gates/                 # Gate-specific implementations
│   ├── entry/             # Entry gate implementations
│   │   ├── manless/       # Automatic entry gate
│   │   └── manual/        # Manual entry gate
│   └── exit/              # Exit gate implementations
│       ├── manless/       # Automatic exit gate
│       └── manual/        # Manual exit gate
├── api/                   # REST API endpoints
├── websocket/             # WebSocket handlers
├── web/                   # Web interfaces
├── services/              # Background services
└── utils/                 # Utility functions
```

## Installation

1. **Install Python 3.10+**
   ```bash
   python --version  # Should be 3.10 or higher
   ```

2. **Clone and setup**
   ```bash
   cd python-parking-system
   pip install -r requirements.txt
   ```

3. **Initialize ALPR models**
   ```bash
   python scripts/init_alpr_models.py
   ```

4. **Setup database**
   ```bash
   python scripts/init_database.py
   ```

## Usage

### Start Individual Gate Services

```bash
# Entry Gate - Manless Mode
python -m gates.entry.manless.main

# Entry Gate - Manual Mode  
python -m gates.entry.manual.main

# Exit Gate - Manless Mode
python -m gates.exit.manless.main

# Exit Gate - Manual Mode
python -m gates.exit.manual.main
```

### Start Web Interface
```bash
# Main control panel
python -m web.main

# Gate-specific interfaces
python -m web.entry_gate
python -m web.exit_gate
```

### Start Background Services
```bash
# ALPR service (for external ALPR processing)
python -m services.alpr_service

# Database sync service
python -m services.sync_service
```

## Configuration

Configuration is managed through environment variables and config files:

- `config/settings.yaml` - Main application settings
- `config/cameras.yaml` - Camera configurations
- `config/gates.yaml` - Gate-specific settings
- `.env` - Environment-specific variables

## Component Details

### ALPR Engine
- Uses fast-alpr library with yolo-v9-t-384-license-plate-end2end detector
- Supports both local and remote processing
- Configurable confidence thresholds
- Image preprocessing and optimization

### Camera Management
- USB camera support via OpenCV
- IP camera support (RTSP/HTTP)
- Automatic device detection
- Image capture and streaming

### Gate Control
- Serial port communication for hardware gates
- Loop sensor integration
- Emergency controls
- Status monitoring

### Database
- SQLite for local storage
- PostgreSQL for production
- Transaction management
- Member data synchronization

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black .
flake8 .
```

### Development Mode
```bash
# Run with auto-reload
python -m gates.entry.manless.main --dev
```

## API Documentation

When running, API documentation is available at:
- Main API: http://localhost:8000/docs
- Entry Gate API: http://localhost:8001/docs  
- Exit Gate API: http://localhost:8002/docs

## License

This project is part of the Sparta Parking System suite.
