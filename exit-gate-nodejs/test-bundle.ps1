# Simple test bundle creation script
param(
    [string]$OutputDir = ".\simple-bundle",
    [string]$AppName = "exit-gate-nodejs"
)

Write-Host "=== Simple Bundle Test ===" -ForegroundColor Green

# Create bundle directory 
$BundleDir = Join-Path $OutputDir $AppName
Write-Host "Creating bundle directory: $BundleDir" -ForegroundColor Yellow

if (Test-Path $OutputDir) {
    Remove-Item $OutputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $BundleDir -Force | Out-Null

Write-Host "Bundle directory created successfully: $BundleDir" -ForegroundColor Green

# Test file creation
$testFile = Join-Path $BundleDir "test.txt"
Write-Host "Creating test file: $testFile" -ForegroundColor Yellow

"Test content" | Out-File -FilePath $testFile -Encoding UTF8

if (Test-Path $testFile) {
    Write-Host "Test file created successfully" -ForegroundColor Green
} else {
    Write-Host "Test file creation failed" -ForegroundColor Red
}

# Test script creation 
$scriptPath = Join-Path $BundleDir "test-script.sh"
Write-Host "Creating test script: $scriptPath" -ForegroundColor Yellow

$scriptContent = @'
#!/bin/bash
echo "Test script works"
'@

try {
    $scriptContent | Out-File -FilePath $scriptPath -Encoding UTF8
    
    # Fix line endings
    $content = Get-Content $scriptPath -Raw
    $content = $content -replace "`r`n", "`n"
    [System.IO.File]::WriteAllText($scriptPath, $content, [System.Text.Encoding]::UTF8)
    
    Write-Host "Test script created successfully" -ForegroundColor Green
} catch {
    Write-Host "Error creating test script: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "=== Test Complete ===" -ForegroundColor Green
Write-Host "Bundle location: $BundleDir" -ForegroundColor Yellow
