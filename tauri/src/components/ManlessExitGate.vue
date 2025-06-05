
<template>
  <div
    class="manless-entry fixed-center full-width"
    :class="[{ 'dark-mode': isDark }, $attrs.class]"
  >
    <div class="row q-gutter-sm">
      <div class="col-6 q-gutter-md q-mt-sm">
        <!-- Camera Section -->
        <div class="column">
          <!-- Left side - License Plate Camera -->
          <q-card
            flat
            class="camera-card bg-transparent"
            style="transform: scale(0.95); margin-top: -2vh"
          >
            <q-btn
              dense
              push
              :loading="isCapturing"
              :disable="isCapturing"
              label="Manual Capture"
              color="white"
              text-color="primary"
              class="text-bold absolute-bottom-left z-top q-ma-lg"
              @click="onPlateCaptured"
              icon="camera"
            />

            <Camera
              v-show="!base64String"
              ref="plateCameraRef"
              :cameraUrl="plateCameraUrl"
              :username="plateCameraCredentials.username"
              :password="plateCameraCredentials.password"
              :ipAddress="plateCameraCredentials.ip_address"
              :deviceId="plateCameraDeviceId"
              :fileName="'plate'"
              :isInterval="isAutoCaptureActive"
              :intervalTime="3000"
              cameraLocation="plate"
              :cameraType="plateCameraType"
              @captured="onPlateCaptured"
              @error="onCameraError"
              class="camera-feed"
              label="License Plate Camera"
            />
            <q-btn
              v-if="plateCameraType === 'cctv' && !base64String"
              icon="refresh"
              dense flat round
              @click="plateCameraRef?.fetchCameraImage()"
              class="absolute-top-right q-ma-xs"
              style="z-index: 1; background-color: rgba(0,0,0,0.3); margin-top: 35px;"
              color="white"
            >
              <q-tooltip>Refresh CCTV Image</q-tooltip>
            </q-btn>
            <q-btn
              v-if="plateCameraType === 'cctv'"
              icon="photo_camera"
              dense flat round
              @click="captureAndShowCctvImage('plate')"
              class="absolute-top-right q-ma-xs"
              style="z-index: 1; background-color: rgba(0,0,0,0.3); margin-top: 70px;"
              color="white"
            >
              <q-tooltip>Capture CCTV Image (Plat)</q-tooltip>
            </q-btn>

            <Camera
              v-show="base64String"
              ref="plateCameraRef"
              :manual-base64="base64String"
              :username="plateCameraCredentials.username"
              :password="plateCameraCredentials.password"
              :ipAddress="plateCameraCredentials.ip_address"
              :deviceId="plateCameraDeviceId"
              :fileName="'plate'"
              :isInterval="isAutoCaptureActive"
              :intervalTime="3000"
              cameraLocation="plate"
              @captured="onPlateCaptured"
              :cameraType="plateCameraType === 'usb' ? 'usb' : 'manual'"
              @error="onCameraError"
              class="camera-feed"
              label="License Plate Camera"
              style="margin-top: -2dvh"
            />

            <div v-if="plateResult?.plate_number && capturedPlate">
              <q-card
                class="plate-detection-overlay bg-dark q-pa-xs"
                :class="{ 'bg-white ': isDark }"
              >
                <q-badge
                  style="top: -10px; left: 7px"
                  class="bg-dark text-white absolute-top-left inset-shadow"
                  label="Plat Image"
                />
                <img
                  :src="capturedPlate"
                  alt="Detected Plate"
                  class="plate-detection-image"
                />
              </q-card>
            </div>
          </q-card>

          <!-- Right side - Driver Camera -->
          <q-card
            flat
            class="camera-card bg-transparent q-mb-lg"
            style="transform: scale(0.95); margin-top: -1vh"
          >
            <Camera
              ref="driverCameraRef"
              :cameraUrl="driverCameraUrl"
              :username="driverCameraCredentials.username"
              :password="driverCameraCredentials.password"
              :ipAddress="driverCameraCredentials.ip_address"
              :deviceId="driverCameraDeviceId"
              :fileName="'driver'"
              :isInterval="false"
              cameraLocation="driver"
              :cameraType="driverCameraType"
              @error="onCameraError"
              class="camera-feed"
              label="Driver Camera"
            />
            <q-btn
              v-if="driverCameraType === 'cctv'"
              icon="refresh"
              dense flat round
              @click="driverCameraRef?.fetchCameraImage()"
              class="absolute-top-right q-ma-xs"
              style="z-index: 1; background-color: rgba(0,0,0,0.3); margin-top: 35px;"
              color="white"
            >
              <q-tooltip>Refresh CCTV Image</q-tooltip>
            </q-btn>
            <q-btn
              v-if="driverCameraType === 'cctv'"
              icon="photo_camera"
              dense flat round
              @click="captureAndShowCctvImage('driver')"
              class="absolute-top-right q-ma-xs"
              style="z-index: 1; background-color: rgba(0,0,0,0.3); margin-top: 70px;"
              color="white"
            >
              <q-tooltip>Capture CCTV Image (Driver)</q-tooltip>
            </q-btn>
          </q-card>
        </div>
      </div>
      <div class="col-6 full-height items-center justify-center">
        <q-card
          flat
          :class="isDark ? 'text-white' : 'bg-transparent text-primary'"
          style="height: 30px"
        >
          <div class="row items-center justify-end">
            <div class="row items-center justify-start q-mr-md">
              <Clock />
            </div>
            <div class="row items-center justify-between q-gutter-md">
              <ConnectionIndicator class="indicator-item" />
              <!-- Server and WebSocket indicators removed -->
              <!-- <ConnectionIndicator :is-connected="isBackendConnected" label="Server" class="indicator-item" />
                <ConnectionIndicator :is-connected="isALPRConnected" label="ALPR" class="indicator-item" icon="videocam"
                iconOff="videocam_off" /> -->
              <q-toggle
                :model-value="isDark"
                @update:model-value="toggleDarkMode"
                color="yellow"
                icon="dark_mode"
                class="text-white"
              />

              <q-btn
                color="primary"
                icon="home"
                flat
                dense
                @click="[$router.push({ path: '/' }), ls.remove('gateMode')]"
              />
            </div>
          </div>
        </q-card>
        <!-- <q-separator spaced    /> -->
        <div class="flex row q-mt-lg">
          <div class="col-6">
            <div class="column">
              <div class="col q-mb-md q-mt-md">
                <!-- NOMOR TIKET -->
                <q-chip
                  square
                  outline
                  class="q-py-lg text-h6 text-dark q-mb-md relative"
                  :class="isDark ? 'text-white' : 'text-dark'"
                  style="width: 90%"
                  :label="transactionData?.id"
                >
                  <q-badge
                    color="primary"
                    text-color="white"
                    label="No. Tiket "
                    class="q-mb-md absolute-top-left"
                    style="top: -8px; left: 5px"
                  />
                </q-chip>
                <!-- PLAT NOMOR  -->
                <PlatNomor
                  style="transform: scale(1.1)"
                  class="q-mt-md q-ml-md"
                  badge="Entry Plate Number"
                  :plate_number="transactionData?.entry_plate_number"
                />
                <PlatNomor
                  style="transform: scale(1.1)"
                  class="q-mt-md q-ml-md"
                  badge="Exit Plate Number"
                  :plate_number="plateResult?.plate_number"
                />
              </div>
            </div>
          </div>

          <div class="col-5 q-pl-md">
            <q-timeline color="grey-6" layout="dense">
              <q-timeline-entry
                :title="
                  transactionData?.entry_time
                    ? formatDate(transactionData.entry_time)
                    : '--/--/--'
                "
                subtitle="Entry Date"
                icon="today"
              />
              <q-timeline-entry
                :title="
                  transactionData?.entry_time
                    ? formatTime(transactionData.entry_time)
                    : '--:--:--'
                "
                subtitle="Entry Time"
                icon="schedule"
              />
              <q-timeline-entry
                :title="
                  transactionData?.entry_time
                    ? manlessStore.parkingDuration(transactionData.entry_time)
                    : '--:--:--'
                "
                subtitle="Duration"
                icon="timer"
              />
            </q-timeline>
          </div>
        </div>
        <div class="column">
          <!-- TOTAL BAYAR  -->
          <q-card
            bordered
            class="glass text-dark q-pr-sm q-mr-xl relative full-width"
          >
            <div>
              <q-badge
                color="primary"
                text-color="white"
                label="Parking Fee"
                class="text-h5 q-mb-md absolute-top-left"
                style="top: -8px; left: 5px"
              />
            </div>
            <!-- style="width: 40vw" -->
            <q-card-section>
              <div
                class="text-right text-weight-bold"
                :class="isDark ? 'text-white' : 'text-dark'"
                style="
                  font-size: clamp(2rem, 4rem, 5rem);
                  font-family: 'Courier Prime', monospace;
                "
              >
                0
                <!-- {{
                    transaksiStore.biayaParkir
                      .toLocaleString("id-ID", {
                        style: "currency",
                        currency: "IDR",
                      })
                      .split(",")[0]
                  }} -->
              </div>
            </q-card-section>
          </q-card>

          <!-- Activity Log -->
          <div class="col-4 q-mt-md">
            <q-card
              bordered
              flat
              class="log-card q-pt-md"
              :class="{ 'bg-dark text-white': isDark }"
            >
              <div>
                <q-badge
                  style="top: -8px; left: 5px"
                  class="absolute-top-left text-white"
                  :class="{ 'text-white': isDark }"
                  >Recent Activity</q-badge
                >
              </div>
              <q-card-section>
                <q-scroll-area style="height: 10dvh">
                  <q-list dense>
                    <q-item
                      v-for="(log, index) in activityLogs.slice(0, 10)"
                      :key="index"
                    >
                      <q-item-section>
                        <q-item-label
                          :class="{
                            'text-negative': log.isError,
                            'text-white': isDark && !log.isError,
                            'text-dark': !isDark && !log.isError,
                          }"
                        >
                          {{ log.message }}
                        </q-item-label>
                        <q-item-label
                          caption
                          :class="{ 'text-grey-5': isDark }"
                        >
                          {{ log.timestamp }}
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-scroll-area>
              </q-card-section>
            </q-card>
          </div>

          <div class="col-8 column justify-between">
            <q-card class="q-mt-sm">
              <q-card-section>
                <div class="row items-center justify-between">
                  <div
                    class="gate-status text-h5"
                    :class="{
                      'text-positive': gateStatus === 'OPEN',
                      'text-negative': gateStatus === 'CLOSED',
                    }"
                  >
                    <q-chip
                      outline
                      :color="gateStatus === 'OPEN' ? 'positive' : 'negative'"
                      text-color="white"
                      icon="door_front"
                    >
                      Gate Status: {{ gateStatus }}
                    </q-chip>
                  </div>
                  <div class="row q-gutter-md">
                    <q-btn
                      dense
                      push
                      icon="qr_code_scanner"
                      color="primary"
                      class="q-mt-md"
                      @click="showQRScanner = true"
                    >
                      <q-tooltip>Scan QR Code</q-tooltip>
                    </q-btn>
                    <q-btn
                      dense
                      push
                      color="positive"
                      icon="door_front"
                      label="PROCESS EXIT"
                      :loading="isProcessing"
                      :disable="isProcessing || gateStatus === 'OPEN'"
                      @click="processExitTransaction"
                      class="text-bold"
                      size="md"
                    />
                    <q-btn
                      dense
                      push
                      color="primary"
                      icon="settings"
                      @click="openSettings"
                      class="text-bold"
                      size="md"
                    />
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- <QRCodeScannerDialog
    v-model="showQRScanner"
    @hide="showQRScanner = false"
    @scanned="onQRCodeScanned"
  /> -->
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch, useAttrs } from 'vue';
import { useQuasar } from 'quasar';
import { invoke } from '@tauri-apps/api/core';
import ls from 'localstorage-slim';

