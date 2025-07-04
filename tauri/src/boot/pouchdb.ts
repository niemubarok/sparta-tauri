// if (typeof window !== 'undefined') {
//   (window as any).global = window;
//   (window as any).process = {
//     env: { DEBUG: undefined }
//   };

// }

import PouchDB from 'pouchdb-browser'
import PouchFind from 'pouchdb-find'
import { boot } from 'quasar/wrappers'
import { Notify } from 'quasar'
import ls from 'localstorage-slim'
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

// Local databases
const localDbs: DatabaseTypes = {
  transactions: new PouchDB('transactions'),
  users: new PouchDB('users'),
  vehicles: new PouchDB('vehicles'),
  tariffs: new PouchDB('tariffs'),
  config: new PouchDB('config'),
  members: new PouchDB('members'),
  membershipTypes: new PouchDB('membership_types'),
  // New databases for store integration
  petugas: new PouchDB('petugas'),
  kendaraan: new PouchDB('kendaraan'),
  levels: new PouchDB('levels'),
  blacklist: new PouchDB('blacklist'),
  tarif: new PouchDB('tarif')
}

const createIndexes = async () => {
  await Promise.all([
    localDbs.transactions.createIndex({
      index: { fields: ['type', 'plate_number', 'status'] }
    }),
    localDbs.members.createIndex({
      index: { fields: ['member_id', 'status'] }
    }),
    localDbs.vehicles.createIndex({
      index: { fields: ['type', 'vehicle_id'] }
    }),
    // New indexes for store integration
    localDbs.petugas.createIndex({
      index: { fields: ['type', 'username', 'status'] }
    }),
    localDbs.kendaraan.createIndex({
      index: { fields: ['type', 'jenis', 'status'] }
    }),
    localDbs.blacklist.createIndex({
      index: { fields: ['type', 'no_pol', 'status'] }
    }),
    localDbs.tarif.createIndex({
      index: { fields: ['type', 'id_jenis_kendaraan', 'status'] }
    })
  ])
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
    // console.log('🔄 Remote databases reinitialized with new URL')
    
    // Restart sync after URL change (using the full implementation defined below)
    setTimeout(() => {
      // console.log('🔄 Starting delayed sync after URL change...');
      // Use the function instead of duplicating code
      restartSyncInitialization().catch(err => {
        // console.error('❌ Error restarting sync after URL change:', err);
      });
    }, 1000);
  } catch (error) {
    // console.error('❌ Error reinitializing remote databases:', error);
    // console.warn('⚠️ Application will continue with previous remote configuration');
  }
}

// Sync options
const syncOpts = {
  live: true,
  retry: true,
}

import { ref } from 'vue';

// Map untuk tracking active sync handlers
const activeSyncHandlers = new Map();

// Reactive state for sync status
const isSyncing = ref(false);
const lastSyncStatus = ref<'active' | 'paused' | 'denied' | 'error' | 'complete'>('paused');
const lastSyncError = ref<any>(null);

// Start sync for all databases
const syncDatabases = async (): Promise<void> => {
  // console.log('🔄 Starting live sync for all databases...');
  const dbNames = Object.keys(localDbs);
  let successCount = 0;
  let failCount = 0;
  
  try {
    for (const dbName of dbNames) {
      // console.log(`🔗 Setting up live sync for ${dbName}...`);
      try {
        // Use the new setupSyncHandler function
        const sync = await setupSyncHandler(
          currentRemoteUrl.value.replace(/\/+$/, ''),
          dbName,
          localDbs[dbName as keyof typeof localDbs]
        );
        if (sync) {
          activeSyncHandlers.set(dbName, sync);
          // console.log(`✅ Sync handler created for ${dbName}`);
          successCount++;
        } else {
          // console.warn(`⚠️ Sync handler not created for ${dbName}`);
          failCount++;
        }
      } catch (error) {
        // console.error(`❌ Failed to setup sync for ${dbName}:`, error);
        failCount++;
      }
    }
    // console.log(`🔄 Sync setup completed: ${successCount} successful, ${failCount} failed (out of ${dbNames.length} databases)`);
  } catch (error) {
    // console.error('💥 Critical error in syncDatabases:', error);
    // console.warn('⚠️ Sync setup may be incomplete, but application will continue');
  }
}

