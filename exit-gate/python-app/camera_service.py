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
from PIL import Image
import io

from config import config

logger = logging.getLogger(__name__)

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
        self.snapshot_path = config.get('camera', 'snapshot_path', 'Streaming/Channels/1/picture')
        self.timeout = config.getint('camera', 'capture_timeout', 5)
        self.enabled = config.getboolean('camera', 'enabled', True)

class CameraService(object):
    """CCTV Camera service for image capture"""
    
    def __init__(self):
        self.cameras = {}
        self._initialize_cameras()
    
    def _initialize_cameras(self):
        """Initialize camera configurations"""
        # Plate camera
        plate_config = CameraConfig("plate")
        plate_config.ip = config.get('camera', 'plate_camera_ip', '192.168.1.100')
        plate_config.username = config.get('camera', 'plate_camera_username', 'admin')
        plate_config.password = config.get('camera', 'plate_camera_password', 'admin123')
        self.cameras['plate'] = plate_config
        
        # Driver camera
        driver_config = CameraConfig("driver")
        driver_config.ip = config.get('camera', 'driver_camera_ip', '192.168.1.101')
        driver_config.username = config.get('camera', 'driver_camera_username', 'admin')
        driver_config.password = config.get('camera', 'driver_camera_password', 'admin123')
        self.cameras['driver'] = driver_config
        
        logger.info("Initialized {} cameras".format(len(self.cameras)))
    
    def capture_image(self, camera_name="plate"):
        """Capture image from specified camera"""
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
        
        try:
            # Build snapshot URL
            snapshot_url = "http://{}/{}".format(camera.ip, camera.snapshot_path)
            
            # Make HTTP request
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
        """Capture images from both cameras for exit processing"""
        results = {}
        
        # Capture plate camera
        plate_result = self.capture_image('plate')
        results['plate'] = plate_result
        
        # Capture driver camera
        driver_result = self.capture_image('driver')
        results['driver'] = driver_result
        
        # Return combined result
        success = plate_result.success or driver_result.success
        image_data = None
        
        if plate_result.success and driver_result.success:
            # Combine images or use primary (plate)
            image_data = plate_result.image_data
        elif plate_result.success:
            image_data = plate_result.image_data
        elif driver_result.success:
            image_data = driver_result.image_data
        
        error_messages = []
        if not plate_result.success:
            error_messages.append("Plate camera: {}".format(plate_result.error_message))
        if not driver_result.success:
            error_messages.append("Driver camera: {}".format(driver_result.error_message))
        
        return CameraCapture(
            success=success,
            image_data=image_data,
            error_message="; ".join(error_messages) if error_messages else None
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
