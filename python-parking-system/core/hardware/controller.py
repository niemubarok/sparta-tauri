"""
Hardware control for gates, sensors, and serial communication
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Callable
import serial
import serial.tools.list_ports

logger = logging.getLogger(__name__)


class SerialConfig:
    """Serial port configuration"""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0,
                 parity: str = 'N', stopbits: int = 1, bytesize: int = 8):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "port": self.port,
            "baudrate": self.baudrate,
            "timeout": self.timeout,
            "parity": self.parity,
            "stopbits": self.stopbits,
            "bytesize": self.bytesize
        }


class GateCommand:
    """Gate control commands"""
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    STATUS = "STATUS"
    EMERGENCY_OPEN = "EMERGENCY_OPEN"
    EMERGENCY_STOP = "EMERGENCY_STOP"


class GateStatus:
    """Gate status values"""
    OPENED = "OPENED"
    CLOSED = "CLOSED"
    OPENING = "OPENING"
    CLOSING = "CLOSING"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class LoopSensor:
    """Loop sensor states"""
    TRIGGERED = "TRIGGERED"
    CLEAR = "CLEAR"


class BaseHardwareController(ABC):
    """Base abstract hardware controller"""
    
    def __init__(self, config: SerialConfig):
        self.config = config
        self._is_connected = False
        self._callbacks: Dict[str, Callable] = {}
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to hardware"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from hardware"""
        pass
    
    @abstractmethod
    async def send_command(self, command: str, data: str = "") -> bool:
        """Send command to hardware"""
        pass
    
    @abstractmethod
    async def read_data(self) -> Optional[str]:
        """Read data from hardware"""
        pass
    
    def add_callback(self, event_type: str, callback: Callable):
        """Add event callback"""
        self._callbacks[event_type] = callback
    
    def remove_callback(self, event_type: str):
        """Remove event callback"""
        self._callbacks.pop(event_type, None)
    
    async def _trigger_callback(self, event_type: str, data: Any = None):
        """Trigger event callback"""
        callback = self._callbacks.get(event_type)
        if callback:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Error in callback for {event_type}: {e}")


