"""
ALPR Service using fast-alpr library
"""

import asyncio
import logging
import base64
import io
import time
from typing import Optional, Dict, Any, List
from PIL import Image
import numpy as np
import cv2
from fast_alpr import ALPR

from ..core.models import ALPRResult

logger = logging.getLogger(__name__)


class ALPRService:
    """ALPR service using fast-alpr library"""
    
    def __init__(self, confidence_threshold: float = 0.8):
        self.confidence_threshold = confidence_threshold
        self.alpr = None
        self.is_initialized = False
        self.model_loaded = False
        
        # Initialize ALPR
        self._initialize_alpr()
    
    def _initialize_alpr(self):
        """Initialize fast-alpr models"""
        try:
            logger.info("Initializing fast-alpr models...")
            
            # Initialize ALPR with recommended models
            self.alpr = ALPR(
                detector_model="yolo-v9-t-384-license-plate-end2end",
                ocr_model="global-plates-mobile-vit-v2-model"
            )
            
            self.is_initialized = True
            self.model_loaded = True
            
            logger.info("Fast-ALPR models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ALPR models: {e}")
            self.is_initialized = False
            self.model_loaded = False
    
    def initialize(self):
        """Initialize method for compatibility"""
        # ALPR is already initialized in __init__
        if not self.is_initialized:
            self._initialize_alpr()
        logger.info("ALPR service ready")
    
    def is_ready(self) -> bool:
        """Check if ALPR service is ready"""
        return self.is_initialized and self.model_loaded
    
    def detect_plate(self, image_data: str, camera_id: str = "unknown") -> Optional[ALPRResult]:
        """
        Detect license plate from base64 image data
        
        Args:
            image_data: Base64 encoded image string
            camera_id: Identifier for the camera source
            
        Returns:
            ALPRResult or None if no plate detected
        """
        if not self.is_ready():
            logger.error("ALPR service not ready")
            return None
        
        try:
            start_time = time.time()
            
            # Decode base64 image
            image = self._decode_base64_image(image_data)
            if image is None:
                logger.error("Failed to decode image data")
                return None
            
            # Run ALPR detection
            results = self.alpr.predict(image)
            
            processing_time = time.time() - start_time
            
            if not results or len(results) == 0:
                logger.debug(f"No plates detected in image from {camera_id}")
                return None
            
            # Get best result (highest confidence)
            best_result = max(results, key=lambda x: x.confidence)
            
            if best_result.confidence < self.confidence_threshold:
                logger.debug(f"Plate detected but confidence too low: {best_result.confidence}")
                return None
            
            # Extract bounding box if available
            bbox = None
            if hasattr(best_result, 'bbox') and best_result.bbox:
                bbox = {
                    "x1": float(best_result.bbox[0]),
                    "y1": float(best_result.bbox[1]), 
                    "x2": float(best_result.bbox[2]),
                    "y2": float(best_result.bbox[3])
                }
            
            alpr_result = ALPRResult(
                plate_number=best_result.text.upper().strip(),
                confidence=float(best_result.confidence),
                processing_time=processing_time,
                bbox=bbox
            )
            
            logger.info(f"Plate detected: {alpr_result.plate_number} "
                       f"(confidence: {alpr_result.confidence:.2f}, "
                       f"time: {processing_time:.2f}s)")
            
            return alpr_result
            
        except Exception as e:
            logger.error(f"ALPR detection failed: {e}")
            return None
    
    def detect_multiple_plates(self, image_data: str, camera_id: str = "unknown") -> List[ALPRResult]:
        """
        Detect multiple license plates from image
        
        Args:
            image_data: Base64 encoded image string
            camera_id: Identifier for the camera source
            
        Returns:
            List of ALPRResult objects
        """
        if not self.is_ready():
            logger.error("ALPR service not ready")
            return []
        
        try:
            start_time = time.time()
            
            # Decode base64 image
            image = self._decode_base64_image(image_data)
            if image is None:
                logger.error("Failed to decode image data")
                return []
            
            # Run ALPR detection
            results = self.alpr.predict(image)
            
            processing_time = time.time() - start_time
            
            if not results or len(results) == 0:
                logger.debug(f"No plates detected in image from {camera_id}")
                return []
            
            # Convert all results above threshold
            alpr_results = []
            for result in results:
                if result.confidence >= self.confidence_threshold:
                    # Extract bounding box if available
                    bbox = None
                    if hasattr(result, 'bbox') and result.bbox:
                        bbox = {
                            "x1": float(result.bbox[0]),
                            "y1": float(result.bbox[1]),
                            "x2": float(result.bbox[2]), 
                            "y2": float(result.bbox[3])
                        }
                    
                    alpr_result = ALPRResult(
                        plate_number=result.text.upper().strip(),
                        confidence=float(result.confidence),
                        processing_time=processing_time,
                        bbox=bbox
                    )
                    alpr_results.append(alpr_result)
            
            # Sort by confidence (highest first)
            alpr_results.sort(key=lambda x: x.confidence, reverse=True)
            
            logger.info(f"Detected {len(alpr_results)} plates in {processing_time:.2f}s")
            
            return alpr_results
            
        except Exception as e:
            logger.error(f"Multiple plate detection failed: {e}")
            return []
    
    def _decode_base64_image(self, image_data: str) -> Optional[np.ndarray]:
        """Decode base64 image to numpy array"""
        try:
            # Remove data URL prefix if present
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array (OpenCV format)
            image_array = np.array(pil_image)
            
            # Convert RGB to BGR for OpenCV
            image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            return image_bgr
            
        except Exception as e:
            logger.error(f"Failed to decode base64 image: {e}")
            return None
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better ALPR results"""
        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Convert back to BGR
            enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
            
            return enhanced_bgr
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image
    
    def detect_with_preprocessing(self, image_data: str, camera_id: str = "unknown") -> Optional[ALPRResult]:
        """Detect plate with image preprocessing"""
        if not self.is_ready():
            return None
        
        try:
            # Decode image
            image = self._decode_base64_image(image_data)
            if image is None:
                return None
            
            # Try detection on original image first
            start_time = time.time()
            results = self.alpr.predict(image)
            
            best_result = None
            if results:
                best_result = max(results, key=lambda x: x.confidence)
            
            # If no good result, try with preprocessing
            if not best_result or best_result.confidence < self.confidence_threshold:
                logger.debug("Trying with image preprocessing...")
                preprocessed = self.preprocess_image(image)
                results = self.alpr.predict(preprocessed)
                
                if results:
                    preprocessed_best = max(results, key=lambda x: x.confidence)
                    if not best_result or preprocessed_best.confidence > best_result.confidence:
                        best_result = preprocessed_best
            
            processing_time = time.time() - start_time
            
            if not best_result or best_result.confidence < self.confidence_threshold:
                return None
            
            return ALPRResult(
                plate_number=best_result.text.upper().strip(),
                confidence=float(best_result.confidence),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"ALPR detection with preprocessing failed: {e}")
            return None
    
    async def detect_plate_async(self, image_data: str, camera_id: str = "unknown") -> Optional[ALPRResult]:
        """Async version of plate detection"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.detect_plate, image_data, camera_id)
    
    def get_status(self) -> Dict[str, Any]:
        """Get ALPR service status"""
        return {
            "initialized": self.is_initialized,
            "model_loaded": self.model_loaded,
            "ready": self.is_ready(),
            "confidence_threshold": self.confidence_threshold,
            "detector_model": "yolo-v9-t-384-license-plate-end2end",
            "ocr_model": "global-plates-mobile-vit-v2-model"
        }
    
    def update_confidence_threshold(self, threshold: float):
        """Update confidence threshold"""
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
            logger.info(f"ALPR confidence threshold updated to {threshold}")
        else:
            logger.error(f"Invalid confidence threshold: {threshold}")


# Global ALPR service instance
alpr_service = ALPRService()
