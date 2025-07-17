"""
Manual Entry Gate Implementation
Operator-controlled entry gate with manual ALPR processing
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
import threading

from ...services.database import database_service
from ...services.alpr import alpr_service
from ...services.camera import camera_service
from ...services.gate import GateService, create_gate_service
from ...core.models import ParkingTransactionCreate, ALPRResult, SystemStatus

logger = logging.getLogger(__name__)


class ManualEntryGate:
    """Manual entry gate with operator control"""
    
    def __init__(self, gate_id: str = "entry_manual"):
        self.gate_id = gate_id
        self.gate_type = "entry"
        self.gate_mode = "manual"
        
        # Services
        self.gate_service: Optional[GateService] = None
        
        # State
        self.is_processing = False
        self.current_transaction = None
        self.activity_logs = []
        self.transaction_count = 0
        
        # Camera configuration
        self.plate_camera_id = f"{gate_id}_plate"
        self.driver_camera_id = f"{gate_id}_driver"
        
        # Threading
        self.processing_lock = threading.Lock()
        
        # Initialize
        self.initialize()
    
    def initialize(self):
        """Initialize manual entry gate"""
        try:
            logger.info(f"Initializing manual entry gate: {self.gate_id}")
            
            # Load settings
            settings = database_service.get_gate_settings(self.gate_id)
            if not settings:
                logger.warning(f"No settings found for {self.gate_id}, using defaults")
                settings = self._create_default_settings()
            
            # Initialize gate service
            self.gate_service = create_gate_service(
                self.gate_id, 
                self.gate_type, 
                settings.control_mode
            )
            
            # Configure cameras
            self._configure_cameras(settings)
            
            # Log initialization
            database_service.log_activity(
                gate_id=self.gate_id,
                gate_type=self.gate_type,
                message="Manual entry gate initialized"
            )
            
            logger.info(f"Manual entry gate {self.gate_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize manual entry gate {self.gate_id}: {e}")
            raise
    
    def _create_default_settings(self):
        """Create default settings"""
        from ...core.models import GateSettings
        
        settings = GateSettings(
            id=self.gate_id,
            gate_type=self.gate_type,
            gate_mode=self.gate_mode,
            control_mode="simulation",
            plate_cam_type="cctv",
            driver_cam_type="cctv",
            alpr_confidence_threshold=0.8,
            auto_capture_interval=5,
            gate_timeout=10
        )
        
        # Save to database
        with database_service.get_session() as session:
            session.add(settings)
            session.commit()
            session.refresh(settings)
        
        return settings
    
    def _configure_cameras(self, settings):
        """Configure cameras based on settings"""
        # Configure plate camera
        if settings.plate_cam_type == "cctv" and settings.plate_cam_ip:
            camera_service.add_cctv_camera(
                self.plate_camera_id,
                settings.plate_cam_ip,
                settings.plate_cam_username or "admin",
                settings.plate_cam_password or "admin"
            )
        elif settings.plate_cam_type == "usb" and settings.plate_cam_device_id:
            camera_service.add_usb_camera(
                self.plate_camera_id,
                int(settings.plate_cam_device_id)
            )
        
        # Configure driver camera
        if settings.driver_cam_type == "cctv" and settings.driver_cam_ip:
            camera_service.add_cctv_camera(
                self.driver_camera_id,
                settings.driver_cam_ip,
                settings.driver_cam_username or "admin",
                settings.driver_cam_password or "admin"
            )
        elif settings.driver_cam_type == "usb" and settings.driver_cam_device_id:
            camera_service.add_usb_camera(
                self.driver_camera_id,
                int(settings.driver_cam_device_id)
            )
    
    def capture_images(self) -> Dict[str, Optional[str]]:
        """Capture images from both cameras"""
        settings = database_service.get_gate_settings(self.gate_id)
        if not settings:
            return {"plate": None, "driver": None}
        
        images = {}
        
        # Capture plate camera
        if settings.plate_cam_type:
            plate_capture = camera_service.capture_image(
                self.plate_camera_id, 
                settings.plate_cam_type
            )
            images["plate"] = plate_capture.image_base64 if plate_capture else None
        else:
            images["plate"] = None
        
        # Capture driver camera
        if settings.driver_cam_type:
            driver_capture = camera_service.capture_image(
                self.driver_camera_id,
                settings.driver_cam_type
            )
            images["driver"] = driver_capture.image_base64 if driver_capture else None
        else:
            images["driver"] = None
        
        return images
    
    def detect_plate(self, image_data: str = None) -> Optional[ALPRResult]:
        """Detect license plate"""
        try:
            # Capture image if not provided
            if not image_data:
                images = self.capture_images()
                image_data = images.get("plate")
                
                if not image_data:
                    self._log_activity("No plate image available for ALPR", "WARNING")
                    return None
            
            # Run ALPR detection
            result = alpr_service.detect_plate(image_data, self.plate_camera_id)
            
            if result:
                self._log_activity(
                    f"Plate detected: {result.plate_number} "
                    f"(confidence: {result.confidence:.2f}, "
                    f"time: {result.processing_time:.2f}s)"
                )
            else:
                self._log_activity("No plate detected", "WARNING")
            
            return result
            
        except Exception as e:
            self._log_activity(f"ALPR detection failed: {e}", "ERROR")
            return None
    
    def manual_plate_entry(self, plate_number: str, operator_id: str = "manual") -> Dict[str, Any]:
        """Manual plate number entry"""
        with self.processing_lock:
            try:
                self.is_processing = True
                
                self._log_activity(f"Manual plate entry: {plate_number} by {operator_id}")
                
                # Capture images
                images = self.capture_images()
                
                # Process entry
                result = self.process_entry(
                    plate_number=plate_number,
                    operator_id=operator_id,
                    images=images,
                    entry_method="manual"
                )
                
                return result
                
            except Exception as e:
                self._log_activity(f"Manual plate entry failed: {e}", "ERROR")
                return {
                    "success": False,
                    "message": f"Manual entry failed: {str(e)}"
                }
            finally:
                self.is_processing = False
    
    def auto_plate_detection(self, operator_id: str = "auto") -> Dict[str, Any]:
        """Automatic plate detection and entry"""
        with self.processing_lock:
            try:
                self.is_processing = True
                
                self._log_activity("Starting automatic plate detection")
                
                # Try detection multiple times for better accuracy
                best_result = None
                attempts = 0
                max_attempts = 5
                
                while attempts < max_attempts:
                    attempts += 1
                    result = self.detect_plate()
                    
                    if result and result.confidence >= 0.8:
                        best_result = result
                        break
                    elif result and (not best_result or result.confidence > best_result.confidence):
                        best_result = result
                    
                    time.sleep(1)  # Wait between attempts
                
                if not best_result:
                    return {
                        "success": False,
                        "message": "No plate detected after multiple attempts"
                    }
                
                if best_result.confidence < 0.8:
                    self._log_activity(
                        f"Low confidence detection: {best_result.plate_number} "
                        f"({best_result.confidence:.2f})", 
                        "WARNING"
                    )
                
                # Capture final images
                images = self.capture_images()
                
                # Process entry
                result = self.process_entry(
                    plate_number=best_result.plate_number,
                    operator_id=operator_id,
                    images=images,
                    entry_method="auto",
                    alpr_result=best_result
                )
                
                return result
                
            except Exception as e:
                self._log_activity(f"Auto plate detection failed: {e}", "ERROR")
                return {
                    "success": False,
                    "message": f"Auto detection failed: {str(e)}"
                }
            finally:
                self.is_processing = False
    
    def process_entry(self, plate_number: str, operator_id: str, images: Dict[str, str],
                     entry_method: str = "manual", alpr_result: ALPRResult = None) -> Dict[str, Any]:
        """Process vehicle entry"""
        try:
            # Check if vehicle is already inside
            existing = database_service.find_transaction_by_plate(plate_number, status=0)
            if existing:
                return {
                    "success": False,
                    "message": f"Vehicle {plate_number} already inside",
                    "transaction_id": existing.id
                }
            
            # Check membership status
            is_member = database_service.check_membership(plate_number)
            
            # Create transaction
            transaction_data = ParkingTransactionCreate(
                no_pol=plate_number,
                id_kendaraan="1",  # Default vehicle type
                jenis_system=entry_method,
                kategori="member" if is_member else "umum"
            )
            
            transaction = database_service.create_transaction(transaction_data, self.gate_id)
            
            # Add images to transaction
            if images.get("plate"):
                transaction.pic_no_pol_masuk = images["plate"]
            if images.get("driver"):
                transaction.pic_driver_masuk = images["driver"]
            
            # Add ALPR confidence if available
            if alpr_result:
                transaction.entry_plate_confidence = alpr_result.confidence
            
            # Save transaction
            with database_service.get_session() as session:
                session.merge(transaction)
                session.commit()
            
            # Open gate for members or after manual confirmation
            if is_member:
                self._log_activity(f"Member vehicle {plate_number} - opening gate automatically")
                gate_opened = self.gate_service.open_gate(auto_close_seconds=10)
                
                if gate_opened:
                    self.transaction_count += 1
                    self._log_activity(f"Gate opened for member {plate_number}")
                else:
                    self._log_activity(f"Failed to open gate for {plate_number}", "ERROR")
            else:
                self._log_activity(f"Non-member vehicle {plate_number} - manual gate control required")
                gate_opened = False
            
            result = {
                "success": True,
                "message": "Entry processed successfully",
                "transaction_id": transaction.id,
                "plate_number": plate_number,
                "is_member": is_member,
                "gate_opened": gate_opened,
                "entry_method": entry_method
            }
            
            if alpr_result:
                result["alpr_confidence"] = alpr_result.confidence
                result["processing_time"] = alpr_result.processing_time
            
            return result
            
        except Exception as e:
            self._log_activity(f"Entry processing failed: {e}", "ERROR")
            return {
                "success": False,
                "message": f"Entry processing failed: {str(e)}"
            }
    
    def manual_gate_open(self, operator_id: str = "operator", reason: str = "Manual open") -> Dict[str, Any]:
        """Manual gate operation"""
        try:
            self._log_activity(f"Manual gate open by {operator_id}: {reason}")
            
            # Capture images for record
            images = self.capture_images()
            
            # Open gate
            success = self.gate_service.open_gate(auto_close_seconds=15)
            
            if success:
                self.transaction_count += 1
                
                # Log manual gate operation
                database_service.log_activity(
                    gate_id=self.gate_id,
                    gate_type=self.gate_type,
                    message=f"Manual gate open by {operator_id}: {reason}",
                    operator_id=operator_id
                )
                
                return {
                    "success": True,
                    "message": "Gate opened manually",
                    "operator_id": operator_id,
                    "reason": reason
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to open gate"
                }
            
        except Exception as e:
            self._log_activity(f"Manual gate open failed: {e}", "ERROR")
            return {
                "success": False,
                "message": f"Manual gate operation failed: {str(e)}"
            }
    
    def emergency_open(self, operator_id: str = "operator") -> Dict[str, Any]:
        """Emergency gate open"""
        try:
            self._log_activity(f"🚨 EMERGENCY GATE OPEN by {operator_id}")
            
            # Open gate without time limit
            success = self.gate_service.open_gate()
            
            if success:
                # Log emergency operation
                database_service.log_activity(
                    gate_id=self.gate_id,
                    gate_type=self.gate_type,
                    level="WARNING",
                    message=f"EMERGENCY GATE OPEN by {operator_id}",
                    operator_id=operator_id
                )
                
                return {
                    "success": True,
                    "message": "Emergency gate open",
                    "operator_id": operator_id
                }
            else:
                return {
                    "success": False,
                    "message": "Emergency gate open failed"
                }
            
        except Exception as e:
            self._log_activity(f"Emergency gate open failed: {e}", "ERROR")
            return {
                "success": False,
                "message": f"Emergency gate operation failed: {str(e)}"
            }
    
    def close_gate(self, operator_id: str = "operator") -> Dict[str, Any]:
        """Manual gate close"""
        try:
            success = self.gate_service.close_gate()
            
            if success:
                self._log_activity(f"Gate closed manually by {operator_id}")
                return {
                    "success": True,
                    "message": "Gate closed",
                    "operator_id": operator_id
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to close gate"
                }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Gate close failed: {str(e)}"
            }
    
    def get_status(self) -> SystemStatus:
        """Get system status"""
        gate_status = self.gate_service.get_status() if self.gate_service else {}
        camera_status = camera_service.get_camera_status()
        alpr_status = alpr_service.get_status()
        
        return SystemStatus(
            gate_id=self.gate_id,
            gate_type=self.gate_type,
            gate_mode=self.gate_mode,
            gate_status=gate_status.get("status", "unknown"),
            alpr_status="ready" if alpr_status.get("ready") else "error",
            camera_status={
                "plate": camera_status.get("all_cameras", {}).get(self.plate_camera_id, "unknown"),
                "driver": camera_status.get("all_cameras", {}).get(self.driver_camera_id, "unknown")
            },
            last_activity=datetime.utcnow() if self.activity_logs else None,
            transaction_count=self.transaction_count
        )
    
    def get_activity_logs(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent activity logs"""
        logs = database_service.get_activity_logs(self.gate_id, hours)
        return [
            {
                "timestamp": log.timestamp.isoformat(),
                "level": log.level,
                "message": log.message,
                "plate_number": log.plate_number,
                "operator_id": log.operator_id
            }
            for log in logs
        ]
    
    def _log_activity(self, message: str, level: str = "INFO"):
        """Log activity"""
        database_service.log_activity(
            gate_id=self.gate_id,
            gate_type=self.gate_type,
            level=level,
            message=message
        )
        
        # Also keep in memory for quick access
        self.activity_logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message
        })
        
        # Keep only last 100 entries in memory
        if len(self.activity_logs) > 100:
            self.activity_logs = self.activity_logs[-100:]
    
    def test_system(self) -> Dict[str, Any]:
        """Test all system components"""
        test_results = {
            "gate_test": False,
            "alpr_test": False,
            "camera_test": {"plate": False, "driver": False},
            "database_test": False,
            "overall_success": False
        }
        
        try:
            # Test gate
            if self.gate_service:
                gate_test = self.gate_service.test_gate(test_duration=2)
                test_results["gate_test"] = gate_test.get("success", False)
            
            # Test ALPR
            test_results["alpr_test"] = alpr_service.is_ready()
            
            # Test cameras
            settings = database_service.get_gate_settings(self.gate_id)
            if settings and settings.plate_cam_type:
                plate_test = camera_service.test_camera(self.plate_camera_id, settings.plate_cam_type)
                test_results["camera_test"]["plate"] = plate_test.get("success", False)
            
            if settings and settings.driver_cam_type:
                driver_test = camera_service.test_camera(self.driver_camera_id, settings.driver_cam_type)
                test_results["camera_test"]["driver"] = driver_test.get("success", False)
            
            # Test database
            try:
                stats = database_service.get_daily_statistics()
                test_results["database_test"] = True
            except:
                test_results["database_test"] = False
            
            # Overall success
            test_results["overall_success"] = (
                test_results["gate_test"] and 
                test_results["alpr_test"] and 
                test_results["database_test"]
            )
            
        except Exception as e:
            logger.error(f"System test failed: {e}")
        
        return test_results
    
    def cleanup(self):
        """Cleanup resources"""
        if self.gate_service:
            self.gate_service.cleanup()
        
        camera_service.remove_camera(self.plate_camera_id)
        camera_service.remove_camera(self.driver_camera_id)
        
        self._log_activity("Manual entry gate shut down")
        logger.info(f"Manual entry gate {self.gate_id} cleaned up")
