#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Test - Barcode Scanner to GPIO
Test yang lebih sederhana untuk memastikan flow bekerja
"""

from __future__ import print_function
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def simple_test():
    """Test sederhana barcode ke GPIO"""
    print("=== SIMPLE BARCODE TO GPIO TEST ===")
    
    try:
        # Import services  
        from usb_barcode_scanner import usb_barcode_scanner
        from gate_service import gate_service
        
        print("✅ Services imported")
        
        # Test gate directly first
        print("📍 Testing gate directly...")
        result = gate_service.open_gate()
        print("   Gate open result: {}".format(result))
        time.sleep(1)
        gate_service.close_gate()
        print("   Gate closed")
        
        # Test barcode simulation
        print("📍 Testing barcode simulation...")
        usb_barcode_scanner.simulate_scan("TEST999888")
        time.sleep(1)
        
        print("✅ Test completed - check logs above for GPIO trigger")
        print("If you see 'GPIO gate open signal sent to pin 24' = SUCCESS!")
        
        return True
        
    except Exception as e:
        print("❌ Error: {}".format(str(e)))
        return False

if __name__ == "__main__":
    simple_test()
