#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced Barcode Scanner Service for USB HID devices
Compatible with Python 2.7 and real USB barcode scanners
"""

from __future__ import absolute_import, print_function, unicode_literals

import os
import sys
import logging
import threading
import time
import re
import select
import termios
import tty
from config import config

logger = logging.getLogger(__name__)

class BarcodeResult(object):
    """Barcode scan result"""
    
    def __init__(self, code, timestamp=None, is_valid=True):
        self.code = code
        self.timestamp = timestamp or time.time()
        self.is_valid = is_valid
    
    def to_dict(self):
        return {
            'code': self.code,
            'timestamp': self.timestamp,
            'is_valid': self.is_valid
        }

class ScannerConfig(object):
    """Scanner configuration"""
    
    def __init__(self):
        self.min_length = config.getint('scanner', 'min_length', 6)
        self.max_length = config.getint('scanner', 'max_length', 20)
        self.timeout = config.getfloat('scanner', 'timeout', 0.1)  # 100ms
        self.cooldown_time = config.getfloat('scanner', 'cooldown_time', 0.5)  # 500ms
        self.prefix = None
        self.suffix = None
        self.enabled = config.getboolean('scanner', 'enabled', True)

class USBBarcodeScanner(object):
    """Enhanced USB Barcode Scanner Service with real input monitoring"""
    
    def __init__(self, scanner_config=None):
        self.config = scanner_config or ScannerConfig()
        self.enabled = self.config.enabled
        self.manually_disabled = False
        
        # Input buffer and timing
        self.buffer = ''
        self.last_keystroke = 0
        self.last_scan_time = 0
        
        # Event listeners
        self.listeners = []
        
        # Threading for input monitoring
        self.input_thread = None
        self.stop_thread = False
        
        # USB HID monitoring
        self.input_devices = []
        self.monitor_stdin = True
        
        # Initialize input monitoring
        self._find_input_devices()
        
        # Start input monitoring if enabled
        if self.enabled:
            self._start_monitoring()
    
    def _find_input_devices(self):
        """Find potential barcode scanner input devices"""
        input_devices = []
        
        # Check /dev/input for event devices (USB HID)
        try:
            input_dir = '/dev/input'
            if os.path.exists(input_dir):
                for device in os.listdir(input_dir):
                    if device.startswith('event'):
                        device_path = os.path.join(input_dir, device)
                        if os.access(device_path, os.R_OK):
                            input_devices.append(device_path)
                            logger.debug("Found input device: {}".format(device_path))
        except Exception as e:
            logger.warning("Error scanning input devices: {}".format(str(e)))
        
        self.input_devices = input_devices
        logger.info("Found {} potential input devices".format(len(input_devices)))
        
        return input_devices
    
    def _start_monitoring(self):
        """Start input monitoring thread"""
        if self.input_thread and self.input_thread.is_alive():
            return
        
        self.stop_thread = False
        self.input_thread = threading.Thread(target=self._monitor_input)
        self.input_thread.daemon = True
        self.input_thread.start()
        
        logger.info("USB Barcode scanner monitoring started")
    
    def _stop_monitoring(self):
        """Stop input monitoring thread"""
        self.stop_thread = True
        if self.input_thread and self.input_thread.is_alive():
            self.input_thread.join(timeout=1)
        
        logger.info("USB Barcode scanner monitoring stopped")
    
    def _monitor_input(self):
        """Monitor for barcode input from USB devices and stdin"""
        while not self.stop_thread:
            try:
                # Monitor stdin for keyboard input (including USB HID scanners)
                if self.monitor_stdin:
                    self._monitor_stdin_input()
                
                time.sleep(0.01)  # Small delay to prevent CPU spinning
                
            except Exception as e:
                logger.error("Input monitoring error: {}".format(str(e)))
                time.sleep(1)  # Wait before retry
    
    def _monitor_stdin_input(self):
        """Monitor stdin for rapid keyboard input (characteristic of barcode scanners)"""
        try:
            # Check if data is available on stdin
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                # Save terminal settings
                old_settings = None
                try:
                    old_settings = termios.tcgetattr(sys.stdin)
                    tty.setraw(sys.stdin.fileno())
                    
                    # Read character
                    char = sys.stdin.read(1)
                    
                    if char:
                        self._process_character(char)
                
                finally:
                    # Restore terminal settings
                    if old_settings:
                        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                        
        except Exception as e:
            # Expected when no input available or terminal not available
            pass
    
    def _process_character(self, character):
        """Process individual character input"""
        if not self.enabled or self.manually_disabled:
            return
        
        current_time = time.time()
        
        # Check cooldown time between scans
        if current_time - self.last_scan_time < self.config.cooldown_time:
            return
        
        # Check timeout - if too much time has passed, reset buffer
        if current_time - self.last_keystroke > self.config.timeout:
            self.buffer = ''
        
        self.last_keystroke = current_time
        
        # Handle special characters
        char_code = ord(character)
        
        # Handle Enter key (10) or Carriage Return (13)
        if char_code in [10, 13]:
            self._process_buffer()
            return
        
        # Handle Tab key (9)
        if char_code == 9:
            self._process_buffer()
            return
        
        # Handle printable ASCII characters (32-126)
        if 32 <= char_code <= 126:
            self.buffer += character
            
            # Auto-process if buffer reaches max length
            if len(self.buffer) >= self.config.max_length:
                self._process_buffer()
    
    def _process_buffer(self):
        """Process accumulated buffer as barcode"""
        if not self.buffer:
            return
        
        code = self.buffer.strip().upper()
        self.buffer = ''
        self.last_scan_time = time.time()
        
        if self._validate_barcode(code):
            result = BarcodeResult(code, time.time(), True)
            self._notify_listeners(result)
            logger.info("Valid USB barcode scanned: {}".format(code))
        else:
            result = BarcodeResult(code, time.time(), False)
            self._notify_listeners(result)
            logger.warning("Invalid USB barcode scanned: {}".format(code))
    
    def _validate_barcode(self, code):
        """Validate barcode format"""
        if len(code) < self.config.min_length:
            return False
        
        if len(code) > self.config.max_length:
            return False
        
        # Check for valid characters (alphanumeric)
        if not re.match(r'^[A-Za-z0-9]+$', code):
            return False
        
        return True
    
    def _notify_listeners(self, result):
        """Notify all listeners of barcode scan"""
        for listener in self.listeners:
            try:
                listener(result)
            except Exception as e:
                logger.error("Listener notification error: {}".format(str(e)))
    
    def add_listener(self, callback):
        """Add barcode scan listener"""
        if callback not in self.listeners:
            self.listeners.append(callback)
            logger.debug("Added USB barcode scan listener")
    
    def remove_listener(self, callback):
        """Remove barcode scan listener"""
        if callback in self.listeners:
            self.listeners.remove(callback)
            logger.debug("Removed USB barcode scan listener")
    
    def enable(self):
        """Enable barcode scanner"""
        self.manually_disabled = False
        if not self.enabled:
            self.enabled = True
            self._start_monitoring()
        logger.info("USB Barcode scanner enabled")
    
    def disable(self):
        """Disable barcode scanner"""
        self.manually_disabled = True
        logger.info("USB Barcode scanner disabled")
    
    def is_enabled(self):
        """Check if scanner is enabled"""
        return self.enabled and not self.manually_disabled
    
    def update_config(self, **kwargs):
        """Update scanner configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.debug("Updated USB scanner config: {} = {}".format(key, value))
    
    def get_config(self):
        """Get current configuration"""
        return {
            'min_length': self.config.min_length,
            'max_length': self.config.max_length,
            'timeout': self.config.timeout,
            'cooldown_time': self.config.cooldown_time,
            'enabled': self.enabled,
            'manually_disabled': self.manually_disabled,
            'last_scan_time': self.last_scan_time,
            'input_devices': len(self.input_devices)
        }
    
    def simulate_scan(self, barcode):
        """Simulate a complete barcode scan (for testing)"""
        logger.info("Simulating USB barcode scan: {}".format(barcode))
        
        # Clear any existing buffer
        self.buffer = ''
        
        # Simulate rapid input
        for char in barcode:
            self._process_character(char)
            time.sleep(0.01)  # 10ms between characters
        
        # Simulate Enter key
        self._process_character(chr(10))
    
    def test_input_devices(self):
        """Test access to input devices"""
        accessible_devices = []
        
        for device in self.input_devices:
            try:
                # Try to open device for reading
                with open(device, 'rb') as f:
                    accessible_devices.append(device)
                    logger.info("Device accessible: {}".format(device))
            except Exception as e:
                logger.warning("Device not accessible: {} - {}".format(device, str(e)))
        
        return accessible_devices
    
    def cleanup(self):
        """Cleanup scanner resources"""
        self._stop_monitoring()
        self.listeners = []
        logger.info("USB Barcode scanner cleanup completed")

