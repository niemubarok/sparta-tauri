import { defineStore } from 'pinia';
import { ref, readonly, computed } from 'vue';
import { invoke } from '@tauri-apps/api/core';
import { localDbs } from 'src/boot/pouchdb'; // Asumsi path ini benar

type OperationMode = 'manless' | 'manual';
type ManualPaymentMode = 'postpaid' | 'prepaid';

interface GateSetting {
  _id: string;
  _rev?: string;
  gateId: string;
  gateName: string;
  gateType: 'entry' | 'exit';
  operationMode: OperationMode;
  manualPaymentMode: ManualPaymentMode;
  printerName: string | null;
  paperSize: '58mm' | '80mm';
  autoPrint: boolean;
  PLATE_CAM_DEVICE_ID: string | null;
  PLATE_CAM_IP: string;
  PLATE_CAM_USERNAME?: string;
  PLATE_CAM_PASSWORD?: string;
  PLATE_CAM_RTSP_PATH?: string;
  PLATE_CAM_DEFAULT_MODE?: string;
  PLATE_CAM_SNAPSHOT_URL?: string;
  PLATE_CAM_HTTP_PORT?: number;
  DRIVER_CAM_DEVICE_ID: string | null;
  DRIVER_CAM_IP: string;
  DRIVER_CAM_USERNAME?: string;
  DRIVER_CAM_PASSWORD?: string;
  DRIVER_CAM_RTSP_PATH?: string;
  DRIVER_CAM_DEFAULT_MODE?: string;
  DRIVER_CAM_SNAPSHOT_URL?: string;
  DRIVER_CAM_HTTP_PORT?: number;
  SCANNER_CAM_DEVICE_ID: string | null;
  SCANNER_CAM_IP: string;
  SCANNER_CAM_USERNAME?: string;
  SCANNER_CAM_PASSWORD?: string;
  SCANNER_CAM_RTSP_PATH?: string;
  SCANNER_CAM_DEFAULT_MODE?: string;
  SCANNER_CAM_SNAPSHOT_URL?: string;
  SCANNER_CAM_HTTP_PORT?: number;
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
  operationMode: 'manless',
  manualPaymentMode: 'postpaid',
  printerName: null,
  paperSize: '58mm',
  autoPrint: true,
  PLATE_CAM_DEVICE_ID: '0', // Default USB camera device ID
  PLATE_CAM_IP: '',
  PLATE_CAM_USERNAME: 'admin',
  PLATE_CAM_PASSWORD: 'password',
  PLATE_CAM_RTSP_PATH: 'Streaming/Channels/101',
  PLATE_CAM_DEFAULT_MODE: 'auto',
  PLATE_CAM_SNAPSHOT_URL: '',
  PLATE_CAM_HTTP_PORT: 80,
  DRIVER_CAM_DEVICE_ID: '1', // Default USB camera device ID for second camera
  DRIVER_CAM_IP: '',
  DRIVER_CAM_USERNAME: 'admin',
  DRIVER_CAM_PASSWORD: 'password',
  DRIVER_CAM_RTSP_PATH: 'Streaming/Channels/101',
  DRIVER_CAM_DEFAULT_MODE: 'auto',
  DRIVER_CAM_SNAPSHOT_URL: '',
  DRIVER_CAM_HTTP_PORT: 80,
  SCANNER_CAM_DEVICE_ID: null,
  SCANNER_CAM_IP: '',
  SCANNER_CAM_USERNAME: 'admin',
  SCANNER_CAM_PASSWORD: 'password',
  SCANNER_CAM_RTSP_PATH: 'Streaming/Channels/101',
  SCANNER_CAM_DEFAULT_MODE: 'auto',
  SCANNER_CAM_SNAPSHOT_URL: '',
  SCANNER_CAM_HTTP_PORT: 80,
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
      defaultMode: gateSettings.value.PLATE_CAM_DEFAULT_MODE || 'auto',
      snapshotUrl: gateSettings.value.PLATE_CAM_SNAPSHOT_URL || '',
      httpPort: gateSettings.value.PLATE_CAM_HTTP_PORT || 80,
    },
    DRIVER: {
      username: gateSettings.value.DRIVER_CAM_USERNAME || '',
      password: gateSettings.value.DRIVER_CAM_PASSWORD || '',
      ipAddress: gateSettings.value.DRIVER_CAM_IP || '',
      rtspStreamPath: gateSettings.value.DRIVER_CAM_RTSP_PATH || '',
      deviceId: gateSettings.value.DRIVER_CAM_DEVICE_ID,
      defaultMode: gateSettings.value.DRIVER_CAM_DEFAULT_MODE || 'auto',
      snapshotUrl: gateSettings.value.DRIVER_CAM_SNAPSHOT_URL || '',
      httpPort: gateSettings.value.DRIVER_CAM_HTTP_PORT || 80,
    },
    SCANNER: {
      username: gateSettings.value.SCANNER_CAM_USERNAME || '',
      password: gateSettings.value.SCANNER_CAM_PASSWORD || '',
      ipAddress: gateSettings.value.SCANNER_CAM_IP || '',
      rtspStreamPath: gateSettings.value.SCANNER_CAM_RTSP_PATH || '',
      deviceId: gateSettings.value.SCANNER_CAM_DEVICE_ID,
      defaultMode: gateSettings.value.SCANNER_CAM_DEFAULT_MODE || 'auto',
      snapshotUrl: gateSettings.value.SCANNER_CAM_SNAPSHOT_URL || '',
      httpPort: gateSettings.value.SCANNER_CAM_HTTP_PORT || 80,
    },
  }));
  
  // Computed properties for gate operation modes
  const isManlessMode = computed(() => gateSettings.value.operationMode === 'manless');
  const isManualMode = computed(() => gateSettings.value.operationMode === 'manual');
  const isPrepaidMode = computed(() => 
    gateSettings.value.operationMode === 'manual' && 
    gateSettings.value.manualPaymentMode === 'prepaid'
  );
  const isPostpaidMode = computed(() => 
    gateSettings.value.operationMode === 'manual' && 
    gateSettings.value.manualPaymentMode === 'postpaid'
  );
  
  async function loadActiveGateId() {
    isLoading.value = true;
    error.value = null;
    console.log('Loading active gate ID...');
    
    // Try localStorage first as it's more reliable
    try {
      console.log('Trying to load active gate ID from localStorage first...');
      const storedId = localStorage.getItem('activeGateId');
      if (storedId) {
        activeGateId.value = storedId;
        console.log('Active gate ID loaded from localStorage:', activeGateId.value);
        isLoading.value = false;
        return; // Exit early if we have a value from localStorage
      }
    } catch (localStorageError) {
      console.warn('Failed to access localStorage:', localStorageError);
    }
    
    // If no localStorage value, try Tauri command
    try {
      console.log('No localStorage value found, trying Tauri command...');
      
      // Add timeout to prevent hanging
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Tauri command timeout after 3 seconds')), 3000);
      });
      
      const invokePromise = invoke('get_active_gate_id');
      
      const id = await Promise.race([invokePromise, timeoutPromise]);
      console.log("🚀 ~ loadActiveGateId ~ id from Tauri:", id)
      
      if (typeof id === 'string' && id) {
        activeGateId.value = id;
        // Save to localStorage for future use
        localStorage.setItem('activeGateId', id);
        console.log('Active gate ID loaded successfully from Tauri and saved to localStorage:', activeGateId.value);
      } else {
        throw new Error('Invalid gate ID received from Tauri');
      }
    } catch (e) {
      console.warn('Failed to load active gate ID from Tauri:', e);
      
      // Final fallback
      activeGateId.value = 'gate_entry_1';
      localStorage.setItem('activeGateId', 'gate_entry_1');
      console.log('Using default active gate ID:', activeGateId.value);
      
      error.value = null; // Clear error since we have fallback
    } finally {
      isLoading.value = false;
    }
  }

  async function loadGateSettings(gateId: string) {
    if (!gateId) {
      console.warn('Cannot load gate settings: gateId is empty');
      return;
    }
    
    console.log(`Loading gate settings for ID: ${gateId}`);
    
    try {
      const doc = await localDbs.config.get(`gate_${gateId}`) as GateSetting;
      console.log("🚀 ~ loadGateSettings ~ doc:", doc)
      gateSettings.value = { ...defaultGateSettings, ...doc, _id: doc._id, gateId: doc.gateId };
      console.log(`Gate settings loaded successfully for ${gateId}:`, gateSettings.value);
    } catch (e) {
      if ((e as { name: string }).name === 'not_found') {
        console.log(`No settings found for gate ${gateId}, creating default settings...`);
        const newDefaultGateDoc: GateSetting = {
          ...defaultGateSettings,
          _id: `gate_${gateId}`,
          gateId: gateId,
          gateName: `Gerbang ${gateId}`,
        };
        
        try {
          const response = await localDbs.config.put(newDefaultGateDoc);
          gateSettings.value = { ...newDefaultGateDoc, _rev: response.rev };
          console.log(`Default settings created and saved for gate ${gateId}:`, gateSettings.value);
        } catch (putError) {
          console.error(`Failed to save default settings for gate ${gateId}:`, putError);
          gateSettings.value = newDefaultGateDoc;
          console.log(`Using default settings in memory for gate ${gateId}:`, gateSettings.value);
        }
      } else {
        console.error(`Failed to load settings for gate ${gateId}:`, e);
        // Set default settings even if there's an error
        gateSettings.value = { 
          ...defaultGateSettings, 
          _id: `gate_${gateId}`, 
          gateId: gateId,
          gateName: `Gerbang ${gateId}`
        };
        console.log(`Using fallback default settings for gate ${gateId}:`, gateSettings.value);
      }
    }
  }

  async function initializeSettings() {
    console.log('Initializing settings...');
    isLoading.value = true;
    error.value = null;
    
    try {
      console.log('Step 1: Loading active gate ID...');
      await loadActiveGateId();
      console.log('Step 1 completed. Active gate ID loaded:', activeGateId.value);
      
      if (activeGateId.value) {
        console.log('Step 2: Loading gate settings for ID:', activeGateId.value);
        await loadGateSettings(activeGateId.value);
        console.log('Step 2 completed. Gate settings loaded:', gateSettings.value);
      } else {
        console.warn('No active gate ID found, skipping gate settings load');
      }
      
      console.log('Settings initialization complete successfully');
    } catch (e) {
      console.error('Error during settings initialization:', e);
      error.value = e;
      
      // Even if there's an error, try to set some defaults so app doesn't break
      if (!activeGateId.value) {
        activeGateId.value = 'gate_entry_1';
        console.log('Set fallback active gate ID:', activeGateId.value);
      }
      
      if (!gateSettings.value.gateId) {
        gateSettings.value = { 
          ...defaultGateSettings, 
          _id: `gate_${activeGateId.value}`, 
          gateId: activeGateId.value,
          gateName: `Gerbang ${activeGateId.value}`
        };
        console.log('Set fallback gate settings:', gateSettings.value);
      }
    } finally {
      isLoading.value = false;
      console.log('Settings initialization finished. Final state:', {
        activeGateId: activeGateId.value,
        gateSettings: gateSettings.value,
        isLoading: isLoading.value,
        error: error.value
      });
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
    // Computed properties for operation modes
    isManlessMode: readonly(isManlessMode),
    isManualMode: readonly(isManualMode),
    isPrepaidMode: readonly(isPrepaidMode),
    isPostpaidMode: readonly(isPostpaidMode),
    // Functions
    loadActiveGateId,
    loadGateSettings,
    initializeSettings,
    saveGateSettings,
    getAllGateSettings,
    captureCctvImage,
  };
});

