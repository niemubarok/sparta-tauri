import { defineStore } from 'pinia';
import { ref, readonly, computed } from 'vue';
import { invoke } from '@tauri-apps/api/core';
import { localDbs } from 'src/boot/pouchdb'; // Asumsi path ini benar

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
  PLATE_CAM_RTSP_PATH?: string;
  DRIVER_CAM_DEVICE_ID: string | null;
  DRIVER_CAM_IP: string;
  DRIVER_CAM_USERNAME?: string;
  DRIVER_CAM_PASSWORD?: string;
  DRIVER_CAM_RTSP_PATH?: string;
  SCANNER_CAM_DEVICE_ID: string | null;
  SCANNER_CAM_IP: string;
  SCANNER_CAM_USERNAME?: string;
  SCANNER_CAM_PASSWORD?: string;
  SCANNER_CAM_RTSP_PATH?: string;
  SERIAL_PORT: string | null;
  CAPTURE_INTERVAL?: number;
  // Former global settings moved into gate settings
  WS_URL: string;
  USE_EXTERNAL_ALPR: boolean;
  darkMode: boolean;
  LOCATION: string | null;
}

const defaultGateSettings: Omit<GateSetting, '_id' | '_rev'> = {
  gateId: '',
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
  PLATE_CAM_RTSP_PATH: '',
  DRIVER_CAM_DEVICE_ID: null,
  DRIVER_CAM_IP: '',
  DRIVER_CAM_USERNAME: '',
  DRIVER_CAM_PASSWORD: '',
  DRIVER_CAM_RTSP_PATH: '',
  SCANNER_CAM_DEVICE_ID: null,
  SCANNER_CAM_IP: '',
  SCANNER_CAM_USERNAME: '',
  SCANNER_CAM_PASSWORD: '',
  SCANNER_CAM_RTSP_PATH: '',
  SERIAL_PORT: null,
  CAPTURE_INTERVAL: 5000,
  // Former global settings with defaults
  WS_URL: 'ws://localhost:8765',
  USE_EXTERNAL_ALPR: false,
  darkMode: false,
  LOCATION: null,
};

export const useSettingsService = defineStore('settings-service', () => {
  const activeGateId = ref<string | null>(null);
  const gateSettings = ref<GateSetting>({ ...defaultGateSettings, _id: '', gateId: '' });
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
    console.log('Loading active gate ID...');
    
    try {
      // Coba load dari Tauri command dulu
      console.log('Trying to load active gate ID from Tauri...');
      const id = await invoke('get_active_gate_id');
      console.log("🚀 ~ cctvConfig ~ id:", id)
      activeGateId.value = typeof id === 'string' ? id : 'gate_entry_1'; // Default to '1' if id is not a string
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
          activeGateId.value = 'gate_entry_1';
          localStorage.setItem('activeGateId', 'gate_entry_1');
          console.log('Using default active gate ID:', activeGateId.value);
        }
      } catch (localStorageError) {
        console.error('Failed to access localStorage:', localStorageError);
        // Fallback terakhir
        activeGateId.value = 'gate_entry_1';
        console.log('Using final fallback active gate ID:', activeGateId.value);
      }
      
      error.value = null; // Clear error since we have fallback
    } finally {
      isLoading.value = false;
    }
  }

  async function loadGateSettings(gateId: string) {
    if (!gateId) return;
    try {
      const doc = await localDbs.config.get(`gate_${gateId}`) as GateSetting;
      console.log("🚀 ~ loadGateSettings ~ doc:", doc)
      gateSettings.value = { ...defaultGateSettings, ...doc, _id: doc._id, _rev: doc._rev, gateId: gateId };
      console.log(`Settings loaded for gate ${gateId}:`, gateSettings.value);
      
    } catch (e) {
      if ((e as { name: string }).name === 'not_found') {
        console.log(`Settings for gate ${gateId} not found, using and saving defaults.`);
        const newDefaultGateDoc: GateSetting = {
          ...defaultGateSettings,
          _id: `gate_${gateId}`,
          gateId: gateId,
          gateName: `Gerbang ${gateId}`,
        };
        try {
          const response = await localDbs.config.put(newDefaultGateDoc);
          gateSettings.value = { ...newDefaultGateDoc, _rev: response.rev };
        } catch (putError) {
          console.error(`Failed to save default settings for gate ${gateId}:`, putError);
          gateSettings.value = newDefaultGateDoc;
        }
      } else {
        console.error(`Failed to load settings for gate ${gateId}:`, e);
        gateSettings.value = { ...defaultGateSettings, _id: `gate_${gateId}`, gateId: gateId };
      }
    }
  }

  async function initializeSettings() {
    console.log('Initializing settings...');
    isLoading.value = true;
    error.value = null;
    
    try {
      await loadActiveGateId();
      console.log('Active gate ID loaded:', activeGateId.value);
      
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
        const existingDoc = await localDbs.config.get(`gate_${currentActiveGateId}`) as GateSetting;
        docToSave = {
          ...existingDoc,
          ...newSettingsPartial,
          _id: `gate_${currentActiveGateId}`,
          gateId: currentActiveGateId,
        };
      } catch (e) {
        if ((e as { name: string }).name === 'not_found') {
          docToSave = {
            ...defaultGateSettings,
            ...newSettingsPartial,
            _id: `gate_${currentActiveGateId}`,
            gateId: currentActiveGateId,
            gateName: `Gerbang ${currentActiveGateId}`,
          };
        } else {
          throw e;
        }
      }

      const response = await localDbs.config.put(docToSave);
      gateSettings.value = { ...docToSave, _rev: response.rev };
      console.log(`Gate settings saved for ${currentActiveGateId}:`, gateSettings.value);
    } catch (e) {
      console.error(`Failed to save settings for gate ${currentActiveGateId}:`, e);
      error.value = e;
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
    gateSettings: readonly(gateSettings),
    isLoading: readonly(isLoading),
    error: readonly(error),
    cctvConfig: readonly(cctvConfig),
    loadActiveGateId,
    loadGateSettings,
    initializeSettings,
    saveGateSettings,
    getAllGateSettings,
  };
});

