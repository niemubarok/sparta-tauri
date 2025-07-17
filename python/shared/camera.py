"""
Camera service for CCTV integration
"""
import requests
import cv2
import numpy as np
import logging
from typing import Optional, Tuple
import io
from PIL import Image

logger = logging.getLogger(__name__)

class CameraService:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = 10
    
    def capture_image(self) -> Optional[bytes]:
        """Capture image from CCTV"""
        try:
            url = self.config.cctv_url
            response = self.session.get(url)
            response.raise_for_status()
            
            logger.info("Image captured successfully from CCTV")
            return response.content
        except Exception as e:
            logger.error(f"Failed to capture image from CCTV: {e}")
            return None
    
    def capture_snapshot(self) -> Optional[bytes]:
        """Capture snapshot from CCTV (alias for capture_image)"""
        return self.capture_image()
    
    def capture_image_cv2(self) -> Optional[np.ndarray]:
        """Capture image as OpenCV array"""
        try:
            image_bytes = self.capture_image()
            if image_bytes:
                # Convert bytes to numpy array
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                return img
            return None
        except Exception as e:
            logger.error(f"Failed to capture image as CV2 array: {e}")
            return None
    
    def save_image(self, image_bytes: bytes, filename: str) -> bool:
        """Save image to file"""
        try:
            with open(filename, 'wb') as f:
                f.write(image_bytes)
            logger.info(f"Image saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save image to {filename}: {e}")
            return False
    
    def resize_image(self, image_bytes: bytes, max_width: int = 800, max_height: int = 600) -> bytes:
        """Resize image to reduce file size"""
        try:
            # Open image with PIL
            img = Image.open(io.BytesIO(image_bytes))
            
            # Calculate new size maintaining aspect ratio
            width, height = img.size
            ratio = min(max_width/width, max_height/height)
            
            if ratio < 1:
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85)
            return output.getvalue()
        except Exception as e:
            logger.error(f"Failed to resize image: {e}")
            return image_bytes
