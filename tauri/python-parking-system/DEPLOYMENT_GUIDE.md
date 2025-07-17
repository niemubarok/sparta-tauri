# Deployment Guide - Python Parking System Standalone Apps

Guide untuk deployment aplikasi parking system di device terpisah.

## Persiapan Deployment

### Prerequisites
- Python 3.8+ installed di setiap device
- Git (optional, untuk clone repository)
- Network access untuk database CouchDB
- Camera device terhubung ke setiap gate device

### Device Requirements
- RAM minimum 4GB per device
- Storage minimum 10GB per device
- Camera USB/IP Camera per device
- Network connectivity

## Deployment Steps

### 1. Persiapan Files
Copy struktur berikut ke setiap device:

```
Device Entry Manual (Device 1):
- Copy folder `entry-manual/` 
- Copy folder `src/` (shared)

Device Entry Manless (Device 2):
- Copy folder `entry-manless/`
- Copy folder `src/` (shared)

Device Exit Manual (Device 3):
- Copy folder `exit-manual/`
- Copy folder `src/` (shared)

Device Exit Manless (Device 4):
- Copy folder `exit-manless/`
- Copy folder `src/` (shared)
```

### 2. Setup Database (Central)
Setup CouchDB di server central:

```bash
# Using Docker
docker run -d --name couchdb \
  -p 5984:5984 \
  -e COUCHDB_USER=admin \
  -e COUCHDB_PASSWORD=password \
  -v couchdb-data:/opt/couchdb/data \
  couchdb:3.3

# Create parking_system database
curl -X PUT http://admin:password@localhost:5984/parking_system
```

### 3. Device Configuration

#### Device 1 - Entry Manual (IP: 192.168.1.101)
```bash
cd entry-manual
# Edit .env file
DEVICE_TYPE=entry_manual
DEVICE_ID=entry_manual_device_001
COUCHDB_HOST=192.168.1.100  # Central database server
COUCHDB_PORT=5984
CAMERA_SOURCE=0  # USB camera index or IP camera URL
API_PORT=8001
```

#### Device 2 - Entry Manless (IP: 192.168.1.102)  
```bash
cd entry-manless
# Edit .env file
DEVICE_TYPE=entry_manless
DEVICE_ID=entry_manless_device_001
COUCHDB_HOST=192.168.1.100
COUCHDB_PORT=5984
CAMERA_SOURCE=0
API_PORT=8002
AUTO_SCAN_INTERVAL=2
```

#### Device 3 - Exit Manual (IP: 192.168.1.103)
```bash
cd exit-manual
# Edit .env file
DEVICE_TYPE=exit_manual
DEVICE_ID=exit_manual_device_001
COUCHDB_HOST=192.168.1.100
COUCHDB_PORT=5984
CAMERA_SOURCE=0
API_PORT=8003
```

#### Device 4 - Exit Manless (IP: 192.168.1.104)
```bash
cd exit-manless
# Edit .env file
DEVICE_TYPE=exit_manless
DEVICE_ID=exit_manless_device_001
COUCHDB_HOST=192.168.1.100
COUCHDB_PORT=5984
CAMERA_SOURCE=0
API_PORT=8004
AUTO_SCAN_INTERVAL=2
```

### 4. Install Dependencies di Setiap Device

```bash
# Di setiap device
pip install -r requirements.txt
```

### 5. Testing Individual Device

```bash
# Test di setiap device
python main.py

# Atau menggunakan batch file di Windows
start.bat
```

### 6. Production Service Setup

#### Windows Service (setiap device)
```bash
# Install NSSM (Non-Sucking Service Manager)
# Download dari https://nssm.cc/

# Install service
nssm install EntryManualGate
nssm set EntryManualGate Application "C:\Python\python.exe"
nssm set EntryManualGate AppParameters "main.py"
nssm set EntryManualGate AppDirectory "C:\parking-system\entry-manual"
nssm set EntryManualGate DisplayName "Entry Manual Gate Service"
nssm set EntryManualGate Description "Parking System Entry Manual Gate"

# Start service
nssm start EntryManualGate
```

