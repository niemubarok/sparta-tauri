# Exit Gate System - Python Implementation

Complete Python implementation of the exit gate system compatible with Python 2.7 and optimized for Raspberry Pi 3 deployment.

## Features

- ✅ **Barcode Scanner Integration** - USB barcode scanner support with keyboard input simulation
- ✅ **Database Operations** - CouchDB/PouchDB compatible transaction management
- ✅ **Gate Control** - GPIO and Serial communication for gate hardware
- ✅ **CCTV Camera Integration** - HTTP-based image capture from IP cameras
- ✅ **Audio Feedback** - Sound system with pygame for user feedback
- ✅ **Web Interface** - Flask-based responsive web application
- ✅ **Real-time Monitoring** - Live status updates and system monitoring
- ✅ **Cross-platform** - Works on Windows, Linux, and Raspberry Pi
- ✅ **Python 2.7 Compatible** - Uses compatible packages and syntax

## Quick Start

### Raspberry Pi Installation

```bash
# Clone or copy the python-app folder to your Raspberry Pi
cd python-app

# Run the quick setup script
chmod +x quick-setup.sh
./quick-setup.sh

# Start the application
./start.sh
```

### Manual Installation

```bash
# Install system dependencies (Raspberry Pi)
sudo apt-get update
sudo apt-get install python-pip python-dev build-essential git curl wget ffmpeg portaudio19-dev alsa-utils pulseaudio libjpeg-dev libpng-dev libfreetype6-dev libffi-dev libssl-dev

# Install Python dependencies
pip install -r requirements.txt

# Create configuration
python -c "from config import Config; Config().save()"

# Start the application
python main.py
```

## Usage

### Web Interface

Access the web interface at `http://localhost:5000` or `http://<your-pi-ip>:5000`

- **Main Dashboard** - Real-time system status and transaction monitoring
- **Settings Page** - Configure all system parameters
- **Manual Controls** - Test gates, cameras, and other components

### Configuration

Edit `config.ini` to configure:

- Database connection (CouchDB/PouchDB sync)
- Gate control method (GPIO or Serial)
- Camera settings (IP addresses, credentials)
- Scanner parameters
- Audio settings
- GPIO pin assignments

### API Endpoints

- `GET /api/status` - System status and statistics
- `POST /api/scan` - Process barcode scan
- `POST /api/gate/open` - Open gate manually
- `POST /api/gate/close` - Close gate manually
- `GET/POST /api/config` - Get/set configuration
- `GET /api/camera/test/<camera>` - Test camera capture

## Hardware Requirements

### Raspberry Pi 3/4
- Raspberry Pi OS (formerly Raspbian)
- Python 2.7 or 3.x
- GPIO access for hardware control
- USB port for barcode scanner
- Network connectivity for cameras and database sync

### Supported Hardware
- **Gate Control**: GPIO relays or Serial communication
- **Barcode Scanner**: USB HID keyboard-emulation scanners
- **Cameras**: IP cameras with HTTP snapshot support (Hikvision, Dahua, etc.)
- **Audio**: USB audio devices or built-in audio jack

## Architecture

### Services

- **database_service.py** - CouchDB interface and transaction processing
- **gate_service.py** - Gate control with GPIO/Serial abstraction
- **barcode_scanner.py** - USB scanner input processing
- **camera_service.py** - CCTV image capture and processing
- **audio_service.py** - Sound feedback system
- **config.py** - Configuration management

### Web Application

- **main.py** - Flask web server and API endpoints
- **templates/index.html** - Main dashboard interface
- **templates/settings.html** - Configuration interface

## Database Schema

Compatible with the original PouchDB schema:

```json
{
  "_id": "transaction_id",
  "type": "parking_transaction",
  "barcode": "vehicle_barcode",
  "license_plate": "plate_number",
  "entry_time": "2024-01-01T10:00:00Z",
  "exit_time": "2024-01-01T12:00:00Z",
  "parking_fee": 5000,
  "status": "completed",
  "images": {
    "entry_plate": "base64_image",
    "entry_driver": "base64_image",
    "exit_plate": "base64_image",
    "exit_driver": "base64_image"
  }
}
```

