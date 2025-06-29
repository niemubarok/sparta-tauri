param(
    [string]$PiIP = "192.168.10.51",
    [string]$PiUser = "pi",
    [string]$RemoteDir = "/home/pi/sparta-exit-gate"
)

$ErrorActionPreference = "Stop"

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-Status($Message) {
    Write-Host "${Blue}[INFO]${Reset} $Message"
}

function Write-Success($Message) {
    Write-Host "${Green}[SUCCESS]${Reset} $Message"
}

function Write-Warning($Message) {
    Write-Host "${Yellow}[WARNING]${Reset} $Message"
}

function Write-Error($Message) {
    Write-Host "${Red}[ERROR]${Reset} $Message"
}

function Test-NetworkConnection($Target) {
    Write-Status "Testing network connectivity to $Target..."
    try {
        $ping = Test-Connection -ComputerName $Target -Count 2 -Quiet
        if ($ping) {
            Write-Success "Network connection to $Target is successful"
            return $true
        } else {
            Write-Warning "Network ping to $Target failed"
            return $false
        }
    } catch {
        Write-Warning "Cannot test network connection: $($_.Exception.Message)"
        return $false
    }
}

Write-Host "🚀 Copying Exit Gate Project from Windows to Raspberry Pi" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "Source: $(Get-Location)"
Write-Host "Target: $PiUser@$PiIP`:$RemoteDir"
Write-Host ""

# Show debug information
Write-Status "Debug Information:"
Write-Host "- PowerShell Version: $($PSVersionTable.PSVersion)"
Write-Host "- OS: $($PSVersionTable.OS)"
Write-Host "- Current User: $($env:USERNAME)"
Write-Host ""

# Check if we're in the correct directory
if (-not (Test-Path "package.json") -or -not (Test-Path "src-tauri")) {
    Write-Error "This script must be run from the exit-gate directory!"
    Write-Status "Current directory: $(Get-Location)"
    Write-Status "Please run this script from: \path\to\spartakuler\exit-gate\"
    exit 1
}

# Check for required tools
Write-Status "Checking required tools..."

$missingTools = @()

# Check for ssh
if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) {
    $missingTools += "ssh"
}

# Check for scp
if (-not (Get-Command scp -ErrorAction SilentlyContinue)) {
    $missingTools += "scp"
}

if ($missingTools.Count -gt 0) {
    Write-Error "Missing required tools: $($missingTools -join ', ')"
    Write-Status "Please install:"
    Write-Status "- OpenSSH for Windows (Windows 10/11 optional feature)"
    Write-Status "- Or Git for Windows (includes SSH tools)"
    Write-Status "- Or WSL (Windows Subsystem for Linux)"
    exit 1
}

Write-Success "All required tools are available"

# Test network connectivity first
Test-NetworkConnection $PiIP

# Test SSH connection
Write-Status "Testing SSH connection to $PiUser@$PiIP..."

# First try with BatchMode to check if key-based auth works
$sshTestBatch = ssh -o ConnectTimeout=10 -o BatchMode=yes "$PiUser@$PiIP" "exit" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Success "SSH connection successful (key-based authentication)"
} else {
    Write-Warning "Key-based authentication failed, trying interactive connection..."
    
    # Try interactive connection (allows password input)
    Write-Status "Please enter your password when prompted..."
    $sshTestInteractive = ssh -o ConnectTimeout=10 "$PiUser@$PiIP" "exit"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "SSH connection successful (password authentication)"
    } else {
        Write-Error "SSH connection failed!"
        Write-Status "Please ensure:"
        Write-Status "1. Raspberry Pi is powered on and connected to network"
        Write-Status "2. SSH is enabled on the Pi (sudo systemctl enable ssh)"
        Write-Status "3. IP address $PiIP is correct"
        Write-Status "4. Username '$PiUser' is correct"
        Write-Status ""
        Write-Status "To setup SSH key authentication (recommended):"
        Write-Status "  ssh-keygen -t rsa"
        Write-Status "  ssh-copy-id $PiUser@$PiIP"
        Write-Status ""
        
        $continue = Read-Host "Do you want to continue anyway? (y/N)"
        if ($continue -notmatch "^[Yy]") {
            exit 1
        } else {
            Write-Warning "Continuing without SSH verification..."
        }
    }
}

# Create remote directory
Write-Status "Creating remote directory structure..."
ssh "$PiUser@$PiIP" "mkdir -p $RemoteDir"

