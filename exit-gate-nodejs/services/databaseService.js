const PouchDB = require('pouchdb');
const PouchDBFind = require('pouchdb-find');
const PouchDBAdapterHttp = require('pouchdb-adapter-http');

// Add plugins
PouchDB.plugin(PouchDBFind);
PouchDB.plugin(PouchDBAdapterHttp);

class DatabaseService {
  constructor() {
    this.localDB = null;
    this.remoteDB = null;
    this.syncHandler = null;
    this.isConnected = false;
    this.syncStatus = {
      connected: false,
      last_sync: null,
      sync_active: false,
      error_message: null,
      docs_synced: 0,
      pending_changes: 0
    };
  }

  async initialize() {
    try {
      console.log('💾 Initializing database service...');
      
      const localDbName = process.env.LOCAL_DB_NAME || 'exit_gate_local';
      const remoteDbUrl = process.env.COUCHDB_URL;
      const databaseName = process.env.DATABASE_NAME || 'parking_system';
      
      // Initialize local database
      this.localDB = new PouchDB(localDbName);
      console.log(`✅ Local database initialized: ${localDbName}`);
      
      // Initialize remote database if configured
      if (remoteDbUrl) {
        try {
          this.remoteDB = new PouchDB(`${remoteDbUrl}/${databaseName}`);
          
          // Test connection
          await this.remoteDB.info();
          this.isConnected = true;
          this.syncStatus.connected = true;
          
          console.log(`✅ Remote database connected: ${remoteDbUrl}/${databaseName}`);
          
          // Start bidirectional sync
          this.startSync();
          
        } catch (remoteError) {
          console.warn('⚠️ Remote database not available, working in offline mode:', remoteError.message);
          this.isConnected = false;
          this.syncStatus.connected = false;
          this.syncStatus.error_message = remoteError.message;
        }
      } else {
        console.log('📴 No remote database configured, working in local mode');
      }
      
      // Create indexes for better query performance
      await this.createIndexes();
      
      console.log('✅ Database service initialized');
      
    } catch (error) {
      console.error('❌ Failed to initialize database service:', error);
      throw error;
    }
  }

  async createIndexes() {
    try {
      const indexes = [
        { index: { fields: ['no_pol'] } },
        { index: { fields: ['no_barcode'] } },
        { index: { fields: ['waktu_masuk'] } },
        { index: { fields: ['waktu_keluar'] } },
        { index: { fields: ['status'] } },
        { index: { fields: ['tanggal'] } },
        { index: { fields: ['id_kendaraan'] } }
      ];

      for (const indexDef of indexes) {
        try {
          await this.localDB.createIndex(indexDef);
        } catch (error) {
          // Index might already exist, ignore error
          if (!error.message.includes('exists')) {
            console.warn('⚠️ Error creating index:', error.message);
          }
        }
      }
      
      console.log('📑 Database indexes created');
    } catch (error) {
      console.error('❌ Error creating indexes:', error);
    }
  }

  startSync() {
    if (!this.remoteDB) {
      return;
    }

    console.log('🔄 Starting database synchronization...');
    
    this.syncHandler = this.localDB.sync(this.remoteDB, {
      live: true,
      retry: true,
      heartbeat: 10000,
      timeout: 30000
    })
    .on('change', (info) => {
      console.log('📊 Sync change:', {
        direction: info.direction,
        docs: info.change.docs ? info.change.docs.length : 0
      });
      
      this.syncStatus.docs_synced += info.change.docs ? info.change.docs.length : 0;
      this.syncStatus.last_sync = new Date().toISOString();
    })
    .on('active', () => {
      console.log('🔄 Sync active');
      this.syncStatus.sync_active = true;
      this.syncStatus.connected = true;
      this.syncStatus.error_message = null;
    })
    .on('paused', () => {
      console.log('⏸️ Sync paused');
      this.syncStatus.sync_active = false;
    })
    .on('error', (err) => {
      console.error('❌ Sync error:', err);
      this.syncStatus.connected = false;
      this.syncStatus.sync_active = false;
      this.syncStatus.error_message = err.message;
    });
  }

