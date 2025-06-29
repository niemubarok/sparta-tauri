param(
    [string]$PiIP = "192.168.10.51",
    [string]$PiUser = "pi"
)

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

Write-Host "🔧 SSH Connection Troubleshoot for Raspberry Pi" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Target: $PiUser@$PiIP"
Write-Host ""

# 1. Test network connectivity
Write-Status "1. Testing network connectivity..."
try {
    $ping = Test-Connection -ComputerName $PiIP -Count 3 -Quiet
    if ($ping) {
        Write-Success "✅ Network ping successful"
    } else {
        Write-Error "❌ Network ping failed"
        Write-Status "Possible issues:"
        Write-Status "- Pi is not powered on"
        Write-Status "- Wrong IP address"
        Write-Status "- Network connectivity issues"
        Write-Status "- Pi is on different network/VLAN"
    }
} catch {
    Write-Warning "⚠️ Ping test inconclusive: $($_.Exception.Message)"
}

# 2. Check SSH tools
Write-Status "2. Checking SSH tools..."
$sshPath = Get-Command ssh -ErrorAction SilentlyContinue
if ($sshPath) {
    Write-Success "✅ SSH found at: $($sshPath.Source)"
    
    # Check SSH version
    try {
        $sshVersion = ssh -V 2>&1
        Write-Status "SSH Version: $sshVersion"
    } catch {
        Write-Warning "Cannot get SSH version"
    }
} else {
    Write-Error "❌ SSH command not found"
    Write-Status "Install options:"
    Write-Status "1. Windows Settings > Apps > Optional Features > OpenSSH Client"
    Write-Status "2. Git for Windows (includes SSH)"
    Write-Status "3. WSL (Windows Subsystem for Linux)"
}

# 3. Test SSH with verbose output
Write-Status "3. Testing SSH connection with verbose output..."
Write-Status "Attempting connection to $PiUser@$PiIP..."

try {
    # Test with verbose mode to see what's happening
    Write-Status "Running: ssh -v -o ConnectTimeout=10 $PiUser@$PiIP 'echo Connection successful'"
    $sshVerbose = ssh -v -o ConnectTimeout=10 "$PiUser@$PiIP" "echo 'Connection successful'" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✅ SSH connection successful!"
    } else {
        Write-Error "❌ SSH connection failed"
        Write-Status "SSH output:"
        $sshVerbose | ForEach-Object { Write-Host "  $_" }
    }
} catch {
    Write-Error "SSH command failed: $($_.Exception.Message)"
}

# 4. Check for SSH keys
Write-Status "4. Checking SSH key configuration..."
$sshDir = "$env:USERPROFILE\.ssh"
if (Test-Path $sshDir) {
    Write-Success "✅ SSH directory exists: $sshDir"
    
    # Check for common key files
    $keyFiles = @("id_rsa", "id_ed25519", "id_ecdsa")
    $foundKeys = @()
    
    foreach ($keyFile in $keyFiles) {
        $keyPath = Join-Path $sshDir $keyFile
        if (Test-Path $keyPath) {
            $foundKeys += $keyFile
            Write-Success "  ✅ Found key: $keyFile"
        }
    }
    
    if ($foundKeys.Count -eq 0) {
        Write-Warning "⚠️ No SSH keys found"
        Write-Status "To generate SSH key:"
        Write-Status "  ssh-keygen -t ed25519 -C 'your-email@example.com'"
    }
    
    # Check known_hosts
    $knownHosts = Join-Path $sshDir "known_hosts"
    if (Test-Path $knownHosts) {
        Write-Success "✅ known_hosts file exists"
        
        # Check if Pi is in known_hosts
        $hostsContent = Get-Content $knownHosts -ErrorAction SilentlyContinue
        if ($hostsContent -match $PiIP) {
            Write-Success "  ✅ Pi IP found in known_hosts"
        } else {
            Write-Warning "  ⚠️ Pi IP not found in known_hosts (first connection?)"
        }
    } else {
        Write-Warning "⚠️ known_hosts file not found"
    }
    
} else {
    Write-Warning "⚠️ SSH directory not found: $sshDir"
    Write-Status "This is normal for first-time SSH usage"
}

