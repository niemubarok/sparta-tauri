"""
Camera management and capture functionality
Supports both USB and IP cameras for plate and driver monitoring
"""

import asyncio
import base64
import logging
import time
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Optional, Dict, Any, List
import cv2
import numpy as np
import requests
from PIL import Image

logger = logging.getLogger(__name__)


class CameraConfig:
    """Camera configuration data"""
    
    def __init__(self, camera_id: str, camera_type: str = "usb", 
                 device_id: Optional[int] = None, url: Optional[str] = None,
                 username: Optional[str] = None, password: Optional[str] = None,
                 snapshot_path: Optional[str] = None, name: Optional[str] = None):
        self.camera_id = camera_id
        self.camera_type = camera_type  # "usb" or "cctv"
        self.device_id = device_id
        self.url = url
        self.username = username
        self.password = password
        self.snapshot_path = snapshot_path
        self.name = name or camera_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "camera_id": self.camera_id,
            "camera_type": self.camera_type,
            "device_id": self.device_id,
            "url": self.url,
            "username": self.username,
            "password": self.password,
            "snapshot_path": self.snapshot_path,
            "name": self.name
        }


class CameraCapture:
    """Represents a captured image from camera"""
    
    def __init__(self, image_base64: str, camera_id: str, timestamp: float = None):
        self.image_base64 = image_base64
        self.camera_id = camera_id
        self.timestamp = timestamp or time.time()
        self.success = bool(image_base64)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_base64": self.image_base64,
            "camera_id": self.camera_id,
            "timestamp": self.timestamp,
            "success": self.success
        }


class BaseCamera(ABC):
    """Base abstract camera class"""
    
    def __init__(self, config: CameraConfig):
        self.config = config
        self._is_connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the camera"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the camera"""
        pass
    
    @abstractmethod
    async def capture_image(self) -> CameraCapture:
        """Capture an image from the camera"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test camera connection"""
        pass
    
    def is_connected(self) -> bool:
        """Check if camera is connected"""
        return self._is_connected


