# Audio System untuk Exit Gate

## Deskripsi
Sistem audio untuk Exit Gate yang akan memutar suara saat gate terbuka, tertutup, dan event lainnya.

## File Audio
File audio harus ditempatkan di folder `sounds/` dengan nama berikut:

### File yang Diperlukan:
- `scan.wav` - Suara saat barcode di-scan
- `gate_open.wav` - Suara saat gate terbuka ⭐
- `gate_close.wav` - Suara saat gate tertutup
- `success.wav` - Suara saat berhasil
- `error.wav` - Suara saat error
- `welcome.wav` - Suara sambutan
- `entrance.wav` - Suara entrance
- `exit.wav` - Suara exit

### Format Audio:
- Format: WAV atau MP3
- Sample Rate: 22050 Hz atau 44100 Hz
- Bit Depth: 16-bit
- Channels: Mono atau Stereo
- Durasi: 0.5-1 detik (pendek)

## Dependencies
Pastikan pygame terinstall:
```bash
pip install pygame
```

Atau untuk Python 2.7:
```bash
pip2 install pygame
```

## Penggunaan di GUI

### Event Audio:
1. **Gate Open** - Suara utama saat gate terbuka
2. **Gate Close** - Suara saat gate tertutup otomatis
3. **Barcode Scan** - Suara saat barcode di-scan
4. **Success** - Suara saat transaksi berhasil
5. **Error** - Suara saat error atau akses ditolak

### Integrasi di GUI:
Audio akan otomatis dimainkan saat:
- Barcode berhasil di-scan
- Gate terbuka (manual atau otomatis)
- Gate tertutup (manual atau otomatis)
- Error terjadi (barcode invalid, gate gagal, dll)

## Testing
Jalankan test audio:
```bash
python test_audio.py
```

## Konfigurasi Volume
Volume dapat diatur melalui audio service:
- Default: 0.7 (70%)
- Range: 0.0 - 1.0
- Dapat diubah secara real-time

## Troubleshooting

### Audio Tidak Bersuara:
1. Pastikan pygame terinstall
2. Cek perangkat audio terhubung
3. Cek volume sistem tidak mute
4. Cek file audio ada di folder `sounds/`

### File Audio Tidak Ditemukan:
1. Letakkan file di folder `python-app/sounds/`
2. Gunakan nama file yang tepat (case-sensitive)
3. Pastikan format file supported (WAV/MP3)

### Performance:
- Audio dimainkan secara asynchronous
- Tidak memblok UI
- Multiple suara dapat dimainkan bersamaan
- Auto-cleanup saat aplikasi ditutup

## File Audio Default
Jika tidak ada file audio custom, sistem akan membuat suara beep sederhana menggunakan generated tones.

## Log Audio
Semua aktivitas audio akan dicatat di log GUI dan file log untuk debugging.
