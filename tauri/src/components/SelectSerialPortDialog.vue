<template>
  <q-card
    class="q-px-md q-pt-sm glass relative"
    style="width: 500px; height: fit-content"
  >
    <q-item>
      <q-item-section avatar>
        <q-icon name="settings_input_component" />
      </q-item-section>
      <q-item-section>
        <q-item-label
          style="margin-left: -20px"
          class="q-mt-xs text-weight-bolder"
          >Pilih Serial Port</q-item-label
        >
      </q-item-section>
      <q-item-section side>
        <q-btn icon="close" flat round dense @click="onDialogCancel" />
      </q-item-section>
    </q-item>
    <q-separator inset />

    <div class="q-pa-md">
      <q-input
        filled
        v-model="selectedPort"
        label="Serial Port (misal: COM3 atau /dev/ttyUSB0)"
        autofocus
        :rules="[val => !!val || 'Serial port tidak boleh kosong']"
        @keydown.enter.prevent="onSaveSettings"
      />
    </div>
    <q-card-actions align="right">
      <q-btn label="Batal" color="primary" flat @click="onDialogCancel" />
      <q-btn label="Simpan" color="primary" @click="onSaveSettings" :disable="!selectedPort"/>
    </q-card-actions>
  </q-card>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useQuasar } from 'quasar';
import { useComponentStore } from 'src/stores/component-store';
import { useSettingsService } from 'src/stores/settings-service';
import { storeToRefs } from 'pinia';

const $q = useQuasar();
const componentStore = useComponentStore();
const settingsService = useSettingsService();
const { gateSettings, saveGateSettings } = storeToRefs(settingsService);

const selectedPort = ref(null);

onMounted(() => {
  // Inisialisasi selectedPort dengan nilai dari gateSettings
  if (gateSettings.value && gateSettings.value.SERIAL_PORT) {
    selectedPort.value = gateSettings.value.SERIAL_PORT;
  }
});

// Watcher untuk memperbarui selectedPort jika gateSettings berubah dari luar
watch(() => gateSettings.value?.SERIAL_PORT, (newVal) => {
  selectedPort.value = newVal || null;
});

const onSaveSettings = () => {
  if (selectedPort.value) {
    saveGateSettings.value({ SERIAL_PORT: selectedPort.value });
    $q.notify({
      type: 'positive',
      message: `Serial port ${selectedPort.value} disimpan.`,
      position: 'top',
    });
  }
  componentStore.selectSerialPortDialogModel = false;
};

const onDialogCancel = () => {
  componentStore.selectSerialPortDialogModel = false;
};

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

<style scoped>
/* .glass {
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  background-color: rgba(255, 255, 255, 0.378);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.125);
}

:deep(.q-dialog__backdrop.fixed-full) {
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(30px);
} */
</style>
