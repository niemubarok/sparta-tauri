#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Barcode Scanner Service for Exit Gate System
Compatible with Python 2.7 and 3.x
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import threading
import time
import re
from typing import Optional, List, Callable, Dict  # For IDE support

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
        self.prefix = None
        self.suffix = None
        self.enabled = config.getboolean('scanner', 'enabled', True)

class BarcodeScanner(object):
    """USB Barcode Scanner Service using keyboard input simulation"""
    
    def __init__(self, scanner_config=None):
        self.config = scanner_config or ScannerConfig()
        self.enabled = self.config.enabled
        self.manually_disabled = False
        
        # Input buffer and timing
        self.buffer = ''
        self.last_keystroke = 0
        
        # Event listeners
        self.listeners = []
        
        # Threading for input simulation
        self.input_thread = None
        self.stop_thread = False
        
        # Start input monitoring if enabled
        if self.enabled:
            self._start_monitoring()
    
    def _start_monitoring(self):
        """Start input monitoring thread"""
        if self.input_thread and self.input_thread.is_alive():
            return
        
        self.stop_thread = False
        self.input_thread = threading.Thread(target=self._monitor_input)
        self.input_thread.daemon = True
        self.input_thread.start()
        
        logger.info("Barcode scanner monitoring started")
    
    def _stop_monitoring(self):
        """Stop input monitoring thread"""
        self.stop_thread = True
        if self.input_thread and self.input_thread.is_alive():
            self.input_thread.join(timeout=1)
        
        logger.info("Barcode scanner monitoring stopped")
    
    def _monitor_input(self):
        """Monitor for barcode input (simulation for testing)"""
        # Note: In a real implementation, this would interface with
        # the USB HID device or keyboard input monitoring
        # For Python 2.7 compatibility, we'll use a simple approach
        
        while not self.stop_thread:
            try:
                time.sleep(0.1)  # Check every 100ms
                
                # In real implementation, this would capture keyboard events
                # For now, we'll just process any pending input
                self._check_buffer_timeout()
                
            except Exception as e:
                logger.error("Input monitoring error: {}".format(str(e)))
                time.sleep(1)  # Wait before retry
    
    def _check_buffer_timeout(self):
        """Check if buffer has timed out and should be processed"""
        if not self.buffer:
            return
        
        current_time = time.time()
        if current_time - self.last_keystroke > self.config.timeout:
            self._process_buffer()
    
    def simulate_input(self, character):
        """Simulate keyboard input (for testing)"""
        if not self.enabled or self.manually_disabled:
            return
        
        current_time = time.time()
        
        # Check timeout
        if current_time - self.last_keystroke > self.config.timeout:
            self.buffer = ''
        
        self.last_keystroke = current_time
        
        # Handle special keys
        if character in ['Enter', '\n', '\r']:
            self._process_buffer()
            return
        
        if character in ['Tab', '\t']:
            self._process_buffer()
            return
        
        # Handle printable characters
        if len(character) == 1 and character.isprintable():
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
        logger.info("Barcode scanner enabled")
    
    def disable(self):
        """Disable barcode scanner"""
        self.manually_disabled = True
        logger.info("Barcode scanner disabled")
    
    def is_enabled(self):
        """Check if scanner is enabled"""
        return self.enabled and not self.manually_disabled
    
    def update_config(self, **kwargs):
        """Update scanner configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.debug("Updated scanner config: {} = {}".format(key, value))
    
    def get_config(self):
        """Get current configuration"""
        return {
            'min_length': self.config.min_length,
            'max_length': self.config.max_length,
            'timeout': self.config.timeout,
            'enabled': self.enabled,
            'manually_disabled': self.manually_disabled
        }
    
    def simulate_scan(self, barcode):
        """Simulate a complete barcode scan (for testing)"""
        logger.info("Simulating barcode scan: {}".format(barcode))
        
        # Clear any existing buffer
        self.buffer = ''
        
        # Simulate rapid input
        for char in barcode:
            self.simulate_input(char)
            time.sleep(0.01)  # 10ms between characters
        
        # Simulate Enter key
        self.simulate_input('Enter')
    
    def cleanup(self):
        """Cleanup scanner resources"""
        self._stop_monitoring()
        self.listeners = []
        logger.info("Barcode scanner cleanup completed")

# Scanner input interface for different platforms
class KeyboardMonitor(object):
    """Cross-platform keyboard monitoring for barcode input"""
    
    def __init__(self, scanner):
        self.scanner = scanner
        self.monitoring = False
    
    def start_monitoring(self):
        """Start keyboard monitoring"""
        # This would be implemented differently for each platform
        # For Python 2.7 compatibility, we'll use a simple approach
        self.monitoring = True
        logger.info("Keyboard monitoring started (simulation mode)")
    
    def stop_monitoring(self):
        """Stop keyboard monitoring"""
        self.monitoring = False
        logger.info("Keyboard monitoring stopped")

# Global barcode scanner instance
barcode_scanner = BarcodeScanner()

# Test functions
def test_barcode_scanner():
    """Test barcode scanner functionality"""
    print("Testing barcode scanner...")
    
    # Add test listener
    def test_listener(result):
        print("Scanned: {} (valid: {})".format(result.code, result.is_valid))
    
    barcode_scanner.add_listener(test_listener)
    
    # Test valid barcodes
    test_codes = [
        "123456",      # Valid
        "ABC123",      # Valid
        "12345",       # Too short
        "ABCDEFGHIJ123456789012345",  # Too long
        "TEST@#$",     # Invalid characters
        "VALIDCODE123" # Valid
    ]
    
    for code in test_codes:
        print("Testing: {}".format(code))
        barcode_scanner.simulate_scan(code)
        time.sleep(0.5)
    
    barcode_scanner.remove_listener(test_listener)
    print("Test completed.")

if __name__ == "__main__":
    test_barcode_scanner()
