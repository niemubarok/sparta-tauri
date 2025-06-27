// Audio service for gate sounds and notifications
export interface AudioConfig {
  gate_open_sound: string
  gate_close_sound?: string
  error_sound?: string
  volume: number // 0.0 to 1.0
  enabled: boolean
}

export interface SoundEvent {
  type: 'gate_open' | 'gate_close' | 'error' | 'success' | 'scan'
  file: string
  volume?: number
}

class AudioService {
  private audioContext: AudioContext | null = null
  private audioBuffers: Map<string, AudioBuffer> = new Map()
  private config: AudioConfig = {
    gate_open_sound: '/sounds/gate-open.mp3',
    gate_close_sound: '/sounds/gate-close.mp3',
    error_sound: '/sounds/error.mp3',
    volume: 0.7,
    enabled: true
  }
  private preloadedSounds: Map<string, HTMLAudioElement> = new Map()

  constructor() {
    this.initializeAudioContext()
    this.preloadSounds()
  }

  private initializeAudioContext() {
    try {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    } catch (error) {
      console.warn('AudioContext not supported:', error)
    }
  }

  private async preloadSounds() {
    const defaultSounds = [
      { key: 'gate_open', url: '/sounds/gate-open.mp3' },
      { key: 'gate_close', url: '/sounds/gate-close.mp3' },
      { key: 'error', url: '/sounds/error.mp3' },
      { key: 'success', url: '/sounds/success.mp3' },
      { key: 'scan', url: '/sounds/scan.mp3' }
    ]

    for (const sound of defaultSounds) {
      try {
        const audio = new Audio(sound.url)
        audio.preload = 'auto'
        audio.volume = this.config.volume
        
        // Handle file not found - create fallback sound
        audio.onerror = () => {
          console.warn(`Sound file ${sound.url} not found, using fallback`)
          this.createFallbackSound(sound.key)
        }
        
        this.preloadedSounds.set(sound.key, audio)
      } catch (error) {
        console.warn(`Failed to preload sound ${sound.key}:`, error)
        this.createFallbackSound(sound.key)
      }
    }
  }

  // Create fallback sounds using Web Audio API
  private createFallbackSound(key: string) {
    if (!this.audioContext) return

    try {
      let frequency = 800
      let duration = 0.3
      
      switch (key) {
        case 'gate_open':
          frequency = 800
          duration = 0.5
          break
        case 'gate_close':
          frequency = 600
          duration = 0.3
          break
        case 'scan':
          frequency = 1000
          duration = 0.1
          break
        case 'success':
          frequency = 900
          duration = 0.4
          break
        case 'error':
          frequency = 400
          duration = 0.6
          break
      }

      // Create a simple beep sound
      const buffer = this.audioContext.createBuffer(1, this.audioContext.sampleRate * duration, this.audioContext.sampleRate)
      const channelData = buffer.getChannelData(0)
      
      for (let i = 0; i < buffer.length; i++) {
        const t = i / this.audioContext.sampleRate
        channelData[i] = Math.sin(2 * Math.PI * frequency * t) * 0.3 * Math.exp(-t * 3)
      }

      // Create an audio element from the buffer
      const audio = new Audio()
      audio.volume = this.config.volume
      
      // Set up playback function
      audio.play = async () => {
        if (this.audioContext) {
          const source = this.audioContext.createBufferSource()
          source.buffer = buffer
          source.connect(this.audioContext.destination)
          source.start()
        }
        return Promise.resolve()
      }
      
      this.preloadedSounds.set(key, audio)
    } catch (error) {
      console.error(`Failed to create fallback sound for ${key}:`, error)
    }
  }

