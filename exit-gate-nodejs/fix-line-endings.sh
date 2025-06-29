#!/bin/bash
# Fix Line Endings for Scripts Transferred from Windows

echo "=== Exit Gate Line Ending Fixer ==="
echo "Fixing Windows line endings (CRLF) to Unix (LF)..."

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to fix line endings
fix_line_endings() {
    local file="$1"
    if [ -f "$file" ]; then
        # Check if file has Windows line endings
        if file "$file" | grep -q "CRLF"; then
            echo "Fixing line endings in: $file"
            # Use sed to remove carriage returns
            sed -i 's/\r$//' "$file"
            # Make executable if it's a shell script
            if [[ "$file" == *.sh ]]; then
                chmod +x "$file"
                echo "Made executable: $file"
            fi
        else
            echo "Already has correct line endings: $file"
            # Still make executable if it's a shell script
            if [[ "$file" == *.sh ]]; then
                chmod +x "$file"
            fi
        fi
    else
        echo "File not found: $file"
    fi
}

# List of script files to fix
SCRIPT_FILES=(
    "install-offline.sh"
    "download-system-packages.sh"
    "test-gpio.sh"
    "setup-gpio.sh"
)

echo ""
echo "Checking and fixing script files..."

for script in "${SCRIPT_FILES[@]}"; do
    fix_line_endings "$script"
done

# Also fix any other .sh files in the directory
echo ""
echo "Checking for other shell scripts..."
for script in *.sh; do
    if [ -f "$script" ]; then
        fix_line_endings "$script"
    fi
done

echo ""
echo "=== Fix completed! ==="
echo ""
echo "You can now run the installation:"
echo "  sudo ./install-offline.sh"
echo ""
