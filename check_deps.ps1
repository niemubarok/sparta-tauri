# PowerShell script untuk memeriksa dependensi
$dllsRequired = @(
    "python310.dll",
    "vcruntime140.dll",
    "msvcp140.dll",
    "WebView2Loader.dll"
)

foreach ($dll in $dllsRequired) {
    $path = Join-Path -Path $PSScriptRoot -ChildPath $dll
    if (Test-Path $path) {
        Write-Host "$dll - OK" -ForegroundColor Green
    } else {
        Write-Host "$dll - MISSING" -ForegroundColor Red
    }
}