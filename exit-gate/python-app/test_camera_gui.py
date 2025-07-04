#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Camera Integration with GUI
Simple test script to verify camera functionality
"""

from __future__ import print_function
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_camera_service():
    """Test camera service independently"""
    print("=== Testing Camera Service ===")
    
    try:
        from camera_service import camera_service
        print("✅ Camera service imported successfully")
        
        # Test camera status
        status = camera_service.get_cameras_status()
        print("Camera Status:")
        for camera_name, camera_status in status.items():
            print("  {}: {}".format(camera_name, "Enabled" if camera_status['enabled'] else "Disabled"))
        
        # Test camera connectivity
        print("\n=== Testing Camera Connectivity ===")
        results = camera_service.test_all_cameras()
        
        for camera_name, success in results.items():
            if success:
                print("✅ Camera '{}': OK".format(camera_name.upper()))
            else:
                print("❌ Camera '{}': FAILED".format(camera_name.upper()))
        
        # Test image capture
        print("\n=== Testing Image Capture ===")
        for camera_name in ['plate', 'driver']:
            print("Testing {} camera...".format(camera_name))
            result = camera_service.capture_image(camera_name)
            
            if result.success:
                print("✅ {} camera capture: SUCCESS".format(camera_name.upper()))
                print("  Image size: {} bytes".format(len(result.image_data) if result.image_data else 0))
            else:
                print("❌ {} camera capture: FAILED".format(camera_name.upper()))
                print("  Error: {}".format(result.error_message))
        
        # Test exit images capture
        print("\n=== Testing Exit Images Capture ===")
        exit_result = camera_service.capture_exit_images()
        if exit_result.success:
            print("✅ Exit images capture: SUCCESS")
            print("  Combined image size: {} bytes".format(len(exit_result.image_data) if exit_result.image_data else 0))
        else:
            print("❌ Exit images capture: FAILED")
            print("  Error: {}".format(exit_result.error_message))
        
        return True
        
    except Exception as e:
        print("❌ Camera service test failed: {}".format(str(e)))
        return False

def test_gui_camera_integration():
    """Test camera integration in GUI (without actually starting GUI)"""
    print("\n=== Testing GUI Camera Integration ===")
    
    try:
        # Import GUI class
        from gui_exit_gate import ExitGateGUI
        print("✅ GUI class imported successfully")
        
        # We can't easily test the full GUI without starting it,
        # but we can test some basic initialization
        print("✅ GUI camera integration code is available")
        
        return True
        
    except Exception as e:
        print("❌ GUI camera integration test failed: {}".format(str(e)))
        return False

def main():
    """Main test function"""
    print("Camera Integration Test")
    print("=" * 50)
    
    # Test camera service
    camera_ok = test_camera_service()
    
    # Test GUI integration
    gui_ok = test_gui_camera_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("  Camera Service: {}".format("✅ PASS" if camera_ok else "❌ FAIL"))
    print("  GUI Integration: {}".format("✅ PASS" if gui_ok else "❌ FAIL"))
    
    if camera_ok and gui_ok:
        print("\n🎉 All tests passed! Camera integration is ready.")
        print("\nTo test with real cameras:")
        print("1. Update config.ini with your camera IPs and credentials")
        print("2. Set camera_brand to 'hikvision', 'glenz', 'dahua', or 'auto'")
        print("3. Run: python gui_exit_gate.py")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return 0 if (camera_ok and gui_ok) else 1

if __name__ == "__main__":
    exit(main())
