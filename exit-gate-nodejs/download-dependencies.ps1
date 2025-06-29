# Manual Dependency Downloader for Offline Installation
# This script helps download specific packages when automatic bundling fails

param(
    [string]$OutputDir = ".\manual-downloads",
    [string[]]$Packages = @(),
    [string]$Platform = "linux-armv7l",
    [switch]$DownloadNode,
    [string]$NodeVersion = "v20.11.0"
)

Write-Host "=== Manual Dependency Downloader ===" -ForegroundColor Green

# Create output directory
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Function to download with retry
function Get-FileWithRetry {
    param(
        [string]$Url,
        [string]$OutputPath,
        [int]$MaxRetries = 3
    )
    
    for ($i = 1; $i -le $MaxRetries; $i++) {
        try {
            Write-Host "Downloading: $Url (Attempt $i/$MaxRetries)"
            Invoke-WebRequest -Uri $Url -OutFile $OutputPath -UseBasicParsing
            Write-Host "✓ Downloaded successfully" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
            if ($i -eq $MaxRetries) {
                return $false
            }
            Start-Sleep -Seconds 2
        }
    }
    return $false
}

# Download Node.js if requested
if ($DownloadNode) {
    Write-Host "`n1. Downloading Node.js for $Platform..." -ForegroundColor Cyan
    
    $NodeArm = "node-$NodeVersion-linux-armv7l"
    $NodeUrl = "https://nodejs.org/dist/$NodeVersion/$NodeArm.tar.xz"
    $NodeFile = Join-Path $OutputDir "$NodeArm.tar.xz"
    
    if (Get-FileWithRetry -Url $NodeUrl -OutputPath $NodeFile) {
        Write-Host "Node.js downloaded: $NodeFile" -ForegroundColor Green
    } else {
        Write-Host "Failed to download Node.js" -ForegroundColor Red
    }
}

# Download specific npm packages
if ($Packages.Count -gt 0) {
    Write-Host "`n2. Downloading NPM packages..." -ForegroundColor Cyan
    
    $PackageDir = Join-Path $OutputDir "npm-packages"
    if (!(Test-Path $PackageDir)) {
        New-Item -ItemType Directory -Path $PackageDir -Force | Out-Null
    }
    
    foreach ($package in $Packages) {
        Write-Host "Processing package: $package" -ForegroundColor Yellow
        
        try {
            # Use npm pack to download package
            npm pack $package --pack-destination $PackageDir 2>&1 | Out-Null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Package $package downloaded" -ForegroundColor Green
            } else {
                Write-Host "✗ Failed to download $package" -ForegroundColor Red
            }
        } catch {
            Write-Host "✗ Error downloading $package : $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# Download system dependencies information
Write-Host "`n3. Creating system dependencies list..." -ForegroundColor Cyan

$SystemDeps = @{
    "required_packages" = @(
        "build-essential",
        "python3-dev", 
        "libasound2-dev",
        "git",
        "curl",
        "wget"
    )
    "optional_packages" = @(
        "vim",
        "htop",
        "tree",
        "unzip"
    )
    "gpio_packages" = @(
        "raspi-gpio",
        "wiringpi"
    )
    "download_commands" = @{
        "debian_packages" = "apt download package-name"
        "manual_download" = "wget http://archive.raspbian.org/raspbian/pool/main/..."
    }
    "installation_notes" = @(
        "For offline installation of system packages:",
        "1. On a connected Pi, run: apt download package-name",
        "2. Copy .deb files to offline Pi",
        "3. Install with: sudo dpkg -i *.deb",
        "4. Fix dependencies: sudo apt-get install -f"
    )
}

$SystemDeps | ConvertTo-Json -Depth 3 | Out-File -FilePath (Join-Path $OutputDir "system-dependencies.json") -Encoding UTF8

# Create download script for system packages
$DownloadScript = @'
#!/bin/bash
# System Package Downloader for Raspberry Pi
# Run this on a Pi with internet connection

DOWNLOAD_DIR="./system-packages"
mkdir -p "$DOWNLOAD_DIR"

echo "Downloading system packages..."

# Required packages
PACKAGES=(
    "build-essential"
    "python3-dev"
    "libasound2-dev" 
    "git"
    "curl"
    "wget"
    "unzip"
)

cd "$DOWNLOAD_DIR"

for package in "${PACKAGES[@]}"; do
    echo "Downloading $package..."
    apt download "$package" 2>/dev/null || echo "Failed to download $package"
done

echo "Download completed. Files saved in: $DOWNLOAD_DIR"
echo ""
echo "To install offline:"
echo "1. Copy this folder to offline Pi"
echo "2. Run: sudo dpkg -i *.deb"
echo "3. Fix dependencies: sudo apt-get install -f"
'@

$DownloadScript | Out-File -FilePath (Join-Path $OutputDir "download-system-packages.sh") -Encoding UTF8

# Create usage instructions
$Instructions = @"
# Manual Dependency Download Instructions

This directory contains manually downloaded dependencies for offline installation.

## Contents

- **Node.js**: ARM-compatible Node.js runtime
- **NPM Packages**: Individual package files
- **System Dependencies**: Information about required system packages

## Usage

### For Node.js
1. Copy the Node.js .tar.xz file to Raspberry Pi
2. Extract: `tar -xf node-*.tar.xz -C /usr/local --strip-components=1`

### For NPM Packages
1. Copy npm-packages folder to Raspberry Pi
2. In your project directory: `npm install ./path/to/package.tgz`

### For System Packages
1. Use the download-system-packages.sh script on a connected Pi
2. Copy the downloaded .deb files to offline Pi
3. Install: `sudo dpkg -i *.deb`

## Common Packages for Exit Gate

If automatic bundling failed, you can manually download these packages:

```powershell
.\download-dependencies.ps1 -Packages @(
    "express",
    "socket.io", 
    "pouchdb-node",
    "raspi-gpio",
    "rpi-gpio",
    "node-speaker",
    "cors",
    "helmet",
    "compression"
) -DownloadNode
```

## Troubleshooting

- If npm pack fails, check your internet connection
- Some packages may require compilation on the target platform
- For GPIO packages, consider downloading pre-compiled versions

"@

$Instructions | Out-File -FilePath (Join-Path $OutputDir "README.md") -Encoding UTF8

Write-Host "`n=== Manual Download Setup Complete ===" -ForegroundColor Green
Write-Host "Output directory: $OutputDir" -ForegroundColor Yellow
Write-Host "`nTo download common packages for Exit Gate:" -ForegroundColor Cyan
Write-Host ".\download-dependencies.ps1 -Packages @('express','socket.io','pouchdb-node','raspi-gpio') -DownloadNode" -ForegroundColor White