# Alternative implementation using evdev for better USB HID support
class EvdevBarcodeScanner(object):
    """Enhanced barcode scanner using evdev for direct USB HID access"""
    
    def __init__(self, scanner_config=None):
        self.config = scanner_config or ScannerConfig()
        self.enabled = self.config.enabled
        self.manually_disabled = False
        self.listeners = []
        self.buffer = ''
        self.last_keystroke = 0
        self.last_scan_time = 0
        
        # Try to import evdev
        self.evdev_available = False
        try:
            import evdev
            self.evdev = evdev
            self.evdev_available = True
            logger.info("evdev available for USB HID monitoring")
        except ImportError:
            logger.warning("evdev not available, falling back to stdin monitoring")
        
        self.devices = []
        self.input_thread = None
        self.stop_thread = False
        
        if self.evdev_available:
            self._find_barcode_devices()
        
        if self.enabled:
            self._start_monitoring()
    
    def _find_barcode_devices(self):
        """Find USB HID devices that could be barcode scanners"""
        if not self.evdev_available:
            return
        
        devices = []
        try:
            for device_path in self.evdev.list_devices():
                device = self.evdev.InputDevice(device_path)
                
                # Look for devices with keyboard capabilities
                if self.evdev.ecodes.EV_KEY in device.capabilities():
                    # Check if device has alphanumeric keys
                    keys = device.capabilities()[self.evdev.ecodes.EV_KEY]
                    has_letters = any(k >= self.evdev.ecodes.KEY_A and k <= self.evdev.ecodes.KEY_Z for k in keys)
                    has_numbers = any(k >= self.evdev.ecodes.KEY_0 and k <= self.evdev.ecodes.KEY_9 for k in keys)
                    
                    if has_letters and has_numbers:
                        devices.append(device)
                        logger.info("Found potential barcode scanner: {} ({})".format(
                            device.name, device.path))
        
        except Exception as e:
            logger.error("Error finding barcode devices: {}".format(str(e)))
        
        self.devices = devices
        return devices
    
    def _start_monitoring(self):
        """Start monitoring barcode scanner devices"""
        if self.input_thread and self.input_thread.is_alive():
            return
        
        self.stop_thread = False
        self.input_thread = threading.Thread(target=self._monitor_devices)
        self.input_thread.daemon = True
        self.input_thread.start()
        
        logger.info("Evdev barcode scanner monitoring started")
    
    def _monitor_devices(self):
        """Monitor barcode scanner devices for input"""
        if not self.evdev_available or not self.devices:
            logger.warning("No evdev devices available, using fallback method")
            # Fallback to simple monitoring
            while not self.stop_thread:
                time.sleep(0.1)
            return
        
        while not self.stop_thread:
            try:
                # Monitor all devices
                for device in self.devices:
                    try:
                        # Check for input events
                        for event in device.read():
                            if event.type == self.evdev.ecodes.EV_KEY and event.value == 1:  # Key press
                                self._process_key_event(event.code)
                    except IOError:
                        # Device disconnected or no data
                        pass
                    except Exception as e:
                        logger.error("Error reading from device: {}".format(str(e)))
                
                time.sleep(0.01)  # Small delay
                
            except Exception as e:
                logger.error("Device monitoring error: {}".format(str(e)))
                time.sleep(1)
    
    def _process_key_event(self, key_code):
        """Process keyboard event from USB device"""
        if not self.enabled or self.manually_disabled:
            return
        
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_scan_time < self.config.cooldown_time:
            return
        
        # Check timeout
        if current_time - self.last_keystroke > self.config.timeout:
            self.buffer = ''
        
        self.last_keystroke = current_time
        
        # Convert key code to character
        character = self._keycode_to_char(key_code)
        
        if character == 'ENTER':
            self._process_buffer()
        elif character and len(character) == 1:
            self.buffer += character
            
            if len(self.buffer) >= self.config.max_length:
                self._process_buffer()
    
    def _keycode_to_char(self, key_code):
        """Convert evdev key code to character"""
        if not self.evdev_available:
            return None
        
        # Handle special keys
        if key_code == self.evdev.ecodes.KEY_ENTER:
            return 'ENTER'
        
        # Handle alphanumeric keys
        if self.evdev.ecodes.KEY_A <= key_code <= self.evdev.ecodes.KEY_Z:
            return chr(ord('A') + (key_code - self.evdev.ecodes.KEY_A))
        
        if self.evdev.ecodes.KEY_0 <= key_code <= self.evdev.ecodes.KEY_9:
            return chr(ord('0') + (key_code - self.evdev.ecodes.KEY_0))
        
        return None
    
    def _process_buffer(self):
        """Process accumulated buffer as barcode"""
        if not self.buffer:
            return
        
        code = self.buffer.strip().upper()
        self.buffer = ''
        self.last_scan_time = time.time()
        
        if len(code) >= self.config.min_length and len(code) <= self.config.max_length:
            result = BarcodeResult(code, time.time(), True)
            self._notify_listeners(result)
            logger.info("Valid evdev barcode scanned: {}".format(code))
        else:
            result = BarcodeResult(code, time.time(), False)
            self._notify_listeners(result)
            logger.warning("Invalid evdev barcode scanned: {}".format(code))
    
    def _notify_listeners(self, result):
        """Notify all listeners of barcode scan"""
        for listener in self.listeners:
            try:
                listener(result)
            except Exception as e:
                logger.error("Listener notification error: {}".format(str(e)))
    
    def add_listener(self, callback):
        """Add barcode scan listener"""
        if callback not in self.listeners:
            self.listeners.append(callback)
    
    def remove_listener(self, callback):
        """Remove barcode scan listener"""
        if callback in self.listeners:
            self.listeners.remove(callback)
    
    def simulate_scan(self, barcode):
        """Simulate barcode scan"""
        logger.info("Simulating evdev barcode scan: {}".format(barcode))
        
        result = BarcodeResult(barcode, time.time(), True)
        self._notify_listeners(result)
    
    def enable(self):
        """Enable scanner"""
        self.manually_disabled = False
        if not self.enabled:
            self.enabled = True
            self._start_monitoring()
    
    def disable(self):
        """Disable scanner"""
        self.manually_disabled = True
    
    def is_enabled(self):
        """Check if enabled"""
        return self.enabled and not self.manually_disabled
    
    def get_config(self):
        """Get configuration"""
        return {
            'min_length': self.config.min_length,
            'max_length': self.config.max_length,
            'timeout': self.config.timeout,
            'cooldown_time': self.config.cooldown_time,
            'enabled': self.enabled,
            'manually_disabled': self.manually_disabled,
            'last_scan_time': self.last_scan_time,
            'evdev_available': self.evdev_available,
            'devices_found': len(self.devices)
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_thread = True
        if self.input_thread and self.input_thread.is_alive():
            self.input_thread.join(timeout=1)
        
        for device in self.devices:
            try:
                device.close()
            except:
                pass
        
        self.listeners = []

# Auto-select best available implementation
def create_barcode_scanner(config=None):
    """Create the best available barcode scanner implementation"""
    
    # Try evdev first (best for USB HID)
    try:
        import evdev
        logger.info("Using evdev-based barcode scanner")
        return EvdevBarcodeScanner(config)
    except ImportError:
        logger.info("evdev not available, using USB barcode scanner")
        return USBBarcodeScanner(config)

# Global barcode scanner instance
barcode_scanner = create_barcode_scanner()

# Test function
def test_usb_barcode_scanner():
    """Test USB barcode scanner functionality"""
    print("Testing USB barcode scanner...")
    
    def test_listener(result):
        print("USB Scanned: {} (valid: {})".format(result.code, result.is_valid))
    
    scanner = create_barcode_scanner()
    scanner.add_listener(test_listener)
    
    print("Scanner ready. Please scan a barcode or press Ctrl+C to exit...")
    print("You can also test with simulation:")
    
    # Test simulation
    test_codes = ["TEST123", "ABCDEF", "123456"]
    for code in test_codes:
        print("Simulating: {}".format(code))
        scanner.simulate_scan(code)
        time.sleep(1)
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping scanner test...")
        scanner.cleanup()

if __name__ == "__main__":
    test_usb_barcode_scanner()
