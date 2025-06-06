<template>
  <q-dialog
    ref="dialogRef"
    no-backdrop-dismiss
    no-esc-dismiss
    maximized
    @hide="onDialogHide"
    persistent
    :key="componentStore.settingsKey"
  >
    <div class="row justify-center items-center">
      <q-card
        class="q-px-md q-pt-sm q-pb-md glass relative"
        style="width: 90vw; height: fit-content"
      >
        <div>
          <q-avatar
            size="40px"
            class="cursor-pointer z-top absolute-top-right q-ma-sm"
            text-color="grey-7"
            color="grey-5"
            icon="close"
            @click="dialogRef.hide()"
          />
        </div>
        <!-- <q-icon name="close"  /> -->
        <q-item>
          <q-item-section avatar>
            <q-icon name="settings" />
          </q-item-section>
          <q-item-section>
            <q-item-label
              style="margin-left: -20px"
              class="q-mt-xs text-weight-bolder"
              >Pengaturan Parkir</q-item-label
            >
          </q-item-section>
        </q-item>

        <!-- General Settings Section -->
        <div class="text-h6 q-mb-md">General Settings</div>
        <div class="q-pa-md">          <!-- ALPR Mode Settings -->
          <div class="q-mb-md">
            <div class="text-subtitle1 q-mb-sm">ALPR Mode Settings</div>
            <div class="row q-col-gutter-md items-center">
              <div class="col-md-6 col-xs-12">                <q-toggle
                  v-model="useExternalAlpr"
                  label="Use External ALPR Service"
                  left-label
                />
                <div class="text-caption text-grey-6 q-mt-xs">
                  {{ useExternalAlpr ? 'Using external WebSocket ALPR service' : 'Using internal Tauri ALPR service' }}
                </div>
              </div>
            </div>
          </div>

          <!-- WebSocket URL Settings -->
          <div class="q-mb-md" v-show="useExternalAlpr">
            <div class="text-subtitle1 q-mb-sm">ALPR WebSocket Settings</div>
            <div class="row q-col-gutter-md">
              <div class="col">                <q-input
                  v-model="wsUrl"
                  label="WebSocket URL"
                  placeholder="ws://localhost:8001/ws"
                />
              </div>
            </div>
          </div>

          <!-- Gate Specific Settings -->
          <div class="q-mb-md">
            <div class="text-subtitle1 q-mb-sm">Gate Configuration</div>
            <div class="row q-col-gutter-md">
              <div class="col-md-6 col-xs-12">
                <q-input
                  v-model="gateName"
                  label="Gate Name"
                />
              </div>
              <div class="col-md-6 col-xs-12">
                <q-select
                  v-model="gateType"
                  :options="['entry', 'exit']"
                  label="Gate Type"
                />
              </div>
              <div class="col-md-12 col-xs-12">
                <q-input
                  v-model="serialPort"
                  label="Serial Port (misal: COM3 atau /dev/ttyUSB0)"
                  :rules="[val => !!val || 'Serial port tidak boleh kosong']"
                />
              </div>
            </div>
          </div>

          <!-- Printer Settings -->
          <div class="q-mb-md">
            <div class="text-subtitle1 q-mb-sm">Printer Settings</div>
            <div class="row q-col-gutter-md items-center">
              <div class="col-md-4 col-xs-12">
                <q-input
                  v-model="printerName"
                  label="Printer Name (leave blank if none)"
                />
              </div>
              <div class="col-md-4 col-xs-12">
                <q-select
                  v-model="paperSize"
                  :options="['58mm', '80mm']"
                  label="Paper Size"
                />
              </div>
              <div class="col-md-4 col-xs-12">
                <q-toggle
                  v-model="autoPrint"
                  label="Auto Print Ticket"
                  color="primary"
                />
              </div>
            </div>
          </div>

          <div >
          <div class="q-pa-md">
            <!-- Camera Settings -->
            <div class="q-mb-md">
              <div class="text-subtitle1 q-mb-sm">Camera Settings</div>
              
              <!-- Capture Interval -->
              <div class="q-mb-md">
                <div class="text-caption q-mb-sm">Capture Interval (ms)</div>
                <div class="row q-col-gutter-md">
                  <div class="col-md-6 col-xs-12">
                    <q-input
                      v-model.number="captureInterval"
                      type="number"
                      label="Interval (e.g., 5000 for 5 seconds)"
                      filled
                    />
                  </div>
                </div>
              </div>

              <!-- License Plate Camera -->
              <div class="q-mb-md">
                <div class="text-caption q-mb-sm">License Plate Camera</div>
                <div class="row q-col-gutter-md">
                  <div class="col">
                    <!-- :disable="plateCameraUrl" -->
                    <q-select
                      v-model="selectedPlateCam"
                      :options="cameras"
                      label="USB Camera"
                      option-value="deviceId"
                      option-label="label"
                      clearable
                      emit-value
                      map-options
                      @update:model-value="updatePlateCamera"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="plateCameraIp" 
                      label="CCTV IP Address"
                      @update:model-value="setPlateCameraIP"
                      />
                    </div>
                    <!-- :disable="selectedPlateCam" -->
                  <div class="col">
                    <q-input
                      v-model="plateCameraUsername"
                      label="CCTV Username"
                      @update:model-value="updatePlateCameraUsername"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="plateCameraPassword"
                      label="CCTV Password"
                      type="password"
                      @update:model-value="updatePlateCameraPassword"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="plateCameraRtspPath"
                      label="CCTV RTSP Path"
                    />
                  </div>
                </div>
              </div>
        
              <!-- Driver Camera -->
              <div class="q-mb-md">
                <div class="text-caption q-mb-sm">Driver Camera</div>
                <div class="row q-col-gutter-md">
                  <div class="col">
                    <q-select
                      v-model="selectedDriverCam"
                      :options="cameras"
                      label="USB Camera"
                      option-value="deviceId"
                      option-label="label"
                      clearable
                      emit-value
                      map-options
                      @update:model-value="updateDriverCamera"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="driverCameraIp"
                      label="CCTV IP Address"
                      @update:model-value="setDriverCameraIP"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="driverCameraUsername"
                      label="CCTV Username"
                      @update:model-value="updateDriverCameraUsername"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="driverCameraPassword"
                      label="CCTV Password"
                      type="password"
                      @update:model-value="updateDriverCameraPassword"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="driverCameraRtspPath"
                      label="CCTV RTSP Path"
                    />
                  </div>
                </div>
              </div>

              <!-- QR Scanner Camera -->
              <div class="q-mb-md">
                <div class="text-caption q-mb-sm">QR Scanner Camera</div>
                <div class="row q-col-gutter-md">
                  <div class="col">
                    <q-select
                      v-model="selectedScannerCam"
                      :options="cameras"
                      label="USB Camera"
                      option-value="deviceId"
                      option-label="label"
                      clearable
                      emit-value
                      map-options
                      @update:model-value="updateScannerCamera"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="scannerCameraIp"
                      label="CCTV URL"
                      @update:model-value="updateScannerCameraUrl"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="scannerCameraUsername"
                      label="CCTV Username"
                      @update:model-value="updateScannerCameraUsername"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="scannerCameraPassword"
                      label="CCTV Password"
                      type="password"
                      @update:model-value="updateScannerCameraPassword"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="scannerCameraRtspPath"
                      label="CCTV RTSP Path"
                      placeholder="/Streaming/Channels/101"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        </div>

        <q-separator spaced />
        <q-card-actions align="right">
          <q-chip
            text-color="primary"
            label="Simpan"
            style="padding: 2rem 1rem"
            class="q-mt-lg q-pa-md text-h6 rounded-corner"
          >
            <q-btn @click="onSaveSettings" push icon="keyboard_return" color="black" class="q-ma-md"
          /></q-chip>
        </q-card-actions>
      </q-card>
    </div>
  </q-dialog>
