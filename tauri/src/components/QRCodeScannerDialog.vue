<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" maximized persistent>
    <div class="full-width flex flex-center q-px-none q-pt-none q-mt-none q-mb-none">
      <q-spinner-dots class="q-mt-md" color="primary" v-if="scanning" size="50px" />

    
    <q-card class="q-px-md q-pt-sm glass relative" style="width: 60dvw; height: fit-content">
      <div>
        <q-avatar
          size="40px"
          class="cursor-pointer z-top absolute-top-right q-ma-sm"
          text-color="grey-7"
          color="grey-5"
          icon="close"
          @click="$emit('hide')"
        />
      </div>

    <div class="text-center q-pb-md q-mt-md">
        <q-icon name="qr_code_2" size="100px" class="text-primary" />
      <h1 class="q-my-none text-weight-bold text-primary">
        Scan QR Code
      </h1>
      <!-- <div class="text-h6 text-grey-10">
        Position the QR code within the frame
      </div> -->
    </div>

      <q-card-section>
        <div class="scanner-container">
          <div class="scanner-overlay">
            <div class="scan-line"></div>
          </div>
          <div class="scanner-frame">
            <Camera 
              ref="videoRef"
              :cameraUrl="scannerCameraUrl"
              :fileName="'qrcode'"
              :isInterval="false"
              cameraLocation="scanner"
              :cameraType="scannerCameraDevice ? 'usb' : 'cctv'"
              @error="onCameraError"
              class="scanner-video"
              />
              <!-- label="QR Code Scanner" -->
          </div>
        </div>
      </q-card-section>

      <q-card-section v-if="lastResult" class="text-center">
        <q-chip color="primary" text-color="white">
          {{ lastResult }}
        </q-chip>
      </q-card-section>

    </q-card>
</div>
  </q-dialog>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useQuasar, useDialogPluginComponent } from 'quasar'
import QrDecoder from 'qrcode-decoder'
import Camera from './Camera.vue'
import ls from 'localstorage-slim'

const $q = useQuasar()
const videoRef = ref(null)
const scanning = ref(false)
const lastResult = ref(null)
const qr = new QrDecoder()

// Get scanner camera URL from localStorage 
const scannerCameraUrl = ref(ls.get('scannerCameraUrl') || '')
const scannerCameraDevice = ref(ls.get('scannerCameraDevice') || '')

const emit = defineEmits(['hide', 'scanned', ...useDialogPluginComponent.emits])
const { dialogRef } = useDialogPluginComponent()


const scan = async () => {
  if (!scanning.value) return
  
  try {
    // Wait for videoRef to be available
    if (!videoRef.value?.$el) {
      requestAnimationFrame(scan)
      return
    }

    // Get video element from Camera component
    const videoElement = videoRef.value.$el.querySelector('video')
    
    // Pastikan video sudah siap
    if (!videoElement || !videoElement.videoWidth) {
      requestAnimationFrame(scan)
      return
    }

    const result = await qr.decodeFromVideo(videoElement)
    
    if (result && result.data && result.data !== lastResult.value) {
      lastResult.value = result.data
      emit('scanned', result.data)
      
      $q.notify({
        type: 'positive',
        message: 'QR Code detected!',
        position: 'top'
      })
      
      setTimeout(() => {
        emit('hide')
      }, 1000)
    }
  } catch (err) {
    // Log error untuk debugging
    console.log("QR scan error:", err)
  }
  
  if (scanning.value) {
    requestAnimationFrame(scan)
  }
}

// Also update onMounted to give more time for component to initialize
onMounted(() => {
  // Use scanner camera settings if available, fallback to plate camera
  scannerCameraUrl.value = ls.get('scannerCameraUrl') || ls.get('plateCameraUrl') || ''
  scannerCameraDevice.value = ls.get('scannerCameraDevice') || ls.get('plateCameraDevice') || ''
  
  // Increase delay to ensure component is mounted
  setTimeout(() => {
    scanning.value = true
    scan()
  }, 2000) // Increased to 2 seconds
})

onBeforeUnmount(() => {
  scanning.value = false
})

const onDialogHide = () => {
  scanning.value = false
  emit('hide')
}

const onCameraError = (error) => {
  console.error("Camera error:", error)

}
</script>

<style scoped>
.scanner-container {
  position: relative;
  width: 50dvw;
  height: fit-content;
  margin: 0 auto;
  overflow: hidden;
}

.scanner-frame {
  width: 100%;
  height: fit-content;
  border: 2px solid #ccc;
  border-radius: 10px;
}

.scanner-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.scanner-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  border: 40px solid rgba(0, 0, 0, 0.3);
  border-radius: 10px;
}

.scan-line {
  position: absolute;
  width: 100%;
  height: 2px;
  background: #00ff00;
  animation: scan 2s linear infinite;
}

@keyframes scan {
  0% {
    top: 0;
  }
  100% {
    top: 100%;
  }
}

.glass {
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  background-color: rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.125);
}
</style>