# Building Exit Gate for Raspberry Pi 3

## Prerequisites

### For Linux Host:
```bash
# Install cross-compilation tools
sudo apt-get update
sudo apt-get install -y gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf

# Add Rust target
rustup target add armv7-unknown-linux-gnueabihf
```

### For Windows Host:
- Install WSL2 with Ubuntu
- Run the build script in WSL2 environment

## Building

### Option 1: Linux/WSL2
```bash
# Make script executable
chmod +x build-rpi.sh

# Run build
./build-rpi.sh
```

### Option 2: Windows (uses WSL2)
```cmd
build-rpi.cmd
```

## Deployment

### Manual Deploy
```bash
# Copy binary to Pi
scp src-tauri/target/armv7-unknown-linux-gnueabihf/release/exit-gate pi@your-pi-ip:~/

# SSH to Pi and setup
ssh pi@your-pi-ip
chmod +x ~/exit-gate
sudo apt-get install -y libc6 libgcc1 libstdc++6
./exit-gate
```

### Automated Deploy
```bash
chmod +x deploy-to-pi.sh
./deploy-to-pi.sh [pi-ip] [username]
```

## Raspberry Pi Setup

### 1. Enable GPIO
```bash
# Add to /boot/config.txt
echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
echo "dtparam=i2c=on" | sudo tee -a /boot/config.txt
```

### 2. Install Dependencies
```bash
sudo apt-get update
sudo apt-get install -y libc6 libgcc1 libstdc++6
```

### 3. Run as Service
```bash
# Enable the service
sudo systemctl enable exit-gate
sudo systemctl start exit-gate

# Check status
sudo systemctl status exit-gate
```

## GPIO Pin Configuration

For Raspberry Pi 3, the default GPIO pins used:
- **Gate Trigger**: GPIO 18 (Pin 12) - Main gate control relay
- **Power GPIO**: GPIO 24 (Pin 18) - Power control indicator
- **Busy GPIO**: GPIO 23 (Pin 16) - Busy/Processing indicator
- **Live GPIO**: GPIO 25 (Pin 22) - System live/active indicator

### GPIO Pin Reference

```
Raspberry Pi 3 GPIO Layout:
                    +3V3  (1) (2)  +5V
                   GPIO2  (3) (4)  +5V
                   GPIO3  (5) (6)  GND
                   GPIO4  (7) (8)  GPIO14
                     GND  (9) (10) GPIO15
                  GPIO17 (11) (12) GPIO18  ← Gate Trigger
                  GPIO27 (13) (14) GND
                  GPIO22 (15) (16) GPIO23  ← Busy GPIO
                    +3V3 (17) (18) GPIO24  ← Power GPIO
                  GPIO10 (19) (20) GND
                   GPIO9 (21) (22) GPIO25  ← Live GPIO
                  GPIO11 (23) (24) GPIO8
                     GND (25) (26) GPIO7
                   GPIO0 (27) (28) GPIO1
                   GPIO5 (29) (30) GND
                   GPIO6 (31) (32) GPIO12
                  GPIO13 (33) (34) GND
                  GPIO19 (35) (36) GPIO16
                  GPIO26 (37) (38) GPIO20
                     GND (39) (40) GPIO21
```

### Wiring Example

For a typical parking gate system:

```
Gate Controller Board:
┌─────────────────┐
│  Gate Control   │
│     Relay       │ ← Connect to GPIO 18 (Pin 12)
└─────────────────┘

Power Indicator LED:
┌─────────────────┐
│   Power LED     │ ← Connect to GPIO 24 (Pin 18)
│   (Green)       │
└─────────────────┘

Busy Indicator LED:
┌─────────────────┐
│   Busy LED      │ ← Connect to GPIO 23 (Pin 16)
│   (Orange)      │
└─────────────────┘

Live Indicator LED:
┌─────────────────┐
│   Live LED      │ ← Connect to GPIO 25 (Pin 22)
│   (Blue)        │
└─────────────────┘
```

### GPIO Configuration in Application

