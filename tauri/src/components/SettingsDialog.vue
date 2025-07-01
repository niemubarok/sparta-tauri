<template>
  <q-dialog
    ref="dialogRef"
    maximized
    @hide="onDialogHide"
    persistent
    :key="componentStore.settingsKey"
  >
    <div class="row justify-center items-center full-height">
      <q-card
        class="q-px-lg q-py-md glass relative"
        style="width: 95vw; max-width: 1400px; height: 90vh; overflow: hidden;"
      >
        <!-- Header -->
        <div class="row items-center q-mb-lg">
          <q-icon name="settings" size="md" color="primary" class="q-mr-md" />
          <div class="text-h5 text-weight-bold" style="color: #1976d2;">
            Pengaturan Sistem Parkir
          </div>
          <q-space />
          <q-btn
            round
            flat
            icon="close"
            color="grey-7"
            size="md"
            @click="dialogRef.hide()"
          />
        </div>

        <!-- Main Content with Scroll -->
        <div class="settings-content" style="height: calc(100% - 120px); overflow-y: auto;">
          <div class="row q-col-gutter-lg">
            <!-- Left Column -->
            <div class="col-12 col-lg-6">
              
              <!-- ALPR Settings Card -->
              <q-card class="settings-card q-mb-lg" flat bordered>
                <q-card-section>
                  <div class="settings-section-title">
                    <q-icon name="auto_awesome" class="q-mr-sm" />
                    Pengaturan ALPR
                  </div>
                  
                  <div class="q-mt-md">
                    <q-toggle
                      v-model="useExternalAlpr"
                      label="Gunakan Service ALPR Eksternal"
                      color="primary"
                      size="md"
                    />
                    <div class="text-caption text-grey-6 q-mt-xs q-ml-lg">
                      {{ useExternalAlpr ? 'Menggunakan service WebSocket ALPR eksternal' : 'Menggunakan service ALPR internal Tauri' }}
                    </div>
                  </div>

                  <div v-show="useExternalAlpr" class="q-mt-md">
                    <q-input
                      v-model="wsUrl"
                      label="WebSocket URL"
                      placeholder="ws://localhost:8001/ws"
                      outlined
                      dense
                    />
                  </div>
                </q-card-section>
              </q-card>

              <!-- Gate Settings Card -->
              <q-card class="settings-card q-mb-lg" flat bordered>
                <q-card-section>
                  <div class="settings-section-title">
                    <q-icon name="door_front" class="q-mr-sm" />
                    Pengaturan Gerbang
                  </div>
                  
                  <div class="row q-col-gutter-md q-mt-md">
                    <div class="col-12 col-sm-6">
                      <q-input
                        v-model="gateName"
                        label="Nama Gerbang"
                        outlined
                        dense
                      />
                    </div>
                    <div class="col-12 col-sm-6">
                      <q-select
                        v-model="gateType"
                        :options="[
                          { label: 'Gerbang Masuk', value: 'entry' },
                          { label: 'Gerbang Keluar', value: 'exit' }
                        ]"
                        label="Tipe Gerbang"
                        outlined
                        dense
                        emit-value
                        map-options
                      />
                    </div>
                    <div class="col-12 col-sm-6">
                      <q-input
                        v-model="prefix"
                        label="Prefix Default"
                        placeholder="Contoh: A, B, C"
                        outlined
                        dense
                      />
                    </div>
                    <div class="col-12 col-sm-6">
                      <q-input
                        v-model="serialPort"
                        label="Serial Port"
                        placeholder="COM3 atau /dev/ttyUSB0"
                        outlined
                        dense
                        :rules="[val => !!val || 'Serial port wajib diisi']"
                      />
                    </div>
                  </div>
                </q-card-section>
              </q-card>

              <!-- Operation Mode Card -->
              <q-card class="settings-card q-mb-lg" flat bordered>
                <q-card-section>
                  <div class="settings-section-title">
                    <q-icon name="settings_applications" class="q-mr-sm" />
                    Mode Operasi
                  </div>
                  
                  <div class="row q-col-gutter-md q-mt-md">
                    <div class="col-12" :class="operationMode === 'manual' ? 'col-sm-6' : ''">
                      <q-select
                        v-model="operationMode"
                        :options="operationModeOptions"
                        label="Mode Operasi"
                        outlined
                        dense
                        emit-value
                        map-options
                      />
                      <div class="text-caption text-grey-6 q-mt-xs">
                        {{ operationMode === 'manless' ? 'Mode otomatis dengan ALPR tanpa petugas' : 'Mode manual dengan input petugas' }}
                      </div>
                    </div>
                    <div class="col-12 col-sm-6" v-show="operationMode === 'manual'">
                      <q-select
                        v-model="manualPaymentMode"
                        :options="manualPaymentModeOptions"
                        label="Mode Pembayaran"
                        outlined
                        dense
                        emit-value
                        map-options
                      />
                      <div class="text-caption text-grey-6 q-mt-xs">
                        {{ manualPaymentMode === 'prepaid' ? 'Bayar di depan dengan tarif tetap' : 'Bayar di belakang dengan tarif progresif' }}
                      </div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>

              <!-- Printer Settings Card -->
              <q-card class="settings-card q-mb-lg" flat bordered>
                <q-card-section>
                  <div class="settings-section-title">
                    <q-icon name="print" class="q-mr-sm" />
                    Pengaturan Printer
                  </div>
                  
                  <div class="row q-col-gutter-md q-mt-md items-end">
                    <div class="col-12 col-sm-4">
                      <q-input
                        v-model="printerName"
                        label="Nama Printer"
                        placeholder="Kosongkan jika tidak ada"
                        outlined
                        dense
                      />
                    </div>
                    <div class="col-12 col-sm-4">
                      <q-select
                        v-model="paperSize"
                        :options="[
                          { label: '58mm (Kecil)', value: '58mm' },
                          { label: '80mm (Besar)', value: '80mm' }
                        ]"
                        label="Ukuran Kertas"
                        outlined
                        dense
                        emit-value
                        map-options
                      />
                    </div>
                    <div class="col-12 col-sm-4">
                      <q-toggle
                        v-model="autoPrint"
                        label="Auto Print Tiket"
                        color="primary"
                        size="md"
                      />
                    </div>
                  </div>
                </q-card-section>
              </q-card>

            </div>

            <!-- Right Column -->
            <div class="col-12 col-lg-6">
              
              <!-- Camera Settings Card -->
              <q-card class="settings-card q-mb-lg" flat bordered>
                <q-card-section>
                  <div class="settings-section-title">
                    <q-icon name="videocam" class="q-mr-sm" />
                    Pengaturan Kamera
                  </div>
                  
                  <!-- Camera Controls -->
                  <div class="row q-col-gutter-md q-mt-md">
                    <div class="col-12 col-sm-6">
                      <q-input
                        v-model.number="captureInterval"
                        type="number"
                        label="Interval Capture (ms)"
                        placeholder="5000 = 5 detik"
                        outlined
                        dense
                      />
                    </div>
                    <div class="col-12 col-sm-6">
                      <q-btn 
                        color="primary" 
                        label="Refresh Kamera" 
                        icon="refresh"
                        @click="getCameras"
                        size="md"
                        style="width: 100%"
                      />
                      <div class="text-caption text-center q-mt-xs">
                        {{ availableCameras.length }} kamera terdeteksi
                      </div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>

              <!-- Camera Configurations -->
              <q-expansion-item
                v-for="(cameraType, index) in [
                  { name: 'plate', label: 'Kamera Plat Nomor', icon: 'pin' },
                  { name: 'driver', label: 'Kamera Driver', icon: 'person' },
                  { name: 'scanner', label: 'Kamera Scanner QR', icon: 'qr_code_scanner' }
                ]"
                :key="cameraType.name"
                :default-opened="index === 0"
                class="settings-expansion q-mb-md"
              >
                <template v-slot:header>
                  <q-item-section avatar>
                    <q-icon :name="cameraType.icon" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-weight-medium">{{ cameraType.label }}</q-item-label>
                  </q-item-section>
                </template>

                <q-card flat bordered class="q-ma-sm">
                  <q-card-section>
                    <!-- USB Camera Selection -->
                    <div class="camera-config-section q-mb-md">
                      <div class="text-subtitle2 text-weight-medium q-mb-sm">USB Kamera</div>
                      <q-select
                        :model-value="cameraType.name === 'plate' ? selectedPlateCam : 
                                      cameraType.name === 'driver' ? selectedDriverCam : selectedScannerCam"
                        @update:model-value="cameraType.name === 'plate' ? updatePlateCamera : 
                                           cameraType.name === 'driver' ? updateDriverCamera : updateScannerCamera"
                        :options="availableCameras"
                        label="Pilih USB Camera"
                        option-value="deviceId"
                        option-label="label"
                        clearable
                        emit-value
                        map-options
                        outlined
                        dense
                      />
                      <div class="text-caption text-grey-6 q-mt-xs" v-if="availableCameras.length === 0">
                        Tidak ada USB kamera terdeteksi. Klik "Refresh Kamera" untuk coba lagi.
                      </div>
                    </div>

                    <!-- CCTV Configuration -->
                    <div class="camera-config-section q-mb-md">
                      <div class="text-subtitle2 text-weight-medium q-mb-sm">Konfigurasi CCTV</div>
                      <div class="row q-col-gutter-sm">
                        <div class="col-12 col-sm-6">
                          <q-input
                            :model-value="cameraType.name === 'plate' ? plateCameraIp : 
                                         cameraType.name === 'driver' ? driverCameraIp : scannerCameraIp"
                            @update:model-value="cameraType.name === 'plate' ? setPlateCameraIP : 
                                               cameraType.name === 'driver' ? setDriverCameraIP : updateScannerCameraUrl"
                            label="IP Address CCTV"
                            placeholder="192.168.1.100"
                            outlined
                            dense
                          />
                        </div>
                        <div class="col-12 col-sm-6">
                          <q-input
                            :model-value="cameraType.name === 'plate' ? plateCameraRtspPath : 
                                         cameraType.name === 'driver' ? driverCameraRtspPath : scannerCameraRtspPath"
                            @update:model-value="val => {
                              if (cameraType.name === 'plate') plateCameraRtspPath = val;
                              else if (cameraType.name === 'driver') driverCameraRtspPath = val;
                              else scannerCameraRtspPath = val;
                            }"
                            label="RTSP Path"
                            placeholder="/Streaming/Channels/101"
                            outlined
                            dense
                          />
                        </div>
                        <div class="col-12 col-sm-6">
                          <q-input
                            :model-value="cameraType.name === 'plate' ? plateCameraUsername : 
                                         cameraType.name === 'driver' ? driverCameraUsername : scannerCameraUsername"
                            @update:model-value="cameraType.name === 'plate' ? updatePlateCameraUsername : 
                                               cameraType.name === 'driver' ? updateDriverCameraUsername : updateScannerCameraUsername"
                            label="Username"
                            placeholder="admin"
                            outlined
                            dense
                          />
                        </div>
                        <div class="col-12 col-sm-6">
                          <q-input
                            :model-value="cameraType.name === 'plate' ? plateCameraPassword : 
                                         cameraType.name === 'driver' ? driverCameraPassword : scannerCameraPassword"
                            @update:model-value="cameraType.name === 'plate' ? updatePlateCameraPassword : 
                                               cameraType.name === 'driver' ? updateDriverCameraPassword : updateScannerCameraPassword"
                            label="Password"
                            type="password"
                            outlined
                            dense
                          />
                        </div>
                      </div>
                    </div>

                    <!-- Capture Mode Configuration -->
                    <div class="camera-config-section">
                      <div class="text-subtitle2 text-weight-medium q-mb-sm">Mode Capture Default</div>
                      <div class="row q-col-gutter-sm">
                        <div class="col-12 col-sm-4">
                          <q-select
                            :model-value="cameraType.name === 'plate' ? plateCameraDefaultMode : 
                                         cameraType.name === 'driver' ? driverCameraDefaultMode : scannerCameraDefaultMode"
                            @update:model-value="val => {
                              if (cameraType.name === 'plate') plateCameraDefaultMode = val;
                              else if (cameraType.name === 'driver') driverCameraDefaultMode = val;
                              else scannerCameraDefaultMode = val;
                            }"
                            :options="captureModeOptions"
                            label="Mode Default"
                            emit-value
                            map-options
                            outlined
                            dense
                          />
                          <div class="text-caption text-grey-6 q-mt-xs">
                            Metode capture default untuk kamera ini
                          </div>
                        </div>
                        <div class="col-12 col-sm-4">
                          <q-input
                            :model-value="cameraType.name === 'plate' ? plateCameraSnapshotUrl : 
                                         cameraType.name === 'driver' ? driverCameraSnapshotUrl : scannerCameraSnapshotUrl"
                            @update:model-value="val => {
                              if (cameraType.name === 'plate') plateCameraSnapshotUrl = val;
                              else if (cameraType.name === 'driver') driverCameraSnapshotUrl = val;
                              else scannerCameraSnapshotUrl = val;
                            }"
                            label="Custom Snapshot URL"
                            placeholder="/cgi-bin/snapshot.cgi"
                            outlined
                            dense
                          />
                        </div>
                        <div class="col-12 col-sm-4">
                          <q-input
                            :model-value="cameraType.name === 'plate' ? plateCameraHttpPort : 
                                         cameraType.name === 'driver' ? driverCameraHttpPort : scannerCameraHttpPort"
                            @update:model-value="val => {
                              if (cameraType.name === 'plate') plateCameraHttpPort = val;
                              else if (cameraType.name === 'driver') driverCameraHttpPort = val;
                              else scannerCameraHttpPort = val;
                            }"
                            type="number"
                            label="HTTP Port"
                            placeholder="80"
                            outlined
                            dense
                          />
                        </div>
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </q-expansion-item>

            </div>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="row justify-end q-pt-md" style="border-top: 1px solid #e0e0e0;">
          <q-btn
            @click="onSaveSettings"
            color="primary"
            size="lg"
            icon="save"
            label="Simpan Pengaturan"
            class="q-px-xl"
            :loading="false"
          />
        </div>
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
import ls from "localstorage-slim";

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
const prefix = ref(''); // Default prefix setting

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

