# Exit Gate System - Organized Structure

## Folder Structure

```
python-app/
├── app/                    # Core application files
│   ├── main.py            # Flask web application
│   ├── gui_exit_gate.py   # Tkinter GUI application  
│   ├── exit_gate_gui.py   # Alternative GUI
│   ├── database_service.py # Database service
│   ├── camera_service.py  # Camera service
│   ├── audio_service.py   # Audio service
│   ├── gate_service.py    # Gate control service
│   ├── barcode_scanner.py # Barcode scanner service
│   ├── config.py          # Configuration handler
│   ├── config.ini         # Configuration file
│   ├── requirements.txt   # Python dependencies
│   ├── sounds/            # Audio files
│   └── templates/         # HTML templates
│
├── tests/                  # Test files and utilities
│   ├── test_*.py          # Unit tests
│   ├── final_comprehensive_test.py
│   ├── check_completed_transactions.py
│   ├── verify_images.py
│   ├── mock_camera_server.py
│   └── console applications
│
├── setup/                  # Installation and setup scripts
│   ├── install.py         # Python installer
│   ├── install.sh         # Shell installer
│   ├── setup_autostart.sh # Autostart setup
│   ├── start_gui.sh       # GUI starter script
│   └── service files
│
├── docs/                   # Documentation
│   ├── README.md          # Main documentation
│   ├── CAMERA_CONFIG.md   # Camera setup
│   ├── BARCODE_SYSTEM_README.md
│   └── other documentation
│
├── run_gui.py             # Launch GUI application
├── run_web.py             # Launch web application
└── README_STRUCTURE.md    # This file
```

## How to Run

### GUI Application
```bash
python run_gui.py
```

### Web Application  
```bash
python run_web.py
```

### Running from App Directory
You can also run directly from the app directory:
```bash
cd app
python gui_exit_gate.py    # GUI version
python main.py             # Web version
```

## Development

### Running Tests
```bash
cd tests
python test_barcode_search.py
python final_comprehensive_test.py
```

### Installation
```bash
cd setup
python install.py
```

## Notes

- All core application files are now in the `app/` folder
- Test files are separated in the `tests/` folder  
- Setup and installation scripts are in the `setup/` folder
- Documentation is organized in the `docs/` folder
- The launcher scripts (`run_gui.py`, `run_web.py`) handle path setup automatically
