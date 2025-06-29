import { invoke } from '@tauri-apps/api/core'
import { audioService } from './audio-service'

export interface SerialConfig {
  port: string
  baud_rate: number
}

export interface GpioConfig {
  pin: number
  active_high: boolean
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

export enum GateControlMode {
  SERIAL = 'SERIAL',
  GPIO = 'GPIO'
}

class GateService {
  private currentStatus: GateStatus = GateStatus.CLOSED
  private serialConfig: SerialConfig | null = null
  private gpioConfig: GpioConfig | null = null
  private controlMode: GateControlMode = GateControlMode.SERIAL
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
        
        // Check for GPIO configuration
        if (settings.gpio_pin !== undefined) {
          this.gpioConfig = {
            pin: settings.gpio_pin,
            active_high: settings.gpio_active_high ?? true
          }
          
          // Use GPIO if available and raspberry pi detected
          if (await this.isRaspberryPi()) {
            this.controlMode = GateControlMode.GPIO
          }
        }
      }
    } catch (error) {
      console.error('Failed to initialize gate service from settings:', error)
    }
  }

  // Check if running on Raspberry Pi
  async isRaspberryPi(): Promise<boolean> {
    try {
      const result = await invoke('check_gpio_availability') as GateResponse
      return result.success
    } catch (error) {
      console.log('GPIO not available, falling back to serial mode')
      return false
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

  // Configure GPIO
  async configureGpio(config: GpioConfig): Promise<boolean> {
    try {
      const result = await invoke('check_gpio_availability') as GateResponse
      if (result.success) {
        this.gpioConfig = config
        this.controlMode = GateControlMode.GPIO
        console.log('GPIO configured successfully:', config)
        return true
      } else {
        console.error('GPIO not available on this system')
        return false
      }
    } catch (error) {
      console.error('Failed to configure GPIO:', error)
      return false
    }
  }

  // Test GPIO pin
  async testGpio(): Promise<boolean> {
    if (!this.gpioConfig) {
      console.error('GPIO not configured')
      return false
    }

    try {
      const result = await invoke('gpio_test_pin', { config: this.gpioConfig }) as GateResponse
      console.log('GPIO test result:', result)
      return result.success
    } catch (error) {
      console.error('GPIO test failed:', error)
      return false
    }
  }

  // Open the gate
  async openGate(autoCloseTimeout?: number): Promise<boolean> {
    try {
      this.setStatus(GateStatus.OPENING)
      this.clearAutoCloseTimer()
      
      let success = false
      
      if (this.controlMode === GateControlMode.GPIO && this.gpioConfig) {
        // Use GPIO control
        const response: GateResponse = await invoke('gpio_open_gate', { 
          config: this.gpioConfig 
        })
        success = response.success
        if (success) {
          console.log('Gate opened via GPIO:', response.message)
        } else {
          console.error('Failed to open gate via GPIO:', response.message)
        }
      } else if (this.controlMode === GateControlMode.SERIAL && this.serialConfig) {
        // Use serial control
        const response: GateResponse = await invoke('open_gate', { 
          portName: this.serialConfig.port 
        })
        success = response.success
        if (success) {
          console.log('Gate opened via serial:', response.message)
        } else {
          console.error('Failed to open gate via serial:', response.message)
        }
      } else {
        console.error('No valid control method configured')
        this.setStatus(GateStatus.ERROR)
        return false
      }

      if (success) {
        this.setStatus(GateStatus.OPEN)
        
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
    try {
      this.setStatus(GateStatus.CLOSING)
      this.clearAutoCloseTimer()
      
      let success = false
      
      if (this.controlMode === GateControlMode.GPIO && this.gpioConfig) {
        // Use GPIO control
        const response: GateResponse = await invoke('gpio_close_gate', { 
          config: this.gpioConfig 
        })
        success = response.success
        if (success) {
          console.log('Gate closed via GPIO:', response.message)
        } else {
          console.error('Failed to close gate via GPIO:', response.message)
        }
      } else if (this.controlMode === GateControlMode.SERIAL && this.serialConfig) {
        // Use serial control
        const response: GateResponse = await invoke('close_gate', { 
          portName: this.serialConfig.port 
        })
        success = response.success
        if (success) {
          console.log('Gate closed via serial:', response.message)
        } else {
          console.error('Failed to close gate via serial:', response.message)
        }
      } else {
        console.error('No valid control method configured')
        this.setStatus(GateStatus.ERROR)
        return false
      }

      if (success) {
        this.setStatus(GateStatus.CLOSED)
        
        // Play gate close sound
        try {
          await audioService.playGateCloseSound()
        } catch (audioError) {
          console.warn('Failed to play gate close sound:', audioError)
        }
        
        return true
      } else {
        this.setStatus(GateStatus.ERROR)
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

  // Get current GPIO configuration
  getGpioConfig(): GpioConfig | null {
    return this.gpioConfig
  }

  // Get current control mode
  getControlMode(): GateControlMode {
    return this.controlMode
  }

  // Set control mode manually
  setControlMode(mode: GateControlMode): boolean {
    if (mode === GateControlMode.GPIO && !this.gpioConfig) {
      console.error('Cannot set GPIO mode: GPIO not configured')
      return false
    }
    if (mode === GateControlMode.SERIAL && !this.serialConfig) {
      console.error('Cannot set Serial mode: Serial not configured')
      return false
    }
    
    this.controlMode = mode
    console.log(`Control mode set to: ${mode}`)
    return true
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
