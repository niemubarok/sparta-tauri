#!/bin/bash

# Create necessary directories
sudo mkdir -p /etc/nixos
sudo mkdir -p /opt/spartakuler/{server,alpr,client}

# Copy NixOS configurations
sudo cp -r nix/* /etc/nixos/

# Enable buildx for ARM support
docker buildx create --use
docker buildx inspect --bootstrap

# Build applications using Docker with ARM platform
docker buildx build --platform linux/arm64 -f Dockerfile.build -t spartakuler-builds --load .

# Copy build artifacts
docker cp spartakuler-builds:/app/server/build /opt/spartakuler/server/
docker cp spartakuler-builds:/app/alpr /opt/spartakuler/
docker cp spartakuler-builds:/app/client/dist /opt/spartakuler/client/

# Add Raspberry Pi specific optimizations
export RUSTFLAGS="-C target-cpu=cortex-a53"
export TARGET_CC=aarch64-linux-gnu-gcc

# Set permissions
sudo chown -R spartakuler:spartakuler /opt/spartakuler

# Build and switch to new NixOS configuration
sudo nixos-rebuild switch --target-host aarch64-linux