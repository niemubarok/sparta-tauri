#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Audio Functionality for Exit Gate System
"""

from __future__ import print_function
import time
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_audio_service():
    """Test the audio service functionality"""
    print("=== Testing Audio Service ===")
    
    try:
        from audio_service import audio_service
        print("✅ Audio service imported successfully")
        
        # Get audio info
        info = audio_service.get_audio_info()
        print("\n📊 Audio System Information:")
        for key, value in info.items():
            print("  {}: {}".format(key, value))
        
        # Check if audio is enabled
        if audio_service.is_enabled():
            print("\n🔊 Audio is enabled and ready")
            
            # Test all sounds
            sounds_to_test = [
                ('scan', 'Barcode scan sound'),
                ('gate_open', 'Gate opening sound'),
                ('gate_close', 'Gate closing sound'),
                ('success', 'Success sound'),
                ('error', 'Error sound'),
                ('welcome', 'Welcome sound'),
                ('entrance', 'Entrance sound'),
                ('exit', 'Exit sound')
            ]
            
            print("\n🎵 Testing sound playback...")
            for sound_name, description in sounds_to_test:
                print("Playing '{}' - {}...".format(sound_name, description))
                success = audio_service.play_sound(sound_name, async_play=False)
                print("Result: {}".format("✅ OK" if success else "❌ FAILED"))
                time.sleep(0.5)  # Short pause between sounds
            
            print("\n🎚️ Testing volume control...")
            original_volume = audio_service.volume
            print("Original volume: {}".format(original_volume))
            
            # Test different volume levels
            for volume in [0.3, 0.7, 1.0]:
                audio_service.set_volume(volume)
                print("Testing volume {}: ".format(volume), end="")
                success = audio_service.play_sound('success', async_play=False)
                print("{}".format("✅ OK" if success else "❌ FAILED"))
                time.sleep(0.5)
            
            # Restore original volume
            audio_service.set_volume(original_volume)
            print("Volume restored to: {}".format(original_volume))
            
        else:
            print("\n❌ Audio is disabled or not available")
            print("Reasons:")
            if not info['pygame_available']:
                print("  - pygame not available (run: pip install pygame)")
            if not info['mixer_initialized']:
                print("  - mixer not initialized")
            if not info['enabled']:
                print("  - audio disabled in configuration")
        
    except ImportError as e:
        print("❌ Failed to import audio service: {}".format(str(e)))
        print("Make sure audio_service.py is in the same directory")
    except Exception as e:
        print("❌ Error testing audio service: {}".format(str(e)))
        import traceback
        traceback.print_exc()

def test_pygame_installation():
    """Test if pygame is properly installed"""
    print("\n=== Testing pygame Installation ===")
    
    try:
        import pygame
        print("✅ pygame is installed")
        print("Version: {}".format(pygame.version.ver))
        
        # Test mixer initialization
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            print("✅ pygame mixer initialized successfully")
            
            # Test basic functionality
            print("Testing basic mixer functions...")
            print("  Number of channels: {}".format(pygame.mixer.get_num_channels()))
            print("  Frequency: {}".format(pygame.mixer.get_init()[0] if pygame.mixer.get_init() else "Not initialized"))
            
            pygame.mixer.quit()
            print("✅ pygame mixer test completed")
            
        except Exception as e:
            print("❌ pygame mixer test failed: {}".format(str(e)))
            
    except ImportError:
        print("❌ pygame not installed")
        print("To install pygame, run:")
        print("  pip install pygame")
        print("  or")
        print("  pip2 install pygame  (for Python 2.7)")

def create_test_sounds():
    """Create simple test sound files if they don't exist"""
    print("\n=== Creating Test Sound Files ===")
    
    sounds_dir = os.path.join(os.path.dirname(__file__), 'sounds')
    
    # Ensure sounds directory exists
    if not os.path.exists(sounds_dir):
        os.makedirs(sounds_dir)
        print("✅ Created sounds directory: {}".format(sounds_dir))
    else:
        print("📁 Sounds directory exists: {}".format(sounds_dir))
    
    # Check for existing sound files
    sound_files = {
        'scan.wav': 'Barcode scan sound',
        'gate_open.wav': 'Gate opening sound', 
        'gate_close.wav': 'Gate closing sound',
        'success.wav': 'Success sound',
        'error.wav': 'Error sound',
        'welcome.wav': 'Welcome sound',
        'entrance.wav': 'Entrance sound',
        'exit.wav': 'Exit sound'
    }
    
    existing_files = []
    missing_files = []
    
    for filename, description in sound_files.items():
        filepath = os.path.join(sounds_dir, filename)
        if os.path.exists(filepath):
            existing_files.append((filename, description))
        else:
            missing_files.append((filename, description))
    
    if existing_files:
        print("\n✅ Existing sound files:")
        for filename, description in existing_files:
            print("  {} - {}".format(filename, description))
    
    if missing_files:
        print("\n⚠️  Missing sound files:")
        for filename, description in missing_files:
            print("  {} - {}".format(filename, description))
        
        print("\nTo add custom sounds:")
        print("1. Place WAV or MP3 files in: {}".format(sounds_dir))
        print("2. Use the exact filenames listed above")
        print("3. Recommended format: WAV, 22050 Hz, 16-bit, mono or stereo")
        
        # Try to create simple test sounds using audio_service
        try:
            from audio_service import audio_service
            if audio_service.is_enabled():
                print("\n🎵 Attempting to create test sounds...")
                audio_service._ensure_sounds_directory()
                audio_service._create_test_sounds()
                print("✅ Test sounds created (if supported)")
            else:
                print("❌ Cannot create test sounds - audio service not available")
        except Exception as e:
            print("❌ Failed to create test sounds: {}".format(str(e)))

def main():
    """Main test function"""
    print("🔊 Exit Gate Audio System Test")
    print("=" * 40)
    
    # Test pygame installation
    test_pygame_installation()
    
    # Create test sounds
    create_test_sounds()
    
    # Test audio service
    test_audio_service()
    
    print("\n🏁 Audio test completed!")
    print("\nIf audio is not working:")
    print("1. Install pygame: pip install pygame")
    print("2. Check audio device is connected and working")
    print("3. Verify sound files exist in sounds/ directory")
    print("4. Check system volume is not muted")

if __name__ == "__main__":
    main()