</template>

<script setup>
import { useDialogPluginComponent, useQuasar } from "quasar";
// import SuccessCheckMark from "./SuccessCheckMark.vue";
import {
  onMounted,
  computed,
  ref,
  watch,
  toRefs, // Ditambahkan
} from "vue";
import { useComponentStore } from "src/stores/component-store";

import { useTransaksiStore } from "src/stores/transaksi-store";
import { useSettingsService } from 'stores/settings-service'; // Ditambahkan
import LoginDialog from "src/components/LoginDialog.vue";

const cameras = ref([]);
const wsUrl = ref(""); // Ganti dari backendUrl ke wsUrl
const useExternalAlpr = ref(false); // Tambahkan toggle ALPR mode

const componentStore = useComponentStore();
// const settingsStore = useSettingsStore(); // Tidak digunakan lagi, digantikan settingsService
const transaksiStore = useTransaksiStore();
const settingsService = useSettingsService(); // Ditambahkan
const { globalSettings, gateSettings, activeGateId } = toRefs(settingsService); // Only get reactive refs

const $q = useQuasar();
defineEmits([...useDialogPluginComponent.emits]);

const { dialogRef } = useDialogPluginComponent();

// Pengaturan gerbang sekarang diambil dari gateSettings dan globalSettings
const gateName = ref('');
const gateType = ref('entry');
const manlessMode = ref(true);
const printerName = ref(null);
const paperSize = ref('58mm');
const autoPrint = ref(true);
const darkMode = ref(false);

