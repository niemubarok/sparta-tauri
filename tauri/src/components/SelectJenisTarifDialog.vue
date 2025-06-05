<template>
  <q-card
    style="width: 50vw; height: fit-content"
    class="q-px-md q-pt-xl q-pb-md glass relative"
  >
    <div>
      <q-chip
        class="bg-yellow-7 text-h6 text-weight-bolder absolute-top-left q-pa-md"
        label="Pilih Jenis Tarif"
      />
    </div>

    <div v-for="(jenisTarif, index) in jenisTarifOptions">
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
          <q-item-label class="text-h6">{{ jenisTarif }}</q-item-label>
        </q-item-section>
      </q-item>
    </div>
  </q-card>
  <!-- </q-dialog> -->
</template>

<script setup>
import { useDialogPluginComponent } from "quasar";
import { onMounted, onBeforeUnmount, ref } from "vue";
import ls from "localstorage-slim";
import { useComponentStore } from "/src/stores/component-store";

// const jenisTarifRef = ref(false);

// defineEmits([
//   // REQUIRED; need to specify some events that your
//   // component will emit through useDialogPluginComponent()
//   ...useDialogPluginComponent.emits,
// ]);

// const { dialogRef } = useDialogPluginComponent();
// const onDialogHide = () => {
//   window.removeEventListener("keydown", handleKeydownOnjenisTarif);
//   componentStore.jenisTarif.in = jenisTarif.value;
// };

const componentStore = useComponentStore();
const jenisTarifOptions = ref(["Auto", "Manual"]);

onMounted(async () => {
  window.addEventListener("keydown", handleKeydownOnjenisTarif);
});

const handleKeydownOnjenisTarif = (event) => {
  const key = event.key;
  console.log(jenisTarifOptions.value[key - 1]);
  console.log(key);

  if (jenisTarifOptions.value[key - 1] !== undefined) {
    componentStore.jenisTarif = jenisTarifOptions.value[key - 1];
    ls.set("jenisTarif", jenisTarifOptions.value[key - 1]);
    componentStore.selectJenisTarifDialogModel = false;
  }

  if (key === "Escape") {
    componentStore.selectJenisTarifDialogModel = false;
  }
};


onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeydownOnjenisTarif);
});
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
