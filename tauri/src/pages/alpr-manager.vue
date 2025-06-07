<script setup>
import { onMounted, onUnmounted, ref, computed, watch } from 'vue';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { Notify, useQuasar } from 'quasar';
import { useSettingsService } from 'stores/settings-service';
import { useAlprStore } from 'stores/alpr-store';

const $q = useQuasar();
const alprStore = useAlprStore();
const settingsService = useSettingsService();

// Reactive state
// const connectionStatus = ref('disconnected'); // Global status removed, will be per camera
const connecting = ref(false);
const checkingHealth = ref(false);
const serviceHealth = ref(null);
const addingCamera = ref(false);
const showCctvImageDialog = ref(false);
const cctvImageUrl = ref('');
const cctvImageLoading = ref(false);
const currentCctvConfig = ref(null);

const cameras = ref([]); // Ini akan menyimpan kamera dari ALPR service
const cctvCamerasByGate = ref({}); // Ini akan menyimpan kamera CCTV dari settings-service
const recentDetections = ref([]);

// Get gate settings from service
const gateSettings = computed(() => settingsService.gateSettings);

// ALPR Mode settings - now from gate settings
const useExternalAlpr = ref(gateSettings.value?.USE_EXTERNAL_ALPR || false);
const wsStatus = ref('disconnected');

// Event listeners
let unlistenStatus = null;
let unlistenDetection = null;
let unlistenCameras = null;

// Methods
const toggleConnection = async () => {
  connecting.value = true;
  try {
    if (connectionStatus.value === 'connected') {
      await invoke('disconnect_from_alpr_service');
      Notify.create({
        type: 'info',
        message: 'Disconnected from ALPR service',
      });
    } else {
      await invoke('connect_to_alpr_service', {
        url: 'ws://localhost:8001/ws',
      });
      Notify.create({
        type: 'positive',
        message: 'Connected to ALPR service',
      });
    }
  } catch (error) {
    Notify.create({
      type: 'negative',
      message: `Connection error: ${error}`,
    });
  } finally {
    connecting.value = false;
  }
};

const checkHealth = async () => {
  checkingHealth.value = true;
  try {
    if (useExternalAlpr.value) {
      // Check external ALPR WebSocket health
      if (!alprStore.isWsConnected) {
        throw new Error('WebSocket not connected');
      }

      // Send health check message through WebSocket
      const message = {
        message_type: 'health_check',
        payload: {}
      };

      const response = await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Health check timeout'));
        }, 5000); // 5 second timeout

        const messageHandler = (event) => {
          try {
            const response = JSON.parse(event.data);
            if (response.message_type === 'health_response') {
              clearTimeout(timeout);
              alprStore.wsConnection.removeEventListener('message', messageHandler);
              resolve(response.payload.healthy);
            }
          } catch (error) {
            // Keep listening for the correct response
          }
        };

        alprStore.wsConnection.addEventListener('message', messageHandler);
        alprStore.wsConnection.send(JSON.stringify(message));
      });

      serviceHealth.value = response;
    } else {
      // Check internal ALPR health
      const health = await invoke('check_alpr_service_health');
      serviceHealth.value = health;
    }

    Notify.create({
      type: serviceHealth.value ? 'positive' : 'negative',
      message: `${useExternalAlpr.value ? 'External' : 'Internal'} ALPR service is ${serviceHealth.value ? 'healthy' : 'unhealthy'}`,
    });
  } catch (error) {
    serviceHealth.value = false;
    Notify.create({
      type: 'negative',
      message: `Health check failed: ${error}`,
    });
  } finally {
    checkingHealth.value = false;
  }
};

const startCamera = async (cameraId) => {
  const camera = cameras.value.find((c) => c.id === cameraId);
  if (camera) camera.loading = true;

  try {
    await invoke('start_camera', { cameraId });
    await loadCameras();

    Notify.create({
      type: 'positive',
      message: 'Camera started successfully',
    });
  } catch (error) {
    Notify.create({
      type: 'negative',
      message: `Failed to start camera: ${error}`,
    });
  } finally {
    if (camera) camera.loading = false;
  }
};

