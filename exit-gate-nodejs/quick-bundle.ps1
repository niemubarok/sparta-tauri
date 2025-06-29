# Quick Bundle Creator - Simplified version
# Creates offline bundle with predefined settings

Write-Host "=== Quick Offline Bundle Creator ===" -ForegroundColor Green
Write-Host "Creating offline bundle with default settings..." -ForegroundColor Yellow

# Set default parameters
$OutputDir = "offline-bundle-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$AppName = "exit-gate-nodejs"

Write-Host "`nBundle will be created in: $OutputDir" -ForegroundColor Cyan

try {
    # Run the main bundling script with default parameters
    .\create-offline-bundle.ps1 -OutputDir $OutputDir -IncludeSystemPackages -Verbose
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n=== Quick Bundle Creation Successful! ===" -ForegroundColor Green
        Write-Host "`nYour offline bundle is ready at: $OutputDir\$AppName" -ForegroundColor Yellow
        Write-Host "`nTo install on Raspberry Pi:" -ForegroundColor Cyan
        Write-Host "1. Copy the '$AppName' folder to your Pi" -ForegroundColor White
        Write-Host "2. Run: chmod +x install-offline.sh" -ForegroundColor White  
        Write-Host "3. Run: sudo ./install-offline.sh" -ForegroundColor White
        Write-Host ""
        
        # Ask if user wants to open the bundle folder
        $openFolder = Read-Host "Open bundle folder now? (y/n)"
        if ($openFolder -eq 'y' -or $openFolder -eq 'Y') {
            if (Test-Path "$OutputDir\$AppName") {
                Start-Process explorer.exe -ArgumentList "$OutputDir\$AppName"
            }
        }
    }
} catch {
    Write-Host "`n=== Bundle Creation Failed ===" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "`nTry running the full script manually:" -ForegroundColor Yellow
    Write-Host ".\create-offline-bundle.ps1 -OutputDir '$OutputDir' -Verbose" -ForegroundColor White
}

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
