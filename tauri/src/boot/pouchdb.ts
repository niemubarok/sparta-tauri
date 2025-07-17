import PouchDB from 'pouchdb-browser'
import PouchFind from 'pouchdb-find'
import { boot } from 'quasar/wrappers'
import { Notify } from 'quasar'
import ls from 'localstorage-slim'
import { ref } from 'vue'
// Import settings service for dynamic CouchDB configuration
import { useSettingsService } from 'src/stores/settings-service';

PouchDB.plugin(PouchFind)

interface DatabaseTypes {
  transactions: PouchDB.Database;
  users: PouchDB.Database;
  vehicles: PouchDB.Database;
  tariffs: PouchDB.Database;
  config: PouchDB.Database;
  members: PouchDB.Database;
  membershipTypes: PouchDB.Database;
  // New databases for store integration
  petugas: PouchDB.Database;
  kendaraan: PouchDB.Database;
  levels: PouchDB.Database;
  blacklist: PouchDB.Database;
  tarif: PouchDB.Database;
}


// Remote database URL - now dynamic based on settings
let currentRemoteUrl = ref('')

// Function to update remote URL from settings
const updateRemoteUrl = () => {
  // Try to get settings, fallback to env variables if not available
  try {
    const settingsService = useSettingsService()
    if (settingsService.couchDbConfig) {
      currentRemoteUrl.value = settingsService.couchDbConfig.remoteUrl
      console.log('🔗 Updated remote CouchDB URL from settings:', currentRemoteUrl.value)
    } else {
      // Fallback to environment variables
      const DB_USER = process.env.DB_USER || 'admin'
      const DB_PASSWORD = process.env.DB_PASSWORD || 'admin'
      const DB_URL = process.env.DB_URL || 'localhost'
      currentRemoteUrl.value = `http://${DB_USER}:${DB_PASSWORD}@${DB_URL}:5984`
      console.log('🔗 Using fallback CouchDB URL from env:', currentRemoteUrl.value)
    }
  } catch (error) {
    // Fallback to environment variables if settings service fails
    const DB_USER = process.env.DB_USER || 'admin'
    const DB_PASSWORD = process.env.DB_PASSWORD || 'admin'
    const DB_URL = process.env.DB_URL || 'localhost'
    currentRemoteUrl.value = `http://${DB_USER}:${DB_PASSWORD}@${DB_URL}:5984`
    console.log('⚠️ Settings service failed, using fallback URL:', currentRemoteUrl.value)
  }
}

// Initialize with fallback values
const DB_USER = process.env.DB_USER || 'admin'
const DB_PASSWORD = process.env.DB_PASSWORD || 'admin'
const REMOTE_URL = process.env.DB_URL ? `http://${DB_USER}:${DB_PASSWORD}@${process.env.DB_URL}:5984` : `http://${DB_USER}:${DB_PASSWORD}@localhost:5984`
currentRemoteUrl.value = REMOTE_URL
console.log("🚀 ~ currentRemoteUrl.value:", currentRemoteUrl.value)

// Function to create remote databases with current URL
const createRemoteDatabases = (baseUrl: string) => {
  console.log('🏗️ Creating remote databases with URL:', baseUrl)
  return {
    transactions: new PouchDB(`${baseUrl}/transactions`),
    users: new PouchDB(`${baseUrl}/users`),
    vehicles: new PouchDB(`${baseUrl}/vehicles`), 
    tariffs: new PouchDB(`${baseUrl}/tariffs`),
    config: new PouchDB(`${baseUrl}/config`),
    members: new PouchDB(`${baseUrl}/members`),
    membershipTypes: new PouchDB(`${baseUrl}/membership_types`),
    // New remote databases for store integration
    petugas: new PouchDB(`${baseUrl}/petugas`),
    kendaraan: new PouchDB(`${baseUrl}/kendaraan`),
    levels: new PouchDB(`${baseUrl}/levels`),
    blacklist: new PouchDB(`${baseUrl}/blacklist`),
    tarif: new PouchDB(`${baseUrl}/tarif`)
  }
}

// Remote databases - initialized with current URL
let remoteDbs = createRemoteDatabases(currentRemoteUrl.value)

