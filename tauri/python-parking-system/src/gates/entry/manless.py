"""
Manless Entry Gate Implementation
Automatic entry gate with continuous ALPR monitoring
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


class ManlessEntryGate:
    """Manless entry gate with automatic operation"""
    
    def __init__(self, gate_id: str = "entry_manless"):
        self.gate_id = gate_id
        self.gate_type = "entry"
        self.gate_mode = "manless"
        
        # Services
        self.gate_service: Optional[GateService] = None
        
        # State
        self.is_running = False
        self.is_processing = False
        self.current_transaction = None
        self.activity_logs = []
        self.transaction_count = 0
        
        # Camera configuration
        self.plate_camera_id = f"{gate_id}_plate"
        self.driver_camera_id = f"{gate_id}_driver"
        
        # Auto-capture settings
        self.auto_capture_interval = 5  # seconds
        self.detection_attempts = 3
        self.confidence_threshold = 0.8
        
        # Threading
        self.processing_lock = threading.Lock()
        self.monitor_thread = None
        
        # Initialize
        self.initialize()
    
    def initialize(self):
        """Initialize manless entry gate"""
        try:
            logger.info(f"Initializing manless entry gate: {self.gate_id}")
            
            # Load settings
            settings = database_service.get_gate_settings(self.gate_id)
            if not settings:
                logger.warning(f"No settings found for {self.gate_id}, using defaults")
                settings = self._create_default_settings()
            
            # Update settings from database
            self.auto_capture_interval = settings.auto_capture_interval or 5
            self.confidence_threshold = settings.alpr_confidence_threshold or 0.8
            
            # Initialize gate service
            self.gate_service = create_gate_service(
                self.gate_id,
                self.gate_type,
                settings.control_mode
            )
            
            # Configure cameras
            self._configure_cameras(settings)
            
            # Start monitoring
            self.start_monitoring()
            
            # Log initialization
            database_service.log_activity(
                gate_id=self.gate_id,
                gate_type=self.gate_type,
                message="Manless entry gate initialized and monitoring started"
            )
            
            logger.info(f"Manless entry gate {self.gate_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize manless entry gate {self.gate_id}: {e}")
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
    
    def start_monitoring(self):
        """Start automatic monitoring"""
        if self.is_running:
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self._log_activity("Automatic monitoring started")
    
    def stop_monitoring(self):
        """Stop automatic monitoring"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self._log_activity("Automatic monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info(f"Starting monitoring loop for {self.gate_id}")
        
        while self.is_running:
            try:
                if not self.is_processing:
                    self._check_for_vehicles()
                
                time.sleep(self.auto_capture_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                self._log_activity(f"Monitoring error: {e}", "ERROR")
                time.sleep(10)  # Wait longer after error
        
        logger.info(f"Monitoring loop stopped for {self.gate_id}")
    
    def _check_for_vehicles(self):
        """Check for vehicles using ALPR"""
        try:
            # Capture image from plate camera
            settings = database_service.get_gate_settings(self.gate_id)
            if not settings or not settings.plate_cam_type:
                return
            
            plate_capture = camera_service.capture_image(
                self.plate_camera_id,
                settings.plate_cam_type
            )
            
            if not plate_capture or not plate_capture.image_base64:
                return
            
            # Run ALPR detection
            alpr_result = alpr_service.detect_plate(
                plate_capture.image_base64,
                self.plate_camera_id
            )
            
            if alpr_result and alpr_result.confidence >= self.confidence_threshold:
                # Vehicle detected, process entry
                self._process_detected_vehicle(alpr_result)
            
        except Exception as e:
            logger.error(f"Error checking for vehicles: {e}")
    
    def _process_detected_vehicle(self, alpr_result: ALPRResult):
        """Process detected vehicle"""
        with self.processing_lock:
            if self.is_processing:
                return  # Already processing another vehicle
            
            self.is_processing = True
        
        try:
            plate_number = alpr_result.plate_number
            
            self._log_activity(
                f"Vehicle detected: {plate_number} "
                f"(confidence: {alpr_result.confidence:.2f})"
            )
            
            # Check if vehicle is already inside
            existing = database_service.find_transaction_by_plate(plate_number, status=0)
            if existing:
                self._log_activity(
                    f"Vehicle {plate_number} already inside - ignoring",
                    "WARNING"
                )
                return
            
            # Capture all images
            images = self.capture_images()
            
            # Check membership
            is_member = database_service.check_membership(plate_number)
            
            if is_member:
                # Automatic processing for members
                result = self.process_member_entry(plate_number, alpr_result, images)
                if result["success"]:
                    self._log_activity(
                        f"Member entry processed: {plate_number} - "
                        f"Gate {'opened' if result['gate_opened'] else 'failed'}"
                    )
            else:
                # Non-member - create transaction but don't open gate
                result = self.process_nonmember_entry(plate_number, alpr_result, images)
                if result["success"]:
                    self._log_activity(
                        f"Non-member detected: {plate_number} - "
                        f"Manual intervention required"
                    )
        
        except Exception as e:
            self._log_activity(f"Error processing detected vehicle: {e}", "ERROR")
        
        finally:
            self.is_processing = False
    
    def process_member_entry(self, plate_number: str, alpr_result: ALPRResult, 
                           images: Dict[str, str]) -> Dict[str, Any]:
        """Process member entry automatically"""
        try:
            # Create transaction
            transaction_data = ParkingTransactionCreate(
                no_pol=plate_number,
                id_kendaraan="1",
                jenis_system="auto_member",
                kategori="member"
            )
            
            transaction = database_service.create_transaction(transaction_data, self.gate_id)
            
            # Add images and ALPR data
            if images.get("plate"):
                transaction.pic_no_pol_masuk = images["plate"]
            if images.get("driver"):
                transaction.pic_driver_masuk = images["driver"]
            
            transaction.entry_plate_confidence = alpr_result.confidence
            
            # Save transaction
            with database_service.get_session() as session:
                session.merge(transaction)
                session.commit()
            
            # Open gate for member
            gate_opened = self.gate_service.open_gate(auto_close_seconds=10)
            
            if gate_opened:
                self.transaction_count += 1
                self._log_activity(f"Gate opened automatically for member {plate_number}")
            else:
                self._log_activity(f"Failed to open gate for member {plate_number}", "ERROR")
            
            return {
                "success": True,
                "transaction_id": transaction.id,
                "plate_number": plate_number,
                "is_member": True,
                "gate_opened": gate_opened,
                "alpr_confidence": alpr_result.confidence
            }
            
        except Exception as e:
            self._log_activity(f"Member entry processing failed: {e}", "ERROR")
            return {
                "success": False,
                "message": f"Member entry failed: {str(e)}"
            }
    
    def process_nonmember_entry(self, plate_number: str, alpr_result: ALPRResult,
                              images: Dict[str, str]) -> Dict[str, Any]:
        """Process non-member entry (create transaction, await manual intervention)"""
        try:
            # Create transaction
            transaction_data = ParkingTransactionCreate(
                no_pol=plate_number,
                id_kendaraan="1",
                jenis_system="auto_nonmember",
                kategori="umum"
            )
            
            transaction = database_service.create_transaction(transaction_data, self.gate_id)
            
            # Add images and ALPR data
            if images.get("plate"):
                transaction.pic_no_pol_masuk = images["plate"]
            if images.get("driver"):
                transaction.pic_driver_masuk = images["driver"]
            
            transaction.entry_plate_confidence = alpr_result.confidence
            
            # Save transaction
            with database_service.get_session() as session:
                session.merge(transaction)
                session.commit()
            
            # Log for operator attention
            database_service.log_activity(
                gate_id=self.gate_id,
                gate_type=self.gate_type,
                level="WARNING",
                message=f"Non-member vehicle detected: {plate_number} - Manual payment required",
                plate_number=plate_number
            )
            
            return {
                "success": True,
                "transaction_id": transaction.id,
                "plate_number": plate_number,
                "is_member": False,
                "gate_opened": False,
                "requires_payment": True,
                "alpr_confidence": alpr_result.confidence
            }
            
        except Exception as e:
            self._log_activity(f"Non-member entry processing failed: {e}", "ERROR")
            return {
                "success": False,
                "message": f"Non-member entry failed: {str(e)}"
            }
    
    def manual_gate_open(self, plate_number: str = None, operator_id: str = "operator") -> Dict[str, Any]:
        """Manual gate open (for non-members after payment)"""
        try:
            self._log_activity(f"Manual gate open by {operator_id} for {plate_number or 'unknown'}")
            
            success = self.gate_service.open_gate(auto_close_seconds=15)
            
            if success:
                self.transaction_count += 1
                
                # Update transaction if plate number provided
                if plate_number:
                    transaction = database_service.find_transaction_by_plate(plate_number, status=0)
                    if transaction:
                        transaction.manual = 1
                        transaction.id_op_masuk = operator_id
                        
                        with database_service.get_session() as session:
                            session.merge(transaction)
                            session.commit()
                
                self._log_activity(f"Gate opened manually for {plate_number or 'vehicle'}")
                
                return {
                    "success": True,
                    "message": "Gate opened manually",
                    "plate_number": plate_number,
                    "operator_id": operator_id
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
    
    def force_detection(self) -> Dict[str, Any]:
        """Force immediate ALPR detection"""
        try:
            self._log_activity("Force detection triggered")
            
            # Try multiple detections for better accuracy
            best_result = None
            attempts = 0
            
            while attempts < self.detection_attempts:
                attempts += 1
                
                # Capture image
                settings = database_service.get_gate_settings(self.gate_id)
                if not settings or not settings.plate_cam_type:
                    return {
                        "success": False,
                        "message": "No plate camera configured"
                    }
                
                plate_capture = camera_service.capture_image(
                    self.plate_camera_id,
                    settings.plate_cam_type
                )
                
                if not plate_capture:
                    continue
                
                # Run ALPR
                result = alpr_service.detect_plate(
                    plate_capture.image_base64,
                    self.plate_camera_id
                )
                
                if result and result.confidence >= self.confidence_threshold:
                    best_result = result
                    break
                elif result and (not best_result or result.confidence > best_result.confidence):
                    best_result = result
                
                time.sleep(1)  # Wait between attempts
            
            if best_result:
                # Process the detected vehicle
                self._process_detected_vehicle(best_result)
                
                return {
                    "success": True,
                    "plate_number": best_result.plate_number,
                    "confidence": best_result.confidence,
                    "attempts": attempts
                }
            else:
                return {
                    "success": False,
                    "message": "No plate detected",
                    "attempts": attempts
                }
        
        except Exception as e:
            self._log_activity(f"Force detection failed: {e}", "ERROR")
            return {
                "success": False,
                "message": f"Force detection failed: {str(e)}"
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
    
    def get_pending_transactions(self) -> List[Dict[str, Any]]:
        """Get transactions awaiting manual intervention"""
        # Get recent non-member transactions
        with database_service.get_session() as session:
            from ...core.models import ParkingTransaction
            
            transactions = session.query(ParkingTransaction).filter(
                ParkingTransaction.id_pintu_masuk == self.gate_id,
                ParkingTransaction.status == 0,
                ParkingTransaction.kategori == "umum",
                ParkingTransaction.manual == 0
            ).order_by(ParkingTransaction.entry_time.desc()).limit(10).all()
            
            return [
                {
                    "transaction_id": t.id,
                    "plate_number": t.no_pol,
                    "entry_time": t.entry_time.isoformat(),
                    "confidence": t.entry_plate_confidence,
                    "has_images": bool(t.pic_no_pol_masuk)
                }
                for t in transactions
            ]
    
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
    
    def update_settings(self, settings_data: Dict[str, Any]) -> bool:
        """Update gate settings"""
        try:
            updated_settings = database_service.update_gate_settings(self.gate_id, settings_data)
            
            if updated_settings:
                # Update local settings
                if "auto_capture_interval" in settings_data:
                    self.auto_capture_interval = settings_data["auto_capture_interval"]
                if "alpr_confidence_threshold" in settings_data:
                    self.confidence_threshold = settings_data["alpr_confidence_threshold"]
                
                # Reconfigure cameras if needed
                if any(key.startswith(("plate_cam", "driver_cam")) for key in settings_data):
                    self._configure_cameras(updated_settings)
                
                self._log_activity("Settings updated")
                return True
            else:
                return False
        
        except Exception as e:
            self._log_activity(f"Settings update failed: {e}", "ERROR")
            return False
    
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
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_monitoring()
        
        if self.gate_service:
            self.gate_service.cleanup()
        
        camera_service.remove_camera(self.plate_camera_id)
        camera_service.remove_camera(self.driver_camera_id)
        
        self._log_activity("Manless entry gate shut down")
        logger.info(f"Manless entry gate {self.gate_id} cleaned up")
