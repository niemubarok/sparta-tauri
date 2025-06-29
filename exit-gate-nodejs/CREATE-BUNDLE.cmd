[Script Info]
Title=Exit Gate Offline Bundle Creator
Description=Creates offline installation bundle for Raspberry Pi
Author=Exit Gate Team
Version=1.0

[Variables]
BundleName=exit-gate-offline-bundle

echo "======================================"
echo "  Exit Gate Offline Bundle Creator"
echo "======================================"
echo ""
echo "This will create a complete offline installation"
echo "bundle for Raspberry Pi deployment."
echo ""
echo "Prerequisites:"
echo "- Node.js and NPM installed"
echo "- Internet connection for downloads"
echo "- PowerShell execution policy allows scripts"
echo ""

pause

echo "Starting bundle creation..."

if exist "quick-bundle.ps1" (
    echo "Running quick bundle script..."
    powershell -ExecutionPolicy Bypass -File "quick-bundle.ps1"
) else if exist "create-offline-bundle.ps1" (
    echo "Running main bundle script..."
    powershell -ExecutionPolicy Bypass -File "create-offline-bundle.ps1" -IncludeSystemPackages -Verbose
) else (
    echo "Error: Bundle scripts not found!"
    echo "Make sure you're in the correct directory."
    pause
    exit /b 1
)

echo ""
echo "Bundle creation completed!"
echo ""
echo "Next steps:"
echo "1. Find your bundle in the 'offline-bundle' folder"
echo "2. Copy the bundle folder to your Raspberry Pi"
echo "3. Run the installation script on Pi"
echo ""

pause
