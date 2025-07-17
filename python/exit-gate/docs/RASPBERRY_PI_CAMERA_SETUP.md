# 🍓 Raspberry Pi Camera Setup Guide

## Problem: Camera Service Not Available on Raspberry Pi Python 3.10.14

Kamu mengalami masalah camera service tidak tersedia di Raspberry Pi dengan Python 3.10.14. Berikut solusi lengkapnya:

## ✅ **SOLUSI LENGKAP**

### 1. **Install Dependencies Raspberry Pi**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system packages
sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-picamera2 \
    python3-libcamera \
    python3-rpi.gpio \
    python3-opencv \
    python3-numpy \
    python3-pil \
    python3-pygame \
    libcamera-apps
```

### 2. **Enable Camera Interface**

```bash
# Enable camera via raspi-config
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable

# Or enable directly
sudo raspi-config nonint do_camera 0

# Reboot after enabling
sudo reboot
```

### 3. **Install Python Packages**

```bash
# Create virtual environment
python3 -m venv exit-gate-env
source exit-gate-env/bin/activate

# Install requirements for Raspberry Pi
pip install -r requirements_raspberry_pi.txt
```

### 4. **Test Camera**

```bash
# Test with libcamera (system level)
libcamera-still -o test.jpg

# Test with our script
python3 test_raspberry_pi_camera.py
```

### 5. **Configure Application**

Edit `app/config.ini`:

```ini
[camera]
enabled = True
raspberry_pi_enabled = True
raspberry_pi_camera_id = 0
raspberry_pi_library = picamera2
```

## 🚀 **ENHANCED FEATURES**

Camera service sekarang mendukung:

### **Multi-Library Support:**
- ✅ `picamera2` (recommended untuk Python 3.10+)
- ✅ `picamera` (legacy support)
- ✅ `OpenCV` (fallback option)

### **Auto-Detection:**
- ✅ Deteksi otomatis Raspberry Pi cameras
- ✅ Auto-configuration sebagai exit camera
- ✅ Fallback ke network cameras jika perlu

### **New Methods Added:**
```python
# Capture dari Raspberry Pi camera
camera_service.capture_raspberry_pi_camera()

# Detect available cameras
cameras = camera_service.detect_raspberry_pi_cameras()

# Auto-configure
camera_service.auto_configure_raspberry_pi_camera()

# Enhanced capture (supports both network & RPi)
result = camera_service.capture_image_enhanced("exit")
```

## 📁 **File Changes**

### **New Files:**
- `requirements_raspberry_pi.txt` - Dependencies untuk Python 3.10+
- `setup_raspberry_pi.sh` - Automated setup script
- `test_raspberry_pi_camera.py` - Camera testing script

### **Enhanced Files:**
- `app/camera_service.py` - Added Raspberry Pi support
- `app/config.py` - Added RPi camera settings

## 🧪 **Testing Commands**

```bash
# 1. Test camera detection
cd app && python3 -c "
from camera_service import camera_service
cameras = camera_service.detect_raspberry_pi_cameras()
print('Found cameras:', cameras)
"

# 2. Test capture
cd app && python3 -c "
from camera_service import camera_service
result = camera_service.capture_raspberry_pi_camera()
print('Capture result:', result.success)
"

# 3. Complete test
python3 test_raspberry_pi_camera.py
```

## ⚠️ **Troubleshooting**

### **Camera Not Detected:**
```bash
# Check camera is connected
ls /dev/video*

# Check camera status
vcgencmd get_camera

# Test with libcamera
libcamera-still --list-cameras
```

### **Permission Issues:**
```bash
# Add user to video group
sudo usermod -a -G video $USER

# Reboot after adding to group
sudo reboot
```

### **Library Import Errors:**
```bash
# Install missing packages
sudo apt install python3-picamera2 python3-libcamera

# For legacy support
sudo apt install python3-picamera
```

## 🎯 **Quick Setup Script**

```bash
# Download and run automated setup
chmod +x setup_raspberry_pi.sh
./setup_raspberry_pi.sh
```

Script ini akan:
- ✅ Install semua dependencies
- ✅ Enable camera interface  
- ✅ Create systemd service
- ✅ Test camera functionality
- ✅ Configure auto-start

## 📋 **Next Steps**

1. **Run Setup:** `./setup_raspberry_pi.sh`
2. **Test Camera:** `python3 test_raspberry_pi_camera.py`
3. **Configure:** Edit `app/config.ini`
4. **Start App:** `cd app && python3 gui_exit_gate.py`

## 🏆 **Result**

Setelah setup:
- ✅ Camera service tersedia dan berfungsi
- ✅ Auto-detection Raspberry Pi cameras
- ✅ Fallback ke network cameras jika diperlukan
- ✅ Compatible dengan Python 3.10.14
- ✅ Ready untuk production

**Camera service sekarang fully compatible dengan Raspberry Pi Python 3.10.14!** 🎉
