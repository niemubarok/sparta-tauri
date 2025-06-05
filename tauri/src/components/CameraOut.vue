<template>
  <!-- <video ref="videoRef" class="rounded-corner"></video> -->
  <div v-if="imageSrc">
  <img 
    :src="imageSrc" 
    alt="Camera Snapshot" 
    style="width: 49vw; height: 52vh" 
  />
  </div>
  <div v-else>
    <q-skeleton
      height="52vh"
      class="rounded-corner"
      width="49vw"
    >
      <template v-slot:default>
        <div class="absolute-center text-center text-grey-7">
          <q-icon name="camera_alt" size="xl" />
          <div>{{cameraStatus ? 'Loading Camera...' : 'Tidak Ada Kamera'}}</div>
        </div>
      </template>
    </q-skeleton>
  </div>
</template>

<script setup>
import { watch, ref, onMounted } from "vue";
import ls from "localstorage-slim";
import { useQuasar } from "quasar";
const $q = useQuasar();
import {api} from 'src/boot/axios'
// import 

// const cameraId = computed(ls.get("cameraIn").id);
// const cameraId = ref(ls.get("cameraIn"));
const imageSrc = ref(null);
const cameraStatus = ref(true)
// const cameraId = ref(
//   "http://10.40.38.54:80/ISAPI/Streaming/channels/1/picture"
// );
// const cameraId = ref(
//   "-"
// );
// const videoRef = ref(null);

// watch(
//   () => ls.get("cameraIn"),
//   (newValue) => {
//     cameraId.value = newValue;
//   }
// );
// const video = ref(null);
// const width = $q.screen.width <= 1366 ? "1280" : "720";
// const height = $q.screen.height <= 1366 ? "720" : "1180";

onMounted(async () => {
  const cameraUrl = ls.get("cameraOutUrl")
  const filename = `tes.png`
  const interval = ls.get("interval") || 5000
  let notFoundCount = 0;
  const intervalId = setInterval(async () => {
    try {
      const image = await api.get(`/cctv/snapshot?fileName=out_snapshot.png&cctv_url=${cameraUrl}`);
      if (image.status === 200) {
        imageSrc.value = image.data.base64;
        notFoundCount = 0;
      } else {
        ++notFoundCount;
        if (notFoundCount >= 5) {
          clearInterval(intervalId);
        }
      }
    } catch (error) {
      ++notFoundCount;
      if (notFoundCount >= 5) {
        clearInterval(intervalId);
        cameraStatus.value = false
      }
    }
  }, interval)
});
</script>
