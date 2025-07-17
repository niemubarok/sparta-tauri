"""
Gate control service for serial and GPIO operations
"""

import asyncio
import logging
import time
import threading
from typing import Optional, Dict, Any, Callable, List
from enum import Enum
import json

# Try to import hardware-specific modules
try:
    import serial
    from serial.tools import list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    logger.warning("pyserial not available - serial control disabled")

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    # logger.info("RPi.GPIO not available - GPIO control disabled")

logger = logging.getLogger(__name__)


class GateStatus(Enum):
    CLOSED = "closed"
    OPEN = "open"
    OPENING = "opening"
    CLOSING = "closing"
    ERROR = "error"


class ControlMode(Enum):
    SIMULATION = "simulation"
    SERIAL = "serial"
    GPIO = "gpio"


class GateService:
    """Gate control service with multiple control modes"""
    
    def __init__(self, gate_id: str = "default"):
        self.gate_id = gate_id
        self.status = GateStatus.CLOSED
        self.control_mode = ControlMode.SIMULATION
        self.last_error = None
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Status listeners
        self.status_listeners: List[Callable] = []
        
        # Serial configuration
        self.serial_port = None
        self.serial_config = {
            "port": "/dev/ttyUSB0",
            "baudrate": 9600,
            "timeout": 1
        }
        
        # GPIO configuration
        self.gpio_config = {
            "pin": 24,
            "active_high": True
        }
        
        # Statistics
        self.operation_count = 0
        self.error_count = 0
        self.successful_operations = 0
        
        # Auto-close timer
        self.auto_close_timer = None
        
        # Initialize based on available hardware
        self._initialize()
    
    def _initialize(self):
        """Initialize gate service based on available hardware"""
        if GPIO_AVAILABLE and self._try_gpio_mode():
            self.control_mode = ControlMode.GPIO
            logger.info(f"Gate {self.gate_id} initialized in GPIO mode")
        elif SERIAL_AVAILABLE and self._try_serial_mode():
            self.control_mode = ControlMode.SERIAL
            logger.info(f"Gate {self.gate_id} initialized in Serial mode")
        else:
            self.control_mode = ControlMode.SIMULATION
            logger.info(f"Gate {self.gate_id} initialized in Simulation mode")
    
    def _try_gpio_mode(self) -> bool:
        """Try to initialize GPIO mode"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.gpio_config["pin"], GPIO.OUT)
            GPIO.output(self.gpio_config["pin"], GPIO.LOW)
            return True
        except Exception as e:
            logger.debug(f"GPIO initialization failed: {e}")
            return False
    
    def _try_serial_mode(self) -> bool:
        """Try to initialize serial mode"""
        try:
            ports = list(list_ports.comports())
            if not ports:
                logger.debug("No serial ports found")
                return False
            
            # Try to configure with first available port
            port = ports[0].device
            logger.debug(f"Attempting to configure serial port: {port}")
            return self.configure_serial(port)
        except Exception as e:
            logger.debug(f"Serial initialization failed: {e}")
            return False
    
    def configure_serial(self, port: str, baudrate: int = 9600) -> bool:
        """Configure serial connection"""
        if not SERIAL_AVAILABLE:
            logger.debug("Serial library not available")
            return False
        
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            
            self.serial_config["port"] = port
            self.serial_config["baudrate"] = baudrate
            
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=self.serial_config["timeout"]
            )
            
            logger.info(f"Serial port configured: {port} at {baudrate}")
            return True
            
        except Exception as e:
            logger.debug(f"Failed to configure serial port {port}: {e}")
            return False
    
    def add_status_listener(self, callback: Callable[[GateStatus], None]):
        """Add status change listener"""
        self.status_listeners.append(callback)
    
    def remove_status_listener(self, callback: Callable[[GateStatus], None]):
        """Remove status change listener"""
        if callback in self.status_listeners:
            self.status_listeners.remove(callback)
    
    def _notify_status_change(self, new_status: GateStatus):
        """Notify all listeners of status change"""
        for callback in self.status_listeners:
            try:
                callback(new_status)
            except Exception as e:
                logger.error(f"Error in status listener: {e}")
    
    def _set_status(self, status: GateStatus):
        """Set gate status and notify listeners"""
        if self.status != status:
            old_status = self.status
            self.status = status
            logger.info(f"Gate {self.gate_id} status: {old_status.value} -> {status.value}")
            self._notify_status_change(status)
    
    def open_gate(self, auto_close_seconds: Optional[int] = None) -> bool:
        """Open the gate"""
        with self.lock:
            try:
                self.operation_count += 1
                self._set_status(GateStatus.OPENING)
                
                success = False
                
                if self.control_mode == ControlMode.GPIO:
                    success = self._gpio_open_gate()
                elif self.control_mode == ControlMode.SERIAL:
                    success = self._serial_open_gate()
                else:  # SIMULATION
                    success = self._simulation_open_gate()
                
                if success:
                    self._set_status(GateStatus.OPEN)
                    self.successful_operations += 1
                    self.last_error = None
                    
                    # Setup auto-close if requested
                    if auto_close_seconds and auto_close_seconds > 0:
                        self._setup_auto_close(auto_close_seconds)
                    
                    logger.info(f"Gate {self.gate_id} opened successfully")
                else:
                    self._set_status(GateStatus.ERROR)
                    self.error_count += 1
                    logger.error(f"Failed to open gate {self.gate_id}")
                
                return success
                
            except Exception as e:
                self.error_count += 1
                self.last_error = str(e)
                self._set_status(GateStatus.ERROR)
                logger.error(f"Error opening gate {self.gate_id}: {e}")
                return False
    
    def close_gate(self) -> bool:
        """Close the gate"""
        with self.lock:
            try:
                self.operation_count += 1
                self._set_status(GateStatus.CLOSING)
                
                # Cancel auto-close timer if active
                if self.auto_close_timer:
                    self.auto_close_timer.cancel()
                    self.auto_close_timer = None
                
                success = False
                
                if self.control_mode == ControlMode.GPIO:
                    success = self._gpio_close_gate()
                elif self.control_mode == ControlMode.SERIAL:
                    success = self._serial_close_gate()
                else:  # SIMULATION
                    success = self._simulation_close_gate()
                
                if success:
                    self._set_status(GateStatus.CLOSED)
                    self.successful_operations += 1
                    self.last_error = None
                    logger.info(f"Gate {self.gate_id} closed successfully")
                else:
                    self._set_status(GateStatus.ERROR)
                    self.error_count += 1
                    logger.error(f"Failed to close gate {self.gate_id}")
                
                return success
                
            except Exception as e:
                self.error_count += 1
                self.last_error = str(e)
                self._set_status(GateStatus.ERROR)
                logger.error(f"Error closing gate {self.gate_id}: {e}")
                return False
    
    def _setup_auto_close(self, seconds: int):
        """Setup auto-close timer"""
        if self.auto_close_timer:
            self.auto_close_timer.cancel()
        
        def auto_close():
            logger.info(f"Auto-closing gate {self.gate_id} after {seconds} seconds")
            self.close_gate()
        
        self.auto_close_timer = threading.Timer(seconds, auto_close)
        self.auto_close_timer.start()
    
    def _gpio_open_gate(self) -> bool:
        """Open gate using GPIO"""
        try:
            pin = self.gpio_config["pin"]
            active_high = self.gpio_config["active_high"]
            
            if active_high:
                GPIO.output(pin, GPIO.HIGH)
            else:
                GPIO.output(pin, GPIO.LOW)
            
            logger.debug(f"GPIO gate open signal sent to pin {pin}")
            return True
            
        except Exception as e:
            logger.error(f"GPIO gate open failed: {e}")
            return False
    
    def _gpio_close_gate(self) -> bool:
        """Close gate using GPIO"""
        try:
            pin = self.gpio_config["pin"]
            active_high = self.gpio_config["active_high"]
            
            if active_high:
                GPIO.output(pin, GPIO.LOW)
            else:
                GPIO.output(pin, GPIO.HIGH)
            
            logger.debug(f"GPIO gate close signal sent to pin {pin}")
            return True
            
        except Exception as e:
            logger.error(f"GPIO gate close failed: {e}")
            return False
    
    def _serial_open_gate(self) -> bool:
        """Open gate using serial command"""
        return self._send_serial_command(" *OPEN1#")
    
    def _serial_close_gate(self) -> bool:
        """Close gate using serial command"""
        return self._send_serial_command(" *CLOSE1#")
    
    def _send_serial_command(self, command: str) -> bool:
        """Send command via serial port"""
        if not SERIAL_AVAILABLE:
            logger.warning(f"Serial not available - simulating command: {command}")
            return True
        
        try:
            if not self.serial_port or not self.serial_port.is_open:
                if not self.configure_serial(self.serial_config["port"]):
                    return False
            
            self.serial_port.write(command.encode('utf-8'))
            self.serial_port.flush()
            
            logger.debug(f"Serial command sent: {command}")
            return True
            
        except Exception as e:
            logger.error(f"Serial command failed: {e}")
            return False
    
    def _simulation_open_gate(self) -> bool:
        """Open gate in simulation mode"""
        logger.info(f"🎭 SIMULATION: Gate {self.gate_id} opened")
        time.sleep(0.5)  # Simulate operation time
        return True
    
    def _simulation_close_gate(self) -> bool:
        """Close gate in simulation mode"""
        logger.info(f"🎭 SIMULATION: Gate {self.gate_id} closed")
        time.sleep(0.5)  # Simulate operation time
        return True
    
    async def open_gate_async(self, auto_close_seconds: Optional[int] = None) -> bool:
        """Async version of open gate"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.open_gate, auto_close_seconds)
    
    async def close_gate_async(self) -> bool:
        """Async version of close gate"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.close_gate)
    
    def get_status(self) -> Dict[str, Any]:
        """Get gate status information"""
        return {
            "gate_id": self.gate_id,
            "status": self.status.value,
            "control_mode": self.control_mode.value,
            "last_error": self.last_error,
            "operation_count": self.operation_count,
            "successful_operations": self.successful_operations,
            "error_count": self.error_count,
            "auto_close_active": self.auto_close_timer is not None
        }
    
    def test_gate(self, test_duration: int = 3) -> Dict[str, Any]:
        """Test gate operation"""
        test_results = {
            "test_started": time.time(),
            "control_mode": self.control_mode.value,
            "open_test": False,
            "close_test": False,
            "errors": []
        }
        
        try:
            # Test open
            logger.info(f"Testing gate {self.gate_id} open...")
            if self.open_gate():
                test_results["open_test"] = True
                time.sleep(test_duration)
            else:
                test_results["errors"].append("Failed to open gate")
            
            # Test close
            logger.info(f"Testing gate {self.gate_id} close...")
            if self.close_gate():
                test_results["close_test"] = True
            else:
                test_results["errors"].append("Failed to close gate")
            
            test_results["success"] = test_results["open_test"] and test_results["close_test"]
            test_results["test_duration"] = time.time() - test_results["test_started"]
            
            return test_results
            
        except Exception as e:
            test_results["errors"].append(f"Test exception: {str(e)}")
            test_results["success"] = False
            return test_results
    
    def reset_statistics(self):
        """Reset operation statistics"""
        self.operation_count = 0
        self.error_count = 0
        self.successful_operations = 0
        self.last_error = None
        logger.info(f"Gate {self.gate_id} statistics reset")
    
    def get_available_serial_ports(self) -> List[str]:
        """Get list of available serial ports"""
        if not SERIAL_AVAILABLE:
            return []
        
        try:
            ports = list_ports.comports()
            return [port.device for port in ports]
        except Exception as e:
            logger.error(f"Failed to get serial ports: {e}")
            return []
    
    def cleanup(self):
        """Cleanup gate service resources"""
        # Cancel auto-close timer
        if self.auto_close_timer:
            self.auto_close_timer.cancel()
            self.auto_close_timer = None
        
        # Close serial port
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        
        # Cleanup GPIO
        if GPIO_AVAILABLE and self.control_mode == ControlMode.GPIO:
            try:
                GPIO.cleanup()
            except:
                pass
        
        logger.info(f"Gate {self.gate_id} service cleaned up")


# Gate service factory
def create_gate_service(gate_id: str, gate_type: str, control_mode: str = "simulation") -> GateService:
    """Create gate service with specific configuration"""
    service = GateService(gate_id)
    
    if control_mode == "gpio" and GPIO_AVAILABLE:
        service.control_mode = ControlMode.GPIO
        service._try_gpio_mode()
    elif control_mode == "serial" and SERIAL_AVAILABLE:
        service.control_mode = ControlMode.SERIAL
        service._try_serial_mode()
    else:
        service.control_mode = ControlMode.SIMULATION
    
    logger.info(f"Created gate service {gate_id} ({gate_type}) in {service.control_mode.value} mode")
    return service
