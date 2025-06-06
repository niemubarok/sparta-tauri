<template>
  <q-page class="flex column flex-start card-gradient" style="overflow-y: auto" padding>
    <!-- Summary Cards -->
    <div class="full-width flex row flex-center">
      <template v-for="data in summaryData" :key="data.caption">
        <CardNumber
          :caption="data.caption"
          :number="data.number"
          :icon="data.icon"
          class="col-md col-xs-11 q-my-sm q-mx-sm"
          style="height: 20vh"
        />
      </template>
    </div>

    <!-- Gates Grid -->
    <div class="row q-col-gutter-md q-mt-md">
      <div v-for="gate in gateSettings" :key="gate.gateId" class="col-md-6 col-lg-4">
        <q-card class="gate-card">
          <q-card-section :class="gate.gateType === 'entry' ? 'bg-positive text-white' : 'bg-negative text-white'">
            <div class="text-h6">{{ gate.gateName }}</div>
            <q-badge :color="gate.gateType === 'entry' ? 'green-9' : 'red-9'">
              {{ gate.gateType === 'entry' ? 'Gerbang Masuk' : 'Gerbang Keluar' }}
            </q-badge>
            <q-badge :color="gateStatuses[gate.gateId] ? 'green' : 'grey'" class="q-ml-sm">
              {{ gateStatuses[gate.gateId] ? 'Terbuka' : 'Tertutup' }}
            </q-badge>
          </q-card-section>

          <q-card-section>
            <div class="row q-gutter-sm">
              <div class="col-12">
                <div class="text-subtitle2">Status Kamera:</div>
                <q-list dense>
                  <q-item v-if="gate.PLATE_CAM_IP">
                    <q-item-section>
                      <q-item-label>Kamera Plat</q-item-label>
                      <q-item-label caption>{{ gate.PLATE_CAM_IP }}</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-btn flat round size="sm" icon="camera" @click="showCameraPreview(gate, 'PLATE_CAM')" />
                    </q-item-section>
                  </q-item>
                  <q-item v-if="gate.DRIVER_CAM_IP">
                    <q-item-section>
                      <q-item-label>Kamera Pengemudi</q-item-label>
                      <q-item-label caption>{{ gate.DRIVER_CAM_IP }}</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-btn flat round size="sm" icon="camera" @click="showCameraPreview(gate, 'DRIVER_CAM')" />
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>
            </div>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn color="primary" :loading="gateStatuses[gate.gateId]" label="Buka Gate" @click="openGate(gate.gateId)" />
            <q-btn color="warning" label="Reset" @click="resetGate(gate.gateId)" />
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <!-- Camera Preview Dialog -->
    <q-dialog v-model="showPreview">
      <q-card style="min-width: 350px">
        <q-card-section class="row items-center">
          <div class="text-h6">Preview Kamera</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <div class="camera-preview">
            <img :src="previewImageUrl" v-if="previewImageUrl" />
            <div v-else class="text-center">Loading...</div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from "vue";
import CardNumber from "src/components/CardNumber.vue";
import { useSettingsService } from "src/stores/settings-service";
import { useTransaksiStore } from "src/stores/transaksi-store";

const settingsService = useSettingsService();
const transaksiStore = useTransaksiStore();

const gateSettings = ref([]);
const showPreview = ref(false);
const previewImageUrl = ref("");

// Summary cards data
const summaryData = ref([
  {
    caption: "Total Kendaraan Masuk",
    get number() {
      return transaksiStore.totalVehicleIn;
    },
    icon: "directions_car",
  },
  {
    caption: "Total Kendaraan Keluar",
    get number() {
      return transaksiStore.totalVehicleOut;
    },
    icon: "logout",
  },
  {
    caption: "Kendaraan di Dalam",
    get number() {
      return transaksiStore.totalVehicleInside;
    },
    icon: "local_parking",
  },
  {
    caption: "Total Gate Aktif",
    get number() {
      return gateSettings.value.length;
    },
    icon: "door_front",
  },
]);

onMounted(async () => {
  // Load initial data
  gateSettings.value = await settingsService.getAllGateSettings();
  await transaksiStore.getCountVehicleInToday();
  await transaksiStore.getCountVehicleOutToday();
  await transaksiStore.getCountVehicleInside();
  
  // Set up auto-refresh
  setInterval(async () => {
    await transaksiStore.getCountVehicleInToday();
    await transaksiStore.getCountVehicleOutToday();
    await transaksiStore.getCountVehicleInside();
  }, 30000);
});

const showCameraPreview = async (gate, cameraType) => {
  showPreview.value = true;
  previewImageUrl.value = "";

  try {
    const config = {
      username: gate[`${cameraType}_USERNAME`],
      password: gate[`${cameraType}_PASSWORD`],
      ipAddress: gate[`${cameraType}_IP`],
      rtspStreamPath: gate[`${cameraType}_RTSP_PATH`],
    };

    const response = await invoke("capture_cctv_image", { args: config });
    if (response.is_success && response.base64) {
      previewImageUrl.value = `data:image/jpeg;base64,${response.base64}`;
    }
  } catch (error) {
    console.error("Failed to get camera preview:", error);
  }
};

const openGate = async (gateId) => {
  try {
    await transaksiStore.setManualOpenGate(gateId);
  } catch (error) {
    console.error("Failed to open gate:", error);
  }
};

const resetGate = async (gateId) => {
  try {
    // Reset logic will be implemented based on your requirements
    console.log("Resetting gate:", gateId);
  } catch (error) {
    console.error("Failed to reset gate:", error);
  }
};
</script>

<style scoped>
.gate-card {
  transition: all 0.3s ease;
}

.gate-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.camera-preview {
  width: 100%;
  height: 300px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.camera-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
</style>
