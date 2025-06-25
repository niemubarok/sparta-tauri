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
    <div class="row justify-center items-center ">
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
        <div class="q-pa-md">          <!-- ALPR Mode Settings -->
          <div class="q-mb-md">
            <div class="text-subtitle1 q-mb-sm">ALPR Mode Settings</div>
            <div class="row q-col-gutter-md items-center">
              <div class="col-md-6 col-xs-12">        
                <q-toggle
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
            <div class="text-subtitle1 q-mb-sm">Pengaturan Gerbang</div>
            <div class="row q-col-gutter-md">
              <div class="col-md-6 col-xs-12">
                <q-input
                  v-model="gateName"
                  label="Nama Gerbang"
                />
              </div>
              <div class="col-md-6 col-xs-12">
                <q-select
                  v-model="gateType"
                  :options="['entry', 'exit']"
                  label="Tipe Gerbang"
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

          <!-- Operation Mode Settings -->
          <div class="q-mb-md">
            <div class="text-subtitle1 q-mb-sm">Mode Operasi</div>
            <div class="row q-col-gutter-md">
              <div class="col-md-6 col-xs-12">
                <q-select
                  v-model="operationMode"
                  :options="operationModeOptions"
                  label="Mode Operasi"
                  emit-value
                  map-options
                />
                <div class="text-caption text-grey-6 q-mt-xs">
                  {{ operationMode === 'manless' ? 'Mode tanpa petugas - otomatis dengan ALPR' : 'Mode dengan petugas - input manual' }}
                </div>
              </div>
              <div class="col-md-6 col-xs-12" v-show="operationMode === 'manual'">
                <q-select
                  v-model="manualPaymentMode"
                  :options="manualPaymentModeOptions"
                  label="Mode Pembayaran Manual"
                  emit-value
                  map-options
                />
                <div class="text-caption text-grey-6 q-mt-xs">
                  {{ manualPaymentMode === 'prepaid' ? 'Bayar depan - tarif prepaid' : 'Bayar belakang - tarif progresif' }}
                </div>
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
                  <div class="col-md-6 col-xs-12">
                    <q-btn 
                      color="primary" 
                      label="Refresh Cameras" 
                      icon="refresh"
                      @click="getCameras"
                      size="sm"
                    />
                    <div class="text-caption q-mt-xs">
                      {{ availableCameras.length }} camera(s) detected
                    </div>
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
                      :options="availableCameras"
                      label="USB Camera"
                      option-value="deviceId"
                      option-label="label"
                      clearable
                      emit-value
                      map-options
                      @update:model-value="updatePlateCamera"
                    />
                    <div class="text-caption text-grey-6 q-mt-xs" v-if="availableCameras.length === 0">
                      No USB cameras detected. Click "Refresh Cameras" to try again.
                    </div>
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
                      :options="availableCameras"
                      label="USB Camera"
                      option-value="deviceId"
                      option-label="label"
                      clearable
                      emit-value
                      map-options
                      @update:model-value="updateDriverCamera"
                    />
                    <div class="text-caption text-grey-6 q-mt-xs" v-if="availableCameras.length === 0">
                      No USB cameras detected. Click "Refresh Cameras" to try again.
                    </div>
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
                      :options="availableCameras"
                      label="USB Camera"
                      option-value="deviceId"
                      option-label="label"
                      clearable
                      emit-value
                      map-options
                      @update:model-value="updateScannerCamera"
                    />
                    <div class="text-caption text-grey-6 q-mt-xs" v-if="availableCameras.length === 0">
                      No USB cameras detected. Click "Refresh Cameras" to try again.
                    </div>
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
import { useSettingsService } from 'stores/settings-service';
import LoginDialog from "src/components/LoginDialog.vue";

// Initialize cameras ref
const cameras = ref([]);
console.log('Cameras ref initialized:', cameras.value);

const wsUrl = ref(""); // Ganti dari backendUrl ke wsUrl
const useExternalAlpr = ref(false); // Tambahkan toggle ALPR mode

const componentStore = useComponentStore();
// const settingsStore = useSettingsStore(); // Tidak digunakan lagi, digantikan settingsService
const transaksiStore = useTransaksiStore();
const settingsService = useSettingsService();
const { gateSettings, activeGateId } = toRefs(settingsService);

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

// Operation mode settings
const operationMode = ref('manless');
const manualPaymentMode = ref('postpaid');