import { useThemeStore } from '../stores/theme';
import { useManlessStore } from 'src/stores/manless-store';
import { useComponentStore } from 'src/stores/component-store'; // May not be needed if gateStore handles all hardware
import { useGateStore } from 'src/stores/gate-store';

import Camera from './Camera.vue';
import Clock from './Clock.vue';
import SettingsDialog from './SettingsDialog.vue';
import ConnectionIndicator from './ConnectionIndicator.vue';
import PlatNomor from './PlatNomor.vue';
import QRCodeScannerDialog from './QRCodeScannerDialog.vue'; // Keep for ExitGate

import { api, detectedPlates as globalDetectedPlates } from 'src/boot/axios';
import { localDbs } from 'src/boot/pouchdb'; // Import PouchDB instance
import { formatDate, formatTime } from 'src/utils/time-util';

const themeStore = useThemeStore();
const manlessStore = useManlessStore();
const componentStore = useComponentStore(); // Evaluate if still needed
const gateStore = useGateStore();
const $q = useQuasar();

const attrs = useAttrs();
defineOptions({
  inheritAttrs: false,
});

const isDark = computed(() => themeStore.isDark);

// Camera state
const plateCameraRef = ref(null);
const driverCameraRef = ref(null);
const base64String = ref(''); // For manual camera feed from Camera.vue
const capturedPlate = ref(null);

