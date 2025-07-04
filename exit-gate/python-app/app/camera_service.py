#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Camera Service for Exit Gate System
Compatible with Python 2.7 and 3.x
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import base64
import time
from typing import Optional, Dict  # For IDE support

import requests
from requests.auth import HTTPBasicAuth

from config import config

logger = logging.getLogger(__name__)

# Handle PIL/Pillow import with fallback for Raspberry Pi
PIL_AVAILABLE = False
try:
    from PIL import Image
    import io
    PIL_AVAILABLE = True
    logger.info("PIL/Pillow loaded successfully")
except ImportError:
    try:
        import Image  # Old PIL import
        import io
        PIL_AVAILABLE = True
        logger.info("Old PIL loaded successfully")
    except ImportError:
        logger.warning("PIL/Pillow not available - camera features will be limited")
        PIL_AVAILABLE = False

# Raspberry Pi camera imports for Python 3.10+
PICAMERA_AVAILABLE = False
PICAMERA2_AVAILABLE = False
CV2_AVAILABLE = False

try:
    # Try new picamera2 library (recommended for Raspberry Pi OS Bullseye+)
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
    logger.info("picamera2 loaded successfully (recommended for Python 3.10+)")
except ImportError:
    try:
        # Try legacy picamera library
        from picamera import PiCamera
        PICAMERA_AVAILABLE = True
        logger.info("picamera (legacy) loaded successfully")
    except ImportError:
        logger.info("No Raspberry Pi camera libraries available")

try:
    # Try OpenCV for additional camera support
    import cv2
    CV2_AVAILABLE = True
    logger.info("OpenCV loaded successfully")
except ImportError:
    logger.info("OpenCV not available")

class CameraCapture(object):
    """Camera capture result"""
    
    def __init__(self, success=False, image_data=None, error_message=None):
        self.success = success
        self.image_data = image_data  # base64 encoded
        self.error_message = error_message
        self.timestamp = time.time()
    
    def to_dict(self):
        return {
            'success': self.success,
            'image_data': self.image_data,
            'error_message': self.error_message,
            'timestamp': self.timestamp
        }

class CameraConfig(object):
    """Camera configuration"""
    
    def __init__(self, name="default"):
        self.name = name
        self.ip = config.get('camera', 'plate_camera_ip', '192.168.1.100')
        self.username = config.get('camera', 'plate_camera_username', 'admin')
        self.password = config.get('camera', 'plate_camera_password', 'admin123')
        
        # Default snapshot path - will be auto-detected by brand
        self.snapshot_path = config.get('camera', 'snapshot_path', 'Streaming/Channels/1/picture')
        
        # Camera brand for specific URL patterns
        self.brand = config.get('camera', 'camera_brand', 'auto')  # auto, hikvision, dahua, glenz, generic
        
        self.timeout = config.getint('camera', 'capture_timeout', 5)
        self.enabled = config.getboolean('camera', 'enabled', True)
    
    def get_snapshot_url(self):
        """Get snapshot URL based on camera brand"""
        base_url = "http://{}".format(self.ip)
        
        # Brand-specific URL patterns
        if self.brand.lower() == 'hikvision' or self.brand.lower() == 'hik':
            # Hikvision standard URLs
            return "{}/ISAPI/Streaming/channels/101/picture".format(base_url)
        elif self.brand.lower() == 'dahua':
            # Dahua standard URLs
            return "{}/cgi-bin/snapshot.cgi?channel=1".format(base_url)
        elif self.brand.lower() == 'glenz':
            # Glenz camera URLs (similar to generic ONVIF)
            return "{}/onvif-http/snapshot?Profile_1".format(base_url)
        elif self.brand.lower() == 'axis':
            # Axis camera URLs
            return "{}/axis-cgi/jpg/image.cgi".format(base_url)
        elif self.brand.lower() == 'generic' or self.brand.lower() == 'onvif':
            # Generic ONVIF snapshot
            return "{}/onvif/media_service/snapshot?ProfileToken=Profile_1".format(base_url)
        elif self.brand.lower() == 'custom':
            # Custom URL with authentication embedded
            if hasattr(self, 'custom_path') and self.custom_path:
                # Build URL with embedded authentication
                auth_url = "http://{}:{}@{}/{}".format(
                    self.username, self.password, self.ip, self.custom_path
                )
                return auth_url
            else:
                # Use default snapshot path
                return "{}/{}".format(base_url, self.snapshot_path)
        else:
            # Use configured path or auto-detect
            if self.brand.lower() == 'auto':
                # Try to auto-detect based on common patterns
                return self._auto_detect_url(base_url)
            else:
                # Use custom snapshot path
                return "{}/{}".format(base_url, self.snapshot_path)
    
    def _auto_detect_url(self, base_url):
        """Auto-detect camera URL by trying common patterns"""
        # Return the configured path as fallback, but we could enhance this
        # to actually test different URLs
        return "{}/{}".format(base_url, self.snapshot_path)

