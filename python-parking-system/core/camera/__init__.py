"""
Camera package initialization
"""

from .manager import (
    CameraConfig,
    CameraCapture,
    BaseCamera,
    UsbCamera,
    IpCamera,
    CameraManager,
    get_camera_manager,
    detect_usb_cameras
)

__all__ = [
    "CameraConfig",
    "CameraCapture",
    "BaseCamera", 
    "UsbCamera",
    "IpCamera",
    "CameraManager",
    "get_camera_manager",
    "detect_usb_cameras"
]
