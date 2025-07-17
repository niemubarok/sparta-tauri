#!/bin/bash
echo "=== USB Barcode Scanner Troubleshooting ==="
echo "1. USB Devices:"
lsusb | grep -i "HID\|keyboard\|scanner" || echo "   No HID devices found"
echo
echo "2. Input Devices:"
ls -la /dev/input/
echo
echo "3. Test simple input - Type and press Enter:"
echo "   (Use your barcode scanner now)"
read -p "Scan barcode: " barcode
echo "Received: $barcode"
echo
echo "4. Sending to Exit Gate API..."
curl -X POST -H "Content-Type: application/json" -d "{\"barcode\":\"$barcode\"}" http://localhost:5001/api/scan
echo
echo "Done!"
