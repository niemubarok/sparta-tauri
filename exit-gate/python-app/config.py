#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exit Gate System Configuration
Compatible with Python 2.7 and 3.x
"""

from __future__ import absolute_import, print_function, unicode_literals

import os
import json
import logging
from configparser import ConfigParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class Config(object):
    """Configuration management for exit gate system"""
    
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = ConfigParser()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            logger.info("Loaded configuration from {}".format(self.config_file))
        else:
            self._create_default_config()
            logger.info("Created default configuration")
    
    def _create_default_config(self):
        """Create default configuration"""
        # Flask settings
        self.config.add_section('flask')
        self.config.set('flask', 'host', '0.0.0.0')
        self.config.set('flask', 'port', '5001')
        self.config.set('flask', 'debug', 'False')
        self.config.set('flask', 'secret_key', 'exit-gate-secret-key-change-me')
        
        # Database settings
        self.config.add_section('database')
        self.config.set('database', 'local_db', 'transactions')
        self.config.set('database', 'remote_url', 'http://localhost:5984')
        self.config.set('database', 'username', 'admin')
        self.config.set('database', 'password', 'password')
        self.config.set('database', 'auto_sync', 'True')
        self.config.set('database', 'sync_interval', '30')
        
        # Serial/Gate settings
        self.config.add_section('gate')
        self.config.set('gate', 'serial_port', '/dev/ttyUSB0')
        self.config.set('gate', 'baud_rate', '9600')
        self.config.set('gate', 'timeout', '10')
        self.config.set('gate', 'control_mode', 'serial')  # serial or gpio
        
        # GPIO settings (Raspberry Pi)
        self.config.add_section('gpio')
        self.config.set('gpio', 'gate_pin', '24')  # Changed to pin 24
        self.config.set('gpio', 'active_high', 'True')
        self.config.set('gpio', 'power_pin', '16')
        self.config.set('gpio', 'busy_pin', '20')
        self.config.set('gpio', 'live_pin', '21')
        self.config.set('gpio', 'pulse_duration', '500')
        
        # Camera settings
        self.config.add_section('camera')
        self.config.set('camera', 'enabled', 'True')
        self.config.set('camera', 'plate_camera_ip', '192.168.1.100')
        self.config.set('camera', 'plate_camera_username', 'admin')
        self.config.set('camera', 'plate_camera_password', 'admin123')
        self.config.set('camera', 'driver_camera_ip', '192.168.1.101')
        self.config.set('camera', 'driver_camera_username', 'admin')
        self.config.set('camera', 'driver_camera_password', 'admin123')
        self.config.set('camera', 'snapshot_path', 'Streaming/Channels/1/picture')
        self.config.set('camera', 'capture_timeout', '5')
        
        # Barcode scanner settings
        self.config.add_section('scanner')
        self.config.set('scanner', 'enabled', 'True')
        self.config.set('scanner', 'min_length', '6')
        self.config.set('scanner', 'max_length', '20')
        self.config.set('scanner', 'timeout', '100')
        
        # Audio settings
        self.config.add_section('audio')
        self.config.set('audio', 'enabled', 'True')
        self.config.set('audio', 'volume', '0.7')
        self.config.set('audio', 'sounds_path', 'sounds')
        
        # System settings
        self.config.add_section('system')
        self.config.set('system', 'gate_id', 'EXIT_GATE_01')
        self.config.set('system', 'operator_id', 'SYSTEM')
        self.config.set('system', 'auto_close_timeout', '10')
        
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
        logger.info("Configuration saved to {}".format(self.config_file))
    
    def get(self, section, option, fallback=None):
        """Get configuration value"""
        try:
            return self.config.get(section, option)
        except:
            return fallback
    
    def getint(self, section, option, fallback=0):
        """Get integer configuration value"""
        try:
            return self.config.getint(section, option)
        except:
            return fallback
    
    def getfloat(self, section, option, fallback=0.0):
        """Get float configuration value"""
        try:
            return self.config.getfloat(section, option)
        except:
            return fallback
    
    def getboolean(self, section, option, fallback=False):
        """Get boolean configuration value"""
        try:
            return self.config.getboolean(section, option)
        except:
            return fallback
    
    def set(self, section, option, value):
        """Set configuration value"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))
    
    def to_dict(self):
        """Convert configuration to dictionary"""
        result = {}
        for section in self.config.sections():
            result[section] = dict(self.config.items(section))
        return result

# Global configuration instance
config = Config()

# Environment detection
def is_raspberry_pi():
    """Check if running on Raspberry Pi"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            return 'Raspberry Pi' in f.read()
    except:
        return False

def is_gpio_available():
    """Check if GPIO is available"""
    if not is_raspberry_pi():
        return False
    
    try:
        import RPi.GPIO as GPIO
        return True
    except ImportError:
        logger.warning("RPi.GPIO not available")
        return False

# Constants for exit gate system
EXIT_GATE_VERSION = "1.0.0"
SUPPORTED_PYTHON_VERSIONS = ["2.7", "3.6", "3.7", "3.8", "3.9", "3.10"]

# Status constants (compatible with original system)
GATE_STATUS_CLOSED = 'CLOSED'
GATE_STATUS_OPENING = 'OPENING'
GATE_STATUS_OPEN = 'OPEN'
GATE_STATUS_CLOSING = 'CLOSING'
GATE_STATUS_ERROR = 'ERROR'

TRANSACTION_STATUS_ENTERED = 0
TRANSACTION_STATUS_EXITED = 1

CONTROL_MODE_SERIAL = 'serial'
CONTROL_MODE_GPIO = 'gpio'
