const EventEmitter = require('events');

class GPIOService extends EventEmitter {
  constructor() {
    super();
    this.isRaspberryPi = false;
    this.gpio = null;
    
    // Exit Gate GPIO Pin Configuration
    this.pins = {
      // INPUT pins (Active Low - sensors)
      LOOP1: 18,      // Loop sensor 1
      LOOP2: 27,      // Loop sensor 2  
      STRUK: 4,       // Print receipt button
      EMERGENCY: 17,  // Emergency button
      
      // OUTPUT pins (Active High - triggers)
      TRIGGER1: 24,   // Main gate trigger
      TRIGGER2: 23,   // Secondary trigger
      LED_LIVE: 25    // Status LED
    };
    
    // Legacy pins for backward compatibility
    this.gatePin = this.pins.TRIGGER1;
    this.ledPin = this.pins.LED_LIVE;
    
    this.activeHigh = process.env.GPIO_ACTIVE_HIGH === 'true';
    this.pulseDuration = parseInt(process.env.GATE_PULSE_DURATION) || 500;
    this.ledHeartbeatInterval = null;
    this.isInitialized = false;
    this.inputValues = {};
  }

  async initialize() {
    try {
      console.log('🔧 Initializing GPIO service...');
      
      // Detect if running on Raspberry Pi
      this.isRaspberryPi = await this.detectRaspberryPi();
      
      if (this.isRaspberryPi) {
        console.log('📟 Raspberry Pi detected, initializing real GPIO...');
        
        try {
          // Try to use raspi-gpio first (more reliable)
          this.gpio = require('raspi-gpio');
          await this.initializeRaspiGpio();
        } catch (raspiError) {
          console.log('⚠️ raspi-gpio not available, trying rpi-gpio...');
          
          try {
            // Fallback to rpi-gpio
            this.gpio = require('rpi-gpio');
            await this.initializeRpiGpio();
          } catch (rpiError) {
            console.log('⚠️ rpi-gpio not available, trying gpio library...');
            
            try {
              // Fallback to gpio library
              this.gpio = require('gpio');
              await this.initializeGpioLib();
            } catch (gpioError) {
              console.warn('⚠️ No GPIO library available, using simulation mode');
              this.isRaspberryPi = false;
            }
          }
        }
      }
      
      if (!this.isRaspberryPi) {
        console.log('💻 Running in simulation mode (not on Raspberry Pi)');
      }
      
      this.isInitialized = true;
      
      // Start input monitoring
      this.startInputMonitoring();
      
      console.log(`✅ GPIO service initialized (Pin ${this.gatePin}: Gate, Pin ${this.ledPin}: LED)`);
      console.log(`📍 GPIO Pin Map: LOOP1=${this.pins.LOOP1}, LOOP2=${this.pins.LOOP2}, STRUK=${this.pins.STRUK}, EMERGENCY=${this.pins.EMERGENCY}`);
      console.log(`📍 OUTPUT Pins: TRIGGER1=${this.pins.TRIGGER1}, TRIGGER2=${this.pins.TRIGGER2}, LED_LIVE=${this.pins.LED_LIVE}`);
      
    } catch (error) {
      console.error('❌ Failed to initialize GPIO service:', error);
      this.isRaspberryPi = false;
      this.isInitialized = true; // Still allow operation in simulation mode
    }
  }

  async detectRaspberryPi() {
    try {
      const fs = require('fs');
      const cpuinfo = fs.readFileSync('/proc/cpuinfo', 'utf8');
      return cpuinfo.includes('Raspberry Pi') || cpuinfo.includes('BCM');
    } catch (error) {
      return false;
    }
  }

  async initializeRaspiGpio() {
    const { DigitalOutput } = require('raspi-gpio');
    
    this.gateOutput = new DigitalOutput(this.gatePin);
    this.ledOutput = new DigitalOutput(this.ledPin);
    
    // Set initial states
    this.gateOutput.write(this.activeHigh ? 0 : 1); // Gate closed
    this.ledOutput.write(0); // LED off
    
    console.log('✅ raspi-gpio initialized');
  }

  async initializeRpiGpio() {
    return new Promise((resolve, reject) => {
      this.gpio.setup(this.gatePin, this.gpio.DIR_OUT, (err) => {
        if (err) {
          reject(err);
          return;
        }
        
        this.gpio.setup(this.ledPin, this.gpio.DIR_OUT, (err) => {
          if (err) {
            reject(err);
            return;
          }
          
          // Set initial states
          this.gpio.write(this.gatePin, this.activeHigh ? false : true); // Gate closed
          this.gpio.write(this.ledPin, false); // LED off
          
          console.log('✅ rpi-gpio initialized');
          resolve();
        });
      });
    });
  }

