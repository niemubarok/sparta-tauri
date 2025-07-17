"""
Pydantic models for API requests and responses
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class CameraConfigModel(BaseModel):
    """Camera configuration model"""
    camera_id: str
    camera_type: str = Field(..., regex="^(usb|cctv)$")
    device_id: Optional[int] = None
    url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    snapshot_path: Optional[str] = None
    name: Optional[str] = None
    
    @validator('device_id')
    def validate_device_id(cls, v, values):
        if values.get('camera_type') == 'usb' and v is None:
            raise ValueError('device_id is required for USB cameras')
        return v
    
    @validator('url')
    def validate_url(cls, v, values):
        if values.get('camera_type') == 'cctv' and not v:
            raise ValueError('url is required for CCTV cameras')
        return v


class DetectedPlateModel(BaseModel):
    """Detected plate model"""
    plate_number: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    plate_image: Optional[str] = None
    bbox: List[float] = Field(default_factory=list)
    camera_id: str = ""
    processing_time: float = 0.0
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())


class AlprResultModel(BaseModel):
    """ALPR result model"""
    success: bool
    detected_plates: List[DetectedPlateModel] = Field(default_factory=list)
    processing_time: float = 0.0
    error: Optional[str] = None


class TransactionCreateModel(BaseModel):
    """Transaction creation model"""
    license_plate: str = Field(..., min_length=1, max_length=20)
    vehicle_type_id: Optional[int] = None
    member_id: Optional[int] = None
    is_member: bool = False
    entry_pic: Optional[str] = None
    driver_pic: Optional[str] = None
    entry_gate_id: Optional[str] = None
    entry_staff: Optional[str] = None


class TransactionUpdateModel(BaseModel):
    """Transaction update model"""
    status: Optional[str] = Field(None, regex="^(MASUK|KELUAR|BATAL)$")
    waktu_keluar: Optional[datetime] = None
    tarif: Optional[float] = Field(None, ge=0.0)
    payment_amount: Optional[float] = Field(None, ge=0.0)
    exit_pic: Optional[str] = None
    exit_gate_id: Optional[str] = None
    exit_staff: Optional[str] = None


class TransactionModel(BaseModel):
    """Transaction model"""
    id: int
    ticket_id: str
    license_plate: str
    status: str
    vehicle_type_id: Optional[int] = None
    member_id: Optional[int] = None
    is_member: bool = False
    waktu_masuk: datetime
    waktu_keluar: Optional[datetime] = None
    tarif: float = 0.0
    payment_amount: float = 0.0
    entry_pic: Optional[str] = None
    driver_pic: Optional[str] = None
    exit_pic: Optional[str] = None
    entry_gate_id: Optional[str] = None
    exit_gate_id: Optional[str] = None
    entry_staff: Optional[str] = None
    exit_staff: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MemberModel(BaseModel):
    """Member model"""
    id: int
    member_id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    license_plate: Optional[str] = None
    status: str
    valid_until: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VehicleTypeModel(BaseModel):
    """Vehicle type model"""
    id: int
    name: str
    tarif_awal: float = 0.0
    tarif_berikutnya: float = 0.0
    tarif_maksimal: float = 0.0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GateSettingsModel(BaseModel):
    """Gate settings model"""
    id: Optional[int] = None
    gate_id: str
    gate_type: str = Field(..., regex="^(entry|exit)$")
    gate_mode: str = Field(..., regex="^(manual|manless)$")
    
    # Camera settings
    plate_cam_type: Optional[str] = Field(None, regex="^(usb|cctv)$")
    plate_cam_device_id: Optional[int] = None
    plate_cam_ip: Optional[str] = None
    plate_cam_username: Optional[str] = None
    plate_cam_password: Optional[str] = None
    plate_cam_snapshot_path: Optional[str] = None
    
    driver_cam_type: Optional[str] = Field(None, regex="^(usb|cctv)$")
    driver_cam_device_id: Optional[int] = None
    driver_cam_ip: Optional[str] = None
    driver_cam_username: Optional[str] = None
    driver_cam_password: Optional[str] = None
    driver_cam_snapshot_path: Optional[str] = None
    
    # ALPR settings
    use_external_alpr: bool = False
    alpr_websocket_url: Optional[str] = None
    alpr_confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    
    # Serial port settings
    serial_port: Optional[str] = None
    serial_baudrate: int = 9600
    
    # General settings
    settings_json: Optional[str] = None
    
    class Config:
        from_attributes = True


class ActivityLogModel(BaseModel):
    """Activity log model"""
    id: Optional[int] = None
    gate_id: str
    level: str = Field(default="INFO", regex="^(INFO|WARNING|ERROR)$")
    message: str = Field(..., min_length=1)
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class ProcessImageRequest(BaseModel):
    """Process image request model"""
    image_data: str = Field(..., description="Base64 encoded image or file path")
    camera_id: str = Field(default="", description="Camera identifier")


class GateCommandRequest(BaseModel):
    """Gate command request model"""
    command: str = Field(..., regex="^(OPEN|CLOSE|STATUS|EMERGENCY_OPEN|EMERGENCY_STOP)$")
    data: str = Field(default="")


class GateStatusResponse(BaseModel):
    """Gate status response model"""
    gate_id: str
    status: str
    loop_sensors: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ApiResponse(BaseModel):
    """Generic API response model"""
    success: bool = True
    message: str = ""
    data: Optional[Any] = None
    error: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated response model"""
    items: List[Any]
    total: int
    page: int = 1
    per_page: int = 10
    pages: int = 1


class CameraTestResponse(BaseModel):
    """Camera test response model"""
    camera_id: str
    success: bool
    message: str = ""
    image_data: Optional[str] = None


class SystemStatusResponse(BaseModel):
    """System status response model"""
    alpr_engine_status: bool
    database_status: bool
    cameras: Dict[str, bool] = Field(default_factory=dict)
    gates: Dict[str, bool] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
