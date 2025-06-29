const express = require('express');
const router = express.Router();

// Import services
const gpioService = require('../services/gpioService');
const databaseService = require('../services/databaseService');
const audioService = require('../services/audioService');

// Gate Control Routes
router.post('/gate/open', async (req, res) => {
  try {
    const { autoCloseTime } = req.body;
    const result = await gpioService.openGate(autoCloseTime);
    
    // Emit status update via WebSocket
    const io = req.app.get('io');
    if (io) {
      io.emit('gate:status', { status: 'OPENING' });
    }
    
    res.json(result);
  } catch (error) {
    console.error('API Error - Gate Open:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to open gate: ' + error.message
    });
  }
});

router.post('/gate/close', async (req, res) => {
  try {
    const result = await gpioService.closeGate();
    
    // Emit status update via WebSocket
    const io = req.app.get('io');
    if (io) {
      io.emit('gate:status', { status: 'CLOSING' });
    }
    
    res.json(result);
  } catch (error) {
    console.error('API Error - Gate Close:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to close gate: ' + error.message
    });
  }
});

router.post('/gate/test', async (req, res) => {
  try {
    const { duration } = req.body;
    const result = await gpioService.testGate(duration);
    res.json(result);
  } catch (error) {
    console.error('API Error - Gate Test:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to test gate: ' + error.message
    });
  }
});

router.get('/gate/status', (req, res) => {
  try {
    const status = gpioService.getStatus();
    res.json({
      success: true,
      status: status
    });
  } catch (error) {
    console.error('API Error - Gate Status:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to get gate status: ' + error.message
    });
  }
});

// Transaction Routes
router.post('/transaction/process', async (req, res) => {
  try {
    const { barcode, licensePlate, operatorId = 'SYSTEM', gateId = 'EXIT_GATE_01' } = req.body;
    
    if (!barcode && !licensePlate) {
      return res.status(400).json({
        success: false,
        message: 'Either barcode or license plate is required'
      });
    }
    
    let transaction = null;
    
    // Find transaction
    if (barcode) {
      transaction = await databaseService.findTransactionByBarcode(barcode);
    } else if (licensePlate) {
      transaction = await databaseService.findTransactionByPlate(licensePlate);
    }
    
    if (!transaction) {
      await audioService.playErrorSound();
      return res.status(404).json({
        success: false,
        message: 'No active transaction found'
      });
    }
    
    // Process exit
    const result = await databaseService.processVehicleExit(
      transaction.no_pol,
      operatorId,
      gateId
    );
    
    if (result.success) {
      await audioService.playSuccessSound();
      
      // Emit transaction result via WebSocket
      const io = req.app.get('io');
      if (io) {
        io.emit('transaction:result', result);
        
        // Update stats
        const stats = await databaseService.getTodayExitStats();
        io.emit('stats:update', stats);
      }
    } else {
      await audioService.playErrorSound();
    }
    
    res.json(result);
    
  } catch (error) {
    console.error('API Error - Process Transaction:', error);
    await audioService.playErrorSound();
    res.status(500).json({
      success: false,
      message: 'Failed to process transaction: ' + error.message
    });
  }
});

router.get('/transaction/search/:query', async (req, res) => {
  try {
    const { query } = req.params;
    
    // Try to find by barcode first, then by license plate
    let transaction = await databaseService.findTransactionByBarcode(query);
    
    if (!transaction) {
      transaction = await databaseService.findTransactionByPlate(query);
    }
    
    if (transaction) {
      res.json({
        success: true,
        transaction: transaction
      });
    } else {
      res.status(404).json({
        success: false,
        message: 'Transaction not found'
      });
    }
    
  } catch (error) {
    console.error('API Error - Search Transaction:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to search transaction: ' + error.message
    });
  }
});

router.get('/transaction/stats', async (req, res) => {
  try {
    const stats = await databaseService.getTodayExitStats();
    res.json({
      success: true,
      stats: stats
    });
  } catch (error) {
    console.error('API Error - Get Stats:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to get statistics: ' + error.message
    });
  }
});

// Settings Routes
router.get('/settings', async (req, res) => {
  try {
    const settings = await databaseService.getSettings();
    res.json({
      success: true,
      settings: settings
    });
  } catch (error) {
    console.error('API Error - Get Settings:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to get settings: ' + error.message
    });
  }
});