// Function to reinitialize remote databases when URL changes
const reinitializeRemoteDatabases = () => {
  try {
    updateRemoteUrl()
    remoteDbs = createRemoteDatabases(currentRemoteUrl.value)
    console.log('🔄 Remote databases reinitialized with new URL')
    
    // Restart change handlers after URL change
    setTimeout(() => {
      console.log('🔄 Starting delayed change handlers after URL change...');
      startChangeHandlers().catch(err => {
        console.error('❌ Error restarting change handlers after URL change:', err);
      });
    }, 1000);
  } catch (error) {
    console.error('❌ Error reinitializing remote databases:', error);
    console.warn('⚠️ Application will continue with previous remote configuration');
  }
}

// Database change handlers
const changeHandlers = new Map()

// Reactive state for database status
const isConnected = ref(false);
const lastChangeStatus = ref<'active' | 'error' | 'idle'>('idle');
const lastChangeError = ref<any>(null);

// Setup change handler for a specific database
const setupChangeHandler = async (dbName: string, dbInstance: PouchDB.Database) => {
  try {
    console.log(`🔄 Setting up change handler for ${dbName}...`);
    
    const changeHandler = dbInstance.changes({
      since: 'now',
      live: true,
      include_docs: true,
      timeout: 30000
    });

    changeHandler
      .on('change', (change) => {
        console.log(`📊 Database change for ${dbName}:`, {
          id: change.id,
          rev: change.changes[0].rev,
          deleted: change.deleted
        });
        
        isConnected.value = true;
        lastChangeStatus.value = 'active';
        lastChangeError.value = null;
        
        // Handle specific change events based on database
        if (dbName === process.env.COUCHDB_MASTER && !ls.get("hasVisitedBefore")) {
          Notify.create({
            type: "info",
            message: `Data ${dbName} telah berubah, silahkan refresh halaman`,
            position: "top",
            color: "info",
            actions: [
              {
                label: 'Refresh',
                color: 'white',
                handler: () => {
                  window.location.reload();
                }
              }
            ],
            timeout: 5000,
          });
        }
      })
      .on('error', (err) => {
        console.error(`❌ Change handler error for ${dbName}:`, err);
        lastChangeStatus.value = 'error';
        lastChangeError.value = err;
        isConnected.value = false;
        
        // Auto-restart change handler after error
        setTimeout(() => {
          console.log(`🔄 Restarting change handler for ${dbName}...`);
          restartChangeHandler(dbName);
        }, 10000);
      })
      .on('complete', (info) => {
        console.log(`✅ Change handler completed for ${dbName}:`, info);
        lastChangeStatus.value = 'idle';
      });

    changeHandlers.set(dbName, changeHandler);
    console.log(`✅ Change handler set up for ${dbName}`);
    return changeHandler;
  } catch (error) {
    console.error(`❌ Failed to setup change handler for ${dbName}:`, error);
    return null;
  }
}

// Start change handlers for all databases
const startChangeHandlers = async (): Promise<void> => {
  console.log('🔄 Starting change handlers for all databases...');
  const dbNames = Object.keys(remoteDbs);
  let successCount = 0;
  let failCount = 0;
  
  try {
    for (const dbName of dbNames) {
      try {
        const changeHandler = await setupChangeHandler(
          dbName,
          remoteDbs[dbName as keyof typeof remoteDbs]
        );
        if (changeHandler) {
          successCount++;
        } else {
          failCount++;
        }
      } catch (error) {
        console.error(`❌ Failed to setup change handler for ${dbName}:`, error);
        failCount++;
      }
    }
    console.log(`🔄 Change handlers setup completed: ${successCount} successful, ${failCount} failed (out of ${dbNames.length} databases)`);
  } catch (error) {
    console.error('💥 Critical error in startChangeHandlers:', error);
  }
}