// Function to ensure remote database exists with enhanced error handling
async function ensureRemoteDatabase(url: string, dbName: string): Promise<boolean> {
  try {
    // console.log(`🔍 Checking if remote database ${dbName} exists at ${url}`);
    
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
    
    // console.log(`🔐 Using explicit auth options for ${dbName}`);
  }
  
  try {
    // Try to access the database
    const remoteDb = new PouchDB(remoteDbUrl, options);
    const info = await remoteDb.info();
    // console.log(`✅ Remote database ${dbName} is accessible:`, {
    //   db_name: info.db_name,
    //   doc_count: info.doc_count,
    //   update_seq: info.update_seq
    // });
    return true;
  } catch (error: any) {
    // console.warn(`⚠️ Remote database ${dbName} not accessible:`, error.message);
    // console.warn(`📝 Error details:`, {
    //   status: error.status,
    //   name: error.name,
    //   reason: error.reason || 'Unknown reason'
    // });
    
    // If it's a 404, try to create the database
    if (error.status === 404 || error.message.includes('not found')) {
      try {
        // console.log(`🏗️ Creating remote database ${dbName}...`);
        const remoteDb = new PouchDB(remoteDbUrl, options);
        await remoteDb.put({
          _id: '_design/init',
          views: {
            all: {
              map: 'function (doc) { emit(doc._id, 1); }'
            }
          }
        });
        // console.log(`✅ Remote database ${dbName} created successfully`);
        return true;
      } catch (createError: any) {
        // console.error(`❌ Failed to create remote database ${dbName}:`, createError.message);
        // console.error('📝 Creation error details:', {
        //   status: createError.status,
        //   name: createError.name,
        //   reason: createError.reason || 'Unknown reason'
        // });
        return false;
      }
    }
    
    // Check for authentication errors
    if (error.status === 401 || error.status === 403) {
      // console.error(`🔒 Authentication failure for ${dbName}. Check your credentials.`);
    }
    
    // Check for server errors
    if (error.status === 500) {
      // console.error(`🚨 Server error when accessing ${dbName}. CouchDB might be misconfigured or overloaded.`);
      // Try to access CouchDB root to check if server is responsive
      try {
        const rootUrl = url.split('/').slice(0, 3).join('/');
        // console.log(`🔍 Attempting to access CouchDB root at ${rootUrl}...`);
        const response = await fetch(rootUrl);
        if (response.ok) {
          // console.log(`✅ CouchDB server is responsive at ${rootUrl}`);
        } else {
          // console.error(`❌ CouchDB server returned ${response.status} at ${rootUrl}`);
        }
      } catch (rootError) {
        // console.error(`❌ Could not connect to CouchDB root:`, rootError);
      }
    }
    
    return false;
  }
  } catch (error) {
    // console.error(`❌ Unexpected error checking remote database ${dbName}:`, error);
    return false;
  }
}

