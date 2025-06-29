# Exit Gate Offline Bundle Creator for Windows
# Creates a complete offline installation package for Raspberry Pi

param(
    [string]$OutputDir = ".\offline-bundle",
    [string]$AppName = "exit-gate-nodejs",
    [switch]$IncludeSystemPackages,
    [switch]$Verbose
)

Write-Host "=== Exit Gate Offline Bundle Creator ===" -ForegroundColor Green
Write-Host "Creating offline installation bundle..." -ForegroundColor Yellow

# Create output directory
if (Test-Path $OutputDir) {
    Remove-Item $OutputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

$BundleDir = Join-Path $OutputDir $AppName
New-Item -ItemType Directory -Path $BundleDir -Force | Out-Null

# Function to log messages
function Write-Log {
    param([string]$Message, [string]$Color = "White")
    if ($Verbose) {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor $Color
    }
}

try {
    # 1. Copy application files
    Write-Host "1. Copying application files..." -ForegroundColor Cyan
    Write-Log "Copying source files" "Green"
    
    $AppFiles = @(
        "package.json",
        "package-lock.json",
        "server.js",
        ".env.example",
        "services",
        "routes", 
        "public",
        "README.md",
        "SETUP.md",
        "IMPLEMENTATION.md",
        ".gitignore"
    )
    
    foreach ($file in $AppFiles) {
        if (Test-Path $file) {
            # Skip if it's a bundle output directory
            if ($file -like "offline-bundle*" -or $file -like "test-bundle*" -or $file -like "simple-bundle*") {
                Write-Log "Skipping bundle directory: $file" "Yellow"
                continue
            }
            
            if (Test-Path $file -PathType Container) {
                Copy-Item $file -Destination $BundleDir -Recurse -Force
                Write-Log "Copied directory: $file" "Green"
            } else {
                Copy-Item $file -Destination $BundleDir -Force
                Write-Log "Copied file: $file" "Green"
            }
        } else {
            Write-Log "Warning: $file not found" "Yellow"
        }
    }

    # 2. Download Node.js dependencies
    Write-Host "2. Downloading Node.js dependencies..." -ForegroundColor Cyan
    
    # Create npm cache directory
    $NpmCacheDir = Join-Path $BundleDir "npm-cache"
    New-Item -ItemType Directory -Path $NpmCacheDir -Force | Out-Null
    
    # Download all dependencies with npm pack
    Write-Log "Downloading npm packages..." "Green"
    
    Push-Location $BundleDir
    try {
        # Check if package-lock.json exists, if not create it
        if (!(Test-Path "package-lock.json")) {
            Write-Log "package-lock.json not found, running npm install first" "Yellow"
            npm install --cache $NpmCacheDir
        } else {
            # Install dependencies and create cache
            npm ci --cache $NpmCacheDir
        }
        
        # Create offline package cache
        npm pack --pack-destination $NpmCacheDir 2>$null
        
        # Get all dependencies and pack them
        $packageJson = Get-Content "package.json" | ConvertFrom-Json
        
        if ($packageJson.dependencies) {
            foreach ($dep in $packageJson.dependencies.PSObject.Properties) {
                $pkgName = $dep.Name
                Write-Log "Packing dependency: $pkgName" "Green"
                npm pack $pkgName --pack-destination $NpmCacheDir 2>$null
            }
        }
        
        if ($packageJson.devDependencies) {
            foreach ($dep in $packageJson.devDependencies.PSObject.Properties) {
                $pkgName = $dep.Name
                Write-Log "Packing dev dependency: $pkgName" "Green"
                npm pack $pkgName --pack-destination $NpmCacheDir 2>$null
            }
        }
        
    } finally {
        Pop-Location
    }

    # 3. Download Node.js binary for ARM
    Write-Host "3. Downloading Node.js ARM binary..." -ForegroundColor Cyan
    
    $NodeVersion = "v20.11.0"
    $NodeArm = "node-$NodeVersion-linux-armv7l"
    $NodeUrl = "https://nodejs.org/dist/$NodeVersion/$NodeArm.tar.xz"
    $NodeFile = Join-Path $BundleDir "$NodeArm.tar.xz"
    
    Write-Log "Downloading Node.js ARM binary..." "Green"
    try {
        Invoke-WebRequest -Uri $NodeUrl -OutFile $NodeFile -UseBasicParsing
        Write-Log "Node.js ARM binary downloaded successfully" "Green"
    } catch {
        Write-Log "Warning: Failed to download Node.js ARM binary: $($_.Exception.Message)" "Yellow"
    }

    # 4. Create system packages list (always include)
    Write-Host "4. Creating system packages information..." -ForegroundColor Cyan
    
    $SystemPackages = @(
        "build-essential",
        "python3-dev",
        "libasound2-dev",
        "git",
        "curl",
        "wget",
        "unzip"
    )
    
    $SystemPackages | Out-File -FilePath (Join-Path $BundleDir "system-packages.txt") -Encoding UTF8
    Write-Log "System packages list created" "Green"
    
    # Create system packages download script
    $SystemDownloadScript = @'
#!/bin/bash
# System Package Downloader - Run this on Pi with internet

echo "=== Downloading System Packages for Offline Installation ==="
echo "Run this script on a Raspberry Pi with internet connection"
echo "Then copy the downloaded packages to your offline Pi"
echo ""

# Create download directory
mkdir -p system-packages
cd system-packages

echo "Downloading required packages..."

# Required packages
PACKAGES=(
    "build-essential"
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
    "pkg-config"
)

# Download packages with dependencies
for package in "${PACKAGES[@]}"; do
    echo "Downloading: $package"
    apt-get download "$package" 2>/dev/null || echo "Warning: Could not download $package"
    
    # Download immediate dependencies
    apt-cache depends "$package" | grep "Depends:" | sed 's/.*Depends: //' | head -10 | while read dep; do
        if [[ "$dep" != *"|"* ]] && [[ "$dep" != *"<"* ]] && [[ "$dep" != *">"* ]]; then
            apt-get download "$dep" 2>/dev/null || true
        fi
    done
done

echo ""
echo "Download completed!"
echo "Files downloaded: $(ls -1 *.deb 2>/dev/null | wc -l)"
echo ""
echo "To use offline:"
echo "1. Copy this 'system-packages' folder to your offline Pi"
echo "2. In the offline installer, these .deb files will be used automatically"
'@

    # Create system packages download script
    $downloadScriptPath = Join-Path $BundleDir "download-system-packages.sh"
    $SystemDownloadScript | Out-File -FilePath $downloadScriptPath -Encoding UTF8
    
    # Fix line endings for Linux compatibility
    if (Test-Path $downloadScriptPath) {
        $scriptContent = Get-Content $downloadScriptPath -Raw
        $scriptContent = $scriptContent -replace "`r`n", "`n"
        [System.IO.File]::WriteAllText($downloadScriptPath, $scriptContent, [System.Text.Encoding]::UTF8)
        Write-Log "System packages download script created with Unix line endings" "Green"
    }
    
    Write-Log "System packages download script created" "Green"

    # 5. Create installation scripts
    Write-Host "5. Creating installation scripts..." -ForegroundColor Cyan
    
    # Create offline installer script
    $OfflineInstaller = @'
#!/bin/bash
# Exit Gate Offline Installer for Raspberry Pi

set -e

APP_NAME="exit-gate-nodejs"
INSTALL_DIR="/opt/$APP_NAME"
SERVICE_NAME="exit-gate"
USER="pi"

echo "=== Exit Gate Offline Installer ==="
echo "Installing from offline bundle..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Install system packages if available
if [ -f "system-packages.txt" ]; then
    echo "Installing system packages..."
    # Note: This requires internet connection
    # For truly offline installation, these packages need to be pre-installed
    # or downloaded as .deb files
    apt update
    xargs -a system-packages.txt apt install -y
fi

# Install Node.js from bundle
if [ -f "node-v*.tar.xz" ]; then
    echo "Installing Node.js from bundle..."
    NODE_ARCHIVE=$(ls node-v*.tar.xz | head -1)
    tar -xf "$NODE_ARCHIVE" -C /usr/local --strip-components=1
    
    # Verify Node.js installation
    if ! command -v node &> /dev/null; then
        echo "Error: Node.js installation failed"
        exit 1
    fi
    
    echo "Node.js version: $(node --version)"
    echo "NPM version: $(npm --version)"
else
    echo "Warning: Node.js bundle not found, assuming Node.js is already installed"
fi

# Create application directory
echo "Creating application directory..."
mkdir -p "$INSTALL_DIR"
chown "$USER:$USER" "$INSTALL_DIR"

# Copy application files
echo "Copying application files..."
cp -r package.json package-lock.json server.js services routes public "$INSTALL_DIR/"

# Copy environment file
if [ -f ".env.example" ]; then
    cp ".env.example" "$INSTALL_DIR/.env"
fi

# Copy documentation
if [ -f "README.md" ]; then cp "README.md" "$INSTALL_DIR/"; fi
if [ -f "SETUP.md" ]; then cp "SETUP.md" "$INSTALL_DIR/"; fi
if [ -f "IMPLEMENTATION.md" ]; then cp "IMPLEMENTATION.md" "$INSTALL_DIR/"; fi

# Install npm dependencies from cache
echo "Installing npm dependencies from cache..."
cd "$INSTALL_DIR"

# Use local npm cache if available
if [ -d "$SCRIPT_DIR/npm-cache" ]; then
    export NPM_CONFIG_CACHE="$SCRIPT_DIR/npm-cache"
    npm ci --offline --no-audit
else
    echo "Warning: NPM cache not found, installing online..."
    npm ci --no-audit
fi

# Set permissions
chown -R "$USER:$USER" "$INSTALL_DIR"

# Create systemd service
echo "Creating systemd service..."
cat > "/etc/systemd/system/$SERVICE_NAME.service" << 'EOF'
[Unit]
Description=Exit Gate Node.js Application
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/exit-gate-nodejs
ExecStart=/usr/local/bin/node server.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"

echo ""
echo "=== Installation completed successfully! ==="
echo ""
echo "Next steps:"
echo "1. Edit configuration: sudo nano $INSTALL_DIR/.env"
echo "2. Start the service: sudo systemctl start $SERVICE_NAME"
echo "3. Check status: sudo systemctl status $SERVICE_NAME"
echo "4. View logs: sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "Web interface will be available at: http://localhost:3000"
echo ""
'@

    # Create line ending fixer script
    $fixerScriptPath = Join-Path $BundleDir "fix-line-endings.sh"
    if (Test-Path "$PSScriptRoot\fix-line-endings.sh") {
        $LineEndingFixer = Get-Content "$PSScriptRoot\fix-line-endings.sh" -Raw
        # Fix line endings for the fixer script itself
        $LineEndingFixer = $LineEndingFixer -replace "`r`n", "`n"
        [System.IO.File]::WriteAllText($fixerScriptPath, $LineEndingFixer, [System.Text.Encoding]::UTF8)
        Write-Log "Line ending fixer script included" "Green"
    }
    
    # Copy actual install-offline.sh file if it exists
    $installScriptPath = Join-Path $BundleDir "install-offline.sh"
    if (Test-Path "$PSScriptRoot\install-offline.sh") {
        $installScript = Get-Content "$PSScriptRoot\install-offline.sh" -Raw
        # Fix line endings
        $installScript = $installScript -replace "`r`n", "`n"
        [System.IO.File]::WriteAllText($installScriptPath, $installScript, [System.Text.Encoding]::UTF8)
        Write-Log "install-offline.sh copied with fixed line endings" "Green"
    }
    
    # Create Windows batch installer for testing
    $WindowsInstaller = @'
@echo off
echo === Exit Gate Offline Test Installer (Windows) ===
echo This installer is for testing on Windows only
echo For production, use install-offline.sh on Raspberry Pi
echo.

cd /d "%~dp0"

if not exist "package.json" (
    echo Error: package.json not found
    pause
    exit /b 1
)

echo Installing npm dependencies from cache...
if exist "npm-cache" (
    set NPM_CONFIG_CACHE=%CD%\npm-cache
    npm ci --offline --no-audit
) else (
    echo Warning: NPM cache not found, installing online...
    npm ci --no-audit
)

if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo Created .env file from .env.example
    )
)

