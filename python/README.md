# Parking System - Manless Gate Application

Aplikasi sistem parkir tanpa petugas (manless) yang terdiri dari entry gate, exit gate, server, dan admin interface.

## Fitur Utama

### Entry Gate
- Deteksi kendaraan dengan sensor loop
- ALPR (Automatic License Plate Recognition) menggunakan fast-alpr
- Manajemen member dan non-member
- Kontrol palang otomatis via GPIO
- Audio feedback
- Print tiket untuk non-member

### Exit Gate
- Scanner barcode/kartu member
- Deteksi plat nomor otomatis
- Validasi transaksi
- Kontrol palang otomatis
- Print struk pembayaran

### Server
- WebSocket server untuk komunikasi real-time
- ALPR processing service
- Database CouchDB untuk penyimpanan data
- API untuk integrasi sistem

### Admin Interface
- Dashboard dengan statistik real-time
- Manajemen member
- Monitoring transaksi
- Konfigurasi sistem
- Chart dan reporting

## Teknologi Stack

- **Python 3.8+** - Bahasa pemrograman utama
- **WebSocket** - Komunikasi real-time
- **CouchDB** - Database NoSQL dengan attachment support
- **fast-alpr** - License plate recognition
- **OpenCV** - Image processing
- **RPi.GPIO** - GPIO control untuk Raspberry Pi
- **Flask** - Web framework untuk admin interface
- **Bootstrap 5** - UI framework

## Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd python
```

### 2. Install Dependencies

#### Untuk Desktop (Development)
```bash
pip install -r requirements.txt
```

#### Untuk Raspberry Pi
```bash
pip install -r requirements_raspberry_pi.txt
```

### 3. Setup Database CouchDB
```bash
# Install CouchDB
sudo apt-get install couchdb

# Atau dengan Docker
docker run -d --name couchdb -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=password -p 5984:5984 couchdb:latest
```

### 4. Konfigurasi
Edit file `config.ini` sesuai dengan environment Anda:
- Database connection
- CCTV IP address dan credentials
- GPIO pin configuration
- WebSocket server settings

### 5. Setup Audio Files
Tempatkan file audio di folder `sounds/`:
- `welcome.wav` - Pesan selamat datang
- `goodbye.wav` - Pesan terima kasih

## Menjalankan Aplikasi

### 1. Start Server
```bash
cd server
python websocket_server.py
```

### 2. Start Entry Gate
```bash
cd entry-gate
python entry_gate.py
```

### 3. Start Exit Gate
```bash
cd exit-gate
python exit_gate_gui.py
```

### 4. Start Admin Interface
```bash
cd admin
python app.py
```

Akses admin interface di: http://localhost:5000

## Konfigurasi Hardware

### GPIO Pin Configuration (Raspberry Pi)
- **Pin 18** - Trigger gate (output)
- **Pin 23** - Loop1 sensor (input)
- **Pin 24** - Loop2 sensor (input)
- **Pin 25** - Printer trigger (output)
- **Pin 17** - LED live indicator (output)
- **Pin 22** - Busy indicator (output)

### CCTV Setup
- IP Camera dengan snapshot HTTP endpoint
- Format URL: `http://username:password@ip:port/snapshot`
- Pastikan kamera dapat diakses dari jaringan yang sama

### Sensor Loop
- Sensor induksi untuk deteksi kendaraan
- Loop1: Deteksi kendaraan mendekat
- Loop2: Deteksi kendaraan sudah positioning

## Mode Simulasi

Aplikasi dapat berjalan dalam mode simulasi untuk development:
- GPIO akan di-simulate (tidak memerlukan Raspberry Pi)
- ALPR akan menggunakan data dummy
- Audio akan di-log tanpa output sound

## Struktur Database

### Collections/Documents:
- **members** - Data member dengan plate number
- **transactions** - Record entry/exit dengan attachment gambar
- **settings** - Konfigurasi sistem

### Transaction Types:
- `member_entry` - Member masuk
- `member_exit` - Member keluar  
- `non_member_entry` - Non-member masuk
- `non_member_exit` - Non-member keluar

## API Endpoints

### WebSocket Messages (Server)
- `register` - Register client
- `alpr_request` - Request ALPR processing
- `member_lookup` - Cari data member
- `save_transaction` - Simpan transaksi
- `last_entry_lookup` - Cari transaksi entry terakhir

### HTTP API (Admin)
- `GET /api/stats` - Statistik dashboard
- `GET /api/live_transactions` - Transaksi real-time

## Troubleshooting

### Common Issues:

1. **GPIO Permission Error**
   ```bash
   sudo usermod -a -G gpio $USER
   # Logout and login again
   ```

2. **CCTV Connection Failed**
   - Periksa IP address dan credentials
   - Test dengan browser: `http://ip:port/snapshot`

3. **Database Connection Error**
   - Pastikan CouchDB running
   - Periksa credentials di config.ini

4. **ALPR Not Working**
   - Install fast-alpr model yang sesuai
   - Periksa format gambar dari CCTV

### Logs
Aplikasi akan menulis log ke console. Untuk production, redirect ke file:
```bash
python app.py >> /var/log/parking-system.log 2>&1
```

## Development

### Project Structure
```
python/
├── shared/          # Komponen bersama
├── server/          # WebSocket server & ALPR
├── entry-gate/      # Aplikasi entry gate
├── exit-gate/       # Aplikasi exit gate (existing)
├── admin/           # Web admin interface
├── sounds/          # Audio files
└── config.ini       # Konfigurasi utama
```

### Adding New Features
1. Update shared components jika diperlukan
2. Modify server untuk API baru
3. Update client applications
4. Add admin interface untuk management

## Production Deployment

### Raspberry Pi Setup
1. Install Raspberry Pi OS Lite
2. Install Python dan dependencies
3. Setup autostart services
4. Configure GPIO permissions
5. Setup network dan firewall

### Service Configuration
Create systemd services untuk auto-start:
```bash
sudo systemctl enable parking-server
sudo systemctl enable parking-entry-gate
sudo systemctl enable parking-exit-gate
sudo systemctl enable parking-admin
```

## Support

Untuk pertanyaan atau issue, silakan buat GitHub issue atau hubungi tim development.
