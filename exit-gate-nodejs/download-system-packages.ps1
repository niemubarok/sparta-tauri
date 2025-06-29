# Pre-download System Packages for Raspberry Pi
# This script downloads .deb packages that can be installed offline

param(
    [string]$OutputDir = ".\system-packages-predownload",
    [string]$Architecture = "armhf",
    [switch]$UseDocker
)

Write-Host "=== System Packages Pre-downloader ===" -ForegroundColor Green
Write-Host "Downloading .deb packages for offline Pi installation..." -ForegroundColor Yellow

# Create output directory
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Required packages for Exit Gate
$RequiredPackages = @(
    "build-essential",
    "python3-dev", 
    "libasound2-dev",
    "git",
    "curl",
    "wget",
    "unzip",
    "gcc",
    "g++",
    "make",
    "libc6-dev",
    "pkg-config"
)

if ($UseDocker) {
    Write-Host "Using Docker to download ARM packages..." -ForegroundColor Cyan
    
    # Create a temporary Dockerfile
    $DockerContent = @"
FROM arm32v7/debian:bullseye
RUN apt-get update
RUN mkdir -p /downloads
WORKDIR /downloads
"@
    
    foreach ($pkg in $RequiredPackages) {
        $DockerContent += "RUN apt-get download $pkg || true`n"
    }
    
    $DockerContent | Out-File -FilePath "Dockerfile.pkgdownload" -Encoding ASCII
    
    try {
        # Build and run container
        Write-Host "Building download container..." -ForegroundColor Yellow
        docker build -f Dockerfile.pkgdownload -t pkg-downloader .
        
        Write-Host "Downloading packages..." -ForegroundColor Yellow
        docker run --rm -v "${PWD}/${OutputDir}:/output" pkg-downloader /bin/bash -c "cp *.deb /output/ 2>/dev/null || echo 'Some packages not found'"
        
        # Cleanup
        Remove-Item "Dockerfile.pkgdownload" -Force
        docker rmi pkg-downloader -f
        
        Write-Host "Packages downloaded to: $OutputDir" -ForegroundColor Green
        
    } catch {
        Write-Host "Docker method failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Try without -UseDocker or install Docker" -ForegroundColor Yellow
    }
    
} else {
    Write-Host "Manual download method..." -ForegroundColor Cyan
    Write-Host "Note: This downloads x86 packages, not ARM packages" -ForegroundColor Yellow
    Write-Host "For ARM packages, use -UseDocker or download on actual Pi" -ForegroundColor Yellow
    
    # Create script for manual execution on Pi
    $PiDownloadScript = @"
#!/bin/bash
# Run this script on Raspberry Pi with internet connection

echo "=== Downloading ARM packages for offline installation ==="

mkdir -p system-packages
cd system-packages

PACKAGES=($(($RequiredPackages | ForEach-Object { "    `"$_`"" }) -join "`n"))

echo "Updating package lists..."
apt-get update

for package in `"`${PACKAGES[@]}`"; do
    echo "Downloading: `$package"
    apt-get download "`$package" 2>/dev/null || echo "Warning: Could not download `$package"
done

echo ""
echo "Download completed!"
echo "Files: `$(ls *.deb 2>/dev/null | wc -l) .deb packages"
echo ""
echo "Copy this 'system-packages' folder to your offline Pi"
echo "The install-offline.sh script will use these packages automatically"
"@

    $PiDownloadScript | Out-File -FilePath (Join-Path $OutputDir "download-on-pi.sh") -Encoding UTF8
    
    # Fix line endings for Linux
    $scriptContent = Get-Content (Join-Path $OutputDir "download-on-pi.sh") -Raw
    $scriptContent = $scriptContent -replace "`r`n", "`n"
    [System.IO.File]::WriteAllText((Join-Path $OutputDir "download-on-pi.sh"), $scriptContent, [System.Text.Encoding]::UTF8)
    
    # Create package list file
    $RequiredPackages | Out-File -FilePath (Join-Path $OutputDir "required-packages.txt") -Encoding UTF8
    
    Write-Host "Created download script for Pi: download-on-pi.sh" -ForegroundColor Green
    Write-Host "Transfer this script to a Pi with internet and run it" -ForegroundColor Yellow
}

# Create instructions
$Instructions = @"
# System Packages Pre-download Instructions

## Method 1: Download on Connected Pi (Recommended)

1. Copy 'download-on-pi.sh' to a Raspberry Pi with internet
2. Run: chmod +x download-on-pi.sh && ./download-on-pi.sh  
3. Copy the generated 'system-packages' folder to your offline bundle

## Method 2: Docker ARM Emulation (Advanced)

Run this script with -UseDocker flag:
``````powershell
.\download-system-packages.ps1 -UseDocker
``````

## Method 3: Manual Download

Visit https://packages.debian.org/bullseye/ and manually download:
$(($RequiredPackages | ForEach-Object { "- $_" }) -join "`n")

## Integration with Bundle

1. Create your offline bundle normally
2. Add the downloaded .deb files to bundle/system-packages/ folder
3. The install-offline.sh will automatically use them

## Package List

Required packages for Exit Gate:
$(($RequiredPackages | ForEach-Object { "- $_" }) -join "`n")

These packages enable:
- Node.js native module compilation
- Audio system support  
- GPIO access libraries
- Development tools
"@

$Instructions | Out-File -FilePath (Join-Path $OutputDir "README.md") -Encoding UTF8

Write-Host "`n=== Pre-download Setup Complete ===" -ForegroundColor Green
Write-Host "Output directory: $OutputDir" -ForegroundColor Yellow
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Use download-on-pi.sh on a connected Pi, OR" -ForegroundColor White
Write-Host "2. Run this script with -UseDocker for ARM packages" -ForegroundColor White
Write-Host "3. Add downloaded packages to your offline bundle" -ForegroundColor White
