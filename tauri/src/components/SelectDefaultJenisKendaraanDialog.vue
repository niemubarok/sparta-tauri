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
        label="Pilih Jenis Kendaraan Default (Tekan shortcut keyboard)"
      />
    </div>

    <div v-for="(jenis, index) in jenisKendaraanOptions" :key="jenis.id || index">
      <q-item class="q-ma-md bg-grey-4" style="border-radius: 5px">
        <q-item-section top avatar>
          <q-btn
            push
            class="bg-dark text-white text-weight-bolder q-px-md"
            :label="jenis.shortcut || (index + 1)"
          />
        </q-item-section>
        <q-item-section>
          <q-item-label class="text-h6">{{ jenis.label || "-" }}</q-item-label>
          <q-item-label caption>{{ jenis.value || "-" }}</q-item-label>
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
import { useKendaraanStore } from "/src/stores/kendaraan-store";
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
  kendaraanStore.setDefaultJenisKendaraan(defaultJenisKendaraan.value);
};

const kendaraanStore = useKendaraanStore();
const componentStore = useComponentStore();
const jenisKendaraanOptions = ref([]);
const defaultJenisKendaraan = ref("");

onMounted(async () => {
  await kendaraanStore.loadJenisKendaraanFromLocal();
  jenisKendaraanOptions.value = kendaraanStore.jenisKendaraanList.map(jk => ({
    value: jk.id, // menggunakan id sebagai value
    label: jk.jenis,
    id: jk.id,
    shortcut: jk.shortcut || jk.id // fallback ke id jika shortcut tidak ada
  }));
});

const handleKeydownOndefaultJenisKendaraan = (event) => {
  const key = event.key.toUpperCase();

  // Cari berdasarkan shortcut
  const matchingOption = jenisKendaraanOptions.value.find(
    (option) => option?.shortcut?.toUpperCase() === key
  );

  if (matchingOption) {
    kendaraanStore.setDefaultJenisKendaraan(matchingOption);
    ls.set("defaultJenisKendaraan", matchingOption);
    componentStore.selectDefaultJenisKendaraanDialogModel = false;
  }

  // Fallback: jika tidak ada shortcut yang cocok, coba dengan angka (index + 1)
  if (!matchingOption && !isNaN(Number(key))) {
    const index = Number(key) - 1;
    if (jenisKendaraanOptions.value[index] !== undefined) {
      const selectedKendaraan = jenisKendaraanOptions.value[index];
      kendaraanStore.setDefaultJenisKendaraan(selectedKendaraan);
      ls.set("defaultJenisKendaraan", selectedKendaraan);
      componentStore.selectDefaultJenisKendaraanDialogModel = false;
    }
  }

  if (key === "ESCAPE") {
    componentStore.selectDefaultJenisKendaraanDialogModel = false;
  }
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
