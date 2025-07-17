"""
Shared configuration for parking system
"""
import configparser
import os
from typing import Dict, Any

class Config:
    def __init__(self, config_file: str = None):
        self.config = configparser.ConfigParser()
        if config_file and os.path.exists(config_file):
            self.config.read(config_file)
        else:
            self._load_defaults()
    
    def _load_defaults(self):
        """Load default configuration"""
        self.config['DATABASE'] = {
            'host': 'localhost',
            'port': '5984',
            'username': 'admin',
            'password': 'admin',
            'database': 'parking_system'
        }
        
        self.config['CCTV'] = {
            'username': 'admin',
            'password': 'password',
            'ip_address': '192.168.1.100',
            'port': '80',
            'snapshot_path': '/snapshot'
        }
        
        self.config['GPIO'] = {
            'trigger_pin': '18',
            'loop1_pin': '23',
            'loop2_pin': '24',
            'struk_pin': '25',
            'led_live_pin': '17',
            'busy_pin': '22'
        }
        
        self.config['ALPR'] = {
            'enabled': 'true',
            'model_path': 'models/alpr_model',
            'confidence_threshold': '0.7'
        }
        
        self.config['WEBSOCKET'] = {
            'server_host': 'localhost',
            'server_port': '8765',
            'entry_gate_id': 'entry_gate_01',
            'exit_gate_id': 'exit_gate_01'
        }
        
        self.config['AUDIO'] = {
            'enabled': 'true',
            'volume': '0.8',
            'welcome_sound': 'sounds/welcome.wav',
            'goodbye_sound': 'sounds/goodbye.wav'
        }
    
    def get(self, section: str, key: str, fallback: str = None) -> str:
        """Get configuration value"""
        return self.config.get(section, key, fallback=fallback)
    
    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get boolean configuration value"""
        return self.config.getboolean(section, key, fallback=fallback)
    
    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        """Get integer configuration value"""
        return self.config.getint(section, key, fallback=fallback)
    
    def getfloat(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get float configuration value"""
        return self.config.getfloat(section, key, fallback=fallback)
    
    def save(self, config_file: str):
        """Save configuration to file"""
        with open(config_file, 'w') as f:
            self.config.write(f)
    
    @property
    def cctv_url(self) -> str:
        """Get complete CCTV snapshot URL"""
        username = self.get('CCTV', 'username')
        password = self.get('CCTV', 'password')
        ip = self.get('CCTV', 'ip_address')
        port = self.get('CCTV', 'port')
        path = self.get('CCTV', 'snapshot_path')
        return f"http://{username}:{password}@{ip}:{port}{path}"
    
    @property
    def database_url(self) -> str:
        """Get complete database URL"""
        host = self.get('DATABASE', 'host')
        port = self.get('DATABASE', 'port')
        return f"http://{host}:{port}"