// State for CCTV image capture and display
const cctvImageLoading = ref(false);
const showCctvImageDialog = ref(false);
const cctvImageUrl = ref('');
const currentCctvConfig = ref(null); // Base64 image of the captured plate for display
const capturedDriver = ref(null); // Base64 image of the captured driver for display

// ALPR and Processing State
const plateResult = ref(null); // Holds the latest ALPR result object { plate_number, confidence, plate_image, ... }
const displayedPlateInfo = ref([]); // Primarily for UI, often mirrors [plateResult.value]
const isCapturing = ref(false); // True when ALPR processing is active
const isProcessing = ref(false); // General async operation guard (e.g., API calls, gate commands)
const error = ref(null); // Holds error messages for UI
const errorDialog = ref(false); // Controls visibility of a generic error dialog

// Gate and System State
const gateStatus = ref('CLOSED'); // 'OPEN', 'CLOSED', 'OPENING', 'CLOSING'
const isAutoCaptureActive = ref(true); // Controls interval capture on plate camera
const activityLogs = ref([]);

// Settings (loaded from localStorage)
import { useSettingsService } from 'src/stores/settings-service'; // Tambahkan import

const settingsService = useSettingsService();
const gateSettings = computed(() => settingsService.gateSettings);

const plateCameraType = computed(() => {
  if (gateSettings.value?.PLATE_CAM_DEVICE_ID) return 'usb';
  if (gateSettings.value?.PLATE_CAM_URL) return 'cctv';
  return 'cctv'; // Default atau bisa juga null/undefined sesuai kebutuhan
});

const driverCameraType = computed(() => {
  if (gateSettings.value?.DRIVER_CAM_DEVICE_ID) return 'usb';
  if (gateSettings.value?.DRIVER_CAM_URL) return 'cctv';
  return 'cctv'; // Default atau bisa juga null/undefined sesuai kebutuhan
});

// Camera URLs dan Device IDs diambil dari gateSettings
const plateCameraUrl = computed(() => gateSettings.value?.PLATE_CAM_URL || '');
const driverCameraUrl = computed(() => gateSettings.value?.DRIVER_CAM_URL || '');
const plateCameraDeviceId = computed(() => gateSettings.value?.PLATE_CAM_DEVICE_ID || null);
const driverCameraDeviceId = computed(() => gateSettings.value?.DRIVER_CAM_DEVICE_ID || null);

