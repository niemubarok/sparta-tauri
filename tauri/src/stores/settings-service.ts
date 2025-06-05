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
  }));

  async function loadActiveGateId() {
    isLoading.value = true;
    error.value = null;
    try {
      // Ini adalah command Tauri yang perlu Anda buat di backend Rust
      const id = await invoke('get_active_gate_id');
      activeGateId.value = typeof id === 'string' ? id : '1'; // Default to '1' if id is not a string
    } catch (e) {
      console.error('Failed to load active gate ID:', e);
      error.value = e;
      // Mungkin set default gateId jika gagal?
      // activeGateId.value = 'default_gate'; 
    }
  }

  async function loadGlobalSettings() {
    try {
      const settings = await localDbs.config.get('global_settings');
      globalSettings.value = settings;
    } catch (e) {
      if ((e as { name: string }).name === 'not_found') {
        console.log('Global settings not found, creating default.');
        // Buat dan simpan pengaturan global default jika tidak ada
        const defaultGlobal = {
          _id: 'global_settings',
          API_IP: 'http://localhost:3333',
          ALPR_IP: 'http://localhost:8000',
          WS_IP: 'ws://localhost:3333',
          darkMode: false,
          // ... tambahkan default lainnya
        };
        await localDbs.config.put(defaultGlobal);
        globalSettings.value = defaultGlobal;
      } else {
        console.error('Failed to load global settings:', e);
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
  }

  async function initializeSettings() {
    isLoading.value = true;
    await loadActiveGateId();
    await loadGlobalSettings();
    if (activeGateId.value) {
      await loadGateSettings(activeGateId.value);
    }
    isLoading.value = false;
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
  }

  async function saveGlobalSettings(newSettings: any) { // Ganti 'any' dengan GlobalSettings
    isLoading.value = true;
    error.value = null;
    try {
      const settingsToSave = {
        ...globalSettings.value, // Pertahankan _id dan _rev jika ada
        ...newSettings,
        _id: 'global_settings', // Pastikan _id selalu ada
      };
      // Ambil dokumen terbaru untuk mendapatkan _rev
      try {
        const existingDoc = await localDbs.config.get('global_settings');
        settingsToSave._rev = existingDoc._rev;
      } catch (e) {
        // Abaikan jika tidak ditemukan, berarti ini dokumen baru
        if ((e as { name: string }).name !== 'not_found') throw e;
      }
      await localDbs.config.put(settingsToSave);
      globalSettings.value = settingsToSave; // Update state lokal
    } catch (e) {
      console.error('Failed to save global settings:', e);
      error.value = e;
    }
    isLoading.value = false;
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
     