# 5. Test different SSH connection methods
Write-Status "5. Testing different connection methods..."

# Method 1: Interactive (password)
Write-Status "Method 1: Interactive authentication"
try {
    Write-Status "Running: ssh -o PreferredAuthentications=password $PiUser@$PiIP 'whoami'"
    $sshPassword = ssh -o PreferredAuthentications=password -o ConnectTimeout=10 "$PiUser@$PiIP" "whoami" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✅ Password authentication works"
    } else {
        Write-Warning "⚠️ Password authentication failed or not available"
    }
} catch {
    Write-Warning "Password authentication test failed: $($_.Exception.Message)"
}

# Method 2: Key-based
Write-Status "Method 2: Key-based authentication"
try {
    $sshKey = ssh -o PreferredAuthentications=publickey -o BatchMode=yes -o ConnectTimeout=10 "$PiUser@$PiIP" "whoami" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✅ Key-based authentication works"
    } else {
        Write-Warning "⚠️ Key-based authentication failed"
        Write-Status "To setup key-based auth:"
        Write-Status "1. Generate key: ssh-keygen -t ed25519"
        Write-Status "2. Copy to Pi: ssh-copy-id $PiUser@$PiIP"
    }
} catch {
    Write-Warning "Key-based authentication test failed: $($_.Exception.Message)"
}

# 6. Common solutions
Write-Host ""
Write-Host "🔧 Common Solutions:" -ForegroundColor Yellow
Write-Host "==================="
Write-Host "1. Enable SSH on Raspberry Pi:"
Write-Host "   sudo systemctl enable ssh"
Write-Host "   sudo systemctl start ssh"
Write-Host ""
Write-Host "2. Check Pi's SSH configuration:"
Write-Host "   sudo nano /etc/ssh/sshd_config"
Write-Host "   # Ensure these lines are present:"
Write-Host "   PermitRootLogin yes"
Write-Host "   PasswordAuthentication yes"
Write-Host "   PubkeyAuthentication yes"
Write-Host ""
Write-Host "3. Find Pi's actual IP address:"
Write-Host "   # On Pi:"
Write-Host "   hostname -I"
Write-Host "   ip addr show"
Write-Host ""
Write-Host "   # From Windows:"
Write-Host "   arp -a | findstr b8-27-eb"
Write-Host "   nmap -sn 192.168.1.0/24"
Write-Host ""
Write-Host "4. Test from Pi side:"
Write-Host "   # Check if SSH service is running:"
Write-Host "   sudo systemctl status ssh"
Write-Host "   # Check SSH logs:"
Write-Host "   sudo journalctl -u ssh -f"
Write-Host ""
Write-Host "5. Windows firewall:"
Write-Host "   # Allow SSH through Windows firewall"
Write-Host "   # Or temporarily disable firewall for testing"

Write-Host ""
Write-Status "💡 Quick test commands:"
Write-Host "# Test SSH manually:"
Write-Host "ssh -v $PiUser@$PiIP"
Write-Host ""
Write-Host "# Test with password only:"
Write-Host "ssh -o PreferredAuthentications=password $PiUser@$PiIP"
Write-Host ""
Write-Host "# Test file copy:"
Write-Host "echo 'test' > test.txt"
Write-Host "scp test.txt $PiUser@$PiIP`:~/"
Write-Host "ssh $PiUser@$PiIP 'cat ~/test.txt && rm ~/test.txt'"

Write-Host ""
Write-Success "🎯 Troubleshooting completed!"
Write-Status "If SSH still doesn't work, check Pi's SSH service and network configuration."
