import { defineStore } from 'pinia';
import { ref, readonly } from 'vue';
import { invoke } from '@tauri-apps/api/core';
import { localDbs } from 'src/boot/pouchdb'; // Asumsi path ini benar

// Definisikan tipe data untuk pengaturan global dan gerbang jika diperlukan
// interface GlobalSettings { ... }
interface GateSetting {
  _id: string;
  _rev?: string;
  gateId: string;
  gateName: string;
  gateType: 'entry' | 'exit';
  manlessMode: boolean;
  printerName: string | null;
  paperSize: '58mm' | '80mm';
  autoPrint: boolean;
  PLATE_CAM_DEVICE_ID: string | null;
  PLATE_CAM_IP: string;
  PLATE_CAM_USERNAME?: string;
  PLATE_CAM_PASSWORD?: string;
  PLATE_CAM_RTSP_PATH?: string; // New field for RTSP path
  DRIVER_CAM_DEVICE_ID: string | null;
  DRIVER_CAM_IP: string;
  DRIVER_CAM_USERNAME?: string;
  DRIVER_CAM_PASSWORD?: string;
  DRIVER_CAM_RTSP_PATH?: string; // New field for RTSP path
  SCANNER_CAM_DEVICE_ID: string | null;
  SCANNER_CAM_IP: string;
  SCANNER_CAM_USERNAME?: string;
  SCANNER_CAM_PASSWORD?: string;
  SCANNER_CAM_RTSP_PATH?: string; // New field for RTSP path
  SERIAL_PORT: string | null;
  CAPTURE_INTERVAL?: number; // New field for capture interval
  // tambahkan properti lain yang mungkin ada di gate settings
}

const defaultGateSettings: Omit<GateSetting, '_id' | '_rev'> = {
  gateId: '', // Akan diisi saat load atau create
  gateName: '',
  gateType: 'entry',
  manlessMode: true,
  printerName: null,
  paperSize: '58mm',
  autoPrint: true,
  PLATE_CAM_DEVICE_ID: null,
  PLATE_CAM_IP: '',
  PLATE_CAM_USERNAME: '',
  PLATE_CAM_PASSWORD: '',
  PLATE_CAM_RTSP_PATH: '', // Default value
  DRIVER_CAM_DEVICE_ID: null,
  DRIVER_CAM_IP: '',
  DRIVER_CAM_USERNAME: '',
  DRIVER_CAM_PASSWORD: '',
  DRIVER_CAM_RTSP_PATH: '', // Default value
  SCANNER_CAM_DEVICE_ID: null,
  SCANNER_CAM_IP: '',
  SCANNER_CAM_USERNAME: '',
  SCANNER_CAM_PASSWORD: '',
  SCANNER_CAM_RTSP_PATH: '', // Default value
  SERIAL_PORT: null,
  CAPTURE_INTERVAL: 5000, // Default to 5000ms (5 seconds)
};