// Capture mode settings for each camera
const captureModeOptions = [
  { label: 'Auto (Detect Best)', value: 'auto' },
  { label: 'Snapshot (HTTP)', value: 'snapshot' },
  { label: 'RTSP (Stream)', value: 'rtsp' }
];

const plateCameraDefaultMode = ref('auto');
const plateCameraSnapshotUrl = ref('');
const plateCameraHttpPort = ref(80);

const driverCameraDefaultMode = ref('auto');
const driverCameraSnapshotUrl = ref('');
const driverCameraHttpPort = ref(80);

const scannerCameraDefaultMode = ref('auto');
const scannerCameraSnapshotUrl = ref('');
const scannerCameraHttpPort = ref(80);

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
    prefix.value = newSettings.prefix || ls.get('prefix') || '';
    printerName.value = newSettings.printerName || null;
    paperSize.value = newSettings.paperSize || '58mm';
    autoPrint.value = newSettings.autoPrint || true;
    serialPort.value = newSettings.SERIAL_PORT || '';
    captureInterval.value = newSettings.CAPTURE_INTERVAL || 5000;
    wsUrl.value = newSettings.WS_URL || '';
    useExternalAlpr.value = newSettings.USE_EXTERNAL_ALPR || false;
    // darkMode.value = newSettings.darkMode || false;
    
    // Camera settings
    selectedPlateCam.value = newSettings.PLATE_CAM_DEVICE_ID || null;
    plateCameraIp.value = newSettings.PLATE_CAM_IP || '';
    plateCameraUsername.value = newSettings.PLATE_CAM_USERNAME || '';
    plateCameraPassword.value = newSettings.PLATE_CAM_PASSWORD || '';
    plateCameraRtspPath.value = newSettings.PLATE_CAM_RTSP_PATH || '';
    plateCameraDefaultMode.value = newSettings.PLATE_CAM_DEFAULT_MODE || 'auto';
    plateCameraSnapshotUrl.value = newSettings.PLATE_CAM_SNAPSHOT_URL || '';
    plateCameraHttpPort.value = newSettings.PLATE_CAM_HTTP_PORT || 80;
    
    selectedDriverCam.value = newSettings.DRIVER_CAM_DEVICE_ID || null;
    driverCameraIp.value = newSettings.DRIVER_CAM_IP || '';
    driverCameraUsername.value = newSettings.DRIVER_CAM_USERNAME || '';
    driverCameraPassword.value = newSettings.DRIVER_CAM_PASSWORD || '';
    driverCameraRtspPath.value = newSettings.DRIVER_CAM_RTSP_PATH || '';
    driverCameraDefaultMode.value = newSettings.DRIVER_CAM_DEFAULT_MODE || 'auto';
    driverCameraSnapshotUrl.value = newSettings.DRIVER_CAM_SNAPSHOT_URL || '';
    driverCameraHttpPort.value = newSettings.DRIVER_CAM_HTTP_PORT || 80;
    
    selectedScannerCam.value = newSettings.SCANNER_CAM_DEVICE_ID || null;
    scannerCameraIp.value = newSettings.SCANNER_CAM_IP || '';
    scannerCameraUsername.value = newSettings.SCANNER_CAM_USERNAME || '';
    scannerCameraPassword.value = newSettings.SCANNER_CAM_PASSWORD || '';
    scannerCameraRtspPath.value = newSettings.SCANNER_CAM_RTSP_PATH || '';
    scannerCameraDefaultMode.value = newSettings.SCANNER_CAM_DEFAULT_MODE || 'auto';
    scannerCameraSnapshotUrl.value = newSettings.SCANNER_CAM_SNAPSHOT_URL || '';
    scannerCameraHttpPort.value = newSettings.SCANNER_CAM_HTTP_PORT || 80;
    
    // Former global settings
    wsUrl.value = newSettings.WS_URL || 'ws://localhost:8765';
    useExternalAlpr.value = newSettings.USE_EXTERNAL_ALPR || false;
    // darkMode.value = newSettings.darkMode || false;
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
      prefix: prefix.value,
      SERIAL_PORT: serialPort.value,
      printerName: printerName.value,
      paperSize: paperSize.value,
      autoPrint: autoPrint.value,
      PLATE_CAM_DEVICE_ID: selectedPlateCam.value,
      PLATE_CAM_IP: plateCameraIp.value,
      PLATE_CAM_USERNAME: plateCameraUsername.value,
      PLATE_CAM_PASSWORD: plateCameraPassword.value,
      PLATE_CAM_RTSP_PATH: plateCameraRtspPath.value,
      PLATE_CAM_DEFAULT_MODE: plateCameraDefaultMode.value,
      PLATE_CAM_SNAPSHOT_URL: plateCameraSnapshotUrl.value,
      PLATE_CAM_HTTP_PORT: plateCameraHttpPort.value,
      DRIVER_CAM_DEVICE_ID: selectedDriverCam.value,
      DRIVER_CAM_IP: driverCameraIp.value,
      DRIVER_CAM_USERNAME: driverCameraUsername.value,
      DRIVER_CAM_PASSWORD: driverCameraPassword.value,
      DRIVER_CAM_RTSP_PATH: driverCameraRtspPath.value,
      DRIVER_CAM_DEFAULT_MODE: driverCameraDefaultMode.value,
      DRIVER_CAM_SNAPSHOT_URL: driverCameraSnapshotUrl.value,
      DRIVER_CAM_HTTP_PORT: driverCameraHttpPort.value,
      SCANNER_CAM_DEVICE_ID: selectedScannerCam.value,
      SCANNER_CAM_IP: scannerCameraIp.value,
      SCANNER_CAM_USERNAME: scannerCameraUsername.value,
      SCANNER_CAM_PASSWORD: scannerCameraPassword.value,
      SCANNER_CAM_RTSP_PATH: scannerCameraRtspPath.value,
      SCANNER_CAM_DEFAULT_MODE: scannerCameraDefaultMode.value,
      SCANNER_CAM_SNAPSHOT_URL: scannerCameraSnapshotUrl.value,
      SCANNER_CAM_HTTP_PORT: scannerCameraHttpPort.value,
      CAPTURE_INTERVAL: parseInt(captureInterval.value, 10) || 5000,
      
      // Former global settings now in gate settings
      WS_URL: wsUrl.value || 'ws://localhost:8765',
      USE_EXTERNAL_ALPR: useExternalAlpr.value || false,
      // darkMode: darkMode.value || false,
      LOCATION: selectedLocation.value,
    };
    
    console.log('Saving consolidated settings:', settingsToSave);
    await settingsService.saveGateSettings(settingsToSave);
    
    // Save prefix to localStorage
    ls.set('prefix', prefix.value);
    
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
    // Initialize prefix from localStorage
    prefix.value = ls.get('prefix') || '';
    
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
  background-color: rgba(255, 255, 255, 0.98);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.125);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

