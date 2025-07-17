"""
Core database models for Python Parking System
Compatible with original Tauri system schema
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, Text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class ParkingTransaction(Base):
    """Main parking transaction table"""
    __tablename__ = "parking_transactions"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    no_pol = Column(String(20), nullable=False, index=True)
    id_kendaraan = Column(String(20), nullable=False)
    status = Column(Integer, nullable=False, default=0)  # 0=entered, 1=exited
    
    # Gate information
    id_pintu_masuk = Column(String(20))
    id_pintu_keluar = Column(String(20))
    
    # Timing
    entry_time = Column(DateTime, default=datetime.utcnow)
    waktu_keluar = Column(DateTime)
    
    # Operators
    id_op_masuk = Column(String(20))
    id_op_keluar = Column(String(20))
    id_shift_masuk = Column(String(20))
    id_shift_keluar = Column(String(20))
    
    # Transaction details
    kategori = Column(String(20))
    status_transaksi = Column(String(20))
    bayar_masuk = Column(Float, default=0)
    bayar_keluar = Column(Float, default=0)
    jenis_system = Column(String(20))
    tanggal = Column(DateTime, default=datetime.utcnow)
    
    # Images (stored as base64)
    pic_driver_masuk = Column(Text)
    pic_driver_keluar = Column(Text)
    pic_no_pol_masuk = Column(Text)
    pic_no_pol_keluar = Column(Text)
    
    # System fields
    sinkron = Column(Integer, default=0)
    upload = Column(Integer, default=0)
    manual = Column(Integer, default=0)
    
    # Additional fields
    no_barcode = Column(String(30), index=True)
    jenis_langganan = Column(String(20))
    veri_check = Column(Integer, default=0)
    alasan = Column(String(200))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ALPR confidence scores
    entry_plate_confidence = Column(Float)
    exit_plate_confidence = Column(Float)


class MemberEntry(Base):
    """Member entry tracking table"""
    __tablename__ = "member_entries"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id = Column(String(50), nullable=False, index=True)
    no_pol = Column(String(20), nullable=False, index=True)
    
    # Entry details
    entry_time = Column(DateTime, default=datetime.utcnow)
    waktu_keluar = Column(DateTime)
    id_pintu_masuk = Column(String(20))
    id_pintu_keluar = Column(String(20))
    
    # Status
    status = Column(Integer, default=0)  # 0=inside, 1=exited
    jenis_kendaraan = Column(String(20))
    
    # Images
    pic_masuk = Column(Text)
    pic_keluar = Column(Text)
    
    # System
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GateSettings(Base):
    """Gate configuration settings"""
    __tablename__ = "gate_settings"
    
    id = Column(String(50), primary_key=True)
    gate_type = Column(String(20), nullable=False)  # 'entry' or 'exit'
    gate_mode = Column(String(20), nullable=False)  # 'manual' or 'manless'
    
    # Serial/Hardware settings
    serial_port = Column(String(50))
    baud_rate = Column(Integer, default=9600)
    control_mode = Column(String(20), default='simulation')  # 'gpio', 'serial', 'simulation'
    gpio_pin = Column(Integer)
    
    # Camera settings
    plate_cam_ip = Column(String(100))
    plate_cam_username = Column(String(50))
    plate_cam_password = Column(String(50))
    plate_cam_device_id = Column(String(50))
    plate_cam_type = Column(String(20))  # 'usb' or 'cctv'
    
    driver_cam_ip = Column(String(100))
    driver_cam_username = Column(String(50))
    driver_cam_password = Column(String(50))
    driver_cam_device_id = Column(String(50))
    driver_cam_type = Column(String(20))  # 'usb' or 'cctv'
    
    # ALPR settings
    use_external_alpr = Column(Boolean, default=False)
    external_alpr_url = Column(String(200))
    alpr_confidence_threshold = Column(Float, default=0.8)
    
    # System settings
    auto_capture_interval = Column(Integer, default=5)
    gate_timeout = Column(Integer, default=10)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActivityLog(Base):
    """Activity logging table"""
    __tablename__ = "activity_logs"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    gate_id = Column(String(50), nullable=False, index=True)
    gate_type = Column(String(20), nullable=False)  # 'entry' or 'exit'
    
    # Log details
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    level = Column(String(10), default='INFO')  # 'INFO', 'WARNING', 'ERROR'
    message = Column(Text, nullable=False)
    
    # Context
    plate_number = Column(String(20))
    barcode = Column(String(30))
    operator_id = Column(String(20))
    
    # Additional data
    extra_data = Column(Text)  # JSON string for additional context


# Pydantic models for API
class ParkingTransactionCreate(BaseModel):
    no_pol: str
    id_kendaraan: str
    id_pintu_masuk: Optional[str] = None
    jenis_system: str = "manual"
    kategori: Optional[str] = None

class ParkingTransactionUpdate(BaseModel):
    status: Optional[int] = None
    waktu_keluar: Optional[datetime] = None
    id_pintu_keluar: Optional[str] = None
    bayar_keluar: Optional[float] = None
    pic_driver_keluar: Optional[str] = None
    pic_no_pol_keluar: Optional[str] = None
    exit_plate_confidence: Optional[float] = None

class ParkingTransactionResponse(BaseModel):
    id: str
    no_pol: str
    status: int
    entry_time: datetime
    waktu_keluar: Optional[datetime] = None
    bayar_masuk: float
    bayar_keluar: float
    no_barcode: Optional[str] = None
    
    class Config:
        from_attributes = True

class ALPRResult(BaseModel):
    plate_number: str
    confidence: float
    processing_time: float
    image_base64: Optional[str] = None
    bbox: Optional[Dict[str, float]] = None

class GateCommand(BaseModel):
    action: str  # 'open', 'close'
    gate_id: str
    operator_id: Optional[str] = None
    reason: Optional[str] = None

class CameraCapture(BaseModel):
    camera_type: str  # 'plate' or 'driver'
    camera_source: str  # 'usb' or 'cctv'
    image_base64: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SystemStatus(BaseModel):
    gate_id: str
    gate_type: str  # 'entry' or 'exit'
    gate_mode: str  # 'manual' or 'manless'
    gate_status: str  # 'open', 'closed', 'opening', 'closing', 'error'
    alpr_status: str  # 'ready', 'processing', 'error'
    camera_status: Dict[str, str]  # camera_type -> status
    last_activity: Optional[datetime] = None
    transaction_count: int = 0
