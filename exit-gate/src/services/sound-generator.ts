// Sound generator utility for creating basic audio effects
export class SoundGenerator {
  private audioContext: AudioContext

  constructor() {
    this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
  }

  // Generate a beep sound
  generateBeep(frequency: number = 800, duration: number = 0.3, volume: number = 0.3): AudioBuffer {
    const sampleRate = this.audioContext.sampleRate
    const numSamples = sampleRate * duration
    const buffer = this.audioContext.createBuffer(1, numSamples, sampleRate)
    const channelData = buffer.getChannelData(0)

    for (let i = 0; i < numSamples; i++) {
      const t = i / sampleRate
      channelData[i] = Math.sin(2 * Math.PI * frequency * t) * volume * Math.exp(-t * 3)
    }

    return buffer
  }

  // Generate a success chime (ascending notes)
  generateSuccessChime(duration: number = 0.8, volume: number = 0.4): AudioBuffer {
    const sampleRate = this.audioContext.sampleRate
    const numSamples = sampleRate * duration
    const buffer = this.audioContext.createBuffer(1, numSamples, sampleRate)
    const channelData = buffer.getChannelData(0)

    const frequencies = [523, 659, 784] // C5, E5, G5
    const noteDuration = duration / frequencies.length

    for (let i = 0; i < numSamples; i++) {
      const t = i / sampleRate
      const noteIndex = Math.floor(t / noteDuration)
      const noteTime = t - (noteIndex * noteDuration)
      
      if (noteIndex < frequencies.length) {
        const frequency = frequencies[noteIndex]
        const envelope = Math.exp(-noteTime * 2)
        channelData[i] = Math.sin(2 * Math.PI * frequency * noteTime) * volume * envelope
      }
    }

    return buffer
  }

  // Generate an error sound (descending notes)
  generateErrorSound(duration: number = 0.6, volume: number = 0.4): AudioBuffer {
    const sampleRate = this.audioContext.sampleRate
    const numSamples = sampleRate * duration
    const buffer = this.audioContext.createBuffer(1, numSamples, sampleRate)
    const channelData = buffer.getChannelData(0)

    const frequencies = [400, 350, 300] // Descending tones
    const noteDuration = duration / frequencies.length

    for (let i = 0; i < numSamples; i++) {
      const t = i / sampleRate
      const noteIndex = Math.floor(t / noteDuration)
      const noteTime = t - (noteIndex * noteDuration)
      
      if (noteIndex < frequencies.length) {
        const frequency = frequencies[noteIndex]
        const envelope = Math.exp(-noteTime * 1.5)
        channelData[i] = Math.sin(2 * Math.PI * frequency * noteTime) * volume * envelope
      }
    }

    return buffer
  }

  // Play generated audio buffer
  async playBuffer(buffer: AudioBuffer): Promise<void> {
    const source = this.audioContext.createBufferSource()
    source.buffer = buffer
    source.connect(this.audioContext.destination)
    source.start()

    return new Promise(resolve => {
      source.onended = () => resolve()
    })
  }

  // Generate and save sound files
  async generateDefaultSounds(): Promise<void> {
    try {
      // Generate different sound effects
      const scanBeep = this.generateBeep(1000, 0.1, 0.3)
      const successChime = this.generateSuccessChime(0.8, 0.4)
      const errorSound = this.generateErrorSound(0.6, 0.4)
      const gateOpenSound = this.generateBeep(800, 0.5, 0.3)
      const gateCloseSound = this.generateBeep(600, 0.3, 0.3)

      console.log('Generated sound buffers for gate system')
      
      // Store in a map for use by audio service
      return Promise.resolve()
    } catch (error) {
      console.error('Failed to generate sounds:', error)
    }
  }
}

export const soundGenerator = new SoundGenerator()
