# Exit Gate - Complete Offline Installation System

## Overview
This system provides a complete offline installation solution for the Exit Gate Node.js application on Raspberry Pi devices. No internet connection is required on the target Raspberry Pi.

## Quick Start

### 1. Create Offline Bundle (Windows)
```cmd
# Double-click to create bundle
CREATE-BUNDLE.cmd

# Or run PowerShell script directly
powershell -ExecutionPolicy Bypass -File simple-bundle-creator.ps1

# Or test bundle creation
test-bundle.cmd
```

### 2. Transfer & Install (Raspberry Pi)
```bash
# Extract bundle to Pi (via USB, SD card, or network transfer)
unzip exit-gate-offline-YYYYMMDD-HHMMSS.zip

# Navigate to bundle directory
cd exit-gate-offline-YYYYMMDD-HHMMSS/

# Fix line endings (if needed)
bash fix-line-endings.sh

# Install everything offline
sudo ./install-offline.sh
```

## Bundle Contents

Each offline bundle includes:
- **Complete Node.js Application** - All source files, routes, services
- **Node.js ARM Binary** - v20.11.0 compiled for Raspberry Pi
- **NPM Dependencies Cache** - All packages cached for offline install
- **Installation Scripts** - Automated installer with fallbacks
- **System Package List** - Required Debian packages
- **Documentation** - Installation guides and troubleshooting

## Bundle Creation Scripts

### `simple-bundle-creator.ps1` (Recommended)
- **Fast & Reliable** - Simple, optimized bundle creation
- **Minimal Output** - Clean progress display
- **Complete Package** - Includes all essentials for offline install
- **Size**: ~39MB compressed bundle

### `CREATE-BUNDLE.cmd` 
- **One-Click Solution** - Double-click to create bundle
- **Windows Friendly** - No PowerShell knowledge required
- **Automatic** - Runs simple-bundle-creator.ps1 script

### `test-bundle.cmd`
- **Testing Tool** - Validates bundle creation process
- **Pre-flight Check** - Verifies all required files exist
- **Development** - Useful for testing changes

## Installation Process

The `install-offline.sh` script performs these steps:

1. **Environment Setup**
   - Fixes file permissions
   - Sets up working directories
   - Validates system architecture

2. **Node.js Installation** 
   - Extracts Node.js ARM binary to `/opt/nodejs`
   - Creates symbolic links in `/usr/local/bin`
   - Configures PATH environment

3. **Application Deployment**
   - Copies application to `/opt/exit-gate`
   - Installs NPM dependencies from cache
   - Sets proper file permissions

4. **System Configuration**
   - Installs system packages (if available)
   - Configures systemd service
   - Sets up GPIO permissions
   - Enables auto-start

5. **Service Activation**
   - Starts exit-gate service
   - Enables service for boot startup
   - Validates installation

## Offline Features

### True Offline Operation
- ✅ No internet required on Raspberry Pi
- ✅ All dependencies bundled
- ✅ Node.js runtime included
- ✅ Automated installation
- ✅ Fallback for missing system packages

### System Package Handling
- **Preferred**: Downloads .deb packages during bundle creation
- **Fallback**: Lists required packages for manual installation
- **Required packages**: build-essential, python3-dev, libasound2-dev, git, curl, wget

### NPM Dependencies
- **Cached Installation**: Uses npm cache for offline installs
- **Version Locked**: Uses package-lock.json for reproducible builds
- **No Network**: Complete npm ci --offline installation

## Bundle Sizes

| Component | Size (Approximate) |
|-----------|-------------------|
| Node.js ARM Binary | ~22MB |
| NPM Dependencies | ~15MB |
| Application Code | ~1MB |
| Scripts & Docs | <1MB |
| **Total Bundle** | **~39MB** |

## File Structure

```
exit-gate-offline-YYYYMMDD-HHMMSS/
├── package.json & package-lock.json    # Application metadata
├── server.js                           # Main application
├── routes/, services/, public/         # Application components
├── npm-cache/                          # Cached NPM packages
├── node-v20.11.0-linux-armv7l.tar.xz  # Node.js ARM binary
├── install-offline.sh                  # Main offline installer
├── fix-line-endings.sh                 # Line ending fixer
├── system-packages.txt                 # Required system packages
├── INSTALL.md                          # Quick installation guide
└── README.md                           # Application documentation
```

## Troubleshooting

### Line Ending Issues
```bash
# Fix Windows CRLF to Linux LF
bash fix-line-endings.sh
```

### Permission Issues
```bash
# Make scripts executable
chmod +x install-offline.sh
chmod +x fix-line-endings.sh
```

### Missing System Packages
```bash
# Install manually if auto-install fails
sudo apt update
sudo apt install build-essential python3-dev libasound2-dev git curl wget
```

### Service Issues
```bash
# Check service status
sudo systemctl status exit-gate

# Restart service
sudo systemctl restart exit-gate

# View logs
sudo journalctl -u exit-gate -f
```

### GPIO Issues
```bash
# Check GPIO permissions
ls -la /dev/gpiomem

# Add user to gpio group
sudo usermod -a -G gpio pi
```

## Network Transfer Options

### USB/SD Card Transfer
1. Create bundle on Windows
2. Copy ZIP to USB drive
3. Transfer to Raspberry Pi
4. Extract and install

### Network Transfer (SCP)
```powershell
# Windows to Pi
scp exit-gate-offline-*.zip pi@raspberrypi.local:~/
```

### Network Transfer (SSH)
```bash
# On Pi, download from Windows machine
scp user@windows-machine:/path/to/bundle.zip ~/
```

## Development & Testing

### Bundle Testing
```cmd
# Test bundle creation
test-bundle.cmd

# Manual testing
powershell -ExecutionPolicy Bypass -File simple-bundle-creator.ps1
```

### Installation Testing
```bash
# Test installation (dry run)
sudo ./install-offline.sh --dry-run

# Verbose installation
sudo ./install-offline.sh --verbose
```

## Production Deployment

### Security Considerations
- Run as non-root user after installation
- Configure firewall rules for port 3000
- Use HTTPS in production environments
- Secure GPIO access permissions

### Performance Optimization
- Consider using PM2 for process management
- Configure log rotation
- Monitor system resources
- Implement health checks

### Backup & Recovery
- Backup configuration files regularly
- Document custom environment variables
- Maintain installation bundle versions
- Test recovery procedures

## Support

### Common Issues
1. **Bundle creation fails** - Check Windows PowerShell execution policy
2. **Transfer corrupted** - Verify ZIP file integrity
3. **Installation fails** - Check Raspberry Pi architecture (ARMv7)
4. **Service won't start** - Check logs and GPIO permissions
5. **Network issues** - Verify port 3000 accessibility

### Getting Help
- Check systemd logs: `sudo journalctl -u exit-gate`
- Verify Node.js: `/opt/nodejs/bin/node --version`
- Test application: `cd /opt/exit-gate && npm test`
- GPIO testing: Check `/sys/class/gpio` permissions

## Version Information

- **Node.js**: v20.11.0 LTS (ARM v7)
- **NPM**: Latest compatible version
- **Target OS**: Raspberry Pi OS (Debian-based)
- **Architecture**: ARMv7 (Raspberry Pi 2B+, 3, 4, Zero 2)

---

**Ready for true offline deployment! 🚀**