  async initializeGpioLib() {
    this.gateGpio = this.gpio.export(this.gatePin, {
      direction: 'out',
      ready: () => {
        this.gateGpio.set(this.activeHigh ? 0 : 1); // Gate closed
      }
    });

    this.ledGpio = this.gpio.export(this.ledPin, {
      direction: 'out',
      ready: () => {
        this.ledGpio.set(0); // LED off
      }
    });

    console.log('✅ gpio library initialized');
  }

  async openGate(autoCloseTime = null) {
    try {
      console.log('🚪 Opening gate...');
      
      if (this.isRaspberryPi) {
        await this.setGatePin(this.activeHigh ? 1 : 0);
        
        // Pulse duration for gate trigger
        setTimeout(async () => {
          await this.setGatePin(this.activeHigh ? 0 : 1);
        }, this.pulseDuration);
      }
      
      this.emit('gateStatusChanged', 'OPENING');
      
      // Simulate gate opening time
      setTimeout(() => {
        this.emit('gateStatusChanged', 'OPEN');
        
        // Auto close if specified
        if (autoCloseTime && autoCloseTime > 0) {
          setTimeout(async () => {
            await this.closeGate();
          }, autoCloseTime * 1000);
        }
      }, 1000);
      
      return {
        success: true,
        message: 'Gate opened successfully',
        autoCloseTime: autoCloseTime
      };
      
    } catch (error) {
      console.error('❌ Error opening gate:', error);
      this.emit('gateStatusChanged', 'ERROR');
      return {
        success: false,
        message: 'Failed to open gate: ' + error.message
      };
    }
  }

  async closeGate() {
    try {
      console.log('🚪 Closing gate...');
      
      if (this.isRaspberryPi) {
        await this.setGatePin(this.activeHigh ? 1 : 0);
        
        // Pulse duration for gate trigger
        setTimeout(async () => {
          await this.setGatePin(this.activeHigh ? 0 : 1);
        }, this.pulseDuration);
      }
      
      this.emit('gateStatusChanged', 'CLOSING');
      
      // Simulate gate closing time
      setTimeout(() => {
        this.emit('gateStatusChanged', 'CLOSED');
      }, 1000);
      
      return {
        success: true,
        message: 'Gate closed successfully'
      };
      
    } catch (error) {
      console.error('❌ Error closing gate:', error);
      this.emit('gateStatusChanged', 'ERROR');
      return {
        success: false,
        message: 'Failed to close gate: ' + error.message
      };
    }
  }

  async testGate(duration = 3) {
    try {
      console.log(`🧪 Testing gate for ${duration} seconds...`);
      
      const openResult = await this.openGate();
      if (!openResult.success) {
        return openResult;
      }
      
      // Wait for specified duration then close
      setTimeout(async () => {
        await this.closeGate();
      }, duration * 1000);
      
      return {
        success: true,
        message: `Gate test completed (${duration}s duration)`
      };
      
    } catch (error) {
      console.error('❌ Error testing gate:', error);
      return {
        success: false,
        message: 'Failed to test gate: ' + error.message
      };
    }
  }

  async setGatePin(value) {
    if (!this.isRaspberryPi) {
      console.log(`🔧 [SIMULATION] Gate pin ${this.gatePin} set to ${value}`);
      return;
    }

    try {
      if (this.gateOutput) {
        // raspi-gpio
        this.gateOutput.write(value);
      } else if (this.gpio && this.gpio.write) {
        // rpi-gpio
        return new Promise((resolve, reject) => {
          this.gpio.write(this.gatePin, value, (err) => {
            if (err) reject(err);
            else resolve();
          });
        });
      } else if (this.gateGpio) {
        // gpio library
        this.gateGpio.set(value);
      }
    } catch (error) {
      console.error('❌ Error setting gate pin:', error);
      throw error;
    }
  }