class UsbCamera(BaseCamera):
    """USB Camera implementation using OpenCV"""
    
    def __init__(self, config: CameraConfig):
        super().__init__(config)
        self._cap = None
    
    async def connect(self) -> bool:
        """Connect to USB camera"""
        try:
            if self.config.device_id is None:
                logger.error("USB camera device_id not specified")
                return False
            
            # Run OpenCV operations in executor to avoid blocking
            loop = asyncio.get_event_loop()
            self._cap = await loop.run_in_executor(
                None, cv2.VideoCapture, self.config.device_id
            )
            
            if not self._cap.isOpened():
                logger.error(f"Failed to open USB camera {self.config.device_id}")
                return False
            
            # Set camera properties for better quality
            await loop.run_in_executor(
                None, self._cap.set, cv2.CAP_PROP_FRAME_WIDTH, 1920
            )
            await loop.run_in_executor(
                None, self._cap.set, cv2.CAP_PROP_FRAME_HEIGHT, 1080
            )
            await loop.run_in_executor(
                None, self._cap.set, cv2.CAP_PROP_FPS, 30
            )
            
            self._is_connected = True
            logger.info(f"USB camera {self.config.camera_id} connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect USB camera {self.config.camera_id}: {e}")
            self._is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect USB camera"""
        try:
            if self._cap is not None:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._cap.release)
                self._cap = None
            
            self._is_connected = False
            logger.info(f"USB camera {self.config.camera_id} disconnected")
            
        except Exception as e:
            logger.error(f"Error disconnecting USB camera {self.config.camera_id}: {e}")
    
    async def capture_image(self) -> CameraCapture:
        """Capture image from USB camera"""
        if not self._is_connected or self._cap is None:
            logger.error(f"USB camera {self.config.camera_id} not connected")
            return CameraCapture("", self.config.camera_id)
        
        try:
            loop = asyncio.get_event_loop()
            
            # Capture frame
            ret, frame = await loop.run_in_executor(None, self._cap.read)
            
            if not ret or frame is None:
                logger.error(f"Failed to capture frame from USB camera {self.config.camera_id}")
                return CameraCapture("", self.config.camera_id)
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(frame_rgb)
            
            # Convert to base64
            buffer = BytesIO()
            pil_image.save(buffer, format='JPEG', quality=85)
            image_bytes = buffer.getvalue()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            logger.debug(f"Captured image from USB camera {self.config.camera_id}")
            return CameraCapture(image_base64, self.config.camera_id)
            
        except Exception as e:
            logger.error(f"Failed to capture image from USB camera {self.config.camera_id}: {e}")
            return CameraCapture("", self.config.camera_id)
    
    async def test_connection(self) -> bool:
        """Test USB camera connection"""
        if not self._is_connected:
            return await self.connect()
        
        try:
            # Try to capture a test frame
            capture = await self.capture_image()
            return capture.success
        except Exception as e:
            logger.error(f"USB camera test failed for {self.config.camera_id}: {e}")
            return False


class IpCamera(BaseCamera):
    """IP Camera implementation for CCTV cameras"""
    
    def __init__(self, config: CameraConfig):
        super().__init__(config)
        self._session = None
    
    async def connect(self) -> bool:
        """Connect to IP camera"""
        try:
            if not self.config.url:
                logger.error("IP camera URL not specified")
                return False
            
            # Create HTTP session with authentication
            self._session = requests.Session()
            
            if self.config.username and self.config.password:
                self._session.auth = (self.config.username, self.config.password)
            
            # Test connection
            test_success = await self.test_connection()
            
            if test_success:
                self._is_connected = True
                logger.info(f"IP camera {self.config.camera_id} connected successfully")
                return True
            else:
                logger.error(f"Failed to connect to IP camera {self.config.camera_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect IP camera {self.config.camera_id}: {e}")
            self._is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect IP camera"""
        try:
            if self._session:
                self._session.close()
                self._session = None
            
            self._is_connected = False
            logger.info(f"IP camera {self.config.camera_id} disconnected")
            
        except Exception as e:
            logger.error(f"Error disconnecting IP camera {self.config.camera_id}: {e}")
    
    async def capture_image(self) -> CameraCapture:
        """Capture image from IP camera"""
        if not self._is_connected or self._session is None:
            logger.error(f"IP camera {self.config.camera_id} not connected")
            return CameraCapture("", self.config.camera_id)
        
        try:
            # Build snapshot URL
            snapshot_url = self._build_snapshot_url()
            
            # Make HTTP request in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self._session.get(snapshot_url, timeout=10)
            )
            
            if response.status_code != 200:
                logger.error(f"HTTP error {response.status_code} from IP camera {self.config.camera_id}")
                return CameraCapture("", self.config.camera_id)
            
            # Convert image bytes to base64
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            
            logger.debug(f"Captured image from IP camera {self.config.camera_id}")
            return CameraCapture(image_base64, self.config.camera_id)
            
        except Exception as e:
            logger.error(f"Failed to capture image from IP camera {self.config.camera_id}: {e}")
            return CameraCapture("", self.config.camera_id)
    
    async def test_connection(self) -> bool:
        """Test IP camera connection"""
        try:
            if not self._session:
                return False
            
            snapshot_url = self._build_snapshot_url()
            
            # Make test request in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._session.head(snapshot_url, timeout=5)
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"IP camera test failed for {self.config.camera_id}: {e}")
            return False
    
    def _build_snapshot_url(self) -> str:
        """Build the snapshot URL"""
        base_url = self.config.url.rstrip('/')
        snapshot_path = self.config.snapshot_path or "Streaming/Channels/1/picture"
        
        # Handle different URL formats
        if '://' in base_url:
            return f"{base_url}/{snapshot_path}"
        else:
            # Assume HTTP if no protocol specified
            return f"http://{base_url}/{snapshot_path}"


