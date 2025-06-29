@echo off
echo === Copying Fixed Barcode Scanner Files to Raspberry Pi ===

echo Copying main.py...
scp main.py pi@192.168.10.51:/home/pi/exit-gate/python-app/

echo Copying usb_barcode_scanner.py...
scp usb_barcode_scanner.py pi@192.168.10.51:/home/pi/exit-gate/python-app/

echo Copying test files...
scp test_barcode_flow.py pi@192.168.10.51:/home/pi/exit-gate/python-app/
scp test_gpio_debug.py pi@192.168.10.51:/home/pi/exit-gate/python-app/
scp test_physical_scanner.py pi@192.168.10.51:/home/pi/exit-gate/python-app/
scp simple_test.py pi@192.168.10.51:/home/pi/exit-gate/python-app/

echo Copying GUI application...
scp gui_exit_gate.py pi@192.168.10.51:/home/pi/exit-gate/python-app/
scp start_gui.sh pi@192.168.10.51:/home/pi/exit-gate/python-app/
scp exit-gate-gui.service pi@192.168.10.51:/home/pi/exit-gate/python-app/

echo Copying fixed gate_service.py...
scp gate_service.py pi@192.168.10.51:/home/pi/exit-gate/python-app/

echo === Testing Connection ===
ssh pi@192.168.10.51 "cd python-app && python test_barcode_flow.py"

echo === Manual Commands ===
echo 1. Test barcode flow: ssh pi@192.168.10.51 "cd /home/pi/exit-gate/python-app && python test_barcode_flow.py"
echo 2. Test PHYSICAL scanner: ssh pi@192.168.10.51 "cd /home/pi/exit-gate/python-app && python test_physical_scanner.py"
echo 3. Test API scan: curl -X POST http://192.168.10.51:5001/api/scan -H "Content-Type: application/json" -d "{\"barcode\":\"TEST123456\"}"
echo 4. Simple test: ssh pi@192.168.10.51 "cd /home/pi/exit-gate/python-app && python simple_test.py"
echo 5. Start GUI: ssh pi@192.168.10.51 "cd /home/pi/exit-gate/python-app && python gui_exit_gate.py"
echo 6. Install GUI service: ssh pi@192.168.10.51 "cd /home/pi/exit-gate/python-app && sudo cp exit-gate-gui.service /etc/systemd/system/ && sudo systemctl enable exit-gate-gui && sudo systemctl start exit-gate-gui"
echo 7. Check logs: ssh pi@192.168.10.51 "cd /home/pi/exit-gate/python-app && tail -f *.log"

pause
