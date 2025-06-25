# PaymentDialog - Bayar di Depan

## Deskripsi
PaymentDialog adalah komponen khusus untuk mode "bayar di depan" pada sistem parkir. Dialog ini ditampilkan setelah user memilih jenis kendaraan dan memungkinkan pembayaran sebelum gate terbuka.

## Fitur
- **UI yang bersih**: Menampilkan tarif parkir dengan jelas
- **Input pembayaran**: Field input untuk jumlah uang yang dibayar
- **Quick payment buttons**: Tombol cepat untuk nominal pembayaran umum
- **Kembalian otomatis**: Menghitung dan menampilkan kembalian jika overpay
- **Keyboard support**: Enter untuk bayar, Esc untuk batal
- **Validasi**: Tidak bisa bayar jika kurang dari tarif

## Alur Penggunaan
1. User memilih jenis kendaraan (A/C/D) di JenisKendaraanCard
2. PaymentDialog muncul otomatis
3. User memasukkan jumlah pembayaran atau pilih dari quick buttons
4. User tekan Enter atau klik tombol "Bayar"
5. Jika pembayaran valid, gate terbuka otomatis
6. State transaction direset setelah 3 detik

## Props/Data
- `biayaParkir`: Tarif dari tarifStore berdasarkan jenis kendaraan
- `jenisKendaraan`: Label jenis kendaraan yang dipilih
- `bayarAmount`: Jumlah uang yang dibayar user
- `kembalian`: Otomatis dihitung dari bayar - tarif

## Events
- `onOk`: Dipanggil ketika pembayaran berhasil
- `onCancel`: Dipanggil ketika user batal

## Integration
Dialog ini terintegrasi dengan:
- `JenisKendaraanCard`: Parent component yang memanggil dialog
- `transaksiStore`: Untuk data transaksi dan pembayaran
- `tarifStore`: Untuk mendapatkan tarif berdasarkan jenis kendaraan
- `componentStore`: Untuk kontrol gate dan state aplikasi
