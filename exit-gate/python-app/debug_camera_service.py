#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug script untuk Camera Service di Raspberry Pi
"""

from __future__ import print_function
import sys
import os

print("=== Camera Service Debug - Raspberry Pi ===")
print("Python version: {}".format(sys.version))

# Test PIL/Pillow import dengan detail
print("\n--- Testing PIL/Pillow Import ---")

PIL_WORKING = False
PIL_METHOD = None

# Method 1: Modern PIL/Pillow
try:
    from PIL import Image
    import io
    PIL_WORKING = True
    PIL_METHOD = "PIL/Pillow (modern)"
    print("✓ PIL/Pillow (modern): SUCCESS")
    if hasattr(Image, '__version__'):
        print("  Version: {}".format(Image.__version__))
    if hasattr(Image, 'PILLOW_VERSION'):
        print("  Pillow Version: {}".format(Image.PILLOW_VERSION))
except ImportError as e:
    print("✗ PIL/Pillow (modern): FAILED - {}".format(e))

# Method 2: Old PIL
if not PIL_WORKING:
    try:
        import Image
        import io
        PIL_WORKING = True
        PIL_METHOD = "PIL (old)"
        print("✓ PIL (old): SUCCESS")
    except ImportError as e:
        print("✗ PIL (old): FAILED - {}".format(e))

# Test basic image operations if PIL available
if PIL_WORKING:
    print("\n--- Testing PIL Image Operations ---")
    try:
        # Test creating image
        if PIL_METHOD == "PIL/Pillow (modern)":
            from PIL import Image
            test_img = Image.new('RGB', (100, 100), color='red')
        else:
            test_img = Image.new('RGB', (100, 100), color='red')
        
        print("✓ Image creation: SUCCESS ({}x{})".format(test_img.size[0], test_img.size[1]))
        
        # Test save to BytesIO
        import io
        output = io.BytesIO()
        test_img.save(output, format='JPEG')
        print("✓ Image save to BytesIO: SUCCESS ({} bytes)".format(len(output.getvalue())))
        
        # Test base64 encoding
        import base64
        img_data = base64.b64encode(output.getvalue())
        print("✓ Base64 encoding: SUCCESS ({} bytes)".format(len(img_data)))
        
    except Exception as e:
        print("✗ PIL operations: FAILED - {}".format(e))
        PIL_WORKING = False

# Test camera service import
print("\n--- Testing Camera Service Import ---")

# Add app directory to path if we're not in it
current_dir = os.getcwd()
if not current_dir.endswith('app'):
    app_dir = os.path.join(os.path.dirname(__file__), 'app')
    if os.path.exists(app_dir):
        sys.path.insert(0, app_dir)
        os.chdir(app_dir)
        print("Changed to app directory: {}".format(app_dir))

try:
    import config
    print("✓ Config module: SUCCESS")
except ImportError as e:
    print("✗ Config module: FAILED - {}".format(e))
    print("  Make sure you're in the app directory or run from project root")

try:
    import camera_service
    print("✓ Camera service module: SUCCESS")
    
    # Test camera service instance
    from camera_service import camera_service as cs
    print("✓ Camera service instance: SUCCESS")
    
    # Test PIL availability in camera service
    from camera_service import PIL_AVAILABLE
    print("Camera service PIL_AVAILABLE: {}".format(PIL_AVAILABLE))
    
    # Test camera status
    status = cs.get_cameras_status()
    print("Camera status: {}".format(status))
    
except ImportError as e:
    print("✗ Camera service: FAILED - {}".format(e))
    print("  Error details: {}".format(str(e)))
except Exception as e:
    print("✗ Camera service error: {}".format(e))

# Test specific PIL import methods
print("\n--- Testing Alternative PIL Import Methods ---")

# Method 1: System PIL
try:
    import PIL
    print("✓ PIL package available")
    print("  PIL path: {}".format(PIL.__file__))
except ImportError:
    print("✗ PIL package not found")

# Method 2: Check PIL installation location
try:
    import PIL.Image
    print("✓ PIL.Image available")
except ImportError as e:
    print("✗ PIL.Image: {}".format(e))

# Check system packages
print("\n--- System Package Information ---")
import subprocess

try:
    # Check if python-pil is installed
    result = subprocess.check_output(['dpkg', '-l', 'python-pil'], stderr=subprocess.STDOUT)
    print("✓ python-pil system package: INSTALLED")
except subprocess.CalledProcessError:
    print("✗ python-pil system package: NOT INSTALLED")
    print("  Install with: sudo apt-get install python-pil")
except OSError:
    print("? dpkg not available (not on Debian/Ubuntu system)")

try:
    # Check python-pil.imagetk
    result = subprocess.check_output(['dpkg', '-l', 'python-pil.imagetk'], stderr=subprocess.STDOUT)
    print("✓ python-pil.imagetk system package: INSTALLED")
except subprocess.CalledProcessError:
    print("✗ python-pil.imagetk system package: NOT INSTALLED")
    print("  Install with: sudo apt-get install python-pil.imagetk")
except OSError:
    print("? dpkg not available")

# Check pip packages
print("\n--- Pip Package Information ---")
try:
    import pip
    installed_packages = pip.get_installed_distributions()
    pil_packages = [pkg for pkg in installed_packages if 'pil' in pkg.project_name.lower()]
    
    if pil_packages:
        for pkg in pil_packages:
            print("✓ Pip package: {} {}".format(pkg.project_name, pkg.version))
    else:
        print("? No PIL-related pip packages found")
        
except Exception as e:
    print("? Could not check pip packages: {}".format(e))

# Environment information
print("\n--- Environment Information ---")
print("Python executable: {}".format(sys.executable))
print("Python path: {}".format(sys.path[:3]))  # First 3 entries
print("Current working directory: {}".format(os.getcwd()))

# Recommendations
print("\n=== RECOMMENDATIONS ===")

if not PIL_WORKING:
    print("PIL/Pillow is not working. Try these solutions:")
    print("1. Install system PIL: sudo apt-get install python-pil python-pil.imagetk")
    print("2. Install specific Pillow: pip install pillow==5.1.0")
    print("3. Install build dependencies: sudo apt-get install libjpeg-dev zlib1g-dev")
    print("4. Uninstall and reinstall: pip uninstall pillow && pip install pillow==5.1.0")
else:
    print("PIL/Pillow is working with method: {}".format(PIL_METHOD))
    print("Camera service should work now.")

print("\nTo test camera service after fixing PIL:")
print("cd app && python -c \"import camera_service; print('Camera service OK')\"")
