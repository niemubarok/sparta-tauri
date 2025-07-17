import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useQuasar } from 'quasar';
import ls from 'localstorage-slim';
import { api } from 'src/boot/axios';
import { remoteDbs } from 'src/boot/pouchdb';

// Interface untuk jenis kendaraan berdasarkan struktur database
export interface JenisKendaraan {
  id: string;
  jenis: string;
  shortcut?: string; // shortcut keyboard untuk jenis kendaraan
  tarif?: number;
  tarif_denda?: number;
  need_access?: number; // 0 = tidak perlu akses, 1 = perlu akses
  keterangan?: string;
  status?: number; // 1 = aktif, 0 = tidak aktif
  created_at?: string;
  updated_at?: string;
}

// Interface untuk tarif parkir
export interface TarifParkir {
  id: string;
  id_jenis_kendaraan: string;
  jam_ke: number;
  tarif: number;
  tarif_denda?: number;
  berlaku_dari?: string;
  berlaku_sampai?: string;
  status?: number;
}

// Interface untuk blacklist kendaraan
export interface BlacklistKendaraan {
  no_pol: string;
  status: number; // 1 = blacklist aktif, 0 = tidak aktif
  alasan?: string;
  tanggal_dibuat?: string;
  created_by?: string;
}

export const useKendaraanStore = defineStore('kendaraan', () => {
  const $q = useQuasar();
  const db = remoteDbs.kendaraan;
  
  // State variables
  const jenisKendaraan = ref<JenisKendaraan[]>([]);
  const tarifParkir = ref<TarifParkir[]>([]);
  const blacklistKendaraan = ref<BlacklistKendaraan[]>([]);
  const isLoading = ref<boolean>(false);
  
  // Configuration
  const API_URL = ref<string>(ls.get('API_URL') || '');

  // Default jenis kendaraan
  const defaultJenisKendaraan: JenisKendaraan[] = [
    {
      id: '1',
      jenis: 'Motor',
      tarif: 2000,
      tarif_denda: 5000,
      need_access: 0,
      status: 1,
      keterangan: 'Sepeda motor dan sejenisnya'
    },
    {
      id: '2', 
      jenis: 'Mobil',
      tarif: 5000,
      tarif_denda: 10000,
      need_access: 0,
      status: 1,
      keterangan: 'Mobil pribadi dan sejenisnya'
    },
    {
      id: '3',
      jenis: 'Bus/Truck',
      tarif: 10000,
      tarif_denda: 20000,
      need_access: 0,
      status: 1,
      keterangan: 'Bus, truck, dan kendaraan besar'
    },
    {
      id: '4',
      jenis: 'VIP',
      tarif: 15000,
      tarif_denda: 25000,
      need_access: 1,
      status: 1,
      keterangan: 'Kendaraan VIP dengan akses khusus'
    }
  ];

  // State for default jenis kendaraan
  const currentDefaultJenisKendaraan = ref<JenisKendaraan | null>(null);

  // Computed properties
  const activeJenisKendaraan = computed(() => 
    jenisKendaraan.value.filter(jk => jk.status === 1)
  );

  const jenisKendaraanForSelect = computed(() => 
    activeJenisKendaraan.value.map(jk => ({
      value: jk.id,
      label: jk.jenis,
      tarif: jk.tarif
    }))
  );

  const activeBlacklist = computed(() =>
    blacklistKendaraan.value.filter(bl => bl.status === 1)
  );

  const jenisKendaraanList = computed(() => 
    activeJenisKendaraan.value
  );

  // Utility functions
  const generateKendaraanId = (): string => {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    return `JK${timestamp}${random}`;
  };

  // Initialize design documents for queries
  const initializeDesignDocs = async (): Promise<void> => {
    const designDoc = {
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

    try {
      await db.put(designDoc);
    } catch (err: any) {
      if (err.name !== 'conflict') {
        console.error('Error creating kendaraan design document:', err);
      }
    }
  };

  // CRUD Operations for Jenis Kendaraan
  const getAllJenisKendaraan = async (): Promise<void> => {
    isLoading.value = true;
    try {
      if (API_URL.value && API_URL.value !== '-') {
        // Try to fetch from server
        const response = await api.get('/jenis-kendaraan');
        if (response.data && response.data.data) {
          jenisKendaraan.value = response.data.data;
          await saveJenisKendaraanToLocal(jenisKendaraan.value);
        }
      } else {
        // Fallback to local database
        await loadJenisKendaraanFromLocal();
      }
    } catch (error) {
      console.error('Error fetching jenis kendaraan from server, using local/default data:', error);
      await loadJenisKendaraanFromLocal();
      
      // If no local data, use defaults
      if (jenisKendaraan.value.length === 0) {
        jenisKendaraan.value = [...defaultJenisKendaraan];
        await saveJenisKendaraanToLocal(jenisKendaraan.value);
      }
    } finally {
      isLoading.value = false;
    }
  };

  const loadJenisKendaraanFromLocal = async (): Promise<void> => {
    try {
      const result = await db.allDocs({
        include_docs: true,
        startkey: 'jenis_kendaraan_',
        endkey: 'jenis_kendaraan_\ufff0'
      });
      
      jenisKendaraan.value = result.rows.map((row: any) => ({
        ...row.doc,
        shortcut: row.doc.shortcut || row.doc.id // fallback ke id jika shortcut tidak ada
      }));
      
      // Jika tidak ada data di local, gunakan data default
      if (jenisKendaraan.value.length === 0) {
        jenisKendaraan.value = [
          {
            id: 'A',
            jenis: 'Mobil',
            shortcut: 'A',
            tarif: 5000,
            status: 1,
            created_at: new Date().toISOString()
          },
          {
            id: 'C',
            jenis: 'Motor',
            shortcut: 'C',
            tarif: 2000,
            status: 1,
            created_at: new Date().toISOString()
          },
          {
            id: 'D',
            jenis: 'Truck/Box',
            shortcut: 'D',
            tarif: 10000,
            status: 1,
            created_at: new Date().toISOString()
          }
        ];
        
        // Simpan data default ke local storage
        await saveJenisKendaraanToLocal(jenisKendaraan.value);
      }
    } catch (error) {
      console.error('Error loading jenis kendaraan from local:', error);
      jenisKendaraan.value = [];
    }
  };

  const saveJenisKendaraanToLocal = async (jenisKendaraanList: JenisKendaraan[]): Promise<void> => {
    try {
      const docs = jenisKendaraanList.map(jk => ({
        _id: `jenis_kendaraan_${jk.id}`,
        type: 'jenis_kendaraan',
        ...jk
      }));

      await db.bulkDocs(docs);
    } catch (error) {
      console.error('Error saving jenis kendaraan to local:', error);
    }
  };

  const addJenisKendaraan = async (newJenisKendaraan: Omit<JenisKendaraan, 'id'>): Promise<boolean> => {
    try {
      const jenisKendaraanData: JenisKendaraan = {
        ...newJenisKendaraan,
        id: generateKendaraanId(),
        created_at: new Date().toISOString(),
        status: newJenisKendaraan.status ?? 1
      };

      // Save to server first
      if (API_URL.value && API_URL.value !== '-') {
        try {
          const response = await api.post('/jenis-kendaraan', jenisKendaraanData);
          if (response.data && response.data.success) {
            jenisKendaraanData.id = response.data.data?.id || jenisKendaraanData.id;
          }
        } catch (serverError) {
          console.warn('Failed to save to server, saving locally only:', serverError);
        }
      }

      // Save to local database
      await db.put({
        _id: `jenis_kendaraan_${jenisKendaraanData.id}`,
        type: 'jenis_kendaraan',
        ...jenisKendaraanData
      });

      // Add to local array
      jenisKendaraan.value.push(jenisKendaraanData);

      $q.notify({
        type: 'positive',
        message: 'Jenis kendaraan berhasil ditambahkan',
        position: 'top'
      });

      return true;
    } catch (error) {
      console.error('Error adding jenis kendaraan:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal menambahkan jenis kendaraan',
        position: 'top'
      });
      return false;
    }
  };

  const editJenisKendaraan = async (id: string, column: string, value: any): Promise<boolean> => {
    try {
      const jenisIndex = jenisKendaraan.value.findIndex(jk => jk.id === id);
      if (jenisIndex === -1) {
        throw new Error('Jenis kendaraan not found');
      }

      const updatedJenisKendaraan = { 
        ...jenisKendaraan.value[jenisIndex],
        [column]: value,
        updated_at: new Date().toISOString()
      };

      // Update on server
      if (API_URL.value && API_URL.value !== '-') {
        try {
          await api.put(`/jenis-kendaraan/${id}`, { [column]: value });
        } catch (serverError) {
          console.warn('Failed to update on server, updating locally only:', serverError);
        }
      }

      // Update local database
      try {
        const doc = await db.get(`jenis_kendaraan_${id}`);
        await db.put({
          ...doc,
          ...updatedJenisKendaraan
        });
      } catch (localError) {
        console.error('Error updating local database:', localError);
      }

      // Update local array
      jenisKendaraan.value[jenisIndex] = updatedJenisKendaraan;

      return true;
    } catch (error) {
      console.error('Error editing jenis kendaraan:', error);
      return false;
    }
  };

  const deleteJenisKendaraan = async (id: string): Promise<boolean> => {
    try {
      // Delete from server
      if (API_URL.value && API_URL.value !== '-') {
        try {
          await api.delete(`/jenis-kendaraan/${id}`);
        } catch (serverError) {
          console.warn('Failed to delete from server, deleting locally only:', serverError);
        }
      }

      // Delete from local database
      try {
        const doc = await db.get(`jenis_kendaraan_${id}`);
        await db.remove(doc);
      } catch (localError) {
        console.error('Error deleting from local database:', localError);
      }

      // Remove from local array
      const index = jenisKendaraan.value.findIndex(jk => jk.id === id);
      if (index !== -1) {
        jenisKendaraan.value.splice(index, 1);
      }

      return true;
    } catch (error) {
      console.error('Error deleting jenis kendaraan:', error);
      return false;
    }
  };

  // CRUD Operations for Blacklist
  const getAllBlacklist = async (): Promise<void> => {
    try {
      if (API_URL.value && API_URL.value !== '-') {
        const response = await api.get('/blacklist-kendaraan');
        if (response.data && response.data.data) {
          blacklistKendaraan.value = response.data.data;
          await saveBlacklistToLocal(blacklistKendaraan.value);
        }
      } else {
        await loadBlacklistFromLocal();
      }
    } catch (error) {
      console.error('Error fetching blacklist from server, using local data:', error);
      await loadBlacklistFromLocal();
    }
  };

  const loadBlacklistFromLocal = async (): Promise<void> => {
    try {
      const result = await db.allDocs({
        include_docs: true,
        startkey: 'blacklist_',
        endkey: 'blacklist_\ufff0'
      });
      
      blacklistKendaraan.value = result.rows.map((row: any) => row.doc);
    } catch (error) {
      console.error('Error loading blacklist from local:', error);
      blacklistKendaraan.value = [];
    }
  };

  const saveBlacklistToLocal = async (blacklistList: BlacklistKendaraan[]): Promise<void> => {
    try {
      const docs = blacklistList.map(bl => ({
        _id: `blacklist_${bl.no_pol.replace(/\s/g, '_')}`,
        type: 'blacklist_kendaraan',
        ...bl
      }));

      await db.bulkDocs(docs);
    } catch (error) {
      console.error('Error saving blacklist to local:', error);
    }
  };

  const addToBlacklist = async (noPol: string, alasan?: string): Promise<boolean> => {
    try {
      const blacklistData: BlacklistKendaraan = {
        no_pol: noPol.toUpperCase(),
        status: 1,
        alasan: alasan || 'Tidak ada keterangan',
        tanggal_dibuat: new Date().toISOString(),
        created_by: (ls.get('pegawai') as any)?.id_petugas || 'SYSTEM'
      };

      // Save to server
      if (API_URL.value && API_URL.value !== '-') {
        try {
          await api.post('/blacklist-kendaraan', blacklistData);
        } catch (serverError) {
          console.warn('Failed to save blacklist to server:', serverError);
        }
      }

      // Save to local
      await db.put({
        _id: `blacklist_${noPol.replace(/\s/g, '_')}`,
        type: 'blacklist_kendaraan',
        ...blacklistData
      });

      blacklistKendaraan.value.push(blacklistData);

      $q.notify({
        type: 'positive',
        message: `Kendaraan ${noPol} berhasil ditambahkan ke blacklist`,
        position: 'top'
      });

      return true;
    } catch (error) {
      console.error('Error adding to blacklist:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal menambahkan ke blacklist',
        position: 'top'
      });
      return false;
    }
  };

  const removeFromBlacklist = async (noPol: string): Promise<boolean> => {
    try {
      // Update status instead of deleting
      const blacklistIndex = blacklistKendaraan.value.findIndex(bl => bl.no_pol === noPol);
      if (blacklistIndex !== -1) {
        blacklistKendaraan.value[blacklistIndex].status = 0;
        
        // Update on server
        if (API_URL.value && API_URL.value !== '-') {
          try {
            await api.put(`/blacklist-kendaraan/${noPol}`, { status: 0 });
          } catch (serverError) {
            console.warn('Failed to update blacklist on server:', serverError);
          }
        }

        // Update local
        try {
          const doc = await db.get(`blacklist_${noPol.replace(/\s/g, '_')}`);
          await db.put({
            ...doc,
            status: 0
          });
        } catch (localError) {
          console.error('Error updating blacklist in local database:', localError);
        }
      }

      return true;
    } catch (error) {
      console.error('Error removing from blacklist:', error);
      return false;
    }
  };

  // Validation functions
  const validateJenisKendaraan = (kendaraan: Partial<JenisKendaraan>): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];

    if (!kendaraan.jenis || kendaraan.jenis.trim().length < 2) {
      errors.push('Nama jenis kendaraan minimal 2 karakter');
    }

    if (!kendaraan.tarif || kendaraan.tarif < 0) {
      errors.push('Tarif harus lebih dari 0');
    }

    if (kendaraan.tarif_denda && kendaraan.tarif_denda < 0) {
      errors.push('Tarif denda tidak boleh negatif');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  };

  // Check if jenis kendaraan name already exists
  const isJenisKendaraanExists = (jenis: string, excludeId?: string): boolean => {
    return jenisKendaraan.value.some(jk => 
      jk.jenis.toLowerCase() === jenis.toLowerCase() && 
      (excludeId ? jk.id !== excludeId : true)
    );
  };

  // Validate blacklist data
  const validateBlacklistData = (platNomor: string): { isValid: boolean; errors: string[] } => {
    const errors: string[] = [];

    if (!platNomor || platNomor.trim().length < 3) {
      errors.push('Plat nomor minimal 3 karakter');
    }

    // Simple plat nomor format validation (Indonesian format)
    const platRegex = /^[A-Z]{1,2}\s?\d{1,4}\s?[A-Z]{1,3}$/i;
    if (!platRegex.test(platNomor.trim())) {
      errors.push('Format plat nomor tidak valid (contoh: B1234XX)');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  };

  // Get kendaraan statistics
  const getKendaraanStatistics = computed(() => {
    const totalJenis = jenisKendaraan.value.length;
    const activeJenis = jenisKendaraan.value.filter(jk => jk.status === 1).length;
    const inactiveJenis = totalJenis - activeJenis;
    
    const totalBlacklist = blacklistKendaraan.value.length;
    const activeBlacklist = blacklistKendaraan.value.filter(bl => bl.status === 1).length;
    
    const avgTarif = activeJenisKendaraan.value.reduce((sum, jk) => sum + (jk.tarif || 0), 0) / activeJenisKendaraan.value.length || 0;
    
    return {
      totalJenis,
      activeJenis,
      inactiveJenis,
      totalBlacklist,
      activeBlacklist,
      avgTarif: Math.round(avgTarif)
    };
  });

  // Calculate parking fee
  const calculateParkingFee = (jenisKendaraanId: string, jamMasuk: Date, jamKeluar: Date = new Date()): number => {
    const jenis = jenisKendaraan.value.find(jk => jk.id === jenisKendaraanId);
    if (!jenis || !jenis.tarif) return 0;

    const hoursDiff = Math.ceil((jamKeluar.getTime() - jamMasuk.getTime()) / (1000 * 60 * 60));
    const hours = Math.max(1, hoursDiff); // Minimum 1 hour

    return hours * jenis.tarif;
  };

  // Seed data for initial setup
  const seedKendaraanData = async (): Promise<void> => {
    try {
      // Check if data already exists
      const existingData = await db.allDocs({ 
        include_docs: true,
        startkey: 'jenis_kendaraan_',
        endkey: 'jenis_kendaraan_\ufff0'
      });

      if (existingData.rows.length > 0) {
        console.log('Kendaraan data already exists, skipping seed');
        return;
      }

      const seedJenisKendaraan: Omit<JenisKendaraan, 'id'>[] = [
        {
          jenis: 'Motor',
          tarif: 2000,
          tarif_denda: 1000,
          need_access: 0,
          keterangan: 'Sepeda motor dan kendaraan roda dua',
          status: 1,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          jenis: 'Mobil',
          tarif: 5000,
          tarif_denda: 2500,
          need_access: 0,
          keterangan: 'Mobil sedan, hatchback, dan SUV',
          status: 1,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          jenis: 'Truk',
          tarif: 10000,
          tarif_denda: 5000,
          need_access: 1,
          keterangan: 'Truk kecil, pickup, dan van',
          status: 1,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          jenis: 'Bus',
          tarif: 15000,
          tarif_denda: 7500,
          need_access: 1,
          keterangan: 'Bus, mikrobus, dan kendaraan angkutan umum',
          status: 1,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          jenis: 'Sepeda',
          tarif: 1000,
          tarif_denda: 500,
          need_access: 0,
          keterangan: 'Sepeda konvensional dan sepeda listrik',
          status: 1,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ];

      for (const jenisData of seedJenisKendaraan) {
        await addJenisKendaraan(jenisData);
      }

      console.log('Jenis kendaraan seed data created successfully');
    } catch (error) {
      console.error('Error seeding jenis kendaraan data:', error);
    }
  };

  // Seed tarif data - simplified version
  const seedTarifData = async (): Promise<void> => {
    try {
      console.log('Tarif seeding skipped - using default tarif in jenis kendaraan');
    } catch (error) {
      console.error('Error seeding tarif data:', error);
    }
  };

  // Seed sample blacklist data - simplified
  const seedBlacklistData = async (): Promise<void> => {
    try {
      // Sample blacklist using the correct interface
      await addToBlacklist('B1234XX', 'Parkir sembarangan berulang kali');
      await addToBlacklist('D5678YY', 'Tidak membayar parkir');

      console.log('Blacklist seed data created successfully');
    } catch (error) {
      console.error('Error seeding blacklist data:', error);
    }
  };

  // Master seed function
  const seedAllKendaraanData = async (): Promise<void> => {
    try {
      await seedKendaraanData();
      await seedTarifData();
      await seedBlacklistData();
      
      // Load all data after seeding
      await loadJenisKendaraanFromLocal();
      await getAllBlacklist();
      
      console.log('All kendaraan seed data created successfully');
    } catch (error) {
      console.error('Error seeding all kendaraan data:', error);
    }
  };

  // Utility functions that were missing
  const getJenisKendaraanById = (id: string): JenisKendaraan | undefined => {
    return jenisKendaraan.value.find(jk => jk.id === id);
  };

  const getJenisKendaraanByName = (jenis: string): JenisKendaraan | undefined => {
    return jenisKendaraan.value.find(jk => jk.jenis.toLowerCase() === jenis.toLowerCase());
  };

  const setDefaultJenisKendaraan = (jenisKendaraan: any) => {
    currentDefaultJenisKendaraan.value = jenisKendaraan;
    ls.set('defaultJenisKendaraan', jenisKendaraan);
  };

  const getDefaultJenisKendaraan = () => {
    if (!currentDefaultJenisKendaraan.value) {
      currentDefaultJenisKendaraan.value = ls.get('defaultJenisKendaraan');
    }
    return currentDefaultJenisKendaraan.value;
  };

  const isBlacklisted = (noPol: string): boolean => {
    return blacklistKendaraan.value.some(bl => 
      bl.no_pol.toLowerCase() === noPol.toLowerCase() && bl.status === 1
    );
  };

  // Initialize the store
  initializeDesignDocs();

  return {
    // State
    jenisKendaraan,
    tarifParkir,
    blacklistKendaraan,
    isLoading,
    API_URL,
    currentDefaultJenisKendaraan,
    
    // Computed
    activeJenisKendaraan,
    jenisKendaraanList,
    jenisKendaraanForSelect,
    activeBlacklist,
    
    // Methods - Jenis Kendaraan
    getAllJenisKendaraan,
    addJenisKendaraan,
    editJenisKendaraan,
    deleteJenisKendaraan,
    loadJenisKendaraanFromLocal,
    
    // Methods - Blacklist
    getAllBlacklist,
    addToBlacklist,
    removeFromBlacklist,
    isBlacklisted,
    
    // Utilities
    getJenisKendaraanById,
    getJenisKendaraanByName,
    setDefaultJenisKendaraan,
    getDefaultJenisKendaraan,
    
    // Validation & Calculations
    validateJenisKendaraan,
    isJenisKendaraanExists,
    validateBlacklistData,
    calculateParkingFee,
    getKendaraanStatistics,
    
    // Seed data
    seedKendaraanData,
    seedTarifData,
    seedBlacklistData,
    seedAllKendaraanData,
    
    // Constants
    defaultJenisKendaraan
  };
});