// Operation mode options
const operationModeOptions = [
  { label: 'Mode Tanpa Petugas (Manless)', value: 'manless' },
  { label: 'Mode Manual (Dengan Petugas)', value: 'manual' }
];

const manualPaymentModeOptions = [
  { label: 'Bayar Belakang (Postpaid)', value: 'postpaid' },
  { label: 'Bayar Depan (Prepaid)', value: 'prepaid' }
];

// Pengaturan kamera sekarang diambil dari gateSettings
const selectedPlateCam = ref(null);
const plateCameraIp = ref('');
const plateCameraUsername = ref('');
const plateCameraPassword = ref('');

const selectedDriverCam = ref(null);
const driverCameraIp = ref('');
const driverCameraUsername = ref('');
const driverCameraPassword = ref('');

const selectedScannerCam = ref(null);
const scannerCameraIp = ref('');
const scannerCameraUsername = ref('');
const scannerCameraPassword = ref('');
const plateCameraRtspPath = ref('');
const driverCameraRtspPath = ref('');
const scannerCameraRtspPath = ref('');
const captureInterval = ref(5000); // Default to 5 seconds

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

// Additional refs that need to be declared before the watcher
const selectedLocation = ref(null)
const parkingLocations = ref([])

// Computed property for camera availability
const availableCameras = computed(() => {
  console.log('Computing available cameras, current count:', cameras.value.length);
  return cameras.value || [];
});

// Watchers individual telah dihapus, penyimpanan dilakukan di onSaveSettings

// Watchers to sync form values with gateSettings changes
watch(gateSettings, (newSettings) => {
  if (newSettings) {
    gateName.value = newSettings.gateName || '';
    gateType.value = newSettings.gateType || 'entry';
    operationMode.value = newSettings.operationMode || 'manless';
    manualPaymentMode.value = newSettings.manualPaymentMode || 'postpaid';
    printerName.value = newSettings.printerName || null;
    paperSize.value = newSettings.paperSize || '58mm';
    autoPrint.value = newSettings.autoPrint || true;
    serialPort.value = newSettings.SERIAL_PORT || '';
    captureInterval.value = newSettings.CAPTURE_INTERVAL || 5000;
    wsUrl.value = newSettings.WS_URL || '';
    useExternalAlpr.value = newSettings.USE_EXTERNAL_ALPR || false;
    darkMode.value = newSettings.darkMode || false;
    
    // Camera settings
    selectedPlateCam.value = newSettings.PLATE_CAM_DEVICE_ID || null;
    plateCameraIp.value = newSettings.PLATE_CAM_IP || '';
    plateCameraUsername.value = newSettings.PLATE_CAM_USERNAME || '';
    plateCameraPassword.value = newSettings.PLATE_CAM_PASSWORD || '';
    plateCameraRtspPath.value = newSettings.PLATE_CAM_RTSP_PATH || '';
    
    selectedDriverCam.value = newSettings.DRIVER_CAM_DEVICE_ID || null;
    driverCameraIp.value = newSettings.DRIVER_CAM_IP || '';
    driverCameraUsername.value = newSettings.DRIVER_CAM_USERNAME || '';
    driverCameraPassword.value = newSettings.DRIVER_CAM_PASSWORD || '';
    driverCameraRtspPath.value = newSettings.DRIVER_CAM_RTSP_PATH || '';
    
    selectedScannerCam.value = newSettings.SCANNER_CAM_DEVICE_ID || null;
    scannerCameraIp.value = newSettings.SCANNER_CAM_IP || '';
    scannerCameraUsername.value = newSettings.SCANNER_CAM_USERNAME || '';
    scannerCameraPassword.value = newSettings.SCANNER_CAM_PASSWORD || '';
    scannerCameraRtspPath.value = newSettings.SCANNER_CAM_RTSP_PATH || '';
    
    // Former global settings
    wsUrl.value = newSettings.WS_URL || 'ws://localhost:8765';
    useExternalAlpr.value = newSettings.USE_EXTERNAL_ALPR || false;
    darkMode.value = newSettings.darkMode || false;
    selectedLocation.value = newSettings.LOCATION || null;
  }
}, { immediate: true, deep: true });

