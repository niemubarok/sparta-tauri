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


// Remote database URL 
const DB_USER = process.env.DB_USER || 'admin'
const DB_PASSWORD = process.env.DB_PASSWORD || 'admin'
const REMOTE_URL = process.env.DB_URL ? `http://${DB_USER}:${DB_PASSWORD}@${process.env.DB_URL}` : `http://${DB_USER}:${DB_PASSWORD}@localhost:5984`

// Remote databases
const remoteDbs = {
  transactions: new PouchDB(`${REMOTE_URL}/transactions`),
  users: new PouchDB(`${REMOTE_URL}/users`),
  vehicles: new PouchDB(`${REMOTE_URL}/vehicles`), 
  tariffs: new PouchDB(`${REMOTE_URL}/tariffs`),
  config: new PouchDB(`${REMOTE_URL}/config`),
  members: new PouchDB(`${REMOTE_URL}/members`),
  membershipTypes: new PouchDB(`${REMOTE_URL}/membership_types`),
  // New remote databases for store integration
  petugas: new PouchDB(`${REMOTE_URL}/petugas`),
  kendaraan: new PouchDB(`${REMOTE_URL}/kendaraan`),
  levels: new PouchDB(`${REMOTE_URL}/levels`),
  blacklist: new PouchDB(`${REMOTE_URL}/blacklist`),
  tarif: new PouchDB(`${REMOTE_URL}/tarif`)
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
    const response = await localDbs.transactions.putAttachment(
      transactionId,
      attachmentName,
      rev,
      Buffer.from(data, 'base64'),
      contentType
    );
    return response;
  } catch (err) {
    console.error('Error adding attachment:', err);
    throw err;
  }
};



const initializeDatabases = async () => {
  try {
    await createIndexes()
    await initializeDesignDocs()
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
    addTransaction, // Export the new function
    addTransactionAttachment,
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
    calculateParkingFeeFromDB
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