#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Raspberry Pi Camera Test Script for Exit Gate System
Tests camera service functionality on Raspberry Pi with Python 3.10+
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test all required imports"""
    print("🧪 Testing imports...")
    
    try:
        import RPi.GPIO as GPIO
        print("✅ RPi.GPIO imported successfully")
    except ImportError as e:
        print("❌ RPi.GPIO import failed: {}".format(e))
    
    try:
        from picamera2 import Picamera2
        print("✅ picamera2 imported successfully")
    except ImportError as e:
        print("⚠️ picamera2 import failed: {}".format(e))
    
    try:
        from picamera import PiCamera
        print("✅ picamera (legacy) imported successfully")
    except ImportError as e:
        print("⚠️ picamera (legacy) import failed: {}".format(e))
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print("⚠️ OpenCV import failed: {}".format(e))
    
    try:
        from PIL import Image
        print("✅ PIL/Pillow imported successfully")
    except ImportError as e:
        print("❌ PIL/Pillow import failed: {}".format(e))

def test_camera_detection():
    """Test camera detection"""
    print("\n📷 Testing camera detection...")
    
    try:
        from camera_service import camera_service
        cameras = camera_service.detect_raspberry_pi_cameras()
        
        if cameras:
            print("✅ Found {} Raspberry Pi cameras:".format(len(cameras)))
            for camera in cameras:
                print("   - ID: {}, Type: {}, Model: {}".format(
                    camera['id'], camera['type'], camera['model']))
        else:
            print("⚠️ No Raspberry Pi cameras detected")
            
    except Exception as e:
        print("❌ Camera detection failed: {}".format(e))

def test_camera_capture():
    """Test camera capture"""
    print("\n📸 Testing camera capture...")
    
    try:
        from camera_service import camera_service
        
        # Test Raspberry Pi camera capture
        result = camera_service.capture_raspberry_pi_camera()
        
        if result.success:
            print("✅ Raspberry Pi camera capture successful")
            print("   Image size: {} bytes".format(len(result.image_data)))
        else:
            print("❌ Camera capture failed: {}".format(result.error_message))
            
    except Exception as e:
        print("❌ Camera capture test failed: {}".format(e))

def test_auto_configuration():
    """Test auto-configuration"""
    print("\n⚙️ Testing auto-configuration...")
    
    try:
        from camera_service import camera_service
        
        success = camera_service.auto_configure_raspberry_pi_camera()
        
        if success:
            print("✅ Auto-configuration successful")
            status = camera_service.get_cameras_status()
            print("   Configured cameras: {}".format(list(status.keys())))
        else:
            print("⚠️ Auto-configuration failed")
            
    except Exception as e:
        print("❌ Auto-configuration test failed: {}".format(e))

def test_enhanced_capture():
    """Test enhanced capture method"""
    print("\n🚀 Testing enhanced capture...")
    
    try:
        from camera_service import camera_service
        
        # First auto-configure
        camera_service.auto_configure_raspberry_pi_camera()
        
        # Test enhanced capture
        result = camera_service.capture_image_enhanced("rpi_exit")
        
        if result.success:
            print("✅ Enhanced capture successful")
            print("   Image size: {} bytes".format(len(result.image_data)))
        else:
            print("❌ Enhanced capture failed: {}".format(result.error_message))
            
    except Exception as e:
        print("❌ Enhanced capture test failed: {}".format(e))

def main():
    """Main test function"""
    print("🍓 Raspberry Pi Camera Service Test")
    print("=" * 50)
    
    # Check if running on Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            if 'Raspberry Pi' not in f.read():
                print("⚠️ Warning: Not running on Raspberry Pi")
    except:
        print("⚠️ Warning: Cannot detect if running on Raspberry Pi")
    
    test_imports()
    test_camera_detection()
    test_camera_capture()
    test_auto_configuration()
    test_enhanced_capture()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
    print("\n💡 Tips for troubleshooting:")
    print("- Enable camera: sudo raspi-config -> Interface Options -> Camera")
    print("- Install packages: sudo apt install python3-picamera2 python3-libcamera")
    print("- Test with libcamera-still: libcamera-still -o test.jpg")
    print("- Check camera connection: ls /dev/video*")
    print("- Reboot after enabling camera: sudo reboot")

if __name__ == "__main__":
    main()
