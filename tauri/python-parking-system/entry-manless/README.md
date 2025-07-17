# Entry Manless Gate - Standalone Application

Gate Entry Otomatis tanpa operator untuk kendaraan masuk.

## Fitur

- 🤖 Deteksi kendaraan otomatis
- 🤖 Scan plat nomor otomatis dengan ALPR
- 🤖 Buka/tutup gate otomatis
- 🤖 Monitoring 24/7
- ✅ Database CouchDB dengan fallback JSON
- ✅ Log aktivitas otomatis
- ✅ Sistem tanpa operator

## Instalasi

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Konfigurasi environment:
```bash
# Edit file .env sesuai kebutuhan
cp .env.example .env
```

3. Setup CouchDB (opsional):
```bash
# Install CouchDB di sistem atau gunakan Docker
docker run -d --name couchdb -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=password couchdb:3.3
```

## Menjalankan Aplikasi

```bash
python main.py
```

## Struktur Device

- **Device Type**: Entry Manless Gate
- **Port**: 8002
- **Mode**: Manless (tanpa operator)
- **Function**: Gate masuk otomatis

## Konfigurasi

Edit file `.env` untuk mengubah konfigurasi:

```env
DEVICE_TYPE=entry_manless
DEVICE_ID=entry_manless_001
GATE_TYPE=entry
GATE_MODE=manless

# Automatic Detection
AUTO_SCAN_INTERVAL=2
VEHICLE_DETECTION_THRESHOLD=0.7
AUTO_GATE_TIMEOUT=10

# Camera
CAMERA_SOURCE=0

# ALPR
ALPR_CONFIDENCE_THRESHOLD=0.5
```

## Deployment

Aplikasi ini dirancang untuk berjalan standalone di device terpisah:

1. Copy folder `entry-manless` ke device target
2. Install Python dan dependencies
3. Konfigurasi `.env` sesuai device
4. Jalankan aplikasi sebagai service

## Log Files

- `entry_manless_gate.log` - Log sistem lengkap
- Console output - Real-time monitoring

## Sistem Otomatis

Sistem berjalan otomatis 24/7 dengan fitur:
- Deteksi kendaraan masuk
- Scan ALPR otomatis
- Validasi database
- Buka gate otomatis
- Log semua aktivitas

## Monitoring

Sistem menampilkan status monitoring setiap 30 detik:
- Status gate
- Waktu scan terakhir
- Device ID
- Aktivitas sistem
