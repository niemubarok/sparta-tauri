import { invoke } from '@tauri-apps/api/core'
import { audioService } from './audio-service'

export interface SerialConfig {
  port: string
  baud_rate: number
}

export interface GateResponse {
  success: boolean
  message: string
}

export enum GateStatus {
  CLOSED = 'CLOSED',
  OPENING = 'OPENING',
  OPEN = 'OPEN',
  CLOSING = 'CLOSING',
  ERROR = 'ERROR'
}

class GateService {
  private currentStatus: GateStatus = GateStatus.CLOSED
  private serialConfig: SerialConfig | null = null
  private autoCloseTimer: number | null = null
  private statusListeners: ((status: GateStatus) => void)[] = []

  constructor() {
    this.initializeFromSettings()
  }

  private async initializeFromSettings() {
    try {
      // This will be implemented to get settings from database
      const { databaseService } = await import('./database')
      const settings = await databaseService.getSettings()
      
      if (settings) {
        this.serialConfig = {
          port: settings.serial_port,
          baud_rate: settings.baud_rate
        }
      }
    } catch (error) {
      console.error('Failed to initialize gate service from settings:', error)
    }
  }

  // Get available serial ports
  async getAvailablePorts(): Promise<string[]> {
    try {
      return await invoke('list_serial_ports')
    } catch (error) {
      console.error('Failed to get serial ports:', error)
      return []
    }
  }

  // Configure serial connection
  async configureSerial(config: SerialConfig): Promise<boolean> {
    try {
      const response: GateResponse = await invoke('open_serial_port', { config })
      
      if (response.success) {
        this.serialConfig = config
        console.log('Serial port configured:', response.message)
        return true
      } else {
        console.error('Failed to configure serial port:', response.message)
        return false
      }
    } catch (error) {
      console.error('Error configuring serial port:', error)
      return false
    }
  }

  // Open the gate
  async openGate(autoCloseTimeout?: number): Promise<boolean> {
    if (!this.serialConfig) {
      console.error('Serial port not configured')
      return false
    }

    try {
      this.setStatus(GateStatus.OPENING)
      
      const response: GateResponse = await invoke('open_gate', { 
        portName: this.serialConfig.port 
      })

      if (response.success) {
        this.setStatus(GateStatus.OPEN)
        console.log('Gate opened:', response.message)
        
        // Play gate open sound
        try {
          await audioService.playGateOpenSound()
        } catch (audioError) {
          console.warn('Failed to play gate open sound:', audioError)
        }
        
        // Set auto-close timer if specified
        if (autoCloseTimeout && autoCloseTimeout > 0) {
          this.setAutoCloseTimer(autoCloseTimeout)
        }
        
        return true
      } else {
        this.setStatus(GateStatus.ERROR)
        console.error('Failed to open gate:', response.message)
        return false
      }
    } catch (error) {
      this.setStatus(GateStatus.ERROR)
      console.error('Error opening gate:', error)
      return false
    }
  }

  // Close the gate
  async closeGate(): Promise<boolean> {
    if (!this.serialConfig) {
      console.error('Serial port not configured')
      return false
    }

    try {
      this.setStatus(GateStatus.CLOSING)
      this.clearAutoCloseTimer()
      
      const response: GateResponse = await invoke('close_gate', { 
        portName: this.serialConfig.port 
      })

      if (response.success) {
        this.setStatus(GateStatus.CLOSED)
        console.log('Gate closed:', response.message)
        
        // Play gate close sound
        try {
          await audioService.playGateCloseSound()
        } catch (audioError) {
          console.warn('Failed to play gate close sound:', audioError)
        }
        
        return true
      } else {
        this.setStatus(GateStatus.ERROR)
        console.error('Failed to close gate:', response.message)
        return false
      }
    } catch (error) {
      this.setStatus(GateStatus.ERROR)
      console.error('Error closing gate:', error)
      return false
    }
  }

  // Set auto-close timer
  private setAutoCloseTimer(seconds: number) {
    this.clearAutoCloseTimer()
    
    this.autoCloseTimer = window.setTimeout(async () => {
      console.log(`Auto-closing gate after ${seconds} seconds`)
      await this.closeGate()
    }, seconds * 1000)
  }

  // Clear auto-close timer
  private clearAutoCloseTimer() {
    if (this.autoCloseTimer) {
      clearTimeout(this.autoCloseTimer)
      this.autoCloseTimer = null
    }
  }

  // Set gate status and notify listeners
  private setStatus(status: GateStatus) {
    this.currentStatus = status
    this.statusListeners.forEach(listener => listener(status))
  }

  // Get current gate status
  getStatus(): GateStatus {
    return this.currentStatus
  }

  // Add status listener
  addStatusListener(callback: (status: GateStatus) => void) {
    this.statusListeners.push(callback)
  }

  // Remove status listener
  removeStatusListener(callback: (status: GateStatus) => void) {
    const index = this.statusListeners.indexOf(callback)
    if (index > -1) {
      this.statusListeners.splice(index, 1)
    }
  }

  // Get current serial configuration
  getSerialConfig(): SerialConfig | null {
    return this.serialConfig
  }

  // Close serial connection
  async closeSerial(): Promise<boolean> {
    if (!this.serialConfig) {
      return true
    }

    try {
      const response: GateResponse = await invoke('close_serial_port', { 
        portName: this.serialConfig.port 
      })

      if (response.success) {
        console.log('Serial port closed:', response.message)
        return true
      } else {
        console.error('Failed to close serial port:', response.message)
        return false
      }
    } catch (error) {
      console.error('Error closing serial port:', error)
      return false
    }
  }

  // Test gate operation (open then close after delay)
  async testGate(openTime: number = 3): Promise<boolean> {
    console.log('Testing gate operation...')
    
    const opened = await this.openGate()
    if (!opened) {
      return false
    }

    // Wait for specified time then close
    setTimeout(async () => {
      await this.closeGate()
    }, openTime * 1000)

    return true
  }

  // Cleanup
  destroy() {
    this.clearAutoCloseTimer()
    this.statusListeners = []
  }
}

export const gateService = new GateService()
