# CCTV Integration Update - Manual Gate

## Summary
Integrasi konfigurasi CCTV di `manual-gate.vue` telah dioptimalkan untuk menggunakan konfigurasi langsung dari `settings-service.ts` tanpa parsing URL yang kompleks.

## Changes Made

### 1. Simplified Camera Credentials
- **Before**: Menggunakan fungsi `parseRtspUrl()` yang kompleks
- **After**: Langsung mengambil dari `gateSettings` dengan fallback yang jelas

```javascript
const plateCameraCredentials = computed(() => {
  const config = {
    username: gateSettings.value?.PLATE_CAM_USERNAME || 'admin',
    password: gateSettings.value?.PLATE_CAM_PASSWORD || 'admin123',
    ip_address: gateSettings.value?.PLATE_CAM_IP || ''
  };
  
  if (!config.ip_address) {
    config.ip_address = '192.168.10.25';
    console.warn('No PLATE_CAM_IP configured, using default IP for testing');
  }
  
  return config;
});
```

### 2. Enhanced Debug Information
- Menampilkan konfigurasi kamera yang lebih detail di console
- Password di-mask untuk keamanan
- Menampilkan apakah konfigurasi sudah diset atau menggunakan default

### 3. Configuration Status Notifications
- **Auto-check**: Notifikasi otomatis saat konfigurasi kamera tidak tersedia
- **Action button**: Tombol untuk langsung membuka Settings dialog
- **Visual indicators**: Chip kamera menunjukkan status konfigurasi (hijau = dikonfigurasi, kuning = default)

### 4. Camera Configuration Management
- **Reload Config**: Tombol untuk memuat ulang konfigurasi tanpa restart
- **Enhanced Test**: Test koneksi dengan error details yang lebih informatif
- **Live Updates**: Watcher untuk monitoring perubahan konfigurasi real-time

### 5. UI Improvements
- **Status Indicators**: Chip kamera menampilkan IP address dan status
- **Color Coding**: 
  - 🟢 Hijau = Konfigurasi sudah diset
  - 🟡 Kuning = Menggunakan default (perlu konfigurasi)
- **Admin Tools**: Tombol debug hanya tampil untuk admin

## Configuration Flow

```
1. SettingsDialog.vue → Simpan konfigurasi CCTV
2. settings-service.ts → Kelola penyimpanan di PouchDB
3. manual-gate.vue → Baca konfigurasi dan gunakan untuk Camera component
4. Camera.vue → Terima props dan hubungkan ke CCTV
```

## Testing Features

### For Admins:
1. **Test Capture** (F-key or button) - Test manual image capture
2. **Test Koneksi** (button) - Test CCTV connection with detailed errors
3. **Reload Config** (button) - Reload camera configuration from settings

### Configuration Check:
- Otomatis cek konfigurasi saat startup
- Notifikasi jika ada kamera yang belum dikonfigurasi
- Link langsung ke Settings dialog

## Default Values for Testing
- **Plate Camera**: 192.168.10.25 (admin/admin123)
- **Driver Camera**: 192.168.10.26 (admin/admin123)
- **RTSP Path**: Streaming/Channels/101

## Next Steps
1. **Test dengan kamera fisik** - Verifikasi koneksi ke kamera CCTV sebenarnya
2. **Performance optimization** - Optimasi untuk kamera berkecepatan tinggi
3. **Error recovery** - Handling otomatis untuk reconnection kamera

## Configuration in Settings
Konfigurasi CCTV tersedia di Settings Dialog (F7) pada section "Camera Settings":
- **USB Camera**: Pilihan kamera USB yang terdeteksi
- **CCTV IP Address**: IP address kamera CCTV
- **CCTV Username/Password**: Kredensial untuk akses kamera
- **CCTV RTSP Path**: Path RTSP stream (default: Streaming/Channels/101)

## Benefits
- ✅ **Simplified code**: Tidak ada parsing URL yang kompleks
- ✅ **Better debugging**: Console logs yang lebih informatif
- ✅ **User-friendly**: Notifikasi dan guidance yang jelas
- ✅ **Real-time updates**: Konfigurasi terupdate tanpa restart
- ✅ **Admin tools**: Debug tools untuk troubleshooting
- ✅ **Visual feedback**: Status indicators yang jelas
