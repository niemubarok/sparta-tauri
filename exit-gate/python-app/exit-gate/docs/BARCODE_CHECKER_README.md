# BARCODE CHECKER SYSTEM - PANDUAN PENGGUNAAN

## Overview
Sistem cek barcode untuk Exit Gate telah diimplementasikan dengan fitur pencarian yang komprehensif dan robust.

## Fitur Utama

### 1. Pencarian Barcode Multi-Strategi
Sistem menggunakan beberapa strategi untuk mencari transaksi berdasarkan barcode:

1. **Direct ID Lookup**: Mencari berdasarkan pola ID transaksi
   - `transaction_{barcode}`
   - `{barcode}` 
   - `parking_{barcode}`
   - `member_{barcode}`

2. **View-Based Search**: Menggunakan CouchDB views untuk pencarian cepat
   - `transactions/by_barcode`
   - `transactions/active_transactions`

3. **Manual Search**: Pencarian manual dalam dokumen aktif
   - Memeriksa field `no_barcode`, `barcode`, `ticket_number`, `card_number`

4. **Full Database Scan**: Sebagai fallback untuk database kecil (<1000 docs)

### 2. Exit Processing
- Validasi transaksi aktif
- Perhitungan tarif parkir berdasarkan durasi
- Pencegahan double exit
- Logging lengkap untuk audit trail

### 3. Debug dan Testing
- Mode debug untuk bypass validasi
- Test transaction generator
- Interactive testing tools
- Database connectivity checks

## Cara Penggunaan

### Menjalankan GUI
```bash
python gui_exit_gate.py
```

### Testing Database
```bash
python test_barcode_database.py
# atau
test_barcode.cmd
```

### Testing dari GUI
1. Klik tombol "DB TEST" untuk test database
2. Klik tombol "TEST SCAN" untuk test barcode scan
3. Toggle "DEBUG" untuk mode debugging

### Input Barcode Manual
1. Focus pada field "Barcode Input" (auto-focus aktif)
2. Ketik atau scan barcode
3. Tekan Enter atau biarkan auto-process (untuk barcode panjang)

## Struktur Database

### Parking Transaction
```json
{
  "_id": "transaction_ABC123",
  "type": "parking_transaction",
  "no_barcode": "ABC123",
  "no_pol": "B1234XYZ",
  "id_kendaraan": 1,
  "waktu_masuk": "2025-07-02T10:00:00",
  "status": 0,
  "bayar_keluar": 0
}
```

### Member Entry
```json
{
  "_id": "member_CARD001",
  "type": "member_entry", 
  "card_number": "CARD001",
  "plat_nomor": "B5678ABC",
  "id_member": "MEMBER001",
  "waktu_masuk": "2025-07-02T10:00:00",
  "status": 0
}
```

## API Response Format

### Successful Exit
```json
{
  "success": true,
  "message": "Vehicle exit processed successfully",
  "fee": 5000,
  "transaction": {...},
  "duration_hours": 2,
  "exit_time": "2025-07-02T12:00:00",
  "search_method": "barcode",
  "transaction_id": "transaction_ABC123"
}
```

### Failed Exit
```json
{
  "success": false,
  "message": "No active transaction found",
  "fee": 0,
  "error_code": "TRANSACTION_NOT_FOUND",
  "search_methods_tried": ["barcode", "plate"]
}
```

### Error Codes
- `DB_NOT_CONNECTED`: Database tidak terkoneksi
- `TRANSACTION_NOT_FOUND`: Transaksi tidak ditemukan
- `ALREADY_EXITED`: Kendaraan sudah keluar
- `UPDATE_FAILED`: Gagal update database
- `SYSTEM_ERROR`: Error sistem

## Debug Mode

### Aktivasi Debug Mode
- Dari GUI: Klik tombol "DEBUG: OFF" untuk mengaktifkan
- Dari code: Set `self.debug_mode = True`

### Perilaku Debug Mode
- Gate tetap terbuka meskipun transaksi tidak ditemukan
- Error handling lebih permisif
- Logging detail untuk troubleshooting
- Bypass beberapa validasi

## Testing Tools

### 1. test_barcode_database.py
Script komprehensif untuk testing:
- Database connection test
- Test data creation
- Barcode search testing
- Exit processing testing
- Duplicate exit prevention
- Interactive testing mode

### 2. GUI Testing
- Button "DB TEST": Test database functionality
- Button "TEST SCAN": Simulate barcode scan
- Interactive barcode input field

### 3. Manual Testing Commands
```python
# Create test transaction
db_service.create_test_transaction("TEST123", "B123TEST")

# Search barcode
transaction = db_service.find_transaction_by_barcode("TEST123")

# Process exit
result = db_service.process_vehicle_exit("TEST123", "OPERATOR", "GATE01")

# List active transactions
active = db_service.list_active_transactions()

# Cleanup test data
db_service.cleanup_test_transactions()
```

## Troubleshooting

### Database Connection Issues
1. Check CouchDB service running
2. Verify config.ini settings
3. Check network connectivity
4. Review database credentials

### Barcode Not Found
1. Check if transaction exists in database
2. Verify barcode format and encoding
3. Check transaction status (0 = active, 1 = exited)
4. Use debug mode for testing

### Exit Processing Fails
1. Check database connectivity
2. Verify transaction is active (status = 0)
3. Check for duplicate exit attempts
4. Review error codes in response

### Performance Issues
1. Monitor database size
2. Check view indexing
3. Consider cleanup of old transactions
4. Review full scan conditions

## Configuration

### Database Settings (config.ini)
```ini
[database]
local_db = transactions
remote_url = http://localhost:5984
username = admin
password = password
```

### Gate Settings
```ini
[gate]
control_mode = gpio
timeout = 5

[gpio]
gate_pin = 18
active_high = true
```

## Logging

### Log Levels
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Critical errors
- DEBUG: Detailed troubleshooting info

### Log Locations
- GUI Log: In-app log display
- File Log: `exit_gate_gui.log`
- Console Log: stdout

## Security Considerations

1. **Database Access**: Credentials stored in config file
2. **Transaction Integrity**: Prevent duplicate exits
3. **Audit Trail**: Complete logging of all operations
4. **Debug Mode**: Should be disabled in production

## Future Enhancements

1. **Image Integration**: Store exit photos with transactions
2. **Real-time Sync**: Remote database synchronization
3. **Advanced Search**: Fuzzy matching and similarity search
4. **Reporting**: Exit statistics and analytics
5. **Multi-gate Support**: Coordinate multiple exit gates

## Support

Untuk troubleshooting dan support:
1. Check log files untuk error details
2. Run test suite untuk isolate issues
3. Use debug mode untuk detailed diagnostics
4. Review database views dan indexes