// Pengaturan kamera sekarang diambil dari gateSettings
const selectedPlateCam = ref(gateSettings.value.PLATE_CAM_DEVICE_ID || null);
const plateCameraIp = ref(gateSettings.value.PLATE_CAM_IP || '');
const plateCameraUsername = ref(gateSettings.value.PLATE_CAM_USERNAME || '');
const plateCameraPassword = ref(gateSettings.value.PLATE_CAM_PASSWORD || '');

const selectedDriverCam = ref(gateSettings.value.DRIVER_CAM_DEVICE_ID || null);
const driverCameraIp = ref(gateSettings.value.DRIVER_CAM_IP || '');
const driverCameraUsername = ref(gateSettings.value.DRIVER_CAM_USERNAME || '');
const driverCameraPassword = ref(gateSettings.value.DRIVER_CAM_PASSWORD || '');

const selectedScannerCam = ref(gateSettings.value.SCANNER_CAM_DEVICE_ID || null);
const scannerCameraIp = ref(gateSettings.value.SCANNER_CAM_IP || '');
const scannerCameraUsername = ref(gateSettings.value.SCANNER_CAM_USERNAME || '');
const scannerCameraPassword = ref(gateSettings.value.SCANNER_CAM_PASSWORD || '');
const plateCameraRtspPath = ref(gateSettings.value.PLATE_CAM_RTSP_PATH || '');
const driverCameraRtspPath = ref(gateSettings.value.DRIVER_CAM_RTSP_PATH || '');
const scannerCameraRtspPath = ref(gateSettings.value.SCANNER_CAM_RTSP_PATH || '');
const captureInterval = ref(gateSettings.value.CAPTURE_INTERVAL || 5000); // Default to 5 seconds

// Add computed properties to determine camera types
const serialPort = ref(''); // Ditambahkan untuk input serial port
const plateCameraType = computed(() => {
  // Tipe kamera sekarang ditentukan secara dinamis berdasarkan keberadaan device ID atau URL
// dan disimpan melalui settingsService jika diperlukan, tidak lagi langsung di sini.
  return null
})

const driverCameraType = computed(() => {
  // Tipe kamera sekarang ditentukan secara dinamis dan disimpan melalui settingsService.
  return null
})

const scannerCameraType = computed(() => {
  // Tipe kamera sekarang ditentukan secara dinamis dan disimpan melalui settingsService.
  return null
})

// Watchers individual telah dihapus, penyimpanan dilakukan di onSaveSettings

