#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Physical Barcode Scanner Listener
Listens to USB input and triggers GPIO directly
"""

from __future__ import print_function
import time
import sys
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimplePhysicalScanner(object):
    """Simple physical barcode scanner listener"""
    
    def __init__(self):
        self.buffer = ""
        self.last_scan_time = 0
        self.min_scan_length = 6
        self.running = True
        
        # Import services
        try:
            from gate_service import gate_service
            self.gate_service = gate_service
            logger.info("Gate service loaded: {}".format(gate_service.get_control_mode()))
        except Exception as e:
            logger.error("Failed to load gate service: {}".format(str(e)))
            self.gate_service = None
    
    def start_listening(self):
        """Start listening for input"""
        logger.info("Starting physical barcode scanner listener...")
        logger.info("Scan a barcode now...")
        
        try:
            while self.running:
                # Read character by character from stdin
                try:
                    char = sys.stdin.read(1)
                    if char:
                        self.process_character(char)
                except KeyboardInterrupt:
                    logger.info("Stopping scanner...")
                    break
                except:
                    time.sleep(0.01)  # Small delay
                    
        except Exception as e:
            logger.error("Scanner error: {}".format(str(e)))
    
    def process_character(self, char):
        """Process input character"""
        current_time = time.time()
        
        # Check for end of scan (Enter or newline)
        if char in ['\n', '\r', '\t']:
            if self.buffer and len(self.buffer) >= self.min_scan_length:
                self.process_scan(self.buffer.strip())
            self.buffer = ""
            return
        
        # Reset buffer if too much time passed
        if current_time - self.last_scan_time > 0.5:
            self.buffer = ""
        
        # Add printable characters
        if ord(char) >= 32 and ord(char) <= 126:
            self.buffer += char
            self.last_scan_time = current_time
    
    def process_scan(self, barcode):
        """Process complete barcode scan"""
        logger.info("=== BARCODE SCANNED ===")
        logger.info("Barcode: {}".format(barcode))
        
        # Validate barcode
        if self.validate_barcode(barcode):
            logger.info("✅ Valid barcode - triggering gate")
            self.trigger_gate(barcode)
        else:
            logger.warning("❌ Invalid barcode format")
    
    def validate_barcode(self, barcode):
        """Validate barcode format"""
        if len(barcode) < self.min_scan_length:
            return False
        
        # Check alphanumeric
        import re
        return re.match(r'^[A-Za-z0-9]+$', barcode) is not None
    
    def trigger_gate(self, barcode):
        """Trigger gate opening"""
        try:
            if self.gate_service:
                logger.info("Opening gate for barcode: {}".format(barcode))
                result = self.gate_service.open_gate(10)  # Auto-close after 10 seconds
                if result:
                    logger.info("✅ Gate opened successfully")
                else:
                    logger.error("❌ Failed to open gate")
            else:
                logger.error("❌ Gate service not available")
                
        except Exception as e:
            logger.error("Error triggering gate: {}".format(str(e)))

def main():
    """Main function"""
    print("=== Physical Barcode Scanner Listener ===")
    print("This program listens for USB barcode scanner input")
    print("Scan a barcode to trigger the gate")
    print("Press Ctrl+C to exit")
    print()
    
    scanner = SimplePhysicalScanner()
    
    try:
        scanner.start_listening()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print("Error: {}".format(str(e)))

if __name__ == "__main__":
    main()
