"""
Create dummy audio files for testing
"""
import wave
import math
import os

def create_dummy_wav(filename, duration=2, sample_rate=44100, frequency=440):
    """Create a dummy WAV file with a simple tone"""
    try:
        # Generate a simple tone
        samples = []
        for i in range(int(sample_rate * duration)):
            t = float(i) / sample_rate
            # Generate sine wave
            sample = math.sin(2.0 * math.pi * frequency * t) * 0.3
            
            # Add fade in/out to avoid clicks
            fade_samples = int(sample_rate * 0.1)  # 0.1 second fade
            if i < fade_samples:
                sample *= float(i) / fade_samples
            elif i > int(sample_rate * duration) - fade_samples:
                sample *= float(int(sample_rate * duration) - i) / fade_samples
            
            # Convert to 16-bit integer
            samples.append(int(sample * 32767))
        
        # Write to WAV file
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Convert samples to bytes
            audio_data = b''
            for sample in samples:
                # Convert to signed 16-bit little-endian
                audio_data += sample.to_bytes(2, byteorder='little', signed=True)
            
            wav_file.writeframes(audio_data)
        
        print(f"✓ Created {filename}")
        return True
    except Exception as e:
        print(f"✗ Error creating {filename}: {e}")
        return False

def main():
    """Create dummy audio files"""
    print("Creating dummy audio files for parking system...")
    
    # Ensure we're in the sounds directory
    sounds_dir = os.path.dirname(__file__)
    if sounds_dir:
        os.chdir(sounds_dir)
    
    success_count = 0
    
    # Create welcome sound (higher tone)
    if create_dummy_wav('welcome.wav', duration=3, frequency=523):  # C5 note
        success_count += 1
    
    # Create goodbye sound (lower tone)
    if create_dummy_wav('goodbye.wav', duration=2, frequency=349):  # F4 note
        success_count += 1
    
    print(f"\nCreated {success_count}/2 audio files successfully!")
    
    if success_count == 2:
        print("✓ All audio files ready for testing")
        print("Note: These are dummy tones. Replace with actual voice recordings for production.")
    else:
        print("⚠ Some files failed to create. Check permissions and try again.")

if __name__ == '__main__':
    main()
