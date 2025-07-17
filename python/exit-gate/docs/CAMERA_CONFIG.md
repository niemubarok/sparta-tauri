# Dokumentasi Konfigurasi Kamera Exit Gate

## Konfigurasi Kamera (config.ini)

```ini
[camera]
enabled = True

# Exit Camera (Kamera Keluar) - Kamera utama
exit_camera_ip = 192.168.10.70
exit_camera_username = admin
exit_camera_password = admin
exit_camera_brand = custom
exit_camera_path = Snapshot/1/RemoteImageCapture?ImageFormat=2
capture_timeout = 10

# Driver Camera (Optional - disabled by default)
driver_camera_enabled = False
driver_camera_ip = 192.168.1.101
driver_camera_username = admin
driver_camera_password = admin123
driver_camera_brand = auto
```

## URL Kamera yang Digunakan

Berdasarkan konfigurasi di atas, URL yang digunakan adalah:
```
http://admin:admin@192.168.10.70/Snapshot/1/RemoteImageCapture?ImageFormat=2
```

## Fitur Kamera di GUI

### 1. Tombol Kontrol Kamera
- **Capture Exit**: Mengambil foto dari kamera keluar
- **Capture Driver**: Mengambil foto dari kamera driver (jika diaktifkan)
- **Capture All**: Mengambil foto dari semua kamera
- **Test Cameras**: Test konektivitas kamera

### 2. Auto-Capture
- Kamera otomatis mengambil foto saat barcode di-scan
- Preview langsung ditampilkan di GUI
- Image disimpan dalam format base64

### 3. Preview Kamera
- Menampilkan hasil capture terakhir
- Update otomatis saat capture baru
- Mendukung resize otomatis untuk preview

## Testing Kamera

### 1. Test via Script
```bash
python test_camera_gui.py
```

### 2. Test Manual dengan curl
```bash
curl -u admin:admin "http://192.168.10.70/Snapshot/1/RemoteImageCapture?ImageFormat=2" -o test.jpg
```

### 3. Test via GUI
1. Jalankan GUI: `python gui_exit_gate.py`
2. Klik tombol "Test Cameras"
3. Klik tombol "Capture Exit"
4. Lihat preview di GUI

## Status Kamera

Kamera akan menampilkan status:
- **EXIT:ON** - Kamera keluar aktif
- **DRIVER:OFF** - Kamera driver dinonaktifkan
- **Camera: Service unavailable** - Service kamera tidak tersedia

## Troubleshooting

### 1. Kamera Tidak Terkoneksi
- Pastikan IP `192.168.10.70` dapat diakses
- Test dengan: `ping 192.168.10.70`
- Cek username/password di config.ini

### 2. URL Tidak Valid
- Test manual dengan curl
- Pastikan path `Snapshot/1/RemoteImageCapture?ImageFormat=2` benar
- Cek brand kamera di config (`exit_camera_brand = custom`)

### 3. Timeout Error
- Increase `capture_timeout` di config
- Cek koneksi jaringan
- Pastikan kamera tidak overloaded

## Konfigurasi Tambahan

### Mengaktifkan Driver Camera
```ini
driver_camera_enabled = True
driver_camera_ip = 192.168.10.71
driver_camera_username = admin
driver_camera_password = admin
```

### Mengganti Timeout
```ini
capture_timeout = 15  # 15 detik timeout
```

### Custom Brand untuk URL Berbeda
```ini
exit_camera_brand = custom
exit_camera_path = custom/snapshot/path
```

## Hasil Test Terakhir

✅ Kamera exit berhasil terkoneksi ke `192.168.10.70`  
✅ Berhasil mengambil gambar (65,440 bytes)  
✅ GUI berhasil dijalankan dengan integrasi kamera  
✅ Auto-capture berfungsi saat scan barcode  
✅ Preview kamera berfungsi di GUI
