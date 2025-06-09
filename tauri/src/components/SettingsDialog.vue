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
        <!-- Loading overlay -->
        <div v-if="isLoading" class="absolute-full flex flex-center bg-white q-pa-md" style="z-index: 1000; background-color: rgba(255, 255, 255, 0.8);">
          <div class="text-center">
            <q-spinner-hourglass size="50px" color="primary" />
            <div class="q-mt-md text-h6">Loading Settings...</div>
          </div>
        </div>

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
        <div class="q-pa-md">          
          <!-- ALPR Mode Settings -->
          <div class="q-mb-md">
            <div class="text-subtitle1 q-mb-sm">ALPR Mode Settings</div>
            <div class="row q-col-gutter-md items-center">
              <div class="col-md-6 col-xs-12">        
                <q-toggle
                  v-model="useExternalAlpr"
                  label="Use External ALPR Service"
                  left-label
                  :disable="isLoading"
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
              <div class="col">                
                <q-input
                  v-model="wsUrl"
                  label="WebSocket URL"
                  placeholder="ws://localhost:8001/ws"
                  :disable="isLoading"
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
                  :disable="isLoading"
                />
              </div>
              <div class="col-md-6 col-xs-12">
                <q-select
                  v-model="gateType"
                  :options="['entry', 'exit']"
                  label="Gate Type"
                  :disable="isLoading"
                />
              </div>
              <div class="col-md-12 col-xs-12">
                <q-input
                  v-model="serialPort"
                  label="Serial Port (misal: COM3 atau /dev/ttyUSB0)"
                  :rules="[val => !!val || 'Serial port tidak boleh kosong']"
                  :disable="isLoading"
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
                  :disable="isLoading"
                />
              </div>
              <div class="col-md-4 col-xs-12">
                <q-select
                  v-model="paperSize"
                  :options="['58mm', '80mm']"
                  label="Paper Size"
                  :disable="isLoading"
                />
              </div>
              <div class="col-md-4 col-xs-12">
                <q-toggle
                  v-model="autoPrint"
                  label="Auto Print Ticket"
                  color="primary"
                  :disable="isLoading"
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
                      :disable="isLoading"
                    />
                  </div>
                </div>
              </div>

              <!-- License Plate Camera -->
              <div class="q-mb-md">
                <div class="text-caption q-mb-sm">License Plate Camera</div>
                <div class="row q-col-gutter-md">
                  <div class="col">
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
                      :disable="isLoading"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="plateCameraIp" 
                      label="CCTV IP Address"
                      @update:model-value="setPlateCameraIP"
                      :disable="isLoading"
                      />
                    </div>
                  <div class="col">
                    <q-input
                      v-model="plateCameraUsername"
                      label="CCTV Username"
                      @update:model-value="updatePlateCameraUsername"
                      :disable="isLoading"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="plateCameraPassword"
                      label="CCTV Password"
                      type="password"
                      @update:model-value="updatePlateCameraPassword"
                      :disable="isLoading"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="plateCameraRtspPath"
                      label="CCTV RTSP Path"
                      :disable="isLoading"
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
                      :disable="isLoading"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="driverCameraIp"
                      label="CCTV IP Address"
                      @update:model-value="setDriverCameraIP"
                      :disable="isLoading"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="driverCameraUsername"
                      label="CCTV Username"
                      @update:model-value="updateDriverCameraUsername"
                      :disable="isLoading"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="driverCameraPassword"
                      label="CCTV Password"
                      type="password"
                      @update:model-value="updateDriverCameraPassword"
                      :disable="isLoading"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="driverCameraRtspPath"
                      label="CCTV RTSP Path"
                      :disable="isLoading"
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
                      :disable="isLoading"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="scannerCameraIp"
                      label="CCTV URL"
                      @update:model-value="updateScannerCameraUrl"
                      :disable="isLoading"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="scannerCameraUsername"
                      label="CCTV Username"
                      @update:model-value="updateScannerCameraUsername"
                      :disable="isLoading"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="scannerCameraPassword"
                      label="CCTV Password"
                      type="password"
                      @update:model-value="updateScannerCameraPassword"
                      :disable="isLoading"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="scannerCameraRtspPath"
                      label="CCTV RTSP Path"
                      placeholder="/Streaming/Channels/101"
                      :disable="isLoading"
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
            <q-btn 
              @click="onSaveSettings" 
              push 
              icon="keyboard_return" 
              color="black" 
              class="q-ma-md"
              :disable="isLoading"
              :loading="isSaving"
            />
          </q-chip>
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

