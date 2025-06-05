<template>
  <q-card
    style="width: 50vw; height: fit-content"
    class="q-px-md q-pt-xl q-pb-md glass relative"
  >
    <div>
      <q-chip
        class="bg-yellow-7 text-h6 text-weight-bolder absolute-top-left q-pa-md"
        label="Pilih Kamera Pintu Masuk"
      />
    </div>

    <div v-for="(camera, index) in cameraOptions">
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
          <q-item-label class="text-h6">{{ camera.label || "-" }}</q-item-label>
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

// const cameraInRef = ref(false);

// defineEmits([
//   // REQUIRED; need to specify some events that your
//   // component will emit through useDialogPluginComponent()
//   ...useDialogPluginComponent.emits,
// ]);

// const { dialogRef } = useDialogPluginComponent();
const onDialogHide = () => {
  window.removeEventListener("keydown", handleKeydownOnCameraIn);
  componentStore.camera.in = cameraIn.value;
};

const componentStore = useComponentStore();
const cameraOptions = ref(["-"]);
const cameraIn = ref("");
const getAvailableCameras = () => {
  navigator.mediaDevices
    .enumerateDevices()
    .then((devices) => {
      devices.forEach((device) => {
        if (device.kind === "videoinput") {
          cameraOptions.value.push({
            label: device.label,
            value: device.deviceId,
          });
        }
      });
    })
    .catch((err) => {
      console.log(err.name + ": " + err.message);
    });
};

onMounted(async () => {
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then(() => {
      getAvailableCameras();
    })
    .catch((error) => {
      // Camera permission denied or error occurred
      console.error("Error accessing camera: ", error);
    });
  window.addEventListener("keydown", handleKeydownOnCameraIn);
});

const handleKeydownOnCameraIn = (event) => {
  const key = event.key;

  if (cameraOptions.value[key - 1] !== undefined) {
    componentStore.camera.in = cameraOptions.value[key - 1];
    ls.set("cameraIn", cameraOptions.value[key - 1]);
    componentStore.selectCameraInDialogModel = false;
  }

  if (key === "Escape") {
    componentStore.selectCameraInDialogModel = false;
  }
  //   componentStore.selectCameraInDialogModel = false
};

// onUnMount(async () => {

// });

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeydownOnCameraIn);
  if (ls.get("cameraIn") === "-") {
    componentStore.stopCamera();
  }
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
