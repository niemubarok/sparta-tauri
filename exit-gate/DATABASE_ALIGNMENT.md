# Exit Gate Database Alignment

## Perubahan yang Dilakukan

### 1. **Database Connection & Structure**

#### Sebelum:
- Database name: `'exit_gate_db'`
- Remote sync: `transactions`, `kendaraan`, `tarif`

#### Sesudah:
- Database name: `'transactions'` (sama dengan entry gate)
- Remote sync: `transactions`, `kendaraan`, `tarif`, `petugas`
- Menambahkan sync untuk database `petugas` agar konsisten dengan entry gate

### 2. **Transaction Interface Enhancement**

#### Penambahan Fields:
```typescript
export interface ParkingTransaction {
  // ...existing fields
  no_barcode?: string    // Support barcode field for exit processing
  entry_pic?: string     // Simplified image field for entry
  exit_pic?: string      // Simplified image field for exit
}
```

### 3. **Transaction Search Methods**

#### Method Baru:
- `findTransactionByPlate(plateNumber: string)` - Cari transaksi berdasarkan nomor plat
- `findTransactionByBarcode(barcode: string)` - Enhanced untuk support `no_barcode` field
- `calculateParkingFee(transaction, exitTime)` - Kalkulasi biaya parkir otomatis
- `processVehicleExit(plateOrBarcode, operatorId, gateId)` - Method komprehensif untuk proses exit

### 4. **Enhanced Exit Processing**

#### Fitur Baru:
- Automatic fee calculation berdasarkan durasi parkir
- Support untuk pencarian transaksi by plate number atau barcode
- Integration dengan camera service untuk capture exit image
- Proper error handling dan response messages

### 5. **Database Sync Alignment**

#### Sekarang Sync dengan:
- **transactions** - Data transaksi parkir
- **kendaraan** - Master data jenis kendaraan
- **tarif** - Master data tarif parkir  
- **petugas** - Master data petugas/operator (baru)

### 6. **Exit Gate UI Updates**

#### Perubahan di `exit-gate.vue`:
- Menggunakan `processVehicleExit()` method yang baru
- Automatic fee calculation dan display
- Enhanced error handling
- Camera integration untuk capture exit image
- Better user feedback dengan fee amount display

## Cara Menggunakan

### 1. **Process Exit by Barcode**
```typescript
const result = await databaseService.processVehicleExit(
  'BARCODE123',     // Barcode dari tiket
  'OPERATOR_ID',    // ID operator
  'EXIT_GATE_01'    // ID gate
)
```

### 2. **Process Exit by Plate Number**
```typescript
const result = await databaseService.processVehicleExit(
  'B1234ABC',       // Nomor plat kendaraan
  'SYSTEM',         // ID operator
  'EXIT_GATE_01'    // ID gate
)
```

### 3. **Manual Fee Calculation**
```typescript
const fee = await databaseService.calculateParkingFee(
  transaction,      // Transaction object
  exitTime         // Optional exit time (default: now)
)
```

## Database Schema Compatibility

Exit gate sekarang fully compatible dengan entry gate database schema:

### Transaction Document Structure:
```javascript
{
  _id: "transaction_1234567890",
  type: "parking_transaction",
  id: "TXN001",
  no_pol: "B1234ABC",
  id_kendaraan: 1,
  status: 0,  // 0 = masuk, 1 = keluar
  waktu_masuk: "2024-12-28T10:00:00Z",
  waktu_keluar: "2024-12-28T12:30:00Z",
  bayar_masuk: 0,
  bayar_keluar: 15000,
  entry_pic: "data:image/jpeg;base64,/9j/4AAQ...",
  exit_pic: "data:image/jpeg;base64,/9j/4AAQ...",
  // ... other fields
}
```

## Sync Configuration

Pastikan remote CouchDB memiliki database berikut:
- `transactions` - Untuk data transaksi
- `kendaraan` - Untuk master jenis kendaraan  
- `tarif` - Untuk master tarif
- `petugas` - Untuk master data operator

## Benefits

1. **Konsistensi Data** - Exit gate menggunakan database structure yang sama dengan entry gate
2. **Enhanced Search** - Bisa cari transaksi by barcode atau plate number
3. **Automatic Calculation** - Fee dihitung otomatis berdasarkan durasi
4. **Better Integration** - Full sync dengan semua database yang diperlukan
5. **Image Support** - Capture dan simpan gambar exit
6. **Error Handling** - Better error messages dan handling

## Testing

Untuk test exit gate functionality:

1. Pastikan ada transaksi entry yang status = 0 (belum exit)
2. Scan barcode atau input plate number
3. Sistem akan otomatis calculate fee dan process exit
4. Transaksi akan update status = 1 dengan waktu keluar dan fee

## Migration Notes

Jika ada data existing di `exit_gate_db`, perlu migration ke database `transactions` agar konsisten dengan entry gate.