// Restart individual change handler
const restartChangeHandler = async (dbName: string) => {
  try {
    // Cancel existing change handler
    const existingHandler = changeHandlers.get(dbName);
    if (existingHandler) {
      existingHandler.cancel();
      changeHandlers.delete(dbName);
    }
    
    // Setup new change handler
    const changeHandler = await setupChangeHandler(
      dbName,
      remoteDbs[dbName as keyof typeof remoteDbs]
    );
    
    if (changeHandler) {
      console.log(`✅ Change handler restarted for ${dbName}`);
    } else {
      console.warn(`⚠️ Failed to restart change handler for ${dbName}`);
    }
    
  } catch (error) {
    console.error(`❌ Error restarting change handler for ${dbName}:`, error);
    // Retry after delay
    setTimeout(() => {
      console.log(`🔄 Retrying restart for ${dbName}...`);
      restartChangeHandler(dbName);
    }, 15000);
  }
};

// Function to ensure remote database exists with enhanced error handling
async function ensureRemoteDatabase(url: string, dbName: string): Promise<boolean> {
  try {
    console.log(`🔍 Checking if remote database ${dbName} exists at ${url}`);
    
    // Parse URL to extract credentials and pure URL if needed
    let remoteDbUrl = `${url}/${dbName}`;
    let options = {} as any;
  
    // If URL doesn't contain credentials, try to add them from env
    if (!url.includes('@')) {
      const DB_USER = process.env.DB_USER || 'admin';
      const DB_PASSWORD = process.env.DB_PASSWORD || 'admin';
      
      options = {
        auth: {
          username: DB_USER,
          password: DB_PASSWORD
        },
        ajax: {
          timeout: 30000,
          withCredentials: false
        }
      };
      
      console.log(`🔐 Using explicit auth options for ${dbName}`);
    }
    
    try {
      // Try to access the database
      const remoteDb = new PouchDB(remoteDbUrl, options);
      const info = await remoteDb.info();
      console.log(`✅ Remote database ${dbName} is accessible:`, {
        db_name: info.db_name,
        doc_count: info.doc_count,
        update_seq: info.update_seq
      });
      return true;
    } catch (error: any) {
      console.warn(`⚠️ Remote database ${dbName} not accessible:`, error.message);
      
      // If it's a 404, try to create the database
      if (error.status === 404 || error.message.includes('not found')) {
        try {
          console.log(`🏗️ Creating remote database ${dbName}...`);
          const remoteDb = new PouchDB(remoteDbUrl, options);
          await remoteDb.put({
            _id: '_design/init',
            views: {
              all: {
                map: 'function (doc) { emit(doc._id, 1); }'
              }
            }
          });
          console.log(`✅ Remote database ${dbName} created successfully`);
          return true;
        } catch (createError: any) {
          console.error(`❌ Failed to create remote database ${dbName}:`, createError.message);
          return false;
        }
      }
      
      return false;
    }
  } catch (error) {
    console.error(`❌ Unexpected error checking remote database ${dbName}:`, error);
    return false;
  }
}

/**
 * Check if remote database is accessible
 */
const checkRemoteConnection = async (): Promise<boolean> => {
  try {
    console.log('🔗 Checking remote database connection...');
    const info = await remoteDbs.transactions.info();
    console.log('✅ Remote database accessible:', info.db_name);
    isConnected.value = true;
    return true;
  } catch (error: any) {
    console.error('❌ Remote database not accessible:', error?.message || error);
    isConnected.value = false;
    return false;
  }
};

/**
 * Get database status for monitoring
 */
const getDatabaseStatus = () => {
  return {
    isConnected: isConnected.value,
    lastChangeStatus: lastChangeStatus.value,
    lastChangeError: lastChangeError.value
  };
};

/**
 * Add document to database
 */
const addTransaction = async (transaction: any) => {
  try {
    const response = await remoteDbs.transactions.put(transaction);
    console.log('✅ Transaction added successfully:', response.id);
    return response;
  } catch (err) {
    console.error('❌ Error adding transaction:', err);
    throw err;
  }
};

/**
 * Add attachment to document
 */
const addTransactionAttachment = async (
  transactionId: string,
  rev: string,
  attachmentName: string,
  data: string,
  contentType: string = 'image/jpeg'
) => {
  try {
    console.log('� Adding attachment:', {
      transactionId,
      attachmentName,
      dataLength: data.length,
      contentType,
      rev
    });
    
    // Convert base64 to Blob (browser-compatible)
    const binaryString = atob(data);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    
    const blob = new Blob([bytes], { type: contentType });
    console.log('💾 Blob created:', {
      size: blob.size,
      type: blob.type
    });
    
    const response = await remoteDbs.transactions.putAttachment(
      transactionId,
      attachmentName,
      rev,
      blob,
      contentType
    );
    
    console.log('✅ Attachment saved successfully:', response);
    return response;
  } catch (err) {
    console.error('❌ Error adding attachment:', err);
    throw err;
  }
};