echo.
echo Installation completed!
echo.
echo To start the application:
echo   npm start
echo.
echo Web interface: http://localhost:3000
echo.
pause
'@

    $WindowsInstaller | Out-File -FilePath (Join-Path $BundleDir "install-test-windows.bat") -Encoding ASCII

    # 6. Create bundle info file
    Write-Host "6. Creating bundle information..." -ForegroundColor Cyan
    
    $BundleInfo = @{
        "created" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "creator" = $env:USERNAME
        "machine" = $env:COMPUTERNAME
        "app_name" = $AppName
        "node_version" = $NodeVersion
        "npm_version" = if (Get-Command npm -ErrorAction SilentlyContinue) { (npm --version) } else { "unknown" }
        "bundle_size" = "calculated_after_creation"
        "files_included" = $AppFiles
        "installation_notes" = @(
            "1. Transfer this entire folder to Raspberry Pi",
            "2. Run: chmod +x install-offline.sh",
            "3. Run: sudo ./install-offline.sh",
            "4. Configure .env file as needed",
            "5. Start service: sudo systemctl start exit-gate"
        )
    }
    
    $BundleInfo | ConvertTo-Json -Depth 3 | Out-File -FilePath (Join-Path $BundleDir "bundle-info.json") -Encoding UTF8

    # 7. Create README for bundle
    $BundleReadme = @"
