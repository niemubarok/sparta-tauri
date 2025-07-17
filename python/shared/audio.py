"""
Audio service for playing sounds
"""
import logging
import threading
from typing import Optional
import os

logger = logging.getLogger(__name__)

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
    logger.warning("pygame not available - audio will be disabled")

class AudioService:
    def __init__(self, config):
        self.config = config
        self.enabled = self.config.getboolean('AUDIO', 'enabled') and HAS_PYGAME
        self.volume = self.config.getfloat('AUDIO', 'volume', 0.8)
        
        if self.enabled:
            try:
                pygame.mixer.init()
                pygame.mixer.music.set_volume(self.volume)
                logger.info("Audio service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize audio: {e}")
                self.enabled = False
        else:
            logger.info("Audio service disabled")
    
    def play_sound(self, sound_file: str):
        """Play sound file"""
        if not self.enabled:
            logger.info(f"SIMULATION: Playing sound {sound_file}")
            return
        
        try:
            if not os.path.exists(sound_file):
                logger.warning(f"Sound file not found: {sound_file}")
                # Try to create dummy audio file
                self._try_create_dummy_audio(sound_file)
                if not os.path.exists(sound_file):
                    logger.info(f"SIMULATION: Audio playback for {sound_file}")
                    return
            
            # Play sound in separate thread to avoid blocking
            threading.Thread(target=self._play_sound_thread, args=(sound_file,)).start()
        except Exception as e:
            logger.error(f"Failed to play sound {sound_file}: {e}")
    
    def _try_create_dummy_audio(self, sound_file: str):
        """Try to create a dummy audio file"""
        try:
            import wave
            import math
            
            # Create a simple beep
            duration = 1  # 1 second
            sample_rate = 44100
            frequency = 440  # A4 note
            
            samples = []
            for i in range(int(sample_rate * duration)):
                t = float(i) / sample_rate
                sample = math.sin(2.0 * math.pi * frequency * t) * 0.1  # Quiet
                samples.append(int(sample * 32767))
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(sound_file), exist_ok=True)
            
            # Write WAV file
            with wave.open(sound_file, 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                
                audio_data = b''
                for sample in samples:
                    audio_data += sample.to_bytes(2, byteorder='little', signed=True)
                
                wav_file.writeframes(audio_data)
            
            logger.info(f"Created dummy audio file: {sound_file}")
        except Exception as e:
            logger.error(f"Failed to create dummy audio: {e}")
    
    def _play_sound_thread(self, sound_file: str):
        """Play sound in separate thread"""
        try:
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
            
            # Wait for sound to finish
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
                
            logger.info(f"Sound played: {sound_file}")
        except Exception as e:
            logger.error(f"Error playing sound {sound_file}: {e}")
    
    def play_welcome(self):
        """Play welcome sound"""
        sound_file = self.config.get('AUDIO', 'welcome_sound', 'sounds/welcome.wav')
        self.play_sound(sound_file)
    
    def play_goodbye(self):
        """Play goodbye sound"""
        sound_file = self.config.get('AUDIO', 'goodbye_sound', 'sounds/goodbye.wav')
        self.play_sound(sound_file)
    
    def speak_text(self, text: str):
        """Speak text using TTS (placeholder for future implementation)"""
        logger.info(f"TTS: {text}")
        # TODO: Implement TTS functionality
    
    def cleanup(self):
        """Cleanup audio resources"""
        if self.enabled:
            try:
                pygame.mixer.quit()
                logger.info("Audio service cleanup completed")
            except Exception as e:
                logger.error(f"Error during audio cleanup: {e}")