const onSaveSettings = async () => {
  console.log('onSaveSettings started - saving all settings...');
  
  try {
    // Combine all settings into one object
    const settingsToSave = {
      // Gate-specific settings
      gateName: gateName.value,
      gateType: gateType.value,
      operationMode: operationMode.value,
      manualPaymentMode: manualPaymentMode.value,
      SERIAL_PORT: serialPort.value,
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
      CAPTURE_INTERVAL: parseInt(captureInterval.value, 10) || 5000,
      
      // Former global settings now in gate settings
      WS_URL: wsUrl.value || 'ws://localhost:8765',
      USE_EXTERNAL_ALPR: useExternalAlpr.value || false,
      darkMode: darkMode.value || false,
      LOCATION: selectedLocation.value,
    };
    
    console.log('Saving consolidated settings:', settingsToSave);
    await settingsService.saveGateSettings(settingsToSave);
    console.log('Settings saved successfully');
    
    // Show success notification
    $q.notify({
      type: 'positive',
      message: 'Settings saved successfully!',
      position: 'top'
    });
    
    // Close dialog first
    dialogRef.value.hide();
    
    // Wait a bit for settings to be saved and reactive system to update
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Refresh settings to ensure they're loaded correctly
    await settingsService.initializeSettings();
    
    // Only reload if absolutely necessary (can be removed if reactive updates work well)
    // setTimeout(() => {
    //   window.location.reload();
    // }, 1000);
    
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
  // window.addEventListener("keydown", handleKeyDownOnSettingDialog);
};

const onCameraInDialogHide = () => {
  // window.location.reload();
  // window.addEventListener("keydown", handleKeyDownOnSettingDialog);
};
const onCameraOutDialogHide = () => {
  // window.location.reload();
  // window.addEventListener("keydown", handleKeyDownOnSettingDialog);
};


const getCameras = async () => {
  try {
    console.log('Starting camera enumeration...');
    
    // First, try to enumerate devices without requesting permission
    let devices = await navigator.mediaDevices.enumerateDevices();
    console.log('Initial device enumeration (before permission):', devices);
    
    // Check if we have detailed labels (permission already granted)
    const hasDetailedLabels = devices.some(device => 
      device.kind === 'videoinput' && device.label && device.label !== ''
    );
    
    if (!hasDetailedLabels) {
      console.log('No detailed labels found, requesting camera permissions...');
      try {
        // Request permission to get detailed device labels
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        // Stop the stream immediately after getting permission
        stream.getTracks().forEach(track => track.stop());
        console.log('Camera permission granted, re-enumerating devices...');
        
        // Re-enumerate devices after permission is granted
        devices = await navigator.mediaDevices.enumerateDevices();
      } catch (permissionError) {
        console.warn('Camera permission denied, using basic device info:', permissionError);
        // Continue with basic device info even if permission is denied
      }
    }

    console.log('Final device enumeration:', devices);
    
    // Filter and map video input devices
    const videoCameras = devices
      .filter(device => device.kind === 'videoinput')
      .map((device, index) => ({
        deviceId: device.deviceId,
        label: device.label || `Camera ${index + 1}`,
        value: device.deviceId // Add value for q-select compatibility
      }));
    
    cameras.value = videoCameras;
    console.log('Available cameras set to:', cameras.value);
    
    // Show notification about camera detection
    if (videoCameras.length > 0) {
      $q.notify({
        type: 'positive',
        message: `Found ${videoCameras.length} camera(s)`,
        position: 'top',
        timeout: 2000
      });
    } else {
      $q.notify({
        type: 'warning',
        message: 'No cameras detected. Please check if cameras are connected.',
        position: 'top',
        timeout: 3000
      });
    }
    
  } catch (error) {
    console.error('Error getting cameras:', error);
    $q.notify({
      type: 'negative',
      message: 'Could not access camera devices. Please check browser permissions.',
      position: 'top'
    });
    
    // Set empty array as fallback
    cameras.value = [];
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
  
  try {
    // Initialize settings first
    console.log('Initializing settings...');
    await settingsService.initializeSettings();
    console.log('Settings initialized successfully');
    
    // Wait a bit to ensure reactive state is updated
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Get cameras after settings are initialized
    console.log('Starting camera enumeration...');
    await getCameras(); 
    console.log('Camera enumeration completed, camera count:', cameras.value.length);
    
    // The form values will be automatically updated by the watcher
    // when gateSettings changes, so we don't need to manually set them here
    console.log('Current settings after initialization:', gateSettings.value);
    console.log('Current camera list:', cameras.value);
    
  } catch (error) {
    console.error('Error initializing settings dialog:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to load settings. Please try again.',
      position: 'top'
    });
  }
});
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
