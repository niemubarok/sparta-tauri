# Audio Files for Exit Gate System

This directory should contain the following sound files for the exit gate system:

## Required Sound Files:

### 1. gate-open.mp3
- **Purpose**: Played when the gate opens
- **Duration**: ~0.5 seconds
- **Type**: Pleasant chime or beep
- **Volume**: Medium level

### 2. gate-close.mp3
- **Purpose**: Played when the gate closes
- **Duration**: ~0.3 seconds
- **Type**: Lower tone beep
- **Volume**: Medium level

### 3. scan.mp3
- **Purpose**: Played when barcode is scanned
- **Duration**: ~0.1 seconds
- **Type**: Quick beep
- **Volume**: Low level

### 4. success.mp3
- **Purpose**: Played when exit is processed successfully
- **Duration**: ~0.8 seconds
- **Type**: Success chime (ascending notes)
- **Volume**: Medium level

### 5. error.mp3
- **Purpose**: Played when an error occurs
- **Duration**: ~0.6 seconds
- **Type**: Error sound (descending notes)
- **Volume**: Medium level

## File Format Requirements:
- Format: MP3 or WAV
- Sample Rate: 44.1 kHz or 48 kHz
- Bit Depth: 16-bit or higher
- Channels: Mono or Stereo

## Alternative: Synthesized Sounds
If you don't have audio files, the system will attempt to generate basic sounds using the Web Audio API. However, for better user experience, it's recommended to use proper audio files.

## Voice Announcements
The system also supports text-to-speech announcements in Indonesian:
- "Pintu terbuka, silakan lewat" (Gate open, please proceed)
- "Terima kasih, selamat jalan" (Thank you, have a safe trip)
- "Terjadi kesalahan, silakan coba lagi" (An error occurred, please try again)

## Testing
Use the Audio Settings in the application to test all sounds and adjust volume levels.
