#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Test: Button Click Simulation
Test exactly what happens when GUI button is clicked
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_button_click_simulation():
    """Simulate exact button click flow from GUI"""
    print("=" * 60)
    print("SIMULATING GUI BUTTON CLICK")
    print("=" * 60)
    
    print("Step 1: Import gate service as GUI does...")
    try:
        from app.gate_service import gate_service
        print(f"✅ Gate service imported: {gate_service}")
        print(f"   Type: {type(gate_service)}")
        print(f"   Available: {gate_service is not None}")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    print("\nStep 2: Check gate service availability...")
    if not gate_service:
        print("❌ Gate service is None - this is the problem!")
        return False
    
    print("✅ Gate service is available")
    
    print("\nStep 3: Get diagnostic info...")
    try:
        diag = gate_service.get_diagnostic_info()
        print(f"Control Mode: {diag.get('control_mode')}")
        print(f"Current Status: {diag.get('current_status')}")
        print(f"GPIO Available: {diag.get('gpio_available')}")
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        return False
    
    print("\nStep 4: Simulate manual_open_gate() method...")
    print("Executing: gate_service.open_gate()")
    
    try:
        # This is EXACTLY what manual_open_gate() does
        result = gate_service.open_gate()
        print(f"Result: {result}")
        
        if result:
            print("✅ Gate opened successfully!")
            print("This means the problem is NOT in gate service")
            print("The problem might be:")
            print("  1. Button not calling manual_open_gate()")
            print("  2. Exception being caught silently")
            print("  3. GUI import path issue")
            print("  4. Threading issue")
            
            # Test status
            status = gate_service.get_current_status()
            print(f"Gate status after open: {status}")
            
            # Test close
            print("\nTesting close...")
            close_result = gate_service.close_gate()
            print(f"Close result: {close_result}")
            
            if close_result:
                final_status = gate_service.get_current_status()
                print(f"Gate status after close: {final_status}")
            
            return True
        else:
            print("❌ Gate failed to open")
            return False
            
    except Exception as e:
        print(f"❌ Exception during open_gate(): {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_import_compatibility():
    """Test import compatibility exactly as GUI would"""
    print("\n" + "=" * 60)
    print("TESTING GUI IMPORT COMPATIBILITY")
    print("=" * 60)
    
    print("Testing GUI's import fallback logic...")
    
    # Test 1: Direct app import (primary)
    print("\n1. Testing primary import: from app.gate_service import gate_service")
    try:
        from app.gate_service import gate_service as gs1
        print("✅ Primary import successful")
        print(f"   Service: {gs1}")
        print(f"   Has open_gate: {hasattr(gs1, 'open_gate') if gs1 else False}")
        primary_success = True
    except Exception as e:
        print(f"❌ Primary import failed: {e}")
        primary_success = False
    
    # Test 2: Fallback import
    print("\n2. Testing fallback import: import gate_service")
    try:
        import gate_service as gs_module
        gs2 = gs_module.gate_service if hasattr(gs_module, 'gate_service') else gs_module
        print("✅ Fallback import successful")
        print(f"   Module: {gs_module}")
        print(f"   Service: {gs2}")
        print(f"   Has open_gate: {hasattr(gs2, 'open_gate') if gs2 else False}")
        fallback_success = True
    except Exception as e:
        print(f"❌ Fallback import failed: {e}")
        fallback_success = False
    
    # Summary
    print(f"\nImport Test Results:")
    print(f"  Primary (app.gate_service): {'✅ SUCCESS' if primary_success else '❌ FAILED'}")
    print(f"  Fallback (gate_service): {'✅ SUCCESS' if fallback_success else '❌ FAILED'}")
    
    if primary_success:
        print("\n✅ GUI should be able to import gate service successfully")
        return True
    elif fallback_success:
        print("\n⚠️ GUI will use fallback import")
        return True
    else:
        print("\n❌ GUI cannot import gate service - THIS IS THE PROBLEM!")
        return False

def test_button_event_handler():
    """Test if button event handler would work"""
    print("\n" + "=" * 60)
    print("TESTING BUTTON EVENT HANDLER")
    print("=" * 60)
    
    try:
        # Simulate GUI initialization
        print("Simulating GUI initialization...")
        
        # Import gate service
        from app.gate_service import gate_service
        
        if not gate_service:
            print("❌ Gate service is None after import")
            return False
        
        print("✅ Gate service initialized")
        
        # Simulate button click handler
        print("\nSimulating button click event...")
        print("Calling manual_open_gate() logic...")
        
        # This is the exact code from manual_open_gate()
        if gate_service:
            result = gate_service.open_gate()
            print("Manual gate open: {}".format("Success" if result else "Failed"))
            if result:
                print("✅ Transaction would be incremented")
                print("✅ Audio sound would play")
                return True
            else:
                print("❌ Gate open failed")
                print("❌ Error sound would play")
                return False
        else:
            print("❌ Gate service not available in button handler")
            return False
            
    except Exception as e:
        print(f"❌ Button handler simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print("🚀 DIAGNOSING GUI GATE ISSUE...")
    print("Checking why 'gate belum terbuka dari gui'\n")
    
    # Test 1: Button click simulation
    test1 = test_button_click_simulation()
    
    # Test 2: Import compatibility
    test2 = test_gui_import_compatibility()
    
    # Test 3: Button event handler
    test3 = test_button_event_handler()
    
    # Final analysis
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print(f"Button Click Simulation: {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"Import Compatibility: {'✅ PASSED' if test2 else '❌ FAILED'}")
    print(f"Button Event Handler: {'✅ PASSED' if test3 else '❌ FAILED'}")
    
    if test1 and test2 and test3:
        print("\n🎉 ALL TESTS PASSED!")
        print("Gate service is working correctly!")
        print("\nPossible causes for GUI issue:")
        print("1. 🖱️ Button click not reaching event handler")
        print("2. 🔇 Silent exceptions in GUI thread")
        print("3. 📺 GUI display not updating")
        print("4. 🔊 Audio feedback missing")
        print("5. 🔧 Hardware connection (if on Raspberry Pi)")
        print("\nRecommendations:")
        print("• Check GUI console/log for errors")
        print("• Verify button click events are firing")
        print("• Test on Raspberry Pi with actual hardware")
        print("• Check debug mode is enabled")
    else:
        print("\n❌ TESTS FAILED!")
        print("Issue is in gate service or import system")
        if not test2:
            print("🔧 FIX: Gate service import issues")
        if not test1:
            print("🔧 FIX: Gate service functionality")
        if not test3:
            print("🔧 FIX: Button event handling")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