# Create temporary directory for selective copying
$tempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }
Write-Status "Creating temporary copy at: $tempDir"

# Directories to copy (essential for build only)
$dirsToCopy = @("src", "src-tauri", "public")

# Files to copy (build configuration files only)
$filesToCopy = @(
    "package.json",
    "pnpm-lock.yaml", 
    "quasar.config.ts",
    "tsconfig.json",
    "postcss.config.cjs",
    "unocss.config.ts",
    "eslint.config.mjs",
    "index.html"
)

# Folders/files to explicitly skip (for reference)
$skipPatterns = @(
    "node_modules",     # Will be installed by pnpm
    "target",          # Rust build artifacts 
    "dist",            # Quasar build output
    ".quasar",         # Quasar temp files
    ".git",            # Version control
    ".vscode",         # Editor settings
    ".github",         # GitHub workflows
    "*.log",           # Log files
    "*.tmp",           # Temporary files
    "deploy-*",        # Previous deployments
    "parkir_awal.sql", # Database schema (not needed for build)
    "*.xlsx",          # Excel files (not needed for build)
    "scripts"          # Optional scripts folder
)

Write-Status "Skipping unnecessary files/folders: $($skipPatterns -join ', ')"

# Copy directories
foreach ($dir in $dirsToCopy) {
    if (Test-Path $dir) {
        Write-Status "Copying directory: $dir"
        Copy-Item -Path $dir -Destination $tempDir -Recurse
    }
}

# Copy files
foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Write-Status "Copying file: $file"
        Copy-Item -Path $file -Destination $tempDir
    }
}

# Copy shell scripts
Get-ChildItem -Path "*.sh" | ForEach-Object {
    Write-Status "Copying script: $($_.Name)"
    Copy-Item -Path $_.FullName -Destination $tempDir
}

# Copy markdown files
Get-ChildItem -Path "*.md" | ForEach-Object {
    Write-Status "Copying documentation: $($_.Name)"
    Copy-Item -Path $_.FullName -Destination $tempDir
}

# Upload to Pi using scp
Write-Status "Uploading to Raspberry Pi..."
Write-Status "Please enter your password if prompted..."

try {
    scp -r "$tempDir\*" "$PiUser@$PiIP`:$RemoteDir/"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Project files copied successfully!"
    } else {
        throw "SCP transfer failed with exit code $LASTEXITCODE"
    }
} catch {
    Write-Error "Failed to copy project files!"
    Write-Status "Error: $($_.Exception.Message)"
    Write-Status "Please check:"
    Write-Status "1. SSH connection is working: ssh $PiUser@$PiIP"
    Write-Status "2. Target directory permissions on Pi"
    Write-Status "3. Available disk space on Pi"
    Remove-Item -Path $tempDir -Recurse -Force
    exit 1
}

# Cleanup temp directory
Remove-Item -Path $tempDir -Recurse -Force

# Skip copying additional files - not needed for build
Write-Status "Skipping database files (not needed for build process)..."
Write-Status "• parkir_awal.sql - will be handled by application setup"
Write-Status "• master parkir.xlsx - not required for build"

# Setup scripts on Pi
Write-Status "Setting up scripts on Raspberry Pi..."

# Make scripts executable
ssh "$PiUser@$PiIP" @"
cd $RemoteDir
chmod +x *.sh 2>/dev/null || true
echo 'Scripts made executable'
"@

# Create environment setup script
Write-Status "Creating environment setup script..."
$setupScript = @'
#!/bin/bash

set -e

echo '🔧 Setting up Exit Gate development environment on Raspberry Pi'
echo '============================================================='

# Update system
echo '📦 Updating system packages...'
sudo apt-get update

# Install basic development tools
echo '🛠️ Installing development tools...'
sudo apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    pkg-config \
    libssl-dev

# Install Tauri dependencies
echo '📱 Installing Tauri dependencies...'
sudo apt-get install -y \
    libgtk-3-dev \
    libwebkit2gtk-4.0-dev \
    libappindicator3-dev \
    librsvg2-dev \
    libdbus-1-dev \
    libudev-dev

# Install multimedia dependencies
echo '🎬 Installing multimedia dependencies...'
sudo apt-get install -y \
    libv4l-dev \
    v4l-utils \
    ffmpeg

# Install Node.js if not present
if ! command -v node &> /dev/null; then
    echo '📦 Installing Node.js...'
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo '✅ Node.js already installed: $(node --version)'
fi

