@echo off
echo === Parking System Setup for Windows ===

echo Installing Python packages...
pip install -r requirements.txt

echo Creating directories...
if not exist "logs" mkdir logs
if not exist "sounds" mkdir sounds

echo Setting up configuration...
if not exist "config.ini" (
    copy config.ini config.ini.backup
    echo Please edit config.ini with your settings
)

echo.
echo === Setup Complete ===
echo.
echo Next steps:
echo 1. Edit config.ini with your CCTV and database settings
echo 2. Add audio files to sounds/ directory
echo 3. Install and start CouchDB
echo 4. Run components:
echo    - Server: python server/websocket_server.py
echo    - Entry Gate: python entry-gate/entry_gate.py
echo    - Exit Gate: python exit-gate/exit_gate_gui.py
echo    - Admin: python admin/app.py
echo.
echo Admin interface will be available at: http://localhost:5000
echo.
pause
