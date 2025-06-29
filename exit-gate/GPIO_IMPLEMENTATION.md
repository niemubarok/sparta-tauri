# GPIO Implementation for Exit Gate System

This document describes the GPIO implementation for controlling gate hardware on Raspberry Pi devices.

## Overview

The exit gate system now supports two control modes:
1. **Serial Communication** - Traditional mode using serial commands (*OUT1ON#/*OUT1OFF#)
2. **GPIO Control** - Direct GPIO pin control for Raspberry Pi deployment

## GPIO Configuration

### Hardware Setup

For Raspberry Pi deployment, connect your gate relay to a GPIO pin:

```
Raspberry Pi GPIO → Relay Module → Gate Motor
Pin X (configurable) → IN1 → Gate Control
```

### Software Configuration

GPIO settings can be configured in the Settings page:

1. **GPIO Pin Number**: Physical pin number (1-40) on Raspberry Pi
2. **Active High/Low**: Whether relay activates on HIGH (true) or LOW (false) signal
3. **Control Mode**: Select between 'serial' and 'gpio'

### Default Configuration

```typescript
interface GpioConfig {
  pin: 18,           // GPIO pin 18 (physical pin 12)
  active_high: true  // Relay activates on HIGH signal
}
```

## Features

### Automatic Detection
- System automatically detects if GPIO interface is available
- Falls back to serial mode if GPIO is unavailable
- Displays current mode in status interface

### GPIO Commands
- `gpio_open_gate`: Opens gate using configured GPIO pin
- `gpio_close_gate`: Closes gate using configured GPIO pin  
- `gpio_test_pin`: Tests GPIO functionality with blink sequence
- `check_gpio_availability`: Checks if GPIO interface is available

### Auto-close Timer
- Supports automatic gate closing after configurable timeout
- Async implementation prevents blocking
- Configurable delay (default: 5 seconds)

## Implementation Details

### Backend (Rust)
- Uses Linux sysfs GPIO interface for compatibility
- Commands executed via shell for reliability
- Async operations prevent blocking
- Error handling and logging

### Frontend (TypeScript)
- Reactive configuration in Settings page
- Real-time status monitoring
- Test functions for validation
- Mode switching capabilities

## Raspberry Pi Deployment

### Prerequisites
1. Raspberry Pi with GPIO access
2. Relay module compatible with 3.3V logic
3. Proper permissions for GPIO access

### Installation Steps
1. Build for ARM64 target: `cargo build --target aarch64-unknown-linux-gnu --release`
2. Deploy binary to Raspberry Pi
3. Configure GPIO permissions
4. Set GPIO configuration in Settings

### GPIO Permissions
Ensure proper permissions for GPIO access:
```bash
sudo usermod -a -G gpio $USER
# or
sudo chmod 666 /sys/class/gpio/export
sudo chmod 666 /sys/class/gpio/unexport
```

## Testing

### GPIO Test Function
The Settings page includes a GPIO test function that:
1. Configures the specified GPIO pin
2. Runs a blink sequence (on-off-on-off)
3. Reports success/failure status

### Status Monitoring
- Real-time display of current control mode
- Connection status indicators
- GPIO availability detection

## Comparison: Serial vs GPIO

| Feature | Serial Mode | GPIO Mode |
|---------|-------------|-----------|
| Hardware Required | Serial-to-relay adapter | Direct GPIO-to-relay |
| Response Time | ~100ms | ~1ms |
| Reliability | Good | Excellent |
| Setup Complexity | Medium | Low |
| Platform Support | Universal | Raspberry Pi only |
| Cost | Higher (adapter needed) | Lower (direct connection) |

## Migration Guide

### From Serial to GPIO
1. Connect relay directly to GPIO pin
2. Configure GPIO pin number in Settings
3. Set `control_mode` to 'gpio'
4. Test GPIO functionality
5. Update any deployment scripts

### Fallback Strategy
The system automatically falls back to serial mode if:
- GPIO interface is unavailable
- GPIO configuration fails
- Running on non-Raspberry Pi hardware

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Check GPIO permissions
   - Run with proper user privileges

2. **GPIO Pin Busy**
   - Check if pin is used by other processes
   - Use different pin number

3. **Relay Not Responding**
   - Verify wiring connections
   - Check active_high setting
   - Test with multimeter

### Debug Commands
```bash
# Check GPIO availability
ls /sys/class/gpio

# Test GPIO manually
echo 18 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio18/direction
echo 1 > /sys/class/gpio/gpio18/value
echo 0 > /sys/class/gpio/gpio18/value
```

## Future Enhancements

1. **Multiple GPIO Support**: Control multiple gates
2. **PWM Support**: Variable speed control
3. **Input Monitoring**: GPIO-based sensors
4. **Hardware Detection**: Auto-detect connected hardware

## Notes

- GPIO implementation is only available on Raspberry Pi
- Serial mode remains the default for compatibility
- Both modes can coexist with automatic switching
- Configuration is stored in database settings
