# Fitur Penyimpanan Gambar CCTV

## Deskripsi
Fitur ini memungkinkan sistem parkir untuk menyimpan gambar dari 2 kamera CCTV secara otomatis:
1. **Kamera Plat Nomor** - Mengambil gambar kendaraan untuk identifikasi plat nomor
2. **Kamera Driver** - Mengambil gambar driver/pengemudi untuk keamanan

## Konfigurasi Kamera

### 1. Konfigurasi IP Kamera CCTV
Pastikan konfigurasi berikut telah diatur di settings:

```javascript
// Kamera Plat Nomor (Pintu Masuk)
PLATE_CAM_IP: "192.168.1.100"
PLATE_CAM_USERNAME: "admin"
PLATE_CAM_PASSWORD: "admin123"
PLATE_CAM_RTSP_PATH: "Streaming/Channels/101"

// Kamera Driver (Pintu Keluar)  
DRIVER_CAM_IP: "192.168.1.101"
DRIVER_CAM_USERNAME: "admin"
DRIVER_CAM_PASSWORD: "admin123"
DRIVER_CAM_RTSP_PATH: "Streaming/Channels/101"
```

### 2. Format URL RTSP
URL RTSP akan dibentuk secara otomatis dengan format:
```
rtsp://username:password@ip_address:554/rtsp_path
```

## Fitur Penyimpanan

### Kapan Gambar Diambil
Gambar akan diambil secara otomatis pada situasi berikut:

1. **Entry Normal** - Saat user memasukkan plat nomor dan menekan Enter
2. **Manual Gate Open** - Saat menekan tombol "Buka Manual"
3. **Emergency Open** - Saat menekan tombol "Emergency"
4. **Exit** - Saat kendaraan keluar (jika ada transaksi)

### Jenis Gambar yang Disimpan

#### Saat Masuk (Entry):
- `plate_entrance.jpg` - Gambar dari kamera plat nomor
- `driver_entrance.jpg` - Gambar dari kamera driver

#### Saat Keluar (Exit):
- `plate_exit.jpg` - Gambar dari kamera plat nomor saat keluar
- `driver_exit.jpg` - Gambar dari kamera driver saat keluar

## Implementasi Teknis

### 1. Store Transaksi (transaksi-store.ts)

#### Method Baru:
```typescript
// Menyimpan gambar sebagai attachment
saveTransactionAttachments(transactionId: string, rev: string): Promise<void>

// Mengambil gambar dari attachment
getTransactionAttachments(transactionId: string): Promise<{
  plateEntrance?: string;
  driverEntrance?: string;
  plateExit?: string;
  driverExit?: string;
}>
```

### 2. Komponen UI

#### TransactionImagesDialog.vue
Dialog untuk menampilkan semua gambar CCTV dari transaksi:
- Menampilkan 4 gambar dalam layout grid
- Klik gambar untuk melihat ukuran penuh
- Loading indicator saat memuat gambar

#### ViewImagesButton.vue
Tombol untuk membuka dialog gambar CCTV:
```vue
<ViewImagesButton
  :transactionId="transaction.id"
  color="primary"
  label="Lihat CCTV"
  icon="camera_alt"
/>
```

### 3. Penyimpanan di PouchDB

Gambar disimpan sebagai **attachment** di PouchDB dengan keuntungan:
- Terpisah dari document utama
- Tidak membebani query transaksi
- Bisa diakses on-demand
- Mendukung sinkronisasi dengan CouchDB

#### Struktur Penyimpanan:
```javascript
// Document transaksi
{
  _id: "transaction_TXN20241228001",
  _rev: "1-abc123",
  id: "TXN20241228001",
  no_pol: "B1234ABC",
  // ... data transaksi lainnya
  
  // Attachment metadata
  _attachments: {
    "plate_entrance.jpg": {
      content_type: "image/jpeg",
      length: 45678,
      digest: "md5-xyz789"
    },
    "driver_entrance.jpg": {
      content_type: "image/jpeg", 
      length: 56789,
      digest: "md5-abc456"
    }
  }
}
```

## Cara Penggunaan

### 1. Menangkap Gambar Otomatis
```javascript
// Saat entry - otomatis menangkap dari kedua kamera
await captureEntryImages();

// Saat exit - otomatis menangkap dari kedua kamera  
await captureExitImages();
```

### 2. Melihat Gambar Transaksi
```javascript
// Di komponen Vue
const $q = useQuasar();

const viewCCTVImages = (transactionId) => {
  $q.dialog({
    component: TransactionImagesDialog,
    componentProps: {
      transactionId: transactionId
    }
  });
};
```

### 3. Mendapatkan Gambar Programatically
```javascript
const transaksiStore = useTransaksiStore();

// Ambil semua gambar dari transaksi
const images = await transaksiStore.getTransactionAttachments('TXN20241228001');

console.log(images);
// Output:
// {
//   plateEntrance: "data:image/jpeg;base64,/9j/4AAQ...",
//   driverEntrance: "data:image/jpeg;base64,/9j/4AAQ...",
//   plateExit: "data:image/jpeg;base64,/9j/4AAQ...",
//   driverExit: "data:image/jpeg;base64,/9j/4AAQ..."
// }
```

## Troubleshooting

### 1. Gambar Tidak Tersimpan
- Pastikan kamera CCTV dapat diakses via RTSP
- Periksa konfigurasi IP, username, password
- Cek koneksi jaringan ke kamera
- Lihat console log untuk error

### 2. Kamera Tidak Terdeteksi
- Pastikan `plateCameraType` dan `driverCameraType` mengembalikan 'cctv'
- Periksa konfigurasi `PLATE_CAM_IP` dan `DRIVER_CAM_IP` di settings
- Test koneksi RTSP secara manual

### 3. Performance Issues
- Gambar disimpan sebagai attachment untuk optimasi
- Loading gambar dilakukan on-demand
- Pertimbangkan kompresi gambar jika file terlalu besar

## Logging & Debugging

Enable logging untuk monitoring:

```javascript
// Di console browser
console.log('📸 Current images:', {
  plateImage: transaksiStore.pic_plat_masuk ? 'Available' : 'Not available',
  driverImage: transaksiStore.pic_body_masuk ? 'Available' : 'Not available'
});
```

Log yang berguna:
- `📸 Capturing entry images from both cameras...`
- `✅ Entry images captured successfully`
- `❌ Error capturing entry images:`
- `📸 Loaded transaction images:`

## Keamanan

1. **RTSP Credentials** - Username/password kamera disimpan terenkripsi
2. **Image Access** - Hanya user yang berwenang bisa melihat gambar
3. **Data Retention** - Gambar mengikuti kebijakan retention transaksi
4. **Network Security** - Gunakan VLAN terpisah untuk kamera CCTV

## Roadmap

### Fitur Mendatang:
1. **Kompresi Gambar** - Mengurangi ukuran file attachment
2. **Watermark** - Menambah timestamp dan info transaksi
3. **Motion Detection** - Hanya simpan gambar saat ada pergerakan
4. **Cloud Backup** - Backup gambar ke cloud storage
5. **AI Recognition** - Integrasi dengan AI untuk plate recognition
