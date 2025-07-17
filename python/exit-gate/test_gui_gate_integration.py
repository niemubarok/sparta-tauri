#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI Gate Integration Test
Test gate service integration with GUI specifically
"""

import sys
import os
import time

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_gui_gate_integration():
    """Test gate service as used by GUI"""
    print("=" * 60)
    print("GUI GATE INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Test import exactly as GUI does
        print("1. Testing import as GUI does...")
        try:
            from app.gate_service import gate_service
            print("✅ Direct app.gate_service import: SUCCESS")
        except Exception as e1:
            print(f"❌ Direct import failed: {e1}")
            try:
                import gate_service as gs
                gate_service = gs.gate_service if hasattr(gs, 'gate_service') else gs
                print("✅ Fallback import: SUCCESS")
            except Exception as e2:
                print(f"❌ Fallback import failed: {e2}")
                return False
        
        # Test gate service instance
        print(f"\n2. Gate service instance: {gate_service}")
        print(f"   Type: {type(gate_service)}")
        print(f"   Available: {gate_service is not None}")
        
        if not gate_service:
            print("❌ Gate service is None!")
            return False
        
        # Test basic methods that GUI uses
        print("\n3. Testing GUI-used methods...")
        
        # Test get_diagnostic_info (used in GUI initialization)
        try:
            diag = gate_service.get_diagnostic_info()
            print("✅ get_diagnostic_info(): SUCCESS")
            print(f"   Control Mode: {diag.get('control_mode')}")
            print(f"   GPIO Available: {diag.get('gpio_available')}")
        except Exception as e:
            print(f"❌ get_diagnostic_info() failed: {e}")
            return False
        
        # Test add_status_listener (used in GUI initialization)
        try:
            def dummy_listener(status):
                print(f"Status change: {status}")
            
            gate_service.add_status_listener(dummy_listener)
            print("✅ add_status_listener(): SUCCESS")
        except Exception as e:
            print(f"❌ add_status_listener() failed: {e}")
            return False
        
        # Test test_hardware (used in GUI initialization)
        try:
            hw_test = gate_service.test_hardware()
            print("✅ test_hardware(): SUCCESS")
            print(f"   Overall Success: {hw_test.get('overall_success')}")
        except Exception as e:
            print(f"❌ test_hardware() failed: {e}")
            return False
        
        # Test get_current_status (used in GUI)
        try:
            status = gate_service.get_current_status()
            print("✅ get_current_status(): SUCCESS")
            print(f"   Current Status: {status}")
        except Exception as e:
            print(f"❌ get_current_status() failed: {e}")
            return False
        
        # Test main gate operations (used by GUI buttons)
        print("\n4. Testing gate operations as GUI would...")
        
        # Test manual open (GUI "OPEN GATE" button)
        print("Testing manual open gate...")
        try:
            result = gate_service.open_gate()
            print(f"✅ open_gate(): {'SUCCESS' if result else 'FAILED'}")
            if result:
                time.sleep(1)
                status_after_open = gate_service.get_current_status()
                print(f"   Status after open: {status_after_open}")
        except Exception as e:
            print(f"❌ open_gate() failed: {e}")
            return False
        
        # Test manual close (GUI "CLOSE GATE" button)
        print("Testing manual close gate...")
        try:
            time.sleep(1)
            result = gate_service.close_gate()
            print(f"✅ close_gate(): {'SUCCESS' if result else 'FAILED'}")
            if result:
                time.sleep(1)
                status_after_close = gate_service.get_current_status()
                print(f"   Status after close: {status_after_close}")
        except Exception as e:
            print(f"❌ close_gate() failed: {e}")
            return False
        
        print("\n5. Testing barcode processing simulation...")
        try:
            # Simulate the exact process that happens when barcode is scanned
            test_barcode = "GUITEST789"
            print(f"Processing test barcode: {test_barcode}")
            
            # In GUI, it calls process_vehicle_exit which eventually calls gate_service.open_gate()
            print("Simulating barcode -> gate open sequence...")
            
            # Open gate for barcode
            result = gate_service.open_gate()
            if result:
                print("✅ Barcode processing -> gate open: SUCCESS")
                
                # Wait 2 seconds (as GUI does)
                time.sleep(2)
                
                # Auto-close (as GUI does)
                close_result = gate_service.close_gate()
                print(f"✅ Auto-close after barcode: {'SUCCESS' if close_result else 'FAILED'}")
            else:
                print("❌ Barcode processing -> gate open: FAILED")
                return False
                
        except Exception as e:
            print(f"❌ Barcode processing simulation failed: {e}")
            return False
        
        print("\n✅ ALL GUI INTEGRATION TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ GUI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_import_paths():
    """Test all possible import paths that GUI might use"""
    print("\n" + "=" * 60)
    print("TESTING ALL IMPORT PATHS")
    print("=" * 60)
    
    import_tests = [
        ("from app.gate_service import gate_service", "app.gate_service"),
        ("import gate_service", "direct gate_service"),
        ("from gate_service import gate_service", "gate_service.gate_service"),
    ]
    
    for import_code, description in import_tests:
        print(f"\nTesting: {description}")
        print(f"Code: {import_code}")
        
        try:
            if "from app.gate_service import gate_service" in import_code:
                from app.gate_service import gate_service
                service = gate_service
            elif "import gate_service" == import_code.strip():
                import gate_service as gs
                service = gs
            elif "from gate_service import gate_service" in import_code:
                from gate_service import gate_service
                service = gate_service
            else:
                continue
            
            print(f"✅ Import successful")
            print(f"   Service type: {type(service)}")
            print(f"   Service available: {service is not None}")
            
            if hasattr(service, 'open_gate'):
                print(f"   Has open_gate method: ✅")
            else:
                print(f"   Has open_gate method: ❌")
                
        except Exception as e:
            print(f"❌ Import failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting GUI Gate Integration Tests...\n")
    
    # Test import paths
    test_gui_import_paths()
    
    # Test GUI integration
    integration_result = test_gui_gate_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"GUI Integration Test: {'✅ PASSED' if integration_result else '❌ FAILED'}")
    
    if integration_result:
        print("\n🎉 GATE SERVICE IS WORKING CORRECTLY!")
        print("The issue is NOT in the gate service itself.")
        print("\nPossible causes for 'gate belum terbuka dari GUI':")
        print("1. GUI event handling issue")
        print("2. Button click not reaching gate service") 
        print("3. Debug mode not enabled")
        print("4. Audio feedback masking successful operation")
        print("5. Hardware connection issue (if on Raspberry Pi)")
        print("\nRecommendations:")
        print("- Check debug mode is ON in GUI")
        print("- Check log output in GUI when clicking buttons")
        print("- Test on actual Raspberry Pi with hardware")
        print("- Verify button event handlers are working")
    else:
        print("\n❌ GATE SERVICE HAS ISSUES!")
        print("Fix gate service before testing GUI.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
