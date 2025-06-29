# Simple Exit Gate Bundle Creator
# Creates offline installation package without complex error handling

param(
    [string]$OutputName = "exit-gate-offline"
)

Write-Host "=== Simple Exit Gate Bundle Creator ===" -ForegroundColor Green

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$bundleName = "$OutputName-$timestamp"

Write-Host "Creating bundle: $bundleName" -ForegroundColor Yellow

# Clean up old bundles
Get-ChildItem -Directory -Name "*offline*" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Create bundle directory
New-Item -ItemType Directory -Path $bundleName -Force | Out-Null
Write-Host "Bundle directory created" -ForegroundColor Green

# Copy essential files
$essentialFiles = @(
    "package.json",
    "package-lock.json", 
    "server.js",
    ".env.example",
    "services",
    "routes",
    "public",
    "README.md",
    "install-offline.sh",
    "fix-line-endings.sh",
    "fix-compatibility.sh",
    "gpio-fix.sh",
    "gpio-troubleshoot.sh",
    "gpio-test.js",
    "gpio-permission-fix.sh",
    "gpio-simple-test.sh",
    "gpio-setup-exit-gate.sh",
    "gpio-test-exit-gate.sh",
    "gpio-manual-fix.sh",
    "install-quick-fix.sh",
    "install-gpio-packages.sh"
)

Write-Host "Copying application files..." -ForegroundColor Cyan
foreach ($file in $essentialFiles) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $bundleName -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "✓ $file" -ForegroundColor Green
    } else {
        Write-Host "⚠ $file not found" -ForegroundColor Yellow
    }
}

# Install and cache dependencies
Write-Host "`nCaching dependencies..." -ForegroundColor Cyan
Push-Location $bundleName

# Make sure we have package-lock.json
if (!(Test-Path "package-lock.json")) {
    Write-Host "Creating package-lock.json..." -ForegroundColor Yellow
    npm install --package-lock-only | Out-Null
}

# Create npm cache
$cacheDir = "npm-cache"
New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null

# Install dependencies
npm ci --cache $cacheDir | Out-Null
Write-Host "✓ Dependencies cached" -ForegroundColor Green

Pop-Location

# Download Node.js for ARM (using v18.19.1 for better Raspberry Pi compatibility)
Write-Host "`nDownloading Node.js ARM binary..." -ForegroundColor Cyan
$nodeUrl = "https://nodejs.org/dist/v18.19.1/node-v18.19.1-linux-armv7l.tar.xz"
$nodeFile = Join-Path $bundleName "node-v18.19.1-linux-armv7l.tar.xz"

try {
    Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeFile -UseBasicParsing
    Write-Host "✓ Node.js ARM binary downloaded" -ForegroundColor Green
} catch {
    Write-Host "⚠ Node.js download failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Create system packages list
Write-Host "`nCreating system packages list..." -ForegroundColor Cyan
$systemPackages = @(
    "build-essential",
    "python3-dev",
    "libasound2-dev", 
    "git",
    "curl",
    "wget"
)

$systemPackages | Out-File -FilePath (Join-Path $bundleName "system-packages.txt") -Encoding UTF8
Write-Host "✓ System packages list created" -ForegroundColor Green

# Create simple README
$readmeContent = @"
# Exit Gate Offline Installation

## Quick Install
1. Transfer this folder to Raspberry Pi
2. Run: chmod +x install-offline.sh
3. Run: sudo ./install-offline.sh

## Contents
- Complete Node.js application
- NPM dependencies cache
- Node.js ARM binary
- Installation scripts

## Notes
- No internet required for installation
- System packages may need to be installed separately
- GPIO pins 24 (gate) and 25 (LED) will be configured

Bundle created: $(Get-Date)
"@

$readmeContent | Out-File -FilePath (Join-Path $bundleName "INSTALL.md") -Encoding UTF8

# Create ZIP archive
Write-Host "`nCreating ZIP archive..." -ForegroundColor Cyan
$zipName = "$bundleName.zip"

if (Get-Command Compress-Archive -ErrorAction SilentlyContinue) {
    Compress-Archive -Path $bundleName -DestinationPath $zipName -Force
    $zipSize = [math]::Round((Get-Item $zipName).Length / 1MB, 1)
    Write-Host "✓ ZIP created: $zipName ($zipSize MB)" -ForegroundColor Green
}

# Calculate bundle size
$bundleSize = [math]::Round((Get-ChildItem $bundleName -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 1)

Write-Host "`n=== Bundle Creation Complete! ===" -ForegroundColor Green
Write-Host "Bundle folder: $bundleName ($bundleSize MB)" -ForegroundColor Yellow
if (Test-Path $zipName) {
    Write-Host "ZIP archive: $zipName" -ForegroundColor Yellow
}
Write-Host "`nTo install on Raspberry Pi:" -ForegroundColor Cyan
Write-Host "1. Transfer bundle to Pi" -ForegroundColor White
Write-Host "2. chmod +x install-offline.sh" -ForegroundColor White  
Write-Host "3. sudo ./install-offline.sh" -ForegroundColor White

Write-Host "`nBundle ready for offline installation! 🎉" -ForegroundColor Green