## GPIO Configuration

Default GPIO pin assignments for Raspberry Pi:

- **Gate Control**: GPIO 24 (Main gate relay control)
- **Power LED**: GPIO 16 (System power indicator)
- **Busy LED**: GPIO 20 (Gate operation indicator)  
- **Live LED**: GPIO 21 (System alive indicator)

Configurable in `config.ini` under `[gpio]` section.

**GPIO Logic:**
- `open_gate()` → GPIO 24 = HIGH (Gate opens/relay activates)
- `close_gate()` → GPIO 24 = LOW (Gate closes/relay deactivates)

## Service Installation

For auto-start on boot:

```bash
# Enable the systemd service
sudo systemctl enable exit-gate

# Start the service
sudo systemctl start exit-gate

# Check status
sudo systemctl status exit-gate
```

## Troubleshooting

### Common Issues

1. **Permission Denied (GPIO)**
   ```bash
   sudo usermod -a -G gpio pi
   # Logout and login again
   ```

2. **Audio Not Working**
   ```bash
   sudo usermod -a -G audio pi
   # Check audio devices: aplay -l
   ```

3. **Scanner Not Detected**
   - Check USB connection: `lsusb`
   - Verify scanner is in HID keyboard mode
   - Test USB scanner: `./test_scanner.sh`
   - Check input devices: `ls /dev/input/`
   - **Debug barcode to gate flow**: `python test_barcode_flow.py`

4. **Barcode Scan Not Triggering Gate**
   ```bash
   # Test complete barcode to gate flow
   python test_barcode_flow.py
   
   # Test API scan endpoint
   curl -X POST http://localhost:5001/api/scan -H 'Content-Type: application/json' -d '{"barcode":"TEST123456"}'
   
   # Check if listeners are connected
   python -c "from usb_barcode_scanner import usb_barcode_scanner; print('Listeners:', len(usb_barcode_scanner.listeners))"
   ```

5. **Database Sync Issues**
   - Verify IP address and credentials
   - Test with: `curl http://camera-ip/ISAPI/Streaming/Channels/1/picture`

5. **Database Sync Issues**
   - Check CouchDB server accessibility
   - Verify credentials in config.ini
   - Check network connectivity

### Logs and Debugging

- Application logs: Check console output when running `python main.py`
- System service logs: `sudo journalctl -u exit-gate -f`
- Enable debug mode in `config.ini`: `debug = True`

## Development

### Project Structure

```
python-app/
├── main.py              # Flask web application
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── install.py          # Installation script
├── quick-setup.sh      # Quick setup for Raspberry Pi
├── services/           # Core services
│   ├── database.py
│   ├── gate_service.py
│   ├── barcode_scanner.py
│   ├── camera_service.py
│   └── audio_service.py
└── templates/          # Web interface templates
    ├── index.html
    └── settings.html
```

### Adding New Features

1. **New Service**: Create service class in `services/` folder
2. **API Endpoint**: Add route in `main.py`
3. **Configuration**: Add settings in `config.py`
4. **UI**: Update templates with new controls

### Testing

```bash
# Test individual components
python -c "from services.gate_service import GateService; GateService().test()"
python -c "from services.database import DatabaseService; DatabaseService().test_connection()"

# Test web interface
curl http://localhost:5000/api/status

# Test USB barcode scanner
./test_scanner.sh

# Test Python USB scanner directly
python test_usb_scanner.py
```

### USB Barcode Scanner Setup

1. **Connect USB Scanner**: Plug in your USB barcode scanner
2. **Verify Detection**: Run `lsusb` to see if device is detected
3. **Test Input**: Run `./test_scanner.sh` and scan a barcode
4. **Configure**: The scanner should work as HID keyboard input device
5. **Troubleshoot**: Check `/dev/input/` for input devices

**Scanner Requirements:**
- Must emulate HID keyboard input
- Should send rapid character sequences followed by Enter/Tab
- Compatible with USB HID standards

## License

This project is part of the Exit Gate System implementation for parking management.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files for error messages
3. Verify hardware connections and configuration
4. Test individual components using the web interface
