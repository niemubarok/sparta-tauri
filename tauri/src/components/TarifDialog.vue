<template>
  <q-dialog ref="dialogRef" :maximized="true"  class="q-pa-xl"
    content-class="dialog__backdrop" >
    <div>
   <q-card
        style="width: 70vw; height: fit-content"
        class="q-px-md q-pt-xl q-pb-md glass rounded-corner relative fixed-center"
      >
      <q-card-section>
        <q-input
          v-model="tarif"
          label="Masukan Tarif Parkir"
          borderless
          autofocus
          class="input-box bg-primary rounded-corner relative q-pa-sm"
          input-class="input-box text-white text-h1 font-weight-bolder"
          label-color="yellow text-h3"
          color="teal"
          :rules="[
            (val) => (val ? val.length >= 1 || 'Masukkan Tarif' : true),

          ]"
          @keydown.enter="onSubmit"
          >
          <template v-slot:append>
            <q-btn
              push
              :size="'xl'"
              class="q-mt-xl q-mr-lg bg-white text-dark"
              icon="keyboard_return"
            />
          </template>
        </q-input>
      </q-card-section>
    </q-card>
    </div>
  </q-dialog>
</template>

<script setup>
import { useDialogPluginComponent, useQuasar } from "quasar";
// import SuccessCheckMark from "./SuccessCheckMark.vue";
import { onMounted, onBeforeUnmount, onBeforeMount, ref } from "vue";
import { useComponentStore } from "src/stores/component-store";
import SettingsDialog from "src/components/SettingsDialog.vue";
import ls from "localstorage-slim";
import { useTransaksiStore } from "src/stores/transaksi-store";

const { dialogRef } = useDialogPluginComponent();
const componentStore = useComponentStore();
const transaksiStore = useTransaksiStore();

const $q = useQuasar();
const props = defineProps({
  type: String,
  url: String,
  component: String,
});

const tarif = ref();

defineEmits([...useDialogPluginComponent.emits]);

const onSubmit = async () => {
  console.log(tarif.value)
  if (tarif.value || tarif.value !== undefined) {
    transaksiStore.biayaParkir = tarif.value;
    transaksiStore.setCheckIn(true);
    dialogRef.value.hide();
    componentStore.currentPage = "payment";
  
  } else {
    $q.notify({
      type: "negative",
      message: "Tarif Harus Diisi",
      position: "center",
      timeout: 1000,
    });
  }
}

const handleKeyDownOnTarifDialog = async (event) => {
  if (event.key === "Escape") {
    event.preventDefault();
    dialogRef.value.hide();
  }
};

onMounted(() => {
  window.addEventListener("keydown", handleKeyDownOnTarifDialog);
  console.log(componentStore.currentPage);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeyDownOnTarifDialog);
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
  background-color: rgba(0, 0, 0, 0.432);
  backdrop-filter: blur(30px);
}
.glass {
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  background-color: rgba(255, 255, 255, 0.301);
  border-radius: 20px;
  border: 1px solid rgba(14, 13, 13, 0.125);
}

/* :deep(.input-box .q-field__append), */
:deep(.input-box .q-field__control),
:deep(.input-box .q-field__append .q-field__marginal) {
  height: 20vh;
  width: 80vw;
  font-size: 2rem;
  font-family: "Courier New", Courier, monospace;
}
</style>
