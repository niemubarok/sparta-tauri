# System Packages Pre-download Instructions

## Method 1: Download on Connected Pi (Recommended)

1. Copy 'download-on-pi.sh' to a Raspberry Pi with internet
2. Run: chmod +x download-on-pi.sh && ./download-on-pi.sh  
3. Copy the generated 'system-packages' folder to your offline bundle

## Method 2: Docker ARM Emulation (Advanced)

Run this script with -UseDocker flag:
```powershell
.\download-system-packages.ps1 -UseDocker
```

## Method 3: Manual Download

Visit https://packages.debian.org/bullseye/ and manually download:
- build-essential
- python3-dev
- libasound2-dev
- git
- curl
- wget
- unzip
- gcc
- g++
- make
- libc6-dev
- pkg-config

## Integration with Bundle

1. Create your offline bundle normally
2. Add the downloaded .deb files to bundle/system-packages/ folder
3. The install-offline.sh will automatically use them

## Package List

Required packages for Exit Gate:
- build-essential
- python3-dev
- libasound2-dev
- git
- curl
- wget
- unzip
- gcc
- g++
- make
- libc6-dev
- pkg-config

These packages enable:
- Node.js native module compilation
- Audio system support  
- GPIO access libraries
- Development tools
