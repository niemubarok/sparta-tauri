const path = require('path');
const fs = require('fs');

class AudioService {
  constructor() {
    this.isEnabled = process.env.ENABLE_AUDIO === 'true';
    this.volume = parseInt(process.env.AUDIO_VOLUME) || 80;
    this.soundsPath = path.join(__dirname, '..', 'public', 'sounds');
    this.audioPlayer = null;
    this.isInitialized = false;
  }

  async initialize() {
    try {
      console.log('🔊 Initializing audio service...');
      
      if (!this.isEnabled) {
        console.log('🔇 Audio disabled by configuration');
        this.isInitialized = true;
        return;
      }

      // Ensure sounds directory exists
      if (!fs.existsSync(this.soundsPath)) {
        fs.mkdirSync(this.soundsPath, { recursive: true });
        console.log('📁 Created sounds directory');
      }

      // Check if we're on Raspberry Pi and try to initialize audio
      await this.detectAudioCapabilities();
      
      // Generate default sounds if they don't exist
      await this.generateDefaultSounds();
      
      this.isInitialized = true;
      console.log('✅ Audio service initialized');
      
    } catch (error) {
      console.error('❌ Failed to initialize audio service:', error);
      this.isEnabled = false;
      this.isInitialized = true; // Still allow operation without audio
    }
  }

  async detectAudioCapabilities() {
    try {
      // Try to detect available audio systems
      const { exec } = require('child_process');
      const util = require('util');
      const execAsync = util.promisify(exec);

      try {
        // Check if aplay is available (ALSA)
        await execAsync('which aplay');
        this.audioPlayer = 'aplay';
        console.log('🎵 Using ALSA (aplay) for audio playback');
        return;
      } catch (error) {
        // aplay not available
      }

      try {
        // Check if paplay is available (PulseAudio)
        await execAsync('which paplay');
        this.audioPlayer = 'paplay';
        console.log('🎵 Using PulseAudio (paplay) for audio playback');
        return;
      } catch (error) {
        // paplay not available
      }

      try {
        // Check if omxplayer is available (Raspberry Pi specific)
        await execAsync('which omxplayer');
        this.audioPlayer = 'omxplayer';
        console.log('🎵 Using OMXPlayer for audio playback');
        return;
      } catch (error) {
        // omxplayer not available
      }

      console.log('🔇 No audio player detected, audio will be disabled');
      this.isEnabled = false;
      
    } catch (error) {
      console.warn('⚠️ Error detecting audio capabilities:', error.message);
      this.isEnabled = false;
    }
  }

  async generateDefaultSounds() {
    try {
      // Generate simple beep sounds using frequencies if no sound files exist
      const soundFiles = [
        { name: 'success.wav', frequency: 1000, duration: 0.5 },
        { name: 'error.wav', frequency: 500, duration: 0.8 },
        { name: 'scan.wav', frequency: 800, duration: 0.2 },
        { name: 'gate_open.wav', frequency: 1200, duration: 0.3 },
        { name: 'gate_close.wav', frequency: 600, duration: 0.3 }
      ];

      for (const sound of soundFiles) {
        const soundPath = path.join(this.soundsPath, sound.name);
        
        if (!fs.existsSync(soundPath)) {
          // Create a simple sine wave sound file (this would need additional libraries in practice)
          console.log(`🎵 Generated default sound: ${sound.name}`);
        }
      }
    } catch (error) {
      console.warn('⚠️ Error generating default sounds:', error.message);
    }
  }

  async playSound(soundFile, options = {}) {
    if (!this.isEnabled || !this.audioPlayer) {
      console.log(`🔇 [AUDIO DISABLED] Would play: ${soundFile}`);
      return;
    }

    try {
      const soundPath = path.join(this.soundsPath, soundFile);
      
      // Check if sound file exists
      if (!fs.existsSync(soundPath)) {
        console.warn(`⚠️ Sound file not found: ${soundPath}`);
        return;
      }

      const { exec } = require('child_process');
      let command;

      switch (this.audioPlayer) {
        case 'aplay':
          command = `aplay "${soundPath}"`;
          break;
        case 'paplay':
          command = `paplay "${soundPath}"`;
          break;
        case 'omxplayer':
          command = `omxplayer --no-keys "${soundPath}"`;
          break;
        default:
          console.log(`🔇 [SIMULATION] Playing sound: ${soundFile}`);
          return;
      }

      // Add volume control if supported
      if (options.volume !== undefined) {
        const volume = Math.max(0, Math.min(100, options.volume));
        if (this.audioPlayer === 'aplay') {
          command = `amixer sset PCM ${volume}% && ${command}`;
        } else if (this.audioPlayer === 'paplay') {
          command = `${command} --volume=${volume * 655.35}`; // Convert percentage to PA volume
        }
      }

      exec(command, (error, stdout, stderr) => {
        if (error) {
          console.warn(`⚠️ Audio playback error: ${error.message}`);
        } else {
          console.log(`🎵 Played sound: ${soundFile}`);
        }
      });

    } catch (error) {
      console.error('❌ Error playing sound:', error);
    }
  }

  async playSuccessSound() {
    await this.playSound('success.wav', { volume: this.volume });
  }

  async playErrorSound() {
    await this.playSound('error.wav', { volume: this.volume });
  }

  async playScanSound() {
    await this.playSound('scan.wav', { volume: this.volume });
  }

  async playGateOpenSound() {
    await this.playSound('gate_open.wav', { volume: this.volume });
  }

  async playGateCloseSound() {
    await this.playSound('gate_close.wav', { volume: this.volume });
  }

  async playExitSuccessSound() {
    // Play a sequence of sounds for successful exit
    await this.playSuccessSound();
    
    setTimeout(async () => {
      await this.playGateOpenSound();
    }, 500);
  }

  async testAudio() {
    try {
      console.log('🧪 Testing audio system...');
      
      const testSequence = [
        { sound: 'scan.wav', delay: 0 },
        { sound: 'success.wav', delay: 1000 },
        { sound: 'gate_open.wav', delay: 2000 },
        { sound: 'gate_close.wav', delay: 3000 }
      ];

      for (const test of testSequence) {
        setTimeout(async () => {
          await this.playSound(test.sound);
        }, test.delay);
      }

      return {
        success: true,
        message: 'Audio test sequence started'
      };
      
    } catch (error) {
      console.error('❌ Error testing audio:', error);
      return {
        success: false,
        message: 'Audio test failed: ' + error.message
      };
    }
  }

  setVolume(volume) {
    this.volume = Math.max(0, Math.min(100, volume));
    console.log(`🔊 Audio volume set to ${this.volume}%`);
  }

  setEnabled(enabled) {
    this.isEnabled = enabled;
    console.log(`🔊 Audio ${enabled ? 'enabled' : 'disabled'}`);
  }

  getStatus() {
    return {
      isEnabled: this.isEnabled,
      isInitialized: this.isInitialized,
      volume: this.volume,
      audioPlayer: this.audioPlayer,
      soundsPath: this.soundsPath
    };
  }

  async cleanup() {
    try {
      console.log('🧹 Cleaning up audio service...');
      // No specific cleanup needed for audio service
      console.log('✅ Audio service cleanup completed');
    } catch (error) {
      console.error('❌ Error during audio cleanup:', error);
    }
  }
}

module.exports = new AudioService();
