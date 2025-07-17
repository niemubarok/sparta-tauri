#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick GPIO Test - Test individual pins
"""

from __future__ import print_function
import time

def test_pin(pin_number):
    """Test individual GPIO pin"""
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        print("Testing GPIO pin {}...".format(pin_number))
        
        # Setup pin
        GPIO.setup(pin_number, GPIO.OUT)
        
        # Test HIGH
        print("Setting pin {} HIGH...".format(pin_number))
        GPIO.output(pin_number, GPIO.HIGH)
        time.sleep(1)
        
        # Test LOW  
        print("Setting pin {} LOW...".format(pin_number))
        GPIO.output(pin_number, GPIO.LOW)
        time.sleep(1)
        
        GPIO.cleanup()
        print("Pin {} test completed successfully".format(pin_number))
        return True
        
    except Exception as e:
        print("Pin {} test failed: {}".format(pin_number, str(e)))
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        pin = int(sys.argv[1])
        test_pin(pin)
    else:
        print("Testing default gate pin 24...")
        test_pin(24)
