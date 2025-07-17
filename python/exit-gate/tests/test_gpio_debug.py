#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GPIO Debug Test untuk Exit Gate System
Test individual components step by step
"""

from __future__ import absolute_import, print_function

import time
import sys
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_gpio_direct():
    """Test GPIO directly without services"""
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        pin = 24  # Gate control pin
        
        # Setup pin
        GPIO.setup(pin, GPIO.OUT)
        logger.info("GPIO pin {} setup complete".format(pin))
        
        # Test open (HIGH)
        print("Testing OPEN gate (GPIO {} HIGH)...".format(pin))
        GPIO.output(pin, GPIO.HIGH)
        logger.info("GPIO {} set to HIGH".format(pin))
        time.sleep(2)
        
        # Test close (LOW)
        print("Testing CLOSE gate (GPIO {} LOW)...".format(pin))
        GPIO.output(pin, GPIO.LOW)
        logger.info("GPIO {} set to LOW".format(pin))
        time.sleep(2)
        
        # Cleanup
        GPIO.cleanup()
        print("GPIO direct test completed successfully")
        return True
        
    except Exception as e:
        logger.error("GPIO direct test failed: {}".format(str(e)))
        return False

def test_gate_service():
    """Test gate service"""
    try:
        from gate_service import gate_service
        
        print("Testing gate service...")
        logger.info("Gate service control mode: {}".format(gate_service.get_control_mode()))
        
        # Test open
        print("Testing gate service OPEN...")
        result = gate_service.open_gate()
        logger.info("Gate open result: {}".format(result))
        time.sleep(2)
        
        # Test close
        print("Testing gate service CLOSE...")
        result = gate_service.close_gate()
        logger.info("Gate close result: {}".format(result))
        
        print("Gate service test completed")
        return True
        
    except Exception as e:
        logger.error("Gate service test failed: {}".format(str(e)))
        return False

def test_barcode_to_gate():
    """Test complete barcode to gate flow"""
    try:
        from usb_barcode_scanner import usb_barcode_scanner
        from gate_service import gate_service
        
        gate_triggered = False
        
        def test_gate_trigger(result):
            global gate_triggered
            logger.info("Barcode scan received: {}".format(result.code))
            
            if result.is_valid:
                logger.info("Valid barcode - triggering gate")
                gate_result = gate_service.open_gate()
                logger.info("Gate trigger result: {}".format(gate_result))
                gate_triggered = True
            else:
                logger.warning("Invalid barcode - no gate trigger")
        
        # Add listener
        usb_barcode_scanner.add_listener(test_gate_trigger)
        
        # Simulate scan
        print("Simulating barcode scan...")
        usb_barcode_scanner.simulate_scan("TEST123456")
        
        time.sleep(1)
        
        if gate_triggered:
            print("SUCCESS: Barcode scan triggered gate")
            return True
        else:
            print("FAILED: Barcode scan did not trigger gate")
            return False
            
    except Exception as e:
        logger.error("Barcode to gate test failed: {}".format(str(e)))
        return False

def main():
    """Run all tests"""
    print("=== GPIO Debug Test Suite ===")
    print()
    
    tests = [
        ("GPIO Direct Test", test_gpio_direct),
        ("Gate Service Test", test_gate_service),
        ("Barcode to Gate Flow Test", test_barcode_to_gate)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print("Running: {}".format(test_name))
        try:
            result = test_func()
            results[test_name] = result
            print("Result: {}".format("PASS" if result else "FAIL"))
        except Exception as e:
            results[test_name] = False
            print("Result: FAIL - {}".format(str(e)))
        print("-" * 50)
    
    # Summary
    print("\n=== Test Summary ===")
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print("{}: {}".format(test_name, status))
    
    all_passed = all(results.values())
    print("\nOverall: {}".format("ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED"))
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