1. **Set Control Mode**: Choose "GPIO (Raspberry Pi)" in Settings
2. **Configure Pins**: Set pin numbers according to your wiring
3. **Enable Features**: Toggle each GPIO function as needed
4. **Test GPIO**: Use test buttons to verify connections
5. **Set Timing**: Configure pulse duration (default: 500ms)

## Troubleshooting

### Permission Issues
```bash
sudo usermod -a -G gpio pi
sudo usermod -a -G dialout pi
```

### Memory Issues
Add swap if needed:
```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Performance Optimization
```bash
# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable wifi-powersave@wlan0

# Increase GPU memory split
echo "gpu_mem=64" | sudo tee -a /boot/config.txt
```

## GPIO Troubleshooting

### Common Issues

#### 1. Permission Denied Errors
```bash
# Add user to gpio group
sudo usermod -a -G gpio pi

# Set GPIO permissions
sudo chmod 666 /dev/gpiomem

# Restart system or logout/login
sudo reboot
```

#### 2. GPIO Already in Use
```bash
# Check which process is using GPIO
sudo lsof /dev/gpiomem

# Kill processes using GPIO
sudo pkill -f exit-gate

# Unexport all GPIO pins
for i in {0..27}; do
    echo $i | sudo tee /sys/class/gpio/unexport 2>/dev/null || true
done
```

#### 3. GPIO Test Failures
```bash
# Test GPIO manually
echo 18 | sudo tee /sys/class/gpio/export
echo out | sudo tee /sys/class/gpio/gpio18/direction
echo 1 | sudo tee /sys/class/gpio/gpio18/value
echo 0 | sudo tee /sys/class/gpio/gpio18/value
echo 18 | sudo tee /sys/class/gpio/unexport
```

#### 4. LED Not Working
- Check LED polarity (anode/cathode)
- Verify resistor value (220Ω recommended)
- Test with multimeter
- Check active_high setting

#### 5. Relay Not Switching
- Verify relay coil voltage (3.3V or 5V)
- Check relay trigger type (active high/low)
- Test relay with external power source
- Verify GPIO current capability

### Hardware Requirements

#### For LED Indicators:
```
GPIO Pin → 220Ω Resistor → LED Anode → LED Cathode → GND
```

#### For Relay Control:
```
GPIO Pin → Relay Driver (ULN2003) → Relay Coil → +5V
```

#### Recommended Components:
- **LEDs**: 3mm or 5mm standard LEDs
- **Resistors**: 220Ω for 3.3V GPIO
- **Relay**: 5V relay with optocoupler isolation
- **Driver**: ULN2003 or similar transistor array

### GPIO Performance Tips

1. **Use shorter wires** for GPIO connections
2. **Add pull-up/pull-down resistors** for inputs
3. **Use optocouplers** for electrical isolation
4. **Avoid GPIO 2,3** (I2C), **GPIO 14,15** (UART)
5. **Test individual pins** before full system integration

## GPIO Setup and Testing

### Quick Setup
```bash
# 1. Deploy to Raspberry Pi
./deploy-to-pi.sh [pi-ip] [username]

# 2. SSH to Raspberry Pi
ssh pi@your-pi-ip

# 3. Run GPIO setup (one-time)
sudo ./setup-gpio.sh

# 4. Reboot system
sudo reboot

# 5. Test GPIO functionality
./test-gpio.sh
```

### Manual GPIO Setup
```bash
# Add user to GPIO group
sudo usermod -a -G gpio pi

# Install GPIO packages
sudo apt-get install -y gpiod libgpiod-dev python3-gpiozero wiringpi

# Set permissions
sudo chmod 666 /dev/gpiomem

# Enable SPI/I2C in /boot/config.txt
echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
echo "dtparam=i2c=on" | sudo tee -a /boot/config.txt

# Reboot
sudo reboot
```

### GPIO Test Commands
```bash
# Test all GPIO pins
./test-gpio.sh

# Test specific pins
./test-gpio.sh 18 24 23 25  # gate power busy live

# Test individual pin manually
echo 18 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio18/direction  
echo 1 > /sys/class/gpio/gpio18/value
echo 0 > /sys/class/gpio/gpio18/value
echo 18 > /sys/class/gpio/unexport
```
