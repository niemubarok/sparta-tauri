#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Audio Service for Exit Gate System
Compatible with Python 2.7 and 3.x
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import threading
import time
from typing import Optional  # For IDE support

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logging.warning("pygame not available, audio functionality disabled")

from config import config

logger = logging.getLogger(__name__)

class AudioService(object):
    """Audio service for playing system sounds"""
    
    def __init__(self):
        self.enabled = config.getboolean('audio', 'enabled', True)
        self.volume = config.getfloat('audio', 'volume', 0.7)
        self.sounds_path = config.get('audio', 'sounds_path', 'sounds')
        
        # Sound files mapping
        self.sound_files = {
            'scan': 'scan.wav',
            'success': 'success.wav',
            'error': 'error.wav',
            'gate_open': 'gate_open.wav',
            'gate_close': 'gate_close.wav',
            'welcome': 'welcome.wav',
            'entrance': 'entrance.wav',
            'exit': 'exit.wav'
        }
        
        # Initialize pygame mixer if available
        self.mixer_initialized = False
        if PYGAME_AVAILABLE and self.enabled:
            self._initialize_mixer()
    
    def _initialize_mixer(self):
        """Initialize pygame mixer"""
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            pygame.mixer.set_num_channels(8)  # Allow multiple sounds
            self.mixer_initialized = True
            logger.info("Audio mixer initialized")
        except Exception as e:
            logger.error("Failed to initialize audio mixer: {}".format(str(e)))
            self.mixer_initialized = False
    
    def _get_sound_path(self, sound_name):
        """Get full path to sound file"""
        if sound_name not in self.sound_files:
            return None
        
        filename = self.sound_files[sound_name]
        return os.path.join(self.sounds_path, filename)
    
    def _ensure_sounds_directory(self):
        """Ensure sounds directory exists"""
        if not os.path.exists(self.sounds_path):
            os.makedirs(self.sounds_path)
            logger.info("Created sounds directory: {}".format(self.sounds_path))
    
    def play_sound(self, sound_name, async_play=True):
        """Play a sound file"""
        if not self.enabled or not PYGAME_AVAILABLE or not self.mixer_initialized:
            return False
        
        sound_path = self._get_sound_path(sound_name)
        if not sound_path or not os.path.exists(sound_path):
            logger.warning("Sound file not found: {} ({})".format(sound_name, sound_path))
            return False
        
        try:
            if async_play:
                # Play in background thread
                thread = threading.Thread(target=self._play_sound_sync, args=(sound_path,))
                thread.daemon = True
                thread.start()
            else:
                # Play synchronously
                self._play_sound_sync(sound_path)
            
            return True
            
        except Exception as e:
            logger.error("Error playing sound '{}': {}".format(sound_name, str(e)))
            return False
    
    def _play_sound_sync(self, sound_path):
        """Play sound synchronously"""
        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(self.volume)
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(sound)
                # Wait for sound to finish if playing synchronously
                while channel.get_busy():
                    time.sleep(0.01)
            
            logger.debug("Played sound: {}".format(sound_path))
            
        except Exception as e:
            logger.error("Error in _play_sound_sync: {}".format(str(e)))
    
    def play_scan_sound(self):
        """Play barcode scan sound"""
        return self.play_sound('scan')
    
    def play_success_sound(self):
        """Play success sound"""
        return self.play_sound('success')
    
    def play_error_sound(self):
        """Play error sound"""
        return self.play_sound('error')
    
    def play_gate_open_sound(self):
        """Play gate open sound"""
        return self.play_sound('gate_open')
    
    def play_gate_close_sound(self):
        """Play gate close sound"""
        return self.play_sound('gate_close')
    
    def play_welcome_sound(self):
        """Play welcome sound"""
        return self.play_sound('welcome')
    
    def play_entrance_sound(self):
        """Play entrance sound"""
        return self.play_sound('entrance')
    
    def play_exit_sound(self):
        """Play exit sound"""
        return self.play_sound('exit')
    
    def set_volume(self, volume):
        """Set audio volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        logger.info("Audio volume set to {}".format(self.volume))
    
    def enable(self):
        """Enable audio"""
        self.enabled = True
        if PYGAME_AVAILABLE and not self.mixer_initialized:
            self._initialize_mixer()
        logger.info("Audio enabled")
    
    def disable(self):
        """Disable audio"""
        self.enabled = False
        logger.info("Audio disabled")
    
    def is_enabled(self):
        """Check if audio is enabled"""
        return self.enabled and PYGAME_AVAILABLE and self.mixer_initialized
    
    def test_audio(self):
        """Test audio functionality"""
        if not self.is_enabled():
            logger.warning("Audio not available for testing")
            return False
        
        # Create test sounds directory
        self._ensure_sounds_directory()
        
        # Generate test beep sound if files don't exist
        self._create_test_sounds()
        
        # Test playing a sound
        logger.info("Testing audio playback...")
        return self.play_success_sound()
    
    def _create_test_sounds(self):
        """Create simple test sound files if they don't exist"""
        if not PYGAME_AVAILABLE:
            return
        
        import numpy as np
        
        try:
            # Create simple beep sounds
            sample_rate = 22050
            duration = 0.5  # seconds
            
            # Generate different frequency beeps for different sounds
            sound_configs = {
                'scan': 800,      # 800 Hz
                'success': 1000,  # 1000 Hz
                'error': 400,     # 400 Hz (lower pitch)
                'gate_open': 600, # 600 Hz
                'gate_close': 500, # 500 Hz
                'welcome': 750,   # 750 Hz
                'entrance': 650,  # 650 Hz
                'exit': 550       # 550 Hz
            }
            
            for sound_name, frequency in sound_configs.items():
                sound_path = self._get_sound_path(sound_name)
                if sound_path and not os.path.exists(sound_path):
                    self._generate_beep(sound_path, frequency, duration, sample_rate)
            
        except ImportError:
            logger.warning("numpy not available, cannot generate test sounds")
        except Exception as e:
            logger.error("Error creating test sounds: {}".format(str(e)))
    
    def _generate_beep(self, filename, frequency, duration, sample_rate):
        """Generate a simple beep sound file"""
        try:
            import numpy as np
            
            # Generate sine wave
            frames = int(duration * sample_rate)
            arr = np.zeros(frames)
            
            for i in range(frames):
                arr[i] = np.sin(2 * np.pi * frequency * i / sample_rate)
            
            # Apply fade in/out to avoid clicks
            fade_frames = int(0.05 * sample_rate)  # 50ms fade
            for i in range(fade_frames):
                arr[i] *= i / fade_frames
                arr[frames - 1 - i] *= i / fade_frames
            
            # Convert to 16-bit integers
            arr = (arr * 32767).astype(np.int16)
            
            # Create pygame sound and save
            sound = pygame.sndarray.make_sound(np.column_stack((arr, arr)))  # Stereo
            pygame.mixer.init()
            
            # Save as WAV file
            pygame.mixer.quit()
            pygame.mixer.init()
            
            # Write directly using wave module for better compatibility
            import wave
            import struct
            
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(2)  # Stereo
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                
                # Write stereo data
                for sample in arr:
                    wav_file.writeframes(struct.pack('<hh', sample, sample))
            
            logger.debug("Generated test sound: {}".format(filename))
            
        except Exception as e:
            logger.error("Error generating beep for {}: {}".format(filename, str(e)))
    
    def get_audio_info(self):
        """Get audio system information"""
        return {
            'pygame_available': PYGAME_AVAILABLE,
            'mixer_initialized': self.mixer_initialized,
            'enabled': self.enabled,
            'volume': self.volume,
            'sounds_path': self.sounds_path,
            'available_sounds': list(self.sound_files.keys())
        }
    
    def cleanup(self):
        """Cleanup audio resources"""
        try:
            if PYGAME_AVAILABLE and self.mixer_initialized:
                pygame.mixer.stop()  # Stop all sounds
                pygame.mixer.quit()
                self.mixer_initialized = False
            
            logger.info("Audio service cleanup completed")
            
        except Exception as e:
            logger.error("Error during audio cleanup: {}".format(str(e)))

# Global audio service instance
audio_service = AudioService()

# Test functions
def test_audio_service():
    """Test audio service functionality"""
    print("Testing audio service...")
    
    info = audio_service.get_audio_info()
    print("Audio info:", info)
    
    if audio_service.is_enabled():
        print("Testing audio playback...")
        
        # Test different sounds
        sounds_to_test = ['scan', 'success', 'error', 'gate_open', 'gate_close']
        
        for sound in sounds_to_test:
            print("Playing '{}'...".format(sound))
            success = audio_service.play_sound(sound, async_play=False)
            print("Result: {}".format("OK" if success else "FAILED"))
            time.sleep(1)
    else:
        print("Audio not available")

if __name__ == "__main__":
    test_audio_service()
