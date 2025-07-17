@echo off
echo Testing Printer Service...
cd /d "%~dp0"

echo.
echo === Testing Entry Gate Printer ===
python -c "
import sys
sys.path.append('shared')
from printer import PrinterService
from config import Config

config = Config()
printer = PrinterService(config)

# Test printer connection
print('Testing printer connection...')
if printer.test_printer():
    print('✅ Printer test successful')
else:
    print('❌ Printer test failed')

# Test ticket printing
print('\nTesting ticket printing...')
ticket_data = {
    'id': '1234567890',
    'waktu_masuk': '2025-07-13T10:30:00Z',
    'no_pol': 'B1234XYZ',
    'id_kendaraan': 2,
    'id_pintu_masuk': 'ENTRY_GATE_01',
    'bayar_masuk': 2000,
    'kategori': 'UMUM'
}

if printer.print_ticket(ticket_data):
    print('✅ Ticket printing successful')
else:
    print('❌ Ticket printing failed')

# Test receipt printing
print('\nTesting receipt printing...')
receipt_data = {
    'id': '1234567890',
    'waktu_masuk': '2025-07-13T10:30:00Z',
    'waktu_keluar': '2025-07-13T12:45:00Z',
    'no_pol': 'B1234XYZ',
    'id_kendaraan': 2,
    'bayar_masuk': 2000,
    'bayar_keluar': 5000,
    'exit_method': 'alpr'
}

if printer.print_exit_receipt(receipt_data):
    print('✅ Receipt printing successful')
else:
    print('❌ Receipt printing failed')

print('\n=== Printer Test Complete ===')
"

echo.
echo Test completed. Check printer output.
pause