// Helper function to parse RTSP URL for credentials
const parseRtspUrl = (url, usernameSetting, passwordSetting, ipSetting) => {
  if (!url) return { username: usernameSetting || 'admin', password: passwordSetting || 'password', ip_address: ipSetting || '' };
  try {
    const urlObj = new URL(url);
    const username = usernameSetting || urlObj.username || 'admin';
    const password = passwordSetting || urlObj.password || 'password';
    const ip_address = ipSetting || urlObj.hostname || '';
    return { username, password, ip_address };
  } catch (e) {
    // Fallback for URLs that might not be standard (e.g., missing protocol for regex)
    // Or if URL parsing fails for any other reason
    const match = url.match(/^(?:rtsp:\/\/)?(?:([^:@\/]+):?([^:@\/]+)?@)?([^:\/?#]+)/i);
    if (match) {
      const username = usernameSetting || match[1] || 'admin';
      const password = passwordSetting || match[2] || 'password';
      const ip_address = ipSetting || match[3] || '';
      return { username, password, ip_address };
    }
    // Ultimate fallback if regex also fails
    return { username: usernameSetting || 'admin', password: passwordSetting || 'password', ip_address: ipSetting || '' };
  }
};

const plateCameraCredentials = computed(() => {
  return parseRtspUrl(
    gateSettings.value?.PLATE_CAM_URL,
    gateSettings.value?.PLATE_CAM_USERNAME,
    gateSettings.value?.PLATE_CAM_PASSWORD,
    gateSettings.value?.PLATE_CAM_IP
  );
});

const driverCameraCredentials = computed(() => {
  return parseRtspUrl(
    gateSettings.value?.DRIVER_CAM_URL,
    gateSettings.value?.DRIVER_CAM_USERNAME,
    gateSettings.value?.DRIVER_CAM_PASSWORD,
    gateSettings.value?.DRIVER_CAM_IP
  );
});
const exitGatePort = ref(ls.get('serialPortExit') || ''); // Specific serial port for exit gate

// Exit Gate Specific State
const showQRScanner = ref(false);
const transactionData = ref(null); // { id, entry_plate_number, entry_time, ... }
const isLoadingTransaction = ref(false);

// --- PouchDB Functions ---
const fetchTransactionByTicketId = async (ticketId) => {
  isLoadingTransaction.value = true;
  addActivityLog(`Fetching transaction for ticket: ${ticketId}`);
  try {
    const doc = await localDbs.transactions.get(ticketId);
    transactionData.value = doc;
    addActivityLog(`Transaction found: ${doc._id}`);
    $q.notify({ type: 'positive', message: 'Transaction data loaded.' });
  } catch (err) {
    console.error('Error fetching transaction by ticket ID:', err);
    addActivityLog(`Error fetching transaction for ticket ${ticketId}: ${err.message}`, true);
    transactionData.value = null;
    $q.notify({ type: 'negative', message: 'Transaction not found or error fetching data.' });
  }
  isLoadingTransaction.value = false;
};

const fetchTransactionByPlateNumber = async (plateNumber) => {
  isLoadingTransaction.value = true;
  addActivityLog(`Fetching transaction for plate: ${plateNumber}`);
  try {
    const result = await localDbs.transactions.find({
      selector: { 
        plate_number: plateNumber, // Field name from ManlessEntryGate save
        status: 'entry' 
      },
      sort: [{ entry_time: 'desc' }], 
      limit: 1
    });
    if (result.docs.length > 0) {
      transactionData.value = result.docs[0];
      addActivityLog(`Transaction found for plate ${plateNumber}: ${result.docs[0]._id}`);
      $q.notify({ type: 'positive', message: 'Transaction data loaded for plate.' });
    } else {
      addActivityLog(`No active transaction found for plate: ${plateNumber}`);
      transactionData.value = null;
      $q.notify({ type: 'warning', message: 'No active transaction found for this plate number.' });
    }
  } catch (err) {
    console.error('Error fetching transaction by plate number:', err);
    addActivityLog(`Error fetching transaction for plate ${plateNumber}: ${err.message}`, true);
    transactionData.value = null;
    $q.notify({ type: 'negative', message: 'Error fetching transaction data by plate.' });
  }
  isLoadingTransaction.value = false;
};

// --- Watchers ---
watch(isDark, (newVal) => {
  ls.set('darkMode', newVal);
  document.body.classList.toggle('body--dark', newVal);
});

watch(globalDetectedPlates, (newPlates) => {
  if (newPlates && newPlates.length > 0) {
    const latestPlate = newPlates[0]; // Assuming the first one is the most relevant
    // Avoid redundant updates if the plate is already processed
    if (!plateResult.value || plateResult.value.plate_number !== latestPlate.plate_number) {
      plateResult.value = { ...latestPlate };
      addActivityLog(`Plate auto-detected via global source: ${latestPlate.plate_number}`);
      console.log('Auto-detected plate from global source (ExitGate):', latestPlate);
    }
  }
}, { deep: true });

watch(plateResult, (newResult) => {
  if (newResult && newResult.plate_number) {
    const imageBase64 = newResult.plate_image || newResult.image_base64; // Prefer plate_image from ALPR result
    capturedPlate.value = imageBase64 ? `data:image/jpeg;base64,${imageBase64}` : null;
    displayedPlateInfo.value = [{ ...newResult }];
    if (base64String.value !== capturedPlate.value) { // Sync with manual camera feed if used
        base64String.value = capturedPlate.value;
    }
  } else {
    capturedPlate.value = null;
    displayedPlateInfo.value = [];
    if (base64String.value !== null) { // Clear manual feed if result is cleared
        base64String.value = null;
    }
  }
}, { deep: true });

watch(base64String, (newValue) => {
  // If Camera.vue emits a manual capture, this updates the ref for it to display
  if (newValue && plateCameraRef.value) {
    plateCameraRef.value.setManualBase64(newValue);
  }
});

const toggleDarkMode = () => {
  themeStore.toggleDarkMode();
};
watch(isDark, (newValue) => {
  ls.set('darkMode', newValue);
  document.body.classList.toggle('body--dark', newValue);
});

const addActivityLog = (message, isError = false) => {
  activityLogs.value.unshift({
    message,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    isError,
  });
  if (activityLogs.value.length > 100) {
    activityLogs.value.splice(100);
  }
};

const detectPlate = async () => {
  if (!plateCameraRef.value) {
    addActivityLog('Plate camera not ready.', true);
    $q.notify({ type: 'negative', message: 'Plate camera not available.' });
    return;
  }
  isCapturing.value = true;
  error.value = null;
  addActivityLog('Initiating plate detection...');
  try {
    const imageFile = await plateCameraRef.value.getImage();
    if (!imageFile) throw new Error('Failed to capture image from plate camera.');

    const toBase64 = file => new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result.split(',')[1]);
      reader.onerror = err => reject(err);
    });
    const imageBase64 = await toBase64(imageFile);
    if (!imageBase64) throw new Error('Failed to convert image to base64.');

    const alprResponse = await invoke('process_alpr_image', {
      base64Image: imageBase64,
      cameraId: plateCameraType.value === 'usb' ? ls.get('plateCameraDevice') : plateCameraUrl.value || '',
    });

    if (alprResponse.success && alprResponse.detected_plates && alprResponse.detected_plates.length > 0) {
      const bestMatch = alprResponse.detected_plates[0];
      plateResult.value = { ...bestMatch }; // Triggers watcher
      addActivityLog(`Plate detected: ${bestMatch.plate_number}, Conf: ${bestMatch.confidence?.toFixed(2)}`);
    } else {
      plateResult.value = null;
      addActivityLog('No plate detected or ALPR processing failed.', alprResponse.error ? true : false);
      $q.notify({ type: 'warning', message: alprResponse.error || 'No plate detected.' });
    }
  } catch (err) {
    console.error('Error in detectPlate (ExitGate):', err);
    error.value = `Plate detection error: ${err.message}`;
    addActivityLog(error.value, true);
    $q.notify({ type: 'negative', message: error.value });
  } finally {
    isCapturing.value = false;
  }
};