const onSaveSettings = async () => {
  console.log('onSaveSettings started - saving all settings...');
  
  try {
    // Kumpulkan semua pengaturan gerbang
    const gateSettingsToSave = {
      gateName: gateName.value,
      gateType: gateType.value,
      SERIAL_PORT: serialPort.value,
      manlessMode: manlessMode.value,
      printerName: printerName.value,
      paperSize: paperSize.value,
      autoPrint: autoPrint.value,
      PLATE_CAM_DEVICE_ID: selectedPlateCam.value,
      PLATE_CAM_IP: plateCameraIp.value,
      PLATE_CAM_USERNAME: plateCameraUsername.value,
      PLATE_CAM_PASSWORD: plateCameraPassword.value,
      PLATE_CAM_RTSP_PATH: plateCameraRtspPath.value,
      DRIVER_CAM_DEVICE_ID: selectedDriverCam.value,
      DRIVER_CAM_IP: driverCameraIp.value,
      DRIVER_CAM_USERNAME: driverCameraUsername.value,
      DRIVER_CAM_PASSWORD: driverCameraPassword.value,
      DRIVER_CAM_RTSP_PATH: driverCameraRtspPath.value,
      SCANNER_CAM_DEVICE_ID: selectedScannerCam.value,
      SCANNER_CAM_IP: scannerCameraIp.value,
      SCANNER_CAM_USERNAME: scannerCameraUsername.value,
      SCANNER_CAM_PASSWORD: scannerCameraPassword.value,
      SCANNER_CAM_RTSP_PATH: scannerCameraRtspPath.value,
      CAPTURE_INTERVAL: parseInt(captureInterval.value, 10) || 5000, // Ensure it's an integer
    };
    
    console.log('Saving gate settings:', gateSettingsToSave);
    await settingsService.saveGateSettings(gateSettingsToSave);
    console.log('Gate settings saved successfully');
    
    // Kumpulkan semua pengaturan global termasuk WebSocket URL dan ALPR mode
    const globalSettingsToSave = {
      WS_URL: wsUrl.value || 'ws://localhost:8001/ws',
      USE_EXTERNAL_ALPR: useExternalAlpr.value || false,
      darkMode: darkMode.value || false,
      LOCATION: selectedLocation.value,
      // Pertahankan pengaturan global lainnya yang mungkin sudah ada
      API_IP: globalSettings.value?.API_IP || 'http://localhost:3333',
      ALPR_IP: globalSettings.value?.ALPR_IP || 'http://localhost:8000',
      WS_IP: globalSettings.value?.WS_IP || 'ws://localhost:3333',
    };
    
    console.log('Saving global settings:', globalSettingsToSave);
    await settingsService.saveGlobalSettings(globalSettingsToSave);
    console.log('Global settings saved successfully');
      // Reload settings to ensure everything is synced
    console.log('Reloading all settings after save...');
    await settingsService.loadGlobalSettings();
    await settingsService.loadGateSettings();
    
    // Resync local variables with the loaded settings
    setTimeout(() => {
      if (isSyncing) return;
      const syncAfterSave = () => {
        console.log('Syncing UI after successful save...');
        
        // Sync global settings
        if (globalSettings.value) {
          wsUrl.value = globalSettings.value.WS_URL || 'ws://localhost:8001/ws';
          useExternalAlpr.value = globalSettings.value.USE_EXTERNAL_ALPR || false;
          darkMode.value = globalSettings.value.darkMode || false;
        }
        
        // Sync gate settings
        if (gateSettings.value) {
          gateName.value = gateSettings.value.gateName || '';
          gateType.value = gateSettings.value.gateType || 'entry';
          serialPort.value = gateSettings.value.SERIAL_PORT || '';
        }
        
        console.log('UI synced with saved settings');
      };
      
      syncAfterSave();
    }, 100);
    
    // Show success notification
    $q.notify({
      type: 'positive',
      message: 'Settings saved successfully!',
      position: 'top'
    });
    
    // Close dialog
    dialogRef.value.hide();
    
    // Optional: Reload page to apply all settings
    setTimeout(() => {
      window.location.reload();
    }, 500);
    
  } catch (error) {
    console.error('Failed to save settings:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to save settings. Please try again.',
      position: 'top'
    });
  }
};

const onSerialPortDialogHide = () => {
  window.addEventListener("keydown", handleKeyDownOnSettingDialog);
};

const onCameraInDialogHide = () => {
  // window.location.reload();
  window.addEventListener("keydown", handleKeyDownOnSettingDialog);
};
const onCameraOutDialogHide = () => {
  // window.location.reload();
  window.addEventListener("keydown", handleKeyDownOnSettingDialog);
};


