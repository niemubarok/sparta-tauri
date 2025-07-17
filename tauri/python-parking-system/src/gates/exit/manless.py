"""
Manless Exit Gate Implementation
Automatic exit gate with ALPR detection and member processing
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import threading

from ...services.database import database_service
from ...services.alpr import alpr_service
from ...services.camera import camera_service
from ...services.gate import GateService, create_gate_service
from ...core.models import ParkingTransactionCreate, ALPRResult, SystemStatus

logger = logging.getLogger(__name__)


class ManlessExitGate:
    """Manless exit gate with automatic operation"""
    
    def __init__(self, gate_id: str = "exit_manless"):
        self.gate_id = gate_id
        self.gate_type = "exit"
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
        self.auto_capture_interval = 3  # seconds - faster for exits
        self.detection_attempts = 3
        self.confidence_threshold = 0.8
        self.processing_timeout = 30  # seconds
        
        # Threading
        self.processing_lock = threading.Lock()
        self.monitor_thread = None
        
        # Initialize
        self.initialize()
    
    def initialize(self):
        """Initialize manless exit gate"""
        try:
            logger.info(f"Initializing manless exit gate: {self.gate_id}")
            
            # Load settings
            settings = database_service.get_gate_settings(self.gate_id)
            if not settings:
                logger.warning(f"No settings found for {self.gate_id}, using defaults")
                settings = self._create_default_settings()
            
            # Update settings from database
            self.auto_capture_interval = settings.auto_capture_interval or 3
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
                message="Manless exit gate initialized and monitoring started"
            )
            
            logger.info(f"Manless exit gate {self.gate_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize manless exit gate {self.gate_id}: {e}")
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
            auto_capture_interval=3,
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
        
        self._log_activity("Automatic exit monitoring started")
    
    def stop_monitoring(self):
        """Stop automatic monitoring"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self._log_activity("Automatic exit monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info(f"Starting exit monitoring loop for {self.gate_id}")
        
        while self.is_running:
            try:
                if not self.is_processing:
                    self._check_for_exit_vehicles()
                
                time.sleep(self.auto_capture_interval)
                
            except Exception as e:
                logger.error(f"Error in exit monitoring loop: {e}")
                self._log_activity(f"Exit monitoring error: {e}", "ERROR")
                time.sleep(10)  # Wait longer after error
        
        logger.info(f"Exit monitoring loop stopped for {self.gate_id}")
    
    def _check_for_exit_vehicles(self):
        """Check for vehicles wanting to exit using ALPR"""
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
                # Vehicle detected, process exit
                self._process_detected_exit_vehicle(alpr_result)
            
        except Exception as e:
            logger.error(f"Error checking for exit vehicles: {e}")
    
    def _process_detected_exit_vehicle(self, alpr_result: ALPRResult):
        """Process detected vehicle for exit"""
        with self.processing_lock:
            if self.is_processing:
                return  # Already processing another vehicle
            
            self.is_processing = True
        
        try:
            plate_number = alpr_result.plate_number
            
            self._log_activity(
                f"Exit vehicle detected: {plate_number} "
                f"(confidence: {alpr_result.confidence:.2f})"
            )
            
            # Find active transaction
            transaction = database_service.find_transaction_by_plate(plate_number, status=0)
            
            if not transaction:
                self._log_activity(
                    f"No active transaction found for {plate_number} - ignoring",
                    "WARNING"
                )
                return
            
            # Capture all images
            images = self.capture_images()
            
            # Check if it's a member (automatic processing)
            is_member = transaction.kategori == "member"
            
            if is_member:
                # Automatic processing for members
                result = self.process_member_exit(transaction, alpr_result, images)
                if result["success"]:
                    self._log_activity(
                        f"Member exit processed: {plate_number} - "
                        f"Fee: Rp{result['fee']:,}, "
                        f"Gate {'opened' if result['gate_opened'] else 'failed'}"
                    )
            else:
                # Non-member - requires payment verification
                result = self.process_nonmember_exit(transaction, alpr_result, images)
                if result["success"]:
                    self._log_activity(
                        f"Non-member exit processed: {plate_number} - "
                        f"Payment verification required"
                    )
        
        except Exception as e:
            self._log_activity(f"Error processing detected exit vehicle: {e}", "ERROR")
        
        finally:
            self.is_processing = False
    
    def process_member_exit(self, transaction, alpr_result: ALPRResult, 
                          images: Dict[str, str]) -> Dict[str, Any]:
        """Process member exit automatically"""
        try:
            # Calculate duration and fee
            duration_info = self._calculate_duration_and_fee(transaction)
            
            # Update transaction
            transaction.waktu_keluar = datetime.utcnow()
            transaction.status = 1
            transaction.tarif = duration_info["fee"]
            transaction.durasi = duration_info["duration_minutes"]
            transaction.id_pintu_keluar = self.gate_id
            transaction.exit_plate_confidence = alpr_result.confidence
            
            # Add exit images
            if images.get("plate"):
                transaction.pic_no_pol_keluar = images["plate"]
            if images.get("driver"):
                transaction.pic_driver_keluar = images["driver"]
            
            # Check plate matching
            plate_matches = alpr_result.plate_number == transaction.no_pol
            if not plate_matches:
                self._log_activity(
                    f"Plate mismatch for member - Entry: {transaction.no_pol}, "
                    f"Exit: {alpr_result.plate_number}",
                    "WARNING"
                )
            
            # Save transaction
            with database_service.get_session() as session:
                session.merge(transaction)
                session.commit()
            
            # Open gate for member
            gate_opened = self.gate_service.open_gate(auto_close_seconds=10)
            
            if gate_opened:
                self.transaction_count += 1
                self._log_activity(
                    f"Gate opened automatically for member {transaction.no_pol} - "
                    f"Fee: Rp{duration_info['fee']:,}"
                )
            else:
                self._log_activity(
                    f"Failed to open gate for member {transaction.no_pol}",
                    "ERROR"
                )
            
            return {
                "success": True,
                "transaction_id": transaction.id,
                "plate_number": transaction.no_pol,
                "entry_time": transaction.entry_time.isoformat(),
                "exit_time": transaction.waktu_keluar.isoformat(),
                "duration": duration_info["duration_text"],
                "fee": duration_info["fee"],
                "is_member": True,
                "gate_opened": gate_opened,
                "plate_matches": plate_matches,
                "alpr_confidence": alpr_result.confidence
            }
            
        except Exception as e:
            self._log_activity(f"Member exit processing failed: {e}", "ERROR")
            return {
                "success": False,
                "message": f"Member exit failed: {str(e)}"
            }
    
    def process_nonmember_exit(self, transaction, alpr_result: ALPRResult,
                             images: Dict[str, str]) -> Dict[str, Any]:
        """Process non-member exit (requires payment verification)"""
        try:
            # Calculate duration and fee
            duration_info = self._calculate_duration_and_fee(transaction)
            
            # Update transaction with exit detection info but don't complete
            transaction.exit_plate_confidence = alpr_result.confidence
            
            # Add exit images
            if images.get("plate"):
                transaction.pic_no_pol_keluar = images["plate"]
            if images.get("driver"):
                transaction.pic_driver_keluar = images["driver"]
            
            # Save partial exit info
            with database_service.get_session() as session:
                session.merge(transaction)
                session.commit()
            
            # Log for operator attention
            database_service.log_activity(
                gate_id=self.gate_id,
                gate_type=self.gate_type,
                level="WARNING",
                message=f"Non-member exit detected: {transaction.no_pol} - "
                       f"Payment required: Rp{duration_info['fee']:,}",
                plate_number=transaction.no_pol
            )
            
            return {
                "success": True,
                "transaction_id": transaction.id,
                "plate_number": transaction.no_pol,
                "entry_time": transaction.entry_time.isoformat(),
                "duration": duration_info["duration_text"],
                "fee": duration_info["fee"],
                "is_member": False,
                "gate_opened": False,
                "requires_payment": True,
                "alpr_confidence": alpr_result.confidence
            }
            
        except Exception as e:
            self._log_activity(f"Non-member exit processing failed: {e}", "ERROR")
            return {
                "success": False,
                "message": f"Non-member exit failed: {str(e)}"
            }
    
    def manual_process_payment(self, transaction_id: int, payment_confirmed: bool,
                             operator_id: str = "operator") -> Dict[str, Any]:
        """Manually process payment and complete exit"""
        try:
            transaction = database_service.find_transaction_by_id(transaction_id)
            
            if not transaction:
                return {
                    "success": False,
                    "message": f"Transaction not found: {transaction_id}"
                }
            
            if transaction.status != 0:
                return {
                    "success": False,
                    "message": f"Transaction already processed: {transaction_id}"
                }
            
            if payment_confirmed:
                # Complete the exit
                duration_info = self._calculate_duration_and_fee(transaction)
                
                transaction.waktu_keluar = datetime.utcnow()
                transaction.status = 1
                transaction.tarif = duration_info["fee"]
                transaction.durasi = duration_info["duration_minutes"]
                transaction.id_op_keluar = operator_id
                transaction.id_pintu_keluar = self.gate_id
                transaction.manual = 1  # Mark as manually processed
                
                # Save transaction
                with database_service.get_session() as session:
                    session.merge(transaction)
                    session.commit()
                
                # Open gate
                gate_opened = self.gate_service.open_gate(auto_close_seconds=15)
                
                if gate_opened:
                    self.transaction_count += 1
                    self._log_activity(
                        f"Payment confirmed and gate opened for {transaction.no_pol} - "
                        f"Fee: Rp{duration_info['fee']:,}"
                    )
                else:
                    self._log_activity(
                        f"Payment confirmed but gate failed to open for {transaction.no_pol}",
                        "ERROR"
                    )
                
                return {
                    "success": True,
                    "transaction_id": transaction.id,
                    "plate_number": transaction.no_pol,
                    "fee": duration_info["fee"],
                    "payment_confirmed": True,
                    "gate_opened": gate_opened
                }
            else:
                # Payment denied
                self._log_activity(
                    f"Payment denied for {transaction.no_pol} by {operator_id}",
                    "WARNING"
                )
                
                return {
                    "success": True,
                    "transaction_id": transaction.id,
                    "plate_number": transaction.no_pol,
                    "payment_confirmed": False,
                    "gate_opened": False,
                    "message": "Payment denied"
                }
        
        except Exception as e:
            self._log_activity(f"Manual payment processing failed: {e}", "ERROR")
            return {
                "success": False,
                "message": f"Payment processing failed: {str(e)}"
            }
    
    def manual_gate_open(self, plate_number: str = None, operator_id: str = "operator") -> Dict[str, Any]:
        """Manual gate open (emergency override)"""
        try:
            self._log_activity(f"Manual gate override by {operator_id} for {plate_number or 'unknown'}")
            
            success = self.gate_service.open_gate(auto_close_seconds=15)
            
            if success:
                self.transaction_count += 1
                
                # If plate number provided, try to complete transaction
                if plate_number:
                    transaction = database_service.find_transaction_by_plate(plate_number, status=0)
                    if transaction:
                        duration_info = self._calculate_duration_and_fee(transaction)
                        
                        transaction.waktu_keluar = datetime.utcnow()
                        transaction.status = 1
                        transaction.tarif = duration_info["fee"]
                        transaction.durasi = duration_info["duration_minutes"]
                        transaction.id_op_keluar = operator_id
                        transaction.id_pintu_keluar = self.gate_id
                        transaction.manual = 1
                        
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
    
    def _calculate_duration_and_fee(self, transaction) -> Dict[str, Any]:
        """Calculate parking duration and fee"""
        try:
            entry_time = transaction.entry_time
            exit_time = datetime.utcnow()
            
            duration = exit_time - entry_time
            duration_minutes = int(duration.total_seconds() / 60)
            duration_hours = duration_minutes / 60
            
            # Format duration text
            if duration_minutes < 60:
                duration_text = f"{duration_minutes} menit"
            else:
                hours = int(duration_hours)
                minutes = duration_minutes % 60
                duration_text = f"{hours} jam {minutes} menit"
            
            # Calculate fee based on vehicle type and duration
            fee = 0
            
            # Get vehicle type tariff
            vehicle_type = database_service.get_vehicle_type(transaction.id_kendaraan)
            if vehicle_type:
                base_fee = vehicle_type.get("tarif_per_jam", 5000)
                
                # Minimum 1 hour billing
                billable_hours = max(1, int(duration_hours) + (1 if duration_minutes % 60 > 0 else 0))
                fee = base_fee * billable_hours
            else:
                # Default fee calculation
                fee = 5000 * max(1, int(duration_hours) + (1 if duration_minutes % 60 > 0 else 0))
            
            # Member discount
            if transaction.kategori == "member":
                fee = int(fee * 0.8)  # 20% discount for members
            
            return {
                "duration_minutes": duration_minutes,
                "duration_hours": duration_hours,
                "duration_text": duration_text,
                "fee": fee,
                "billable_hours": max(1, int(duration_hours) + (1 if duration_minutes % 60 > 0 else 0))
            }
            
        except Exception as e:
            logger.error(f"Fee calculation error: {e}")
            return {
                "duration_minutes": 0,
                "duration_hours": 0,
                "duration_text": "Unknown",
                "fee": 5000,  # Default fee
                "billable_hours": 1
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
        """Force immediate ALPR detection for exit"""
        try:
            self._log_activity("Force exit detection triggered")
            
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
                # Process the detected vehicle for exit
                self._process_detected_exit_vehicle(best_result)
                
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
            self._log_activity(f"Force exit detection failed: {e}", "ERROR")
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
    
    def get_pending_payments(self) -> List[Dict[str, Any]]:
        """Get transactions awaiting payment confirmation"""
        # Get recent non-member exit transactions
        with database_service.get_session() as session:
            from ...core.models import ParkingTransaction
            
            transactions = session.query(ParkingTransaction).filter(
                ParkingTransaction.id_pintu_keluar == self.gate_id,
                ParkingTransaction.status == 0,
                ParkingTransaction.kategori == "umum",
                ParkingTransaction.pic_no_pol_keluar.isnot(None)  # Has exit detection
            ).order_by(ParkingTransaction.entry_time.desc()).limit(10).all()
            
            results = []
            for t in transactions:
                duration_info = self._calculate_duration_and_fee(t)
                
                results.append({
                    "transaction_id": t.id,
                    "plate_number": t.no_pol,
                    "entry_time": t.entry_time.isoformat(),
                    "duration": duration_info["duration_text"],
                    "fee": duration_info["fee"],
                    "exit_confidence": t.exit_plate_confidence,
                    "has_exit_images": bool(t.pic_no_pol_keluar)
                })
            
            return results
    
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
        
        self._log_activity("Manless exit gate shut down")
        logger.info(f"Manless exit gate {self.gate_id} cleaned up")
