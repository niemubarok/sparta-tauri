# Update Struktur Transaksi - Summary

## ✅ **Struktur Transaksi Baru Sesuai Format yang Diminta:**

### **Field-field Utama:**
```json
{
  "_id": "transaction_1751704905117106",
  "id": "1751704905117106",
  "no_pol": "B12345",
  "id_kendaraan": 2,
  "status": 1,
  "id_pintu_masuk": "01",
  "waktu_masuk": "2025-07-05T08:41:45.117Z",
  "id_op_masuk": "SYSTEM",
  "id_shift_masuk": "S1",
  "kategori": "UMUM",
  "status_transaksi": "1",
  "jenis_system": "PREPAID",
  "tanggal": "2025-07-05",
  "sinkron": 0,
  "upload": 0,
  "manual": 0,
  "veri_check": 0,
  "bayar_masuk": 2000,
  "type": "parking_transaction"
}
```

### **Field Exit (untuk transaksi keluar):**
```json
{
  "waktu_keluar": "2025-07-05T15:43:19.717667",
  "bayar_keluar": 0,
  "id_pintu_keluar": "EXIT_GATE_01",
  "id_op_keluar": "SYSTEM",
  "id_shift_keluar": "SHIFT_001",
  "exit_method": "barcode",
  "exit_input": "1751704905117106",
  "updated_at": "2025-07-05T15:43:19.728789"
}
```

### **Attachments:**
```json
{
  "_attachments": {
    "exit.jpg": {
      "content_type": "image/jpeg",
      "revpos": 4,
      "digest": "md5-KwCSXiNA8O3FF2YZXbiyGg==",
      "length": 45839,
      "stub": true
    },
    "entry.jpg": {
      "content_type": "image/jpeg",
      "revpos": 4,
      "digest": "md5-hUwmP6WWmiYRzJXq1yXxZw==",
      "length": 46368,
      "stub": true
    }
  }
}
```

## 🔧 **Files yang Diupdate:**

### **1. shared/database.py**
- ✅ `save_transaction()` - Struktur sesuai format baru
- ✅ `update_transaction_exit()` - Update transaksi dengan data exit
- ✅ `_get_vehicle_type_id()` - Mapping jenis kendaraan ke ID
- ✅ Support image attachments: entry.jpg & exit.jpg

### **2. entry-gate/entry_gate_gui.py** 
- ✅ Update transaction data structure
- ✅ Image capture untuk entry.jpg attachment
- ✅ Mapping ke format database yang baru

### **3. Test Scripts**
- ✅ `test_transaction_structure.py` - Test script untuk verify structure
- ✅ `test_transaction.bat` - Batch file untuk testing

## 📊 **Mapping Data:**

### **Vehicle Type IDs:**
- Motorcycle: 1
- Car: 2  
- Truck: 3
- Bus: 4

### **Status Codes:**
- Active Transaction: "1"
- Completed Transaction: "2"

### **Categories:**
- Member: "MEMBER"
- Non-Member: "UMUM"

## 🚀 **Usage:**

### **Entry Transaction:**
```python
entry_data = {
    "license_plate": "B1234XYZ",
    "vehicle_type": "Car", 
    "is_member": False,
    "transaction_type": "entry",
    "entry_fee": 2000
}
doc_id = db.save_transaction(entry_data, entry_image=image_bytes)
```

### **Exit Transaction:**
```python
exit_data = {
    "exit_fee": 5000,
    "exit_method": "alpr", 
    "exit_input": "B1234XYZ"
}
db.update_transaction_exit(transaction_id, exit_data, exit_image=image_bytes)
```

## ✅ **Ready for Testing:**
Run: `test_transaction.bat` untuk verify struktur baru


gk usah buat buat file untuk test mulu
trus pake terminal yang kebuka jangan buka terminal baru mulu