const captureAndShowCctvImage = async (cameraType) => {
  let cameraConfig;
  let cameraName;

  if (cameraType === 'plate') {
    cameraConfig = plateCameraCredentials.value;
    cameraName = gateSettings.value?.PLATE_CAM_NAME || 'Kamera Plat Nomor'; // Use a default name if not set
  } else if (cameraType === 'driver') {
    cameraConfig = driverCameraCredentials.value;
    cameraName = gateSettings.value?.DRIVER_CAM_NAME || 'Kamera Pengemudi'; // Use a default name if not set
  } else {
    $q.notify({
      type: 'negative',
      message: 'Jenis kamera tidak valid.',
    });
    return;
  }

  if (!cameraConfig || !cameraConfig.ip_address) {
    $q.notify({
      type: 'warning',
      message: `Konfigurasi untuk ${cameraName} tidak ditemukan atau tidak lengkap.`,
    });
    return;
  }

  cctvImageLoading.value = true;
  showCctvImageDialog.value = true;
  cctvImageUrl.value = ''; // Clear previous image
  currentCctvConfig.value = { ...cameraConfig, name: cameraName, rtsp_path: gateSettings.value?.[`${cameraType.toUpperCase()}_CAM_RTSP_PATH`] || '' }; // Store camera config for dialog title

  try {
    const config = {
      username: cameraConfig.username,
      password: cameraConfig.password,
      ipAddress: cameraConfig.ip_address,
      rtspStreamPath: gateSettings.value?.[`${cameraType.toUpperCase()}_CAM_RTSP_PATH`] || '', // Ensure RTSP path is included
    };
    console.log('🚀 ~ captureAndShowCctvImage ~ config:', config);

    const response = await invoke('capture_cctv_image', { args: config });
    console.log('🚀 ~ captureAndShowCctvImage ~ response:', response);

    if (response.is_success && response.base64) {
      cctvImageUrl.value = response.base64;
      $q.notify({
        type: 'positive',
        message: `Gambar dari ${cameraName} berhasil diambil.`,
      });
    } else {
      $q.notify({
        type: 'negative',
        message: `Gagal mengambil gambar: ${response.message || 'Error tidak diketahui'}`,
      });
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: `Error saat mengambil gambar CCTV: ${error}`,
    });
  } finally {
    cctvImageLoading.value = false;
  }
};

const onPlateCaptured = async () => {
  addActivityLog('Manual capture initiated...');
  isProcessing.value = true; // Use general processing flag

  // Capture driver image first
  try {
    const driverCameraAvailable = driverCameraType.value === 'usb' ? ls.get('driverCameraDevice') : driverCameraUrl.value;
    if (driverCameraAvailable && driverCameraRef.value) {
      const driverImageFile = await driverCameraRef.value.getImage();
      if (driverImageFile) {
        const reader = new FileReader();
        reader.readAsDataURL(driverImageFile);
        reader.onloadend = () => { capturedDriver.value = reader.result; };
        addActivityLog('Driver image captured.');
      }
    } else {
      addActivityLog('Driver camera not available or not configured.');
    }
  } catch (err) {
    console.error('Failed to capture driver image (ExitGate):', err);
    addActivityLog('Failed to capture driver image.', true);
  }

  await detectPlate(); // This updates plateResult
  await handleExitPlateLogic(); // Call the new handler for exit plate logic

  if (plateResult.value && plateResult.value.plate_number) {
    addActivityLog(`Plate for exit: ${plateResult.value.plate_number}, conf: ${plateResult.value.confidence?.toFixed(2)}`);
    if (transactionData.value) {
      if (transactionData.value.entry_plate_number === plateResult.value.plate_number) {
        addActivityLog(`Plate matches active ticket: ${transactionData.value.id}.`);
        // Potentially trigger payment check or gate open if conditions met
      } else {
        addActivityLog(`Plate ${plateResult.value.plate_number} MISMATCH with ticket plate ${transactionData.value.entry_plate_number}.`, true);
        $q.notify({
          type: 'warning',
          message: 'Detected plate does not match ticket information.',
          position: 'top-right',
        });
      }
    } else {
        addActivityLog('No active transaction. Scan QR code to load transaction details.');
    }
    // Consider calling sendDataToBackend() here or after payment confirmation
  } else {
    addActivityLog('No plate detected during manual capture sequence.', true);
  }
  isProcessing.value = false;
};