class CameraManager:
    """Manages multiple cameras and provides unified interface"""
    
    def __init__(self):
        self._cameras: Dict[str, BaseCamera] = {}
        self._configs: Dict[str, CameraConfig] = {}
    
    def add_camera(self, config: CameraConfig) -> bool:
        """Add a camera configuration"""
        try:
            if config.camera_type.lower() == "usb":
                camera = UsbCamera(config)
            elif config.camera_type.lower() == "cctv":
                camera = IpCamera(config)
            else:
                logger.error(f"Unsupported camera type: {config.camera_type}")
                return False
            
            self._cameras[config.camera_id] = camera
            self._configs[config.camera_id] = config
            
            logger.info(f"Added {config.camera_type} camera: {config.camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add camera {config.camera_id}: {e}")
            return False
    
    def remove_camera(self, camera_id: str) -> bool:
        """Remove a camera"""
        try:
            if camera_id in self._cameras:
                asyncio.create_task(self._cameras[camera_id].disconnect())
                del self._cameras[camera_id]
                del self._configs[camera_id]
                logger.info(f"Removed camera: {camera_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove camera {camera_id}: {e}")
            return False
    
    def get_camera(self, camera_id: str) -> Optional[BaseCamera]:
        """Get camera by ID"""
        return self._cameras.get(camera_id)
    
    def get_camera_config(self, camera_id: str) -> Optional[CameraConfig]:
        """Get camera configuration by ID"""
        return self._configs.get(camera_id)
    
    def list_cameras(self) -> List[str]:
        """List all camera IDs"""
        return list(self._cameras.keys())
    
    def list_camera_configs(self) -> List[CameraConfig]:
        """List all camera configurations"""
        return list(self._configs.values())
    
    async def connect_camera(self, camera_id: str) -> bool:
        """Connect to a specific camera"""
        camera = self.get_camera(camera_id)
        if camera:
            return await camera.connect()
        return False
    
    async def disconnect_camera(self, camera_id: str) -> bool:
        """Disconnect from a specific camera"""
        camera = self.get_camera(camera_id)
        if camera:
            await camera.disconnect()
            return True
        return False
    
    async def capture_image(self, camera_id: str) -> CameraCapture:
        """Capture image from a specific camera"""
        camera = self.get_camera(camera_id)
        if camera:
            if not camera.is_connected():
                await camera.connect()
            return await camera.capture_image()
        
        return CameraCapture("", camera_id)
    
    async def test_camera(self, camera_id: str) -> bool:
        """Test a specific camera"""
        camera = self.get_camera(camera_id)
        if camera:
            return await camera.test_connection()
        return False
    
    async def test_all_cameras(self) -> Dict[str, bool]:
        """Test all cameras"""
        results = {}
        
        for camera_id in self._cameras:
            results[camera_id] = await self.test_camera(camera_id)
        
        return results
    
    async def disconnect_all(self):
        """Disconnect all cameras"""
        tasks = []
        for camera in self._cameras.values():
            tasks.append(camera.disconnect())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("All cameras disconnected")


# Global camera manager instance
_camera_manager: Optional[CameraManager] = None


def get_camera_manager() -> CameraManager:
    """Get or create the global camera manager instance"""
    global _camera_manager
    
    if _camera_manager is None:
        _camera_manager = CameraManager()
    
    return _camera_manager


async def detect_usb_cameras() -> List[int]:
    """Detect available USB cameras"""
    available_cameras = []
    
    # Test camera indices 0-9
    for i in range(10):
        try:
            loop = asyncio.get_event_loop()
            cap = await loop.run_in_executor(None, cv2.VideoCapture, i)
            
            if cap.isOpened():
                available_cameras.append(i)
                await loop.run_in_executor(None, cap.release)
            
        except Exception:
            continue
    
    logger.info(f"Detected USB cameras: {available_cameras}")
    return available_cameras