/**
 * Get attachment from document
 */
const getTransactionAttachment = async (
  transactionId: string,
  attachmentName: string
) => {
  try {
    const response = await remoteDbs.transactions.getAttachment(
      transactionId,
      attachmentName
    );
    return response;
  } catch (err) {
    console.error('❌ Error getting attachment:', err);
    throw err;
  }
};

// Health check function
const startDatabaseHealthCheck = () => {
  console.log('🏥 Starting database health monitoring...');
  
  // Check health every 60 seconds
  setInterval(() => {
    console.log('🔍 Checking database health...');
    
    Object.keys(remoteDbs).forEach(dbName => {
      const changeHandler = changeHandlers.get(dbName);
      
      if (!changeHandler) {
        console.log(`⚠️ Missing change handler for ${dbName}, restarting...`);
        restartChangeHandler(dbName);
        return;
      }
    });
  }, 60000); // Check every 60 seconds
  
  console.log('✅ Database health monitoring started');
};

// Initialize databases function
const initializeDatabases = async () => {
  try {
    console.log('🚀 Initializing databases...');
    
    // Update remote URL from settings
    try {
      updateRemoteUrl();
    } catch (error) {
      console.error('❌ Error updating remote URL:', error);
    }
    
    // Check connection
    await checkRemoteConnection();
    
    // Start change handlers
    startChangeHandlers().catch(error => {
      console.error('❌ Error starting change handlers:', error);
    });
    
    // Start health monitoring after 30 seconds
    setTimeout(() => {
      try {
        startDatabaseHealthCheck();
      } catch (error) {
        console.error('❌ Error starting health check:', error);
      }
    }, 30000);
    
    console.log('✅ Database initialization completed');
    return true;
  } catch (error) {
    console.error('❌ Database initialization failed:', error);
    return false;
  }
}

export default boot(({ app }) => {
  console.log('🚀 Initializing PouchDB boot...');
  
  try {
    // Start the database initialization in the background
    setTimeout(() => {
      console.log('⏰ Starting database initialization...');
      initializeDatabases().catch(err => {
        console.error('❌ Database initialization failed:', err);
      });
    }, 100); // Short timeout to ensure app UI is initialized first
  } catch (error) {
    console.error('❌ Boot error:', error);
  }
  
  console.log('✅ PouchDB boot completed');
})

