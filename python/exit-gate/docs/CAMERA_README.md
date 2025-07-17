# Camera Integration Documentation

## Overview

Camera service telah diintegrasikan ke dalam Exit Gate GUI untuk mengambil snapshot dari kamera IP (CCTV) menggunakan HTTP requests. Sistem mendukung berbagai merk kamera termasuk Hikvision, Glenz, Dahua, dan lainnya.

## Fitur Camera Integration

### 1. Preview Kamera di GUI
- Preview window di GUI utama
- Tampilan status kamera (ON/OFF)
- Update preview otomatis saat capture

### 2. Tombol Kontrol Kamera
- **Capture Exit**: Ambil foto dari kamera keluar (utama)
- **Capture Driver**: Ambil foto dari kamera driver (opsional)
- **Capture All**: Ambil foto dari semua kamera yang tersedia
- **Test Cameras**: Test konektivitas semua kamera

### 3. Auto-Capture saat Scan Barcode
- Otomatis mengambil foto saat barcode di-scan
- Mendukung audit trail dengan timestamp
- Preview langsung di GUI

## Konfigurasi Camera

### File config.ini

```ini
[camera]
enabled = True

# Exit Camera (Kamera Keluar) - Primary Camera
exit_camera_ip = 192.168.10.210
exit_camera_username = admin
exit_camera_password = admin
exit_camera_brand = custom
exit_camera_path = Snapshot/1/RemoteImageCapture?ImageFormat=2
capture_timeout = 10

# Optional Driver Camera (disabled by default)
driver_camera_enabled = False
driver_camera_ip = 192.168.1.101
driver_camera_username = admin
driver_camera_password = admin123
driver_camera_brand = auto
```

### Supported Camera Brands

#### 1. Hikvision
```ini
plate_camera_brand = hikvision
```
URL Pattern: `http://IP/ISAPI/Streaming/channels/101/picture`

#### 2. Glenz
```ini
plate_camera_brand = glenz
```
URL Pattern: `http://IP/onvif-http/snapshot?Profile_1`

#### 3. Dahua
```ini
plate_camera_brand = dahua
```
URL Pattern: `http://IP/cgi-bin/snapshot.cgi?channel=1`

#### 4. Axis
```ini
plate_camera_brand = axis
```
URL Pattern: `http://IP/axis-cgi/jpg/image.cgi`

#### 5. Generic/ONVIF
```ini
plate_camera_brand = generic
```
URL Pattern: `http://IP/onvif/media_service/snapshot?ProfileToken=Profile_1`

#### 7. Custom Path
```ini
exit_camera_brand = custom
exit_camera_path = Snapshot/1/RemoteImageCapture?ImageFormat=2
```
URL Result: `http://admin:admin@192.168.10.210/Snapshot/1/RemoteImageCapture?ImageFormat=2`

#### 8. Auto-detect
```ini
exit_camera_brand = auto
```
Menggunakan snapshot_path yang dikonfigurasi

## Testing Camera

### 1. Test Individual Camera
```bash
python test_camera_gui.py
```

### 2. Test dari GUI
- Klik tombol "Test Cameras" di GUI
- Lihat log untuk hasil test
- Status kamera akan update otomatis

### 3. Manual Test dengan curl

#### Custom Camera (sesuai konfigurasi Anda):
```bash
curl -u admin:admin "http://192.168.10.210/Snapshot/1/RemoteImageCapture?ImageFormat=2" -o test.jpg
# atau dengan embedded auth:
curl "http://admin:admin@192.168.10.210/Snapshot/1/RemoteImageCapture?ImageFormat=2" -o test.jpg
```

#### Hikvision:
```bash
curl -u admin:admin123 "http://192.168.1.100/ISAPI/Streaming/channels/101/picture" -o test.jpg
```

#### Glenz:
```bash
curl -u admin:admin123 "http://192.168.1.100/onvif-http/snapshot?Profile_1" -o test.jpg
```

#### Dahua:
```bash
curl -u admin:admin123 "http://192.168.1.100/cgi-bin/snapshot.cgi?channel=1" -o test.jpg
```