export const useSettingsService = defineStore('settings-service', () => {
  const activeGateId = ref<string | null>(null);
  const globalSettings = ref<any>({}); // Ganti 'any' dengan GlobalSettings
  const gateSettings = ref<GateSetting>({ ...defaultGateSettings, _id: '', gateId: '' }); // Inisialisasi dengan struktur default
  const isLoading = ref(false);
  const error = ref<any>(null);
  const cctvConfig = computed(() => ({
    PLATE: {
      username: gateSettings.value.PLATE_CAM_USERNAME || '',
      password: gateSettings.value.PLATE_CAM_PASSWORD || '',
      ipAddress: gateSettings.value.PLATE_CAM_IP || '',
      rtspStreamPath: gateSettings.value.PLATE_CAM_RTSP_PATH || '',
      deviceId: gateSettings.value.PLATE_CAM_DEVICE_ID,
    },
    DRIVER: {
      username: gateSettings.value.DRIVER_CAM_USERNAME || '',
      password: gateSettings.value.DRIVER_CAM_PASSWORD || '',
      ipAddress: gateSettings.value.DRIVER_CAM_IP || '',
      rtspStreamPath: gateSettings.value.DRIVER_CAM_RTSP_PATH || '',
      deviceId: gateSettings.value.DRIVER_CAM_DEVICE_ID,
    },
    SCANNER: {
      username: gateSettings.value.SCANNER_CAM_USERNAME || '',
      password: gateSettings.value.SCANNER_CAM_PASSWORD || '',
      ipAddress: gateSettings.value.SCANNER_CAM_IP || '',
      rtspStreamPath: gateSettings.value.SCANNER_CAM_RTSP_PATH || '',
      deviceId: gateSettings.value.SCANNER_CAM_DEVICE_ID,
    },
  }));  async function loadActiveGateId() {
    isLoading.value = true;
    error.value = null;
    console.log('Loading active gate ID...');
    
    try {
      // Coba load dari Tauri command dulu
      console.log('Trying to load active gate ID from Tauri...');
      const id = await invoke('get_active_gate_id');
      console.log("🚀 ~ cctvConfig ~ id:", id)
      activeGateId.value = typeof id === 'string' ? id : 'entry_1'; // Default to '1' if id is not a string
      console.log('Active gate ID loaded successfully from Tauri:', activeGateId.value);
    } catch (e) {
      console.warn('Failed to load active gate ID from Tauri, trying localStorage fallback:', e);
      
      try {
        // Fallback ke localStorage
        const storedId = localStorage.getItem('activeGateId');
        if (storedId) {
          activeGateId.value = storedId;
          console.log('Active gate ID loaded from localStorage:', activeGateId.value);
        } else {
          // Set default jika tidak ada di localStorage juga
          activeGateId.value = 'entry_1';
          localStorage.setItem('activeGateId', 'entry_1');
          console.log('Using default active gate ID:', activeGateId.value);
        }
      } catch (localStorageError) {
        console.error('Failed to access localStorage:', localStorageError);
        // Fallback terakhir
        activeGateId.value = 'entry_1';
        console.log('Using final fallback active gate ID:', activeGateId.value);
      }
      
      error.value = null; // Clear error since we have fallback
    } finally {
      isLoading.value = false;
    }
  }async function loadGlobalSettings() {
    console.log('loadGlobalSettings called');
    console.log('localDbs.config available:', !!localDbs.config);
    
    try {
      console.log('Attempting to get global_settings document...');
      const settings = await localDbs.config.get('global_settings');
      console.log('Global settings loaded from database:', settings);
      globalSettings.value = settings;
    } catch (e) {
      console.log('Error occurred while loading global settings:', e);
      if ((e as { name: string }).name === 'not_found') {
        console.log('Global settings not found, creating default.');
        
        // Buat dan simpan pengaturan global default jika tidak ada
        const defaultGlobal = {
          _id: 'global_settings',
          API_IP: 'http://localhost:3333',
          ALPR_IP: 'http://localhost:8000',
          WS_IP: 'ws://localhost:3333',
          WS_URL: 'ws://localhost:8001/ws', // Add WebSocket URL for ALPR
          USE_EXTERNAL_ALPR: false, // Add ALPR mode setting
          darkMode: false,
          LOCATION: null,
          // ... tambahkan default lainnya
        };
        
        try {
          console.log('Creating default global settings:', defaultGlobal);
          await localDbs.config.put(defaultGlobal);
          globalSettings.value = defaultGlobal;
          console.log('Default global settings saved and set to state');
        } catch (putError) {
          console.error('Failed to save default global settings:', putError);
          // Use default even if save fails
          globalSettings.value = defaultGlobal;
        }
      } else {
        console.error('Failed to load global settings:', e);
        // Use default global settings as fallback
        globalSettings.value = {
          _id: 'global_settings',
          API_IP: 'http://localhost:3333',
          ALPR_IP: 'http://localhost:8000',
          WS_IP: 'ws://localhost:3333',
          WS_URL: 'ws://localhost:8001/ws',
          USE_EXTERNAL_ALPR: false,
          darkMode: false,
          LOCATION: null,
        };
        console.log('Using fallback global settings due to error');
      }
    }
  }

  async function loadGateSettings(gateId: string) {
    if (!gateId) return;
    try {
      const doc = await localDbs.config.get(`gate_${gateId}`) as GateSetting;
      // Pastikan semua field dari defaultGateSettings ada, gabungkan dengan data dari DB
      console.log("🚀 ~ loadGateSettings ~ doc:", doc)
      gateSettings.value = { ...defaultGateSettings, ...doc, _id: doc._id, _rev: doc._rev, gateId: gateId };
      console.log(`Settings loaded for gate ${gateId}:`, gateSettings.value);
    } catch (e) {
      if ((e as { name: string }).name === 'not_found') {
        console.log(`Settings for gate ${gateId} not found, using and saving defaults.`);
        // Jika tidak ada dokumen, gunakan default settings dengan gateId yang aktif dan simpan
        const newDefaultGateDoc: GateSetting = {
          ...defaultGateSettings,
          _id: `gate_${gateId}`,
          gateId: gateId,
          gateName: `Gerbang ${gateId}`, // Nama default bisa lebih baik
        };
        try {
          const response = await localDbs.config.put(newDefaultGateDoc);
          gateSettings.value = { ...newDefaultGateDoc, _rev: response.rev };
        } catch (putError) {
          console.error(`Failed to save default settings for gate ${gateId}:`, putError);
          // Fallback ke state lokal tanpa _rev jika penyimpanan gagal
          gateSettings.value = newDefaultGateDoc;
        }
      } else {
        console.error(`Failed to load settings for gate ${gateId}:`, e);
        // Jika ada error lain, reset ke default tanpa mencoba menyimpan
        gateSettings.value = { ...defaultGateSettings, _id: `gate_${gateId}`, gateId: gateId };
      }
    }
  }  async function initializeSettings() {
    console.log('Initializing settings...');
    isLoading.value = true;
    error.value = null;
    
    try {
      // Load active gate ID first
      await loadActiveGateId();
      console.log('Active gate ID loaded:', activeGateId.value);
      
      // Load global settings
      await loadGlobalSettings();
      console.log('Global settings loaded:', globalSettings.value);
      
      // Load gate settings if we have an active gate ID
      if (activeGateId.value) {
        await loadGateSettings(activeGateId.value);
        console.log('Gate settings loaded:', gateSettings.value);
      } else {
        console.warn('No active gate ID found, skipping gate settings load');
      }
      
      console.log('Settings initialization complete');
    } catch (e) {
      console.error('Error during settings initialization:', e);
      error.value = e;
      // Continue even if there are errors - use defaults
    } finally {
      isLoading.value = false;
    }
  }

  async function getAllGateSettings(): Promise<GateSetting[]> {
    isLoading.value = true;
    error.value = null;
    try {
      const result = await localDbs.config.allDocs<GateSetting>({
        include_docs: true,
        startkey: 'gate_',
        endkey: 'gate_\uffff'
      });
      return result.rows.map(row => ({ ...defaultGateSettings, ...row.doc } as GateSetting));
    } catch (e) {
      console.error('Failed to load all gate settings:', e);
      error.value = e;
      return [];
    } finally {
      isLoading.value = false;
    }
  }  async function saveGlobalSettings(newSettings: any) { // Ganti 'any' dengan GlobalSettings
    console.log('saveGlobalSettings called with:', newSettings);
    console.log('Current globalSettings.value:', globalSettings.value);
    isLoading.value = true;
    error.value = null;
    try {
      // Ensure we have the current settings first
      let currentSettings = {};
      try {
        currentSettings = await localDbs.config.get('global_settings');
        console.log('Found existing global settings:', currentSettings);
      } catch (e) {
        if ((e as { name: string }).name === 'not_found') {
          console.log('No existing global settings found');
          currentSettings = {
            _id: 'global_settings',
            API_IP: 'http://localhost:3333',
            ALPR_IP: 'http://localhost:8000',
            WS_IP: 'ws://localhost:3333',
            WS_URL: 'ws://localhost:8001/ws',
            USE_EXTERNAL_ALPR: false,
            darkMode: false,
            LOCATION: null,
          };
        } else {
          throw e;
        }
      }
      
      const settingsToSave = {
        ...currentSettings, // Start with current settings
        ...newSettings,     // Apply new changes
        _id: 'global_settings', // Ensure _id is always present
      };
      console.log('Settings to save:', settingsToSave);
      
      console.log('Saving settings to database...');
      const result = await localDbs.config.put(settingsToSave);
      console.log('Save result:', result);
      
      // Update local state with the saved settings
      globalSettings.value = { ...settingsToSave, _rev: result.rev };
      console.log('Global settings saved successfully, updated state to:', globalSettings.value);
    } catch (e) {
      console.error('Failed to save global settings:', e);
      error.value = e;
      throw e; // Re-throw to let caller handle
    } finally {
      isLoading.value = false;
    }
  }

  async function saveGateSettings(newSettingsPartial: Partial<Omit<GateSetting, '_id' | '_rev' | 'gateId'>>) {
    const currentActiveGateId = activeGateId.value;
    console.log("🚀 ~ saveGateSettings ~ currentActiveGateId:", currentActiveGateId)
    if (!currentActiveGateId) {
      console.error("Cannot save gate settings, no active gate ID.");
      return;
    }
    isLoading.value = true;
    error.value = null;
    try {
      let docToSave: GateSetting;
      try {
        // Coba ambil dokumen yang sudah ada untuk mendapatkan _rev
        const existingDoc = await localDbs.config.get(`gate_${currentActiveGateId}`) as GateSetting;
        docToSave = {
          ...existingDoc,
          ...newSettingsPartial,
          _id: `gate_${currentActiveGateId}`,
          gateId: currentActiveGateId,
        };
      } catch (e) {
        // Jika dokumen tidak ditemukan, buat yang baru
        if ((e as { name: string }).name === 'not_found') {
          docToSave = {
            ...defaultGateSettings,
            ...newSettingsPartial,
            _id: `gate_${currentActiveGateId}`,
            gateId: currentActiveGateId,
            gateName: `Gerbang ${currentActiveGateId}`,
          };
        } else {
          throw e; // Lemparkan error lain
        }
      }

      const response = await localDbs.config.put(docToSave);
      gateSettings.value = { ...docToSave, _rev: response.rev }; // Update state lokal dengan _rev baru
      console.log(`Gate settings saved for ${currentActiveGateId}:`, gateSettings.value);
    } catch (e) {
      console.error(`Failed to save settings for gate ${currentActiveGateId}:`, e);
      error.value = e;
      // Pertimbangkan untuk memuat ulang pengaturan jika penyimpanan gagal untuk menjaga konsistensi
      await loadGateSettings(currentActiveGateId);
    }
    isLoading.value = false;
  }

  // New function to capture CCTV image using the updated Rust command
  async function captureCctvImage(cameraType: 'PLATE' | 'DRIVER' | 'SCANNER') {
    isLoading.value = true;
    error.value = null;
    try {
      let username = '';
      let password = '';
      let ip_address = '';
      let rtsp_stream_path = '';

      switch (cameraType) {
        case 'PLATE':
          username = gateSettings.value.PLATE_CAM_USERNAME || '';
          password = gateSettings.value.PLATE_CAM_PASSWORD || '';
          ip_address = gateSettings.value.PLATE_CAM_IP || '';
          rtsp_stream_path = gateSettings.value.PLATE_CAM_RTSP_PATH || '';
          break;
        case 'DRIVER':
          username = gateSettings.value.DRIVER_CAM_USERNAME || '';
          password = gateSettings.value.DRIVER_CAM_PASSWORD || '';
          ip_address = gateSettings.value.DRIVER_CAM_IP || '';
          rtsp_stream_path = gateSettings.value.DRIVER_CAM_RTSP_PATH || '';
          break;
        case 'SCANNER':
          username = gateSettings.value.SCANNER_CAM_USERNAME || '';
          password = gateSettings.value.SCANNER_CAM_PASSWORD || '';
          ip_address = gateSettings.value.SCANNER_CAM_IP || '';
          rtsp_stream_path = gateSettings.value.SCANNER_CAM_RTSP_PATH || '';
          break;
      }

      if (!ip_address) {
        throw new Error(`IP Address for ${cameraType} camera is not set.`);
      }

      const result = await invoke<any>('capture_cctv_image', {
        username: username,
        password: password,
        ip_address: ip_address,
        rtsp_stream_path: rtsp_stream_path,
      });
      console.log(`Capture result for ${cameraType} camera:`, result);
      return result;
    } catch (e) {
      console.error(`Failed to capture image from ${cameraType} camera:`, e);
      error.value = e;
      throw e; // Re-throw to allow component to handle
    } finally {
      isLoading.value = false;
    }
  }

  return {
    activeGateId: readonly(activeGateId),
    globalSettings: readonly(globalSettings),
    gateSettings: readonly(gateSettings),
    isLoading: readonly(isLoading),
    error: readonly(error),
    cctvConfig: readonly(cctvConfig),
    loadActiveGateId,
    loadGlobalSettings,
    loadGateSettings,
    initializeSettings,
    saveGlobalSettings,
    saveGateSettings,
    getAllGateSettings, // Tambahkan fungsi baru di sini
  };
});
     