const stopCamera = async (cameraId) => {
  const camera = cameras.value.find((c) => c.id === cameraId);
  if (camera) camera.loading = true;

  try {
    await invoke('stop_camera', { cameraId });
    await loadCameras();

    Notify.create({
      type: 'info',
      message: 'Camera stopped successfully',
    });
  } catch (error) {
    Notify.create({
      type: 'negative',
      message: `Failed to stop camera: ${error}`,
    });
  } finally {
    if (camera) camera.loading = false;
  }
};

const removeCamera = async (cameraId) => {
  const camera = cameras.value.find((c) => c.id === cameraId);
  if (camera) camera.loading = true;

  try {
    await invoke('remove_camera', { cameraId });
    await loadCameras();

    Notify.create({
      type: 'info',
      message: 'Camera removed successfully',
    });
  } catch (error) {
    Notify.create({
      type: 'negative',
      message: `Failed to remove camera: ${error}`,
    });
  } finally {
    if (camera) camera.loading = false;
  }
};

// const loadAlprServiceCameras = async () => {
//   try {
//     // Ini untuk kamera yang dikelola oleh service ALPR Python (jika masih ada)
//     const cameraList = await invoke('get_cameras');
//     cameras.value = cameraList.map((camera) => ({
//       ...camera,
//       loading: false,
//     }));
//   } catch (error) {
//     console.error('Failed to load ALPR service cameras:', error);
//   }
// };

const loadCctvCamerasFromSettings = async () => {
  try {
    const allGateSettings = await settingsService.getAllGateSettings();
    console.log(
      '🚀 ~ loadCctvCamerasFromSettings ~ allGateSettings:',
      allGateSettings
    );
    const cctvByGate = {};
    allGateSettings.forEach((gate) => {
      if (gate.gateName) {
        const gateCams = [];
        if (gate.PLATE_CAM_IP && gate.PLATE_CAM_IP) {
          gateCams.push({
            id: `${gate.gateId}_plate`,
            name: `${gate.gateName} - Plat Nomor`,
            rtsp_IP: gate.PLATE_CAM_IP,
            username: gate.PLATE_CAM_USERNAME,
            password: gate.PLATE_CAM_PASSWORD,
            ip_address: gate.PLATE_CAM_IP,
            rtsp_path: gate.PLATE_CAM_RTSP_PATH,
            type: 'cctv',
            gateId: gate.gateId,
            status: 'unknown',
          });
        }
        if (gate.DRIVER_CAM_IP && gate.DRIVER_CAM_IP) {
          gateCams.push({
            id: `${gate.gateId}_driver`,
            name: `${gate.gateName} - Pengemudi`,
            rtsp_IP: gate.DRIVER_CAM_IP,
            username: gate.DRIVER_CAM_USERNAME,
            password: gate.DRIVER_CAM_PASSWORD,
            ip_address: gate.DRIVER_CAM_IP,
            rtsp_path: gate.DRIVER_CAM_RTSP_PATH,
            type: 'cctv',
            gateId: gate.gateId,
            status: 'unknown',
          });
        }
        // Tambahkan SCANNER_CAM_IP jika perlu
        // if (gate.SCANNER_CAM_IP) { ... }
        if (gateCams.length > 0) {
          cctvByGate[gate.gateName] = gateCams;
        }
      }
    });
    console.log('🚀 ~ loadCctvCamerasFromSettings ~ cctvByGate:', cctvByGate);
    cctvCamerasByGate.value = cctvByGate;
  } catch (error) {
    console.error('Failed to load CCTV cameras from settings:', error);
    Notify.create({
      type: 'negative',
      message: 'Gagal memuat konfigurasi kamera CCTV dari pengaturan.',
    });
  }
};