const getCameras = async () => {
  try {
    console.log('Requesting camera permissions by calling getUserMedia...');
    // Meminta akses ke kamera (video saja sudah cukup untuk memicu prompt izin)
    // dan untuk mendapatkan label perangkat yang lebih deskriptif.
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    // Hentikan stream setelah izin didapatkan dan label perangkat tersedia, karena kita hanya butuh daftar perangkat.
    stream.getTracks().forEach(track => track.stop());

    console.log('Enumerating devices after permission grant...');
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoCameras = devices
      .filter(device => device.kind === 'videoinput')
      .map(device => ({
        deviceId: device.deviceId,
        label: device.label || `Camera ${cameras.value.length + 1}`,
        value: device.deviceId // Add value for q-select compatibility
      }));
    
    cameras.value = videoCameras;
    console.log('Available cameras:', cameras.value);
    
    // Pemulihan pilihan kamera sekarang menggunakan gateSettings
    // Nilai-nilai ini sudah diinisialisasi dan akan diperbarui oleh watcher
    // selectedPlateCam.value = gateSettings.value.PLATE_CAM_DEVICE_ID || null;
    // selectedDriverCam.value = gateSettings.value.DRIVER_CAM_DEVICE_ID || null;
    // selectedScannerCam.value = gateSettings.value.SCANNER_CAM_DEVICE_ID || null;
  } catch (error) {
    console.error('Error getting cameras:', error);
    $q.notify({
      type: 'negative',
      message: 'Could not access camera. Please check permissions.',
      position: 'top'
    });
  }
};

const updatePlateCamera = (cam) => {
  // Dipanggil oleh q-select @update:model-value, 'cam' adalah objek kamera atau null
  // selectedPlateCam.value sudah diupdate oleh v-model q-select
  // Perubahan akan disimpan oleh watcher selectedPlateCam
  // console.log("updatePlateCamera, selected cam object:", cam);
};

const updateDriverCamera = (cam) => {
  // Dipanggil oleh q-select @update:model-value, 'cam' adalah objek kamera atau null
  // selectedDriverCam.value sudah diupdate oleh v-model q-select
  // Perubahan akan disimpan oleh watcher selectedDriverCam
  // console.log("updateDriverCamera, selected cam object:", cam);
};

const updateScannerCamera = (cam) => {
  // Dipanggil oleh q-select @update:model-value, 'cam' adalah objek kamera atau null
  // selectedScannerCam.value sudah diupdate oleh v-model q-select
  // Perubahan akan disimpan oleh watcher selectedScannerCam
  // console.log("updateScannerCamera, selected cam object:", cam);
};

const setPlateCameraIP = (ip) => {
  if (ip) {
    // Clear USB camera selection
    selectedPlateCam.value = null
    // settingsService.saveGateSettings({ PLATE_CAM_DEVICE_ID: null, PLATE_CAM_IP: ip }); // Sudah ditangani oleh watcher
  }
}

const setDriverCameraIP = (ip) => {
  if (ip) {
    // Clear USB camera selection
    selectedDriverCam.value = null
    // settingsService.saveGateSettings({ DRIVER_CAM_DEVICE_ID: null, DRIVER_CAM_IP: ip }); // Sudah ditangani oleh watcher
  }
}

const updateScannerCameraUrl = (url) => {
  if (url) {
    // Clear USB camera selection
    selectedScannerCam.value = null
    // settingsService.saveGateSettings({ SCANNER_CAM_DEVICE_ID: null, SCANNER_CAM_IP: url }); // Sudah ditangani oleh watcher
  }
}

const updatePlateCameraUsername = (username) => {
  // settingsService.saveGateSettings({ PLATE_CAM_USERNAME: username }); // Sudah ditangani oleh watcher
}

const updatePlateCameraPassword = (password) => {
  // settingsService.saveGateSettings({ PLATE_CAM_PASSWORD: password }); // Sudah ditangani oleh watcher
}

const updateDriverCameraUsername = (username) => {
  // settingsService.saveGateSettings({ DRIVER_CAM_USERNAME: username }); // Sudah ditangani oleh watcher
}

const updateDriverCameraPassword = (password) => {
  // settingsService.saveGateSettings({ DRIVER_CAM_PASSWORD: password }); // Sudah ditangani oleh watcher
}

const updateScannerCameraUsername = (username) => {
  // settingsService.saveGateSettings({ SCANNER_CAM_USERNAME: username }); // Sudah ditangani oleh watcher
}

const updateScannerCameraPassword = (password) => {
  // settingsService.saveGateSettings({ SCANNER_CAM_PASSWORD: password }); // Sudah ditangani oleh watcher
}

// backendUrl, alprUrl, dan wsUrl sekarang diambil dari globalSettings dan tidak lagi disimpan secara lokal di sini.
// Inisialisasi sudah dilakukan di atas dengan `globalSettings.value?.API_IP` dll.
const selectedLocation = ref(null)
const parkingLocations = ref([])

