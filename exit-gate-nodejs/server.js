const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const compression = require('compression');
const path = require('path');
require('dotenv').config();

// Import services
const gpioService = require('./services/gpioService');
const databaseService = require('./services/databaseService');
const audioService = require('./services/audioService');

// Import routes
const apiRoutes = require('./routes/api');
const webRoutes = require('./routes/web');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: process.env.CORS_ORIGIN || "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

// Middleware
app.use(helmet({
  contentSecurityPolicy: false, // Disable for development
}));
app.use(compression());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Make io available to routes
app.set('io', io);

// Routes
app.use('/api', apiRoutes);
app.use('/', webRoutes);

// Global variables for system state
let gateStatus = 'CLOSED';
let ledStatus = false;
let currentTransaction = null;
let todayStats = {
  totalExits: 0,
  totalRevenue: 0
};

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  // Send current status to new client
  socket.emit('gate:status', { status: gateStatus });
  socket.emit('led:status', { status: ledStatus });
  socket.emit('stats:update', todayStats);

  // Handle gate control requests
  socket.on('gate:open', async (data) => {
    try {
      const autoCloseTime = data.autoCloseTime || parseInt(process.env.GATE_AUTO_CLOSE_TIME) || 10;
      const result = await gpioService.openGate(autoCloseTime);
      
      if (result.success) {
        gateStatus = 'OPENING';
        io.emit('gate:status', { status: gateStatus });
        
        // Simulate gate opening time
        setTimeout(() => {
          gateStatus = 'OPEN';
          io.emit('gate:status', { status: gateStatus });
          
          // Auto close timer
          setTimeout(async () => {
            const closeResult = await gpioService.closeGate();
            if (closeResult.success) {
              gateStatus = 'CLOSED';
              io.emit('gate:status', { status: gateStatus });
            }
          }, autoCloseTime * 1000);
        }, 1000);
      }
      
      socket.emit('gate:result', result);
    } catch (error) {
      console.error('Error opening gate:', error);
      socket.emit('error', { message: 'Failed to open gate' });
    }
  });

  socket.on('gate:close', async () => {
    try {
      const result = await gpioService.closeGate();
      
      if (result.success) {
        gateStatus = 'CLOSING';
        io.emit('gate:status', { status: gateStatus });
        
        setTimeout(() => {
          gateStatus = 'CLOSED';
          io.emit('gate:status', { status: gateStatus });
        }, 1000);
      }
      
      socket.emit('gate:result', result);
    } catch (error) {
      console.error('Error closing gate:', error);
      socket.emit('error', { message: 'Failed to close gate' });
    }
  });

  socket.on('gate:test', async () => {
    try {
      const testDuration = parseInt(process.env.GATE_TEST_DURATION) || 3;
      const result = await gpioService.testGate(testDuration);
      socket.emit('gate:result', result);
    } catch (error) {
      console.error('Error testing gate:', error);
      socket.emit('error', { message: 'Failed to test gate' });
    }
  });

  // Handle transaction processing
  socket.on('transaction:process', async (data) => {
    try {
      console.log('Processing transaction:', data);
      
      const { barcode, licensePlate } = data;
      let transaction = null;

      // Find transaction by barcode or license plate
      if (barcode) {
        transaction = await databaseService.findTransactionByBarcode(barcode);
      } else if (licensePlate) {
        transaction = await databaseService.findTransactionByPlate(licensePlate);
      }

      if (transaction) {
        // Process exit
        const exitResult = await databaseService.processVehicleExit(
          transaction.no_pol,
          'SYSTEM',
          'EXIT_GATE_01'
        );

        if (exitResult.success) {
          currentTransaction = exitResult.transaction;
          
          // Update today's stats
          todayStats.totalExits++;
          todayStats.totalRevenue += exitResult.fee || 0;
          
          // Play success sound
          try {
            await audioService.playSuccessSound();
          } catch (audioError) {
            console.warn('Audio error:', audioError.message);
          }
          
          // Emit transaction result
          socket.emit('transaction:result', {
            success: true,
            transaction: currentTransaction,
            fee: exitResult.fee
          });
          
          // Update stats for all clients
          io.emit('stats:update', todayStats);
          
          // Auto-open gate
          setTimeout(() => {
            socket.emit('gate:open', { autoCloseTime: 10 });
          }, 1000);
          
        } else {
          socket.emit('transaction:result', {
            success: false,
            message: exitResult.message || 'Failed to process exit'
          });
          
          try {
            await audioService.playErrorSound();
          } catch (audioError) {
            console.warn('Audio error:', audioError.message);
          }
        }
      } else {
        socket.emit('transaction:result', {
          success: false,
          message: 'No active transaction found'
        });
        
        try {
          await audioService.playErrorSound();
        } catch (audioError) {
          console.warn('Audio error:', audioError.message);
        }
      }
    } catch (error) {
      console.error('Error processing transaction:', error);
      socket.emit('transaction:result', {
        success: false,
        message: 'Error processing transaction: ' + error.message
      });
    }
  });

  // Handle barcode scan
  socket.on('scanner:scan', async (data) => {
    try {
      console.log('Barcode scanned:', data.code);
      
      // Play scan sound
      try {
        await audioService.playScanSound();
      } catch (audioError) {
        console.warn('Audio error:', audioError.message);
      }
      
      // Process as transaction
      socket.emit('transaction:process', { barcode: data.code });
    } catch (error) {
      console.error('Error handling barcode scan:', error);
      socket.emit('error', { message: 'Error processing barcode scan' });
    }
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

// Error handling
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({
    success: false,
    message: 'Internal server error',
    error: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: 'Route not found'
  });
});

// Initialize services and start server
async function startServer() {
  try {
    console.log('🚀 Starting Exit Gate System...');
    
    // Initialize GPIO service
    console.log('📡 Initializing GPIO service...');
    await gpioService.initialize();
    
    // Initialize database service
    console.log('💾 Initializing database service...');
    await databaseService.initialize();
    
    // Initialize audio service
    console.log('🔊 Initializing audio service...');
    await audioService.initialize();
    
    // Load today's stats
    console.log('📊 Loading today\'s statistics...');
    todayStats = await databaseService.getTodayExitStats();
    
    // Start LED heartbeat
    gpioService.startLedHeartbeat();
    
    // Start server
    server.listen(PORT, HOST, () => {
      console.log(`✅ Exit Gate System running on http://${HOST}:${PORT}`);
      console.log('📌 GPIO Configuration:');
      console.log(`   - Gate control pin: ${process.env.GATE_GPIO_PIN}`);
      console.log(`   - LED indicator pin: ${process.env.LED_GPIO_PIN}`);
      console.log('🌐 WebSocket server ready for connections');
    });
    
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Shutting down Exit Gate System...');
  
  try {
    // Close gate if open
    if (gateStatus === 'OPEN') {
      await gpioService.closeGate();
    }
    
    // Cleanup GPIO
    await gpioService.cleanup();
    
    // Close database connections
    await databaseService.cleanup();
    
    // Close server
    server.close(() => {
      console.log('✅ Exit Gate System shutdown complete');
      process.exit(0);
    });
  } catch (error) {
    console.error('❌ Error during shutdown:', error);
    process.exit(1);
  }
});

process.on('SIGTERM', async () => {
  console.log('🛑 Received SIGTERM, shutting down gracefully...');
  await gpioService.cleanup();
  process.exit(0);
});

// Start the server
startServer();
