#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gate Control Service for Exit Gate System
Compatible with Python 2.7 and 3.x
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import threading
import time
import subprocess
import os

# Remove problematic imports for Python 2.7 compatibility
try:
    from enum import Enum
except ImportError:
    # Python 2.7 fallback
    class Enum(object):
        pass

try:
    from typing import Optional, Callable  # For IDE support
except ImportError:
    # Python 2.7 fallback
    pass

# Serial import with fallback
try:
    import serial
    from serial.tools import list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("Warning: pyserial not available - serial control disabled")

from config import config, is_raspberry_pi, is_gpio_available
from config import GATE_STATUS_CLOSED, GATE_STATUS_OPENING, GATE_STATUS_OPEN
from config import GATE_STATUS_CLOSING, GATE_STATUS_ERROR
from config import CONTROL_MODE_SERIAL, CONTROL_MODE_GPIO

logger = logging.getLogger(__name__)

# GPIO import with fallback
GPIO = None
if is_gpio_available():
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
    except ImportError:
        logger.warning("RPi.GPIO not available")

class GateStatus(object):
    """Gate status constants (Python 2.7 compatible)"""
    CLOSED = GATE_STATUS_CLOSED
    OPENING = GATE_STATUS_OPENING
    OPEN = GATE_STATUS_OPEN
    CLOSING = GATE_STATUS_CLOSING
    ERROR = GATE_STATUS_ERROR

class ControlMode(object):
    """Control mode constants"""
    SERIAL = CONTROL_MODE_SERIAL
    GPIO = CONTROL_MODE_GPIO