:deep(.q-dialog__backdrop.fixed-full) {
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
}

.settings-content {
  padding: 0 8px;
}

.settings-content::-webkit-scrollbar {
  width: 8px;
}

.settings-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

.settings-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
}

.settings-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.5);
}

.settings-card {
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.3s ease;
}

.settings-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.settings-section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1976d2;
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.settings-expansion {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.settings-expansion :deep(.q-expansion-item__container) {
  border-radius: 8px;
}

.settings-expansion :deep(.q-item) {
  padding: 12px 16px;
  background-color: #f8f9fa;
  color: #424242;
}

.settings-expansion :deep(.q-item:hover) {
  background-color: #e3f2fd;
  color: #1565c0;
}

.camera-config-section {
  padding: 12px;
  background-color: #fafafa;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.camera-config-section .text-subtitle2 {
  color: #1976d2;
  font-weight: 600;
  margin-bottom: 8px;
}

/* Input field improvements */
:deep(.q-field--outlined .q-field__control) {
  border-radius: 8px;
  background-color: #ffffff;
}

:deep(.q-field--outlined .q-field__control:before) {
  border-color: #e0e0e0;
}

:deep(.q-field--dense .q-field__control) {
  height: 40px;
  background-color: #ffffff;
}

:deep(.q-field--focused .q-field__control) {
  background-color: #ffffff !important;
}

:deep(.q-field--focused .q-field__native) {
  color: #424242 !important;
}

:deep(.q-select__dropdown-icon) {
  color: #1976d2;
}

/* Toggle improvements */
:deep(.q-toggle__inner) {
  color: #1976d2;
}

/* Button improvements */
:deep(.q-btn) {
  border-radius: 8px;
  text-transform: none;
  font-weight: 500;
}

/* Responsive adjustments */
@media (max-width: 1023px) {
  .settings-content {
    padding: 0 4px;
  }
  
  .settings-card {
    margin-bottom: 16px !important;
  }
}

@media (max-width: 599px) {
  .row.q-col-gutter-sm > .col-12:not(:last-child) {
    margin-bottom: 8px;
  }
  
  .camera-config-section {
    padding: 8px;
  }
  
  .settings-section-title {
    font-size: 14px;
  }
}

/* Animation for expansion items */
.settings-expansion :deep(.q-expansion-item__content) {
  transition: all 0.3s ease;
}

/* Status indicators */
.text-caption {
  font-size: 12px;
  line-height: 1.4;
  color: #666666 !important;
}

/* Ensure proper text contrast */
:deep(.q-item-label) {
  color: #424242 !important;
}

:deep(.q-expansion-item__label) {
  color: #424242 !important;
  font-weight: 500;
}

/* Input label improvements */
:deep(.q-field__label) {
  color: #424242 !important;
}

:deep(.q-field--focused .q-field__label) {
  color: #1976d2 !important;
}

/* Card section improvements */
:deep(.q-card__section) {
  padding: 16px 20px;
}

/* Text color improvements for better visibility */
:deep(.q-field__control) {
  color: #424242;
}

:deep(.q-field__native) {
  color: #424242 !important;
}

:deep(.q-input .q-field__native) {
  color: #424242 !important;
}

:deep(.q-select .q-field__native) {
  color: #424242 !important;
}

:deep(.q-field__input) {
  color: #424242 !important;
}

:deep(.q-toggle__label) {
  color: #424242 !important;
}

/* Placeholder text */
:deep(.q-field__input::placeholder) {
  color: #999999 !important;
}

:deep(input::placeholder) {
  color: #999999 !important;
}

/* Selected option text in dropdowns */
:deep(.q-select__selection) {
  color: #424242 !important;
}

/* Dropdown options */
:deep(.q-menu .q-item) {
  color: #424242 !important;
}

/* Input text when typing */
:deep(input[type="text"]) {
  color: #424242 !important;
}

:deep(input[type="number"]) {
  color: #424242 !important;
}

:deep(input[type="password"]) {
  color: #424242 !important;
}

/* Ensure all input elements have proper contrast */
:deep(.q-field .q-field__control .q-field__native) {
  color: #424242 !important;
  background-color: transparent !important;
}

:deep(.q-field .q-field__control input) {
  color: #424242 !important;
  background-color: transparent !important;
}

/* Fix for autofilled inputs */
:deep(input:-webkit-autofill) {
  -webkit-text-fill-color: #424242 !important;
  -webkit-box-shadow: 0 0 0px 1000px #ffffff inset !important;
}

:deep(input:-webkit-autofill:focus) {
  -webkit-text-fill-color: #424242 !important;
  -webkit-box-shadow: 0 0 0px 1000px #ffffff inset !important;
}

/* Ensure text remains visible in all states */
:deep(.q-field--readonly .q-field__native) {
  color: #424242 !important;
}

:deep(.q-field--disable .q-field__native) {
  color: #757575 !important;
}

/* Force text visibility in all scenarios */
* {
  -webkit-text-fill-color: initial !important;
}

:deep(.q-field__native),
:deep(.q-field__input),
:deep(input) {
  -webkit-text-fill-color: #424242 !important;
  color: #424242 !important;
}

/* Specific fixes for different input types */
:deep(.q-select .q-field__native span) {
  color: #424242 !important;
}

/* Override any inherited transparency */
:deep(.q-field__control) {
  background-color: #ffffff !important;
}

:deep(.q-field--outlined .q-field__control) {
  background-color: #ffffff !important;
}

/* Help text improvements */
.text-grey-6 {
  color: #757575 !important;
}

/* Separator styling */
:deep(.q-separator) {
  background-color: #e0e0e0;
  opacity: 0.6;
}
</style>