const formatTimestamp = (timestamp) => {
  return new Date(timestamp).toLocaleString('id-ID');
};

// Lifecycle
onMounted(async () => {
  // Initialize settings service
  await settingsService.initializeSettings();
  
  // Update useExternalAlpr from gate settings
  useExternalAlpr.value = gateSettings.value?.USE_EXTERNAL_ALPR || false;
  
  // Initialize ALPR store from settings
  await alprStore.initializeFromSettings();
  
  // Initialize ALPR store and connect if using external ALPR
  if (useExternalAlpr.value) {
    await connectToExternalAlpr();
  }

  // Watch for WebSocket connection status
  watch(() => alprStore.isWsConnected, (newStatus) => {
    wsStatus.value = newStatus ? 'connected' : 'disconnected';
  });

  // Load initial data
  // await loadAlprServiceCameras(); // Jika masih menggunakan service ALPR terpisah untuk beberapa kamera
  await loadCctvCamerasFromSettings();

  // Initialize camera connection status for ALPR service cameras
  cameras.value.forEach((camera) => {
    // Placeholder: Implement actual logic to get individual camera connection status
    // For now, defaulting to a status from the camera object if available, or 'disconnected'
    camera.connectionStatus =
      camera.status === 'active' ? 'connected' : 'disconnected';
  });

  // Global connection status check removed or adapted
  // try {
  //   const status = await invoke('get_connection_status');
  //   // connectionStatus.value = status.connected ? 'connected' : 'disconnected'; // Global status removed
  // } catch (error) {
  //   console.error('Failed to get connection status:', error);
  // }

  // Listen to events
  unlistenStatus = await listen('alpr-connection-status', (event) => {
    connectionStatus.value = event.payload.status;
  });

  unlistenDetection = await listen('alpr-plate-detection', (event) => {
    const detection = event.payload;
    recentDetections.value.unshift(detection);

    // Keep only last 50 detections
    if (recentDetections.value.length > 50) {
      recentDetections.value = recentDetections.value.slice(0, 50);
    }

    // Show notification for high confidence detections
    if (detection.confidence > 0.7) {
      Notify.create({
        type: 'positive',
        message: `Plat terdeteksi: ${detection.plate_text}`,
        caption: `Kamera: ${detection.camera_name}`,
        timeout: 3000,
      });
    }
  });

  unlistenCameras = await listen('alpr-camera-list', (event) => {
    // Ini mungkin perlu disesuaikan jika event ini hanya untuk kamera dari service ALPR Python
    cameras.value = event.payload.map((camera) => ({
      ...camera,
      loading: false,
    }));
  });
  
  // Watch for changes in gate settings to update ALPR mode
  watch(() => gateSettings.value?.USE_EXTERNAL_ALPR, (newValue) => {
    if (newValue !== undefined && newValue !== useExternalAlpr.value) {
      toggleAlprMode(newValue);
    }
  });
});

onUnmounted(() => {
  // Disconnect from external ALPR if connected
  if (useExternalAlpr.value) {
    disconnectFromExternalAlpr();
  }

  // Clean up event listeners
  if (unlistenStatus) unlistenStatus();
  if (unlistenDetection) unlistenDetection();
  if (unlistenCameras) unlistenCameras();
});

const uploadedImage = ref(null);
const alprResult = ref(null);
const uploading = ref(false);

const handleImageUpload = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    uploadedImage.value = e.target.result;
  };
  reader.readAsDataURL(file);
};

const connectToExternalAlpr = async () => {
  try {
    // Get WebSocket URL from gate settings
    const wsUrl = gateSettings.value?.WS_URL || 'ws://localhost:8765';
    
    // Update the WebSocket URL in alprStore
    alprStore.updateWebSocketUrl(wsUrl);
    
    await alprStore.connectWebSocket();
    
    // Wait for the connection to be established
    const timeout = 5000; // 5 seconds timeout
    const startTime = Date.now();
    
    while (!alprStore.isWsConnected && Date.now() - startTime < timeout) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    if (!alprStore.isWsConnected) {
      throw new Error('Connection timeout');
    }

    return true;
  } catch (error) {
    console.error('Connection error:', error);
    throw new Error(`Failed to connect to external ALPR: ${error.message}`);
  }
};

