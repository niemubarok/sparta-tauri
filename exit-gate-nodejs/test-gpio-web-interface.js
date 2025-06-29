#!/usr/bin/env node

const http = require('http');
const chalk = require('chalk');

// GPIO pin mappings for Exit Gate
const GPIO_PINS = {
    INPUT: {
        LOOP1: 18,
        LOOP2: 27,
        STRUK: 4,
        EMERGENCY: 17
    },
    OUTPUT: {
        TRIGGER1: 24,
        TRIGGER2: 23,
        LED_LIVE: 25
    }
};

const BASE_URL = 'http://192.168.10.51:3000';

console.log(chalk.blue('🔧 Exit Gate GPIO Web Interface Test Suite'));
console.log(chalk.gray('=' .repeat(50)));

// Test GPIO Status endpoint
async function testGPIOStatus() {
    console.log(chalk.yellow('\n📊 Testing GPIO Status endpoint...'));
    
    try {
        const response = await fetch(`${BASE_URL}/api/gpio/status`);
        const data = await response.json();
        
        if (response.ok) {
            console.log(chalk.green('✅ GPIO Status endpoint works'));
            console.log('Input pins status:');
            Object.entries(GPIO_PINS.INPUT).forEach(([name, pin]) => {
                const status = data.inputs[pin];
                const color = status === 1 ? chalk.green : chalk.red;
                console.log(`  ${name} (GPIO ${pin}): ${color(status)}`);
            });
        } else {
            console.log(chalk.red('❌ GPIO Status endpoint failed'));
            console.log(data);
        }
    } catch (error) {
        console.log(chalk.red('❌ Failed to test GPIO Status:'), error.message);
    }
}

// Test individual GPIO pin
async function testGPIOPin(pin, name) {
    try {
        const response = await fetch(`${BASE_URL}/api/gpio/test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pin })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            console.log(chalk.green(`  ✅ ${name} (GPIO ${pin}): ${data.message}`));
        } else {
            console.log(chalk.red(`  ❌ ${name} (GPIO ${pin}): ${data.error || 'Test failed'}`));
        }
    } catch (error) {
        console.log(chalk.red(`  ❌ ${name} (GPIO ${pin}): ${error.message}`));
    }
}

// Test all GPIO output pins
async function testAllOutputPins() {
    console.log(chalk.yellow('\n🔌 Testing individual GPIO output pins...'));
    
    for (const [name, pin] of Object.entries(GPIO_PINS.OUTPUT)) {
        await testGPIOPin(pin, name);
        await new Promise(resolve => setTimeout(resolve, 500)); // 500ms delay
    }
}

// Test all GPIO pins at once
async function testAllGPIOPins() {
    console.log(chalk.yellow('\n🚀 Testing all GPIO pins at once...'));
    
    try {
        const response = await fetch(`${BASE_URL}/api/gpio/test-all`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            console.log(chalk.green('✅ All GPIO pins test completed'));
            console.log('Results:');
            data.results.forEach(result => {
                const color = result.success ? chalk.green : chalk.red;
                const status = result.success ? '✅' : '❌';
                console.log(`  ${status} GPIO ${result.pin}: ${color(result.message || result.error)}`);
            });
        } else {
            console.log(chalk.red('❌ All GPIO pins test failed'));
            console.log(data);
        }
    } catch (error) {
        console.log(chalk.red('❌ Failed to test all GPIO pins:'), error.message);
    }
}

// Test GPIO set endpoint
async function testGPIOSet() {
    console.log(chalk.yellow('\n⚡ Testing GPIO set endpoint...'));
    
    const testPin = GPIO_PINS.OUTPUT.LED_LIVE;
    
    try {
        // Test setting pin HIGH
        let response = await fetch(`${BASE_URL}/api/gpio/set`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pin: testPin, value: 1 })
        });
        
        let data = await response.json();
        
        if (response.ok && data.success) {
            console.log(chalk.green(`  ✅ Set GPIO ${testPin} HIGH: ${data.message}`));
        } else {
            console.log(chalk.red(`  ❌ Failed to set GPIO ${testPin} HIGH: ${data.error}`));
        }
        
        await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second delay
        
        // Test setting pin LOW
        response = await fetch(`${BASE_URL}/api/gpio/set`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pin: testPin, value: 0 })
        });
        
        data = await response.json();
        
        if (response.ok && data.success) {
            console.log(chalk.green(`  ✅ Set GPIO ${testPin} LOW: ${data.message}`));
        } else {
            console.log(chalk.red(`  ❌ Failed to set GPIO ${testPin} LOW: ${data.error}`));
        }
        
    } catch (error) {
        console.log(chalk.red('❌ Failed to test GPIO set:'), error.message);
    }
}

// Check web interface accessibility
async function testWebInterface() {
    console.log(chalk.yellow('\n🌐 Testing web interface accessibility...'));
    
    try {
        const response = await fetch(BASE_URL);
        
        if (response.ok) {
            const html = await response.text();
            
            if (html.includes('GPIO Controls')) {
                console.log(chalk.green('✅ Web interface accessible with GPIO Controls'));
            } else {
                console.log(chalk.yellow('⚠️  Web interface accessible but GPIO Controls section not found'));
            }
        } else {
            console.log(chalk.red('❌ Web interface not accessible'));
        }
    } catch (error) {
        console.log(chalk.red('❌ Failed to access web interface:'), error.message);
    }
}

// Main test function
async function runTests() {
    try {
        await testWebInterface();
        await testGPIOStatus();
        await testAllOutputPins();
        await testAllGPIOPins();
        await testGPIOSet();
        
        console.log(chalk.blue('\n🎉 GPIO Web Interface Test Suite Completed!'));
        console.log(chalk.gray('=' .repeat(50)));
        console.log(chalk.cyan(`💻 Open browser: ${BASE_URL}`));
        console.log(chalk.cyan('🔧 Test GPIO controls in the web interface'));
        
    } catch (error) {
        console.log(chalk.red('\n💥 Test suite failed:'), error.message);
    }
}

// Run tests if this file is executed directly
if (require.main === module) {
    runTests();
}

module.exports = {
    testGPIOStatus,
    testGPIOPin,
    testAllOutputPins,
    testAllGPIOPins,
    testGPIOSet,
    testWebInterface,
    runTests
};
