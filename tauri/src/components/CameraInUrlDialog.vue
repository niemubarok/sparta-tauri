<template>
  <!-- <q-dialog ref="dialogRef" no-backdrop-dismiss @hide="onDialogHide"> -->
    <q-card
      class="q-px-md q-pt-sm glass relative"
      style="width: 500px; height: fit-content"
    >
      <div>
        <q-avatar
          size="40px"
          class="cursor-pointer z-top absolute-top-right q-ma-sm"
          text-color="grey-7"
          color="grey-5"
          icon="close"
          />
          <!-- @click="dialogRef.hide()" -->
      </div>
      <!-- <q-icon name="close"  /> -->
      <q-item>
        <q-item-section avatar>
          <q-icon name="http" />
        </q-item-section>
        <q-item-section>
          <q-item-label
            style="margin-left: -20px"
            class="q-mt-xs text-weight-bolder"
            >URL CCTV Kamera Masuk</q-item-label
          >
        </q-item-section>
      </q-item>
      <q-separator inset />

      <div class="q-mt-md">
        <q-input
          filled
          class="q-mb-md"
          v-model="cameraInUrl"
          type="text"
          label="Masukkan URL"
          autofocus
          :rules="[(v) => !!v || 'URL harus diisi']"
          @keydown.enter="onSaveSettings"
        >
          <template v-slot:append>
            <q-btn push class="bg-dark text-white" icon="keyboard_return" />
          </template>
        </q-input>
      </div>
    </q-card>
  <!-- </q-dialog> -->
</template>

<script setup>
import { useDialogPluginComponent, useQuasar } from "quasar";
// import SuccessCheckMark from "./SuccessCheckMark.vue";
import { onMounted, ref } from "vue";
import { useComponentStore } from "src/stores/component-store";

import ls from "localstorage-slim";
import { useTransaksiStore } from "src/stores/transaksi-store";
import { useSettingsService } from "src/stores/settings-service"; // Diubah
// const transaksiStore = useTransaksiStore();
// // ls.config.encrypt = false;

// const $q = useQuasar();
const cameraInUrl = ref("");

const onDialogHide = () => {
  useComponentStore().settingsKey = true
  // if (!transaksiStore.API_URL || transaksiStore.API_URL === "-") {
  //   dialogRef.value.show();
  //   $q.notify({
  //     type: "negative",
  //     message: "Silahkan Isi URL API terlebih dahulu",
  //     position: "center",
  //   });
  // }
};
// defineEmits([...useDialogPluginComponent.emits]);

// const { dialogRef } = useDialogPluginComponent();
onMounted(async () => {
  const { gateSettings, saveGateSettings } = useSettingsService();
cameraInUrl.value = gateSettings.value?.PLATE_CAM_URL || ''; // Diubah
});

const onSaveSettings = () => {
  const newSettings = { ...gateSettings.value, PLATE_CAM_URL: cameraInUrl.value };
saveGateSettings(newSettings); // Diubah
  useComponentStore().selectCameraInDialogModel = false;
  // dialogRef.value.hide();
  // window.location.reload();
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