const cameras = ref([]);
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

const isLoading = ref(false)
const isSaving = ref(false)

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
  
  isSaving.value = true;
  
  try {
    // Combine all settings into one object
    const settingsToSave = {
      // Gate-specific settings
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
    
    // Close dialog and reload as needed
    dialogRef.value.hide();
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
  } finally {
    isSaving.value = false;
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
  
  try {
    isLoading.value = true;
    
    // Panggil getCameras jika manlessMode aktif saat komponen dimuat
    await getCameras(); 
    
    // Initialize settings first
    console.log('Initializing settings...');
    await settingsService.initializeSettings();
    console.log('Settings initialized');
    
    // Wait a bit to ensure reactive state is updated
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Update form with current settings
    const currentSettings = gateSettings.value;
    if (currentSettings) {
      gateName.value = currentSettings.gateName || '';
      gateType.value = currentSettings.gateType || 'entry';
      manlessMode.value = currentSettings.manlessMode || true;
      printerName.value = currentSettings.printerName || null;
      paperSize.value = currentSettings.paperSize || '58mm';
      autoPrint.value = currentSettings.autoPrint || true;
      serialPort.value = currentSettings.SERIAL_PORT || '';
      captureInterval.value = currentSettings.CAPTURE_INTERVAL || 5000;
      
      // Camera settings
      selectedPlateCam.value = currentSettings.PLATE_CAM_DEVICE_ID || null;
      plateCameraIp.value = currentSettings.PLATE_CAM_IP || '';
      plateCameraUsername.value = currentSettings.PLATE_CAM_USERNAME || '';
      plateCameraPassword.value = currentSettings.PLATE_CAM_PASSWORD || '';
      plateCameraRtspPath.value = currentSettings.PLATE_CAM_RTSP_PATH || '';
      
      selectedDriverCam.value = currentSettings.DRIVER_CAM_DEVICE_ID || null;
      driverCameraIp.value = currentSettings.DRIVER_CAM_IP || '';
      driverCameraUsername.value = currentSettings.DRIVER_CAM_USERNAME || '';
      driverCameraPassword.value = currentSettings.DRIVER_CAM_PASSWORD || '';
      driverCameraRtspPath.value = currentSettings.DRIVER_CAM_RTSP_PATH || '';
      
      selectedScannerCam.value = currentSettings.SCANNER_CAM_DEVICE_ID || null;
      scannerCameraIp.value = currentSettings.SCANNER_CAM_IP || '';
      scannerCameraUsername.value = currentSettings.SCANNER_CAM_USERNAME || '';
      scannerCameraPassword.value = currentSettings.SCANNER_CAM_PASSWORD || '';
      scannerCameraRtspPath.value = currentSettings.SCANNER_CAM_RTSP_PATH || '';
      
      // Former global settings
      wsUrl.value = currentSettings.WS_URL || 'ws://localhost:8765';
      useExternalAlpr.value = currentSettings.USE_EXTERNAL_ALPR || false;
      darkMode.value = currentSettings.darkMode || false;
      selectedLocation.value = currentSettings.LOCATION || null;
    }
  } catch (error) {
    console.error('Failed to load settings:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to load settings. Please try again.',
      position: 'top'
    });
  } finally {
    isLoading.value = false;
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
