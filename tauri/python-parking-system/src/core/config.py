"""
Configuration module for Python Parking System
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Device Configuration
    device_type: str = "entry_manual"  # entry_manual, entry_manless, exit_manual, exit_manless
    device_id: str = "device_001"
    gate_type: str = "entry"  # entry, exit
    gate_mode: str = "manual"  # manual, manless
    
    # System Mode Configuration
    system_mode: str = "entry_manual"  # entry_manual, entry_manless, exit_manual, exit_manless
    ui_auto_start: bool = True
    
    # Database Configuration  
    database_type: str = "couchdb"  # couchdb, json
    couchdb_url: str = "http://127.0.0.1:5984"
    couchdb_host: str = "localhost"
    couchdb_port: int = 5984
    couchdb_username: Optional[str] = "admin"
    couchdb_password: Optional[str] = "password"
    couchdb_database: str = "parking_system"
    
    # Camera Configuration
    camera_source: int = 0  # Camera index or IP camera URL
    camera_width: int = 1920
    camera_height: int = 1080
    camera_fps: int = 30
    default_camera_timeout: int = 5
    camera_retry_attempts: int = 3
    
    # ALPR Configuration
    alpr_detector_model: str = "yolo-v9-t-384-license-plate-end2end"
    alpr_ocr_model: str = "global-plates-mobile-vit-v2-model"
    alpr_detector_path: str = "./models/yolo-v9-t-384-license-plate-end2end.pt"
    alpr_ocr_path: str = "./models/global-plates-mobile-vit-v2-model.pt" 
    alpr_confidence_threshold: float = 0.5
    
    # Automatic Detection Configuration (for manless gates)
    auto_scan_interval: int = 2
    vehicle_detection_threshold: float = 0.7
    auto_gate_timeout: int = 10
    
    # Gate Configuration
    gate_auto_close_timeout: int = 10
    gate_safety_timeout: int = 30
    
    # Network/API Configuration
    api_host: str = "localhost"
    api_port: int = 8000
    api_debug: bool = False
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "parking_system.log"
    
    # System Configuration
    system_name: str = "Python Parking System"
    system_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Allow extra fields from .env files


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()


# Global settings instance
settings = get_settings()
