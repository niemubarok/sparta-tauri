#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gate Control Service for Exit Gate System - Improved Version
Enhanced error handling, better GPIO management, and comprehensive diagnostics
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import threading
import time
import subprocess
import os
import json
from datetime import datetime

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

# Config import with fallback
try:
    from config import config, is_raspberry_pi, is_gpio_available
    from config import GATE_STATUS_CLOSED, GATE_STATUS_OPENING, GATE_STATUS_OPEN
    from config import GATE_STATUS_CLOSING, GATE_STATUS_ERROR
    from config import CONTROL_MODE_SERIAL, CONTROL_MODE_GPIO
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    print("Warning: config module not available - using defaults")
    # Define fallback constants
    GATE_STATUS_CLOSED = "CLOSED"
    GATE_STATUS_OPENING = "OPENING"
    GATE_STATUS_OPEN = "OPEN"
    GATE_STATUS_CLOSING = "CLOSING"
    GATE_STATUS_ERROR = "ERROR"
    CONTROL_MODE_SERIAL = "SERIAL"
    CONTROL_MODE_GPIO = "GPIO"
    
    # Fallback functions
    def is_raspberry_pi():
        return check_raspberry_pi()
    
    def is_gpio_available():
        return GPIO_AVAILABLE

logger = logging.getLogger(__name__)

# GPIO import with enhanced fallback and diagnostics
GPIO = None
GPIO_AVAILABLE = False
GPIO_ERROR = None

