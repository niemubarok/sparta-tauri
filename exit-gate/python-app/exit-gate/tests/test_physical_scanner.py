#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Physical USB Barcode Scanner
Test scanner fisik dan pastikan GPIO trigger
"""

from __future__ import print_function
import time
import logging
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_physical_scanner():
    """Test physical USB barcode scanner"""
    print("=== PHYSICAL USB BARCODE SCANNER TEST ===")
    
    try:
        from usb_barcode_scanner import usb_barcode_scanner  
        from gate_service import gate_service
        
        # Check current setup
        scanner_config = usb_barcode_scanner.get_config()
        print("Scanner config: {}".format(scanner_config))
        print("Gate control mode: {}".format(gate_service.get_control_mode()))
        
        # Track scans
        scan_count = [0]
        gate_triggers = [0]
        
        def physical_scan_handler(result):
            scan_count[0] += 1
            logger.info("PHYSICAL SCAN #{}: {} (valid: {})".format(
                scan_count[0], result.code, result.is_valid))
            print(">>> PHYSICAL BARCODE SCANNED: {} <<<".format(result.code))
            
            if result.is_valid:
                # Trigger gate
                gate_result = gate_service.open_gate()
                gate_triggers[0] += 1
                print(">>> GPIO TRIGGERED! Gate result: {} <<<".format(gate_result))
                
                # Auto close after 3 seconds
                def auto_close():
                    time.sleep(3)
                    gate_service.close_gate()
                    print(">>> Gate auto-closed <<<")
                
                threading.Thread(target=auto_close).start()
        
        # Add listener for physical scans
        usb_barcode_scanner.add_listener(physical_scan_handler)
        print("✅ Listener added for physical scanner")
        
        # Test simulation first
        print("\n📍 Testing simulation (should trigger GPIO)...")
        usb_barcode_scanner.simulate_scan("SIM123456")
        time.sleep(1)
        
        print("\n📍 Now waiting for PHYSICAL barcode scans...")
        print("💡 Instructions:")
        print("   1. Make sure USB barcode scanner is connected")
        print("   2. Scanner should be in HID keyboard mode")
        print("   3. Point scanner at a barcode and trigger it")
        print("   4. Watch for GPIO trigger messages")
        print("   5. Press Ctrl+C to stop")
        
        # Wait for physical scans
        start_time = time.time()
        while True:
            try:
                time.sleep(1)
                elapsed = int(time.time() - start_time)
                
                if elapsed % 10 == 0:  # Every 10 seconds
                    print("⏰ Waiting... {} scans received, {} GPIO triggers".format(
                        scan_count[0], gate_triggers[0]))
                
            except KeyboardInterrupt:
                break
        
        print("\n=== FINAL RESULTS ===")
        print("Total scans: {}".format(scan_count[0]))
        print("GPIO triggers: {}".format(gate_triggers[0]))
        
        if gate_triggers[0] > 0:
            print("✅ SUCCESS: Physical scanner triggered GPIO!")
        else:
            print("❌ No GPIO triggers from physical scanner")
            print("💡 Check:")
            print("   - USB connection: lsusb")
            print("   - Scanner mode: Should emit keyboard input")
            print("   - Try different barcode")
        
        return gate_triggers[0] > 0
        
    except Exception as e:
        print("❌ Error: {}".format(str(e)))
        return False

if __name__ == "__main__":
    test_physical_scanner()
