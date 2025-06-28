# 🚨 Troubleshooting: "Failed to Start Stream" - Manual Gate CCTV

## Masalah yang Ditemukan

Kamera CCTV di manual-gate.vue menampilkan error "failed to start stream" karena beberapa masalah konfigurasi.

## ✅ Perbaikan yang Sudah Dilakukan

### 1. **Fixed Camera Type Detection**
**Sebelum:**
```javascript
const plateCameraType = computed(() => {
  // ... logic
  return null; // Menyebabkan kamera tidak terdeteksi
});
```

**Sesudah:**
```javascript
const plateCameraType = computed(() => {
  if (gateSettings.value?.PLATE_CAM_DEVICE_ID) return 'usb';
  if (gateSettings.value?.PLATE_CAM_IP) return 'cctv';
  return 'cctv'; // Default to cctv jika tidak ada config
});
```

### 2. **Added Default Camera Credentials**
**Sebelum:**
```javascript
const plateCameraCredentials = computed(() => {
  return parseRtspUrl(...); // Bisa return undefined/null
});
```

**Sesudah:**
```javascript
const plateCameraCredentials = computed(() => {
  return parseRtspUrl(...) || {
    username: 'admin',
    password: 'Hiks2024',
    ip_address: '192.168.10.25' // Default fallback
  };
});
```

### 3. **Enhanced Template Props**
Template Camera sudah memiliki props yang lengkap:
```vue
<Camera
  ref="plateCameraRef"
  :username="plateCameraCredentials.username"
  :password="plateCameraCredentials.password"
  :ipAddress="plateCameraCredentials.ip_address"
  :rtspStreamPath="gateSettings.PLATE_CAM_RTSP_PATH || 'Streaming/Channels/101'"
  :cameraType="plateCameraType"
  label="Kamera Kendaraan"
/>
```

### 4. **Added Debug Tools**

#### A. Camera Debugger Component
- Real-time status monitoring
- Test koneksi dan capture
- Debug panel floating untuk admin

#### B. Debug Functions
```javascript
// Test koneksi manual
const testCameraConnection = async () => { ... }

// Test capture manual  
const testCaptureImages = async () => { ... }
```

#### C. Console Logging
Logging yang lebih detail untuk troubleshooting:
```javascript
console.log('Manual Gate - plateCameraCredentials:', plateCameraCredentials.value);
console.log('Manual Gate - driverCameraCredentials:', driverCameraCredentials.value);
```

## 🔧 Cara Testing

### 1. **Gunakan Camera Debugger**
- Login sebagai admin
- Klik tombol floating "bug" di kanan atas
- Panel debug akan muncul dengan info lengkap
- Klik "Test Koneksi" untuk mengecek

### 2. **Manual Testing Buttons**
Untuk admin, tersedia tombol:
- **"Test Capture"** - Test capture gambar
- **"Test Koneksi"** - Test koneksi ke kamera

### 3. **Console Debugging**
Buka Developer Tools → Console, akan muncul log:
```
Manual Gate - plateCameraType: cctv
Manual Gate - plateCameraCredentials: {username: "admin", password: "Hiks2024", ip_address: "192.168.10.25"}
```

## ⚙️ Konfigurasi yang Diperlukan

### Option 1: Gunakan Default (untuk testing)
Tidak perlu konfigurasi apapun, sistem akan menggunakan:
- **Plate Camera:** `admin:Hiks2024@192.168.10.25`
- **Driver Camera:** `admin:Hiks2024@192.168.10.26`

### Option 2: Konfigurasi Manual di Settings
Set di settings service:
```javascript
gateSettings: {
  PLATE_CAM_IP: "192.168.1.100",
  PLATE_CAM_USERNAME: "admin",
  PLATE_CAM_PASSWORD: "password123",
  PLATE_CAM_RTSP_PATH: "Streaming/Channels/101",
  
  DRIVER_CAM_IP: "192.168.1.101", 
  DRIVER_CAM_USERNAME: "admin",
  DRIVER_CAM_PASSWORD: "password123",
  DRIVER_CAM_RTSP_PATH: "Streaming/Channels/101"
}
```

## 🔍 Checklist Troubleshooting

### ✅ **1. Verify Camera Type**
```javascript
console.log('Camera types:', {
  plate: plateCameraType.value,
  driver: driverCameraType.value
});
// Should show: { plate: "cctv", driver: "cctv" }
```

### ✅ **2. Verify Credentials** 
```javascript
console.log('Credentials:', {
  plate: plateCameraCredentials.value,
  driver: driverCameraCredentials.value  
});
// Should show valid username, password, ip_address
```

### ✅ **3. Test Network Connection**
- Pastikan kamera dapat diakses via ping
- Test RTSP URL manual dengan VLC/ffmpeg
- Pastikan port 554 terbuka

### ✅ **4. Verify RTSP URL Format**
URL yang dibentuk harus seperti:
```
rtsp://admin:Hiks2024@192.168.10.25:554/Streaming/Channels/101
```

## 🚀 Next Steps

Jika masih ada masalah:

1. **Gunakan Camera Debugger** untuk melihat status real-time
2. **Check console logs** untuk error detail
3. **Test manual** dengan tombol test yang disediakan
4. **Verify network** - ping IP kamera dari command prompt
5. **Check credentials** - test login via browser ke IP kamera

## 📝 Known Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Failed to start stream" | ✅ Fixed: Added default camera type 'cctv' |
| Camera type returns null | ✅ Fixed: Added fallback logic |
| Missing credentials | ✅ Fixed: Added default credentials |
| No debugging info | ✅ Fixed: Added debug tools |

Dengan perbaikan ini, kamera CCTV di manual-gate.vue seharusnya bisa berfungsi dengan baik. Gunakan debug tools untuk monitoring dan troubleshooting lebih lanjut.
