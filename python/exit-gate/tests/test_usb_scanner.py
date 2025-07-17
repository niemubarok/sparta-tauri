#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
USB Barcode Scanner Test Script
Test real USB barcode scanner input
"""

from __future__ import absolute_import, print_function

import sys
import time
import threading
import select
import termios
import tty

def test_usb_scanner():
    """Test USB barcode scanner by monitoring rapid keyboard input"""
    
    print("=== USB Barcode Scanner Test ===")
    print("Instructions:")
    print("1. Connect your USB barcode scanner")
    print("2. Scan a barcode - it should appear as rapid keyboard input")
    print("3. Press Ctrl+C to exit")
    print()
    
    # Buffer for collecting rapid input
    input_buffer = ""
    last_input_time = 0
    scan_timeout = 0.1  # 100ms timeout between characters
    
    # Set terminal to raw mode for character-by-character input
    try:
        old_settings = termios.tcgetattr(sys.stdin.fileno())
        tty.setraw(sys.stdin.fileno())
        
        print("Ready for barcode scanning...")
        
        while True:
            # Check if input is available
            if select.select([sys.stdin], [], [], 0.01) == ([sys.stdin], [], []):
                char = sys.stdin.read(1)
                current_time = time.time()
                
                # If too much time passed, process previous buffer and start new
                if current_time - last_input_time > scan_timeout and input_buffer:
                    process_barcode(input_buffer)
                    input_buffer = ""
                
                # Add character to buffer
                if ord(char) >= 32 and ord(char) <= 126:  # Printable characters
                    input_buffer += char
                    last_input_time = current_time
                elif char in ['\n', '\r']:  # Enter key
                    if input_buffer:
                        process_barcode(input_buffer)
                        input_buffer = ""
                elif ord(char) == 3:  # Ctrl+C
                    break
            else:
                # Check timeout for pending buffer
                current_time = time.time()
                if input_buffer and current_time - last_input_time > scan_timeout:
                    process_barcode(input_buffer)
                    input_buffer = ""
            
            time.sleep(0.001)  # Small delay
            
    except KeyboardInterrupt:
        pass
    finally:
        # Restore terminal settings
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
        print("\nTest completed.")

def process_barcode(barcode_data):
    """Process detected barcode"""
    barcode = barcode_data.strip().upper()
    
    if len(barcode) >= 4:  # Minimum barcode length
        print("\n🔍 BARCODE DETECTED: '{}'".format(barcode))
        print("   Length: {} characters".format(len(barcode)))
        print("   Time: {}".format(time.strftime("%H:%M:%S")))
        
        # Test gate trigger
        print("   🚪 Triggering gate...")
        trigger_gate()
        print("   ✅ Gate trigger completed\n")
    else:
        print("   ⚠️ Too short, ignored: '{}'".format(barcode))

def trigger_gate():
    """Trigger gate via API"""
    try:
        import urllib2
        import json
        
        # Try to trigger gate via API
        req = urllib2.Request('http://localhost:5001/api/gate/open', 
                             data='{}', 
                             headers={'Content-Type': 'application/json'})
        response = urllib2.urlopen(req, timeout=2)
        result = json.loads(response.read())
        
        if result.get('success'):
            print("       Gate opened successfully!")
        else:
            print("       Gate open failed: {}".format(result.get('message', 'Unknown error')))
            
    except Exception as e:
        print("       Gate trigger error: {}".format(str(e)))

if __name__ == "__main__":
    test_usb_scanner()