# Exit Gate Offline Installation Bundle

This bundle contains everything needed to install the Exit Gate application on a Raspberry Pi **WITHOUT internet connection**.

## 🚨 TRULY OFFLINE INSTALLATION

This installer does NOT require internet connection. All dependencies are bundled.

## Contents

- **Application files**: Complete Node.js application
- **NPM dependencies**: All required packages cached locally  
- **Node.js binary**: ARM-compatible Node.js runtime
- **Installation scripts**: Automated setup scripts
- **System packages**: Download script for .deb files

## For COMPLETELY Offline Installation

### Option 1: Basic Installation (Assumes build tools exist)
If the target Pi already has build-essential, python3-dev, etc:

1. Transfer this folder to Raspberry Pi
2. Run: ``chmod +x install-offline.sh``
3. Run: ``sudo ./install-offline.sh``

### Option 2: Complete Offline (Download system packages first)
For a Pi that has NEVER been connected to internet:

**Step A: On a Pi WITH internet (same model):**
```bash
chmod +x download-system-packages.sh
./download-system-packages.sh
```

**Step B: Copy system-packages folder to offline Pi**

**Step C: Install on offline Pi:**
```bash
chmod +x install-offline.sh  
sudo ./install-offline.sh
```

## What Gets Installed

- Node.js $NodeVersion (from bundle, no internet needed)
- NPM dependencies (from cache, no internet needed)
- System packages (from .deb files if provided)
- GPIO permissions setup
- Systemd service configuration