def check_raspberry_pi():
    """Check if running on Raspberry Pi"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            return 'Raspberry Pi' in f.read() or 'BCM' in f.read()
    except:
        return False

def check_gpio_permissions():
    """Check GPIO permissions"""
    issues = []
    
    # Check gpio group
    try:
        result = subprocess.run(['groups'], capture_output=True, text=True)
        if 'gpio' not in result.stdout:
            issues.append("User not in gpio group")
    except:
        issues.append("Cannot check gpio group")
    
    # Check /dev/gpiomem
    if not os.path.exists('/dev/gpiomem'):
        issues.append("/dev/gpiomem missing")
    
    # Check /sys/class/gpio/export
    if os.path.exists('/sys/class/gpio/export'):
        try:
            with open('/sys/class/gpio/export', 'a') as f:
                pass
        except PermissionError:
            issues.append("GPIO export permission denied")
    else:
        issues.append("GPIO export missing")
    
    return issues

# Try to import and setup GPIO with detailed error reporting
if check_raspberry_pi():
    gpio_issues = check_gpio_permissions()
    if gpio_issues:
        GPIO_ERROR = "GPIO permission issues: " + ", ".join(gpio_issues)
        logger.warning(GPIO_ERROR)
    
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO_AVAILABLE = True
        logger.info("✅ RPi.GPIO imported and configured successfully")
    except ImportError as e:
        GPIO_ERROR = f"RPi.GPIO import failed: {e}"
        logger.warning(GPIO_ERROR)
    except Exception as e:
        GPIO_ERROR = f"RPi.GPIO setup failed: {e}"
        logger.warning(GPIO_ERROR)
else:
    GPIO_ERROR = "Not running on Raspberry Pi"
    logger.info("Not running on Raspberry Pi - GPIO disabled")

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
    SIMULATION = "SIMULATION"

class GateService(object):
    """Enhanced Gate control service with improved diagnostics and error handling"""
    
    def __init__(self):
        self.current_status = GateStatus.CLOSED
        self.control_mode = ControlMode.SIMULATION  # Start with safe default
        self.last_error = None
        self.operation_count = 0
        self.error_count = 0
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Serial configuration with fallbacks
        self.serial_port = None
        if CONFIG_AVAILABLE:
            self.serial_config = {
                'port': config.get('gate', 'serial_port', '/dev/ttyUSB0'),
                'baudrate': config.getint('gate', 'baud_rate', 9600),
                'timeout': config.getint('gate', 'timeout', 1)
            }
        else:
            self.serial_config = {
                'port': '/dev/ttyUSB0',
                'baudrate': 9600,
                'timeout': 1
            }
        
        # GPIO configuration with fallbacks
        if CONFIG_AVAILABLE:
            self.gpio_config = {
                'gate_pin': config.getint('gpio', 'gate_pin', 24),  # Changed default to 24
                'active_high': config.getboolean('gpio', 'active_high', True),
                'power_pin': config.getint('gpio', 'power_pin', 16),
                'busy_pin': config.getint('gpio', 'busy_pin', 20),
                'live_pin': config.getint('gpio', 'live_pin', 21),
                'pulse_duration': config.getfloat('gpio', 'pulse_duration', 0.5)
            }
        else:
            self.gpio_config = {
                'gate_pin': 24,  # Default gate pin
                'active_high': True,
                'power_pin': 16,
                'busy_pin': 20,
                'live_pin': 21,
                'pulse_duration': 0.5
            }
        
        # Status listeners
        self.status_listeners = []
        
        # Diagnostic information
        self.diagnostic_info = {
            'initialization_time': datetime.now().isoformat(),
            'gpio_available': GPIO_AVAILABLE,
            'gpio_error': GPIO_ERROR,
            'serial_available': SERIAL_AVAILABLE,
            'config_available': CONFIG_AVAILABLE,
            'raspberry_pi': check_raspberry_pi(),
            'gpio_permissions': check_gpio_permissions(),
            'last_operation': None,
            'successful_operations': 0,
            'failed_operations': 0
        }
        
        # Initialize based on system capabilities
        self._initialize()
    
    def _initialize(self):
        """Initialize gate service based on system capabilities with enhanced diagnostics"""
        logger.info("🚪 Initializing Gate Service...")
        
        try:
            # Determine control mode with priority: GPIO > Serial > Simulation
            if self._try_gpio_mode():
                self.control_mode = ControlMode.GPIO
                logger.info("✅ Initialized GPIO control mode")
            elif self._try_serial_mode():
                self.control_mode = ControlMode.SERIAL
                logger.info("✅ Initialized Serial control mode")
            else:
                self.control_mode = ControlMode.SIMULATION
                logger.warning("⚠️ Hardware not available - running in SIMULATION mode")
            
            # Record successful initialization
            self.diagnostic_info['control_mode'] = self.control_mode
            self.diagnostic_info['initialization_success'] = True
            
            logger.info(f"Gate Service initialized successfully in {self.control_mode} mode")
                
        except Exception as e:
            logger.error("Failed to initialize gate service: {}".format(str(e)))
            self.control_mode = ControlMode.SIMULATION
            self.last_error = str(e)
            self.error_count += 1
            self.diagnostic_info['control_mode'] = ControlMode.SIMULATION
            self.diagnostic_info['initialization_success'] = False
            self.diagnostic_info['initialization_error'] = str(e)
            logger.warning("Falling back to SIMULATION mode")
    
    def _try_gpio_mode(self):
        """Try to initialize GPIO mode with comprehensive checks"""
        if not GPIO_AVAILABLE:
            logger.debug("GPIO not available: {}".format(GPIO_ERROR or "Unknown reason"))
            return False
        
        if not check_raspberry_pi():
            logger.debug("Not running on Raspberry Pi")
            return False
        
        gpio_issues = check_gpio_permissions()
        if gpio_issues:
            logger.warning("GPIO permission issues: {}".format(", ".join(gpio_issues)))
            # Continue anyway - might work in some cases
        
        try:
            # Test GPIO setup
            return self._setup_gpio()
        except Exception as e:
            logger.error("GPIO mode initialization failed: {}".format(str(e)))
            return False
    
    def _try_serial_mode(self):
        """Try to initialize serial mode"""
        if not SERIAL_AVAILABLE:
            logger.debug("Serial not available")
            return False
        
        try:
            # Check for available serial ports
            ports = list(list_ports.comports())
            if not ports:
                logger.debug("No serial ports found")
                return False
            
            # Try to configure with first available port
            return self.configure_serial(ports[0].device, self.serial_config['baudrate'])
        except Exception as e:
            logger.debug("Serial mode initialization failed: {}".format(str(e)))
            return False
    
    def _setup_gpio(self):
        """Setup GPIO pins with enhanced error handling and validation"""
        if not GPIO_AVAILABLE or not GPIO:
            raise Exception("GPIO not available")
        
        try:
            pin = self.gpio_config['gate_pin']
            logger.info(f"Setting up GPIO pin {pin} for gate control...")
            
            # Setup gate control pin
            GPIO.setup(pin, GPIO.OUT)
            
            # Initialize to CLOSED state (LOW for active-high relays)
            initial_state = GPIO.LOW if self.gpio_config['active_high'] else GPIO.HIGH
            GPIO.output(pin, initial_state)
            logger.info(f"GPIO {pin} initialized to {'LOW' if initial_state == GPIO.LOW else 'HIGH'} (gate CLOSED)")
            
            # Setup indicator pins if configured
            if self.gpio_config.get('power_pin'):
                GPIO.setup(self.gpio_config['power_pin'], GPIO.OUT)
                GPIO.output(self.gpio_config['power_pin'], GPIO.HIGH)  # Power on
                logger.debug(f"Power indicator pin {self.gpio_config['power_pin']} set to HIGH")
            
            if self.gpio_config.get('live_pin'):
                GPIO.setup(self.gpio_config['live_pin'], GPIO.OUT)
                GPIO.output(self.gpio_config['live_pin'], GPIO.HIGH)  # System live
                logger.debug(f"Live indicator pin {self.gpio_config['live_pin']} set to HIGH")
            
            if self.gpio_config.get('busy_pin'):
                GPIO.setup(self.gpio_config['busy_pin'], GPIO.OUT)
                GPIO.output(self.gpio_config['busy_pin'], GPIO.LOW)  # Not busy
                logger.debug(f"Busy indicator pin {self.gpio_config['busy_pin']} set to LOW")
            
            # Test GPIO functionality
            self._test_gpio_pin(pin)
            
            logger.info("✅ GPIO pins configured and tested successfully")
            return True
            
        except Exception as e:
            logger.error("Failed to setup GPIO: {}".format(str(e)))
            raise
    
    def _test_gpio_pin(self, pin):
        """Test GPIO pin functionality with quick toggle"""
        try:
            logger.debug(f"Testing GPIO pin {pin}...")
            
            # Quick test - toggle pin
            active_state = GPIO.HIGH if self.gpio_config['active_high'] else GPIO.LOW
            inactive_state = GPIO.LOW if self.gpio_config['active_high'] else GPIO.HIGH
            
            # Toggle for test
            GPIO.output(pin, active_state)
            time.sleep(0.1)
            GPIO.output(pin, inactive_state)
            
            logger.debug(f"GPIO pin {pin} test completed successfully")
            
        except Exception as e:
            logger.error(f"GPIO pin {pin} test failed: {e}")
            raise
    
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
    
    def open_gate(self, auto_close_timeout=None):
        """Open the gate with enhanced error handling and logging"""
        with self.lock:
            try:
                logger.info("🔓 Opening gate...")
                self._set_status(GateStatus.OPENING)
                self._record_operation("open_gate")
                
                success = False
                
                if self.control_mode == ControlMode.GPIO and GPIO_AVAILABLE:
                    success = self._gpio_open_gate()
                elif self.control_mode == ControlMode.SERIAL and SERIAL_AVAILABLE:
                    success = self._serial_open_gate()
                elif self.control_mode == ControlMode.SIMULATION:
                    success = self._simulation_open_gate()
                else:
                    logger.error("No valid control mode available")
                    success = False
                
                if success:
                    self._set_status(GateStatus.OPEN)
                    self.diagnostic_info['successful_operations'] += 1
                    logger.info("✅ Gate opened successfully")
                    return True
                else:
                    self._set_status(GateStatus.ERROR)
                    self.error_count += 1
                    self.diagnostic_info['failed_operations'] += 1
                    logger.error("❌ Failed to open gate")
                    return False
                    
            except Exception as e:
                self._set_status(GateStatus.ERROR)
                self.last_error = str(e)
                self.error_count += 1
                self.diagnostic_info['failed_operations'] += 1
                logger.error("Error opening gate: {}".format(str(e)))
                return False
    
    def close_gate(self):
        """Close the gate with enhanced error handling and logging"""
        with self.lock:
            try:
                logger.info("🔒 Closing gate...")
                self._set_status(GateStatus.CLOSING)
                self._record_operation("close_gate")
                
                success = False
                
                if self.control_mode == ControlMode.GPIO and GPIO_AVAILABLE:
                    success = self._gpio_close_gate()
                elif self.control_mode == ControlMode.SERIAL and SERIAL_AVAILABLE:
                    success = self._serial_close_gate()
                elif self.control_mode == ControlMode.SIMULATION:
                    success = self._simulation_close_gate()
                else:
                    logger.error("No valid control mode available")
                    success = False
                
                if success:
                    self._set_status(GateStatus.CLOSED)
                    self.diagnostic_info['successful_operations'] += 1
                    logger.info("✅ Gate closed successfully")
                    return True
                else:
                    self._set_status(GateStatus.ERROR)
                    self.error_count += 1
                    self.diagnostic_info['failed_operations'] += 1
                    logger.error("❌ Failed to close gate")
                    return False
                    
            except Exception as e:
                self._set_status(GateStatus.ERROR)
                self.last_error = str(e)
                self.error_count += 1
                self.diagnostic_info['failed_operations'] += 1
                logger.error("Error closing gate: {}".format(str(e)))
                return False
    
    def _gpio_open_gate(self):
        """Open gate using GPIO with enhanced logging and error handling"""
        if not GPIO_AVAILABLE or not GPIO:
            raise Exception("GPIO not available")
        
        try:
            pin = self.gpio_config['gate_pin']
            
            # Set busy indicator
            if self.gpio_config.get('busy_pin'):
                GPIO.output(self.gpio_config['busy_pin'], GPIO.HIGH)
                logger.debug(f"Busy indicator pin {self.gpio_config['busy_pin']} set to HIGH")
            
            # Open gate = HIGH (relay ON, gate opens)
            active_state = GPIO.HIGH if self.gpio_config['active_high'] else GPIO.LOW
            GPIO.output(pin, active_state)
            
            state_name = "HIGH" if active_state == GPIO.HIGH else "LOW"
            logger.info(f"🔆 GPIO gate OPEN signal sent to pin {pin} ({state_name} - Gate Opening)")
            
            # Hold for pulse duration if specified
            if self.gpio_config.get('pulse_duration', 0) > 0:
                time.sleep(self.gpio_config['pulse_duration'])
                # Return to inactive state for pulse mode
                inactive_state = GPIO.LOW if self.gpio_config['active_high'] else GPIO.HIGH
                GPIO.output(pin, inactive_state)
                logger.debug(f"Pulse completed - pin {pin} returned to inactive state")
            
            return True
            
        except Exception as e:
            logger.error("GPIO gate open failed: {}".format(str(e)))
            raise
    
    def _gpio_close_gate(self):
        """Close gate using GPIO with enhanced logging and error handling"""
        if not GPIO_AVAILABLE or not GPIO:
            raise Exception("GPIO not available")
        
        try:
            pin = self.gpio_config['gate_pin']
            
            # Close gate = LOW (relay OFF, gate closes)
            inactive_state = GPIO.LOW if self.gpio_config['active_high'] else GPIO.HIGH
            GPIO.output(pin, inactive_state)
            
            # Clear busy indicator
            if self.gpio_config.get('busy_pin'):
                GPIO.output(self.gpio_config['busy_pin'], GPIO.LOW)
                logger.debug(f"Busy indicator pin {self.gpio_config['busy_pin']} set to LOW")
            
            state_name = "LOW" if inactive_state == GPIO.LOW else "HIGH"
            logger.info(f"🔅 GPIO gate CLOSE signal sent to pin {pin} ({state_name} - Gate Closing)")
            
            return True
            
        except Exception as e:
            logger.error("GPIO gate close failed: {}".format(str(e)))
            raise
    
    def _simulation_open_gate(self):
        """Open gate in simulation mode"""
        logger.info("🎭 SIMULATION: Gate opened")
        time.sleep(0.5)  # Simulate operation time
        return True
    
    def _simulation_close_gate(self):
        """Close gate in simulation mode"""
        logger.info("🎭 SIMULATION: Gate closed")
        time.sleep(0.5)  # Simulate operation time
        return True
    
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
    
    def _record_operation(self, operation):
        """Record operation for diagnostics"""
        self.operation_count += 1
        self.diagnostic_info['last_operation'] = {
            'operation': operation,
            'timestamp': datetime.now().isoformat(),
            'control_mode': self.control_mode
        }
    
    def get_diagnostic_info(self):
        """Get comprehensive diagnostic information"""
        return {
            **self.diagnostic_info,
            'current_status': self.current_status,
            'control_mode': self.control_mode,
            'last_error': self.last_error,
            'operation_count': self.operation_count,
            'error_count': self.error_count,
            'gpio_config': self.gpio_config,
            'serial_config': self.serial_config,
            'available_ports': self.get_available_ports() if SERIAL_AVAILABLE else [],
            'hardware_test_available': True
        }
    
    def test_hardware(self):
        """Test hardware functionality with detailed results"""
        logger.info("🧪 Testing hardware functionality...")
        
        test_results = {
            'gpio_test': False,
            'serial_test': False,
            'overall_success': False,
            'control_mode': self.control_mode,
            'timestamp': datetime.now().isoformat()
        }
        
        # Test GPIO if available
        if self.control_mode == ControlMode.GPIO and GPIO_AVAILABLE:
            try:
                original_status = self.current_status
                
                logger.debug("Testing GPIO functionality...")
                pin = self.gpio_config['gate_pin']
                active_state = GPIO.HIGH if self.gpio_config['active_high'] else GPIO.LOW
                inactive_state = GPIO.LOW if self.gpio_config['active_high'] else GPIO.HIGH
                
                # Quick GPIO test
                GPIO.output(pin, active_state)
                time.sleep(0.1)
                GPIO.output(pin, inactive_state)
                
                test_results['gpio_test'] = True
                test_results['gpio_pin'] = pin
                logger.info("✅ GPIO test passed")
                
                # Restore state
                self.current_status = original_status
                
            except Exception as e:
                logger.error(f"❌ GPIO test failed: {e}")
                test_results['gpio_test'] = False
                test_results['gpio_error'] = str(e)
        
        # Test Serial if available
        if self.control_mode == ControlMode.SERIAL and SERIAL_AVAILABLE:
            try:
                logger.debug("Testing Serial functionality...")
                # Test serial port opening
                if self.serial_port and self.serial_port.is_open:
                    test_results['serial_test'] = True
                    logger.info("✅ Serial test passed")
                else:
                    # Try to configure
                    ports = self.get_available_ports()
                    if ports:
                        test_results['serial_test'] = self.configure_serial(ports[0])
                    else:
                        test_results['serial_test'] = False
                        test_results['serial_error'] = "No serial ports available"
                        
            except Exception as e:
                logger.error(f"❌ Serial test failed: {e}")
                test_results['serial_test'] = False
                test_results['serial_error'] = str(e)
        
        # Simulation always works
        if self.control_mode == ControlMode.SIMULATION:
            test_results['simulation_test'] = True
            logger.info("✅ Simulation mode test passed")
        
        # Overall success
        if self.control_mode == ControlMode.GPIO:
            test_results['overall_success'] = test_results['gpio_test']
        elif self.control_mode == ControlMode.SERIAL:
            test_results['overall_success'] = test_results['serial_test']
        else:
            test_results['overall_success'] = True  # Simulation always works
        
        return test_results
    
    def reset_error_state(self):
        """Reset error state and counters"""
        with self.lock:
            if self.current_status == GateStatus.ERROR:
                self.current_status = GateStatus.CLOSED  # Assume closed as safe state
                self.last_error = None
                logger.info("Error state reset - status set to CLOSED")
                return True
            return False
    
    def reset_diagnostic_counters(self):
        """Reset diagnostic counters"""
        self.operation_count = 0
        self.error_count = 0
        self.diagnostic_info['successful_operations'] = 0
        self.diagnostic_info['failed_operations'] = 0
        logger.info("Diagnostic counters reset")
    
    def test_gate(self, test_duration=3):
        """Test gate operation (open then close) with enhanced logging"""
        logger.info("🧪 Starting comprehensive gate test...")
        
        try:
            # Test open
            logger.info("Testing gate OPEN...")
            if not self.open_gate():
                logger.error("Gate open test failed")
                return False
            
            # Wait for test duration
            logger.info(f"Waiting {test_duration} seconds...")
            time.sleep(test_duration)
            
            # Test close
            logger.info("Testing gate CLOSE...")
            if not self.close_gate():
                logger.error("Gate close test failed")
                return False
            
            logger.info("✅ Gate test completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Gate test failed with exception: {e}")
            return False
    
    def test_gpio_pin(self, pin, active_high=True, blink_count=3):
        """Test individual GPIO pin with enhanced error handling"""
        if not GPIO_AVAILABLE or not GPIO:
            logger.error("GPIO not available for pin testing")
            return False
        
        try:
            logger.info(f"Testing GPIO pin {pin} ({blink_count} blinks)...")
            GPIO.setup(pin, GPIO.OUT)
            
            for i in range(blink_count):
                # Turn on
                on_state = GPIO.HIGH if active_high else GPIO.LOW
                GPIO.output(pin, on_state)
                logger.debug(f"Pin {pin} blink {i+1} - ON ({on_state})")
                time.sleep(0.5)
                
                # Turn off
                off_state = GPIO.LOW if active_high else GPIO.HIGH
                GPIO.output(pin, off_state)
                logger.debug(f"Pin {pin} blink {i+1} - OFF ({off_state})")
                time.sleep(0.5)
            
            logger.info(f"✅ GPIO pin {pin} test completed successfully ({blink_count} blinks)")
            return True
            
        except Exception as e:
            logger.error(f"❌ GPIO pin {pin} test failed: {e}")
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
        """Get current gate status with additional information"""
        return {
            'status': self.current_status,
            'control_mode': self.control_mode,
            'last_error': self.last_error,
            'operation_count': self.operation_count,
            'error_count': self.error_count,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_current_status(self):
        """Get current gate status as string"""
        return str(self.current_status)
    
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
        """Set control mode with validation"""
        if mode in [ControlMode.SERIAL, ControlMode.GPIO, ControlMode.SIMULATION]:
            if mode == ControlMode.GPIO and not GPIO_AVAILABLE:
                logger.error("GPIO mode not available on this system")
                return False
            
            if mode == ControlMode.SERIAL and not SERIAL_AVAILABLE:
                logger.error("Serial mode not available on this system")
                return False
            
            self.control_mode = mode
            logger.info("Control mode set to: {}".format(mode))
            return True
        
        logger.error("Invalid control mode: {}".format(mode))
        return False
    
    def get_system_info(self):
        """Get comprehensive system information"""
        return {
            'raspberry_pi': check_raspberry_pi(),
            'gpio_available': GPIO_AVAILABLE,
            'gpio_error': GPIO_ERROR,
            'gpio_permissions': check_gpio_permissions(),
            'serial_available': SERIAL_AVAILABLE,
            'config_available': CONFIG_AVAILABLE,
            'control_mode': self.control_mode,
            'current_status': self.current_status,
            'last_error': self.last_error,
            'serial_config': self.serial_config,
            'gpio_config': self.gpio_config,
            'available_ports': self.get_available_ports(),
            'operation_count': self.operation_count,
            'error_count': self.error_count,
            'diagnostic_info': self.diagnostic_info
        }
    
    def cleanup(self):
        """Cleanup resources with enhanced error handling"""
        try:
            logger.info("🧹 Cleaning up gate service...")
            
            # Close serial port
            if SERIAL_AVAILABLE and self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                logger.info("Serial port closed")
            
            # Cleanup GPIO
            if GPIO_AVAILABLE and GPIO:
                # Set gate to safe state (closed) before cleanup
                try:
                    pin = self.gpio_config['gate_pin']
                    safe_state = GPIO.LOW if self.gpio_config['active_high'] else GPIO.HIGH
                    GPIO.output(pin, safe_state)
                    logger.info(f"Gate set to safe state (CLOSED) on pin {pin}")
                except:
                    pass
                
                GPIO.cleanup()
                logger.info("GPIO cleanup completed")
            
            # Reset status
            self.current_status = GateStatus.CLOSED
            
            logger.info("✅ Gate service cleanup completed successfully")
            
        except Exception as e:
            logger.error("Error during cleanup: {}".format(str(e)))

# Global gate service instance with error handling
try:
    gate_service = GateService()
    logger.info("Global gate service instance created successfully")
except Exception as e:
    logger.error(f"Failed to create gate service instance: {e}")
    # Create a dummy service for testing
    gate_service = None

# Cleanup on module exit
import atexit
if gate_service:
    atexit.register(gate_service.cleanup)