const manualOpen = async () => {
  isProcessing.value = true;
  addActivityLog('Attempting to manually open exit gate...');
  try {
    if (exitGatePort.value && gateStore.isPortOpen('exit')) {
      await gateStore.writeToPort('exit', '*OUT1ON#'); // Example command, adjust as per hardware
      gateStatus.value = 'OPEN';
      addActivityLog('Manual open command sent via gateStore. Gate is OPEN.');
      // Auto-close logic
      setTimeout(() => {
        if (gateStatus.value === 'OPEN') {
          gateStore.writeToPort('exit', '*OUT1OFF#'); // Command to close
          gateStatus.value = 'CLOSED';
          addActivityLog('Gate closed automatically after timeout.');
        }
      }, 30000); // 30 seconds
    } else {
      // Fallback or error if serial port not configured/open
      // For now, using componentStore as a placeholder if direct hardware control fails
      await componentStore.openGate(); // This needs to be a real implementation or removed
      gateStatus.value = 'OPEN';
      addActivityLog('Manual open command sent via componentStore (fallback). Gate is OPEN.');
       setTimeout(() => {
        if (gateStatus.value === 'OPEN') {
          gateStatus.value = 'CLOSED';
          addActivityLog('Gate closed automatically after timeout (fallback).');
        }
      }, 30000);
      if (!exitGatePort.value) addActivityLog('Exit gate serial port not configured.', true);
      else if (!gateStore.isPortOpen('exit')) addActivityLog('Exit gate serial port not open.', true);
    }
  } catch (err) {
    console.error('Manual open error (ExitGate):', err);
    addActivityLog(`Failed to open gate manually: ${err.message}`, true);
    $q.notify({ type: 'negative', message: 'Failed to open gate manually.' });
  } finally {
    isProcessing.value = false;
  }
};

const openSettings = () => {
  const dialog = $q.dialog({
    component: SettingsDialog,
    componentProps: { persistent: true },
  });
  dialog.onOk(() => {
    plateCameraUrl.value = ls.get('plateCameraUrl') || '';
    driverCameraUrl.value = ls.get('driverCameraUrl') || '';
    plateCameraType.value = ls.get('plateCameraType') || (ls.get('plateCameraDevice') ? 'usb' : 'cctv');
    driverCameraType.value = ls.get('driverCameraType') || (ls.get('driverCameraDevice') ? 'usb' : 'cctv');
    exitGatePort.value = ls.get('serialPortExit') || '';
    addActivityLog('Settings updated. Re-initializing components if necessary.');
    // Potentially re-initialize cameras or serial connections if critical settings changed
    // Example: if (exitGatePort.value && !gateStore.isPortOpen('exit')) initializeExitSerialPort();
  });
};

const onQRCodeScanned = async (ticketId) => {
  showQRScanner.value = false;
  if (ticketId) {
    addActivityLog(`QR Code Scanned: ${ticketId}`);
    await fetchTransactionByTicketId(ticketId);
  } else {
    addActivityLog('QR Code scan cancelled or failed.', true);
  }
};

// This function will be called after ALPR (detectPlate) has updated plateResult.value
const handleExitPlateLogic = async () => {
  if (plateResult.value && plateResult.value.plate_number) {
    addActivityLog(`Exit Plate Detected: ${plateResult.value.plate_number}, Conf: ${plateResult.value.confidence?.toFixed(2)}`);
    // If no transaction is loaded yet (e.g. via QR scan), try to fetch by plate
    if (!transactionData.value) {
      await fetchTransactionByPlateNumber(plateResult.value.plate_number);
    }
    // If a transaction is loaded (either by QR or now by plate), compare plates
    if (transactionData.value) {
      // Ensure field name 'plate_number' matches what was saved in ManlessEntryGate
      if (transactionData.value.plate_number !== plateResult.value.plate_number) { 
        $q.notify({
          type: 'negative',
          message: `Plate Mismatch! Entry: ${transactionData.value.plate_number}, Exit: ${plateResult.value.plate_number}`,
          timeout: 7000,
          position: 'top',
        });
        addActivityLog(`PLATE MISMATCH. Entry: ${transactionData.value.plate_number}, Exit: ${plateResult.value.plate_number}`, true);
      } else {
        addActivityLog('Plate match confirmed with current transaction.');
        $q.notify({ type: 'positive', message: 'Plate match confirmed.' });
      }
    }
  } else {
    addActivityLog('No plate detected at exit or ALPR failed.', true);
  }
};

const processExitTransaction = async () => {
  if (!transactionData.value) {
    $q.notify({ type: 'warning', message: 'No transaction data loaded to process exit.' });
    addActivityLog('Process exit attempted without transaction data.', true);
    return;
  }

  isProcessing.value = true;
  addActivityLog(`Processing exit for transaction ID: ${transactionData.value._id}`);

  const exitTime = new Date().toISOString();
  let fee = 0;
  // Basic fee calculation (example: flat rate or simple duration based)
  // This should be replaced with actual tariff logic from PouchDB
  const entryTime = new Date(transactionData.value.entry_time);
  const durationMs = new Date(exitTime).getTime() - entryTime.getTime();
  const durationHours = durationMs / (1000 * 60 * 60);
  
  // Example: Rp 5000 for the first hour, Rp 3000 for subsequent hours
  if (durationHours <= 1) {
    fee = 5000;
  } else {
    fee = 5000 + Math.ceil(durationHours - 1) * 3000;
  }
  addActivityLog(`Calculated fee: Rp ${fee} for ${durationHours.toFixed(2)} hours.`);

  const updatedTransaction = {
    ...transactionData.value,
    exit_time: exitTime,
    exit_plate_number: plateResult.value?.plate_number || transactionData.value.plate_number, // Use detected exit plate if available
    fee: fee,
    status: 'exited',
    // Add other relevant exit details here, e.g., exit gate ID, operator ID if applicable
  };

  try {
    const response = await localDbs.transactions.put(updatedTransaction);
    addActivityLog(`Transaction ${updatedTransaction._id} updated successfully. Rev: ${response.rev}`);
    $q.notify({ type: 'positive', message: `Exit processed. Fee: Rp ${fee}. Gate will open.` });
    
    // Simulate gate opening by calling the existing manualOpen function
    await manualOpen(); 
    transactionData.value = null; // Clear transaction data after successful exit
    plateResult.value = null; // Clear plate result
    // Potentially reset other UI elements

  } catch (err) {
    console.error('Error updating transaction for exit:', err);
    addActivityLog(`Error updating transaction ${updatedTransaction._id} for exit: ${err.message}`, true);
    $q.notify({ type: 'negative', message: 'Failed to process exit. Please try again.' });
  } finally {
    isProcessing.value = false;
  }
};


