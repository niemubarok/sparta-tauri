"""
Camera service for CCTV and USB camera integration
"""

import asyncio
import logging
import base64
import io
import time
from typing import Optional, Dict, Any, List, Tuple
import cv2
import numpy as np
import requests
from requests.auth import HTTPBasicAuth
from PIL import Image
import threading

from ..core.models import CameraCapture

logger = logging.getLogger(__name__)


class CameraService:
    """Camera service for both CCTV and USB cameras"""
    
    def __init__(self):
        self.usb_cameras = {}  # device_id -> cv2.VideoCapture
        self.cctv_cameras = {}  # camera_id -> config
        self.camera_status = {}
        self.capture_lock = threading.Lock()
    
    def initialize(self):
        """Initialize camera service"""
        logger.info("Camera service ready")
    
    def cleanup(self):
        """Cleanup camera resources"""
        for camera_id, cap in self.usb_cameras.items():
            try:
                cap.release()
                logger.info(f"Released USB camera: {camera_id}")
            except Exception as e:
                logger.error(f"Error releasing camera {camera_id}: {e}")
        
        self.usb_cameras.clear()
        self.cctv_cameras.clear()
        self.camera_status.clear()
        logger.info("Camera service cleaned up")
    
    def add_cctv_camera(self, camera_id: str, ip: str, username: str = "admin", 
                       password: str = "admin", snapshot_path: str = "Streaming/Channels/1/picture"):
        """Add CCTV camera configuration"""
        self.cctv_cameras[camera_id] = {
            "ip": ip,
            "username": username,
            "password": password,
            "snapshot_path": snapshot_path,
            "url": f"http://{username}:{password}@{ip}/{snapshot_path}"
        }
        self.camera_status[camera_id] = "configured"
        logger.info(f"CCTV camera added: {camera_id} at {ip}")
    
    def add_usb_camera(self, camera_id: str, device_id: int = 0):
        """Add USB camera"""
        try:
            cap = cv2.VideoCapture(device_id)
            if cap.isOpened():
                self.usb_cameras[camera_id] = cap
                self.camera_status[camera_id] = "ready"
                logger.info(f"USB camera added: {camera_id} on device {device_id}")
            else:
                self.camera_status[camera_id] = "error"
                logger.error(f"Failed to open USB camera device {device_id}")
        except Exception as e:
            self.camera_status[camera_id] = "error"
            logger.error(f"Error adding USB camera {camera_id}: {e}")
    
    def capture_cctv_image(self, camera_id: str) -> Optional[str]:
        """Capture image from CCTV camera"""
        if camera_id not in self.cctv_cameras:
            logger.error(f"CCTV camera {camera_id} not configured")
            return None
        
        camera_config = self.cctv_cameras[camera_id]
        
        try:
            # Make HTTP request to get snapshot
            response = requests.get(
                camera_config["url"],
                timeout=10,
                auth=HTTPBasicAuth(camera_config["username"], camera_config["password"])
            )
            
            if response.status_code == 200:
                # Convert image to base64
                image_base64 = base64.b64encode(response.content).decode('utf-8')
                
                self.camera_status[camera_id] = "ready"
                logger.debug(f"CCTV image captured from {camera_id}")
                
                return f"data:image/jpeg;base64,{image_base64}"
            else:
                self.camera_status[camera_id] = "error"
                logger.error(f"CCTV camera {camera_id} returned status {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            self.camera_status[camera_id] = "timeout"
            logger.error(f"CCTV camera {camera_id} timeout")
            return None
        except Exception as e:
            self.camera_status[camera_id] = "error"
            logger.error(f"Error capturing from CCTV camera {camera_id}: {e}")
            return None
    
    def capture_usb_image(self, camera_id: str) -> Optional[str]:
        """Capture image from USB camera"""
        if camera_id not in self.usb_cameras:
            logger.error(f"USB camera {camera_id} not configured")
            return None
        
        cap = self.usb_cameras[camera_id]
        
        try:
            with self.capture_lock:
                # Read frame from camera
                ret, frame = cap.read()
                
                if not ret:
                    self.camera_status[camera_id] = "error"
                    logger.error(f"Failed to read frame from USB camera {camera_id}")
                    return None
                
                # Convert frame to JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                
                # Convert to base64
                image_base64 = base64.b64encode(buffer).decode('utf-8')
                
                self.camera_status[camera_id] = "ready"
                logger.debug(f"USB image captured from {camera_id}")
                
                return f"data:image/jpeg;base64,{image_base64}"
                
        except Exception as e:
            self.camera_status[camera_id] = "error"
            logger.error(f"Error capturing from USB camera {camera_id}: {e}")
            return None
    
    def capture_image(self, camera_id: str, camera_type: str) -> Optional[CameraCapture]:
        """Capture image from any camera type"""
        start_time = time.time()
        
        if camera_type == "cctv":
            image_data = self.capture_cctv_image(camera_id)
        elif camera_type == "usb":
            image_data = self.capture_usb_image(camera_id)
        else:
            logger.error(f"Unknown camera type: {camera_type}")
            return None
        
        if image_data is None:
            return None
        
        capture_time = time.time() - start_time
        
        return CameraCapture(
            camera_type=camera_type,
            camera_source=camera_id,
            image_base64=image_data
        )
    
    async def capture_image_async(self, camera_id: str, camera_type: str) -> Optional[CameraCapture]:
        """Async version of image capture"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.capture_image, camera_id, camera_type)
    
    def capture_both_cameras(self, plate_camera_id: str, plate_camera_type: str,
                           driver_camera_id: str = None, driver_camera_type: str = None) -> Dict[str, Optional[str]]:
        """Capture from both plate and driver cameras"""
        results = {}
        
        # Capture plate camera
        plate_capture = self.capture_image(plate_camera_id, plate_camera_type)
        results["plate"] = plate_capture.image_base64 if plate_capture else None
        
        # Capture driver camera if configured
        if driver_camera_id and driver_camera_type:
            driver_capture = self.capture_image(driver_camera_id, driver_camera_type)
            results["driver"] = driver_capture.image_base64 if driver_capture else None
        else:
            results["driver"] = None
        
        return results
    
    def test_camera(self, camera_id: str, camera_type: str) -> Dict[str, Any]:
        """Test camera connectivity and capture"""
        start_time = time.time()
        
        try:
            capture = self.capture_image(camera_id, camera_type)
            test_time = time.time() - start_time
            
            if capture:
                return {
                    "success": True,
                    "message": f"Camera {camera_id} test successful",
                    "capture_time": test_time,
                    "image_size": len(capture.image_base64) if capture.image_base64 else 0
                }
            else:
                return {
                    "success": False,
                    "message": f"Camera {camera_id} test failed - no image captured",
                    "capture_time": test_time
                }
                
        except Exception as e:
            test_time = time.time() - start_time
            return {
                "success": False,
                "message": f"Camera {camera_id} test failed: {str(e)}",
                "capture_time": test_time
            }
    
    def get_camera_status(self, camera_id: str = None) -> Dict[str, Any]:
        """Get camera status"""
        if camera_id:
            return {
                "camera_id": camera_id,
                "status": self.camera_status.get(camera_id, "unknown"),
                "type": "cctv" if camera_id in self.cctv_cameras else "usb" if camera_id in self.usb_cameras else "unknown"
            }
        else:
            return {
                "all_cameras": self.camera_status,
                "cctv_cameras": list(self.cctv_cameras.keys()),
                "usb_cameras": list(self.usb_cameras.keys())
            }
    
    def update_cctv_config(self, camera_id: str, ip: str = None, username: str = None, 
                          password: str = None, snapshot_path: str = None):
        """Update CCTV camera configuration"""
        if camera_id not in self.cctv_cameras:
            logger.error(f"CCTV camera {camera_id} not found")
            return False
        
        config = self.cctv_cameras[camera_id]
        
        if ip:
            config["ip"] = ip
        if username:
            config["username"] = username
        if password:
            config["password"] = password
        if snapshot_path:
            config["snapshot_path"] = snapshot_path
        
        # Update URL
        config["url"] = f"http://{config['username']}:{config['password']}@{config['ip']}/{config['snapshot_path']}"
        
        logger.info(f"CCTV camera {camera_id} configuration updated")
        return True
    
    def remove_camera(self, camera_id: str):
        """Remove camera configuration"""
        if camera_id in self.usb_cameras:
            cap = self.usb_cameras[camera_id]
            cap.release()
            del self.usb_cameras[camera_id]
        
        if camera_id in self.cctv_cameras:
            del self.cctv_cameras[camera_id]
        
        if camera_id in self.camera_status:
            del self.camera_status[camera_id]
        
        logger.info(f"Camera {camera_id} removed")
    
    def cleanup(self):
        """Cleanup camera resources"""
        for cap in self.usb_cameras.values():
            cap.release()
        
        self.usb_cameras.clear()
        self.cctv_cameras.clear()
        self.camera_status.clear()
        
        logger.info("Camera service cleaned up")
    
    def list_available_usb_cameras(self) -> List[int]:
        """List available USB camera devices"""
        available_cameras = []
        
        for i in range(10):  # Check first 10 devices
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    available_cameras.append(i)
                cap.release()
            except:
                continue
        
        return available_cameras
    
    def get_camera_info(self, camera_id: str) -> Dict[str, Any]:
        """Get detailed camera information"""
        if camera_id in self.cctv_cameras:
            config = self.cctv_cameras[camera_id]
            return {
                "type": "cctv",
                "camera_id": camera_id,
                "ip": config["ip"],
                "username": config["username"],
                "snapshot_path": config["snapshot_path"],
                "status": self.camera_status.get(camera_id, "unknown")
            }
        elif camera_id in self.usb_cameras:
            return {
                "type": "usb",
                "camera_id": camera_id,
                "status": self.camera_status.get(camera_id, "unknown"),
                "device_ready": self.usb_cameras[camera_id].isOpened()
            }
        else:
            return {"error": f"Camera {camera_id} not found"}


# Global camera service instance
camera_service = CameraService()
