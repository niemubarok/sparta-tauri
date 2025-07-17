"""
GPIO service for Raspberry Pi
"""
import logging
import time
from typing import Dict, Any
import threading

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except ImportError:
    HAS_GPIO = False
    logger.warning("RPi.GPIO not available - running in simulation mode")

class GPIOService:
    def __init__(self, config):
        self.config = config
        self.pins = {
            'trigger': self.config.getint('GPIO', 'trigger_pin'),
            'loop1': self.config.getint('GPIO', 'loop1_pin'),
            'loop2': self.config.getint('GPIO', 'loop2_pin'),
            'struk': self.config.getint('GPIO', 'struk_pin'),
            'led_live': self.config.getint('GPIO', 'led_live_pin'),
            'busy': self.config.getint('GPIO', 'busy_pin')
        }
        
        self.callbacks = {}
        self.simulation_mode = not HAS_GPIO
        
        if HAS_GPIO:
            self._setup_gpio()
        else:
            logger.info("Running in GPIO simulation mode")
    
    def _setup_gpio(self):
        """Setup GPIO pins"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Setup output pins
            GPIO.setup(self.pins['trigger'], GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(self.pins['struk'], GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(self.pins['led_live'], GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(self.pins['busy'], GPIO.OUT, initial=GPIO.LOW)
            
            # Setup input pins with pull-up resistors
            GPIO.setup(self.pins['loop1'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.pins['loop2'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # Set LED live to indicate system is running
            GPIO.output(self.pins['led_live'], GPIO.HIGH)
            
            logger.info("GPIO setup completed")
        except Exception as e:
            logger.error(f"Failed to setup GPIO: {e}")
            raise
    
    def set_busy(self, busy: bool):
        """Set busy status"""
        if HAS_GPIO:
            GPIO.output(self.pins['busy'], GPIO.HIGH if busy else GPIO.LOW)
        logger.info(f"Busy status set to: {busy}")
    
    def open_gate(self):
        """Open gate by triggering gate motor"""
        try:
            self.set_busy(True)
            
            if HAS_GPIO:
                # Send high signal to trigger pin
                GPIO.output(self.pins['trigger'], GPIO.HIGH)
                time.sleep(1)  # Keep signal high for 1 second
                GPIO.output(self.pins['trigger'], GPIO.LOW)
            else:
                logger.info("SIMULATION: Gate opened")
                time.sleep(1)
            
            logger.info("Gate opened successfully")
            
            # Set busy to false after operation
            threading.Timer(3.0, lambda: self.set_busy(False)).start()
            
        except Exception as e:
            logger.error(f"Failed to open gate: {e}")
            self.set_busy(False)
            raise
    
    def print_ticket(self):
        """Print ticket"""
        try:
            if HAS_GPIO:
                GPIO.output(self.pins['struk'], GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(self.pins['struk'], GPIO.LOW)
            else:
                logger.info("SIMULATION: Ticket printed")
            
            logger.info("Ticket printed successfully")
        except Exception as e:
            logger.error(f"Failed to print ticket: {e}")
            raise
    
    def setup_loop_detection(self, loop1_callback=None, loop2_callback=None):
        """Setup loop detection callbacks"""
        if not HAS_GPIO:
            logger.info("SIMULATION: Loop detection setup")
            return
        
        try:
            if loop1_callback:
                self.callbacks['loop1'] = loop1_callback
                GPIO.add_event_detect(self.pins['loop1'], GPIO.FALLING, 
                                    callback=self._loop1_triggered, bouncetime=1000)
            
            if loop2_callback:
                self.callbacks['loop2'] = loop2_callback
                GPIO.add_event_detect(self.pins['loop2'], GPIO.FALLING, 
                                    callback=self._loop2_triggered, bouncetime=1000)
            
            logger.info("Loop detection setup completed")
        except Exception as e:
            logger.error(f"Failed to setup loop detection: {e}")
            raise
    
    def _loop1_triggered(self, channel):
        """Loop1 triggered callback"""
        logger.info("Loop1 triggered - vehicle detected")
        if 'loop1' in self.callbacks:
            threading.Thread(target=self.callbacks['loop1']).start()
    
    def _loop2_triggered(self, channel):
        """Loop2 triggered callback"""
        logger.info("Loop2 triggered - vehicle positioned")
        if 'loop2' in self.callbacks:
            threading.Thread(target=self.callbacks['loop2']).start()
    
    def simulate_loop_trigger(self, loop_name: str):
        """Simulate loop trigger for testing"""
        if loop_name == 'loop1' and 'loop1' in self.callbacks:
            logger.info("SIMULATION: Loop1 triggered")
            threading.Thread(target=self.callbacks['loop1']).start()
        elif loop_name == 'loop2' and 'loop2' in self.callbacks:
            logger.info("SIMULATION: Loop2 triggered")
            threading.Thread(target=self.callbacks['loop2']).start()
    
    def cleanup(self):
        """Cleanup GPIO"""
        if HAS_GPIO:
            GPIO.cleanup()
            logger.info("GPIO cleanup completed")
    
    def __del__(self):
        """Destructor"""
        self.cleanup()