const sendDataToBackend = async () => {
  if (!transactionData.value || !plateResult.value || !plateResult.value.plate_number) {
    addActivityLog('Missing transaction or plate data for backend sync. Cannot send.', true);
    $q.notify({type: 'warning', message: 'Cannot send data: Missing transaction or plate info.'});
    return;
  }
  isProcessing.value = true;
  addActivityLog('Sending exit transaction data to backend...');
  try {
    const formData = new FormData();

    // Append plate image (ALPR processed if available)
    if (plateResult.value && (plateResult.value.plate_image || plateResult.value.image_base64)) {
      const imageBase64 = plateResult.value.plate_image || plateResult.value.image_base64;
      const fetchRes = await fetch(`data:image/jpeg;base64,${imageBase64}`);
      const blob = await fetchRes.blob();
      formData.append('plate_image', blob, 'exit_plate.jpg');
    } else if (plateCameraRef.value) { // Fallback to raw camera image if ALPR image not available
      const plateImageFile = await plateCameraRef.value.getImage();
      if (plateImageFile) formData.append('plate_image', plateImageFile, 'exit_plate_raw.jpg');
    }

    // Append driver image if available
    if (capturedDriver.value) {
        const base64Data = capturedDriver.value.split(',')[1];
        const fetchRes = await fetch(`data:image/jpeg;base64,${base64Data}`);
        const blob = await fetchRes.blob();
        formData.append('driver_image', blob, 'exit_driver.jpg');
    }

    formData.append('transaction_id', transactionData.value.id);
    formData.append('exit_plate_number', plateResult.value.plate_number);
    formData.append('exit_plate_confidence', plateResult.value.confidence?.toFixed(2) || '0');
    formData.append('exit_time', new Date().toISOString());
    formData.append('gate_id', ls.get('gateId') || 'EXIT_GATE_01'); // Get gate ID from settings
    formData.append('operator', 'SYSTEM'); // Or actual operator if logged in
    // Add payment details if applicable and available in transactionData.value
    // formData.append('amount_paid', transactionData.value.parking_fee);
    // formData.append('payment_method', transactionData.value.payment_method || 'UNKNOWN');

    const response = await api.post('/transactions/process_exit', formData, { // Ensure this endpoint is correct
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    addActivityLog(`Exit for transaction ${transactionData.value.id} processed. Backend: ${response.data.message || 'OK'}`);
    // Clear transaction data and plate result after successful processing
    transactionData.value = null;
    plateResult.value = null;
    // Potentially close gate if it was opened for this transaction
    // if (gateStatus.value === 'OPEN') { /* logic to close gate */ }
  } catch (err) {
    console.error('Error sending exit data to backend:', err);
    addActivityLog(`Failed to send exit data to backend: ${err.message}`, true);
    $q.notify({ type: 'negative', message: 'Failed to process exit with backend.' });
  } finally {
    isProcessing.value = false;
  }
};

const onCameraError = (err) => {
  error.value = `Camera error: ${err.message || 'Unknown camera error'}`;
  errorDialog.value = true;
  addActivityLog(error.value, true);
};

const dismissError = () => {
  errorDialog.value = false;
  error.value = null;
};

const openSettingsFromError = () => {
  dismissError();
  openSettings();
};

const initializeExitSerialPort = async () => {
  if (exitGatePort.value) {
    try {
      await gateStore.initializeSerialPort({
        portName: exitGatePort.value,
        type: 'exit', // Important for gateStore to manage ports separately
      });
      addActivityLog(`Exit gate serial port ${exitGatePort.value} initialized.`);
    } catch (err) {
      addActivityLog(`Failed to initialize exit gate serial port ${exitGatePort.value}: ${err.message}`, true);
      $q.notify({ type: 'negative', message: `Serial Port ${exitGatePort.value} init failed.` });
    }
  }
};

onMounted(async () => {
  document.body.classList.toggle('body--dark', isDark.value);
  addActivityLog('Manless Exit Gate system initializing...');

  // Load settings
  plateCameraUrl.value = ls.get('plateCameraUrl') || '';
  driverCameraUrl.value = ls.get('driverCameraUrl') || '';
  plateCameraType.value = ls.get('plateCameraType') || (ls.get('plateCameraDevice') ? 'usb' : 'cctv');
  driverCameraType.value = ls.get('driverCameraType') || (ls.get('driverCameraDevice') ? 'usb' : 'cctv');
  exitGatePort.value = ls.get('serialPortExit') || '';

  await initializeExitSerialPort();

  addActivityLog('Manless Exit Gate system initialized.');
});

onUnmounted(async () => {
  if (plateCameraRef.value) {
    plateCameraRef.value.stopInterval();
  }
  if (exitGatePort.value && gateStore.isPortOpen('exit')) {
    try {
      await gateStore.closeSerialPort('exit');
      addActivityLog(`Exit gate serial port ${exitGatePort.value} closed.`);
    } catch (err) {
      addActivityLog(`Failed to close exit gate serial port ${exitGatePort.value}: ${err.message}`, true);
    }
  }
});

</script>

<style scoped>
.indicator-item {
  backdrop-filter: blur(4px);
}

.connection-indicator {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 10px;
  display: flex;
  align-items: center;
  gap: 4px;
  z-index: 10;
  background-color: rgba(0, 0, 0, 0.6);
  color: rgb(99, 252, 132);
  transition: all 0.3s ease;
}

/* Add pulse animation */
.connection-indicator::before {
  content: '';
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: rgb(99, 252, 132);
  animation: pulse 1.5s ease infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(99, 252, 132, 0.7);
  }

  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(99, 252, 132, 0);
  }

  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(99, 252, 132, 0);
  }
}

