#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Barcode Scanner to Gate Flow
Debug kenapa barcode scan tidak trigger GPIO
"""

from __future__ import print_function
import time
import logging

# Setup logging untuk debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_barcode_to_gate_flow():
    """Test complete flow dari barcode scan ke gate trigger"""
    print("=== Testing Barcode Scanner to Gate Flow ===")
    
    try:
        # Import services
        from usb_barcode_scanner import usb_barcode_scanner
        from gate_service import gate_service
        
        print("1. Services imported successfully")
        
        # Check gate service status
        print("2. Gate service info:")
        print("   Control mode: {}".format(gate_service.get_control_mode()))
        print("   Current status: {}".format(gate_service.get_status()))
        
        # Test gate direct
        print("3. Testing gate directly...")
        gate_result = gate_service.open_gate()
        print("   Direct gate open result: {}".format(gate_result))
        time.sleep(2)
        gate_service.close_gate()
        print("   Direct gate close completed")
        
        # Setup barcode listener yang trigger gate
        gate_triggered_count = [0]  # Use list to avoid global scope issues
        
        def barcode_gate_test_listener(result):
            logger.info("=== BARCODE LISTENER CALLED ===")
            logger.info("Barcode: {} (valid: {})".format(result.code, result.is_valid))
            
            if result.is_valid:
                logger.info("Valid barcode - triggering gate...")
                gate_result = gate_service.open_gate()
                logger.info("Gate trigger result: {}".format(gate_result))
                gate_triggered_count[0] += 1
                print("   >>> GATE TRIGGERED BY BARCODE! <<<")
            else:
                logger.warning("Invalid barcode - no gate trigger")
        
        # Add listener
        print("4. Adding barcode listener...")
        usb_barcode_scanner.add_listener(barcode_gate_test_listener)
        print("   Listener added successfully")
        
        # Test simulated scan
        print("5. Testing simulated barcode scan...")
        usb_barcode_scanner.simulate_scan("TEST123456")
        time.sleep(1)
        
        # Check result
        if gate_triggered_count[0] > 0:
            print("✅ SUCCESS: Barcode scan triggered gate {} times".format(gate_triggered_count[0]))
            return True
        else:
            print("❌ FAILED: Barcode scan did not trigger gate")
            return False
            
    except Exception as e:
        logger.error("Test failed: {}".format(str(e)))
        print("❌ ERROR: {}".format(str(e)))
        return False

def test_api_scan():
    """Test API scan endpoint"""
    print("\n=== Testing API Scan Endpoint ===")
    
    try:
        import requests
        
        # Test API scan
        response = requests.post('http://localhost:5001/api/scan', 
                               json={'barcode': 'TEST123456'},
                               timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API scan successful: {}".format(result))
            return True
        else:
            print("❌ API scan failed: status {}".format(response.status_code))
            return False
            
    except Exception as e:
        print("❌ API test error: {}".format(str(e)))
        return False

def main():
    """Run all tests"""
    print("Starting barcode scanner to gate flow debugging...")
    print("=" * 60)
    
    # Test 1: Direct flow
    success1 = test_barcode_to_gate_flow()
    
    # Test 2: API endpoint
    success2 = test_api_scan()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("Direct barcode flow: {}".format("PASS" if success1 else "FAIL"))
    print("API scan endpoint: {}".format("PASS" if success2 else "FAIL"))
    
    if success1:
        print("\n✅ Barcode scanner to gate flow is working!")
        print("If physical scanner not working, check:")
        print("1. USB connection: lsusb")
        print("2. Input devices: ls /dev/input/")
        print("3. Scanner mode: Should be HID keyboard emulation")
    else:
        print("\n❌ Barcode scanner to gate flow is broken!")
        print("Check the listener connection and gate service")

if __name__ == "__main__":
    main()
