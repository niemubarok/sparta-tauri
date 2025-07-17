"""
Manual Exit Gate Implementation
Operator-controlled exit gate with barcode scanning and manual processing
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


class ManualExitGate:
    """Manual exit gate with operator control and barcode scanning"""
    
    def __init__(self, gate_id: str = "exit_manual"):
        self.gate_id = gate_id
        self.gate_type = "exit"
        self.gate_mode = "manual"
        
        # Services
        self.gate_service: Optional[GateService] = None
        
        # State
        self.is_running = False
        self.current_transaction = None
        self.activity_logs = []
        self.transaction_count = 0
        
        # Camera configuration
        self.plate_camera_id = f"{gate_id}_plate"
        self.driver_camera_id = f"{gate_id}_driver"
        
        # Manual operation settings
        self.alpr_confidence_threshold = 0.7
        self.barcode_timeout = 30  # seconds
        
        # Threading
        self.processing_lock = threading.Lock()
        
        # Initialize
        self.initialize()
    
    def initialize(self):
        """Initialize manual exit gate"""
        try:
            logger.info(f"Initializing manual exit gate: {self.gate_id}")
            
            # Load settings
            settings = database_service.get_gate_settings(self.gate_id)
            if not settings:
                logger.warning(f"No settings found for {self.gate_id}, using defaults")
                settings = self._create_default_settings()
            
            # Update settings from database
            self.alpr_confidence_threshold = settings.alpr_confidence_threshold or 0.7
            
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
                message="Manual exit gate initialized"
            )
            
            logger.info(f"Manual exit gate {self.gate_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize manual exit gate {self.gate_id}: {e}")
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
            alpr_confidence_threshold=0.7,
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
    
    def process_exit_by_barcode(self, barcode: str, operator_id: str = "operator") -> Dict[str, Any]:
        """Process exit using barcode/transaction ID"""
        try:
            self._log_activity(f"Exit processing started by {operator_id} with barcode: {barcode}")
            
            # Find transaction by barcode/ID
            transaction = database_service.find_transaction_by_id(barcode)
            
            if not transaction:
                return {
                    "success": False,
                    "message": f"Transaction not found: {barcode}"
                }
            
            if transaction.status != 0:
                return {
                    "success": False,
                    "message": f"Transaction already processed: {barcode}"
                }
            
            # Capture exit images
            images = self.capture_images()
            
            # Calculate parking duration and fee
            duration_info = self._calculate_duration_and_fee(transaction)
            
            # Update transaction
            transaction.waktu_keluar = datetime.utcnow()
            transaction.status = 1
            transaction.tarif = duration_info["fee"]
            transaction.durasi = duration_info["duration_minutes"]
            transaction.id_op_keluar = operator_id
            transaction.id_pintu_keluar = self.gate_id
            
            # Add exit images
            if images.get("plate"):
                transaction.pic_no_pol_keluar = images["plate"]
            if images.get("driver"):
                transaction.pic_driver_keluar = images["driver"]
            
            # Try ALPR on exit
            exit_alpr_result = None
            if images.get("plate"):
                exit_alpr_result = alpr_service.detect_plate(
                    images["plate"],
                    self.plate_camera_id
                )
                
                if exit_alpr_result:
                    transaction.exit_plate_confidence = exit_alpr_result.confidence
                    
                    # Check if exit plate matches entry plate
                    if exit_alpr_result.plate_number != transaction.no_pol:
                        self._log_activity(
                            f"Plate mismatch - Entry: {transaction.no_pol}, "
                            f"Exit: {exit_alpr_result.plate_number}",
                            "WARNING"
                        )
            
            # Save transaction
            with database_service.get_session() as session:
                session.merge(transaction)
                session.commit()
            
            # Open gate
            gate_opened = self.gate_service.open_gate(auto_close_seconds=15)
            
            if gate_opened:
                self.transaction_count += 1
                self._log_activity(
                    f"Exit processed successfully - ID: {transaction.id}, "
                    f"Plate: {transaction.no_pol}, Fee: Rp{duration_info['fee']:,}, "
                    f"Duration: {duration_info['duration_text']}"
                )
            else:
                self._log_activity(f"Gate failed to open for transaction {transaction.id}", "ERROR")
            
            return {
                "success": True,
                "transaction_id": transaction.id,
                "plate_number": transaction.no_pol,
                "entry_time": transaction.entry_time.isoformat(),
                "exit_time": transaction.waktu_keluar.isoformat(),
                "duration": duration_info["duration_text"],
                "fee": duration_info["fee"],
                "gate_opened": gate_opened,
                "exit_alpr": {
                    "detected": exit_alpr_result is not None,
                    "plate_number": exit_alpr_result.plate_number if exit_alpr_result else None,
                    "confidence": exit_alpr_result.confidence if exit_alpr_result else None,
                    "matches_entry": exit_alpr_result.plate_number == transaction.no_pol if exit_alpr_result else None
                } if exit_alpr_result else None
            }
            
        except Exception as e:
            self._log_activity(f"Exit processing failed: {e}", "ERROR")
            return {
                "success": False,
                "message": f"Exit processing failed: {str(e)}"
            }
    
    def process_exit_by_plate(self, plate_number: str, operator_id: str = "operator") -> Dict[str, Any]:
        """Process exit using plate number"""
        try:
            self._log_activity(f"Exit processing started by {operator_id} for plate: {plate_number}")
            
            # Find active transaction by plate
            transaction = database_service.find_transaction_by_plate(plate_number, status=0)
            
            if not transaction:
                return {
                    "success": False,
                    "message": f"No active transaction found for plate: {plate_number}"
                }
            
            # Process using barcode method
            return self.process_exit_by_barcode(str(transaction.id), operator_id)
            
        except Exception as e:
            self._log_activity(f"Exit by plate processing failed: {e}", "ERROR")
            return {
                "success": False,
                "message": f"Exit by plate failed: {str(e)}"
            }
    
    def auto_detect_plate_for_exit(self, operator_id: str = "operator") -> Dict[str, Any]:
        """Automatically detect plate and process exit"""
        try:
            self._log_activity(f"Auto plate detection for exit started by {operator_id}")
            
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
            
            if not plate_capture or not plate_capture.image_base64:
                return {
                    "success": False,
                    "message": "Failed to capture image"
                }
            
            # Run ALPR
            alpr_result = alpr_service.detect_plate(
                plate_capture.image_base64,
                self.plate_camera_id
            )
            
            if not alpr_result:
                return {
                    "success": False,
                    "message": "No plate detected in image"
                }
            
            if alpr_result.confidence < self.alpr_confidence_threshold:
                return {
                    "success": False,
                    "message": f"Low confidence detection: {alpr_result.confidence:.2f} < {self.alpr_confidence_threshold}",
                    "detected_plate": alpr_result.plate_number,
                    "confidence": alpr_result.confidence
                }
            
            # Process exit using detected plate
            result = self.process_exit_by_plate(alpr_result.plate_number, operator_id)
            
            # Add ALPR info to result
            if result["success"]:
                result["auto_detected"] = True
                result["detection_confidence"] = alpr_result.confidence
            
            return result
            
        except Exception as e:
            self._log_activity(f"Auto detect for exit failed: {e}", "ERROR")
            return {
                "success": False,
                "message": f"Auto detection failed: {str(e)}"
            }
    
    def manual_gate_open(self, reason: str = "Manual override", operator_id: str = "operator") -> Dict[str, Any]:
        """Manual gate open without transaction"""
        try:
            self._log_activity(f"Manual gate override by {operator_id}: {reason}")
            
            success = self.gate_service.open_gate(auto_close_seconds=15)
            
            if success:
                # Log the manual override
                database_service.log_activity(
                    gate_id=self.gate_id,
                    gate_type=self.gate_type,
                    level="WARNING",
                    message=f"Manual gate override: {reason}",
                    operator_id=operator_id
                )
                
                return {
                    "success": True,
                    "message": "Gate opened manually",
                    "reason": reason,
                    "operator_id": operator_id
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to open gate"
                }
        
        except Exception as e:
            self._log_activity(f"Manual gate override failed: {e}", "ERROR")
            return {
                "success": False,
                "message": f"Manual override failed: {str(e)}"
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
    
    def search_transactions(self, query: str, search_type: str = "auto") -> List[Dict[str, Any]]:
        """Search for transactions by various criteria"""
        try:
            transactions = []
            
            if search_type == "auto" or search_type == "id":
                # Try by transaction ID
                try:
                    transaction_id = int(query)
                    transaction = database_service.find_transaction_by_id(transaction_id)
                    if transaction and transaction.status == 0:
                        transactions.append(transaction)
                except ValueError:
                    pass
            
            if search_type == "auto" or search_type == "plate":
                # Try by plate number
                transaction = database_service.find_transaction_by_plate(query, status=0)
                if transaction and transaction not in transactions:
                    transactions.append(transaction)
            
            # Convert to response format
            results = []
            for t in transactions:
                duration_info = self._calculate_duration_and_fee(t)
                
                results.append({
                    "transaction_id": t.id,
                    "plate_number": t.no_pol,
                    "entry_time": t.entry_time.isoformat(),
                    "duration": duration_info["duration_text"],
                    "estimated_fee": duration_info["fee"],
                    "category": t.kategori,
                    "vehicle_type": t.id_kendaraan,
                    "entry_gate": t.id_pintu_masuk,
                    "has_images": bool(t.pic_no_pol_masuk)
                })
            
            return results
            
        except Exception as e:
            self._log_activity(f"Transaction search failed: {e}", "ERROR")
            return []
    
    def get_active_transactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of active transactions"""
        try:
            with database_service.get_session() as session:
                from ...core.models import ParkingTransaction
                
                transactions = session.query(ParkingTransaction).filter(
                    ParkingTransaction.status == 0
                ).order_by(ParkingTransaction.entry_time.desc()).limit(limit).all()
                
                results = []
                for t in transactions:
                    duration_info = self._calculate_duration_and_fee(t)
                    
                    results.append({
                        "transaction_id": t.id,
                        "plate_number": t.no_pol,
                        "entry_time": t.entry_time.isoformat(),
                        "duration": duration_info["duration_text"],
                        "estimated_fee": duration_info["fee"],
                        "category": t.kategori,
                        "vehicle_type": t.id_kendaraan,
                        "entry_gate": t.id_pintu_masuk,
                        "has_images": bool(t.pic_no_pol_masuk)
                    })
                
                return results
            
        except Exception as e:
            self._log_activity(f"Get active transactions failed: {e}", "ERROR")
            return []
    
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
    
    def update_settings(self, settings_data: Dict[str, Any]) -> bool:
        """Update gate settings"""
        try:
            updated_settings = database_service.update_gate_settings(self.gate_id, settings_data)
            
            if updated_settings:
                # Update local settings
                if "alpr_confidence_threshold" in settings_data:
                    self.alpr_confidence_threshold = settings_data["alpr_confidence_threshold"]
                
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
        if self.gate_service:
            self.gate_service.cleanup()
        
        camera_service.remove_camera(self.plate_camera_id)
        camera_service.remove_camera(self.driver_camera_id)
        
        self._log_activity("Manual exit gate shut down")
        logger.info(f"Manual exit gate {self.gate_id} cleaned up")
