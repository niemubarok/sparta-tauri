# PowerShell script to install Python 3.10, VC_redist_X64, and MicrosoftEdgeWebView2RuntimeInstallerX64
# Run as Administrator

$ErrorActionPreference = 'Stop'

# URLs for installers
$pythonUrl = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
$vcRedistUrl = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
$webview2Url = "https://msedge.sf.dl.delivery.mp.microsoft.com/filestreamingservice/files/2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2/MicrosoftEdgeWebView2RuntimeInstallerX64.exe"

# Check if Python 3.10 is installed
$pythonInstalled = $false
try {
    $ver = python --version 2>&1
    if ($ver -match '3.10') { $pythonInstalled = $true }
} catch {}
if (-not $pythonInstalled) {
    Write-Host "Downloading Python 3.10..."
    Invoke-WebRequest -Uri $pythonUrl -OutFile "python-3.10.11-amd64.exe"
    Write-Host "Installing Python 3.10..."
    Start-Process -Wait -FilePath "python-3.10.11-amd64.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1"
} else {
    Write-Host "Python 3.10 already installed. Skipping Python install."
}

# Check if VC_redist_X64 is installed
$vcRedistInstalled = Test-Path "HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64"
if (-not $vcRedistInstalled) {
    Write-Host "Downloading VC_redist_X64..."
    Invoke-WebRequest -Uri $vcRedistUrl -OutFile "vc_redist.x64.exe"
    Write-Host "Installing VC_redist_X64..."
    Start-Process -Wait -FilePath "vc_redist.x64.exe" -ArgumentList "/install /quiet /norestart"
} else {
    Write-Host "VC_redist_X64 already installed. Skipping VC_redist install."
}

# Check if WebView2 Runtime is installed (per Microsoft docs)
$webview2Guid = "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
$webview2Installed = $false

$locations = @(
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\$webview2Guid",
    "HKCU:\Software\Microsoft\EdgeUpdate\Clients\$webview2Guid",
    "HKLM:\SOFTWARE\Microsoft\EdgeUpdate\Clients\$webview2Guid"
)
foreach ($loc in $locations) {
    try {
        $pv = (Get-ItemProperty -Path $loc -Name pv -ErrorAction Stop).pv
        if ($pv -and $pv -ne "0.0.0.0") { $webview2Installed = $true }
    } catch {}
}

if (-not $webview2Installed) {
    Write-Host "Downloading MicrosoftEdgeWebView2RuntimeInstallerX64..."
    Invoke-WebRequest -Uri $webview2Url -OutFile "MicrosoftEdgeWebView2RuntimeInstallerX64.exe"
    Write-Host "Installing MicrosoftEdgeWebView2RuntimeInstallerX64..."
    Start-Process -Wait -FilePath "MicrosoftEdgeWebView2RuntimeInstallerX64.exe" -ArgumentList "/silent /install"
} else {
    Write-Host "MicrosoftEdgeWebView2Runtime already installed. Skipping WebView2 install."
}

Write-Host "All dependencies installed."

# Install pip if not available, then install fast-alpr
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    $pipAvailable = $false
    try { python -m pip --version *>$null; if ($LASTEXITCODE -eq 0) { $pipAvailable = $true } } catch {}
    if (-not $pipAvailable) {
        Write-Host "pip not found, trying to install pip with ensurepip..."
        try { python -m ensurepip --upgrade *>$null } catch {}
        try { python -m pip --version *>$null; if ($LASTEXITCODE -eq 0) { $pipAvailable = $true } } catch {}
    }
    if (-not $pipAvailable) {
        Write-Host "ensurepip failed or pip still not available, downloading get-pip.py..."
        $getPipUrl = "https://bootstrap.pypa.io/get-pip.py"
        Invoke-WebRequest -Uri $getPipUrl -OutFile "get-pip.py"
        try { python get-pip.py } catch {}
        try { python -m pip --version *>$null; if ($LASTEXITCODE -eq 0) { $pipAvailable = $true } } catch {}
    }
    if (-not $pipAvailable) {
        Write-Host "pip still not available after get-pip.py. Please check your Python installation. Skipping fast-alpr check/install."
        return
    }
    $fastalpr = $null
    try { $fastalpr = python -m pip show fast-alpr 2>$null } catch {}
    if ($fastalpr) {
        Write-Host "fast-alpr already installed. Skipping fast-alpr install."
    } else {
        Write-Host "Installing fast-alpr with pip..."
        python -m pip install --upgrade pip
        python -m pip install fast-alpr
    }

    # Inisialisasi fast-alpr agar model otomatis terdownload
    Write-Host "Inisialisasi fast-alpr agar model otomatis terdownload..."
    try {
        python -c "import fast_alpr; alpr = fast_alpr.ALPR(detector_model='yolo-v9-t-384-license-plate-end2end', ocr_model='global-plates-mobile-vit-v2-model'); import numpy as np; from PIL import Image; dummy = np.zeros((1,1,3), dtype=np.uint8); Image.fromarray(dummy).save('alpr_dummy.jpg'); alpr.predict('alpr_dummy.jpg'); print('fast-alpr model download/init done')"
        Remove-Item -Force alpr_dummy.jpg -ErrorAction SilentlyContinue
    } catch {
        Write-Host "GAGAL inisialisasi fast-alpr"
        pause
    }
} else {
    Write-Host "Python not found in PATH. Please restart your terminal or add Python to PATH."
}