/* Add red color for disconnected state */
.connection-indicator.disconnected::before {
  background-color: rgb(255, 82, 82);
  animation: pulse-red 1.5s ease infinite;
}

@keyframes pulse-red {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(255, 82, 82, 0.7);
  }

  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(255, 82, 82, 0);
  }

  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(255, 82, 82, 0);
  }
}

.connection-indicator.connected {
  background-color: rgba(0, 128, 0, 0.6);
}

.connection-indicator.disconnected {
  background-color: rgba(255, 0, 0, 0.6);
}

.manless-entry {
  height: 100vh;
  min-height: 100vh;
  background-color: #f5f5f5;
  transition: background-color 0.3s ease;
  padding: 0.3rem;
}

.manless-entry.dark-mode {
  background-color: #121212;
}

.dark-mode .camera-card,
.dark-mode .control-card,
.dark-mode .log-card {
  background-color: rgba(30, 30, 30, 0.95) !important;
  color: #fff;
}

.camera-card,
.control-card,
.log-card,
.header-card {
  border-radius: 5px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s ease, color 0.3s ease;
}

.dark-mode .camera-feed {
  background-color: #1e1e1e;
  border: 1px solid #333;
}

.camera-feed {
  border-radius: 4px;
  overflow: hidden;
  background-color: #ffffff;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.plate-result {
  background-color: rgba(0, 0, 0, 0.02);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.dark-mode .plate-result {
  background-color: rgba(255, 255, 255, 0.05);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.plate-image {
  max-width: 200px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.dark-mode .plate-image {
  border-color: #333;
}

.header-card {
  background: linear-gradient(135deg, var(--q-primary) 0%, var(--q-dark) 100%);
}

.dark-mode .header-card {
  background: linear-gradient(135deg, #1e1e1e 0%, #000 100%);
}

.q-card {
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.95);
  transition: background-color 0.3s ease, color 0.3s ease;
}

.dark-mode .q-card {
  background-color: rgba(30, 30, 30, 0.95);
  color: #fff;
}

.plate-camera-container {
  position: relative;
}

.plate-detection-overlay {
  position: absolute;
  bottom: 16px;
  right: 16px;
  width: min(200px, 90%);
  height: auto;
  pointer-events: none;
  z-index: 100;
}

.plate-detection-image {
  width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transform-origin: bottom right;
}

/* Add animate.css classes for zoom animation */
.animate__animated {
  animation-duration: 0.5s;
}

.animate__zoomIn {
  animation-name: zoomIn;
}

.animate__zoomOut {
  animation-name: zoomOut;
}

@keyframes zoomIn {
  from {
    opacity: 0;
    transform: scale3d(0.3, 0.3, 0.3);
  }

  to {
    opacity: 1;
    transform: scale3d(1, 1, 1);
  }
}

@keyframes zoomOut {
  from {
    opacity: 1;
  }

  to {
    opacity: 0;
    transform: scale3d(0.3, 0.3, 0.3);
  }
}

/* Add responsive styles */
@media (max-width: 600px) {
  .text-h5 {
    font-size: 1.2rem !important;
  }

  .text-h6 {
    font-size: 1rem !important;
  }

  .q-btn {
    padding: 4px 8px;
  }

  .q-card-section {
    padding: 12px !important;
  }

  .plate-detection-overlay {
    position: relative;
    bottom: auto;
    right: auto;
    width: 100%;
    margin-top: 1rem;
  }

  .camera-feed {
    min-height: 200px;
  }

  .q-scroll-area {
    height: 200px !important;
  }
}

@media (min-width: 601px) and (max-width: 1024px) {
  .camera-feed {
    min-height: 300px;
  }

  .plate-detection-overlay {
    width: 250px;
  }
}
</style>

<q-dialog v-model="showCctvImageDialog">
  <q-card style="width: 700px; max-width: 80vw;">
    <q-card-section class="row items-center q-pb-none">
      <div class="text-h6">Gambar CCTV - {{ currentCctvConfig?.name }}</div>
      <q-space />
      <q-btn icon="close" flat round dense v-close-popup />
    </q-card-section>

    <q-card-section class="q-pt-none">
      <q-img
        v-if="cctvImageUrl"
        :src="cctvImageUrl"
        spinner-color="primary"
        style="height: 400px; max-width: 100%"
        fit="contain"
      />
      <div v-else class="text-center q-pa-md">
        <q-spinner-dots color="primary" size="40px" />
        <p>Memuat gambar...</p>
      </div>
    </q-card-section>

    <q-card-actions align="right">
      <q-btn flat label="Tutup" color="primary" v-close-popup />
    </q-card-actions>
  </q-card>
</q-dialog>
