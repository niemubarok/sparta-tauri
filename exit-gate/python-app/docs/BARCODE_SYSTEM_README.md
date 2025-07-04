# BARCODE SYSTEM DOCUMENTATION

## Pattern Barcode

Sistem menggunakan pattern yang konsisten untuk identifikasi transaksi:

### ID Pattern
- **Transaction ID**: `transaction_{barcode}`
- **Barcode Field**: `{barcode}`

### Contoh
Jika barcode adalah `1234`:
- `_id` akan menjadi: `transaction_1234`
- `no_barcode` akan menjadi: `1234`

## Struktur Database

### Transaksi Parking
```json
{
  "_id": "transaction_1234",
  "type": "parking_transaction",
  "no_barcode": "1234",
  "no_pol": "B1234XYZ",
  "id_kendaraan": 1,
  "waktu_masuk": "2025-07-02T01:00:00Z",
  "status": 0,
  "status_transaksi": "0"
}
```

### Member Entry
```json
{
  "_id": "member_5678",
  "type": "member_entry", 
  "card_number": "5678",
  "plat_nomor": "B5678ABC",
  "id_member": "MEMBER_001",
  "waktu_masuk": "2025-07-02T01:00:00Z",
  "status": 0
}
```

## Strategi Pencarian Barcode

Database service menggunakan beberapa strategi untuk mencari transaksi:

### 1. Primary Strategy - Direct ID Lookup
```python
# Cari berdasarkan pattern utama
transaction_id = "transaction_{}".format(barcode)
doc = db[transaction_id]
```

### 2. Alternative ID Patterns
```python
alternative_ids = [
    barcode,  # Direct barcode as ID
    "parking_{}".format(barcode),
    "member_{}".format(barcode)
]
```

### 3. Active Transactions View
```python
# Cari di active transactions dengan ekstraksi barcode dari _id
for row in db.view('transactions/active_transactions'):
    doc_id = row.value.get('_id')
    if doc_id.startswith('transaction_'):
        extracted_barcode = doc_id.replace('transaction_', '')
        if extracted_barcode == barcode:
            return row.value
```

### 4. Full Database Scan (Fallback)
Hanya dijalankan jika database kecil (< 1000 dokumen)

## Status Transaksi

- **Status 0**: Transaksi aktif (belum keluar)
- **Status 1**: Transaksi selesai (sudah keluar)

## Proses Exit Vehicle

1. **Cari Transaksi**: Gunakan barcode untuk mencari transaksi aktif
2. **Validasi**: Pastikan status = 0 (belum keluar)
3. **Hitung Tarif**: Berdasarkan durasi parkir
4. **Update Status**: Ubah status menjadi 1 dan tambah data keluar

### Contoh Proses Exit
```python
result = db_service.process_vehicle_exit("1234", "OPERATOR_01", "EXIT_GATE_01")

# Result structure:
{
    'success': True,
    'message': 'Vehicle exit processed successfully',
    'fee': 5000,
    'transaction_id': 'transaction_1234',
    'duration_hours': 2,
    'search_method': 'barcode'
}
```

## Error Codes

- **DB_NOT_CONNECTED**: Database tidak terhubung
- **TRANSACTION_NOT_FOUND**: Transaksi tidak ditemukan
- **ALREADY_EXITED**: Kendaraan sudah keluar sebelumnya
- **UPDATE_FAILED**: Gagal update database
- **SYSTEM_ERROR**: Error sistem

## Testing

### Membuat Test Transaction
```python
# Buat transaksi test
db_service.create_test_transaction("1234", "TESTPLATE")

# Ini akan membuat:
# _id: "transaction_1234"
# no_barcode: "1234"
# no_pol: "TESTPLATE"
```

### Menjalankan Test
```bash
python test_barcode_logic.py
```

### Cleanup Test Data
```python
db_service.cleanup_test_transactions()
```

## GUI Integration

GUI akan menggunakan barcode yang diinput untuk:
1. Mencari transaksi aktif
2. Memproses exit kendaraan
3. Update display

### Contoh di GUI
```python
def process_vehicle_exit(self, barcode):
    result = self.db_service.process_vehicle_exit(barcode, "SYSTEM", "EXIT_GATE_01")
    
    if result.get('success'):
        # Buka gate
        self.gate_service.open_gate()
        # Update UI
        self.update_transaction_count()
    else:
        # Tampilkan error
        self.log("Error: {}".format(result.get('message')))
```

## Database Views

### Transactions by Barcode
```javascript
function(doc) {
    if (doc.type === 'parking_transaction' && doc.no_barcode) {
        emit(doc.no_barcode, doc);
    }
}
```

### Active Transactions
```javascript
function(doc) {
    if ((doc.type === 'parking_transaction' || doc.type === 'member_entry') && doc.status === 0) {
        emit(doc._id, doc);
    }
}
```

## Mock Database

Untuk testing tanpa CouchDB, sistem menggunakan mock database yang:
- Menyimpan data dalam memory
- Mengimplementasi interface yang sama
- Support view queries sederhana
- Cocok untuk development dan testing

## Troubleshooting

### Problem: Transaksi tidak ditemukan
- Periksa format barcode (harus exact match)
- Pastikan transaksi masih aktif (status = 0)
- Check log untuk melihat strategi pencarian mana yang dijalankan

### Problem: Database tidak terhubung
- Sistem akan fallback ke mock database
- Check koneksi CouchDB di config.ini
- Pastikan credentials benar

### Problem: Performance lambat
- Jika database besar, pastikan views sudah di-setup
- Hindari full scan dengan membatasi doc_count check
- Gunakan index yang tepat
