# Exit Gate Node.js Compatibility Troubleshooting Guide

## Problem: GLIBCXX_3.4.26 Not Found Error

### Error Symptoms
```
/usr/local/bin/node: /usr/lib/arm-linux-gnueabihf/libstdc++.so.6: version `GLIBCXX_3.4.26' not found (required by /usr/local/bin/node)
exit-gate.service: Main process exited, code=exited, status=1/FAILURE
```

### Root Cause
This error occurs when the Node.js binary requires a newer version of the C++ standard library (libstdc++) than what's available on the Raspberry Pi system. Node.js v20+ requires GLIBCXX_3.4.26, but older Raspberry Pi OS versions only have GLIBCXX_3.4.25 or earlier.

### Quick Fix Solutions

#### Option 1: Use the Updated Bundle (Recommended)
The latest bundle now includes Node.js v18.19.1 which is compatible with older systems:

1. **Download the new bundle**: `exit-gate-offline-20250629-152636.zip`
2. **Install normally**: 
   ```bash
   sudo ./install-offline.sh
   ```

#### Option 2: Run the Compatibility Fix Script
If you have an internet connection on the Pi:

```bash
# Make script executable
chmod +x fix-compatibility.sh

# Run the compatibility fix
sudo ./fix-compatibility.sh
```

#### Option 3: Manual Fix (No Internet Required)
If the bundle doesn't work and you have no internet:

1. **Stop the service**:
   ```bash
   sudo systemctl stop exit-gate
   ```

2. **Remove current Node.js**:
   ```bash
   sudo rm -rf /usr/local/bin/node /usr/local/bin/npm /usr/local/bin/npx /usr/local/lib/node_modules
   ```

3. **Extract the bundled Node.js v18.19.1**:
   ```bash
   cd /path/to/bundle
   sudo tar -xf node-v18.19.1-linux-armv7l.tar.xz -C /usr/local --strip-components=1
   ```

4. **Test Node.js**:
   ```bash
   node --version
   # Should output: v18.19.1
   ```

5. **Restart the service**:
   ```bash
   sudo systemctl start exit-gate
   ```

### System Compatibility Check

#### Check Your System's GLIBCXX Version
```bash
# Check available GLIBCXX versions
strings /usr/lib/arm-linux-gnueabihf/libstdc++.so.6 | grep GLIBCXX

# Check GLIBC version
ldd --version
```

#### Compatible Node.js Versions by Raspberry Pi OS

| Raspberry Pi OS Version | Max Node.js Version | GLIBCXX Available |
|------------------------|-------------------|------------------|
| Buster (10) | Node.js 16.x | 3.4.25 |
| Bullseye (11) | Node.js 18.x | 3.4.26 |
| Bookworm (12) | Node.js 20.x | 3.4.30+ |

#### Check Your Raspberry Pi OS Version
```bash
cat /etc/os-release
```

### Alternative Solutions

#### Update Raspberry Pi OS (Requires Internet)
```bash
# Update package lists
sudo apt update

# Upgrade system packages
sudo apt upgrade -y

# Upgrade to newer OS version (careful!)
# sudo apt full-upgrade
```

#### Install Compatible Node.js Manually
```bash
# For ARMv7 (Pi 2B+, 3, 4, Zero 2)
wget https://nodejs.org/dist/v18.19.1/node-v18.19.1-linux-armv7l.tar.xz
sudo tar -xf node-v18.19.1-linux-armv7l.tar.xz -C /usr/local --strip-components=1

# For ARMv6 (Pi Zero, Pi 1)
wget https://nodejs.org/dist/v16.20.2/node-v16.20.2-linux-armv6l.tar.xz
sudo tar -xf node-v16.20.2-linux-armv6l.tar.xz -C /usr/local --strip-components=1
```

### Prevention Tips

1. **Always check compatibility** before installing newer Node.js versions
2. **Use LTS versions** for better long-term compatibility
3. **Keep Raspberry Pi OS updated** for latest library support
4. **Test in development environment** before production deployment

### Hardware-Specific Notes

#### Raspberry Pi Zero / Pi 1 (ARMv6)
- Use Node.js v16.x maximum
- Download ARMv6 binaries specifically
- May need even older versions for very old OS

#### Raspberry Pi 2B+ / 3 / 4 / Zero 2 (ARMv7/v8)
- Can use Node.js v18.x on updated systems
- ARMv7 binaries work on ARMv8 systems
- v20+ requires very recent OS versions

### Testing Your Fix

#### Verify Node.js Installation
```bash
# Check version
node --version

# Test basic functionality
node -e "console.log('Node.js is working!')"

# Check npm
npm --version
```

#### Test Exit Gate Application
```bash
# Check service status
sudo systemctl status exit-gate

# View logs
sudo journalctl -u exit-gate -f

# Test application directly
cd /opt/exit-gate
node server.js
```

### Advanced Troubleshooting

#### If Node.js Still Doesn't Work

1. **Check architecture**:
   ```bash
   uname -m
   # Should be: armv7l, armv6l, or aarch64
   ```

2. **Verify downloaded binary matches architecture**:
   ```bash
   file /usr/local/bin/node
   ```

3. **Check library dependencies**:
   ```bash
   ldd /usr/local/bin/node
   ```

4. **Try even older Node.js version**:
   - Node.js v16.20.2 for maximum compatibility
   - Node.js v14.21.3 for very old systems

#### Create Custom Bundle with Specific Node.js Version

Modify the bundle creator script to use a specific version:

```powershell
# In simple-bundle-creator.ps1, change:
$nodeUrl = "https://nodejs.org/dist/v16.20.2/node-v16.20.2-linux-armv7l.tar.xz"
```

### Emergency Recovery

If you completely break Node.js installation:

```bash
# Remove everything
sudo rm -rf /usr/local/bin/node* /usr/local/bin/npm* /usr/local/lib/node_modules

# Install via package manager (may be older version)
sudo apt update
sudo apt install nodejs npm

# Or reinstall from known working bundle
```

---

## Summary

The GLIBCXX compatibility issue is resolved by:
1. **Using Node.js v18.19.1 instead of v20.x** (default in new bundles)
2. **Running the fix-compatibility.sh script** for automatic fixing
3. **Manually downgrading Node.js** if needed
4. **Updating Raspberry Pi OS** for newer Node.js support

The new offline installation bundles now include the compatible Node.js version by default, preventing this issue for most users.
