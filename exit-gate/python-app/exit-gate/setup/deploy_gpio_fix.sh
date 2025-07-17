#!/bin/bash
# Automatic GPIO Fix Deployment Script
# Copy this script dan files ke Raspberry Pi dan jalankan

echo "=== Exit Gate GPIO Fix Deployment ==="
echo "Deploying fixed files..."

# Stop application if running
echo "Stopping application..."
pkill -f "python main.py" 2>/dev/null || true

# Update config.ini untuk pin 24
echo "Updating config.ini..."
if [ -f config.ini ]; then
    sed -i 's/gate_pin = 18/gate_pin = 24/g' config.ini
    sed -i 's/power_pin = 24/power_pin = 16/g' config.ini
    sed -i 's/busy_pin = 23/busy_pin = 20/g' config.ini
    sed -i 's/live_pin = 25/live_pin = 21/g' config.ini
    echo "Config updated to use GPIO pin 24 for gate control"
else
    echo "Creating new config.ini..."
    python -c "from config import Config; Config().save_config()"
fi

# Make test script executable
chmod +x test_gpio_debug.py

echo "Testing GPIO directly..."
python test_gpio_debug.py

echo "=== Manual Test Commands ==="
echo "1. Test GPIO manually:"
echo "   python -c \"from gate_service import gate_service; print('Open:', gate_service.open_gate()); import time; time.sleep(3); print('Close:', gate_service.close_gate())\""
echo ""
echo "2. Test barcode scan:"
echo "   curl -X POST http://localhost:5001/api/scan -H 'Content-Type: application/json' -d '{\"barcode\":\"TEST123456\"}'"
echo ""
echo "3. Test web interface:"
echo "   curl http://localhost:5001/api/gate/open"
echo "   curl http://localhost:5001/api/gate/close"
echo ""
echo "4. Start application:"
echo "   python main.py"

echo "=== GPIO Pin Mapping (Fixed) ==="
echo "Gate Control: GPIO 24 (Physical pin 18)"
echo "Power LED:    GPIO 16 (Physical pin 36)"  
echo "Busy LED:     GPIO 20 (Physical pin 38)"
echo "Live LED:     GPIO 21 (Physical pin 40)"
echo ""
echo "Logic:"
echo "- open_gate()  → GPIO 24 = HIGH (relay ON)"
echo "- close_gate() → GPIO 24 = LOW  (relay OFF)"
