# Image Attachment Integration with Vue.js Dashboard

## Ringkasan Perubahan

Sistem exit gate Python telah diperbarui untuk menyimpan gambar sebagai attachment dalam database CouchDB agar kompatibel dengan tampilan `daftar-transaksi.vue`.

## Struktur Penyimpanan Gambar

### 1. Attachment Names
Gambar disimpan dengan nama standar yang sesuai dengan ekspektasi Vue.js dashboard:

- **Entry Image**: `entry.jpg` - Gambar kendaraan saat masuk
- **Exit Image**: `exit.jpg` - Gambar kendaraan saat keluar  
- **Additional Images**: 
  - `exit_driver.jpg` - Gambar driver saat keluar
  - `*_image.jpg` - Gambar lainnya dengan suffix `_image`

### 2. Database Document Structure
```json
{
  "_id": "transaction_1234",
  "type": "parking_transaction",
  "no_barcode": "1234",
  "no_pol": "B1234AB",
  "status": 0,
  "_attachments": {
    "entry.jpg": {
      "content_type": "image/jpeg",
      "length": 45678,
      "data": "base64_image_data..."
    },
    "exit.jpg": {
      "content_type": "image/jpeg", 
      "length": 56789,
      "data": "base64_image_data..."
    }
  }
}
```

## Kompatibilitas dengan Vue.js Dashboard

### 1. Image Detection Logic
Vue.js dashboard menggunakan fungsi `getImageList()` yang memprioritaskan:

1. **Attachment** (`_attachments['entry.jpg']`, `_attachments['exit.jpg']`)
2. **Direct Field** (`entry_pic`, `exit_pic`) - hanya jika tidak ada attachment

### 2. Image Loading
Dashboard menggunakan `loadAttachmentImage()` untuk memuat gambar:

```javascript
const loadAttachmentImage = async (transactionId, attachmentName) => {
  const blob = await getTransactionAttachment(transactionId, attachmentName)
  const url = URL.createObjectURL(blob)
  return url
}
```

### 3. Image Display Priority
Dashboard menampilkan gambar dengan prioritas:

1. Attachment (`entry.jpg`, `exit.jpg`) 
2. Field langsung jika tidak ada attachment
3. Mencegah duplikasi gambar yang sama

## Perubahan di Python Exit Gate

### 1. Database Service (`database_service.py`)

#### Metode Baru:
- `generate_sample_image_data(image_type)` - Generate sample image untuk testing
- `create_test_transaction(barcode, plate_number, entry_image_data)` - Dengan entry image
- `process_vehicle_exit(barcode, operator_id, gate_id, exit_image_data)` - Dengan exit image  
- `add_image_to_transaction(transaction_id, image_name, image_data)` - Menyimpan attachment

#### Perubahan:
- Test transaction otomatis menyimpan entry image sebagai `entry.jpg`
- Vehicle exit otomatis menyimpan exit image sebagai `exit.jpg`
- Support base64 image data dengan konversi otomatis

### 2. GUI Service (`gui_exit_gate.py`)

#### Metode Baru:
- `save_exit_images_to_transaction(barcode, capture_result)` - Menyimpan gambar ke DB
- Variable untuk menyimpan captured images:
  - `self.last_exit_image_data`
  - `self.last_plate_image_data` 
  - `self.last_driver_image_data`

#### Perubahan:
- `capture_exit_images_async()` menyimpan hasil capture
- `process_vehicle_exit()` menggunakan stored image data
- Test database menggunakan sample image data
- Auto-clear stored images setelah digunakan

## Flow Penyimpanan Gambar

### 1. Entry Process (Test Transaction)
```
1. User membuat test transaction
2. System generate sample entry image  
3. Transaction disimpan dengan entry.jpg attachment
4. Vue.js dashboard dapat menampilkan entry image
```

### 2. Exit Process  
```
1. Barcode di-scan
2. Camera service capture exit images
3. Images disimpan sebagai instance variables
4. Database exit processing menggunakan stored images
5. Exit image disimpan sebagai exit.jpg attachment  
6. Stored images di-clear
7. Vue.js dashboard dapat menampilkan exit image
```

## Testing

### 1. Test Database Function
Klik tombol **"DB TEST"** di GUI untuk menguji:
- Pembuatan test transaction dengan entry image
- Exit processing dengan exit image  
- Verifikasi attachment tersimpan

### 2. Test Image Display
Di Vue.js dashboard (`daftar-transaksi.vue`):
- Lihat kolom "Gambar" untuk jumlah gambar
- Klik detail transaksi untuk melihat gambar
- Verifikasi entry dan exit image terpisah

## Keuntungan

1. **Konsistensi**: Struktur data sama antara Python dan Vue.js
2. **Skalabilitas**: Support multiple images per transaction
3. **Performance**: Lazy loading images di dashboard
4. **Audit Trail**: Gambar tersimpan permanen di database
5. **Duplikasi Prevention**: Mencegah tampilan gambar yang sama

## Debug dan Troubleshooting

### 1. Check Database Content
```python
# Di Python console atau test
transaction = db_service.find_transaction_by_barcode("TEST123")
if transaction:
    print("Attachments:", transaction.get('_attachments', {}))
```

### 2. Check Vue.js Console
```javascript
// Di browser console
console.log('Image list:', getImageList(selectedTransaction))
```

### 3. Verifikasi Compatibility
- Pastikan attachment names konsisten (`entry.jpg`, `exit.jpg`)
- Verifikasi content_type = `image/jpeg`
- Check base64 data format valid

## Migration Notes

Jika ada data existing dengan structure lama:
1. Field `entry_pic`/`exit_pic` masih didukung sebagai fallback
2. Prioritas attachment lebih tinggi dari field langsung
3. Function `fixAttachmentDuplicates()` tersedia di Vue.js untuk cleanup
