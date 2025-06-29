# Build Exit Gate for Raspberry Pi 3 using WSL2
# Requires WSL2 with Ubuntu installed

param(
    [string]$WSLDistro = "Ubuntu-24.04"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Building Exit Gate for Raspberry Pi 3 (Windows) ===" -ForegroundColor Green

# Check if WSL2 is available
try {
    $wslCheck = wsl --list --verbose 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "WSL not found"
    }
    
    # Check if specified distro exists and start it
    $distroList = wsl --list --verbose
    # Clean up Unicode null characters from WSL output
    $cleanedDistroList = $distroList | ForEach-Object { $_ -replace '\0', '' }
    $distroExists = $cleanedDistroList | Where-Object { $_.Trim() -like "*$WSLDistro*" }
    if (-not $distroExists) {
        Write-Host "Available WSL distributions:" -ForegroundColor Yellow
        $cleanedDistroList | ForEach-Object { Write-Host $_ }
        throw "Specified distribution '$WSLDistro' not found."
    }
    
    # Ensure the distribution is running
    $distroStatus = $cleanedDistroList | Where-Object { $_.Trim() -like "*$WSLDistro*" }
    if ($distroStatus -match "Stopped") {
        Write-Host "Starting WSL distribution..." -ForegroundColor Yellow
        wsl --distribution $WSLDistro echo "WSL started" | Out-Null
    }
} catch {
    Write-Host "WSL2 is required for cross-compilation from Windows" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "Using WSL2 for cross-compilation..." -ForegroundColor Yellow

# Set WSL project path
$WSL_PROJECT_PATH = "/tmp/exit-gate-build"

try {
    # Clean and create WSL build directory
    Write-Host "Preparing WSL environment..." -ForegroundColor Yellow
    wsl --distribution $WSLDistro rm -rf $WSL_PROJECT_PATH
    wsl --distribution $WSLDistro mkdir -p $WSL_PROJECT_PATH

    # Copy project files to WSL
    Write-Host "Copying project files to WSL..." -ForegroundColor Yellow
    $currentPath = (Get-Location).Path
    # Convert Windows path to WSL path manually
    $drive = $currentPath.Substring(0, 1).ToLower()
    $restPath = $currentPath.Substring(3).Replace('\', '/')
    $wslPath = "/mnt/$drive/$restPath"
    
    # Copy files excluding node_modules, target, dist, .git
    wsl --distribution $WSLDistro bash -c "rsync -av --exclude='node_modules' --exclude='target' --exclude='dist' --exclude='.git' '$wslPath/' '$WSL_PROJECT_PATH/'"

    # Install dependencies step by step to avoid script issues
    Write-Host "Installing system dependencies..." -ForegroundColor Yellow
    wsl --distribution $WSLDistro sudo apt-get update
    wsl --distribution $WSLDistro sudo apt-get install -y gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf curl build-essential pkg-config
    
    # Install ARM-specific OpenSSL development packages
    Write-Host "Installing ARM OpenSSL development packages..." -ForegroundColor Yellow
    
    # Skip ARM package installation since Ubuntu repositories don't have ARM packages
    # We'll use vendored OpenSSL instead
    Write-Host "Skipping ARM package installation - using vendored OpenSSL for cross-compilation" -ForegroundColor Green

    # Install Node.js if needed
    Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
    $nodeCheck = wsl --distribution $WSLDistro bash -c "command -v node || echo 'NOT_FOUND'"
    if ($nodeCheck -eq "NOT_FOUND") {
        Write-Host "Installing Node.js..." -ForegroundColor Yellow
        wsl --distribution $WSLDistro bash -c "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
        wsl --distribution $WSLDistro sudo apt-get install -y nodejs
    }

    # Install pnpm if needed
    $pnpmCheck = wsl --distribution $WSLDistro bash -c "command -v pnpm || echo 'NOT_FOUND'"
    if ($pnpmCheck -eq "NOT_FOUND") {
        Write-Host "Installing pnpm..." -ForegroundColor Yellow
        wsl --distribution $WSLDistro npm install -g pnpm
    }

    # Install Rust if needed
    Write-Host "Checking Rust installation..." -ForegroundColor Yellow
    $rustCheck = wsl --distribution $WSLDistro bash -c "command -v rustc || echo 'NOT_FOUND'"
    if ($rustCheck -eq "NOT_FOUND") {
        Write-Host "Installing Rust..." -ForegroundColor Yellow
        wsl --distribution $WSLDistro bash -c "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y"
    }

    # Setup Rust environment and add target
    Write-Host "Setting up Rust for cross-compilation..." -ForegroundColor Yellow
    wsl --distribution $WSLDistro bash -c "source ~/.cargo/env && rustup target add armv7-unknown-linux-gnueabihf"

    # Create Cargo config
    Write-Host "Creating Cargo configuration..." -ForegroundColor Yellow
    wsl --distribution $WSLDistro mkdir -p "$WSL_PROJECT_PATH/src-tauri/.cargo"
    $cargoConfig = @"
[target.armv7-unknown-linux-gnueabihf]
linker = "arm-linux-gnueabihf-gcc"

[env]
CC_armv7_unknown_linux_gnueabihf = "arm-linux-gnueabihf-gcc"
CXX_armv7_unknown_linux_gnueabihf = "arm-linux-gnueabihf-g++"
AR_armv7_unknown_linux_gnueabihf = "arm-linux-gnueabihf-ar"
PKG_CONFIG_ALLOW_CROSS = "1"
"@
    $cargoConfig | wsl --distribution $WSLDistro tee "$WSL_PROJECT_PATH/src-tauri/.cargo/config.toml" | Out-Null

    # Build frontend
    Write-Host "Building frontend..." -ForegroundColor Yellow
    wsl --distribution $WSLDistro bash -c "cd '$WSL_PROJECT_PATH' && pnpm install"
    wsl --distribution $WSLDistro bash -c "cd '$WSL_PROJECT_PATH' && pnpm build"

    # Build Tauri application
    Write-Host "Building Tauri application for Raspberry Pi..." -ForegroundColor Yellow
    wsl --distribution $WSLDistro bash -c "cd '$WSL_PROJECT_PATH/src-tauri' && source ~/.cargo/env && export CC_armv7_unknown_linux_gnueabihf=arm-linux-gnueabihf-gcc && export CXX_armv7_unknown_linux_gnueabihf=arm-linux-gnueabihf-g++ && export AR_armv7_unknown_linux_gnueabihf=arm-linux-gnueabihf-ar && export CARGO_TARGET_ARMV7_UNKNOWN_LINUX_GNUEABIHF_LINKER=arm-linux-gnueabihf-gcc && export PKG_CONFIG_ALLOW_CROSS=1 && cargo build --target armv7-unknown-linux-gnueabihf --release"

    # Copy binary back to Windows
    Write-Host "Copying binary back to Windows..." -ForegroundColor Yellow
    if (!(Test-Path "dist")) {
        New-Item -ItemType Directory -Path "dist" | Out-Null
    }

    # Create temporary file on Windows side
    $tempFile = [System.IO.Path]::GetTempFileName() + "-exit-gate-rpi"
    # Convert Windows path to WSL path manually
    $drive = $tempFile.Substring(0, 1).ToLower()
    $restPath = $tempFile.Substring(3).Replace('\', '/')
    $tempWslPath = "/mnt/$drive/$restPath"
    
    wsl --distribution $WSLDistro cp "$WSL_PROJECT_PATH/src-tauri/target/armv7-unknown-linux-gnueabihf/release/exit-gate" "$tempWslPath"
    Move-Item $tempFile "dist/exit-gate-rpi" -Force

    Write-Host "=== Build completed ===" -ForegroundColor Green
    Write-Host "Binary location: dist/exit-gate-rpi" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To deploy to Raspberry Pi:" -ForegroundColor Yellow
    Write-Host "1. Copy to Pi: scp dist/exit-gate-rpi pi@your-pi-ip:~/" -ForegroundColor White
    Write-Host "2. SSH to Pi and make executable: chmod +x ~/exit-gate-rpi" -ForegroundColor White
    Write-Host "3. Install deps on Pi: sudo apt-get install -y libc6 libgcc1 libstdc++6" -ForegroundColor White
    Write-Host "4. Run: ./exit-gate-rpi" -ForegroundColor White

} catch {
    Write-Host "Build failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
}
