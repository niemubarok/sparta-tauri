<template>
  <q-card v-if="showDebug" class="fixed-top-right q-ma-md" style="z-index: 9999; width: 300px; max-height: 400px; overflow-y: auto;">
    <q-card-section>
      <div class="text-h6 flex items-center">
        📷 Camera Debug
        <q-space />
        <q-btn 
          flat 
          round 
          dense 
          icon="close" 
          @click="showDebug = false"
        />
      </div>
    </q-card-section>
    
    <q-card-section class="q-pt-none">
      <!-- Plate Camera Info -->
      <div class="q-mb-md">
        <div class="text-subtitle2 text-weight-bold">🚗 Kamera Plat Nomor</div>
        <div class="text-caption">
          <div>Type: <strong>{{ plateCameraType }}</strong></div>
          <div>IP: <strong>{{ plateCameraCredentials.ip_address }}</strong></div>
          <div>User: <strong>{{ plateCameraCredentials.username }}</strong></div>
          <div>Status: 
            <q-chip 
              :color="plateStatus === 'connected' ? 'green' : 'red'" 
              text-color="white" 
              size="sm"
            >
              {{ plateStatus }}
            </q-chip>
          </div>
        </div>
      </div>
      
      <!-- Driver Camera Info -->
      <div class="q-mb-md">
        <div class="text-subtitle2 text-weight-bold">👤 Kamera Driver</div>
        <div class="text-caption">
          <div>Type: <strong>{{ driverCameraType }}</strong></div>
          <div>IP: <strong>{{ driverCameraCredentials.ip_address }}</strong></div>
          <div>User: <strong>{{ driverCameraCredentials.username }}</strong></div>
          <div>Status: 
            <q-chip 
              :color="driverStatus === 'connected' ? 'green' : 'red'" 
              text-color="white" 
              size="sm"
            >
              {{ driverStatus }}
            </q-chip>
          </div>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="row q-gutter-sm">
        <q-btn 
          size="sm" 
          color="primary" 
          @click="testConnections"
          :loading="testing"
        >
          Test Koneksi
        </q-btn>
        <q-btn 
          size="sm" 
          color="secondary" 
          @click="captureTest"
          :loading="capturing"
        >
          Test Capture
        </q-btn>
      </div>
    </q-card-section>
  </q-card>
  
  <!-- Debug Toggle Button -->
  <q-btn
    v-if="!showDebug"
    fab
    color="info"
    icon="bug_report"
    class="fixed-top-right q-ma-md"
    style="z-index: 9998;"
    @click="showDebug = true"
  >
    <q-tooltip>Show Camera Debug</q-tooltip>
  </q-btn>
</template>

<script setup>
import { ref, computed, inject } from 'vue';
import { useQuasar } from 'quasar';

const props = defineProps({
  plateCameraType: String,
  driverCameraType: String,
  plateCameraCredentials: Object,
  driverCameraCredentials: Object,
  plateCameraRef: Object,
  driverCameraRef: Object
});

const $q = useQuasar();
const showDebug = ref(false);
const testing = ref(false);
const capturing = ref(false);
const plateStatus = ref('unknown');
const driverStatus = ref('unknown');

const testConnections = async () => {
  testing.value = true;
  
  try {
    // Test plate camera
    try {
      await props.plateCameraRef?.fetchCameraImage();
      plateStatus.value = 'connected';
    } catch (error) {
      plateStatus.value = 'disconnected';
      console.error('Plate camera test failed:', error);
    }

    // Test driver camera
    try {
      await props.driverCameraRef?.fetchCameraImage();
      driverStatus.value = 'connected';
    } catch (error) {
      driverStatus.value = 'disconnected';
      console.error('Driver camera test failed:', error);
    }

    $q.notify({
      type: 'info',
      message: 'Test koneksi selesai - lihat hasil di debug panel',
      position: 'top'
    });

  } finally {
    testing.value = false;
  }
};

const captureTest = async () => {
  capturing.value = true;
  
  try {
    let plateResult = false;
    let driverResult = false;

    // Test capture from both cameras
    try {
      const plateImage = await props.plateCameraRef?.getImage();
      plateResult = !!plateImage;
    } catch (error) {
      console.error('Plate capture failed:', error);
    }

    try {
      const driverImage = await props.driverCameraRef?.getImage();
      driverResult = !!driverImage;
    } catch (error) {
      console.error('Driver capture failed:', error);
    }

    $q.dialog({
      title: '📸 Capture Test Results',
      message: `
        <div>
          <p>🚗 Plat Camera: ${plateResult ? '✅ Success' : '❌ Failed'}</p>
          <p>👤 Driver Camera: ${driverResult ? '✅ Success' : '❌ Failed'}</p>
        </div>
      `,
      html: true
    });

  } finally {
    capturing.value = false;
  }
};
</script>

<style scoped>
.fixed-top-right {
  position: fixed;
  top: 0;
  right: 0;
}
</style>
