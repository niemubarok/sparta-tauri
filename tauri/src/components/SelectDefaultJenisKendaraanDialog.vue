<template>
  <!-- :maximized="true" -->
  <!-- <q-dialog
    ref="dialogRef"
    v-model="defaultJenisKendaraanRef"
    @hide="onDialogHide"
    class="q-pa-xl"
    content-class="dialog__backdrop"
  > -->
  <!-- no-backdrop-dismiss
      no-route-dismiss -->
  <!-- :content-css="{ 'background-color': 'rgba(0, 0, 0, 0.9)' }" -->
  <q-card
    style="width: 50vw; height: fit-content"
    class="q-px-md q-pt-xl q-pb-md glass relative"
  >
    <!-- <div>
      <q-avatar
        size="40px"
        class="cursor-pointer z-top absolute-top-right q-ma-sm"
        text-color="grey-7"
        color="grey-5"
        icon="close"
        @click="dialogRef.hide()"
      />
    </div> -->
    <!-- <q-icon name="close"  /> -->
    <!-- <q-item> -->
    <!-- <q-item-section avatar>
            <q-icon :name="props.icon" size="xl" />
          </q-item-section> -->
    <!-- <q-item-section> -->
    <!-- style="margin-left: -15px" -->
    <div>
      <q-chip
        class="bg-yellow-7 text-h6 text-weight-bolder absolute-top-left q-pa-md"
        label="Pilih Jenis Kendaraan Default"
      />
    </div>

    <div v-for="(pos, index) in jenisKendaraanOptions">
      <!-- :class="
              defaultShortcut === jenisKendaraan.shortcut && 'bg-yellow text-dark'
            " -->
      <!-- {{ index }} -->
      <q-item class="q-ma-md bg-grey-4" style="border-radius: 5px">
        <q-item-section top avatar>
          <!-- <q-avatar color="primary" text-color="white" icon="bluetooth" /> -->
          <q-btn
            push
            class="bg-dark text-white text-weight-bolder q-px-md"
            :label="index + 1"
          />
        </q-item-section>
        <q-item-section>
          <q-item-label class="text-h6">{{ pos.label || "-" }}</q-item-label>
        </q-item-section>
      </q-item>
    </div>
  </q-card>
  <!-- </q-dialog> -->
</template>

<script setup>
import { useDialogPluginComponent } from "quasar";
import { onMounted, ref } from "vue";
import ls from "localstorage-slim";
import { useTransaksiStore } from "/src/stores/transaksi-store";
import { useComponentStore } from "/src/stores/component-store";

const defaultJenisKendaraanRef = ref(false);

defineEmits([
  // REQUIRED; need to specify some events that your
  // component will emit through useDialogPluginComponent()
  ...useDialogPluginComponent.emits,
]);

const { dialogRef } = useDialogPluginComponent();
const onDialogHide = () => {
  window.removeEventListener("keydown", handleKeydownOndefaultJenisKendaraan);
  transaksiStore.defaultJenisKendaraan = defaultJenisKendaraan.value;
};

const transaksiStore = useTransaksiStore();
const componentStore = useComponentStore();
const jenisKendaraanOptions = ref(["-"]);
const defaultJenisKendaraan = ref("");
onMounted(async () => {
  // jenisKendaraanOptions.value = await transaksiStore.getLokasiPos();
  jenisKendaraanOptions.value = await transaksiStore.getJenisKendaraan();
});

const handleKeydownOndefaultJenisKendaraan = (event) => {
  const key = event.key;

  if (jenisKendaraanOptions.value[key - 1] !== undefined) {
    transaksiStore.defaultJenisKendaraan = jenisKendaraanOptions.value[key - 1];
    ls.set("defaultJenisKendaraan", jenisKendaraanOptions.value[key - 1]);
    componentStore.selectDefaultJenisKendaraanDialogModel = false;
  }

  if (key === "Escape") {
    // dialogRef.value.hide();
    componentStore.selectDefaultJenisKendaraanDialogModel = false;
  }
  //   dialogRef.value.hide();
};

onMounted(async () => {
  //   console.log(jenisKendaraanOptions.value.findIndex((index) => index));

  window.addEventListener("keydown", handleKeydownOndefaultJenisKendaraan);
});

// onUnmounted(() => {
// //   window.removeEventListener("keydown", handleKeydownOnJenisKendaraan);
// // });
</script>

<style scoped>
:deep(.q-dialog__backdrop.fixed-full) {
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
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
  height: 10vh;
  width: 80vw;
  font-size: 2rem;
  font-family: "Courier New", Courier, monospace;
}
</style>
