#!/bin/bash

# Test script for Raspberry Pi deployment
# Run this on the Raspberry Pi to test GPIO and system functionality

echo "=== Exit Gate System Test for Raspberry Pi ==="

# Check system info
echo "System Information:"
echo "Raspberry Pi Model: $(cat /proc/device-tree/model 2>/dev/null || echo 'Unknown')"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"
echo ""

# Check dependencies
echo "Checking Dependencies:"
deps=("libc6" "libgcc1" "libstdc++6")
for dep in "${deps[@]}"; do
    if dpkg -l | grep -q "^ii.*$dep "; then
        echo "✓ $dep installed"
    else
        echo "✗ $dep missing - run: sudo apt-get install $dep"
    fi
done
echo ""

# Check GPIO permissions
echo "Checking GPIO Permissions:"
if groups | grep -q gpio; then
    echo "✓ User is in gpio group"
else
    echo "✗ User not in gpio group - run: sudo usermod -a -G gpio $USER"
fi

if [ -w /dev/gpiomem ]; then
    echo "✓ GPIO memory accessible"
else
    echo "✗ GPIO memory not accessible"
fi
echo ""

# Check if exit-gate binary exists
echo "Checking Exit Gate Binary:"
if [ -f "./exit-gate" ]; then
    echo "✓ exit-gate binary found"
    echo "File size: $(ls -lh ./exit-gate | awk '{print $5}')"
    echo "Permissions: $(ls -l ./exit-gate | awk '{print $1}')"
    
    # Check if executable
    if [ -x "./exit-gate" ]; then
        echo "✓ Binary is executable"
    else
        echo "✗ Binary not executable - run: chmod +x ./exit-gate"
    fi
else
    echo "✗ exit-gate binary not found"
    echo "Copy from build machine: scp dist/exit-gate-rpi pi@$(hostname -I | awk '{print $1}'):~/exit-gate"
fi
echo ""

# Test GPIO pins (if binary exists)
if [ -f "./exit-gate" ] && [ -x "./exit-gate" ]; then
    echo "Testing GPIO functionality:"
    echo "This will be handled by the exit-gate application"
    echo "Run: ./exit-gate to start the application"
else
    echo "Cannot test GPIO - binary not ready"
fi
echo ""

# Memory and performance info
echo "System Resources:"
echo "Memory: $(free -h | awk '/^Mem:/ {print $2 " total, " $7 " available"}')"
echo "CPU: $(nproc) cores, $(cat /proc/cpuinfo | grep "cpu MHz" | head -1 | awk '{print $4}') MHz"
echo "Disk: $(df -h / | awk 'NR==2 {print $4 " available"}')"
echo ""

# Network info
echo "Network Configuration:"
echo "IP Address: $(hostname -I | awk '{print $1}')"
echo "Hostname: $(hostname)"
echo ""

echo "=== Test Complete ==="
echo ""
echo "Next steps:"
echo "1. Fix any missing dependencies or permissions"
echo "2. Run: ./exit-gate to start the application"
echo "3. Check logs for any runtime issues"