## No Internet Required After Setup

- ✅ Node.js runtime: Bundled
- ✅ NPM packages: Cached locally
- ✅ Application code: Complete bundle
- ✅ System packages: Downloaded .deb files (optional)

"@

    $BundleReadme | Out-File -FilePath (Join-Path $BundleDir "README-BUNDLE.md") -Encoding UTF8

    # 8. Calculate bundle size
    Write-Host "7. Calculating bundle size..." -ForegroundColor Cyan
    
    $BundleSize = (Get-ChildItem $BundleDir -Recurse | Measure-Object -Property Length -Sum).Sum
    $BundleSizeMB = [math]::Round($BundleSize / 1MB, 2)
    
    # Update bundle info with size
    $BundleInfoContent = Get-Content (Join-Path $BundleDir "bundle-info.json") | ConvertFrom-Json
    $BundleInfoContent.bundle_size = "$BundleSizeMB MB"
    $BundleInfoContent | ConvertTo-Json -Depth 3 | Out-File -FilePath (Join-Path $BundleDir "bundle-info.json") -Encoding UTF8

    # 9. Create ZIP archive
    Write-Host "8. Creating ZIP archive..." -ForegroundColor Cyan
    
    $ZipPath = Join-Path $OutputDir "$AppName-offline-bundle.zip"
    
    if (Get-Command Compress-Archive -ErrorAction SilentlyContinue) {
        Compress-Archive -Path $BundleDir -DestinationPath $ZipPath -Force
        Write-Log "ZIP archive created: $ZipPath" "Green"
    } else {
        Write-Log "Warning: Compress-Archive not available, ZIP not created" "Yellow"
    }

    # 10. Success message
    Write-Host ""
    Write-Host "=== Bundle Creation Completed Successfully! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Bundle location: $BundleDir" -ForegroundColor Yellow
    Write-Host "Bundle size: $BundleSizeMB MB" -ForegroundColor Yellow
    if (Test-Path $ZipPath) {
        Write-Host "ZIP archive: $ZipPath" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "To install on Raspberry Pi:" -ForegroundColor Cyan
    Write-Host "1. Transfer the bundle folder to Raspberry Pi" -ForegroundColor White
    Write-Host "2. Run: chmod +x install-offline.sh" -ForegroundColor White
    Write-Host "3. Run: sudo ./install-offline.sh" -ForegroundColor White
    Write-Host ""
    Write-Host "For testing on Windows:" -ForegroundColor Cyan
    Write-Host "1. Navigate to bundle folder" -ForegroundColor White
    Write-Host "2. Run: install-test-windows.bat" -ForegroundColor White
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "=== Error during bundle creation ===" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    exit 1
}
