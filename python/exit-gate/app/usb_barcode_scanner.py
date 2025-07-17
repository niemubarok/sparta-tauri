#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
USB Barcode Scanner Service for Exit Gate System
Real USB HID input monitoring for Python 2.7
"""

from __future__ import absolute_import, print_function, unicode_literals

import os
import sys
import time
import threading
import logging
import select
import termios
import tty
from datetime import datetime

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

class USBBarcodeScanner(object):
    """USB Barcode Scanner using /dev/input monitoring"""
    
    def __init__(self, config=None):
        self.config = config or {
            'min_length': 6,
            'max_length': 20,
            'timeout': 0.1,  # 100ms between keystrokes
            'cooldown': 0.5  # 500ms cooldown between scans
        }
        
        self.enabled = True
        self.manually_disabled = False
        self.listeners = []
        
        # Scanner state
        self.buffer = ''
        self.last_keystroke = 0
        self.last_scan_time = 0
        
        # Input monitoring
        self.input_thread = None
        self.stop_thread = False
        self.input_devices = []
        
        # Find USB input devices
        self._find_input_devices()
        
        # Start monitoring if devices found
        if self.input_devices:
            self._start_monitoring()
        else:
            logger.warning("No USB input devices found for barcode scanner")
    
    def _find_input_devices(self):
        """Find USB input devices that could be barcode scanners"""
        try:
            # Look for event devices
            event_devices = []
            if os.path.exists('/dev/input'):
                for device in os.listdir('/dev/input'):
                    if device.startswith('event'):
                        device_path = '/dev/input/' + device
                        try:
                            # Try to open device to check if it's readable
                            with open(device_path, 'rb') as f:
                                event_devices.append(device_path)
                        except (IOError, OSError):
                            continue
            
            self.input_devices = event_devices
            logger.info("Found {} input devices: {}".format(
                len(self.input_devices), self.input_devices))
            
        except Exception as e:
            logger.error("Error finding input devices: {}".format(str(e)))
            self.input_devices = []
    
    def _start_monitoring(self):
        """Start USB input monitoring thread"""
        if self.input_thread and self.input_thread.is_alive():
            return
        
        self.stop_thread = False
        self.input_thread = threading.Thread(target=self._monitor_usb_input)
        self.input_thread.daemon = True
        self.input_thread.start()
        
        logger.info("USB barcode scanner monitoring started")
    
    def _stop_monitoring(self):
        """Stop USB input monitoring"""
        self.stop_thread = True
        if self.input_thread and self.input_thread.is_alive():
            self.input_thread.join(timeout=1)
        
        logger.info("USB barcode scanner monitoring stopped")
    
    def _monitor_usb_input(self):
        """Monitor USB input devices for barcode data"""
        logger.info("Starting USB input monitoring for physical scanner...")
        
        while not self.stop_thread:
            try:
                # Try multiple approaches for physical scanner input
                
                # Method 1: Check stdin for rapid input (scanner as keyboard)
                self._monitor_stdin_input()
                
                # Method 2: Monitor /dev/input/event* files (advanced)
                self._monitor_input_events()
                
                time.sleep(0.01)  # Small delay to prevent high CPU usage
                
            except Exception as e:
                logger.error("USB input monitoring error: {}".format(str(e)))
                time.sleep(1)
        
        logger.info("USB input monitoring stopped")
    
    def _monitor_input_events(self):
        """Monitor /dev/input/event files for barcode scanner input"""
        try:
            import struct
            import select
            
            # Try to read from available input devices
            for device_path in self.input_devices[:1]:  # Only try first device
                try:
                    with open(device_path, 'rb') as device:
                        # Check if data is available without blocking
                        ready, _, _ = select.select([device], [], [], 0)
                        if ready:
                            # Read input event
                            data = device.read(24)  # Standard input event size
                            if len(data) == 24:
                                # Parse input event (simplified)
                                _, _, type_, code, value = struct.unpack('llHHI', data)
                                
                                # Look for key press events (type 1, value 1)
                                if type_ == 1 and value == 1:
                                    # Convert key code to character (simplified mapping)
                                    char = self._keycode_to_char(code)
                                    if char:
                                        self._process_character(char)
                except:
                    # Device not accessible or error, continue to next
                    continue
        except:
            # Input event monitoring not available, fall back to stdin
            pass
    
    def _monitor_stdin_input(self):
        """Monitor stdin for rapid keyboard input (barcode scanner pattern)"""
        try:
            # Check if there's input available
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                # Read single character
                char = sys.stdin.read(1)
                if char:
                    self._process_character(char)
        except:
            # stdin not available or in wrong mode
            pass
    
    def _process_character(self, char):
        """Process individual character from input"""
        if not self.enabled or self.manually_disabled:
            return
        
        current_time = time.time()
        
        # Check cooldown period
        if current_time - self.last_scan_time < self.config['cooldown']:
            return
        
        # Check timeout - if too much time passed, reset buffer
        if current_time - self.last_keystroke > self.config['timeout']:
            self.buffer = ''
        
        self.last_keystroke = current_time
        
        # Handle special characters
        if char in ['\n', '\r']:  # Enter key
            self._process_buffer()
            return
        
        if char == '\t':  # Tab key
            self._process_buffer()
            return
        
        # Add printable characters to buffer
        if ord(char) >= 32 and ord(char) <= 126:
            self.buffer += char
            
            # Auto-process if buffer reaches max length
            if len(self.buffer) >= self.config['max_length']:
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
            logger.info("Valid barcode scanned: {}".format(code))
        else:
            result = BarcodeResult(code, time.time(), False)
            self._notify_listeners(result)
            logger.warning("Invalid barcode scanned: {}".format(code))
    
    def _validate_barcode(self, code):
        """Validate barcode format"""
        if len(code) < self.config['min_length']:
            return False
        
        if len(code) > self.config['max_length']:
            return False
        
        # Check for valid characters (alphanumeric)
        import re
        if not re.match(r'^[A-Za-z0-9]+$', code):
            return False
        
        return True
    
    def _notify_listeners(self, result):
        """Notify all listeners of barcode scan"""
        logger.info("USB Scanner: Notifying {} listeners for barcode: {}".format(
            len(self.listeners), result.code))
        
        for listener in self.listeners:
            try:
                logger.info("USB Scanner: Calling listener for barcode scan")
                listener(result)
            except Exception as e:
                logger.error("Listener notification error: {}".format(str(e)))
    
    def add_listener(self, callback):
        """Add barcode scan listener"""
        if callback not in self.listeners:
            self.listeners.append(callback)
            logger.debug("Added barcode scan listener")
    
    def remove_listener(self, callback):
        """Remove barcode scan listener"""
        if callback in self.listeners:
            self.listeners.remove(callback)
            logger.debug("Removed barcode scan listener")
    
    def enable(self):
        """Enable barcode scanner"""
        self.manually_disabled = False
        if not self.enabled:
            self.enabled = True
            self._start_monitoring()
        logger.info("USB barcode scanner enabled")
    
    def disable(self):
        """Disable barcode scanner"""
        self.manually_disabled = True
        logger.info("USB barcode scanner disabled")
    
    def is_enabled(self):
        """Check if scanner is enabled"""
        return self.enabled and not self.manually_disabled
    
    def get_config(self):
        """Get current configuration"""
        return {
            'min_length': self.config['min_length'],
            'max_length': self.config['max_length'],
            'timeout': self.config['timeout'],
            'cooldown': self.config['cooldown'],
            'enabled': self.enabled,
            'manually_disabled': self.manually_disabled,
            'input_devices': len(self.input_devices),
            'last_scan_time': self.last_scan_time
        }
    
    def simulate_scan(self, barcode):
        """Simulate a complete barcode scan (for testing)"""
        logger.info("USB Scanner: Simulating barcode scan: {}".format(barcode))
        
        # Clear any existing buffer
        self.buffer = ''
        
        # Process barcode directly and notify listeners immediately
        if self._validate_barcode(barcode):
            result = BarcodeResult(barcode, time.time(), True)
            logger.info("USB Scanner: Valid barcode - notifying listeners")
            self._notify_listeners(result)
        else:
            result = BarcodeResult(barcode, time.time(), False)
            logger.info("USB Scanner: Invalid barcode - notifying listeners")
            self._notify_listeners(result)
    
    def cleanup(self):
        """Cleanup scanner resources"""
        self._stop_monitoring()
        self.listeners = []
        logger.info("USB barcode scanner cleanup completed")
    
    def _keycode_to_char(self, keycode):
        """Convert keycode to character (simplified mapping for barcode scanners)"""
        # Basic keycode to character mapping for most common barcode characters
        keycode_map = {
            2: '1', 3: '2', 4: '3', 5: '4', 6: '5', 7: '6', 8: '7', 9: '8', 10: '9', 11: '0',
            16: 'Q', 17: 'W', 18: 'E', 19: 'R', 20: 'T', 21: 'Y', 22: 'U', 23: 'I', 24: 'O', 25: 'P',
            30: 'A', 31: 'S', 32: 'D', 33: 'F', 34: 'G', 35: 'H', 36: 'J', 37: 'K', 38: 'L',
            44: 'Z', 45: 'X', 46: 'C', 47: 'V', 48: 'B', 49: 'N', 50: 'M',
            28: '\n',  # Enter key
            15: '\t'   # Tab key
        }
        return keycode_map.get(keycode)
    
# Alternative simple implementation using keyboard hook
class SimpleUSBScanner(object):
    """Simple USB scanner that monitors rapid keyboard input"""
    
    def __init__(self, config=None):
        self.config = config or {
            'min_length': 6,
            'max_length': 20,
            'rapid_input_threshold': 0.05,  # 50ms between chars indicates scanner
            'cooldown': 0.5
        }
        
        self.enabled = True
        self.manually_disabled = False
        self.listeners = []
        
        # Input state
        self.input_buffer = []
        self.last_input_time = 0
        self.last_scan_time = 0
        
        # Start simple monitoring
        self._setup_simple_monitoring()
    
    def _setup_simple_monitoring(self):
        """Setup simple input monitoring"""
        logger.info("Simple USB scanner monitoring enabled")
        # In a real implementation, this would hook into keyboard input
        # For now, we'll rely on API simulation
    
    def process_rapid_input(self, characters):
        """Process rapid input that indicates barcode scanner"""
        if not self.enabled or self.manually_disabled:
            return
        
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_scan_time < self.config['cooldown']:
            return
        
        # Validate and process
        code = ''.join(characters).strip().upper()
        
        if self._validate_barcode(code):
            result = BarcodeResult(code, current_time, True)
            self._notify_listeners(result)
            self.last_scan_time = current_time
            logger.info("Valid USB barcode detected: {}".format(code))
    
    def _validate_barcode(self, code):
        """Validate barcode"""
        if len(code) < self.config['min_length']:
            return False
        if len(code) > self.config['max_length']:
            return False
        
        import re
        return re.match(r'^[A-Za-z0-9]+$', code) is not None
    
    def _notify_listeners(self, result):
        """Notify listeners"""
        logger.info("Simple USB Scanner: Notifying {} listeners for barcode: {}".format(
            len(self.listeners), result.code))
        
        for listener in self.listeners:
            try:
                logger.info("Simple USB Scanner: Calling listener function")
                listener(result)
            except Exception as e:
                logger.error("Simple USB Scanner: Listener error: {}".format(str(e)))
    
    def add_listener(self, callback):
        """Add listener"""
        if callback not in self.listeners:
            self.listeners.append(callback)
    
    def remove_listener(self, callback):
        """Remove listener"""
        if callback in self.listeners:
            self.listeners.remove(callback)
    
    def simulate_scan(self, barcode):
        """Simulate scan"""
        logger.info("Simple USB Scanner: Simulating scan for: {}".format(barcode))
        
        # Validate and create result
        if self._validate_barcode(barcode):
            result = BarcodeResult(barcode, time.time(), True)
            logger.info("Simple USB Scanner: Valid barcode - calling listeners")
            self._notify_listeners(result)
        else:
            result = BarcodeResult(barcode, time.time(), False)
            logger.info("Simple USB Scanner: Invalid barcode - calling listeners")
            self._notify_listeners(result)
    
    def get_config(self):
        """Get config"""
        return {
            'min_length': self.config['min_length'],
            'max_length': self.config['max_length'],
            'enabled': self.enabled,
            'manually_disabled': self.manually_disabled,
            'last_scan_time': self.last_scan_time
        }
    
    def enable(self):
        """Enable scanner"""
        self.manually_disabled = False
        logger.info("Simple USB scanner enabled")
    
    def disable(self):
        """Disable scanner"""
        self.manually_disabled = True
        logger.info("Simple USB scanner disabled")
    
    def is_enabled(self):
        """Check if enabled"""
        return self.enabled and not self.manually_disabled
    
    def cleanup(self):
        """Cleanup"""
        self.listeners = []

# Global scanner instance - use the simple one for better compatibility
usb_barcode_scanner = SimpleUSBScanner()

# Also create main scanner for advanced features if needed
main_usb_scanner = USBBarcodeScanner()

if __name__ == "__main__":
    # Test the USB scanner
    def test_listener(result):
        print("USB Scan: {} (valid: {})".format(result.code, result.is_valid))
    
    scanner = USBBarcodeScanner()
    scanner.add_listener(test_listener)
    
    print("USB Barcode Scanner Test - Type barcodes and press Enter")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scanner.cleanup()
        print("\nTest completed")