// Function to setup sync handler with authorization - based on user's pattern
async function setupSyncHandler(url: string, dbName: string, dbInstance: PouchDB.Database) {
  try {
    // First ensure the remote database exists
    const dbExists = await ensureRemoteDatabase(url, dbName);
    if (!dbExists) {
      // console.warn(`⚠️ Skipping sync for ${dbName} - remote database not available`);
      return null;
    }
  } catch (error) {
    // console.error(`❌ Error checking remote database ${dbName}:`, error);
    // console.warn(`⚠️ Skipping sync for ${dbName} due to error check failure`);
    return null;
  }

  // Parse URL to get authentication components if they exist
  let syncUrl = `${url}/${dbName}`;
  let authHeaders = {};
  
  // If URL already has credentials, don't add extra auth headers
  if (!url.includes('@')) {
    // Use basic auth instead of Bearer token if no credentials in URL
    const DB_USER = process.env.DB_USER || 'admin';
    const DB_PASSWORD = process.env.DB_PASSWORD || 'admin';
    authHeaders = {
      Authorization: `Basic ${btoa(`${DB_USER}:${DB_PASSWORD}`)}`,
    };
    // console.log(`🔐 Using basic auth for ${dbName} sync`);
  } else {
    // console.log(`🔐 Using URL embedded credentials for ${dbName} sync`);
  }
  
  const syncHandler = dbInstance.sync(syncUrl, {
    live: true,
    retry: true,
    // @ts-ignore - PouchDB types might not include all auth options
    headers: authHeaders,
    // @ts-ignore - PouchDB types might not include all options
    credentials: "include",
    heartbeat: 5000,
    ajax: {
      timeout: 30000, // Increase timeout to 30 seconds
      withCredentials: false // Set to false if using Basic Auth headers
    }
  } as any);

  const isFirstVisit = !ls.get("hasVisitedBefore");

  syncHandler
    .on("change", (info) => {
      if (dbName === process.env.COUCHDB_MASTER) {
        if (info.direction === "pull" && !isFirstVisit) {
          Notify.create({
            type: "negative",
            message: `Ada Perubahan Data Master Silahkan Refresh Halaman`,
            position: "top",
            color: "negative",
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
      }
      
      // console.log(`📊 Live sync change for ${dbName}:`, {
      //   direction: info.direction,
      //   docsWritten: info.change?.docs_written || 0
      // });
      isSyncing.value = true;
      lastSyncStatus.value = 'active';
    })
    .on("paused", (err: any) => {
      // console.log(`⏸️ Live sync paused for ${dbName}:`, (err && typeof err === 'object' && 'message' in err) ? err.message : 'normal pause');
      isSyncing.value = false;
      lastSyncStatus.value = 'paused';
      if (err) {
        lastSyncError.value = err;
        // Only auto-restart if it's not a critical error
        if (err.status !== 404 && err.status !== 500) {
          setTimeout(() => {
            // console.log(`🔄 Auto-restarting sync for ${dbName}...`);
            syncSingleDatabase(dbName);
          }, 15000);
        }
      }
    })
    .on("active", () => {
      // console.log(`🔄 Live sync active for ${dbName}`);
      isSyncing.value = true;
      lastSyncStatus.value = 'active';
      lastSyncError.value = null;
    })
    .on("error", (err: any) => {
      // console.error(`❌ Live sync error for ${dbName}:`, err);
      // console.error(`🔍 Detailed error info:`, {
        status: err.status,
      //   name: err.name,
      //   message: err.message,
      //   reason: err.reason || 'Unknown reason'
      // });
      
      isSyncing.value = false;
      lastSyncStatus.value = 'error';
      lastSyncError.value = err;
      
      // Special handling for auth errors
      if (err.status === 401 || err.status === 403) {
        // console.warn(`🔒 Authentication error detected for ${dbName}, attempting to reconnect with different auth...`);
        
        // Try to reinitialize with updated credentials after a short delay
        setTimeout(() => {
          // console.log(`🔄 Reinitializing remote databases with updated auth...`);
          reinitializeRemoteDatabases();
        }, 10000);
        
        return;
      }
      
      // Only auto-restart if it's not a critical error (404, 500)
      if (err.status !== 404 && err.status !== 500) {
        setTimeout(() => {
          // console.log(`🔄 Auto-restarting sync for ${dbName} after error...`);
          syncSingleDatabase(dbName);
        }, 20000);
      } else {
        // console.log(`🚫 Not restarting sync for ${dbName} due to critical error (${err.status})`);
        
        // For 500 errors, try a different approach after a longer delay
        if (err.status === 500) {
          setTimeout(() => {
            // console.log(`🔄 Attempting special recovery for ${dbName} after 500 error...`);
            // Try to access the database directly to check what's happening
            new PouchDB(`${url}/${dbName}`).info()
              .then(info => {
                // console.log(`✅ Database ${dbName} is actually accessible:`, info);
                syncSingleDatabase(dbName);
              })
              .catch(checkError => {
              //
              });
          }, 30000);
        }
      }
    });

  return syncHandler;
}

// Fungsi untuk restart single database sync - definisikan dulu sebelum digunakan
const syncSingleDatabase = async (dbName: string) => {
  try {
    // Cancel existing sync handler
    const existingSync = activeSyncHandlers.get(dbName);
    if (existingSync) {
  //
      existingSync.cancel();
      activeSyncHandlers.delete(dbName);
    }
    
  //
    
    // Use the new setupSyncHandler function
    const sync = await setupSyncHandler(
      currentRemoteUrl.value.replace(/\/+$/, ''), // Remove trailing slashes
      dbName,
      localDbs[dbName as keyof typeof localDbs]
    );
    
    if (sync) {
      activeSyncHandlers.set(dbName, sync);
  //
    } else {
  //
    }
    
  } catch (error) {
  //
    // Retry setelah delay
    setTimeout(() => {
  //
      syncSingleDatabase(dbName);
    }, 10000);
  }
};


/**
 * Force immediate manual sync for all databases
 * Useful for troubleshooting sync issues
 */
const forceSyncAllDatabases = async (): Promise<void> => {
  console.log('🔄 Starting forced sync for all databases...');
  
  // Update sync status
  isSyncing.value = true;
  lastSyncStatus.value = 'active';
  lastSyncError.value = null;
  
  const syncPromises = Object.keys(localDbs).map(dbName => {
    return new Promise((resolve, reject) => {
      console.log(`🔄 Forcing sync for ${dbName}...`);
      
      const sync = localDbs[dbName as keyof typeof localDbs].sync(
        remoteDbs[dbName as keyof typeof remoteDbs], 
        {
          timeout: 30000, // 30 second timeout
          retry: true,    // Enable retry for manual sync
          batch_size: 50  // Reasonable batch size
        }
      );
      
      let completed = false;
      
      sync.on('complete', (info) => {
        if (!completed) {
          completed = true;
          console.log(`✅ Forced sync completed for ${dbName}:`, info);
          resolve(info);
        }
      });
      
      sync.on('error', (err) => {
        if (!completed) {
          completed = true;
          console.error(`❌ Forced sync failed for ${dbName}:`, err);
          reject(err);
        }
      });
      
      sync.on('change', (info) => {
        console.log(`🔄 Sync progress for ${dbName}:`, {
          direction: info.direction,
          docsWritten: info.change?.docs_written || 0
        });
      });
      
      // Timeout handler
      setTimeout(() => {
        if (!completed) {
          completed = true;
          const timeoutError = new Error(`Sync timeout for ${dbName} after 30 seconds`);
          console.error('⏰ Sync timeout:', timeoutError);
          sync.cancel();
          reject(timeoutError);
        }
      }, 30000);
    });
  });
  
  try {
    const results = await Promise.allSettled(syncPromises);
    const successful = results.filter(r => r.status === 'fulfilled').length;
    const failed = results.filter(r => r.status === 'rejected').length;
    
    console.log(`✅ Forced sync completed: ${successful} successful, ${failed} failed`);
    
    // Update sync status based on results
    if (failed === 0) {
      isSyncing.value = false;
      lastSyncStatus.value = 'complete';
    } else {
      isSyncing.value = false;
      lastSyncStatus.value = 'error';
      lastSyncError.value = new Error(`${failed} databases failed to sync`);
    }
    
    // Log failed syncs
    results.forEach((result, index) => {
      if (result.status === 'rejected') {
        const dbName = Object.keys(localDbs)[index];
        console.error(`❌ ${dbName} sync failed:`, result.reason);
      }
    });
    
  } catch (error) {
    console.error('❌ Critical error in forced sync:', error);
    isSyncing.value = false;
    lastSyncStatus.value = 'error';
    lastSyncError.value = error;
    throw error;
  }
};

/**
 * Check if remote database is accessible
 */
const checkRemoteConnection = async (): Promise<boolean> => {
  try {
    console.log('🔗 Checking remote database connection...');
    const info = await remoteDbs.transactions.info();
    console.log('✅ Remote database accessible:', info.db_name);
    return true;
  } catch (error: any) {
    console.error('❌ Remote database not accessible:', error?.message || error);
    return false;
  }
};

/**
 * Enhanced function to sync and verify specific transaction with connection check
 */
const safeSyncTransaction = async (transactionId: string): Promise<boolean> => {
  try {
    console.log('🔄 Starting safe sync for transaction:', transactionId);
    
    // First check if remote is accessible
    const isConnected = await checkRemoteConnection();
    if (!isConnected) {
      console.warn('⚠️ Remote database not accessible, skipping sync');
      return false;
    }
    
    // Check if transaction exists locally
    const localDoc = await localDbs.transactions.get(transactionId);
    if (!localDoc) {
      console.error('❌ Transaction not found locally:', transactionId);
      return false;
    }
    
    // Try simple push replication first (most reliable)
    const pushResult = await new Promise((resolve, reject) => {
      const replication = localDbs.transactions.replicate.to(remoteDbs.transactions, {
        timeout: 20000,
        retry: false,
        batch_size: 1,
        filter: (doc: any) => doc._id === transactionId
      });
      
      let completed = false;
      
      replication.on('complete', (info) => {
        if (!completed) {
          completed = true;
          console.log('✅ Push replication completed:', info);
          resolve(info);
        }
      });
      
      replication.on('error', (err) => {
        if (!completed) {
          completed = true;
          console.error('❌ Push replication failed:', err);
          reject(err);
        }
      });
      
      // Timeout after 20 seconds
      setTimeout(() => {
        if (!completed) {
          completed = true;
          replication.cancel();
          reject(new Error('Push replication timeout'));
        }
      }, 20000);
    });
    
    // Verify the transaction exists in remote
    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for propagation
    const verified = await checkTransactionInRemote(transactionId);
    
    console.log(`🔍 Transaction ${transactionId} sync result:`, {
      pushed: !!pushResult,
      verified: verified
    });
    
    return verified;
  } catch (error) {
    console.error(`❌ Safe sync failed for transaction ${transactionId}:`, error);
    return false;
  }
};

/**
 * Force sync and verify specific transaction exists in remote
 */
const forceSyncAndVerifyTransaction = async (transactionId: string): Promise<boolean> => {
  try {
    console.log('🔍 Force syncing and verifying transaction:', transactionId);
    
    // First force sync the transaction
    await forceSyncSpecificTransaction(transactionId);
    
    // Wait a moment for sync to propagate
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Then verify it exists in remote
    const exists = await checkTransactionInRemote(transactionId);
    
    console.log(`🔍 Transaction ${transactionId} verification result:`, exists ? 'EXISTS' : 'NOT FOUND');
    
    return exists;
  } catch (error) {
    console.error(`❌ Error verifying transaction ${transactionId}:`, error);
    return false;
  }
};

/**
 * Get detailed sync status with database-specific information
 */
const getDetailedSyncStatus = () => {
  return {
    global: {
      isSyncing: isSyncing.value,
      lastSyncStatus: lastSyncStatus.value,
      lastSyncError: lastSyncError.value?.message || null
    },
    databases: Object.keys(localDbs).map(dbName => ({
      name: dbName,
      // Add individual database sync status if needed
      status: 'monitoring' // Placeholder - can be enhanced
    }))
  };
};

/**
 * Get sync status for monitoring
 */
const getSyncStatus = () => {
  return {
    isSyncing: isSyncing.value,
    lastSyncStatus: lastSyncStatus.value,
    lastSyncError: lastSyncError.value
  };
};

/**
 * Check if a specific transaction exists in remote database
 */
const checkTransactionInRemote = async (transactionId: string): Promise<boolean> => {
  try {
    await remoteDbs.transactions.get(transactionId);
    return true;
  } catch (error: any) {
    if (error?.status === 404) {
      return false; // Document not found
    }
    throw error; // Other errors
  }
};

/**
 * Force immediate manual sync for a specific transaction
 * Useful for ensuring critical transactions are synced immediately
 */
const forceSyncSpecificTransaction = async (transactionId: string): Promise<void> => {
  console.log('🔄 Starting forced sync for specific transaction:', transactionId);
  
  try {
    // Check if transaction exists locally first
    const exists = await localDbs.transactions.get(transactionId);
    if (!exists) {
      throw new Error(`Transaction ${transactionId} not found in local database`);
    }
    
    // Use a more aggressive sync configuration
    const sync = localDbs.transactions.sync(remoteDbs.transactions, {
      timeout: 60000, // Increase to 60 seconds
      retry: true,    // Enable retry for better reliability
      batch_size: 5,  // Small batch for faster processing
      checkpoint: false, // Disable checkpointing for immediate sync
      filter: (doc: any) => doc._id === transactionId // Only sync specific transaction
    });
    
    return new Promise((resolve, reject) => {
      let completed = false;
      let timeoutHandle: NodeJS.Timeout;
      
      const cleanup = () => {
        if (timeoutHandle) {
          clearTimeout(timeoutHandle);
        }
        try {
          sync.cancel();
        } catch (e) {
          // Ignore cancel errors
        }
      };
      
      sync.on('complete', (info) => {
        if (!completed) {
          completed = true;
          cleanup();
          console.log(`✅ Forced sync completed for transaction ${transactionId}:`, info);
          resolve();
        }
      });
      
      sync.on('error', (err) => {
        if (!completed) {
          completed = true;
          cleanup();
          console.error(`❌ Forced sync failed for transaction ${transactionId}:`, err);
          reject(err);
        }
      });
      
      sync.on('change', (info) => {
        console.log(`🔄 Forced sync progress for ${transactionId}:`, {
          direction: info.direction,
          docsWritten: info.change?.docs_written || 0
        });
      });
      
      sync.on('paused', (err) => {
        if (err) {
          console.warn(`⚠️ Forced sync paused with error for ${transactionId}:`, err);
        } else {
          console.log(`⏸️ Forced sync paused for ${transactionId} (normal)`);
        }
      });
      
      // Increased timeout handler
      timeoutHandle = setTimeout(() => {
        if (!completed) {
          completed = true;
          cleanup();
          const timeoutError = new Error(`Forced sync timeout for transaction ${transactionId} after 60 seconds`);
          console.error('⏰ Forced sync timeout:', timeoutError);
          reject(timeoutError);
        }
      }, 60000); // 60 seconds timeout
    });
  } catch (error) {
    console.error(`❌ Error in forced sync for transaction ${transactionId}:`, error);
    throw error;
  }
};

const addTransaction = async (transaction: any, immediateSync = false) => {
  try {
    const response = await localDbs.transactions.put(transaction);
    
    if (immediateSync) {
      // Update sync status immediately
      isSyncing.value = true;
      lastSyncStatus.value = 'active';
      lastSyncError.value = null;
      
      console.log('🔄 Triggering immediate sync for transaction:', response.id);
      
      // Create promise for immediate sync with optimized settings
      const syncPromise = new Promise((resolve, reject) => {
        const sync = localDbs.transactions.sync(remoteDbs.transactions, {
          timeout: 45000, // Increased to 45 seconds
          retry: true,    // Enable retry for better reliability
          batch_size: 5,  // Smaller batch for faster sync
          checkpoint: false, // Disable checkpointing for immediate sync
          filter: (doc: any) => doc._id === response.id // Only sync this transaction
        });
        
        let hasCompleted = false;
        let timeoutHandle: NodeJS.Timeout;
        
        const cleanup = () => {
          if (timeoutHandle) {
            clearTimeout(timeoutHandle);
          }
          try {
            sync.cancel();
          } catch (e) {
            // Ignore cancel errors
          }
        };
        
        sync.on('complete', (info) => {
          if (!hasCompleted) {
            hasCompleted = true;
            cleanup();
            isSyncing.value = false;
            lastSyncStatus.value = 'complete';
            
            console.log('✅ Immediate sync completed for transaction:', response.id, info);
            console.log('📊 Sync summary:', {
              transactionId: response.id,
              docsWritten: info.push?.docs_written || 0,
              docsRead: info.pull?.docs_written || 0,
              lastSeq: info.push?.last_seq
            });
            
            resolve(info);
          }
        });
        
        sync.on('error', (err: any) => {
          if (!hasCompleted) {
            hasCompleted = true;
            cleanup();
            isSyncing.value = false;
            lastSyncStatus.value = 'error';
            lastSyncError.value = err;
            
            console.error('❌ Immediate sync failed for transaction:', response.id, err);
            console.error('🔍 Sync error details:', {
              transactionId: response.id,
              error: err?.message || err,
              status: err?.status,
              reason: err?.reason,
              name: err?.name
            });
            
            // Try simpler push-only sync as fallback
            console.log('🔄 Attempting push-only fallback sync...');
            const pushSync = localDbs.transactions.replicate.to(remoteDbs.transactions, {
              timeout: 30000,
              retry: false,
              batch_size: 1,
              filter: (doc: any) => doc._id === response.id
            });
            
            pushSync.on('complete', (pushInfo) => {
              console.log('✅ Push-only fallback sync completed:', pushInfo);
              resolve({ fallback: 'push-only', info: pushInfo });
            });
            
            pushSync.on('error', (pushErr) => {
              console.error('❌ Push-only fallback also failed:', pushErr);
              reject(pushErr);
            });
          }
        });
        
        sync.on('change', (info) => {
          console.log('🔄 Immediate sync progress for transaction:', response.id, {
            direction: info.direction,
            docsWritten: info.change?.docs_written || 0
          });
        });
        
        sync.on('paused', (err) => {
          if (err) {
            console.warn('⚠️ Immediate sync paused with error:', err);
          } else {
            console.log('⏸️ Immediate sync paused (normal)');
          }
        });
        
        sync.on('active', () => {
          console.log('🔄 Immediate sync active for transaction:', response.id);
          isSyncing.value = true;
          lastSyncStatus.value = 'active';
        });
        
        // Set timeout for the entire sync operation
        timeoutHandle = setTimeout(() => {
          if (!hasCompleted) {
            hasCompleted = true;
            cleanup();
            isSyncing.value = false;
            lastSyncStatus.value = 'error';
            lastSyncError.value = new Error('Sync timeout after 45 seconds');
            
            console.warn('⏰ Immediate sync timeout for transaction:', response.id);
            
            // Final fallback - simple replication without waiting
            console.log('🔄 Starting background push as final fallback...');
            localDbs.transactions.replicate.to(remoteDbs.transactions, {
              timeout: 10000,
              retry: false,
              batch_size: 1,
              filter: (doc: any) => doc._id === response.id
            }).on('complete', (bgInfo) => {
              console.log('✅ Background push completed:', bgInfo);
            }).on('error', (bgErr) => {
              console.error('❌ Background push failed:', bgErr);
            });
            
            resolve({ timeout_fallback: true });
          }
        }, 45000);
      });
      
      // Start sync but don't block the main thread
      syncPromise.catch(error => {
        console.error('🔥 Immediate sync completely failed:', error);
        // Even if sync fails, the transaction is saved locally
        // Background sync will eventually pick it up
      });
    }
    
    return response;
  } catch (err) {
    console.error('Error adding transaction:', err);
    throw err;
  }
};

/**
 * Menyimpan attachment gambar ke dokumen transaksi.
 * @param transactionId ID dokumen transaksi
 * @param rev Revisi dokumen terakhir
 * @param attachmentName Nama attachment (misal: 'plate.jpg')
 * @param data Data gambar (base64 string tanpa prefix)
 * @param contentType Tipe konten (misal: 'image/jpeg')
 */
const addTransactionAttachment = async (
  transactionId: string,
  rev: string,
  attachmentName: string,
  data: string,
  contentType: string = 'image/jpeg'
) => {
  try {
    console.log('📎 Adding attachment:', {
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
    
    const response = await localDbs.transactions.putAttachment(
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
    console.error('📋 Attachment details:', {
      transactionId,
      attachmentName,
      dataLength: data?.length || 0,
      contentType,
      rev
    });
    throw err;
  }
};

// Fungsi untuk restart semua sync initialization seperti pertama kali buka
const restartSyncInitialization = async () => {
  console.log('🔄 Restarting sync initialization...');
  
  // 1. Cancel semua sync handlers yang aktif
  console.log('🛑 Cancelling all active sync handlers...');
  activeSyncHandlers.forEach((handler, dbName) => {
    try {
      handler.cancel();
      console.log(`✅ Cancelled sync for ${dbName}`);
    } catch (error) {
      console.log(`⚠️ Error cancelling sync for ${dbName}:`, error);
    }
  });
  
  // 2. Clear map handler
  activeSyncHandlers.clear();
  console.log('🧹 Cleared sync handlers map');
  
  // 3. Tunggu sebentar untuk ensure cancellation
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // 4. Restart sync untuk semua database
  console.log('🚀 Restarting sync for all databases...');
  await syncDatabases();
  
  console.log('✅ Sync initialization restarted successfully');
};

// Fungsi untuk health check dan auto-recovery  
const startSyncHealthCheck = () => {
  // console.log('🏥 Starting sync health monitoring...');
  
  // Jalankan health check setiap 45 detik
  setInterval(() => {
    // console.log('🔍 Checking sync health...');
    
    const dbNames = Object.keys(localDbs);
    
    dbNames.forEach(dbName => {
      const syncHandler = activeSyncHandlers.get(dbName);
      
      if (!syncHandler) {
        // console.log(`⚠️ Missing sync handler for ${dbName}, restarting...`);
        syncSingleDatabase(dbName);
        return;
      }
      
      // Check if sync handler is still active
      try {
        // Jika sync handler sudah cancelled atau error, restart
        if (syncHandler._destroyed || syncHandler._cancelled) {
          // console.log(`💀 Dead sync handler detected for ${dbName}, restarting...`);
          activeSyncHandlers.delete(dbName);
          syncSingleDatabase(dbName);
        }
      } catch (error) {
        // console.log(`🚨 Sync handler check failed for ${dbName}, restarting...`);
        activeSyncHandlers.delete(dbName);
        syncSingleDatabase(dbName);
      }
    });
  }, 45000); // Check setiap 45 detik
  
  // console.log('✅ Sync health monitoring started');
};


const initializeDatabases = async () => {
  try {
    // Create indexes but don't wait for it to complete
    createIndexes().catch(error => {
  //
    });
    
    // Initialize design docs but don't wait for it to complete
    initializeDesignDocs().catch(error => {
  //
    });
    
    // Update remote URL from settings before starting sync
    try {
      updateRemoteUrl();
    } catch (error) {
  //
    }
    
    // Start live sync but don't wait for it to complete
    syncDatabases().catch(error => {
  //
    });
    
    // Start health monitoring setelah 30 detik
    setTimeout(() => {
      try {
        startSyncHealthCheck();
      } catch (error) {
  //
      }
    }, 30000);
    
  //
    return true;
  } catch (error) {
  //
    return false;
  }
}

export default boot(({ app }) => {
  // No async/await here - this makes the boot function truly non-blocking
  //
  
  try {
    // Start the database initialization in the background
    setTimeout(() => {
  //
      initializeDatabases().catch(err => {
  //
      });
    }, 100); // Short timeout to ensure app UI is initialized first
  } catch (error) {
    // Catch any synchronous errors that might occur
  //
  }
  
  // Always proceed with app initialization
  //
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
    for (const dbName of Object.keys(localDbs)) {
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
    localDbs,
    remoteDbs, 
    syncDatabases,
    forceSyncAllDatabases, // Enhanced function for manual sync
    forceSyncSpecificTransaction, // Enhanced function for specific transaction sync
    forceSyncAndVerifyTransaction, // Function to sync and verify
    safeSyncTransaction, // New safe sync function with connection check
    checkRemoteConnection, // New function to check remote connection
    diagnoseCouchDbConnection, // New diagnostic function
    getSyncStatus,         // Basic sync monitoring
    getDetailedSyncStatus, // Detailed sync status
    checkTransactionInRemote, // Function for transaction verification
    isSyncing, // Export reactive sync status
    lastSyncStatus,
    lastSyncError,
    addTransaction, // Enhanced with better immediate sync and fallbacks
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
     syncSingleDatabase,        // Fungsi untuk restart individual sync
    startSyncHealthCheck,      // Fungsi untuk health monitoring
    restartSyncInitialization, // Fungsi untuk restart sync initialization
    activeSyncHandlers, 
    // CouchDB configuration functions
    updateRemoteUrl,           // Function to update remote URL from settings
    reinitializeRemoteDatabases, // Function to reinitialize remote databases
    currentRemoteUrl,          // Current remote URL ref
}

// Utility functions for Petugas Store
const addPetugas = async (petugas: any) => {
  try {
    const response = await localDbs.petugas.put(petugas);
    return response;
  } catch (err) {
    console.error('Error adding petugas:', err);
    throw err;
  }
};

const updatePetugas = async (petugas: any) => {
  try {
    const response = await localDbs.petugas.put(petugas);
    return response;
  } catch (err) {
    console.error('Error updating petugas:', err);
    throw err;
  }
};

const deletePetugas = async (id: string) => {
  try {
    const doc = await localDbs.petugas.get(id);
    const response = await localDbs.petugas.remove(doc);
    return response;
  } catch (err) {
    console.error('Error deleting petugas:', err);
    throw err;
  }
};

const getAllPetugas = async () => {
  try {
    const result = await localDbs.petugas.allDocs({
      include_docs: true,
      startkey: 'petugas_',
      endkey: 'petugas_\ufff0'
    });
    return result.rows.map(row => row.doc);
  } catch (err) {
    console.error('Error getting all petugas:', err);
    throw err;
  }
};

const getPetugasByUsername = async (username: string) => {
  try {
    const result = await localDbs.petugas.find({
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
    const response = await localDbs.kendaraan.put(jenisKendaraan);
    return response;
  } catch (err) {
    console.error('Error adding jenis kendaraan:', err);
    throw err;
  }
};

const updateJenisKendaraan = async (jenisKendaraan: any) => {
  try {
    const response = await localDbs.kendaraan.put(jenisKendaraan);
    return response;
  } catch (err) {
    console.error('Error updating jenis kendaraan:', err);
    throw err;
  }
};

const deleteJenisKendaraan = async (id: string) => {
  try {
    const doc = await localDbs.kendaraan.get(id);
    const response = await localDbs.kendaraan.remove(doc);
    return response;
  } catch (err) {
    console.error('Error deleting jenis kendaraan:', err);
    throw err;
  }
};

const getAllJenisKendaraan = async () => {
  try {
    const result = await localDbs.kendaraan.allDocs({
      include_docs: true,
      startkey: 'jenis_kendaraan_',
      endkey: 'jenis_kendaraan_\ufff0'
    });
    return result.rows.map(row => row.doc);
  } catch (err) {
    console.error('Error getting all jenis kendaraan:', err);
    throw err;
  }
};

// Utility functions for Blacklist
const addToBlacklist = async (blacklistItem: any) => {
  try {
    const response = await localDbs.blacklist.put(blacklistItem);
    return response;
  } catch (err) {
    console.error('Error adding to blacklist:', err);
    throw err;
  }
};

const removeFromBlacklist = async (id: string) => {
  try {
    const doc = await localDbs.blacklist.get(id);
    const response = await localDbs.blacklist.remove(doc);
    return response;
  } catch (err) {
    console.error('Error removing from blacklist:', err);
    throw err;
  }
};

const getAllBlacklist = async () => {
  try {
    const result = await localDbs.blacklist.allDocs({
      include_docs: true,
      startkey: 'blacklist_',
      endkey: 'blacklist_\ufff0'
    });
    return result.rows.map(row => row.doc);
  } catch (err) {
    console.error('Error getting all blacklist:', err);
    throw err;
  }
};

const checkBlacklist = async (noPol: string) => {
  try {
    const result = await localDbs.blacklist.find({
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
    const response = await localDbs.levels.put(level);
    return response;
  } catch (err) {
    console.error('Error adding level:', err);
    throw err;
  }
};

const getAllLevels = async () => {
  try {
    const result = await localDbs.levels.allDocs({
      include_docs: true,
      startkey: 'level_',
      endkey: 'level_\ufff0'
    });
    return result.rows.map(row => row.doc);
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
    const response = await localDbs.tarif.put(tarif);
    return response;
  } catch (err) {
    console.error('Error creating tarif:', err);
    throw err;
  }
};

const updateTarif = async (tarif: any) => {
  try {
    const response = await localDbs.tarif.put(tarif);
    return response;
  } catch (err) {
    console.error('Error updating tarif:', err);
    throw err;
  }
};

const deleteTarif = async (id: string) => {
  try {
    const doc = await localDbs.tarif.get(id);
    const response = await localDbs.tarif.remove(doc);
    return response;
  } catch (err) {
    console.error('Error deleting tarif:', err);
    throw err;
  }
};

const getAllTarif = async () => {
  try {
    const result = await localDbs.tarif.allDocs({
      include_docs: true,
      startkey: 'tarif_',
      endkey: 'tarif_\ufff0'
    });
    return result.rows.map(row => row.doc);
  } catch (err) {
    console.error('Error getting all tarif:', err);
    throw err;
  }
};

const getTarifByMobil = async (idMobil: string) => {
  try {
    const result = await localDbs.tarif.query('tarif/by_id_mobil', {
      key: idMobil,
      include_docs: true
    });
    return result.rows.map(row => row.doc);
  } catch (err) {
    console.error('Error getting tarif by mobil:', err);
    throw err;
  }
};

const getTarifByJamKe = async (idMobil: string, jamKe: number) => {
  try {
    const result = await localDbs.tarif.query('tarif/by_jam_ke', {
      key: [idMobil, jamKe],
      include_docs: true
    });
    return result.rows.map(row => row.doc);
  } catch (err) {
    console.error('Error getting tarif by jam ke:', err);
    throw err;
  }
};

const getAllTarifInap = async () => {
  try {
    const result = await localDbs.tarif.allDocs({
      include_docs: true,
      startkey: 'tarif_inap_',
      endkey: 'tarif_inap_\ufff0'
    });
    return result.rows.map(row => row.doc);
  } catch (err) {
    console.error('Error getting all tarif inap:', err);
    throw err;
  }
};

const getTarifInapByMobil = async (idMobil: string) => {
  try {
    const result = await localDbs.tarif.query('tarif/tarif_inap_by_mobil', {
      key: idMobil,
      include_docs: true
    });
    return result.rows.map(row => row.doc);
  } catch (err) {
    console.error('Error getting tarif inap by mobil:', err);
    throw err;
  }
};

const getAllTarifMember = async () => {
  try {
    const result = await localDbs.tarif.allDocs({
      include_docs: true,
      startkey: 'tarif_member_',
      endkey: 'tarif_member_\ufff0'
    });
    return result.rows.map(row => row.doc);
  } catch (err) {
    console.error('Error getting all tarif member:', err);
    throw err;
  }
};

const getTarifMemberByMobil = async (idMobil: string) => {
  try {
    const result = await localDbs.tarif.query('tarif/tarif_member_by_mobil', {
      key: idMobil,
      include_docs: true
    });
    return result.rows.map(row => row.doc);
  } catch (err) {
    console.error('Error getting tarif member by mobil:', err);
    throw err;
  }
};

const getAllTarifStiker = async () => {
  try {
    const result = await localDbs.tarif.allDocs({
      include_docs: true,
      startkey: 'tarif_stiker_',
      endkey: 'tarif_stiker_\ufff0'
    });
    return result.rows.map(row => row.doc);
  } catch (err) {
    console.error('Error getting all tarif stiker:', err);
    throw err;
  }
};

const getTarifStikerByMobil = async (idMobil: string) => {
  try {
    const result = await localDbs.tarif.query('tarif/tarif_stiker_by_mobil', {
      key: idMobil,
      include_docs: true
    });
    return result.rows.map(row => row.doc);
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
    await localDbs.petugas.put(petugasDesignDoc);
    await localDbs.kendaraan.put(kendaraanDesignDoc);
    await localDbs.tarif.put(tarifDesignDoc);
  } catch (err: any) {
    if (err.name !== 'conflict') {
      console.error('Error initializing design docs:', err);
    }
  }
};

/**
 * Mengambil attachment gambar dari dokumen transaksi.
 * @param transactionId ID dokumen transaksi
 * @param attachmentName Nama attachment (misal: 'entry.jpg')
 */
const getTransactionAttachment = async (
  transactionId: string,
  attachmentName: string
) => {
  try {
    const response = await localDbs.transactions.getAttachment(
      transactionId,
      attachmentName
    );
    return response;
  } catch (err) {
    console.error('Error getting attachment:', err);
    throw err;
  }
};