const disconnectFromExternalAlpr = () => {
  alprStore.disconnect();
  Notify.create({
    type: 'info',
    message: 'Disconnected from external ALPR service',
  });
};

const toggleAlprMode = async (newValue) => {
  try {
    useExternalAlpr.value = newValue;
    
    if (useExternalAlpr.value) {
      await connectToExternalAlpr();
      if (!alprStore.isWsConnected) {
        throw new Error('Failed to connect to external ALPR');
      }
    } else {
      disconnectFromExternalAlpr();
    }

    // Update ALPR mode in store and save to settings
    alprStore.updateAlprMode(useExternalAlpr.value);
    await settingsService.saveGateSettings({
      USE_EXTERNAL_ALPR: useExternalAlpr.value
    });
    
    Notify.create({
      type: 'positive',
      message: `Switched to ${useExternalAlpr.value ? 'external' : 'internal'} ALPR`,
    });
  } catch (error) {
    console.error('Error toggling ALPR mode:', error);
    useExternalAlpr.value = !newValue; // Revert the toggle
    Notify.create({
      type: 'negative',
      message: `Failed to switch ALPR mode: ${error.message}`,
    });
  }
};

const processAlpr = async () => {
  if (!uploadedImage.value) return;
  uploading.value = true;
  try {
    const base64Image = uploadedImage.value.split(',')[1];
    
    // Menggunakan alprStore.processImage untuk kedua mode
    const result = await alprStore.processImage(base64Image, 'simulator');
    console.log("🚀 ~ processAlpr ~ result:", result);

    // Gunakan hasil langsung dari alprStore
    if (result && result.detectedPlate && result.detectedPlate.length > 0) {
      alprResult.value = {
        plateImage: result.processedImage,
        plateNumber: result.detectedPlate[0].plate_number,
        confidence: result.detectedPlate[0].confidence,
        processingTime: result.processingTime
      };
    } else {
      alprResult.value = null;
      Notify.create({
        type: 'warning',
        message: 'No license plate detected',
      });
    }
  } catch (error) {
    console.error('Error processing ALPR:', error);
    alprResult.value = null;
    Notify.create({
      type: 'negative',
      message: `Error processing ALPR: ${error}`,
    });
  } finally {
    uploading.value = false;
  }
};

// Watch WebSocket connection status
watch(() => alprStore.isWsConnected, (newStatus) => {
  if (useExternalAlpr.value && !newStatus) {
    // Connection lost while in external mode
    Notify.create({
      type: 'warning',
      message: 'External ALPR connection lost. Attempting to reconnect...',
    });
  }
}, { immediate: true });

// Watch for changes in gate settings
watch(() => gateSettings.value, (newSettings) => {
  if (newSettings) {
    // Update ALPR mode from settings
    if (newSettings.USE_EXTERNAL_ALPR !== undefined && 
        newSettings.USE_EXTERNAL_ALPR !== useExternalAlpr.value) {
      useExternalAlpr.value = newSettings.USE_EXTERNAL_ALPR;
    }
  }
}, { deep: true });
</script>