  async setLedPin(value) {
    if (!this.isRaspberryPi) {
      return;
    }

    try {
      if (this.ledOutput) {
        // raspi-gpio
        this.ledOutput.write(value);
      } else if (this.gpio && this.gpio.write) {
        // rpi-gpio
        return new Promise((resolve, reject) => {
          this.gpio.write(this.ledPin, value, (err) => {
            if (err) reject(err);
            else resolve();
          });
        });
      } else if (this.ledGpio) {
        // gpio library
        this.ledGpio.set(value);
      }
    } catch (error) {
      console.error('❌ Error setting LED pin:', error);
    }
  }

  startLedHeartbeat() {
    if (this.ledHeartbeatInterval) {
      clearInterval(this.ledHeartbeatInterval);
    }

    console.log('💓 Starting LED heartbeat...');
    let ledState = false;

    this.ledHeartbeatInterval = setInterval(async () => {
      ledState = !ledState;
      await this.setLedPin(ledState ? 1 : 0);
    }, 1000); // Blink every second
  }

  stopLedHeartbeat() {
    if (this.ledHeartbeatInterval) {
      clearInterval(this.ledHeartbeatInterval);
      this.ledHeartbeatInterval = null;
    }
    
    // Turn off LED
    this.setLedPin(0);
    console.log('💓 LED heartbeat stopped');
  }

  async cleanup() {
    try {
      console.log('🧹 Cleaning up GPIO service...');
      
      this.stopLedHeartbeat();
      this.stopInputMonitoring();
      
      if (this.isRaspberryPi) {
        // Set pins to safe state
        await this.setGatePin(this.activeHigh ? 0 : 1); // Gate closed
        await this.setLedPin(0); // LED off
        
        if (this.gpio && this.gpio.destroy) {
          this.gpio.destroy();
        }
        
        if (this.gateGpio && this.gateGpio.unexport) {
          this.gateGpio.unexport();
        }
        
        if (this.ledGpio && this.ledGpio.unexport) {
          this.ledGpio.unexport();
        }
      }
      
      console.log('✅ GPIO service cleanup completed');
    } catch (error) {
      console.error('❌ Error during GPIO cleanup:', error);
    }
  }

  async testPin(pin, name, duration = 2000) {
    try {
      console.log(`🧪 Testing ${name} (GPIO ${pin}) for ${duration}ms...`);
      
      if (!this.isRaspberryPi) {
        console.log(`🔧 [SIMULATION] Testing ${name} (GPIO ${pin})`);
        return {
          success: true,
          message: `${name} test completed (simulation mode)`
        };
      }
      
      // Check if it's an output pin
      const outputPins = [this.pins.TRIGGER1, this.pins.TRIGGER2, this.pins.LED_LIVE];
      
      if (outputPins.includes(pin)) {
        // Test output pin by toggling it
        await this.writePin(pin, 1);
        await new Promise(resolve => setTimeout(resolve, duration));
        await this.writePin(pin, 0);
        
        return {
          success: true,
          message: `${name} output test completed`
        };
      } else {
        // Test input pin by reading current value
        const value = await this.readPin(pin);
        return {
          success: true,
          message: `${name} input value: ${value ? 'HIGH' : 'LOW'}`
        };
      }
      
    } catch (error) {
      console.error(`❌ Error testing ${name}:`, error);
      return {
        success: false,
        message: `Failed to test ${name}: ${error.message}`
      };
    }
  }

  async testAllPins() {
    try {
      console.log('🧪 Testing all GPIO pins...');
      
      const results = [];
      
      // Test all defined pins
      for (const [name, pin] of Object.entries(this.pins)) {
        const result = await this.testPin(pin, name, 1000); // 1 second test
        results.push({
          name: name,
          pin: pin,
          success: result.success,
          message: result.message
        });
        
        // Small delay between tests
        await new Promise(resolve => setTimeout(resolve, 200));
      }
      
      return results;
      
    } catch (error) {
      console.error('❌ Error testing all pins:', error);
      throw error;
    }
  }

  async writePin(pin, value) {
    try {
      if (!this.isRaspberryPi) {
        console.log(`🔧 [SIMULATION] GPIO ${pin} set to ${value}`);
        return {
          success: true,
          message: `GPIO ${pin} set to ${value} (simulation)`
        };
      }
      
      // Use sysfs interface for more reliable GPIO control
      const fs = require('fs').promises;
      
      try {
        // Export pin if not already exported
        await fs.writeFile('/sys/class/gpio/export', pin.toString()).catch(() => {});
        
        // Set direction to output
        await fs.writeFile(`/sys/class/gpio/gpio${pin}/direction`, 'out');
        
        // Write value
        await fs.writeFile(`/sys/class/gpio/gpio${pin}/value`, value.toString());
        
        console.log(`✅ GPIO ${pin} set to ${value}`);
        return {
          success: true,
          message: `GPIO ${pin} set to ${value}`
        };
        
      } catch (error) {
        console.error(`❌ Error writing to GPIO ${pin}:`, error);
        return {
          success: false,
          message: `Failed to write GPIO ${pin}: ${error.message}`
        };
      }
      
    } catch (error) {
      console.error(`❌ Error in writePin:`, error);
      return {
        success: false,
        message: `Write pin error: ${error.message}`
      };
    }
  }

