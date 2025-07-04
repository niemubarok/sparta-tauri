#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual Gate Test Script
Test gate functionality directly without GUI
"""

import sys
import os
import time

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_gate_service():
    """Test gate service functionality"""
    print("=" * 50)
    print("MANUAL GATE SERVICE TEST")
    print("=" * 50)
    
    try:
        # Import gate service
        print("Importing gate service...")
        from app.gate_service import gate_service
        
        if not gate_service:
            print("❌ Gate service instance is None")
            return False
        
        print("✅ Gate service imported successfully")
        
        # Get diagnostic info
        print("\n📊 Gate Service Diagnostics:")
        diag = gate_service.get_diagnostic_info()
        for key, value in diag.items():
            print(f"  {key}: {value}")
        
        # Test hardware
        print("\n🧪 Testing hardware...")
        hw_test = gate_service.test_hardware()
        print(f"Hardware test result: {'✅ PASSED' if hw_test.get('overall_success') else '❌ FAILED'}")
        
        # Test gate operations
        print("\n🚪 Testing gate operations...")
        
        # Test open gate
        print("Testing OPEN gate...")
        result = gate_service.open_gate()
        print(f"Open result: {'✅ SUCCESS' if result else '❌ FAILED'}")
        
        if result:
            print("Waiting 3 seconds...")
            time.sleep(3)
            
            # Test close gate
            print("Testing CLOSE gate...")
            result = gate_service.close_gate()
            print(f"Close result: {'✅ SUCCESS' if result else '❌ FAILED'}")
        
        print("\n✅ Manual gate test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_barcode():
    """Test direct barcode processing simulation"""
    print("\n" + "=" * 50)
    print("DIRECT BARCODE PROCESSING TEST")
    print("=" * 50)
    
    try:
        # Import gate service
        from app.gate_service import gate_service
        
        if not gate_service:
            print("❌ Gate service not available")
            return False
        
        # Simulate barcode input
        test_barcode = "TEST123456"
        print(f"Simulating barcode: {test_barcode}")
        
        # Test gate open for barcode
        print("Opening gate for barcode...")
        result = gate_service.open_gate()
        
        if result:
            print("✅ Gate opened successfully!")
            print(f"Current status: {gate_service.get_current_status()}")
            
            # Wait and close
            time.sleep(2)
            print("Auto-closing gate...")
            close_result = gate_service.close_gate()
            print(f"Auto-close: {'✅ SUCCESS' if close_result else '❌ FAILED'}")
        else:
            print("❌ Failed to open gate for barcode")
        
        return result
        
    except Exception as e:
        print(f"❌ Barcode test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting manual gate tests...\n")
    
    # Test 1: Gate service functionality
    test1_result = test_gate_service()
    
    # Test 2: Direct barcode simulation
    test2_result = test_direct_barcode()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Gate Service Test: {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"Barcode Test: {'✅ PASSED' if test2_result else '❌ FAILED'}")
    
    if test1_result and test2_result:
        print("\n🎉 ALL TESTS PASSED!")
        print("Gate service is working correctly.")
        print("Issue mungkin di GUI integration atau hardware connection.")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Check gate service configuration.")
    
    input("\nPress Enter to exit...")