class CameraService(object):
    """CCTV Camera service for image capture"""
    
    def __init__(self):
        self.cameras = {}
        self._initialize_cameras()
    
    def log(self, message):
        """Log message"""
        logger.info(message)
        print("[CAMERA] {}".format(message))
    
    def _initialize_cameras(self):
        """Initialize camera configurations"""
        # Exit camera (Kamera Keluar) - Primary camera
        exit_config = CameraConfig("exit")
        exit_config.ip = config.get('camera', 'exit_camera_ip', '192.168.10.70')
        exit_config.username = config.get('camera', 'exit_camera_username', 'admin')
        exit_config.password = config.get('camera', 'exit_camera_password', 'admin')
        exit_config.brand = config.get('camera', 'exit_camera_brand', 'custom')
        exit_config.custom_path = config.get('camera', 'exit_camera_path', 'Snapshot/1/RemoteImageCapture?ImageFormat=2')
        exit_config.snapshot_path = exit_config.custom_path  # Fallback
        exit_config.timeout = config.getint('camera', 'capture_timeout', 10)
        self.cameras['exit'] = exit_config
        
        # Optional driver camera (disabled by default)
        driver_enabled = config.getboolean('camera', 'driver_camera_enabled', False)
        if driver_enabled:
            driver_config = CameraConfig("driver")
            driver_config.ip = config.get('camera', 'driver_camera_ip', '192.168.1.101')
            driver_config.username = config.get('camera', 'driver_camera_username', 'admin')
            driver_config.password = config.get('camera', 'driver_camera_password', 'admin123')
            driver_config.brand = config.get('camera', 'driver_camera_brand', 'auto')
            driver_config.enabled = True
            self.cameras['driver'] = driver_config
            logger.info("Driver camera enabled")
        else:
            logger.info("Driver camera disabled in configuration")
        
        logger.info("Initialized {} cameras".format(len(self.cameras)))
        
        # Auto-detect and configure Raspberry Pi cameras if available
        self._auto_configure_raspberry_pi()
    
    def _auto_configure_raspberry_pi(self):
        """Auto-configure Raspberry Pi cameras if available"""
        try:
            from config import is_raspberry_pi
            
            # Only auto-configure on Raspberry Pi
            if not is_raspberry_pi():
                return
            
            # Check if Raspberry Pi camera is enabled in config
            rpi_camera_enabled = config.getboolean('camera', 'raspberry_pi_enabled', True)
            if not rpi_camera_enabled:
                logger.info("Raspberry Pi camera disabled in configuration")
                return
            
            # Detect Raspberry Pi cameras
            cameras = self.detect_raspberry_pi_cameras()
            
            if cameras:
                # Use first detected camera as exit camera
                camera_info = cameras[0]
                
                # Create Raspberry Pi camera config
                rpi_config = CameraConfig("rpi_exit")
                rpi_config.ip = "localhost"  # Local camera
                rpi_config.camera_type = "raspberry_pi"
                rpi_config.camera_id = camera_info['id']
                rpi_config.library = camera_info['type']
                rpi_config.enabled = True
                
                # Add to cameras (replace exit camera if exists)
                self.cameras['exit'] = rpi_config
                
                logger.info("Auto-configured Raspberry Pi camera as exit camera: {} (ID: {})".format(
                    camera_info['model'], camera_info['id']))
            else:
                logger.info("No Raspberry Pi cameras detected for auto-configuration")
                
        except Exception as e:
            logger.warning("Error during Raspberry Pi auto-configuration: {}".format(str(e)))
    
    def capture_image(self, camera_name="exit"):
        """Capture image from specified camera (enhanced with Raspberry Pi support)"""
        if camera_name not in self.cameras:
            return CameraCapture(
                success=False,
                error_message="Camera '{}' not found".format(camera_name)
            )
        
        camera = self.cameras[camera_name]
        
        if not camera.enabled:
            return CameraCapture(
                success=False,
                error_message="Camera '{}' is disabled".format(camera_name)
            )
        
        # Check if this is a Raspberry Pi camera
        if hasattr(camera, 'camera_type') and camera.camera_type == "raspberry_pi":
            camera_id = getattr(camera, 'camera_id', 0)
            use_picamera2 = getattr(camera, 'library', 'picamera2') == 'picamera2'
            return self.capture_raspberry_pi_camera(camera_id, use_picamera2)
        
        # Standard network camera capture
        try:
            # Build snapshot URL using brand-specific logic
            snapshot_url = camera.get_snapshot_url()
            
            # Check if URL already contains authentication
            if '@' in snapshot_url and '://' in snapshot_url:
                # URL already contains embedded authentication
                self.log("Attempting capture from: {}".format(snapshot_url.replace(camera.password, '***')))
                
                # Make HTTP request without additional auth
                response = requests.get(
                    snapshot_url,
                    timeout=camera.timeout,
                    stream=True
                )
            else:
                # Use separate authentication
                self.log("Attempting capture from: {}".format(snapshot_url))
                
                # Make HTTP request with auth
                auth = HTTPBasicAuth(camera.username, camera.password)
                response = requests.get(
                    snapshot_url,
                    auth=auth,
                    timeout=camera.timeout,
                    stream=True
                )
            
            if response.status_code == 200:
                # Convert image to base64
                image_data = base64.b64encode(response.content).decode('utf-8')
                
                logger.info("Successfully captured image from camera '{}'".format(camera_name))
                return CameraCapture(
                    success=True,
                    image_data=image_data
                )
            else:
                error_msg = "HTTP {} from camera '{}'".format(response.status_code, camera_name)
                logger.error(error_msg)
                return CameraCapture(
                    success=False,
                    error_message=error_msg
                )
        
        except requests.exceptions.Timeout:
            error_msg = "Timeout capturing from camera '{}'".format(camera_name)
            logger.error(error_msg)
            return CameraCapture(
                success=False,
                error_message=error_msg
            )
        
        except requests.exceptions.ConnectionError:
            error_msg = "Connection error to camera '{}'".format(camera_name)
            logger.error(error_msg)
            return CameraCapture(
                success=False,
                error_message=error_msg
            )
        
        except Exception as e:
            error_msg = "Unexpected error capturing from camera '{}': {}".format(camera_name, str(e))
            logger.error(error_msg)
            return CameraCapture(
                success=False,
                error_message=error_msg
            )
    
    def capture_exit_images(self):
        """Capture images from available cameras for exit processing"""
        results = {}
        
        # Capture exit camera (primary)
        exit_result = self.capture_image('exit')
        results['exit'] = exit_result
        
        # Capture driver camera if available
        if 'driver' in self.cameras:
            driver_result = self.capture_image('driver')
            results['driver'] = driver_result
        else:
            # Create dummy result for driver camera
            driver_result = CameraCapture(success=False, error_message="Driver camera not configured")
            results['driver'] = driver_result
        
        # Return combined result - prioritize exit camera
        success = exit_result.success  # Main success based on exit camera
        image_data = None
        
        if exit_result.success:
            # Use exit camera image as primary
            image_data = exit_result.image_data
            
            # If driver camera also available, could combine images here
            if 'driver' in self.cameras and results['driver'].success:
                # For now, just use exit camera. Could enhance to combine images
                pass
        elif 'driver' in self.cameras and results['driver'].success:
            # Fallback to driver camera if exit camera fails
            image_data = results['driver'].image_data
            success = True
        
        # Collect error messages
        error_messages = []
        if not exit_result.success:
            error_messages.append("Exit camera: {}".format(exit_result.error_message))
        if 'driver' in self.cameras and not results['driver'].success:
            error_messages.append("Driver camera: {}".format(results['driver'].error_message))
        
        return CameraCapture(
            success=success,
            image_data=image_data,
            error_message="; ".join(error_messages) if error_messages and not success else None
        )
    
    def test_camera(self, camera_name="plate"):
        """Test camera connectivity"""
        logger.info("Testing camera: {}".format(camera_name))
        
        if camera_name not in self.cameras:
            return False
        
        result = self.capture_image(camera_name)
        if result.success:
            logger.info("Camera '{}' test successful".format(camera_name))
            return True
        else:
            logger.error("Camera '{}' test failed: {}".format(camera_name, result.error_message))
            return False
    
    def test_all_cameras(self):
        """Test all configured cameras"""
        results = {}
        for camera_name in self.cameras:
            results[camera_name] = self.test_camera(camera_name)
        return results
    
    def get_camera_info(self, camera_name):
        """Get camera configuration info"""
        if camera_name not in self.cameras:
            return None
        
        camera = self.cameras[camera_name]
        return {
            'name': camera.name,
            'ip': camera.ip,
            'username': camera.username,
            'enabled': camera.enabled,
            'snapshot_url': "http://{}/{}".format(camera.ip, camera.snapshot_path)
        }
    
    def update_camera_config(self, camera_name, **kwargs):
        """Update camera configuration"""
        if camera_name not in self.cameras:
            return False
        
        camera = self.cameras[camera_name]
        for key, value in kwargs.items():
            if hasattr(camera, key):
                setattr(camera, key, value)
                logger.info("Updated camera '{}' {}: {}".format(camera_name, key, value))
        
        return True
    
    def enable_camera(self, camera_name):
        """Enable camera"""
        if camera_name in self.cameras:
            self.cameras[camera_name].enabled = True
            logger.info("Camera '{}' enabled".format(camera_name))
            return True
        return False
    
    def disable_camera(self, camera_name):
        """Disable camera"""
        if camera_name in self.cameras:
            self.cameras[camera_name].enabled = False
            logger.info("Camera '{}' disabled".format(camera_name))
            return True
        return False
    
    def get_cameras_status(self):
        """Get status of all cameras"""
        status = {}
        for camera_name, camera in self.cameras.items():
            status[camera_name] = {
                'enabled': camera.enabled,
                'ip': camera.ip,
                'last_test': None  # Would be enhanced to track last test time
            }
        return status
    
    # ============== RASPBERRY PI CAMERA METHODS ==============
    
    def capture_raspberry_pi_camera(self, camera_id=0, use_picamera2=True):
        """Capture image from Raspberry Pi camera module"""
        try:
            if use_picamera2 and PICAMERA2_AVAILABLE:
                return self._capture_with_picamera2(camera_id)
            elif PICAMERA_AVAILABLE:
                return self._capture_with_picamera_legacy(camera_id)
            elif CV2_AVAILABLE:
                return self._capture_with_opencv(camera_id)
            else:
                return CameraCapture(
                    success=False,
                    error_message="No Raspberry Pi camera libraries available. Install: sudo apt install python3-picamera2"
                )
        except Exception as e:
            error_msg = "Error capturing from Raspberry Pi camera: {}".format(str(e))
            logger.error(error_msg)
            return CameraCapture(success=False, error_message=error_msg)
    
    def _capture_with_picamera2(self, camera_id=0):
        """Capture with picamera2 (recommended for Python 3.10+)"""
        try:
            picam2 = Picamera2(camera_id)
            
            # Configure camera
            config = picam2.create_still_configuration()
            picam2.configure(config)
            
            # Start camera
            picam2.start()
            time.sleep(2)  # Allow camera to warm up
            
            # Capture to memory
            stream = io.BytesIO()
            picam2.capture_file(stream, format='jpeg')
            
            # Stop camera
            picam2.stop()
            
            # Encode to base64
            stream.seek(0)
            image_data = base64.b64encode(stream.getvalue()).decode('utf-8')
            
            logger.info("Successfully captured image from Raspberry Pi camera (picamera2)")
            return CameraCapture(success=True, image_data=image_data)
            
        except Exception as e:
            error_msg = "picamera2 capture error: {}".format(str(e))
            logger.error(error_msg)
            return CameraCapture(success=False, error_message=error_msg)
    
    def _capture_with_picamera_legacy(self, camera_id=0):
        """Capture with legacy picamera library"""
        try:
            from picamera import PiCamera
            
            with PiCamera() as camera:
                # Configure camera
                camera.resolution = (1024, 768)
                camera.rotation = 0
                
                # Warm up
                time.sleep(2)
                
                # Capture to memory
                stream = io.BytesIO()
                camera.capture(stream, format='jpeg')
                
                # Encode to base64
                stream.seek(0)
                image_data = base64.b64encode(stream.getvalue()).decode('utf-8')
                
                logger.info("Successfully captured image from Raspberry Pi camera (legacy picamera)")
                return CameraCapture(success=True, image_data=image_data)
                
        except Exception as e:
            error_msg = "Legacy picamera capture error: {}".format(str(e))
            logger.error(error_msg)
            return CameraCapture(success=False, error_message=error_msg)
    
    def _capture_with_opencv(self, camera_id=0):
        """Capture with OpenCV (fallback option)"""
        try:
            cap = cv2.VideoCapture(camera_id)
            
            if not cap.isOpened():
                return CameraCapture(
                    success=False,
                    error_message="Could not open camera {}".format(camera_id)
                )
            
            # Capture frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return CameraCapture(
                    success=False,
                    error_message="Could not capture frame from camera {}".format(camera_id)
                )
            
            # Convert to JPEG and base64
            _, buffer = cv2.imencode('.jpg', frame)
            image_data = base64.b64encode(buffer).decode('utf-8')
            
            logger.info("Successfully captured image from camera {} (OpenCV)".format(camera_id))
            return CameraCapture(success=True, image_data=image_data)
            
        except Exception as e:
            error_msg = "OpenCV capture error: {}".format(str(e))
            logger.error(error_msg)
            return CameraCapture(success=False, error_message=error_msg)
    
    def detect_raspberry_pi_cameras(self):
        """Detect available Raspberry Pi cameras"""
        cameras_found = []
        
        if PICAMERA2_AVAILABLE:
            try:
                # Try to detect cameras with picamera2
                global_cameras = Picamera2.global_camera_info()
                for i, camera_info in enumerate(global_cameras):
                    cameras_found.append({
                        'id': i,
                        'type': 'picamera2',
                        'model': camera_info.get('Model', 'Unknown'),
                        'location': camera_info.get('Location', 'Unknown')
                    })
                logger.info("Found {} Raspberry Pi cameras (picamera2)".format(len(cameras_found)))
            except Exception as e:
                logger.warning("Error detecting cameras with picamera2: {}".format(str(e)))
        
        elif PICAMERA_AVAILABLE:
            try:
                # Try legacy picamera detection
                from picamera import PiCamera
                camera = PiCamera()
                camera.close()
                cameras_found.append({
                    'id': 0,
                    'type': 'picamera_legacy',
                    'model': 'Raspberry Pi Camera',
                    'location': 'CSI'
                })
                logger.info("Found Raspberry Pi camera (legacy picamera)")
            except Exception as e:
                logger.warning("No legacy picamera found: {}".format(str(e)))
        
        # Try OpenCV detection as fallback
        if CV2_AVAILABLE and not cameras_found:
            for i in range(3):  # Check first 3 camera indices
                try:
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        cameras_found.append({
                            'id': i,
                            'type': 'opencv',
                            'model': 'USB/Built-in Camera',
                            'location': '/dev/video{}'.format(i)
                        })
                        cap.release()
                except:
                    pass
            if cameras_found:
                logger.info("Found {} cameras (OpenCV)".format(len(cameras_found)))
        
        return cameras_found
    
    def auto_configure_raspberry_pi_camera(self):
        """Auto-configure Raspberry Pi camera as exit camera"""
        cameras = self.detect_raspberry_pi_cameras()
        
        if not cameras:
            logger.warning("No Raspberry Pi cameras detected")
            return False
        
        # Use first detected camera
        camera_info = cameras[0]
        
        # Create Raspberry Pi camera config
        rpi_config = CameraConfig("rpi_exit")
        rpi_config.ip = "localhost"  # Local camera
        rpi_config.camera_type = "raspberry_pi"
        rpi_config.camera_id = camera_info['id']
        rpi_config.library = camera_info['type']
        rpi_config.enabled = True
        
        # Add to cameras
        self.cameras['rpi_exit'] = rpi_config
        
        logger.info("Auto-configured Raspberry Pi camera: {} (ID: {})".format(
            camera_info['model'], camera_info['id']))
        
        return True
    
    # Override capture_image to support Raspberry Pi cameras
    def capture_image_enhanced(self, camera_name="exit"):
        """Enhanced capture method that supports both network and Raspberry Pi cameras"""
        if camera_name not in self.cameras:
            return CameraCapture(
                success=False,
                error_message="Camera '{}' not found".format(camera_name)
            )
        
        camera = self.cameras[camera_name]
        
        if not camera.enabled:
            return CameraCapture(
                success=False,
                error_message="Camera '{}' is disabled".format(camera_name)
            )
        
        # Check if this is a Raspberry Pi camera
        if hasattr(camera, 'camera_type') and camera.camera_type == "raspberry_pi":
            camera_id = getattr(camera, 'camera_id', 0)
            use_picamera2 = getattr(camera, 'library', 'picamera2') == 'picamera2'
            return self.capture_raspberry_pi_camera(camera_id, use_picamera2)
        else:
            # Use standard network camera capture
            return self.capture_image(camera_name)
    
    # ============== END RASPBERRY PI METHODS ==============
    
    def create_combined_exit_image(self, plate_image=None, driver_image=None):
        """Create combined exit image from plate and driver cameras"""
        try:
            images = []
            
            if plate_image:
                # Decode base64 image
                plate_data = base64.b64decode(plate_image)
                plate_img = Image.open(io.BytesIO(plate_data))
                images.append(plate_img)
            
            if driver_image:
                driver_data = base64.b64decode(driver_image)
                driver_img = Image.open(io.BytesIO(driver_data))
                images.append(driver_img)
            
            if not images:
                return None
            
            if len(images) == 1:
                # Only one image, return as-is
                output = io.BytesIO()
                images[0].save(output, format='JPEG', quality=85)
                return base64.b64encode(output.getvalue()).decode('utf-8')
            
            # Combine images side by side
            total_width = sum(img.width for img in images)
            max_height = max(img.height for img in images)
            
            combined = Image.new('RGB', (total_width, max_height), (255, 255, 255))
            
            x_offset = 0
            for img in images:
                combined.paste(img, (x_offset, 0))
                x_offset += img.width
            
            # Convert to base64
            output = io.BytesIO()
            combined.save(output, format='JPEG', quality=85)
            return base64.b64encode(output.getvalue()).decode('utf-8')
            
        except Exception as e:
            logger.error("Error creating combined image: {}".format(str(e)))
            return None

# Global camera service instance
camera_service = CameraService()

# Test functions
def test_camera_service():
    """Test camera service functionality"""
    print("Testing camera service...")
    
    # Test all cameras
    results = camera_service.test_all_cameras()
    for camera_name, success in results.items():
        print("Camera '{}': {}".format(camera_name, "OK" if success else "FAILED"))
    
    # Test image capture
    plate_result = camera_service.capture_image('plate')
    print("Plate camera capture: {}".format("SUCCESS" if plate_result.success else "FAILED"))
    if not plate_result.success:
        print("Error: {}".format(plate_result.error_message))
    
    # Test exit image capture
    exit_result = camera_service.capture_exit_images()
    print("Exit images capture: {}".format("SUCCESS" if exit_result.success else "FAILED"))
    if not exit_result.success:
        print("Error: {}".format(exit_result.error_message))

if __name__ == "__main__":
    test_camera_service()