# Install pnpm if not present
if ! command -v pnpm &> /dev/null; then
    echo '📦 Installing pnpm...'
    npm install -g pnpm
else
    echo '✅ pnpm already installed: $(pnpm --version)'
fi

# Install Rust if not present
if ! command -v rustc &> /dev/null; then
    echo '🦀 Installing Rust...'
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
else
    echo '✅ Rust already installed: $(rustc --version)'
fi

# Install Tauri CLI
echo '🔧 Installing Tauri CLI...'
source ~/.cargo/env 2>/dev/null || true
cargo install tauri-cli --locked

echo '✅ Environment setup completed!'
echo '🚀 You can now run: ./quick-build.sh'
'@

ssh "$PiUser@$PiIP" "cat > $RemoteDir/setup-environment.sh << 'EOF'
$setupScript
EOF"

# Create quick build script
$buildScript = @'
#!/bin/bash

set -e

echo '🚀 Quick build for Exit Gate System'
echo '=================================='

cd $(dirname "$0")

# Check environment
if ! command -v pnpm &> /dev/null || ! command -v cargo &> /dev/null; then
    echo '⚠️ Development environment not set up!'
    echo 'Run: ./setup-environment.sh'
    exit 1
fi

source ~/.cargo/env 2>/dev/null || true
export NODE_OPTIONS="--max-old-space-size=2048"

ARCH=$(uname -m)
if [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
    export RUSTFLAGS="-C target-cpu=cortex-a72"
elif [[ "$ARCH" == "armv7l" ]]; then
    export RUSTFLAGS="-C target-cpu=cortex-a53"
fi

echo '📦 Installing dependencies...'
pnpm install

echo '🏗️ Building Exit Gate System...'
pnpm tauri build --verbose

if [[ $? -eq 0 ]]; then
    echo '✅ Build completed successfully!'
    ls -la src-tauri/target/release/tauri-quasar 2>/dev/null || echo 'Binary location may vary'
else
    echo '❌ Build failed!'
    exit 1
fi
'@

ssh "$PiUser@$PiIP" "cat > $RemoteDir/quick-build.sh << 'EOF'
$buildScript
EOF"

# Make scripts executable
ssh "$PiUser@$PiIP" "cd $RemoteDir && chmod +x setup-environment.sh quick-build.sh"

# Verify copy
Write-Status "Verifying copied files on Pi..."
ssh "$PiUser@$PiIP" "cd $RemoteDir && ls -la"

# Show success and next steps
Write-Host ""
Write-Success "Exit Gate project copied successfully from Windows to Raspberry Pi!"
Write-Host "=================================================================="
Write-Status "Project location on Pi: $RemoteDir"
Write-Host ""
Write-Status "Files copied for build:"
Write-Host "✅ Source code (src/, src-tauri/)"
Write-Host "✅ Static assets (public/)"
Write-Host "✅ Build configuration (package.json, quasar.config.ts, etc.)"
Write-Host "✅ Essential shell scripts (*.sh)"
Write-Host "✅ Documentation (*.md)"
Write-Host ""
Write-Status "Files skipped (not needed for build):"
Write-Host "⏭️ node_modules/ (will be installed via pnpm)"
Write-Host "⏭️ target/ (Rust build artifacts)"
Write-Host "⏭️ dist/ (Quasar build output)"
Write-Host "⏭️ .git/, .vscode/ (development files)"
Write-Host "⏭️ Database files (parkir_awal.sql, *.xlsx)"
Write-Host ""
Write-Status "Next steps:"
Write-Host "1. Connect to Pi: ssh $PiUser@$PiIP"
Write-Host "2. Go to project: cd $RemoteDir"
Write-Host "3. Setup environment: ./setup-environment.sh"
Write-Host "4. Build project: ./quick-build.sh"
Write-Host ""

# Optional auto-setup
$autoSetup = Read-Host "Do you want to automatically run environment setup on Pi now? (y/N)"
if ($autoSetup -match "^[Yy]") {
    Write-Status "Running environment setup on Pi..."
    ssh "$PiUser@$PiIP" "cd $RemoteDir && ./setup-environment.sh"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Environment setup completed!"
        Write-Status "You can now build the project on the Pi."
    } else {
        Write-Warning "Environment setup had some issues. Please check manually."
    }
}

Write-Host ""
Write-Success "🎉 Copy and setup process completed!"