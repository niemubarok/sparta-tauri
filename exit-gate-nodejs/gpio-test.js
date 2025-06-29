// Simple GPIO Test for Exit Gate System
// Run with: node gpio-test.js

require('dotenv').config();

const GATE_PIN = parseInt(process.env.GATE_GPIO_PIN) || 24;
const LED_PIN = parseInt(process.env.LED_GPIO_PIN) || 25;
const ACTIVE_HIGH = process.env.GPIO_ACTIVE_HIGH === 'true';

console.log('==========================================');
console.log('  SIMPLE GPIO TEST');
console.log('==========================================');
console.log(`Gate Pin: ${GATE_PIN}`);
console.log(`LED Pin: ${LED_PIN}`);
console.log(`Active High: ${ACTIVE_HIGH}`);
console.log('');

// Check if running on Raspberry Pi
const fs = require('fs');
let isRaspberryPi = false;
try {
    const cpuinfo = fs.readFileSync('/proc/cpuinfo', 'utf8');
    isRaspberryPi = cpuinfo.includes('Raspberry Pi') || cpuinfo.includes('BCM');
    console.log(`Running on Raspberry Pi: ${isRaspberryPi}`);
} catch (error) {
    console.log('Not running on Linux/Raspberry Pi');
}

if (!isRaspberryPi) {
    console.log('GPIO test can only run on Raspberry Pi');
    process.exit(1);
}

// Simple GPIO control using sysfs
class SimpleGPIO {
    constructor(pin) {
        this.pin = pin;
        this.exported = false;
    }
    
    async export() {
        try {
            fs.writeFileSync('/sys/class/gpio/export', this.pin.toString());
            await this.sleep(100);
            fs.writeFileSync(`/sys/class/gpio/gpio${this.pin}/direction`, 'out');
            this.exported = true;
            console.log(`✓ GPIO ${this.pin} exported and set to output`);
        } catch (error) {
            if (error.code === 'EBUSY') {
                console.log(`○ GPIO ${this.pin} already exported`);
                this.exported = true;
            } else {
                console.error(`✗ Failed to export GPIO ${this.pin}:`, error.message);
            }
        }
    }
    
    async unexport() {
        try {
            if (this.exported) {
                fs.writeFileSync('/sys/class/gpio/unexport', this.pin.toString());
                this.exported = false;
                console.log(`✓ GPIO ${this.pin} unexported`);
            }
        } catch (error) {
            console.error(`✗ Failed to unexport GPIO ${this.pin}:`, error.message);
        }
    }
    
    async setValue(value) {
        try {
            if (!this.exported) {
                throw new Error('Pin not exported');
            }
            fs.writeFileSync(`/sys/class/gpio/gpio${this.pin}/value`, value.toString());
            console.log(`GPIO ${this.pin} set to ${value}`);
        } catch (error) {
            console.error(`✗ Failed to set GPIO ${this.pin} value:`, error.message);
        }
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

async function testGPIO() {
    console.log('\nInitializing GPIO pins...');
    
    const gateGpio = new SimpleGPIO(GATE_PIN);
    const ledGpio = new SimpleGPIO(LED_PIN);
    
    try {
        // Export pins
        await gateGpio.export();
        await ledGpio.export();
        
        console.log('\nTesting LED (3 blinks)...');
        for (let i = 0; i < 3; i++) {
            await ledGpio.setValue(1);
            await ledGpio.sleep(500);
            await ledGpio.setValue(0);
            await ledGpio.sleep(500);
        }
        
        console.log('\nTesting gate trigger (3 pulses)...');
        for (let i = 0; i < 3; i++) {
            console.log(`Gate pulse ${i + 1}...`);
            await gateGpio.setValue(ACTIVE_HIGH ? 1 : 0);
            await gateGpio.sleep(500);
            await gateGpio.setValue(ACTIVE_HIGH ? 0 : 1);
            await gateGpio.sleep(1000);
        }
        
        console.log('\nTesting complete! Check if:');
        console.log('1. LED blinked 3 times');
        console.log('2. Gate received 3 trigger pulses');
        console.log('3. No error messages appeared');
        
    } catch (error) {
        console.error('\n✗ GPIO test failed:', error);
    } finally {
        // Cleanup
        console.log('\nCleaning up...');
        await gateGpio.setValue(ACTIVE_HIGH ? 0 : 1); // Gate safe state
        await ledGpio.setValue(0); // LED off
        await gateGpio.unexport();
        await ledGpio.unexport();
    }
}

// Test using GPIO service
async function testGPIOService() {
    console.log('\n==========================================');
    console.log('  TESTING GPIO SERVICE');
    console.log('==========================================');
    
    try {
        const gpioService = require('./services/gpioService');
        
        console.log('Initializing GPIO service...');
        await gpioService.initialize();
        
        const status = gpioService.getStatus();
        console.log('Service status:', status);
        
        if (status.isRaspberryPi) {
            console.log('\nTesting LED heartbeat...');
            gpioService.startLedHeartbeat();
            await new Promise(resolve => setTimeout(resolve, 5000));
            gpioService.stopLedHeartbeat();
            
            console.log('\nTesting gate operation...');
            const result = await gpioService.openGate(3);
            console.log('Gate result:', result);
            
            await new Promise(resolve => setTimeout(resolve, 4000));
            
            console.log('✓ GPIO service test completed');
        } else {
            console.log('GPIO service running in simulation mode');
        }
        
    } catch (error) {
        console.error('✗ GPIO service test failed:', error);
    }
}

async function main() {
    // Test 1: Direct GPIO control
    await testGPIO();
    
    // Test 2: GPIO service
    await testGPIOService();
    
    console.log('\n==========================================');
    console.log('  ALL TESTS COMPLETE');
    console.log('==========================================');
    
    process.exit(0);
}

main().catch(console.error);
