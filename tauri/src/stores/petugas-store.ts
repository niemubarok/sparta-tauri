import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useQuasar } from 'quasar';
import ls from 'localstorage-slim';
import { api } from 'src/boot/axios';
import { 
  remoteDbs,
  addPetugas,
  updatePetugas,
  deletePetugas,
  getAllPetugas,
  getPetugasByUsername,
  addLevel,
  getAllLevels
} from 'src/boot/pouchdb';

// Interface untuk petugas berdasarkan struktur database
export interface Petugas {
  id_petugas: string;
  nama: string;
  no_hp: string;
  username: string;
  password: string;
  level_code: string;
  level_name?: string;
  status: number; // 1 = aktif, 0 = tidak aktif
  tanggal_dibuat?: string;
  tanggal_diubah?: string;
  foto?: string;
}

// Interface untuk level user
export interface LevelUser {
  level_id: number;
  level_code: string;
  level_name: string;
  keterangan?: string;
  update_date?: string;
}

// Interface untuk login log
export interface LoginLog {
  id_petugas: string;
  waktu_login: string;
  waktu_logout?: string;
  ip_address?: string;
  device_info?: string;
  adm?: string;
}

export const usePetugasStore = defineStore('petugas', () => {
  const $q = useQuasar();
  const db = remoteDbs.petugas;
  
  // State variables
  const daftarPetugas = ref<Petugas[]>([]);
  const daftarLevel = ref<LevelUser[]>([]);
  const isLoading = ref<boolean>(false);
  const currentPetugas = ref<Petugas | null>(null);
  
  // Configuration
  const API_URL = ref<string>(ls.get('API_URL') || '');

  // Default level options
  const defaultLevels: LevelUser[] = [
    { level_id: 1, level_code: '0001', level_name: 'Administrator' },
    { level_id: 2, level_code: '0002', level_name: 'Leader' },
    { level_id: 3, level_code: '0003', level_name: 'Supervisor' },
    { level_id: 4, level_code: '0005', level_name: 'Cashier' }
  ];

  // Computed properties
  const activePetugas = computed(() => 
    daftarPetugas.value.filter(p => p.status === 1)
  );

  const petugasByLevel = computed(() => {
    const grouped: Record<string, Petugas[]> = {};
    daftarPetugas.value.forEach(petugas => {
      const level = petugas.level_name || petugas.level_code;
      if (!grouped[level]) {
        grouped[level] = [];
      }
      grouped[level].push(petugas);
    });
    return grouped;
  });

  // Utility functions
  const generatePetugasId = (): string => {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    return `PTG${timestamp}${random}`;
  };

  const getLevelName = (levelCode: string): string => {
    const level = defaultLevels.find(l => l.level_code === levelCode);
    return level?.level_name || levelCode;
  };

  // Initialize design documents for queries
  const initializeDesignDocs = async (): Promise<void> => {
    const designDoc = {
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

    try {
      // Design docs are now handled in pouchdb.ts
      console.log('Design docs initialized in pouchdb.ts');
    } catch (err: any) {
      console.error('Error creating petugas design document:', err);
    }
  };

  // CRUD Operations
  const getAllPetugas = async (): Promise<void> => {
    isLoading.value = true;
    try {
      if (API_URL.value && API_URL.value !== '-') {
        // Try to fetch from server
        const response = await api.get('/petugas');
        if (response.data && response.data.data) {
          daftarPetugas.value = response.data.data.map((p: any) => ({
            ...p,
            level_name: getLevelName(p.level_code)
          }));
          
          // Save to local database
          await saveAllToLocal(daftarPetugas.value);
        }
      } else {
        // Fallback to local database
        await loadFromLocal();
      }
    } catch (error) {
      console.error('Error fetching petugas from server, using local data:', error);
      await loadFromLocal();
    } finally {
      isLoading.value = false;
    }
  };

  const loadFromLocal = async (): Promise<void> => {
    try {
      const petugasList = await getPetugasFromLocal();
      daftarPetugas.value = petugasList.map((petugas: any) => ({
        ...petugas,
        level_name: getLevelName(petugas.level_code)
      }));
    } catch (error) {
      console.error('Error loading petugas from local:', error);
      daftarPetugas.value = [];
    }
  };

  const saveAllToLocal = async (petugasList: Petugas[]): Promise<void> => {
    try {
      const docs = petugasList.map(petugas => ({
        _id: `petugas_${petugas.id_petugas}`,
        type: 'petugas',
        ...petugas
      }));

      await remoteDbs.petugas.bulkDocs(docs);
    } catch (error) {
      console.error('Error saving petugas to local:', error);
    }
  };

  const addMasterPetugasToDB = async (newPetugas: Omit<Petugas, 'id_petugas'>): Promise<boolean> => {
    try {
      const petugasId = generatePetugasId()
      const petugas: Petugas = {
        ...newPetugas,
        id_petugas: petugasId,
        tanggal_dibuat: new Date().toISOString(),
        level_name: getLevelName(newPetugas.level_code)
      };

      // Save to server first
      if (API_URL.value && API_URL.value !== '-') {
        try {
          const response = await api.post('/petugas', petugas);
          if (response.data && response.data.success) {
            petugas.id_petugas = response.data.data?.id_petugas || petugas.id_petugas;
          }
        } catch (serverError) {
          console.warn('Failed to save to server, saving locally only:', serverError);
        }
      }

      // Save to local database
      await addPetugas({
        _id: `petugas_${petugas.id_petugas}`,
        type: 'petugas',
        ...petugas
      });

      // Add to local array
      daftarPetugas.value.push(petugas);

      $q.notify({
        type: 'positive',
        message: 'Petugas berhasil ditambahkan',
        position: 'top'
      });

      return true;
    } catch (error) {
      console.error('Error adding petugas:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal menambahkan petugas',
        position: 'top'
      });
      return false;
    }
  };

  const editMasterPetugasOnDB = async (id: string, column: string, value: any): Promise<boolean> => {
    try {
      const petugasIndex = daftarPetugas.value.findIndex(p => p.id_petugas === id);
      if (petugasIndex === -1) {
        throw new Error('Petugas not found');
      }

      const updatedPetugas = { 
        ...daftarPetugas.value[petugasIndex],
        [column]: value,
        tanggal_diubah: new Date().toISOString()
      };

      // Add level_name if level_code changed
      if (column === 'level_code') {
        updatedPetugas.level_name = getLevelName(value);
      }

      // Update on server
      if (API_URL.value && API_URL.value !== '-') {
        try {
          await api.put(`/petugas/${id}`, { [column]: value });
        } catch (serverError) {
          console.warn('Failed to update on server, updating locally only:', serverError);
        }
      }

      // Update local database
      try {
        const doc = await remoteDbs.petugas.get(`petugas_${id}`);
        await updatePetugas({
          ...doc,
          ...updatedPetugas
        });
      } catch (localError) {
        console.error('Error updating local database:', localError);
      }

      // Update local array
      daftarPetugas.value[petugasIndex] = updatedPetugas;

      return true;
    } catch (error) {
      console.error('Error editing petugas:', error);
      return false;
    }
  };

  const deleteMasterPetugasFromDB = async (id: string): Promise<boolean> => {
    try {
      // Check if user is trying to delete admin
      const petugas = daftarPetugas.value.find(p => p.id_petugas === id);
      if (petugas?.level_code === '0001') {
        $q.notify({
          type: 'warning',
          message: 'Administrator tidak dapat dihapus',
          position: 'top'
        });
        return false;
      }

      // Delete from server
      if (API_URL.value && API_URL.value !== '-') {
        try {
          await api.delete(`/petugas/${id}`);
        } catch (serverError) {
          console.warn('Failed to delete from server, deleting locally only:', serverError);
        }
      }

      // Delete from local database
      try {
        await deletePetugas(`petugas_${id}`);
      } catch (localError) {
        console.error('Error deleting from local database:', localError);
      }

      // Remove from local array
      const index = daftarPetugas.value.findIndex(p => p.id_petugas === id);
      if (index !== -1) {
        daftarPetugas.value.splice(index, 1);
      }

      return true;
    } catch (error) {
      console.error('Error deleting petugas:', error);
      return false;
    }
  };

  // Authentication functions
  const authenticatePetugas = async (username: string, password: string): Promise<Petugas | null> => {
    try {
      const petugasDoc = await getPetugasByUsername(username);

      if (petugasDoc) {
        const petugas = petugasDoc as any as Petugas;
        if (petugas.password === password && petugas.status === 1) {
          currentPetugas.value = petugas;
          
          // Log login
          await logLogin(petugas.id_petugas);
          
          return petugas;
        }
      }
      return null;
    } catch (error) {
      console.error('Error authenticating petugas:', error);
      return null;
    }
  };

  const logLogin = async (idPetugas: string): Promise<void> => {
    try {
      const loginLog: LoginLog = {
        id_petugas: idPetugas,
        waktu_login: new Date().toISOString(),
        ip_address: 'localhost', // Could be enhanced to get real IP
        device_info: navigator.userAgent
      };

      await db.post({
        _id: `login_${Date.now()}`,
        type: 'login_log',
        ...loginLog
      });
    } catch (error) {
      console.error('Error logging login:', error);
    }
  };

  const logout = (): void => {
    currentPetugas.value = null;
    ls.remove('pegawai');
    ls.remove('shift');
    ls.remove('timeLogin');
  };

  // Initialize levels
  const initializeLevels = (): void => {
    daftarLevel.value = defaultLevels;
  };

  // Seed data for initial setup
  const seedPetugasData = async (): Promise<void> => {
    try {
      // Check if data already exists
      const existingData = await db.allDocs({ 
        include_docs: true,
        startkey: 'petugas_',
        endkey: 'petugas_\ufff0'
      });

      if (existingData.rows.length > 0) {
        console.log('Petugas data already exists, skipping seed');
        return;
      }

      const seedPetugas: Omit<Petugas, 'id_petugas'>[] = [
        {
          nama: 'Administrator',
          no_hp: '081234567890',
          username: 'admin',
          password: 'admin123',
          level_code: 'ADM',
          level_name: 'Administrator',
          status: 1,
          tanggal_dibuat: new Date().toISOString(),
          foto: ''
        },
        {
          nama: 'Petugas Parkir 1',
          no_hp: '081234567891',
          username: 'petugas1',
          password: 'petugas123',
          level_code: 'PGS',
          level_name: 'Petugas',
          status: 1,
          tanggal_dibuat: new Date().toISOString(),
          foto: ''
        },
        {
          nama: 'Supervisor Parkir',
          no_hp: '081234567892',
          username: 'supervisor',
          password: 'supervisor123',
          level_code: 'SPV',
          level_name: 'Supervisor',
          status: 1,
          tanggal_dibuat: new Date().toISOString(),
          foto: ''
        }
      ];

      for (const petugasData of seedPetugas) {
        await addMasterPetugasToDB(petugasData);
      }

      await loadFromLocal();
      console.log('Petugas seed data created successfully');
    } catch (error) {
      console.error('Error seeding petugas data:', error);
    }
  };

  // Seed level data
  const seedLevelData = async (): Promise<void> => {
    try {
      const seedLevels: LevelUser[] = [
        {
          level_id: 1,
          level_code: 'ADM',
          level_name: 'Administrator',
          keterangan: 'Full access to all features',
          update_date: new Date().toISOString()
        },
        {
          level_id: 2,
          level_code: 'SPV',
          level_name: 'Supervisor',
          keterangan: 'Can manage staff and view reports',
          update_date: new Date().toISOString()
        },
        {
          level_id: 3,
          level_code: 'PGS',
          level_name: 'Petugas',
          keterangan: 'Can process parking transactions',
          update_date: new Date().toISOString()
        },
        {
          level_id: 4,
          level_code: 'CST',
          level_name: 'Cashier',
          keterangan: 'Can handle payments only',
          update_date: new Date().toISOString()
        }
      ];

      // Save to local database
      const docs = seedLevels.map(level => ({
        _id: `level_${level.level_code}`,
        type: 'level',
        ...level
      }));

      await db.bulkDocs(docs);
      daftarLevel.value = seedLevels;
      
      console.log('Level seed data created successfully');
    } catch (error) {
      console.error('Error seeding level data:', error);
    }
  };

  // Validation functions
  const validatePetugas = (petugas: Partial<Petugas>): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];

    if (!petugas.nama || petugas.nama.trim().length < 2) {
      errors.push('Nama minimal 2 karakter');
    }

    if (!petugas.username || petugas.username.trim().length < 3) {
      errors.push('Username minimal 3 karakter');
    }

    if (!petugas.password || petugas.password.length < 6) {
      errors.push('Password minimal 6 karakter');
    }

    if (!petugas.no_hp || !/^[\d\+\-\s]+$/.test(petugas.no_hp)) {
      errors.push('Nomor HP tidak valid');
    }

    if (!petugas.level_code || !daftarLevel.value.find(l => l.level_code === petugas.level_code)) {
      errors.push('Level user tidak valid');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  };

  // Check if username already exists
  const isUsernameExists = async (username: string, excludeId?: string): Promise<boolean> => {
    try {
      const result = await db.query('by_username', {
        key: username,
        include_docs: true
      });

      if (excludeId) {
        return result.rows.some(row => row.doc && (row.doc as any).id_petugas !== excludeId);
      }

      return result.rows.length > 0;
    } catch (error) {
      console.error('Error checking username:', error);
      return false;
    }
  };

  // Get petugas data from local database only
  const getPetugasFromLocal = async (): Promise<Petugas[]> => {
    try {
      const result = await db.allDocs({
        include_docs: true,
        startkey: 'petugas_',
        endkey: 'petugas_\ufff0'
      });

      return result.rows.map(row => {
        const doc = row.doc as any;
        return {
          id_petugas: doc.id_petugas,
          nama: doc.nama,
          no_hp: doc.no_hp,
          username: doc.username,
          password: doc.password,
          level_code: doc.level_code,
          level_name: doc.level_name,
          status: doc.status,
          tanggal_dibuat: doc.tanggal_dibuat,
          tanggal_diubah: doc.tanggal_diubah,
          foto: doc.foto
        } as Petugas;
      });
    } catch (error) {
      console.error('Error getting petugas from local:', error);
      return [];
    }
  };

  // Get petugas statistics
  const getPetugasStatistics = computed(() => {
    const total = daftarPetugas.value.length;
    const active = daftarPetugas.value.filter(p => p.status === 1).length;
    const inactive = total - active;
    
    const byLevel = daftarLevel.value.map(level => ({
      level: level.level_name,
      count: daftarPetugas.value.filter(p => p.level_code === level.level_code).length
    }));

    return {
      total,
      active,
      inactive,
      byLevel
    };
  });

  // Initialize the store
  initializeDesignDocs();
  initializeLevels();
  seedPetugasData();
  seedLevelData();

  return {
    // State
    daftarPetugas,
    daftarLevel,
    isLoading,
    currentPetugas,
    API_URL,
    
    // Computed
    activePetugas,
    petugasByLevel,
    getPetugasStatistics,
    
    // Methods
    getAllPetugas,
    getPetugasFromLocal,
    addMasterPetugasToDB,
    editMasterPetugasOnDB,
    deleteMasterPetugasFromDB,
    authenticatePetugas,
    logLogin,
    logout,
    getLevelName,
    loadFromLocal,
    seedPetugasData,
    seedLevelData,
    validatePetugas,
    isUsernameExists,
    
    // Constants
    defaultLevels
  };
});
