#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Test Script untuk Verifikasi Gate Service Implementation
Menggunakan diagnostic tool dan gate service yang telah diperbaiki
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def main():
    print("🚪 EXIT GATE SYSTEM - IMPLEMENTATION VERIFICATION")
    print("="*60)
    
    # Test 1: Import gate service
    print("\n1️⃣ Testing Gate Service Import...")
    try:
        from gate_service import gate_service
        print("   ✅ Gate service imported successfully")
        
        if gate_service:
            print(f"   📊 Control mode: {gate_service.get_control_mode()}")
            status_info = gate_service.get_status()
            print(f"   📊 Status: {status_info}")
        else:
            print("   ⚠️ Gate service is None")
            
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Get diagnostic information
    print("\n2️⃣ Testing Diagnostic Information...")
    try:
        if gate_service:
            diagnostic_info = gate_service.get_diagnostic_info()
            print("   📋 Diagnostic Info:")
            print(f"      Control Mode: {diagnostic_info.get('control_mode')}")
            print(f"      GPIO Available: {diagnostic_info.get('gpio_available')}")
            print(f"      Raspberry Pi: {diagnostic_info.get('raspberry_pi')}")
            print(f"      Serial Available: {diagnostic_info.get('serial_available')}")
            
            gpio_error = diagnostic_info.get('gpio_error')
            if gpio_error:
                print(f"      GPIO Error: {gpio_error}")
                
            gpio_permissions = diagnostic_info.get('gpio_permissions', [])
            if gpio_permissions:
                print(f"      GPIO Issues: {', '.join(gpio_permissions)}")
        else:
            print("   ❌ Gate service not available")
            
    except Exception as e:
        print(f"   ❌ Diagnostic test failed: {e}")
    
    # Test 3: Hardware test
    print("\n3️⃣ Testing Hardware Functionality...")
    try:
        if gate_service:
            test_results = gate_service.test_hardware()
            overall_success = test_results.get('overall_success', False)
            print(f"   🧪 Hardware Test: {'✅ PASSED' if overall_success else '❌ FAILED'}")
            
            for test_name, result in test_results.items():
                if test_name != 'overall_success' and isinstance(result, bool):
                    print(f"      {test_name}: {'✅' if result else '❌'}")
        else:
            print("   ❌ Gate service not available")
            
    except Exception as e:
        print(f"   ❌ Hardware test failed: {e}")
    
    # Test 4: Gate operations
    print("\n4️⃣ Testing Gate Operations...")
    try:
        if gate_service:
            # Test open
            print("   🔓 Testing gate OPEN...")
            open_result = gate_service.open_gate()
            print(f"      Result: {'✅ SUCCESS' if open_result else '❌ FAILED'}")
            
            import time
            time.sleep(1)
            
            # Test close
            print("   🔒 Testing gate CLOSE...")
            close_result = gate_service.close_gate()
            print(f"      Result: {'✅ SUCCESS' if close_result else '❌ FAILED'}")
            
            if open_result and close_result:
                print("   ✅ Gate operations working correctly")
            else:
                print("   ⚠️ Some gate operations failed")
        else:
            print("   ❌ Gate service not available")
            
    except Exception as e:
        print(f"   ❌ Gate operations test failed: {e}")
    
    # Test 5: Import diagnostic tool
    print("\n5️⃣ Testing Diagnostic Tool Import...")
    try:
        # Import from parent directory
        sys.path.insert(0, os.path.dirname(__file__))
        from test_gate_service_debug import GateServiceDiagnostic
        
        diagnostic = GateServiceDiagnostic()
        print("   ✅ Diagnostic tool imported successfully")
        print(f"   📊 Tool ready with {len(diagnostic.results)} initial results")
        
    except Exception as e:
        print(f"   ❌ Diagnostic tool import failed: {e}")
    
    # Test 6: Import GUI components (basic check)
    print("\n6️⃣ Testing GUI Components...")
    try:
        import gui_exit_gate
        print("   ✅ GUI module imported successfully")
        
        # Check if ExitGateGUI class exists
        if hasattr(gui_exit_gate, 'ExitGateGUI'):
            print("   ✅ ExitGateGUI class available")
        else:
            print("   ❌ ExitGateGUI class not found")
            
    except Exception as e:
        print(f"   ❌ GUI import failed: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 IMPLEMENTATION VERIFICATION SUMMARY")
    print("="*60)
    
    if gate_service:
        control_mode = gate_service.get_control_mode()
        status_info = gate_service.get_status()
        
        print(f"✅ Gate Service: AVAILABLE ({control_mode})")
        print(f"📊 Current Status: {status_info.get('status', 'Unknown')}")
        print(f"🔢 Operations: {status_info.get('operation_count', 0)}")
        print(f"❌ Errors: {status_info.get('error_count', 0)}")
        
        if control_mode == 'SIMULATION':
            print("⚠️  Running in SIMULATION mode")
            print("💡 For GPIO mode: check Raspberry Pi and GPIO setup")
        elif control_mode == 'GPIO':
            print("🎉 GPIO mode active - hardware ready!")
        elif control_mode == 'SERIAL':
            print("🔌 Serial mode active")
        
    else:
        print("❌ Gate Service: NOT AVAILABLE")
    
    print("\n🚀 Implementation verification completed!")
    print("💡 Run 'python test_gate_service_debug.py' for detailed diagnostics")
    print("💡 Run 'python run_gui.py' to start the GUI application")
    
    return True

if __name__ == "__main__":
    main()
