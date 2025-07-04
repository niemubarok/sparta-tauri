#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick PIL Check untuk Raspberry Pi
"""

from __future__ import print_function
import sys
import os

print("=== Quick PIL Check ===")

# Cek lokasi kita
current_dir = os.getcwd()
print("Current directory: {}".format(current_dir))

# Pindah ke app directory jika perlu
if not current_dir.endswith('app'):
    app_dir = os.path.join(os.path.dirname(__file__), 'app')
    if os.path.exists(app_dir):
        sys.path.insert(0, app_dir)
        os.chdir(app_dir)
        print("Changed to app directory: {}".format(app_dir))

# Test berbagai metode import PIL
print("\n1. Testing PIL/Pillow imports:")

# Method 1
try:
    from PIL import Image
    print("✓ from PIL import Image: SUCCESS")
    print("  Image module: {}".format(Image.__file__ if hasattr(Image, '__file__') else 'built-in'))
    if hasattr(Image, '__version__'):
        print("  Version: {}".format(Image.__version__))
except ImportError as e:
    print("✗ from PIL import Image: FAILED - {}".format(e))

# Method 2  
try:
    import PIL.Image
    print("✓ import PIL.Image: SUCCESS")
except ImportError as e:
    print("✗ import PIL.Image: FAILED - {}".format(e))

# Method 3
try:
    import Image
    print("✓ import Image (old): SUCCESS")
except ImportError as e:
    print("✗ import Image (old): FAILED - {}".format(e))

# Method 4
try:
    import PIL
    print("✓ import PIL: SUCCESS")
    print("  PIL path: {}".format(PIL.__file__))
    print("  PIL dir contents: {}".format([item for item in dir(PIL) if not item.startswith('_')][:5]))
except ImportError as e:
    print("✗ import PIL: FAILED - {}".format(e))

print("\n2. Testing io module:")
try:
    import io
    print("✓ io module: SUCCESS")
except ImportError as e:
    print("✗ io module: FAILED - {}".format(e))

print("\n3. Testing camera service import:")
try:
    import camera_service
    print("✓ camera_service import: SUCCESS")
    
    # Check PIL status
    from camera_service import PIL_AVAILABLE, PIL_ERROR_MESSAGE
    print("Camera service PIL_AVAILABLE: {}".format(PIL_AVAILABLE))
    if PIL_ERROR_MESSAGE:
        print("Camera service PIL_ERROR_MESSAGE: {}".format(PIL_ERROR_MESSAGE))
    
    # Get PIL status from service
    from camera_service import camera_service as cs
    pil_status = cs.get_pil_status()
    print("PIL Status from service:")
    for key, value in pil_status.items():
        print("  {}: {}".format(key, value))
        
except ImportError as e:
    print("✗ camera_service import: FAILED - {}".format(e))
except Exception as e:
    print("✗ camera_service error: {}".format(e))

print("\n4. Environment info:")
print("Python executable: {}".format(sys.executable))
print("Python version: {}".format(sys.version))
print("Sys.path (first 3): {}".format(sys.path[:3]))

# Recommendations
print("\n=== RECOMMENDATIONS ===")
print("If PIL is not working, try these commands on your Raspberry Pi:")
print("1. sudo apt-get update")
print("2. sudo apt-get install python-pil python-pil.imagetk python-imaging-tk")
print("3. sudo apt-get install libjpeg-dev zlib1g-dev libpng-dev")
print("4. pip install pillow==5.1.0")
print("5. Test: python -c \"from PIL import Image; print('PIL OK')\"")

print("\nTo run this debug:")
print("python debug_camera_service.py")
