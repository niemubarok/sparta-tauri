// Barcode scanner service for USB input handling
export interface BarcodeResult {
  code: string
  timestamp: Date
  isValid: boolean
}

export interface ScannerConfig {
  minLength: number
  maxLength: number
  timeout: number // milliseconds to wait for complete barcode
  prefix?: string
  suffix?: string
}

class BarcodeScanner {
  private buffer = ''
  private lastKeystroke = 0
  private listeners: ((result: BarcodeResult) => void)[] = []
  private enabled = true
  private manuallyDisabled = false
  private config: ScannerConfig = {
    minLength: 6,
    maxLength: 20,
    timeout: 100, // 100ms timeout between keystrokes
    suffix: 'Enter'
  }

  constructor(config?: Partial<ScannerConfig>) {
    if (config) {
      this.config = { ...this.config, ...config }
    }
    this.setupKeyboardListener()
  }

  private setupKeyboardListener() {
    document.addEventListener('keydown', this.handleKeyDown.bind(this))
  }

  private handleKeyDown(event: KeyboardEvent) {
    // Check if user is typing in an input field FIRST (before any other checks)
    const target = event.target as HTMLElement
    const isInputField = target.tagName === 'INPUT' || 
                        target.tagName === 'TEXTAREA' || 
                        target.contentEditable === 'true' ||
                        target.classList.contains('q-field__native') ||
                        target.closest('.q-field') !== null ||
                        target.closest('.q-input') !== null ||
                        target.closest('.q-select') !== null ||
                        target.getAttribute('role') === 'textbox' ||
                        target.getAttribute('contenteditable') === 'true'

    // If user is typing in an input field, don't intercept AT ALL
    if (isInputField) {
      return
    }

    // Check if we're on settings page or other pages where scanner should be disabled
    const currentPath = window.location.hash || window.location.pathname
    if (currentPath.includes('/settings') || currentPath.includes('#/settings')) {
      return
    }

    // Don't process if scanner is disabled
    if (!this.enabled || this.manuallyDisabled) {
      return
    }

    const now = Date.now()
    
    // If too much time has passed, reset buffer
    if (now - this.lastKeystroke > this.config.timeout) {
      this.buffer = ''
    }
    
    this.lastKeystroke = now

    // Handle Enter key (common barcode scanner suffix)
    if (event.key === 'Enter') {
      event.preventDefault()
      this.processBarcode()
      return
    }

    // Handle Tab key (another common suffix)
    if (event.key === 'Tab') {
      event.preventDefault()
      this.processBarcode()
      return
    }

    // Add printable characters to buffer
    if (event.key.length === 1) {
      this.buffer += event.key
      
      // Prevent default to avoid input interference
      if (this.buffer.length <= this.config.maxLength) {
        event.preventDefault()
      }
    }

    // Handle backspace
    if (event.key === 'Backspace') {
      this.buffer = this.buffer.slice(0, -1)
      event.preventDefault()
    }
  }

  private processBarcode() {
    if (this.buffer.length >= this.config.minLength && 
        this.buffer.length <= this.config.maxLength) {
      
      const result: BarcodeResult = {
        code: this.buffer.trim(),
        timestamp: new Date(),
        isValid: this.validateBarcode(this.buffer.trim())
      }

      // Notify all listeners
      this.listeners.forEach(listener => listener(result))
    }

    // Reset buffer
    this.buffer = ''
  }

  private validateBarcode(code: string): boolean {
    // Basic validation - can be extended based on your barcode format
    if (code.length < this.config.minLength || code.length > this.config.maxLength) {
      return false
    }

    // Check if code contains only valid characters (alphanumeric)
    const validPattern = /^[A-Za-z0-9]+$/
    return validPattern.test(code)
  }

  // Add listener for barcode scan events
  addListener(callback: (result: BarcodeResult) => void) {
    this.listeners.push(callback)
  }

  // Remove listener
  removeListener(callback: (result: BarcodeResult) => void) {
    const index = this.listeners.indexOf(callback)
    if (index > -1) {
      this.listeners.splice(index, 1)
    }
  }

  // Update configuration
  updateConfig(config: Partial<ScannerConfig>) {
    this.config = { ...this.config, ...config }
  }

  // Get current configuration
  getConfig(): ScannerConfig {
    return { ...this.config }
  }

  // Manually trigger barcode processing (for testing)
  simulateScan(code: string) {
    const result: BarcodeResult = {
      code,
      timestamp: new Date(),
      isValid: this.validateBarcode(code)
    }
    
    this.listeners.forEach(listener => listener(result))
  }

  // Enable/disable scanner
  enable() {
    this.enabled = true
    this.manuallyDisabled = false
  }

  disable() {
    this.enabled = false
    this.manuallyDisabled = true
    this.buffer = '' // Clear buffer when disabled
  }

  // Temporarily disable scanner (for specific pages)
  temporaryDisable() {
    this.manuallyDisabled = true
    this.buffer = ''
  }

  // Re-enable scanner after temporary disable
  temporaryEnable() {
    this.manuallyDisabled = false
  }

  isEnabled(): boolean {
    return this.enabled && !this.manuallyDisabled
  }

  // Clean up event listeners
  destroy() {
    document.removeEventListener('keydown', this.handleKeyDown.bind(this))
    this.listeners = []
  }
}

export const barcodeScanner = new BarcodeScanner()