## Cara Penggunaan

### 1. Setup Initial
1. Update `config.ini` dengan IP dan kredensial kamera
2. Set `camera_brand` sesuai merk kamera
3. Test konektivitas: `python test_camera_gui.py`

### 2. Menjalankan GUI dengan Camera
```bash
python gui_exit_gate.py
```

### 3. Fitur GUI Camera
- **Auto-capture**: Foto otomatis saat scan barcode
- **Manual capture**: Klik tombol capture untuk test
- **Preview**: Lihat hasil capture di preview window
- **Status**: Monitor status kamera di status bar

## Troubleshooting

### 1. Camera Not Connected
**Error**: `Connection error to camera 'plate'`

**Solutions**:
- Cek IP kamera di `config.ini`
- Ping kamera: `ping 192.168.1.100`
- Cek network connectivity
- Pastikan kamera dalam network yang sama

### 2. Authentication Failed
**Error**: `HTTP 401 from camera 'plate'`

**Solutions**:
- Cek username/password di `config.ini`
- Test login via web browser
- Pastikan user memiliki permission snapshot

### 3. Timeout Error
**Error**: `Timeout capturing from camera 'plate'`

**Solutions**:
- Increase `capture_timeout` di config
- Cek network latency
- Pastikan kamera tidak overloaded

### 4. Wrong URL Path
**Error**: `HTTP 404 from camera 'plate'`

**Solutions**:
- Cek `camera_brand` setting
- Test manual dengan curl
- Gunakan brand `auto` atau `custom`
- Set custom `snapshot_path`

### 5. PIL/Pillow Not Available
**Warning**: `PIL/Pillow not available - camera preview disabled`

**Solutions**:
```bash
pip install pillow==6.2.2  # Python 2.7
# atau
pip install pillow  # Python 3.x
```

## Advanced Configuration

### Multiple Camera Setup
Bisa ditambahkan kamera ketiga atau keempat dengan memodifikasi `camera_service.py`:

```python
# Overview camera
overview_config = CameraConfig("overview")
overview_config.ip = config.get('camera', 'overview_camera_ip', '192.168.1.102')
overview_config.username = config.get('camera', 'overview_camera_username', 'admin')
overview_config.password = config.get('camera', 'overview_camera_password', 'admin123')
overview_config.brand = config.get('camera', 'overview_camera_brand', 'auto')
self.cameras['overview'] = overview_config
```

### Custom URL Patterns
Untuk kamera dengan URL pattern khusus, tambahkan di `get_snapshot_url()`:

```python
elif self.brand.lower() == 'custom_brand':
    return "{}/custom/snapshot/path".format(base_url)
```

### Image Processing
Untuk processing tambahan (resize, compression, watermark), modifikasi method `capture_image()` di `camera_service.py`.

## Integration dengan Database

Camera capture terintegrasi dengan database service:
- Image disimpan sebagai base64 di transaction record
- Timestamp capture tersimpan
- Link dengan barcode dan transaction ID

## Security Notes

1. **Kredensial Kamera**: Gunakan user khusus dengan permission minimal
2. **Network Security**: Pastikan kamera di network terpisah/VLAN
3. **HTTPS**: Gunakan HTTPS jika kamera mendukung
4. **Firewall**: Buka port minimal yang diperlukan

## Performance Tips

1. **Image Quality**: Set quality/resolution sesuai kebutuhan
2. **Timeout**: Set timeout yang appropriate (3-10 detik)
3. **Concurrent Capture**: Hindari capture simultan dari banyak kamera
4. **Storage**: Monitor disk space untuk image storage

## API Reference

### CameraService Methods
- `capture_image(camera_name)`: Capture dari kamera tertentu
- `capture_exit_images()`: Capture dari semua kamera
- `test_all_cameras()`: Test konektivitas semua kamera
- `get_cameras_status()`: Get status semua kamera

### GUI Methods
- `capture_camera_image(camera_name)`: GUI capture method
- `capture_exit_images()`: GUI exit capture
- `update_camera_preview(image_data)`: Update preview display
- `test_all_cameras()`: GUI test method
