# Mode Bayar di Depan (Prepaid Mode)

## Deskripsi
Mode "Bayar di Depan" memungkinkan pembayaran parkir dilakukan sebelum kendaraan masuk, langsung setelah memilih jenis kendaraan.

## Cara Mengaktifkan Mode Bayar di Depan

### 1. Via Button UI
- Klik tombol **"Mode Bayar Depan"** di halaman manual-gate
- Button akan berubah warna menjadi primary (biru) ketika aktif
- Button akan menampilkan **"Mode Bayar Belakang"** ketika mode prepaid aktif

### 2. Via Keyboard Shortcut
- Tekan **F9** untuk toggle antara mode bayar depan/belakang
- Shortcut berfungsi di halaman manual-gate

## Workflow Mode Bayar di Depan

### Sebelum Aktivasi:
1. User input plat nomor
2. Pilih jenis kendaraan
3. Kendaraan masuk
4. Nanti saat keluar baru bayar

### Setelah Aktivasi Mode Bayar di Depan:
1. **Tidak perlu input plat nomor** - sistem auto generate
2. **Pilih jenis kendaraan** (A/C/D keyboard shortcuts atau click)
3. **PaymentDialog muncul otomatis** dengan tarif sesuai jenis kendaraan
4. **Bayar sekarang** - input jumlah bayar atau pilih quick amounts
5. **Gate terbuka otomatis** setelah payment berhasil

## Komponen yang Terlibat

### 1. **manual-gate.vue**
- Menampilkan JenisKendaraanCard saat prepaid mode dan belum check-in
- Menampilkan PaymentCard saat mode normal dan sudah check-in
- Toggle button dan keyboard shortcut F9

### 2. **JenisKendaraanCard.vue**
- Pilihan jenis kendaraan dengan shortcuts A/C/D
- Langsung buka PaymentDialog setelah pilih
- Handle payment completion dan gate opening

### 3. **PaymentDialog.vue**
- Dialog khusus untuk pembayaran prepaid
- Input amount dengan quick payment buttons
- Validasi pembayaran dan kalkulasi kembalian
- Keyboard support (Enter/Esc)

## State Management

### Local Storage:
- `prepaidMode`: Boolean untuk menyimpan status mode

### TransaksiStore:
- `biayaParkir`: Tarif dari tarifStore
- `bayar`: Jumlah yang dibayar
- `selectedJenisKendaraan`: Data kendaraan yang dipilih
- `platNomor`: Auto-generated untuk prepaid

### ComponentStore:
- `hideInputPlatNomor`: Hide input saat prepaid mode
- Gate control functions

## Notifications
- Mode switched: Info notification saat ganti mode
- Payment success: Success notification dengan info kembalian
- Payment cancelled: Info notification saat batal

## Reset Behavior
- Ganti mode → Reset transaction state
- Payment success → Auto reset setelah 3 detik
- Payment cancelled → Immediate reset

Mode ini memberikan experience yang lebih smooth untuk parkir bayar di depan dengan UI yang sederhana dan keyboard shortcuts yang efisien.