// New function to diagnose CouchDB connection issues
const diagnoseCouchDbConnection = async (): Promise<object> => {
  console.log('🔍 Running CouchDB connection diagnostic...');
  
  const diagnosticResults: any = {
    serverInfo: null,
    authStatus: null,
    databasesAccessible: {},
    errors: []
  };
  
  try {
    // Get base URL without credentials for safe logging
    const urlParts = currentRemoteUrl.value.split('@');
    const safeUrl = urlParts.length > 1 
      ? `http://${urlParts[1]}` 
      : currentRemoteUrl.value;
    
    console.log(`🔗 Testing connection to CouchDB at ${safeUrl}`);
    
    // 1. Try to access server info
    try {
      const response = await fetch(`${currentRemoteUrl.value}/`);
      
      if (response.ok) {
        const info = await response.json();
        diagnosticResults.serverInfo = {
          version: info.version,
          vendor: info.vendor,
          features: info.features
        };
        console.log('✅ CouchDB server accessible:', diagnosticResults.serverInfo);
      } else {
        console.error(`❌ CouchDB server returned ${response.status}`);
        diagnosticResults.errors.push(`Server returned ${response.status}`);
      }
    } catch (error: any) {
      console.error('❌ Failed to connect to CouchDB server:', error.message);
      diagnosticResults.errors.push(`Connection error: ${error.message}`);
    }
    
    // 2. Test authentication
    try {
      const response = await fetch(`${currentRemoteUrl.value}/_session`);
      
      if (response.ok) {
        const session = await response.json();
        diagnosticResults.authStatus = {
          authenticated: session.userCtx && session.userCtx.name !== null,
          username: session.userCtx ? session.userCtx.name : 'anonymous',
          roles: session.userCtx ? session.userCtx.roles : []
        };
        console.log('✅ Authentication check:', diagnosticResults.authStatus);
      } else {
        console.error(`❌ Authentication check failed: ${response.status}`);
        diagnosticResults.errors.push(`Auth check failed: ${response.status}`);
      }
    } catch (error: any) {
      console.error('❌ Failed to check authentication:', error.message);
      diagnosticResults.errors.push(`Auth error: ${error.message}`);
    }
    
    // 3. Check each database
    for (const dbName of Object.keys(remoteDbs)) {
      try {
        const remoteDb = new PouchDB(`${currentRemoteUrl.value}/${dbName}`);
        const info = await remoteDb.info();
        diagnosticResults.databasesAccessible[dbName] = {
          accessible: true,
          docCount: info.doc_count,
          updateSeq: info.update_seq
        };
        console.log(`✅ Database ${dbName} accessible`);
      } catch (error: any) {
        diagnosticResults.databasesAccessible[dbName] = {
          accessible: false,
          error: error.status || error.message
        };
        console.error(`❌ Database ${dbName} not accessible:`, error.message);
      }
    }
    
    return diagnosticResults;
  } catch (error: any) {
    console.error('❌ Diagnostic failed:', error);
    diagnosticResults.errors.push(`Diagnostic error: ${error.message}`);
    return diagnosticResults;
  }
};

export { 
    remoteDbs,
    checkRemoteConnection,
    diagnoseCouchDbConnection,
    getDatabaseStatus,
    addTransaction,
    addTransactionAttachment,
    getTransactionAttachment,
    // Petugas functions
    addPetugas,
    updatePetugas,
    deletePetugas,
    getAllPetugas,
    getPetugasByUsername,
    // Kendaraan functions
    addJenisKendaraan,
    updateJenisKendaraan,
    deleteJenisKendaraan,
    getAllJenisKendaraan,
    // Blacklist functions
    addToBlacklist,
    removeFromBlacklist,
    getAllBlacklist,
    checkBlacklist,
    // Level functions
    addLevel,
    getAllLevels,
    // Tarif functions
    createTarif,
    updateTarif,
    deleteTarif,
    getAllTarif,
    getTarifByMobil,
    getTarifByJamKe,
    getAllTarifInap,
    getTarifInapByMobil,
    getAllTarifMember,
    getTarifMemberByMobil,
    getAllTarifStiker,
    getTarifStikerByMobil,
    calculateParkingFeeFromDB,
    restartChangeHandler,
    startChangeHandlers,
    changeHandlers,
    // CouchDB configuration functions
    updateRemoteUrl,
    reinitializeRemoteDatabases,
    currentRemoteUrl,
    // Status monitoring
    isConnected,
    lastChangeStatus,
    lastChangeError
}

// Utility functions for Petugas Store
const addPetugas = async (petugas: any) => {
  try {
    const response = await remoteDbs.petugas.put(petugas);
    return response;
  } catch (err) {
    console.error('Error adding petugas:', err);
    throw err;
  }
};

const updatePetugas = async (petugas: any) => {
  try {
    const response = await remoteDbs.petugas.put(petugas);
    return response;
  } catch (err) {
    console.error('Error updating petugas:', err);
    throw err;
  }
};

const deletePetugas = async (id: string) => {
  try {
    const doc = await remoteDbs.petugas.get(id);
    const response = await remoteDbs.petugas.remove(doc);
    return response;
  } catch (err) {
    console.error('Error deleting petugas:', err);
    throw err;
  }
};

const getAllPetugas = async () => {
  try {
    const result = await remoteDbs.petugas.allDocs({
      include_docs: true,
      startkey: 'petugas_',
      endkey: 'petugas_\ufff0'
    });
    return result.rows.map((row: any) => row.doc);
  } catch (err) {
    console.error('Error getting all petugas:', err);
    throw err;
  }
};

