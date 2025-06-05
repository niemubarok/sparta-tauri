<template>
  <q-dialog ref="dialogRef" no-backdrop-dismiss @hide="onDialogHide">
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
            >Pengaturan API URL</q-item-label
          >
        </q-item-section>
      </q-item>
      <q-separator inset />

      <div class="q-mt-md">
        <q-input
          filled
          class="q-mb-md"
          v-model="transaksiStore.API_URL"
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
  </q-dialog>
</template>

<script setup>
import { useDialogPluginComponent, useQuasar } from "quasar";
// import SuccessCheckMark from "./SuccessCheckMark.vue";
import { onMounted, ref } from "vue";
import { useComponentStore } from "src/stores/component-store";

import ls from "localstorage-slim";
import { useTransaksiStore } from "src/stores/transaksi-store";
const transaksiStore = useTransaksiStore();
// ls.config.encrypt = false;

const $q = useQuasar();

const onDialogHide = () => {
  if (!transaksiStore.API_URL || transaksiStore.API_URL === "-") {
    dialogRef.value.show();
    $q.notify({
      type: "negative",
      message: "Silahkan Isi URL API terlebih dahulu",
      position: "center",
    });
  }
};
onMounted(async () => {});

const onSaveSettings = () => {
  ls.set("API_URL", transaksiStore.API_URL);

  dialogRef.value.hide();
  window.location.reload();
};

defineEmits([...useDialogPluginComponent.emits]);

const { dialogRef } = useDialogPluginComponent();
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