#### Linux Systemd Service (setiap device)
```bash
# Create service file
sudo nano /etc/systemd/system/entry-manual-gate.service

[Unit]
Description=Entry Manual Gate Service
After=network.target

[Service]
Type=simple
User=parking
WorkingDirectory=/opt/parking-system/entry-manual
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable entry-manual-gate.service
sudo systemctl start entry-manual-gate.service
```

## Network Architecture

```
                    Central Database
                    CouchDB Server
                   (192.168.1.100:5984)
                           |
            +--------------+--------------+
            |              |              |
    Entry Manual    Entry Manless   Exit Manual    Exit Manless
   192.168.1.101   192.168.1.102  192.168.1.103  192.168.1.104
      Port 8001       Port 8002      Port 8003      Port 8004
         |               |              |              |
     Operator        Automatic      Operator       Automatic
     Interface       Detection      Interface      Detection
```

## Monitoring & Maintenance

### Health Check
Setiap device menyediakan endpoint untuk health check:
```bash
# Check device status
curl http://192.168.1.101:8001/health  # Entry Manual
curl http://192.168.1.102:8002/health  # Entry Manless
curl http://192.168.1.103:8003/health  # Exit Manual  
curl http://192.168.1.104:8004/health  # Exit Manless
```

### Log Monitoring
```bash
# Monitor logs di setiap device
tail -f entry_manual_gate.log
tail -f entry_manless_gate.log
tail -f exit_manual_gate.log
tail -f exit_manless_gate.log
```

### Database Backup
```bash
# Backup CouchDB database
curl -X GET http://admin:password@192.168.1.100:5984/parking_system/_all_docs?include_docs=true > backup_parking_system.json
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check network connectivity ke database server
   - Verify CouchDB credentials
   - Sistem akan fallback ke JSON files

2. **Camera Not Detected**
   - Check camera connection
   - Verify camera permissions
   - Test dengan aplikasi camera lain
   - Update CAMERA_SOURCE di .env

3. **ALPR Model Download Failed**
   - Check internet connection
   - Verify disk space
   - Models akan didownload otomatis saat pertama run

4. **Port Already in Use**
   - Check port availability dengan `netstat -an | grep 8001`
   - Update API_PORT di .env file

### Emergency Procedures

1. **Manual Failover**
   ```bash
   # Stop service
   sudo systemctl stop entry-manual-gate.service
   
   # Run manually untuk debugging
   python main.py
   ```

2. **Database Failover**
   - Sistem otomatis fallback ke JSON files
   - Data akan sync kembali setelah database available

3. **Camera Failover**
   - Sistem akan berjalan dalam simulation mode
   - Manual input tetap bisa digunakan

## Security Considerations

1. **Network Security**
   - Use firewall untuk restrict access
   - VPN untuk remote management
   - Change default database passwords

2. **Application Security**
   - Regular updates untuk dependencies
   - Monitor logs untuk suspicious activity
   - Secure camera feeds

3. **Physical Security**
   - Secure device placement
   - Tamper-proof enclosures
   - Backup power supply

## Performance Optimization

1. **Hardware Recommendations**
   - SSD storage untuk faster I/O
   - Dedicated GPU untuk ALPR (optional)
   - Gigabit network untuk database sync

2. **Software Optimization**
   - Adjust ALPR confidence threshold
   - Optimize camera resolution vs performance
   - Monitor memory usage

## Maintenance Schedule

### Daily
- Check log files untuk errors
- Verify device connectivity
- Monitor camera feeds

### Weekly  
- Database backup
- Performance monitoring
- Update check

### Monthly
- Full system health check
- Security audit
- Dependency updates

Setiap aplikasi dirancang untuk autonomous operation dengan minimal maintenance required.
