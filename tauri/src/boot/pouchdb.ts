// if (typeof window !== 'undefined') {
//   (window as any).global = window;
//   (window as any).process = {
//     env: { DEBUG: undefined }
//   };

// }

import PouchDB from 'pouchdb-browser'
import PouchFind from 'pouchdb-find'
import { boot } from 'quasar/wrappers'



PouchDB.plugin(PouchFind)


interface DatabaseTypes {
  transactions: PouchDB.Database;
  users: PouchDB.Database;
  vehicles: PouchDB.Database;
  tariffs: PouchDB.Database;
  config: PouchDB.Database;
  members: PouchDB.Database;
    membershipTypes: PouchDB.Database;
}

// Local databases
const localDbs: DatabaseTypes = {
  transactions: new PouchDB('transactions'),
  users: new PouchDB('users'),
  vehicles: new PouchDB('vehicles'),
  tariffs: new PouchDB('tariffs'),
  config: new PouchDB('config'),
  members: new PouchDB('members'),
  membershipTypes: new PouchDB('membership_types')
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
    })
  ])
}


// Remote database URL 
const COUCHDB_USER = process.env.COUCHDB_USER || 'admin'
const COUCHDB_PASSWORD = process.env.COUCHDB_PASSWORD || 'admin'
const REMOTE_URL = process.env.COUCHDB_URL ? `http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@${process.env.COUCHDB_URL}` : `http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@localhost:5984`

// Remote databases
const remoteDbs = {
  transactions: new PouchDB(`${REMOTE_URL}/transactions`),
  users: new PouchDB(`${REMOTE_URL}/users`),
  vehicles: new PouchDB(`${REMOTE_URL}/vehicles`), 
  tariffs: new PouchDB(`${REMOTE_URL}/tariffs`),
  config: new PouchDB(`${REMOTE_URL}/config`),
  members: new PouchDB(`${REMOTE_URL}/members`),
  membershipTypes: new PouchDB(`${REMOTE_URL}/membership_types`)
}

// Sync options
const syncOpts = {
  live: true,
  retry: true,
}

import { ref } from 'vue';

// Reactive state for sync status
const isSyncing = ref(false);
const lastSyncStatus = ref<'active' | 'paused' | 'denied' | 'error' | 'complete'>('paused');
const lastSyncError = ref<any>(null);

// Start sync for all databases
const syncDatabases = () => {
  Object.keys(localDbs).forEach(dbName => {
    const sync = localDbs[dbName as keyof typeof localDbs].sync(remoteDbs[dbName as keyof typeof remoteDbs], syncOpts);

    sync.on('change', info => {
      console.log('sync change', dbName, info);
      isSyncing.value = true; // Indicate syncing is active on change
      lastSyncStatus.value = 'active';
    });
    sync.on('paused', err => {
      console.log('sync paused', dbName, err);
      isSyncing.value = false;
      lastSyncStatus.value = 'paused';
      if (err) lastSyncError.value = err;
    });
    sync.on('active', () => {
      console.log('sync active', dbName);
      isSyncing.value = true;
      lastSyncStatus.value = 'active';
      lastSyncError.value = null; // Clear previous errors on active sync
    });
    sync.on('denied', err => {
      console.error('sync denied', dbName, err);
      isSyncing.value = false;
      lastSyncStatus.value = 'denied';
      lastSyncError.value = err;
    });
    sync.on('complete', info => {
      console.log('sync complete', dbName, info);
      isSyncing.value = false;
      lastSyncStatus.value = 'complete';
    });
    sync.on('error', err => {
      console.error('sync error', dbName, err);
      isSyncing.value = false;
      lastSyncStatus.value = 'error';
      lastSyncError.value = err;
    });
  });
}

const addTransaction = async (transaction: any) => {
  try {
    const response = await localDbs.transactions.put(transaction);
    return response;
  } catch (err) {
    console.error('Error adding transaction:', err);
    throw err;
  }
};

const initializeDatabases = async () => {
  try {
    await createIndexes()
    syncDatabases()
    console.log('PouchDB initialized successfully')
  } catch (error) {
    console.error('Failed to initialize PouchDB:', error)
  }
}

export default boot(async ({ app }) => {
  await initializeDatabases()
})

export { 
    localDbs,
    remoteDbs, 
    syncDatabases,
    isSyncing, // Export reactive sync status
    lastSyncStatus,
    lastSyncError,
    addTransaction // Export the new function
}