const getPetugasByUsername = async (username: string) => {
  try {
    const result = await remoteDbs.petugas.find({
      selector: { type: 'petugas', username: username }
    });
    return result.docs[0] || null;
  } catch (err) {
    console.error('Error getting petugas by username:', err);
    throw err;
  }
};

// Utility functions for Kendaraan Store
const addJenisKendaraan = async (jenisKendaraan: any) => {
  try {
    const response = await remoteDbs.kendaraan.put(jenisKendaraan);
    return response;
  } catch (err) {
    console.error('Error adding jenis kendaraan:', err);
    throw err;
  }
};

const updateJenisKendaraan = async (jenisKendaraan: any) => {
  try {
    const response = await remoteDbs.kendaraan.put(jenisKendaraan);
    return response;
  } catch (err) {
    console.error('Error updating jenis kendaraan:', err);
    throw err;
  }
};

const deleteJenisKendaraan = async (id: string) => {
  try {
    const doc = await remoteDbs.kendaraan.get(id);
    const response = await remoteDbs.kendaraan.remove(doc);
    return response;
  } catch (err) {
    console.error('Error deleting jenis kendaraan:', err);
    throw err;
  }
};

const getAllJenisKendaraan = async () => {
  try {
    const result = await remoteDbs.kendaraan.allDocs({
      include_docs: true,
      startkey: 'jenis_kendaraan_',
      endkey: 'jenis_kendaraan_\ufff0'
    });
    return result.rows.map((row: any) => row.doc);
  } catch (err) {
    console.error('Error getting all jenis kendaraan:', err);
    throw err;
  }
};

// Utility functions for Blacklist
const addToBlacklist = async (blacklistItem: any) => {
  try {
    const response = await remoteDbs.blacklist.put(blacklistItem);
    return response;
  } catch (err) {
    console.error('Error adding to blacklist:', err);
    throw err;
  }
};

const removeFromBlacklist = async (id: string) => {
  try {
    const doc = await remoteDbs.blacklist.get(id);
    const response = await remoteDbs.blacklist.remove(doc);
    return response;
  } catch (err) {
    console.error('Error removing from blacklist:', err);
    throw err;
  }
};

const getAllBlacklist = async () => {
  try {
    const result = await remoteDbs.blacklist.allDocs({
      include_docs: true,
      startkey: 'blacklist_',
      endkey: 'blacklist_\ufff0'
    });
    return result.rows.map((row: any) => row.doc);
  } catch (err) {
    console.error('Error getting all blacklist:', err);
    throw err;
  }
};

const checkBlacklist = async (noPol: string) => {
  try {
    const result = await remoteDbs.blacklist.find({
      selector: { type: 'blacklist_kendaraan', no_pol: noPol.toUpperCase(), status: 1 }
    });
    return result.docs.length > 0;
  } catch (err) {
    console.error('Error checking blacklist:', err);
    return false;
  }
};

// Utility functions for Levels
const addLevel = async (level: any) => {
  try {
    const response = await remoteDbs.levels.put(level);
    return response;
  } catch (err) {
    console.error('Error adding level:', err);
    throw err;
  }
};

const getAllLevels = async () => {
  try {
    const result = await remoteDbs.levels.allDocs({
      include_docs: true,
      startkey: 'level_',
      endkey: 'level_\ufff0'
    });
    return result.rows.map((row: any) => row.doc);
  } catch (err) {
    console.error('Error getting all levels:', err);
    throw err;
  }
};

// ===========================================
// TARIF UTILITY FUNCTIONS
// ===========================================

const createTarif = async (tarif: any) => {
  try {
    const response = await remoteDbs.tarif.put(tarif);
    return response;
  } catch (err) {
    console.error('Error creating tarif:', err);
    throw err;
  }
};

const updateTarif = async (tarif: any) => {
  try {
    const response = await remoteDbs.tarif.put(tarif);
    return response;
  } catch (err) {
    console.error('Error updating tarif:', err);
    throw err;
  }
};

const deleteTarif = async (id: string) => {
  try {
    const doc = await remoteDbs.tarif.get(id);
    const response = await remoteDbs.tarif.remove(doc);
    return response;
  } catch (err) {
    console.error('Error deleting tarif:', err);
    throw err;
  }
};

