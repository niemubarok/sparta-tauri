#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick GPIO Test - Test new GPIO logic
"""

from __future__ import print_function
import time

def test_gpio_logic():
    """Test fixed GPIO logic"""
    print("=== GPIO LOGIC TEST ===")
    
    try:
        from gate_service import gate_service
        
        print("Gate control mode: {}".format(gate_service.get_control_mode()))
        print("Initial gate status: {}".format(gate_service.get_status()))
        
        # Test open (should be HIGH)
        print("\n1. Testing OPEN gate (should set GPIO 24 HIGH)...")
        result = gate_service.open_gate()
        print("   Open result: {}".format(result))
        print("   Gate status: {}".format(gate_service.get_status()))
        time.sleep(2)
        
        # Test close (should be LOW)
        print("\n2. Testing CLOSE gate (should set GPIO 24 LOW)...")
        result = gate_service.close_gate()
        print("   Close result: {}".format(result))
        print("   Gate status: {}".format(gate_service.get_status()))
        
        print("\n✅ GPIO logic test completed")
        print("💡 Check logs for 'GPIO gate OPEN signal sent to pin 24 (HIGH)' and 'GPIO gate CLOSE signal sent to pin 24 (LOW)'")
        
        return True
        
    except Exception as e:
        print("❌ Error: {}".format(str(e)))
        return False

if __name__ == "__main__":
    test_gpio_logic()
