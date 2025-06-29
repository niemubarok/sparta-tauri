#!/bin/bash
# Deploy Exit Gate dengan Barcode Scanner Integration

echo "🚀 DEPLOYING EXIT GATE WITH BARCODE SCANNER"
echo "=========================================="

# Copy updated files to Raspberry Pi
echo "📂 Copying updated files..."

scp simple_server.py pi@192.168.1.100:/home/pi/exit-gate/python-app/
scp exit-gate.service pi@192.168.1.100:/home/pi/exit-gate/python-app/
scp test_usb_barcode_scanner.py pi@192.168.1.100:/home/pi/exit-gate/python-app/
scp demo_parking_scanner.py pi@192.168.1.100:/home/pi/exit-gate/python-app/
scp create_test_parking_data.py pi@192.168.1.100:/home/pi/exit-gate/python-app/

echo "📦 Installing service file..."

# Copy service file to systemd
ssh pi@192.168.1.100 "
sudo cp /home/pi/exit-gate/python-app/exit-gate.service /etc/systemd/system/
sudo systemctl daemon-reload
"

echo "🔧 Checking which version to run..."

# Ask user which version to use
echo ""
echo "Select Exit Gate version to run:"
echo "1) simple_server.py (Simple, with barcode integration)"
echo "2) main.py (Full featured, all services)"
echo ""
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo "📝 Using simple_server.py..."
    
    # Update service to use simple_server.py
    ssh pi@192.168.1.100 "
    sudo sed -i 's|main.py|simple_server.py|g' /etc/systemd/system/exit-gate.service
    sudo systemctl daemon-reload
    "
    
elif [ "$choice" = "2" ]; then
    echo "📝 Using main.py..."
    
    # Update service to use main.py  
    ssh pi@192.168.1.100 "
    sudo sed -i 's|simple_server.py|main.py|g' /etc/systemd/system/exit-gate.service
    sudo systemctl daemon-reload
    "
    
else
    echo "❌ Invalid choice. Keeping current configuration."
fi

echo "🔄 Restarting service..."

ssh pi@192.168.1.100 "
sudo systemctl restart exit-gate.service
sudo systemctl enable exit-gate.service
"

echo "✅ Deployment completed!"

echo ""
echo "🔍 Checking service status..."
ssh pi@192.168.1.100 "sudo systemctl status exit-gate.service --no-pager"

echo ""
echo "📋 Next steps:"
echo "1. Test web interface: http://192.168.1.100:5001"
echo "2. Test USB barcode scanner: ssh pi@192.168.1.100 'cd exit-gate/python-app && python test_usb_barcode_scanner.py'"
echo "3. Create test data: ssh pi@192.168.1.100 'cd exit-gate/python-app && python create_test_parking_data.py'"
echo "4. Check logs: ssh pi@192.168.1.100 'sudo journalctl -u exit-gate.service -f'"
