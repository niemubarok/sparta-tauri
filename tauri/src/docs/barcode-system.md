# Sistem Barcode dan Tiket Parkir

## Overview

Sistem ini menambahkan fitur barcode dan tiket untuk tracking kendaraan parkir yang lebih baik. Setiap kendaraan yang masuk akan mendapatkan tiket dengan barcode yang unik, dan untuk keluar harus scan barcode tersebut.

## Fitur Baru

### 1. Cetak Tiket Saat Masuk (Entry Gate)

**Alur:**
1. Customer masuk → input plat nomor/pilih jenis kendaraan
2. Sistem proses transaksi masuk
3. **Dialog cetak tiket muncul** (fitur baru)
4. Tiket dicetak dengan informasi:
   - Barcode unik
   - Plat nomor
   - Jenis kendaraan
   - Waktu masuk
   - Status pembayaran (untuk prepaid)
   - Informasi operator

**Komponen Baru:**
- `TicketPrintDialog.vue` - Dialog untuk preview dan cetak tiket
- Fungsi `updateTransactionTicketInfo()` di transaksi store

### 2. Scan Barcode Saat Keluar (Exit Gate)

**Alur:**
1. Customer scan barcode tiket
2. Sistem validasi barcode dan cari transaksi di database
3. Tampilkan informasi kendaraan dan pembayaran
4. Konfirmasi keluar → buka gate

**Fitur di ManualExitPage.vue:**
- Input barcode scanner di bagian atas
- Fungsi `processBarcode()` untuk validasi
- Integrasi dengan ExitConfirmationDialog

**Komponen Baru:**
- `ExitConfirmationDialog.vue` - Dialog konfirmasi keluar dengan info pembayaran
- Fungsi `findTransactionByBarcode()` di transaksi store

## Struktur Barcode

Format barcode: `{GATE}{DATE}{TIME}{SEQUENCE}`

Contoh: `0120241225143012340001`
- `01` = Gate ID
- `20241225` = Tanggal (YYYYMMDD)
- `143012` = Waktu (HHMMSS)
- `0001` = Sequence number

## Database Changes

### Transaksi Table
- `no_barcode` - Menyimpan barcode unik
- `ticket_number` - Menyimpan nomor tiket (sama dengan barcode)

### PouchDB Views
- `by_barcode` - Index untuk cari transaksi berdasarkan barcode

## Komponen dan Fungsi Baru

### 1. TicketPrintDialog.vue
```vue
<TicketPrintDialog
  v-model="showDialog"
  :transaction="transactionData"
  @printed="onTicketPrinted"
  @cancelled="onCancelled"
/>
```

**Props:**
- `modelValue` - Control dialog visibility
- `transaction` - Data transaksi untuk tiket

**Events:**
- `printed` - Emitted when ticket printed successfully
- `cancelled` - Emitted when dialog cancelled

### 2. ExitConfirmationDialog.vue
```vue
<ExitConfirmationDialog
  v-model="showDialog"
  :transaction="transactionData"
  @confirmed="onExitConfirmed"
  @cancelled="onCancelled"
/>
```

**Props:**
- `modelValue` - Control dialog visibility
- `transaction` - Data transaksi yang akan keluar

**Events:**
- `confirmed` - Emitted when exit confirmed with payment data
- `cancelled` - Emitted when exit cancelled

### 3. Transaksi Store Functions

#### findTransactionByBarcode(barcode: string)
```typescript
const transaction = await transaksiStore.findTransactionByBarcode("0120241225143012340001");
```

#### updateTransactionTicketInfo(transactionData)
```typescript
await transaksiStore.updateTransactionTicketInfo({
  barcode: "0120241225143012340001",
  ticket_number: "0120241225143012340001"
});
```

### 4. Format Utils
File: `src/utils/format-utils.ts`

Utility functions untuk formatting:
- `formatCurrency()` - Format mata uang
- `formatDate()` - Format tanggal
- `formatTime()` - Format waktu
- `formatDateTime()` - Format tanggal dan waktu
- `formatDuration()` - Format durasi parkir

## Integration Points

### Manual Gate (Entry)
File: `src/pages/manual-gate.vue`

1. Import TicketPrintDialog
2. Tambah state untuk dialog
3. Modifikasi `processEntry()` untuk show dialog
4. Handler untuk ticket printed/cancelled

### Manual Exit Page
File: `src/pages/ManualExitPage.vue`

1. Tambah barcode scanner input
2. Fungsi `processBarcode()` untuk validasi
3. Integration dengan ExitConfirmationDialog
4. Flow untuk both prepaid dan regular transactions

## Keyboard Shortcuts

### Entry Gate
- F1 = Focus input plat nomor
- F9 = Toggle prepaid mode
- F8 = Manual gate open
- F12 = Emergency gate open

### Exit Gate  
- F8 = Manual gate open
- F12 = Emergency gate open

## Error Handling

### Barcode Validation
- Minimum 5 characters
- Case insensitive
- Auto uppercase conversion

### Transaction Not Found
- Clear error message
- Reset form state
- Allow retry

### Database Errors
- Graceful error handling
- User friendly messages
- Console logging for debugging

## Printing

### Browser Print API
- Uses window.open() with print-specific HTML
- Optimized for thermal printers (80mm width)
- Monospace font for better barcode readability

### Print Styles
- Thermal printer friendly
- 80mm paper width
- High contrast for barcodes
- Clear information hierarchy

## Testing

### Entry Flow
1. Test normal entry with ticket printing
2. Test prepaid mode with ticket
3. Test ticket printing cancellation
4. Verify database updates

### Exit Flow
1. Test barcode scanning
2. Test transaction validation
3. Test prepaid vs regular payment flows
4. Test error scenarios (invalid barcode, already exited)

## Future Enhancements

1. **Real Barcode Integration**
   - Integration dengan barcode scanner hardware
   - Support untuk berbagai format barcode

2. **Receipt Printing**
   - Print receipt setelah pembayaran
   - Email/SMS notification

3. **Mobile App Integration**
   - QR code untuk mobile scanning
   - Digital tickets

4. **Analytics**
   - Track scan success rate
   - Print failure monitoring
   - Usage statistics

## Troubleshooting

### Common Issues

1. **Barcode tidak terbaca**
   - Pastikan format barcode benar
   - Check database index untuk by_barcode view

2. **Transaksi tidak ditemukan**
   - Verify barcode format
   - Check transaction status (sudah keluar?)

3. **Print tidak berfungsi**
   - Check browser print permissions
   - Verify print CSS

4. **Database sync issues**
   - Check PouchDB design docs
   - Verify transaction structure

## Migration Guide

Untuk existing installations:

1. **Database Migration**
   ```javascript
   // Update existing transactions with empty barcode fields
   await db.query('transaksi/all').then(result => {
     result.rows.forEach(row => {
       if (!row.doc.no_barcode) {
         row.doc.no_barcode = null;
         row.doc.ticket_number = null;
         db.put(row.doc);
       }
     });
   });
   ```

2. **Design Document Update**
   - PouchDB akan otomatis update design docs
   - View `by_barcode` akan tersedia

3. **Component Updates**
   - Import komponen baru di pages
   - Update handlers untuk ticket printing