const getAllTarif = async () => {
  try {
    const result = await remoteDbs.tarif.allDocs({
      include_docs: true,
      startkey: 'tarif_',
      endkey: 'tarif_\ufff0'
    });
    return result.rows.map((row: any) => row.doc);
  } catch (err) {
    console.error('Error getting all tarif:', err);
    throw err;
  }
};

const getTarifByMobil = async (idMobil: string) => {
  try {
    const result = await remoteDbs.tarif.query('tarif/by_id_mobil', {
      key: idMobil,
      include_docs: true
    });
    return result.rows.map((row: any) => row.doc);
  } catch (err) {
    console.error('Error getting tarif by mobil:', err);
    throw err;
  }
};

const getTarifByJamKe = async (idMobil: string, jamKe: number) => {
  try {
    const result = await remoteDbs.tarif.query('tarif/by_jam_ke', {
      key: [idMobil, jamKe],
      include_docs: true
    });
    return result.rows.map((row: any) => row.doc);
  } catch (err) {
    console.error('Error getting tarif by jam ke:', err);
    throw err;
  }
};

const getAllTarifInap = async () => {
  try {
    const result = await remoteDbs.tarif.allDocs({
      include_docs: true,
      startkey: 'tarif_inap_',
      endkey: 'tarif_inap_\ufff0'
    });
    return result.rows.map((row: any) => row.doc);
  } catch (err) {
    console.error('Error getting all tarif inap:', err);
    throw err;
  }
};

const getTarifInapByMobil = async (idMobil: string) => {
  try {
    const result = await remoteDbs.tarif.query('tarif/tarif_inap_by_mobil', {
      key: idMobil,
      include_docs: true
    });
    return result.rows.map((row: any) => row.doc);
  } catch (err) {
    console.error('Error getting tarif inap by mobil:', err);
    throw err;
  }
};

const getAllTarifMember = async () => {
  try {
    const result = await remoteDbs.tarif.allDocs({
      include_docs: true,
      startkey: 'tarif_member_',
      endkey: 'tarif_member_\ufff0'
    });
    return result.rows.map((row: any) => row.doc);
  } catch (err) {
    console.error('Error getting all tarif member:', err);
    throw err;
  }
};

const getTarifMemberByMobil = async (idMobil: string) => {
  try {
    const result = await remoteDbs.tarif.query('tarif/tarif_member_by_mobil', {
      key: idMobil,
      include_docs: true
    });
    return result.rows.map((row: any) => row.doc);
  } catch (err) {
    console.error('Error getting tarif member by mobil:', err);
    throw err;
  }
};

const getAllTarifStiker = async () => {
  try {
    const result = await remoteDbs.tarif.allDocs({
      include_docs: true,
      startkey: 'tarif_stiker_',
      endkey: 'tarif_stiker_\ufff0'
    });
    return result.rows.map((row: any) => row.doc);
  } catch (err) {
    console.error('Error getting all tarif stiker:', err);
    throw err;
  }
};

const getTarifStikerByMobil = async (idMobil: string) => {
  try {
    const result = await remoteDbs.tarif.query('tarif/tarif_stiker_by_mobil', {
      key: idMobil,
      include_docs: true
    });
    return result.rows.map((row: any) => row.doc);
  } catch (err) {
    console.error('Error getting tarif stiker by mobil:', err);
    throw err;
  }
};

