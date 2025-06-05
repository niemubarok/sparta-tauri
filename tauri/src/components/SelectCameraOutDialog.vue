<template>
  <!-- :maximized="true" -->
  <!-- <q-dialog
    ref="dialogRef"
    v-model="cameraOutRef"
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
        label="Pilih Kamera Pintu Keluar"
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

// const cameraOutRef = ref(false);

// defineEmits([
//   // REQUIRED; need to specify some events that your
//   // component will emit through useDialogPluginComponent()
//   ...useDialogPluginComponent.emits,
// ]);

// const { dialogRef } = useDialogPluginComponent();
// const onDialogHide = () => {
//   window.removeEventListener("keydown", handleKeydownOnCameraOut);
//   componentStore.camera.out = cameraOut.value;
// };

const componentStore = useComponentStore();
const cameraOptions = ref(["-"]);
const cameraOut = ref("");
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
});

const handleKeydownOnCameraOut = (event) => {
  const key = event.key;

  if (cameraOptions.value[key - 1] !== undefined) {
    componentStore.camera.out = cameraOptions.value[key - 1];
    ls.set("cameraOut", cameraOptions.value[key - 1]);
    componentStore.selectCameraOutDialogModel = false;
  }

  if (key === "Escape") {
    componentStore.selectCameraOutDialogModel = false;
  }
};

onMounted(async () => {
  window.addEventListener("keydown", handleKeydownOnCameraOut);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeydownOnCameraOut);
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
