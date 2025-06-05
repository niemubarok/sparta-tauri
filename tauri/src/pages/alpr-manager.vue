<script setup>
import { onMounted, onUnmounted, ref, computed } from 'vue';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { Notify, useQuasar } from 'quasar'; // Ditambahkan useQuasar
import { useSettingsService } from 'stores/settings-service';

const $q = useQuasar(); // Ditambahkan untuk akses properti Quasar

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
const settingsService = useSettingsService();

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
    const health = await invoke('check_alpr_service_health');
    serviceHealth.value = health;
    Notify.create({
      type: health ? 'positive' : 'negative',
      message: `Service is ${health ? 'healthy' : 'unhealthy'}`,
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

  // Watch for changes in settings that might affect CCTV cameras
  // This might be complex if settings can change frequently without a full app reload.
  // For simplicity, we'll rely on the initial load and potential manual refresh.
});

const captureAndShowCctvImage = async (camera) => {
  cctvImageLoading.value = true;
  showCctvImageDialog.value = true;
  cctvImageUrl.value = ''; // Clear previous image
  currentCctvConfig.value = camera; // Store camera config for dialog title

  try {
    const config = {
      username: camera.username,
      password: camera.password,
      ipAddress: camera.ip_address, // Mengubah ip_address menjadi ipAddress
      rtspStreamPath: camera.rtsp_path, // Mengubah rtsp_stream_path menjadi rtspStreamPath
    };
    console.log('🚀 ~ captureAndShowCctvImage ~ config:', config);

    const response = await invoke('capture_cctv_image', { args: config });
    console.log('🚀 ~ captureAndShowCctvImage ~ response:', response);

    if (response.is_success && response.base64) {
      cctvImageUrl.value = response.base64;
      Notify.create({
        type: 'positive',
        message: `Gambar dari ${camera.name} berhasil diambil.`,
      });
    } else {
      Notify.create({
        type: 'negative',
        message: `Gagal mengambil gambar: ${
          response.message || 'Error tidak diketahui'
        }`,
      });
    }
  } catch (error) {
    Notify.create({
      type: 'negative',
      message: `Error saat mengambil gambar CCTV: ${error}`,
    });
  } finally {
    cctvImageLoading.value = false;
  }
};

onUnmounted(() => {
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

const processAlpr = async () => {
  if (!uploadedImage.value) return;
  uploading.value = true;
  try {
    // Extract base64 data from the data URL by removing the prefix
    const base64Image = uploadedImage.value.split(',')[1];

    const result = await invoke('process_alpr_image', {
      base64Image: base64Image,
      cameraId: 'simulator',
    });
    console.log('🚀 ~ processAlpr ~ result:', result);

    if (result.success) {
      alprResult.value = result.detected_plates[0];
      if (alprResult.value) {
        console.log('ALPR Result from backend:', alprResult.value);
        console.log('Confidence value:', alprResult.value.confidence);
        console.log('Plate image exists:', !!alprResult.value.plate_image);
        const detection = {
          label: 'License Plate',
          confidence: alprResult.value.confidence,
          bounding_box: {
            x1: alprResult.value.bbox.x,
            y1: alprResult.value.bbox.y,
            x2: alprResult.value.bbox.x + alprResult.value.bbox.width,
            y2: alprResult.value.bbox.y + alprResult.value.bbox.height,
          },
        };
        const ocr = {
          text: alprResult.value.plate_number,
          confidence: alprResult.value.confidence,
        };
        console.log('Final detection object:', detection);
        console.log('Final OCR object:', ocr);
        alprResult.value = {
          detection,
          ocr,
          plate_image: alprResult.value.plate_image,
        };
      }
    } else {
      console.error('ALPR processing failed:', result.message);
    }
  } catch (error) {
    console.error('Error processing ALPR:', error);
  } finally {
    uploading.value = false;
  }
};
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
              <!-- Global connection toggle removed -->
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
            <!-- Global connection status chip removed -->
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
                  <div v-if="alprResult?.ocr.text">
                    <div class="row items-center">
                      <div class="col-auto" v-if="alprResult.plate_image">
                        <img
                          :src="`data:image/jpeg;base64,${alprResult.plate_image}`"
                          alt="Plate Image"
                          style="
                            max-width: 100px;
                            max-height: 60px;
                            margin-right: 10px;
                          "
                        />
                      </div>
                      <div class="col">
                        <b>Plat:</b> {{ alprResult?.ocr?.text }}<br />
                        <b>Confidence:</b>
                        {{
                          (
                            Number(alprResult?.detection.confidence) * 100
                          ).toFixed(2)
                        }}%
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
