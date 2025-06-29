#!/bin/bash
# Run this script on Raspberry Pi with internet connection

echo "=== Downloading ARM packages for offline installation ==="

mkdir -p system-packages
cd system-packages

PACKAGES=(    "build-essential"
    "python3-dev"
    "libasound2-dev"
    "git"
    "curl"
    "wget"
    "unzip"
    "gcc"
    "g++"
    "make"
    "libc6-dev"
    "pkg-config")

echo "Updating package lists..."
apt-get update

for package in "${PACKAGES[@]}"; do
    echo "Downloading: $package"
    apt-get download "$package" 2>/dev/null || echo "Warning: Could not download $package"
done

echo ""
echo "Download completed!"
echo "Files: $(ls *.deb 2>/dev/null | wc -l) .deb packages"
echo ""
echo "Copy this 'system-packages' folder to your offline Pi"
echo "The install-offline.sh script will use these packages automatically"
