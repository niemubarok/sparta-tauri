# Audio Files Directory

This directory should contain the following audio files:

## Required Files:
- `welcome.wav` - Welcome message: "Selamat Datang silahkan tempelkan kartu atau tekan tombol"
- `goodbye.wav` - Thank you message: "Terima Kasih silahkan masuk"

## Creating Audio Files:

### Option 1: Text-to-Speech Online
1. Visit: https://ttstool.com/ or https://www.naturalreaders.com/
2. Enter Indonesian text
3. Download as WAV file

### Option 2: Generate Dummy Files (for testing)
Run the Python script below to create dummy audio files:

```python
import wave
import numpy as np

def create_dummy_wav(filename, duration=2, sample_rate=44100):
    # Generate a simple tone
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    frequency = 440  # A4 note
    audio = np.sin(2 * np.pi * frequency * t) * 0.3
    
    # Convert to 16-bit integers
    audio = (audio * 32767).astype(np.int16)
    
    # Write to WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.tobytes())

# Create dummy files
create_dummy_wav('welcome.wav')
create_dummy_wav('goodbye.wav')
print("Dummy audio files created!")
```

## File Specifications:
- Format: WAV
- Sample Rate: 44.1 kHz recommended
- Bit Depth: 16-bit
- Channels: Mono preferred
- Duration: 2-5 seconds recommended