  async findTransactionByBarcode(barcode) {
    try {
      const result = await this.localDB.find({
        selector: {
          no_barcode: barcode,
          status: 0, // Active transaction
          waktu_keluar: { $exists: false }
        },
        limit: 1
      });

      return result.docs.length > 0 ? result.docs[0] : null;
    } catch (error) {
      console.error('❌ Error finding transaction by barcode:', error);
      throw error;
    }
  }

  async findTransactionByPlate(licensePlate) {
    try {
      const result = await this.localDB.find({
        selector: {
          no_pol: licensePlate,
          status: 0, // Active transaction
          waktu_keluar: { $exists: false }
        },
        limit: 1,
        sort: [{ 'waktu_masuk': 'desc' }]
      });

      return result.docs.length > 0 ? result.docs[0] : null;
    } catch (error) {
      console.error('❌ Error finding transaction by plate:', error);
      throw error;
    }
  }

  async processVehicleExit(licensePlate, operatorId, gateId) {
    try {
      console.log(`🚗 Processing exit for vehicle: ${licensePlate}`);
      
      // Find active transaction
      const transaction = await this.findTransactionByPlate(licensePlate);
      
      if (!transaction) {
        return {
          success: false,
          message: `No active transaction found for vehicle ${licensePlate}`
        };
      }

      // Calculate exit fee
      const fee = await this.calculateExitFee(transaction);
      
      // Get current timestamp
      const exitTime = new Date().toISOString();
      
      // Update transaction with exit information
      const updatedTransaction = {
        ...transaction,
        waktu_keluar: exitTime,
        id_op_keluar: operatorId,
        id_pintu_keluar: gateId,
        bayar_keluar: fee,
        status: 0, // Completed
        pklogin: exitTime
      };

      // Save updated transaction
      const saveResult = await this.localDB.put(updatedTransaction);
      
      if (saveResult.ok) {
        console.log(`✅ Exit processed successfully for ${licensePlate}, fee: ${fee}`);
        
        return {
          success: true,
          transaction: updatedTransaction,
          fee: fee,
          message: `Exit processed successfully for ${licensePlate}`
        };
      } else {
        throw new Error('Failed to save transaction');
      }
      
    } catch (error) {
      console.error('❌ Error processing vehicle exit:', error);
      return {
        success: false,
        message: 'Error processing exit: ' + error.message
      };
    }
  }

  async calculateExitFee(transaction) {
    try {
      // Get vehicle type and tariff
      const vehicleType = await this.getVehicleType(transaction.id_kendaraan);
      
      if (!vehicleType) {
        console.warn('⚠️ Vehicle type not found, using default fee');
        return 5000; // Default fee
      }

      // Simple calculation - could be more complex based on parking duration
      const entryTime = new Date(transaction.waktu_masuk);
      const exitTime = new Date();
      const durationHours = Math.ceil((exitTime - entryTime) / (1000 * 60 * 60));
      
      let fee = vehicleType.tarif || 5000;
      
      // Apply hourly rate if duration > 1 hour
      if (durationHours > 1 && vehicleType.tarif_interval) {
        fee += (durationHours - 1) * vehicleType.tarif_interval;
      }
      
      // Apply maximum daily rate if configured
      if (vehicleType.maksimum && fee > vehicleType.maksimum) {
        fee = vehicleType.maksimum;
      }
      
      return fee;
      
    } catch (error) {
      console.error('❌ Error calculating exit fee:', error);
      return 5000; // Default fee on error
    }
  }

  async getVehicleType(vehicleTypeId) {
    try {
      const result = await this.localDB.find({
        selector: {
          type: 'vehicle_type',
          id_kendaraan: vehicleTypeId
        },
        limit: 1
      });

      return result.docs.length > 0 ? result.docs[0] : null;
    } catch (error) {
      console.error('❌ Error getting vehicle type:', error);
      return null;
    }
  }

