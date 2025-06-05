#!/bin/bash

# Install dependencies for cross-compilation
sudo apt-get update
sudo apt-get install -y gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

# Set up rust target for ARM64
rustup target add aarch64-unknown-linux-gnu

# Build frontend
cd tauri
pnpm install
pnpm build

# Build Tauri application for ARM64
cd src-tauri
cargo build --target aarch64-unknown-linux-gnu --release

# The binary will be in target/aarch64-unknown-linux-gnu/release/
