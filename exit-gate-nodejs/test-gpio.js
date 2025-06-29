const gpioService = require('./services/gpioService');

async function testGpio() {
  console.log('🧪 Testing GPIO functionality...');
  
  try {
    // Initialize GPIO service
    await gpioService.initialize();
    
    const status = gpioService.getStatus();
    console.log('📊 GPIO Status:', status);
    
    if (status.isRaspberryPi) {
      console.log('✅ Running on Raspberry Pi - testing real GPIO');
      
      // Test gate control
      console.log('🚪 Testing gate control...');
      const openResult = await gpioService.openGate(3);
      console.log('Open result:', openResult);
      
      // Wait a bit then close
      setTimeout(async () => {
        const closeResult = await gpioService.closeGate();
        console.log('Close result:', closeResult);
        
        // Test LED
        console.log('💡 Testing LED heartbeat...');
        gpioService.startLedHeartbeat();
        
        // Stop after 10 seconds
        setTimeout(async () => {
          gpioService.stopLedHeartbeat();
          console.log('✅ GPIO test completed');
          
          // Cleanup
          await gpioService.cleanup();
          process.exit(0);
        }, 10000);
      }, 3000);
      
    } else {
      console.log('💻 Running in simulation mode');
      
      // Test simulation
      console.log('🚪 Testing gate simulation...');
      const testResult = await gpioService.testGate(3);
      console.log('Test result:', testResult);
      
      console.log('💡 Testing LED simulation...');
      gpioService.startLedHeartbeat();
      
      setTimeout(async () => {
        gpioService.stopLedHeartbeat();
        console.log('✅ GPIO simulation test completed');
        
        await gpioService.cleanup();
        process.exit(0);
      }, 5000);
    }
    
  } catch (error) {
    console.error('❌ GPIO test failed:', error);
    process.exit(1);
  }
}

// Run test
testGpio();
