# Exit Manual Gate - Standalone Application

Gate Exit dengan Operator untuk kontrol manual kendaraan keluar.

## Fitur

- ✅ Kontrol manual oleh operator
- ✅ Scan plat nomor kendaraan dengan ALPR
- ✅ Validasi pembayaran/tiket
- ✅ Buka/tutup gate manual
- ✅ Monitor aktivitas kendaraan
- ✅ Database CouchDB dengan fallback JSON
- ✅ Log sistem lengkap
- ✅ Interface visual untuk operator

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

- **Device Type**: Exit Manual Gate
- **Port**: 8003
- **Mode**: Manual (dengan operator)
- **Function**: Gate keluar kendaraan

## Konfigurasi

Edit file `.env` untuk mengubah konfigurasi:

```env
DEVICE_TYPE=exit_manual
DEVICE_ID=exit_manual_001
GATE_TYPE=exit
GATE_MODE=manual

# Database
COUCHDB_HOST=localhost
COUCHDB_PORT=5984

# Camera
CAMERA_SOURCE=0

# ALPR
ALPR_CONFIDENCE_THRESHOLD=0.5
```

## Deployment

Aplikasi ini dirancang untuk berjalan standalone di device terpisah:

1. Copy folder `exit-manual` ke device target
2. Install Python dan dependencies
3. Konfigurasi `.env` sesuai device
4. Jalankan aplikasi

## Log Files

- `exit_manual_gate.log` - Log sistem lengkap
- Console output - Real-time monitoring

## Kontrol Operator

Sistem menyediakan interface visual untuk operator dengan fitur:
- Scan plat nomor manual
- Validasi pembayaran/tiket
- Kontrol buka/tutup gate
- Monitor status real-time
- Log aktivitas kendaraan keluar

## Proses Exit

1. Kendaraan datang ke gate exit
2. Operator scan plat nomor
3. Sistem validasi dari database
4. Cek pembayaran/durasi parkir
5. Operator buka gate jika valid
6. Log aktivitas keluar