class SerialGateController(BaseHardwareController):
    """Serial-based gate controller"""
    
    def __init__(self, config: SerialConfig, gate_id: str):
        super().__init__(config)
        self.gate_id = gate_id
        self._serial = None
        self._read_task = None
        self._last_status = GateStatus.UNKNOWN
        self._loop_sensors = {
            "loop1": LoopSensor.CLEAR,
            "loop2": LoopSensor.CLEAR,
            "loop3": LoopSensor.CLEAR
        }
    
    async def connect(self) -> bool:
        """Connect to serial gate controller"""
        try:
            # Open serial connection in executor
            loop = asyncio.get_event_loop()
            self._serial = await loop.run_in_executor(
                None,
                lambda: serial.Serial(
                    port=self.config.port,
                    baudrate=self.config.baudrate,
                    timeout=self.config.timeout,
                    parity=self.config.parity,
                    stopbits=self.config.stopbits,
                    bytesize=self.config.bytesize
                )
            )
            
            if self._serial.is_open:
                self._is_connected = True
                
                # Start reading task
                self._read_task = asyncio.create_task(self._read_loop())
                
                logger.info(f"Gate controller {self.gate_id} connected to {self.config.port}")
                return True
            else:
                logger.error(f"Failed to open serial port {self.config.port}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect gate controller {self.gate_id}: {e}")
            self._is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from serial gate controller"""
        try:
            self._is_connected = False
            
            if self._read_task:
                self._read_task.cancel()
                try:
                    await self._read_task
                except asyncio.CancelledError:
                    pass
            
            if self._serial and self._serial.is_open:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._serial.close)
                self._serial = None
            
            logger.info(f"Gate controller {self.gate_id} disconnected")
            
        except Exception as e:
            logger.error(f"Error disconnecting gate controller {self.gate_id}: {e}")
    
    async def send_command(self, command: str, data: str = "") -> bool:
        """Send command to gate controller"""
        if not self._is_connected or not self._serial:
            logger.error(f"Gate controller {self.gate_id} not connected")
            return False
        
        try:
            # Format command
            if data:
                message = f"{command}:{data}\n"
            else:
                message = f"{command}\n"
            
            # Send command in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, 
                lambda: self._serial.write(message.encode())
            )
            
            logger.debug(f"Sent command to gate {self.gate_id}: {message.strip()}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send command to gate {self.gate_id}: {e}")
            return False
    
    async def read_data(self) -> Optional[str]:
        """Read data from gate controller"""
        if not self._is_connected or not self._serial:
            return None
        
        try:
            loop = asyncio.get_event_loop()
            
            # Check if data available
            if self._serial.in_waiting > 0:
                data = await loop.run_in_executor(
                    None, 
                    lambda: self._serial.readline().decode().strip()
                )
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to read data from gate {self.gate_id}: {e}")
            return None
    
    async def _read_loop(self):
        """Continuous reading loop"""
        while self._is_connected:
            try:
                data = await self.read_data()
                if data:
                    await self._process_incoming_data(data)
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in read loop for gate {self.gate_id}: {e}")
                await asyncio.sleep(1)
    
    async def _process_incoming_data(self, data: str):
        """Process incoming data from gate controller"""
        try:
            # Parse common gate data formats
            if ":" in data:
                key, value = data.split(":", 1)
                key = key.strip().upper()
                value = value.strip().upper()
                
                if key in ["STATUS", "GATE_STATUS"]:
                    old_status = self._last_status
                    self._last_status = value
                    
                    if old_status != value:
                        await self._trigger_callback("status_changed", {
                            "gate_id": self.gate_id,
                            "old_status": old_status,
                            "new_status": value
                        })
                
                elif key.startswith("LOOP"):
                    loop_num = key.replace("LOOP", "").lower()
                    old_state = self._loop_sensors.get(f"loop{loop_num}", LoopSensor.CLEAR)
                    new_state = LoopSensor.TRIGGERED if value == "1" else LoopSensor.CLEAR
                    
                    self._loop_sensors[f"loop{loop_num}"] = new_state
                    
                    if old_state != new_state:
                        await self._trigger_callback("loop_sensor_changed", {
                            "gate_id": self.gate_id,
                            "loop": f"loop{loop_num}",
                            "old_state": old_state,
                            "new_state": new_state
                        })
            
            # Trigger general data callback
            await self._trigger_callback("data_received", {
                "gate_id": self.gate_id,
                "data": data
            })
            
        except Exception as e:
            logger.error(f"Error processing data from gate {self.gate_id}: {e}")
    
    async def open_gate(self) -> bool:
        """Open the gate"""
        return await self.send_command(GateCommand.OPEN)
    
    async def close_gate(self) -> bool:
        """Close the gate"""
        return await self.send_command(GateCommand.CLOSE)
    
    async def emergency_open(self) -> bool:
        """Emergency open the gate"""
        return await self.send_command(GateCommand.EMERGENCY_OPEN)
    
    async def emergency_stop(self) -> bool:
        """Emergency stop the gate"""
        return await self.send_command(GateCommand.EMERGENCY_STOP)
    
    async def get_status(self) -> str:
        """Get current gate status"""
        await self.send_command(GateCommand.STATUS)
        return self._last_status
    
    def get_loop_sensor_state(self, loop_name: str) -> str:
        """Get loop sensor state"""
        return self._loop_sensors.get(loop_name, LoopSensor.CLEAR)
    
    def get_all_loop_states(self) -> Dict[str, str]:
        """Get all loop sensor states"""
        return self._loop_sensors.copy()


class HardwareManager:
    """Manages multiple hardware controllers"""
    
    def __init__(self):
        self._controllers: Dict[str, BaseHardwareController] = {}
    
    def add_gate_controller(self, gate_id: str, config: SerialConfig) -> bool:
        """Add a gate controller"""
        try:
            controller = SerialGateController(config, gate_id)
            self._controllers[gate_id] = controller
            logger.info(f"Added gate controller: {gate_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add gate controller {gate_id}: {e}")
            return False
    
    def remove_controller(self, gate_id: str) -> bool:
        """Remove a controller"""
        try:
            if gate_id in self._controllers:
                asyncio.create_task(self._controllers[gate_id].disconnect())
                del self._controllers[gate_id]
                logger.info(f"Removed controller: {gate_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove controller {gate_id}: {e}")
            return False
    
    def get_controller(self, gate_id: str) -> Optional[BaseHardwareController]:
        """Get controller by gate ID"""
        return self._controllers.get(gate_id)
    
    async def connect_controller(self, gate_id: str) -> bool:
        """Connect to a specific controller"""
        controller = self.get_controller(gate_id)
        if controller:
            return await controller.connect()
        return False
    
    async def disconnect_controller(self, gate_id: str) -> bool:
        """Disconnect from a specific controller"""
        controller = self.get_controller(gate_id)
        if controller:
            await controller.disconnect()
            return True
        return False
    
    async def disconnect_all(self):
        """Disconnect all controllers"""
        tasks = []
        for controller in self._controllers.values():
            tasks.append(controller.disconnect())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("All hardware controllers disconnected")
    
    def list_controllers(self) -> list:
        """List all controller IDs"""
        return list(self._controllers.keys())


def list_serial_ports() -> list:
    """List available serial ports"""
    try:
        ports = serial.tools.list_ports.comports()
        return [{"port": port.device, "description": port.description} for port in ports]
    except Exception as e:
        logger.error(f"Failed to list serial ports: {e}")
        return []


# Global hardware manager instance
_hardware_manager: Optional[HardwareManager] = None


def get_hardware_manager() -> HardwareManager:
    """Get or create the global hardware manager instance"""
    global _hardware_manager
    
    if _hardware_manager is None:
        _hardware_manager = HardwareManager()
    
    return _hardware_manager