  // Play sound by type
  async playSound(type: SoundEvent['type'], options?: { volume?: number }): Promise<boolean> {
    if (!this.config.enabled) {
      return false
    }

    try {
      let soundKey = type
      let audioFile: HTMLAudioElement | undefined

      // Map sound types to files
      switch (type) {
        case 'gate_open':
          audioFile = this.preloadedSounds.get('gate_open')
          break
        case 'gate_close':
          audioFile = this.preloadedSounds.get('gate_close')
          break
        case 'error':
          audioFile = this.preloadedSounds.get('error')
          break
        case 'success':
          audioFile = this.preloadedSounds.get('success')
          break
        case 'scan':
          audioFile = this.preloadedSounds.get('scan')
          break
        default:
          console.warn('Unknown sound type:', type)
          return false
      }

      if (!audioFile) {
        console.warn(`Sound file not found for type: ${type}`)
        return false
      }

      // Set volume
      audioFile.volume = options?.volume ?? this.config.volume

      // Reset audio to beginning and play
      audioFile.currentTime = 0
      await audioFile.play()
      
      console.log(`Played sound: ${type}`)
      return true
    } catch (error) {
      console.error(`Failed to play sound ${type}:`, error)
      return false
    }
  }

  // Play custom sound file
  async playCustomSound(url: string, volume?: number): Promise<boolean> {
    if (!this.config.enabled) {
      return false
    }

    try {
      const audio = new Audio(url)
      audio.volume = volume ?? this.config.volume
      await audio.play()
      return true
    } catch (error) {
      console.error('Failed to play custom sound:', error)
      return false
    }
  }

  // Text-to-speech for announcements
  async speak(text: string, options?: { lang?: string; rate?: number; pitch?: number }): Promise<boolean> {
    if (!this.config.enabled || !('speechSynthesis' in window)) {
      return false
    }

    try {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = options?.lang || 'id-ID' // Indonesian
      utterance.rate = options?.rate || 1.0
      utterance.pitch = options?.pitch || 1.0
      utterance.volume = this.config.volume

      speechSynthesis.speak(utterance)
      return true
    } catch (error) {
      console.error('Text-to-speech failed:', error)
      return false
    }
  }

  // Configuration methods
  updateConfig(newConfig: Partial<AudioConfig>) {
    this.config = { ...this.config, ...newConfig }
    
    // Update volume for all preloaded sounds
    this.preloadedSounds.forEach(audio => {
      audio.volume = this.config.volume
    })
  }

  getConfig(): AudioConfig {
    return { ...this.config }
  }

  // Enable/disable audio
  setEnabled(enabled: boolean) {
    this.config.enabled = enabled
  }

  isEnabled(): boolean {
    return this.config.enabled
  }

  // Volume control
  setVolume(volume: number) {
    this.config.volume = Math.max(0, Math.min(1, volume))
    this.preloadedSounds.forEach(audio => {
      audio.volume = this.config.volume
    })
  }

  getVolume(): number {
    return this.config.volume
  }

  // Test all sounds
  async testAllSounds(): Promise<void> {
    const sounds: SoundEvent['type'][] = ['scan', 'success', 'gate_open', 'gate_close', 'error']
    
    for (let i = 0; i < sounds.length; i++) {
      setTimeout(() => {
        this.playSound(sounds[i])
      }, i * 1000) // Play each sound 1 second apart
    }
  }

  // Gate-specific sound methods
  async playGateOpenSound(): Promise<boolean> {
    const success = await this.playSound('gate_open')
    
    // Optional: Add voice announcement
    setTimeout(() => {
      this.speak('Pintu terbuka, silakan lewat')
    }, 500)
    
    return success
  }

  async playGateCloseSound(): Promise<boolean> {
    return await this.playSound('gate_close')
  }

  async playExitSuccessSound(): Promise<boolean> {
    const success = await this.playSound('success')
    
    // Optional: Add voice announcement
    setTimeout(() => {
      this.speak('Terima kasih, selamat jalan')
    }, 300)
    
    return success
  }

  async playErrorSound(): Promise<boolean> {
    const success = await this.playSound('error')
    
    // Optional: Add voice announcement
    setTimeout(() => {
      this.speak('Terjadi kesalahan, silakan coba lagi')
    }, 300)
    
    return success
  }

  async playScanSound(): Promise<boolean> {
    return await this.playSound('scan')
  }

  // Cleanup
  destroy() {
    this.preloadedSounds.forEach(audio => {
      audio.pause()
      audio.src = ''
    })
    this.preloadedSounds.clear()
    
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close()
    }
  }
}

export const audioService = new AudioService()
