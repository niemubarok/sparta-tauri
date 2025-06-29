# Exit Gate Barcode Scanner Integration - Troubleshooting

## Problem: Web bisa trigger GPIO tapi barcode tidak

### Root Cause:
- Service menjalankan `simple_server.py` yang tidak memiliki barcode scanner otomatis
- Barcode scanner service terpisah di `barcode_scanner.py` dan `main.py`

### Solutions Applied:

#### ✅ Solution 1: Updated simple_server.py dengan barcode integration
- Tambah import `barcode_scanner` module
- Tambah listener untuk handle barcode scan otomatis
- Integrate dengan existing GPIO dan database flow

#### ✅ Solution 2: Service configuration options
- Option 1: `simple_server.py` (lightweight dengan barcode)
- Option 2: `main.py` (full featured dengan semua services)

## Deployment Steps:

### 1. Copy Updated Files:
```bash
scp simple_server.py pi@192.168.1.100:/home/pi/exit-gate/python-app/
scp exit-gate.service pi@192.168.1.100:/home/pi/exit-gate/python-app/
```

### 2. Update Service:
```bash
ssh pi@192.168.1.100
sudo cp /home/pi/exit-gate/python-app/exit-gate.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart exit-gate.service
```

### 3. Test Barcode Scanner:
```bash
ssh pi@192.168.1.100
cd /home/pi/exit-gate/python-app
python test_usb_barcode_scanner.py
```

## Verification:

### Check Service Status:
```bash
sudo systemctl status exit-gate.service
sudo journalctl -u exit-gate.service -f
```

### Test Flow:
1. **Manual Web Test**: http://192.168.1.100:5001 → Manual scan → Should work ✅
2. **USB Scanner Test**: Physical barcode scan → Should trigger GPIO automatically ✅
3. **Database Test**: Create test parking data → Test with real plate numbers ✅

### Expected Log Output:
```
✅ Barcode scanner module loaded
✅ Barcode scanner listener added - automatic scanning enabled
🔍 AUTOMATIC BARCODE SCAN: B1234XYZ
📋 Parking transaction found: status=MASUK
🚪 Gate opened for vehicle: B1234XYZ
✅ Transaction updated to 'KELUAR' status
```

## File Structure After Update:

```
python-app/
├── simple_server.py          # ✅ Updated with barcode integration
├── main.py                   # ✅ Full featured alternative
├── barcode_scanner.py        # ✅ Barcode scanner service
├── exit-gate.service         # ✅ Updated service config
├── test_usb_barcode_scanner.py  # ✅ Hardware test script
└── create_test_parking_data.py  # ✅ Test data creator
```

## Troubleshooting:

### If barcode still not working:
1. Check USB scanner connection: `lsusb`
2. Test scanner hardware: `python test_usb_barcode_scanner.py`
3. Check service logs: `sudo journalctl -u exit-gate.service -f`
4. Verify barcode_scanner.py module is importable

### If "Module not found" error:
```bash
cd /home/pi/exit-gate/python-app
python -c "from barcode_scanner import barcode_scanner; print('OK')"
```

### If config.py missing:
```bash
# Create minimal config.py
echo "class Config: pass" > config.py
echo "config = Config()" >> config.py
```