class GateService(object):
    """Gate control service supporting both serial and GPIO control"""
    
    def __init__(self):
        self.current_status = GateStatus.CLOSED
        self.control_mode = ControlMode.SERIAL
        
        # Serial configuration
        self.serial_port = None
        self.serial_config = {
            'port': config.get('gate', 'serial_port', '/dev/ttyUSB0'),
            'baudrate': config.getint('gate', 'baud_rate', 9600),
            'timeout': config.getint('gate', 'timeout', 1)
        }
        
        # GPIO configuration
        self.gpio_config = {
            'gate_pin': config.getint('gpio', 'gate_pin', 18),
            'active_high': config.getboolean('gpio', 'active_high', True),
            'power_pin': config.getint('gpio', 'power_pin', 24),
            'busy_pin': config.getint('gpio', 'busy_pin', 23),
            'live_pin': config.getint('gpio', 'live_pin', 25),
            'pulse_duration': config.getfloat('gpio', 'pulse_duration', 0.5)
        }
        
        # Status listeners
        self.status_listeners = []
        
        # NOTE: Auto-close timer functionality removed
        # Gate will be controlled by hardware sensor
        
        # Initialize based on system capabilities
        self._initialize()
    
    def _initialize(self):
        """Initialize gate service based on system capabilities"""
        try:
            # Check if GPIO is available and raspberry pi
            if is_raspberry_pi() and is_gpio_available() and GPIO:
                self.control_mode = ControlMode.GPIO
                self._setup_gpio()
                logger.info("Initialized GPIO control mode")
            elif SERIAL_AVAILABLE:
                self.control_mode = ControlMode.SERIAL
                logger.info("Initialized Serial control mode")
            else:
                # Fallback to simulation mode for testing
                self.control_mode = "SIMULATION"
                logger.warning("Hardware not available - running in SIMULATION mode")
                
        except Exception as e:
            logger.error("Failed to initialize gate service: {}".format(str(e)))
            self.control_mode = "SIMULATION"
            logger.warning("Falling back to SIMULATION mode")
    
    def _setup_gpio(self):
        """Setup GPIO pins"""
        if not GPIO:
            return False
        
        try:
            # Setup gate control pin - FIXED: Initialize to CLOSED state
            GPIO.setup(self.gpio_config['gate_pin'], GPIO.OUT)
            # For relay: LOW = gate closed, HIGH = gate open
            GPIO.output(self.gpio_config['gate_pin'], GPIO.LOW)  # Start with gate CLOSED
            
            # Setup indicator pins if configured
            if self.gpio_config.get('power_pin'):
                GPIO.setup(self.gpio_config['power_pin'], GPIO.OUT)
                GPIO.output(self.gpio_config['power_pin'], GPIO.HIGH)  # Power on
            
            if self.gpio_config.get('live_pin'):
                GPIO.setup(self.gpio_config['live_pin'], GPIO.OUT)
                GPIO.output(self.gpio_config['live_pin'], GPIO.HIGH)  # System live
            
            if self.gpio_config.get('busy_pin'):
                GPIO.setup(self.gpio_config['busy_pin'], GPIO.OUT)
                GPIO.output(self.gpio_config['busy_pin'], GPIO.LOW)  # Not busy
            
            logger.info("GPIO pins configured successfully - Gate initialized to CLOSED (LOW)")
            return True
            
        except Exception as e:
            logger.error("Failed to setup GPIO: {}".format(str(e)))
            return False
    
    def get_available_ports(self):
        """Get list of available serial ports"""
        if not SERIAL_AVAILABLE:
            return []
            
        try:
            ports = list_ports.comports()
            return [port.device for port in ports]
        except Exception as e:
            logger.error("Failed to get serial ports: {}".format(str(e)))
            return []
    
    def configure_serial(self, port, baudrate=9600):
        """Configure serial connection"""
        if not SERIAL_AVAILABLE:
            logger.warning("Serial not available - cannot configure")
            return False
            
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            
            self.serial_config['port'] = port
            self.serial_config['baudrate'] = baudrate
            
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=self.serial_config['timeout']
            )
            
            logger.info("Serial port configured: {} at {}".format(port, baudrate))
            return True
            
        except Exception as e:
            logger.error("Failed to configure serial port: {}".format(str(e)))
            return False
    
    def open_gate(self, auto_close_timeout=None):
        """Open the gate"""
        try:
            self._set_status(GateStatus.OPENING)
            
            success = False
            
            if self.control_mode == ControlMode.GPIO and GPIO:
                success = self._gpio_open_gate()
            elif self.control_mode == ControlMode.SERIAL and SERIAL_AVAILABLE:
                success = self._serial_open_gate()
            elif self.control_mode == "SIMULATION":
                # Simulation mode for testing
                logger.info("SIMULATION: Gate opened")
                success = True
            else:
                logger.warning("No valid control mode available")
                success = False
            
            if success:
                self._set_status(GateStatus.OPEN)
                
                # NOTE: Auto-close timer removed - gate will be controlled by hardware sensor
                # No software timer needed
                
                logger.info("Gate opened successfully")
                return True
            else:
                self._set_status(GateStatus.ERROR)
                logger.error("Failed to open gate")
                return False
                
        except Exception as e:
            self._set_status(GateStatus.ERROR)
            logger.error("Error opening gate: {}".format(str(e)))
            return False
    
    def close_gate(self):
        """Close the gate"""
        try:
            self._set_status(GateStatus.CLOSING)
            
            success = False
            
            if self.control_mode == ControlMode.GPIO and GPIO:
                success = self._gpio_close_gate()
            elif self.control_mode == ControlMode.SERIAL and SERIAL_AVAILABLE:
                success = self._serial_close_gate()
            elif self.control_mode == "SIMULATION":
                # Simulation mode for testing
                logger.info("SIMULATION: Gate closed")
                success = True
            else:
                logger.warning("No valid control mode available")
                success = False
            
            if success:
                self._set_status(GateStatus.CLOSED)
                logger.info("Gate closed successfully")
                return True
            else:
                self._set_status(GateStatus.ERROR)
                logger.error("Failed to close gate")
                return False
                
        except Exception as e:
            self._set_status(GateStatus.ERROR)
            logger.error("Error closing gate: {}".format(str(e)))
            return False
    
    def _gpio_open_gate(self):
        """Open gate using GPIO"""
        if not GPIO:
            return False
        
        try:
            # Set busy indicator
            if self.gpio_config.get('busy_pin'):
                GPIO.output(self.gpio_config['busy_pin'], GPIO.HIGH)
            
            # FIXED: Open gate = HIGH (relay ON, gate opens)
            GPIO.output(self.gpio_config['gate_pin'], GPIO.HIGH)
            
            logger.info("GPIO gate OPEN signal sent to pin {} (HIGH - Gate Opening)".format(
                self.gpio_config['gate_pin']))
            return True
            
        except Exception as e:
            logger.error("GPIO gate open failed: {}".format(str(e)))
            return False
    
    def _gpio_close_gate(self):
        """Close gate using GPIO"""
        if not GPIO:
            return False
        
        try:
            # FIXED: Close gate = LOW (relay OFF, gate closes)
            GPIO.output(self.gpio_config['gate_pin'], GPIO.LOW)
            
            # Clear busy indicator
            if self.gpio_config.get('busy_pin'):
                GPIO.output(self.gpio_config['busy_pin'], GPIO.LOW)
            
            logger.info("GPIO gate CLOSE signal sent to pin {} (LOW - Gate Closing)".format(
                self.gpio_config['gate_pin']))
            return True
            
        except Exception as e:
            logger.error("GPIO gate close failed: {}".format(str(e)))
            return False
    
    def _serial_open_gate(self):
        """Open gate using serial command"""
        return self._send_serial_command('*OUT1ON#')
    
    def _serial_close_gate(self):
        """Close gate using serial command"""
        return self._send_serial_command('*OUT1OFF#')
    
    def _send_serial_command(self, command):
        """Send command via serial port"""
        if not SERIAL_AVAILABLE:
            logger.warning("Serial not available - simulating command: {}".format(command))
            return True  # Simulate success for testing
            
        try:
            if not self.serial_port or not self.serial_port.is_open:
                if not self.configure_serial(self.serial_config['port'], 
                                           self.serial_config['baudrate']):
                    return False
            
            self.serial_port.write(command.encode('utf-8'))
            self.serial_port.flush()
            
            logger.info("Serial command sent: {}".format(command))
            return True
            
        except Exception as e:
            logger.error("Serial command failed: {}".format(str(e)))
            return False
    
    def test_gate(self, test_duration=3):
        """Test gate operation (open then close)"""
        logger.info("Starting gate test...")
        
        if not self.open_gate():
            return False
        
        # Wait for test duration
        time.sleep(test_duration)
        
        return self.close_gate()
    
    def test_gpio_pin(self, pin, active_high=True, blink_count=3):
        """Test individual GPIO pin"""
        if not GPIO:
            return False
        
        try:
            GPIO.setup(pin, GPIO.OUT)
            
            for i in range(blink_count):
                # Turn on
                GPIO.output(pin, GPIO.HIGH if active_high else GPIO.LOW)
                time.sleep(0.5)
                
                # Turn off
                GPIO.output(pin, GPIO.LOW if active_high else GPIO.HIGH)
                time.sleep(0.5)
            
            logger.info("GPIO pin {} test completed ({} blinks)".format(pin, blink_count))
            return True
            
        except Exception as e:
            logger.error("GPIO pin {} test failed: {}".format(pin, str(e)))
            return False
    
    def _set_status(self, status):
        """Set gate status and notify listeners"""
        self.current_status = status
        for listener in self.status_listeners:
            try:
                listener(status)
            except Exception as e:
                logger.error("Status listener error: {}".format(str(e)))
    
    def get_status(self):
        """Get current gate status"""
        return self.current_status
    
    def add_status_listener(self, callback):
        """Add status change listener"""
        self.status_listeners.append(callback)
    
    def remove_status_listener(self, callback):
        """Remove status change listener"""
        if callback in self.status_listeners:
            self.status_listeners.remove(callback)
    
    def get_control_mode(self):
        """Get current control mode"""
        return self.control_mode
    
    def set_control_mode(self, mode):
        """Set control mode"""
        if mode in [ControlMode.SERIAL, ControlMode.GPIO]:
            if mode == ControlMode.GPIO and not (is_raspberry_pi() and GPIO):
                logger.error("GPIO mode not available on this system")
                return False
            
            self.control_mode = mode
            logger.info("Control mode set to: {}".format(mode))
            return True
        
        return False
    
    def get_system_info(self):
        """Get system information"""
        return {
            'is_raspberry_pi': is_raspberry_pi(),
            'gpio_available': is_gpio_available(),
            'control_mode': self.control_mode,
            'current_status': self.current_status,
            'serial_config': self.serial_config,
            'gpio_config': self.gpio_config,
            'available_ports': self.get_available_ports()
        }
    
    def cleanup(self):
        """Cleanup resources"""
        try:            
            if SERIAL_AVAILABLE and self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            
            if GPIO:
                GPIO.cleanup()
            
            logger.info("Gate service cleanup completed")
            
        except Exception as e:
            logger.error("Error during cleanup: {}".format(str(e)))

# Global gate service instance
gate_service = GateService()