  async readPin(pin) {
    try {
      if (!this.isRaspberryPi) {
        // Simulate random input values
        return Math.random() > 0.5;
      }
      
      const fs = require('fs').promises;
      
      try {
        // Export pin if not already exported
        await fs.writeFile('/sys/class/gpio/export', pin.toString()).catch(() => {});
        
        // Set direction to input
        await fs.writeFile(`/sys/class/gpio/gpio${pin}/direction`, 'in');
        
        // Read value
        const value = await fs.readFile(`/sys/class/gpio/gpio${pin}/value`, 'utf8');
        const pinValue = parseInt(value.trim()) === 1;
        
        // Store value for status reporting
        this.inputValues[pin] = pinValue;
        
        return pinValue;
        
      } catch (error) {
        console.error(`❌ Error reading GPIO ${pin}:`, error);
        return null;
      }
      
    } catch (error) {
      console.error(`❌ Error in readPin:`, error);
      return null;
    }
  }

  readAllInputs() {
    try {
      const inputs = {};
      
      // Read all input pins
      const inputPins = {
        loop1: this.pins.LOOP1,
        loop2: this.pins.LOOP2,
        struk: this.pins.STRUK,
        emergency: this.pins.EMERGENCY
      };
      
      if (!this.isRaspberryPi) {
        // Simulate values
        for (const [name, pin] of Object.entries(inputPins)) {
          inputs[name] = Math.random() > 0.3; // Mostly HIGH (inactive for active-low)
        }
        return inputs;
      }
      
      // Read actual values
      for (const [name, pin] of Object.entries(inputPins)) {
        inputs[name] = this.inputValues[pin] !== undefined ? this.inputValues[pin] : null;
      }
      
      return inputs;
      
    } catch (error) {
      console.error('❌ Error reading all inputs:', error);
      return {};
    }
  }

  // Start continuous input monitoring
  startInputMonitoring() {
    if (this.inputMonitoringInterval) {
      clearInterval(this.inputMonitoringInterval);
    }
    
    console.log('👁️ Starting input monitoring...');
    
    this.inputMonitoringInterval = setInterval(async () => {
      const inputPins = [this.pins.LOOP1, this.pins.LOOP2, this.pins.STRUK, this.pins.EMERGENCY];
      
      for (const pin of inputPins) {
        await this.readPin(pin);
      }
    }, 100); // Read every 100ms
  }

  stopInputMonitoring() {
    if (this.inputMonitoringInterval) {
      clearInterval(this.inputMonitoringInterval);
      this.inputMonitoringInterval = null;
      console.log('👁️ Input monitoring stopped');
    }
  }

  async cleanup() {
    try {
      console.log('🧹 Cleaning up GPIO service...');
      
      this.stopLedHeartbeat();
      this.stopInputMonitoring();
      
      if (this.isRaspberryPi) {
        // Set pins to safe state
        await this.setGatePin(this.activeHigh ? 0 : 1); // Gate closed
        await this.setLedPin(0); // LED off
        
        if (this.gpio && this.gpio.destroy) {
          this.gpio.destroy();
        }
        
        if (this.gateGpio && this.gateGpio.unexport) {
          this.gateGpio.unexport();
        }
        
        if (this.ledGpio && this.ledGpio.unexport) {
          this.ledGpio.unexport();
        }
      }
      
      console.log('✅ GPIO service cleanup completed');
    } catch (error) {
      console.error('❌ Error during GPIO cleanup:', error);
    }
  }

  getStatus() {
    return {
      initialized: this.isInitialized,
      isRaspberryPi: this.isRaspberryPi,
      pins: this.pins,
      gatePin: this.gatePin,
      ledPin: this.ledPin,
      activeHigh: this.activeHigh,
      pulseDuration: this.pulseDuration,
      inputValues: this.inputValues
    };
  }
}

module.exports = new GPIOService();