<template>
  <q-page class="q-pa-md" padding>
    <div class="row q-gutter-md">
      <!-- Header -->
      <div class="col-12">
        <q-card class="q-pa-md">
          <div class="row items-center justify-between">
            <div>
              <div class="text-h5 text-weight-bold">ALPR Manager</div>
              <div
                :class="$q.dark.isActive ? 'text-grey-5' : 'text-grey-7'"
                class="text-subtitle2"
              >
                Kelola CCTV dan Automatic License Plate Recognition
              </div>
            </div>
            <div class="row q-gutter-sm">
              <!-- ALPR Mode Toggle -->                  <q-btn-toggle
                    v-model="useExternalAlpr"
                    :options="[
                      { label: 'Internal ALPR', value: false },
                      { label: 'External ALPR', value: true }
                    ]"
                    color="primary"
                    text-color="white"
                    toggle-color="secondary"
                    @update:model-value="toggleAlprMode"
                    :loading="connecting"
                    :disable="connecting"
                  />
              <q-btn
                color="secondary"
                icon="health_and_safety"
                label="Check ALPR Service Health"
                :loading="checkingHealth"
                @click="checkHealth"
              />
            </div>
          </div>

          <!-- Status Indicators -->
          <div class="row q-gutter-sm q-mt-md">
            <q-chip
              :color="useExternalAlpr ? 'purple' : 'primary'"
              text-color="white"
              icon="settings"
            >
              {{ useExternalAlpr ? 'External ALPR' : 'Internal ALPR' }}
            </q-chip>
            <q-chip
              v-if="useExternalAlpr"
              :color="alprStore.isWsConnected ? 'positive' : 'negative'"
              text-color="white"
              :icon="alprStore.isWsConnected ? 'wifi' : 'wifi_off'"
            >
              WebSocket {{ alprStore.isWsConnected ? 'Connected' : 'Disconnected' }}
            </q-chip>
            <q-chip
              v-if="serviceHealth !== null"
              :color="serviceHealth ? 'positive' : 'negative'"
              text-color="white"
              :icon="serviceHealth ? 'check_circle' : 'error'"
            >
              ALPR Service {{ serviceHealth ? 'Healthy' : 'Unhealthy' }}
            </q-chip>
          </div>
        </q-card>

        <div class="row q-gutter-md q-mt-md">
          <!-- Upload & ALPR Section -->
          <div class="col-12">
            <q-card class="q-pa-md q-mb-md">
              <div class="text-h6 q-mb-md">Tes ALPR</div>
              <div class="row items-center q-gutter-md">
                <input
                  type="file"
                  accept="image/*"
                  @change="handleImageUpload"
                />
                <q-btn
                  color="primary"
                  label="Proses ALPR"
                  :loading="uploading"
                  @click="processAlpr"
                  :disable="!uploadedImage"
                />
              </div>
              <div v-if="uploadedImage" class="q-mt-md">
                <img
                  :src="uploadedImage"
                  alt="Uploaded"
                  style="max-width: 300px; max-height: 200px"
                />
              </div>
              <div v-if="alprResult" class="q-mt-md">
                <q-banner
                  dense
                  :class="
                    $q.dark.isActive
                      ? 'bg-grey-9 text-white'
                      : 'bg-grey-2 text-black'
                  "
                >
                  <div v-if="alprResult?.plateNumber">
                    <div class="row items-center">
                        <div class="col-auto" v-if="alprResult.plateImage">
                        <img
                          :src="`data:image/jpeg;base64,${alprResult.plateImage}`"
                          alt="Plate Image"
                          style="max-width: 100px; max-height: 60px; margin-right: 10px;"
                        />
                        </div>
                        <div class="col">
                        <div class="row q-gutter-sm">
                          <q-chip
                          color="primary"
                          text-color="white"
                          icon="directions_car"
                          >
                          {{ alprResult?.plateNumber }}
                          </q-chip>
                          
                          <q-chip
                          :color="Number(alprResult?.confidence) > 0.7 ? 'positive' : 'warning'"
                          text-color="white"
                          icon="verified"
                          >
                          {{ (Number(alprResult?.confidence) * 100).toFixed(2) }}%
                          </q-chip>

                          <q-chip
                          color="secondary"
                          text-color="white"
                          icon="timer"
                          >
                          {{ (alprResult?.processingTime).toFixed(2) }} s
                          </q-chip>
                        </div>
                        </div>
                    </div>
                  </div>
                  <div v-else>Tidak ada plat terdeteksi.</div>
                </q-banner>
              </div>
            </q-card>
          </div>
        </div>
      </div>

      <!-- Camera Management -->
      <div class="col-12 col-md-6">
        <q-card class="q-pa-md full-height">
          <div class="text-h6 q-mb-md">Manajemen Kamera</div>

          <!-- CCTV Camera List from Settings -->
          <div v-if="Object.keys(cctvCamerasByGate).length > 0">
            <q-item-label header class="q-mt-md"
              >Kamera CCTV (dari Pengaturan Gerbang)</q-item-label
            >
            <div
              v-for="(gateCams, gateName) in cctvCamerasByGate"
              :key="gateName"
            >
              <q-list bordered separator class="q-mb-md">
                <q-item-label
                  header
                  :class="
                    $q.dark.isActive
                      ? 'bg-grey-8 text-white'
                      : 'bg-grey-2 text-black'
                  "
                  >{{ gateName }}</q-item-label
                >
                <q-item
                  v-for="camera in gateCams"
                  :key="camera.id"
                  class="q-pa-md"
                >
                  <q-item-section avatar>
                    <q-avatar
                      color="blue-grey"
                      text-color="white"
                      icon="linked_camera"
                    />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-weight-bold">
                      {{ camera.name }}
                    </q-item-label>
                    <q-item-label caption>
                      IP: {{ camera.rtsp_IP }}
                    </q-item-label>
                    <q-item-label caption>
                      Status:
                      <q-badge color="grey">{{ camera.status }}</q-badge>
                      <!-- Anda perlu mekanisme untuk update status CCTV ini jika diperlukan -->
                    </q-item-label>
                  </q-item-section>
                  <q-item-section side>
                    <q-btn
                      flat
                      dense
                      icon="visibility"
                      @click="captureAndShowCctvImage(camera)"
                    >
                      <q-tooltip>Test Kamera & Lihat Snapshot</q-tooltip>
                    </q-btn>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
          <q-item
            v-if="
              Object.keys(cctvCamerasByGate).length === 0 &&
              cameras.length === 0
            "
          >
            <q-item-section>
              <q-item-label
                :class="$q.dark.isActive ? 'text-grey-5' : 'text-grey-7'"
                class="text-center q-py-md"
              >
                Belum ada kamera ALPR atau CCTV yang dikonfigurasi.
              </q-item-label>
            </q-item-section>
          </q-item>

          <!-- ALPR Service Camera List (jika masih ada) -->
          <div v-if="cameras.length > 0">
            <q-item-label header class="q-mt-md"
              >Kamera dari ALPR Service</q-item-label
            >
            <q-list bordered separator>
              <q-item
                v-for="camera in cameras"
                :key="camera.id"
                class="q-pa-md"
              >
                <q-item-section avatar>
                  <q-avatar
                    :color="camera.status === 'active' ? 'positive' : 'grey'"
                    text-color="white"
                    :icon="
                      camera.status === 'active' ? 'videocam' : 'videocam_off'
                    "
                  />
                </q-item-section>

                <q-item-section>
                  <q-item-label class="text-weight-bold">
                    {{ camera.name }}
                  </q-item-label>
                  <q-item-label caption>
                    {{ camera.rtsp_IP }}
                  </q-item-label>
                  <q-item-label caption>
                    Status:
                    <span
                      :class="
                        camera.status === 'active'
                          ? 'text-positive'
                          : 'text-grey'
                      "
                    >
                      {{ camera.status === 'active' ? 'Aktif' : 'Tidak Aktif' }}
                    </span>
                    <q-badge
                      :color="
                        camera.connectionStatus === 'connected'
                          ? 'positive'
                          : 'negative'
                      "
                      class="q-ml-sm"
                    >
                      {{ camera.connectionStatus }}
                    </q-badge>
                  </q-item-label>
                </q-item-section>

                <q-item-section side>
                  <div class="row q-gutter-xs">
                    <q-btn
                      v-if="camera.status !== 'active'"
                      size="sm"
                      color="positive"
                      icon="play_arrow"
                      :loading="camera.loading"
                      @click="startCamera(camera.id)"
                    >
                      <q-tooltip>Start Camera</q-tooltip>
                    </q-btn>
                    <q-btn
                      v-else
                      size="sm"
                      color="warning"
                      icon="stop"
                      :loading="camera.loading"
                      @click="stopCamera(camera.id)"
                    >
                      <q-tooltip>Stop Camera</q-tooltip>
                    </q-btn>
                    <q-btn
                      size="sm"
                      color="negative"
                      icon="delete"
                      :loading="camera.loading"
                      @click="removeCamera(camera.id)"
                    >
                      <q-tooltip>Remove Camera</q-tooltip>
                    </q-btn>
                  </div>
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </q-card>
      </div>

      <!-- Plate Detection Results -->
      <!-- <div class="col-12 col-md-6">
        <q-card class="q-pa-md full-height">
          <div class="text-h6 q-mb-md">Deteksi Plat Nomor</div>

          <q-list
            bordered
            separator
            style="max-height: 500px; overflow-y: auto"
          >
            <q-item-label header> Deteksi Terbaru </q-item-label>
            <q-item
              v-for="detection in recentDetections"
              :key="detection.timestamp"
              class="q-pa-md"
            >
              <q-item-section avatar>
                <q-avatar square size="60px">
                  <img
                    v-if="detection.plate_image"
                    :src="`data:image/jpeg;base64,${detection.plate_image}`"
                  />
                  <q-icon v-else name="image" size="30px" :color="$q.dark.isActive ? 'grey-5' : 'grey-7'" />
                </q-avatar>
              </q-item-section>

              <q-item-section>
                <q-item-label class="text-weight-bold text-h6">
                  {{ detection.plate_text }}
                </q-item-label>
                <q-item-label caption>
                  Kamera: {{ detection.camera_name }}
                </q-item-label>
                <q-item-label caption>
                  Confidence: {{ (detection.confidence * 100).toFixed(1) }}%
                </q-item-label>
                <q-item-label caption>
                  {{ formatTimestamp(detection.timestamp) }}
                </q-item-label>
              </q-item-section>

              <q-item-section side>
                <q-chip
                  :color="
                    detection.confidence > 0.8
                      ? 'positive'
                      : detection.confidence > 0.6
                      ? 'warning'
                      : 'negative'
                  "
                  text-color="white"
                  size="sm"
                >
                  {{
                    detection.confidence > 0.8
                      ? 'Tinggi'
                      : detection.confidence > 0.6
                      ? 'Sedang'
                      : 'Rendah'
                  }}
                </q-chip>
              </q-item-section>
            </q-item>

            <q-item v-if="recentDetections.length === 0">
              <q-item-section>
                <q-item-label class="text-center text-grey-5">
                  Belum ada deteksi plat nomor
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div> -->
    </div>
    <!-- CCTV Image Dialog -->
    <q-dialog v-model="showCctvImageDialog">
      <q-card style="width: 700px; max-width: 80vw">
        <q-card-section>
          <div class="text-h6">Snapshot dari {{ currentCctvConfig?.name }}</div>
        </q-card-section>

        <q-card-section class="q-pt-none text-center">
          <q-spinner-dots color="primary" size="3em" v-if="cctvImageLoading" />
          <img
            v-if="!cctvImageLoading && cctvImageUrl"
            :src="cctvImageUrl"
            alt="CCTV Snapshot"
            style="max-width: 100%; max-height: 70vh; object-fit: contain"
          />
          <div v-if="!cctvImageLoading && !cctvImageUrl">
            Tidak ada gambar untuk ditampilkan atau gagal memuat.
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Tutup" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<style scoped>
.full-height {
  height: 100%;
}
</style>