const updateBackendUrl = (val) => {
  // Tidak perlu menyimpan di sini, akan disimpan di onSaveSettings
  // backendUrl.value akan diupdate oleh v-model
}

const updateAlprUrl = (val) => {
  // Pengaturan ALPR_IP sekarang ditangani oleh backend Tauri.
}

const updateWSUrl = (val) => {
  // Tidak perlu menyimpan di sini, akan disimpan di onSaveSettings
  console.log('WebSocket URL updated in UI:', val);
}

const updateExternalAlprSetting = (val) => {
  // Tidak perlu menyimpan di sini, akan disimpan di onSaveSettings
  console.log('External ALPR setting updated in UI:', val);
}

const updateLocation = (val) => {
  transaksiStore.lokasiPos = val
}

onMounted(async () => {
  console.log('SettingsDialog onMounted started');
  
  // Panggil getCameras jika manlessMode aktif saat komponen dimuat
  // Pastikan getCameras juga sudah diupdate untuk tidak bergantung pada settingsStore lama
  
  await getCameras(); 
  
  // Initialize settings first
  console.log('Initializing settings...');
  await settingsService.initializeSettings();
  console.log('Settings initialized');
    // Wait a bit to ensure reactive state is updated
  await new Promise(resolve => setTimeout(resolve, 100));
  
  // Flag to prevent recursive updates
  let isSyncing = false;
  
  // Sinkronisasi nilai lokal dengan settingsService saat komponen dimuat
  // dan setiap kali ada perubahan di store
  const syncSettings = () => {
    if (isSyncing) {
      console.log('syncSettings already running, skipping...');
      return;
    }
    
    isSyncing = true;
    console.log('syncSettings called');
    console.log('Current globalSettings:', globalSettings.value);
    console.log('Current gateSettings:', gateSettings.value);
    
    try {
      // Global Settings
      const currentGlobal = globalSettings.value;
      if (currentGlobal) {
        console.log('Syncing global settings - WS_URL:', currentGlobal.WS_URL, 'USE_EXTERNAL_ALPR:', currentGlobal.USE_EXTERNAL_ALPR);
        darkMode.value = currentGlobal.darkMode || false;
        wsUrl.value = currentGlobal.WS_URL || 'ws://localhost:8001/ws';
        useExternalAlpr.value = currentGlobal.USE_EXTERNAL_ALPR || false;
        selectedLocation.value = currentGlobal.LOCATION || null;
        console.log('After sync - wsUrl.value:', wsUrl.value, 'useExternalAlpr.value:', useExternalAlpr.value);
      } else {
        console.log('No global settings found in syncSettings');
      }

    // Gate Settings
    const currentGate = gateSettings.value;
    if (currentGate && activeGateId.value) {
      gateName.value = currentGate.gateName || '';
      gateType.value = currentGate.gateType || 'entry';
      manlessMode.value = currentGate.manlessMode === undefined ? true : currentGate.manlessMode;
      gateName.value = currentGate.gateName || '';
      gateType.value = currentGate.gateType || 'entry';
      serialPort.value = currentGate.SERIAL_PORT || ''; // Inisialisasi serialPort
      manlessMode.value = currentGate.manlessMode === undefined ? true : currentGate.manlessMode;
      printerName.value = currentGate.printerName || null;
      paperSize.value = currentGate.paperSize || '58mm';
      if (typeof autoPrint === 'object' && autoPrint !== null && typeof autoPrint.value !== 'undefined') {
        autoPrint.value = currentGate.autoPrint === undefined ? true : !!currentGate.autoPrint; // Pastikan nilai adalah boolean
      } else {
        console.error(`autoPrint is not a valid ref in syncSettings. Type: ${typeof autoPrint}, Value:`, autoPrint, "currentGate.autoPrint:", currentGate.autoPrint);
        // Tidak menetapkan autoPrint.value jika autoPrint bukan ref yang valid untuk menghindari crash.
        // Akar masalah mengapa autoPrint bukan ref perlu diinvestigasi.
      }
      // enableExitGateMode.value sudah dihapus, gateType yang akan menentukan mode gerbang

      // q-select dengan emit-value akan menyimpan deviceId (string) atau null di v-model
      selectedPlateCam.value = currentGate.PLATE_CAM_DEVICE_ID || null;
      plateCameraIp.value = currentGate.PLATE_CAM_IP || '';
      plateCameraUsername.value = currentGate.PLATE_CAM_USERNAME || '';
      plateCameraPassword.value = currentGate.PLATE_CAM_PASSWORD || '';

      selectedDriverCam.value = currentGate.DRIVER_CAM_DEVICE_ID || null;
      driverCameraIp.value = currentGate.DRIVER_CAM_IP || '';
      driverCameraUsername.value = currentGate.DRIVER_CAM_USERNAME || '';
      driverCameraPassword.value = currentGate.DRIVER_CAM_PASSWORD || '';

      selectedScannerCam.value = currentGate.SCANNER_CAM_DEVICE_ID || null;
      scannerCameraIp.value = currentGate.SCANNER_CAM_IP || '';
      scannerCameraUsername.value = currentGate.SCANNER_CAM_USERNAME || '';
      scannerCameraPassword.value = currentGate.SCANNER_CAM_PASSWORD || '';
      plateCameraRtspPath.value = currentGate.PLATE_CAM_RTSP_PATH || '';
      driverCameraRtspPath.value = currentGate.DRIVER_CAM_RTSP_PATH || '';      scannerCameraRtspPath.value = currentGate.SCANNER_CAM_RTSP_PATH || '';
      // enableExitGateMode.value sudah dihapus
    }
    } finally {
      isSyncing = false;
    }
  };
  // Panggil syncSettings setelah settings diinisialisasi
  console.log('Calling initial syncSettings...');
  syncSettings();
  // Watcher untuk memperbarui nilai lokal jika data di settingsService berubah
  // atau jika daftar kamera berubah (misalnya setelah izin diberikan dan getCameras dipanggil)
  watch([globalSettings, gateSettings, cameras], () => {
    if (!isSyncing) {
      console.log('Settings watcher triggered, calling syncSettings...');
      syncSettings();
    }
  }, { deep: true, flush: 'post' });  // Watcher untuk sinkronisasi UI dari settings store saja
  // Tidak ada penyimpanan otomatis, semua perubahan tersimpan di onSaveSettings

  watch(selectedPlateCam, (newDeviceId) => {
    if (newDeviceId && plateCameraIp.value !== '') {
      plateCameraIp.value = ''; 
    }
  });

  watch(selectedDriverCam, (newDeviceId) => {
    if (newDeviceId && driverCameraIp.value !== '') {
      driverCameraIp.value = '';
    }
  });

  watch(selectedScannerCam, (newDeviceId) => {
    if (newDeviceId && scannerCameraIp.value !== '') {
      scannerCameraIp.value = '';
    }
  });

  // Watcher untuk URL kamera yang mengosongkan pilihan USB jika URL diisi
  watch(plateCameraIp, (newUrl) => {
    if (newUrl && selectedPlateCam.value !== null) {
      selectedPlateCam.value = null;
    }
  });

  watch(driverCameraIp, (newUrl) => {
    if (newUrl && selectedDriverCam.value !== null) {
      selectedDriverCam.value = null;
    }
  });

  watch(scannerCameraIp, (newUrl) => {
    if (newUrl && selectedScannerCam.value !== null) {
      selectedScannerCam.value = null;
    }
  });

});

const onDialogHide = () => {
  // if (transaksiStore.lokasiPos === "-" || transaksiStore.lokasiPos === null) {
  //   dialogRef.value.show();
  //   $q.notify({
  //     type: "negative",
  //     message: "Silahkan pilih lokasi terlebih dahulu",
  //     position: "center",
  //   });
  // } else {
  //   window.removeEventListener("keydown", handleKeyDownOnSettingDialog);
  // }

  // else if (transaksiStore.API_IP === "-") {
  //   dialogRef.value.show();
  //   $q.notify({
  //     type: "negative",
  //     message: "Silahkan Isi URL API terlebih dahulu",
  //     position: "center",
  //   });
  // }
};

// const isSubOpen = ref(false);
</script>

<style scoped>
.glass {
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  background-color: rgba(255, 255, 255, 0.378);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.125);
}

:deep(.q-dialog__backdrop.fixed-full) {
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(30px);
}
</style>