router.post('/settings', async (req, res) => {
  try {
    const result = await databaseService.updateSettings(req.body);
    res.json(result);
  } catch (error) {
    console.error('API Error - Update Settings:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to update settings: ' + error.message
    });
  }
});

// GPIO Routes
router.get('/gpio/status', (req, res) => {
  try {
    const status = gpioService.getStatus();
    const gpioInputs = gpioService.readAllInputs();
    
    res.json({
      success: true,
      gpio: {
        initialized: status.initialized,
        inputs: gpioInputs,
        pins: status.pins
      }
    });
  } catch (error) {
    console.error('API Error - GPIO Status:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to get GPIO status: ' + error.message
    });
  }
});

router.post('/gpio/test', async (req, res) => {
  try {
    const { pin, name, duration = 2000 } = req.body;
    
    if (!pin || !name) {
      return res.status(400).json({
        success: false,
        message: 'Pin number and name are required'
      });
    }
    
    const result = await gpioService.testPin(pin, name, duration);
    res.json(result);
  } catch (error) {
    console.error('API Error - GPIO Test:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to test GPIO pin: ' + error.message
    });
  }
});

router.post('/gpio/test-all', async (req, res) => {
  try {
    const results = await gpioService.testAllPins();
    res.json({
      success: true,
      message: 'All GPIO tests completed',
      results: results
    });
  } catch (error) {
    console.error('API Error - GPIO Test All:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to test all GPIO pins: ' + error.message
    });
  }
});

router.post('/gpio/set', async (req, res) => {
  try {
    const { pin, value } = req.body;
    
    if (pin === undefined || value === undefined) {
      return res.status(400).json({
        success: false,
        message: 'Pin number and value are required'
      });
    }
    
    const result = await gpioService.writePin(pin, value);
    res.json(result);
  } catch (error) {
    console.error('API Error - GPIO Set:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to set GPIO pin: ' + error.message
    });
  }
});

// Audio Routes
router.post('/audio/test', async (req, res) => {
  try {
    const result = await audioService.testAudio();
    res.json(result);
  } catch (error) {
    console.error('API Error - Test Audio:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to test audio: ' + error.message
    });
  }
});

router.post('/audio/play/:soundType', async (req, res) => {
  try {
    const { soundType } = req.params;
    
    switch (soundType) {
      case 'success':
        await audioService.playSuccessSound();
        break;
      case 'error':
        await audioService.playErrorSound();
        break;
      case 'scan':
        await audioService.playScanSound();
        break;
      case 'gate_open':
        await audioService.playGateOpenSound();
        break;
      case 'gate_close':
        await audioService.playGateCloseSound();
        break;
      default:
        return res.status(400).json({
          success: false,
          message: 'Invalid sound type'
        });
    }
    
    res.json({
      success: true,
      message: `Played ${soundType} sound`
    });
    
  } catch (error) {
    console.error('API Error - Play Sound:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to play sound: ' + error.message
    });
  }
});

router.get('/audio/status', (req, res) => {
  try {
    const status = audioService.getStatus();
    res.json({
      success: true,
      status: status
    });
  } catch (error) {
    console.error('API Error - Audio Status:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to get audio status: ' + error.message
    });
  }
});

// System Routes
router.get('/system/status', async (req, res) => {
  try {
    const systemStatus = {
      gpio: gpioService.getStatus(),
      audio: audioService.getStatus(),
      database: databaseService.getSyncStatus(),
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      version: process.env.npm_package_version || '1.0.0'
    };
    
    res.json({
      success: true,
      status: systemStatus
    });
  } catch (error) {
    console.error('API Error - System Status:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to get system status: ' + error.message
    });
  }
});

// Database Routes (for testing/debugging)
router.post('/database/sample-data', async (req, res) => {
  try {
    if (process.env.NODE_ENV !== 'development') {
      return res.status(403).json({
        success: false,
        message: 'Sample data creation only allowed in development mode'
      });
    }
    
    await databaseService.addSampleData();
    
    res.json({
      success: true,
      message: 'Sample data added successfully'
    });
  } catch (error) {
    console.error('API Error - Add Sample Data:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to add sample data: ' + error.message
    });
  }
});

router.get('/database/sync-status', (req, res) => {
  try {
    const syncStatus = databaseService.getSyncStatus();
    res.json({
      success: true,
      syncStatus: syncStatus
    });
  } catch (error) {
    console.error('API Error - Sync Status:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to get sync status: ' + error.message
    });
  }
});

module.exports = router;