const calculateParkingFeeFromDB = async (idMobil: string, jamMasuk: Date, jamKeluar: Date = new Date()) => {
  try {
    const hoursDiff = Math.ceil((jamKeluar.getTime() - jamMasuk.getTime()) / (1000 * 60 * 60));
    const hours = Math.max(1, hoursDiff);

    // Get regular tariffs
    const tarifList = await getTarifByMobil(idMobil);
    const activeTarifs = tarifList
      .filter((t: any) => t.status === 1)
      .sort((a: any, b: any) => a.jam_ke - b.jam_ke);

    if (activeTarifs.length === 0) {
      return { totalFee: 0, details: [], isInap: false };
    }

    // Check if it's overnight parking
    const jamMasukHour = jamMasuk.getHours();
    const jamKeluarHour = jamKeluar.getHours();
    const isInap = (jamMasukHour >= 22 || jamMasukHour <= 6) || 
                   (jamKeluarHour >= 22 || jamKeluarHour <= 6) ||
                   hours > 12;

    if (isInap) {
      const tarifInapList = await getTarifInapByMobil(idMobil);
      const activeTarifInap = tarifInapList.find((t: any) => t.status === 1);
      
      if (activeTarifInap) {
        return {
          totalFee: (activeTarifInap as any).tarif_inap,
          details: [{ jam_ke: 1, tarif: (activeTarifInap as any).tarif_inap }],
          isInap: true,
          tarifInap: (activeTarifInap as any).tarif_inap
        };
      }
    }

    // Calculate regular tariff
    const details: Array<{jam_ke: number; tarif: number}> = [];
    let totalFee = 0;

    for (let i = 1; i <= hours; i++) {
      const tarif = activeTarifs.find((t: any) => t.jam_ke === i) || activeTarifs[activeTarifs.length - 1];
      if (tarif) {
        details.push({ jam_ke: i, tarif: (tarif as any).tarif });
        totalFee += (tarif as any).tarif;
      }
    }

    return { totalFee, details, isInap: false };
  } catch (err) {
    console.error('Error calculating parking fee:', err);
    return { totalFee: 0, details: [], isInap: false };
  }
};

// Design document initialization for new databases
const initializeDesignDocs = async () => {
  // Petugas design docs
  const petugasDesignDoc = {
    _id: '_design/petugas',
    views: {
      by_username: {
        map: `function (doc) {
          if (doc.type === 'petugas') {
            emit(doc.username, doc);
          }
        }`
      },
      by_level: {
        map: `function (doc) {
          if (doc.type === 'petugas') {
            emit(doc.level_code, doc);
          }
        }`
      },
      by_status: {
        map: `function (doc) {
          if (doc.type === 'petugas') {
            emit(doc.status, doc);
          }
        }`
      }
    }
  };

  // Kendaraan design docs
  const kendaraanDesignDoc = {
    _id: '_design/kendaraan',
    views: {
      jenis_by_status: {
        map: `function (doc) {
          if (doc.type === 'jenis_kendaraan') {
            emit(doc.status, doc);
          }
        }`
      },
      blacklist_by_nopol: {
        map: `function (doc) {
          if (doc.type === 'blacklist_kendaraan') {
            emit(doc.no_pol, doc);
          }
        }`
      },
      tarif_by_jenis: {
        map: `function (doc) {
          if (doc.type === 'tarif_parkir') {
            emit(doc.id_jenis_kendaraan, doc);
          }
        }`
      }
    }
  };

  // Tarif design docs
  const tarifDesignDoc = {
    _id: '_design/tarif',
    views: {
      by_id_mobil: {
        map: `function (doc) {
          if (doc.type === 'tarif') {
            emit(doc.id_mobil, doc);
          }
        }`
      },
      by_jam_ke: {
        map: `function (doc) {
          if (doc.type === 'tarif') {
            emit([doc.id_mobil, doc.jam_ke], doc);
          }
        }`
      },
      by_status: {
        map: `function (doc) {
          if (doc.type === 'tarif') {
            emit(doc.status, doc);
          }
        }`
      },
      tarif_inap_by_mobil: {
        map: `function (doc) {
          if (doc.type === 'tarif_inap') {
            emit(doc.id_mobil, doc);
          }
        }`
      },
      tarif_member_by_mobil: {
        map: `function (doc) {
          if (doc.type === 'tarif_member') {
            emit(doc.id_mobil, doc);
          }
        }`
      },
      tarif_stiker_by_mobil: {
        map: `function (doc) {
          if (doc.type === 'tarif_stiker') {
            emit(doc.id_mobil, doc);
          }
        }`
      }
    }
  };

  try {
    await remoteDbs.petugas.put(petugasDesignDoc);
    await remoteDbs.kendaraan.put(kendaraanDesignDoc);
    await remoteDbs.tarif.put(tarifDesignDoc);
  } catch (err: any) {
    if (err.name !== 'conflict') {
      console.error('Error initializing design docs:', err);
    }
  }
};