  async getTodayExitStats() {
    try {
      const today = new Date();
      const startOfDay = new Date(today.getFullYear(), today.getMonth(), today.getDate());
      const endOfDay = new Date(startOfDay.getTime() + 24 * 60 * 60 * 1000);

      const result = await this.localDB.find({
        selector: {
          waktu_keluar: {
            $gte: startOfDay.toISOString(),
            $lt: endOfDay.toISOString()
          },
          status: 0
        }
      });

      const totalExits = result.docs.length;
      const totalRevenue = result.docs.reduce((sum, doc) => {
        return sum + (doc.bayar_keluar || 0);
      }, 0);

      return {
        totalExits,
        totalRevenue
      };
    } catch (error) {
      console.error('❌ Error getting today stats:', error);
      return {
        totalExits: 0,
        totalRevenue: 0
      };
    }
  }

  async getSettings() {
    try {
      const result = await this.localDB.find({
        selector: {
          type: 'settings'
        },
        limit: 1
      });

      if (result.docs.length > 0) {
        return result.docs[0];
      }

      // Return default settings if none found
      return {
        _id: 'settings_default',
        type: 'settings',
        gate_auto_close_time: 10,
        gpio_pin: 24,
        led_pin: 25,
        gpio_active_high: true,
        audio_enabled: true,
        camera_enabled: false
      };
    } catch (error) {
      console.error('❌ Error getting settings:', error);
      return null;
    }
  }

  async updateSettings(settings) {
    try {
      const currentSettings = await this.getSettings();
      
      const updatedSettings = {
        ...currentSettings,
        ...settings,
        type: 'settings',
        updated_at: new Date().toISOString()
      };

      const result = await this.localDB.put(updatedSettings);
      
      return {
        success: result.ok,
        settings: updatedSettings
      };
    } catch (error) {
      console.error('❌ Error updating settings:', error);
      return {
        success: false,
        message: error.message
      };
    }
  }

  getSyncStatus() {
    return {
      ...this.syncStatus,
      isConnected: this.isConnected
    };
  }

  async cleanup() {
    try {
      console.log('🧹 Cleaning up database service...');
      
      if (this.syncHandler) {
        this.syncHandler.cancel();
        this.syncHandler = null;
      }
      
      if (this.localDB) {
        await this.localDB.close();
      }
      
      if (this.remoteDB) {
        await this.remoteDB.close();
      }
      
      console.log('✅ Database service cleanup completed');
    } catch (error) {
      console.error('❌ Error during database cleanup:', error);
    }
  }

  // Utility methods for testing
  async addSampleData() {
    try {
      const sampleTransaction = {
        _id: `transaction_${Date.now()}`,
        id: `TX${Date.now()}`,
        no_pol: 'B1234ABC',
        id_kendaraan: 'MOBIL',
        status: 0,
        id_pintu_masuk: 'GATE_01',
        waktu_masuk: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
        id_op_masuk: 'OPERATOR_01',
        no_barcode: `BC${Date.now()}`,
        tanggal: new Date().toISOString(),
        bayar_masuk: 0,
        jenis_system: 'AUTO'
      };

      const sampleVehicleType = {
        _id: 'vehicle_type_mobil',
        type: 'vehicle_type',
        id_kendaraan: 'MOBIL',
        nama_kendaraan: 'Mobil',
        tarif: 5000,
        tarif_interval: 3000,
        interval: 60,
        maksimum: 25000
      };

      await this.localDB.put(sampleTransaction);
      await this.localDB.put(sampleVehicleType);
      
      console.log('✅ Sample data added successfully');
    } catch (error) {
      console.error('❌ Error adding sample data:', error);
    }
  }
}

module.exports = new DatabaseService();
