<template>
  <div class="camera-container">
    <q-chip v-if="label"
      style="border-radius:8px; top: 0px; left: 0px; font-size:medium; background-color: rgba(0, 0, 0, 0.5);"
      class="text-white absolute inset-shadow" :label="label" />
    <div class="connection-indicator" :class="{ 'connected': cameraStatus }">
      <div class="indicator-dot"></div>
    </div>

   

    <div v-if="cameraType === 'usb'" class="rounded-corner camera-view">
      <video ref="videoRef" class="rounded-corner"></video>
    </div>
    <div v-else-if="cameraType === 'manual' && imageSrc" class="camera-view">
      <img :src="imageSrc" alt="Manual image" @error="(e) => {
        console.error('Image load error:', e);
        message = 'Invalid image data';
        cameraStatus = false;
      }" />
      <span class="text-red">{{ message }}</span>
    </div>
    <div v-else-if="cameraType === 'cctv'" class="camera-view">

      <q-skeleton v-if="!imageSrc" class="full-height">
        <template v-slot:default>
          <div class="absolute-center text-center text-grey-7">
            <q-icon name="camera_alt" size="xl" />
            <div>{{ message }}</div>
          </div>
        </template>
      </q-skeleton>


      <img v-else-if="imageSrc && typeof imageSrc === 'string' && imageSrc.startsWith('data:image')" :src="imageSrc" alt="CCTV image" @error="(e) => {
        console.error('Image load error:', e);
        message = 'Invalid image data';
        cameraStatus = false;
      }" />
    </div>
    <div v-else class="camera-view">
      <q-skeleton class="full-height">
        <template v-slot:default>
          <div class="absolute-center text-center text-grey-7">
            <q-icon name="camera_off" size="xl" />
            <div>Tidak ada kamera yang digunakan</div>
          </div>
        </template>
      </q-skeleton>
    </div>

    <q-toggle
      v-if="cameraType === 'cctv' "
      v-model="isLiveModeActive"
      label="Live"
      class="absolute z-top"
      style="bottom: 5px; right: 5px; background-color: rgba(0,0,0,0.3); padding: 2px 8px; border-radius: 15px;"
      color="green"
      dense
      @update:model-value="handleModeChange"
    />
  </div>
</template>

<script setup>
import { watch, ref, onMounted, onUnmounted, computed, nextTick } from "vue";
import ls from "localstorage-slim";
import { useQuasar } from "quasar";
import { useRouter } from "vue-router";
import { invoke } from '@tauri-apps/api/core';
import { base64ToBlob } from "src/utils/helpers.js";
import { useCameraStore } from "src/stores/camera-store";
import { useGateStore } from "src/stores/gate-store";
import { listen } from '@tauri-apps/api/event';

let unlistenLiveFrame = null;
const streamId = ref(null);

const props = defineProps({
  cameraLocation: String,
  cameraUrl: String,
  fileName: String,
  deviceId: String,
  isInterval: {
    type: Boolean,
    default: true,
  },
  cameraType: {
    type: String,
    default: 'default',
  },
  label: {
    type: String,
    default: '',
  },
  manualBase64: {
    type: String,
    default: '',
  },
  cropArea: Object,
  username: {
    type: String,
    default: 'admin',
  },
  password: {
    type: String,
    default: 'Hiks2024',
  },
  ipAddress:{
    type: String,
    default:'192.168.10.25'
  },
  rtspStreamPath:{
    type: String,
    default:'Streaming/Channels/101'
  },
  label: { type: String, default: 'Camera' },
});

const $q = useQuasar();
const router = useRouter();
const imageSrc = ref('');
const cameraStatus = ref(true);
const videoRef = ref(null);
const stream = ref(null);
const message = ref("Loading Image...");
const connectionCheckInterval = ref(null);
const intervalId = ref(null);
const isLiveStreamEnabled = ref(false); // Actual current state of the RTSP stream, true if playing/attempting, false otherwise
const isLiveModeActive = ref(
  (props.cameraType === 'cctv' )
    ? (ls.get(`liveModeActive_${props.cameraUrl}_${props.label || 'default'}`) === null ? true : !!ls.get(`liveModeActive_${props.cameraUrl}_${props.label || 'default'}`))
    : false
);
const cameraStore = useCameraStore()
const gateStore = useGateStore()

const emit = defineEmits(['captured', 'error']);



const retryCount = ref(0);
const maxRetries = 3;
const retryDelay = 2000; // 2 seconds
const notFoundCount = ref(0);

// Update the computed cameraDeviceId
const cameraDeviceId = computed(() => props.deviceId);

// Update USB camera initialization to use specific device
const initUsbCamera = async (deviceId) => {
  try {
    stream.value = await navigator.mediaDevices.getUserMedia({
      video: {
        deviceId: deviceId ? { exact: deviceId } : undefined
      }
    });
    if (videoRef.value) {
      videoRef.value.srcObject = stream.value;
      videoRef.value.play();
    }
    message.value = '';
  } catch (error) {
    message.value = 'Cannot access USB camera';
    console.error('Error accessing USB camera:', error);
    emit('error', error);
  }
};

// Method to get image from either USB or CCTV camera
const getImage = async () => {
  try {
    let imageFile;
    if(props.cameraType === 'cctv') {
    
     
          imageFile = await fetchCameraImage()
            
    } else  {
      // Capture from USB camera
      if (!videoRef.value || !videoRef.value.srcObject) {
        throw new Error('Camera not initialized');
        return
      }
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.value.videoWidth;
      canvas.height = videoRef.value.videoHeight;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      ctx.drawImage(videoRef.value, 0, 0);

      // Convert canvas to Blob
      const blob = await new Promise((resolve) => {
        canvas.toBlob(resolve, 'image/jpeg', 0.95);
      });

      // Create a File object from the blob
      imageFile = new File([blob], 'plate.jpg', { type: 'image/jpeg' });
    } 

    // Crop the image if cropArea is provided
    if (props.cropArea) {
      const croppedImage = await cropImageFromFile(imageFile, props.cropArea);
      return croppedImage;
    }

    return imageFile;
  } catch (error) {
    console.error('Error capturing image:', error);
    emit('error', error);
    throw error;
  }
};

// Helper to convert File to base64 string (tanpa prefix)
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      // Remove prefix if exists
      const result = reader.result;
      const base64 = result.includes(',') ? result.split(',')[1] : result;
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

const cropImageFromFile = (file, cropArea) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const image = new Image();
      image.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d', { willReadFrequently: true });

        canvas.width = cropArea.width;
        canvas.height = cropArea.height;

        ctx.drawImage(
          image,
          cropArea.x,
          cropArea.y,
          cropArea.width,
          cropArea.height,
          0,
          0,
          cropArea.width,
          cropArea.height
        );

        canvas.toBlob((blob) => {
          if (blob) {
            resolve(new File([blob], file.name, { type: file.type }));
          } else {
            reject(new Error('Failed to crop image'));
          }
        }, file.type);
      };
      image.onerror = reject;
      image.src = reader.result;
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

const fetchCameraImage = async () => {
  try {
    // if (router.currentRoute.value.path !== "/") {
    //   return;
    // }
    
    const    config = {
      username: props.username,
      password: props.password,
      ipAddress: props.ipAddress, // Mengubah ip_address menjadi ipAddress
      rtspStreamPath: props.rtspStreamPath,
    }
    // Use Tauri invoke to capture image from CCTV
    const response = await invoke('capture_cctv_image', { args: config });
    if (response && response.is_success && response.base64) {
      imageSrc.value = response.base64;
      
      message.value = '';
      retryCount.value = 0;
      notFoundCount.value = 0;
      cameraStatus.value = true;
      return response.base64;
    } else {
      message.value = response && response.message ? response.message : 'Failed to capture image from CCTV';
      cameraStatus.value = false;
    }
  } catch (error) {
    ++notFoundCount.value;
    if (error.code === 'ERR_NETWORK' && retryCount.value < maxRetries) {
      message.value = `Connection lost. Retrying... (${retryCount.value + 1}/${maxRetries})`;
      retryCount.value++;
      setTimeout(fetchCameraImage, retryDelay);
    } else if (notFoundCount.value >= 5) {
      clearInterval(intervalId);
      cameraStatus.value = false;
      message.value = 'Camera connection failed';
      emit('error', error);
    }
  }
};

const setManualBase64 = async (base64String) => {
  try {
    if (!base64String) {
      throw new Error('Base64 string is empty');
    }

    // Check if base64 string already has a prefix
    let fullBase64 = base64String.startsWith('data:image')
      ? base64String
      : `data:image/jpeg;base64,${base64String}`;

    // Create an image element to apply cropping
    const image = new Image();
    image.src = fullBase64;

    image.onload = async () => {
      if (props.cropArea) {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d', { willReadFrequently: true });

        canvas.width = props.cropArea.width;
        canvas.height = props.cropArea.height;

        ctx.drawImage(
          image,
          props.cropArea.x,
          props.cropArea.y,
          props.cropArea.width,
          props.cropArea.height,
          0,
          0,
          props.cropArea.width,
          props.cropArea.height
        );

        // Convert cropped canvas to base64
        fullBase64 = canvas.toDataURL('image/jpeg');
      }

      cameraStore.imgSrc = fullBase64;
      message.value = '';
      cameraStatus.value = true;
    };

    image.onerror = () => {
      throw new Error('Failed to load manual image');
    };
  } catch (error) {
    console.error('Error setting manual image:', error);
    message.value = 'Invalid image data';
    cameraStatus.value = false;
  }
};

const startLiveStream = async () => {
  try {
    if (!props.ipAddress) {
      throw new Error('RTSP IP is not provided');
    }

    // Stop any existing live stream before starting a new one
    await stopLiveStream();

    // Generate a unique stream ID for this session
    streamId.value = `stream-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Start listening for live frames from the backend
    unlistenLiveFrame = await listen(`cctv-live-frame::${streamId.value}`, (event) => {
      const base64Payload = event.payload;
      // console.log(`Received frame for stream ${streamId.value}. Payload length: ${base64Payload.length}`);
      // Log first 50 and last 50 characters of the payload for inspection
      // console.log(`Payload snippet: ${base64Payload.substring(0, 50)}...${base64Payload.substring(base64Payload.length - 50)}`);
      imageSrc.value = `data:image/jpeg;base64,${base64Payload}`;
      // console.log(`imageSrc updated. Length: ${imageSrc.value.length}`);
      cameraStatus.value = true;
      message.value = '';
    });
    // Invoke the Rust command to start the RTSP live stream
    const result = await invoke('start_rtsp_live_stream', {
      args: {
        streamId: streamId.value,
        username: props.username,
        password: props.password,
        ipAddress: props.ipAddress,
        rtspStreamPath: props.rtspStreamPath,
      },
    });
    if (!result.is_success) {
      throw new Error(result.message || 'Failed to start RTSP live stream');
    }

    console.log('RTSP Live stream started:', result.message);
    isLiveStreamEnabled.value = true; // Set to true when stream successfully starts

    // Set a placeholder message while waiting for the first frame
    message.value = 'Starting live stream...';
    imageSrc.value = ''; // Clear previous image

    // Clear interval if it was running for snapshot mode
    if (intervalId.value) {
      clearInterval(intervalId.value);
      intervalId.value = null;
    }
  } catch (error) {
    console.error('Error starting live stream:', error);
    message.value = 'Failed to start live stream';
    cameraStatus.value = false;
    isLiveStreamEnabled.value = false; // Ensure stream enabled is false on error
    emit('error', error);
  }
};

const stopLiveStream = async () => {
  // Stop listening to events if active
  if (unlistenLiveFrame) {
    unlistenLiveFrame();
    unlistenLiveFrame = null;
  }

  // Clear image source
  imageSrc.value = '';

  // Stop any ongoing interval for snapshot mode
  if (intervalId.value) {
    clearInterval(intervalId.value);
    intervalId.value = null;
  }

  // Only try to stop the backend stream if a streamId exists and it was enabled
  if (streamId.value && isLiveStreamEnabled.value) {
    try {
      const result = await invoke('stop_rtsp_live_stream', {
        streamId: streamId.value,
      });
      if (result.is_success) {
        console.log('Live stream stopped:', result.message);
      } else {
        console.error('Failed to stop live stream:', result.message);
      }
    } catch (error) {
      console.error('Error invoking stop_rtsp_live_stream:', error);
    } finally {
      streamId.value = null; // Ensure streamId is cleared after attempt to stop
    }
  }

  isLiveStreamEnabled.value = false;
  imageSrc.value = ''; // Clear displayed image
  message.value = 'Live stream stopped.';

  // If we were in live mode, and it's stopped, we might want to fetch an image if interval is desired
  if (!isLiveModeActive.value && props.isInterval) {
    fetchCameraImage(); // Fetch initial image for interval mode
  }
}; 


watch(() => props.manualBase64, (newValue) => {
  console.log("Manual base64 changed:", newValue ? newValue.substring(0, 50) + '...' : 'empty')
  if (newValue) {
    setManualBase64(newValue)
  }
}, { immediate: true });


watch(() => cameraStore.imgSrc, (newValue) => {
  // console.log("ImageSrc changed:", newValue ? newValue.substring(0, 50) + '...' : 'empty')
  if (newValue) {
    imageSrc.value = newValue
    message.value = '';
    cameraStatus.value = true;
  }
}, { immediate: true });

// Update initialization logic
onMounted(async () => {
  if (props.cameraType === 'usb') {
    try {
      // Use props.deviceId directly if available, otherwise fallback to cameraDeviceId computed value
      const deviceToUse = cameraDeviceId.value;
      if (deviceToUse) {
        await initUsbCamera(deviceToUse);
      } else {
        // Optionally, handle the case where no deviceId is available
        // For example, try to initialize with default/any camera or show an error
        console.warn('No USB camera deviceId provided, attempting to use default camera.');
        await initUsbCamera(); // Attempt to initialize without a specific deviceId
      }
    } catch (error) {
      console.error('Error initializing USB camera:', error);
      message.value = 'Cannot access USB camera. Please check permissions and ensure a camera is connected.';
      emit('error', error);
    }
    return;
  }

  // CCTV camera logic
  const intervalValue = ls.get("interval") || 5000;
  // let intervalId; // intervalId is already defined in the component scope

  if (props.cameraType === 'cctv') {
    if (isLiveModeActive.value ) {
      isLiveStreamEnabled.value = true; // Attempt to start live stream
      await nextTick();
      startLiveStream();
    } else if (props.isInterval) {
      if (intervalId.value) clearInterval(intervalId.value); // Clear existing interval if any
      intervalId.value = setInterval(fetchCameraImage, intervalValue);
      fetchCameraImage(); // Initial fetch
    } else {
      await fetchCameraImage(); // Fetch once if not interval and not live
    }
  } else if (props.isInterval) { // For non-CCTV types that support interval
    if (intervalId.value) clearInterval(intervalId.value); // Clear existing interval if any
    intervalId.value = setInterval(fetchCameraImage, intervalValue);
    fetchCameraImage(); // Initial fetch
  } else if (props.cameraType !== 'usb') { // For non-USB, non-interval types, fetch once
    await fetchCameraImage();
  }

  // The logic for starting CCTV live stream or interval is now within the main block above
  // This specific block is redundant after the changes.

  onUnmounted(() => {
    // socket.off('snapshot_result');
    // clearInterval(connectionCheckInterval);
    // if (intervalId.value) clearInterval(intervalId.value); // Now handled in onUnmounted
    if (stream.value) { // For USB camera stream
      stream.value.getTracks().forEach(track => track.stop());
    }
  });
});

// onUnmounted(() => {
//   if (stream.value) {
//     stream.value.getTracks().forEach(track => track.stop());
//   }
//   if (liveStreamVideoRef.value && (liveStreamVideoRef.value.srcObject || liveStreamVideoRef.value.src)) {
//     if (liveStreamVideoRef.value.srcObject) {
//       const tracks = liveStreamVideoRef.value.srcObject.getTracks();
//       tracks.forEach(track => track.stop());
//       liveStreamVideoRef.value.srcObject = null;
//     }
//     liveStreamVideoRef.value.src = ''; // Clear src for MJPEG case too
//   }
//   // Stop RTSP stream if it was running
//   if (props.cameraType === 'cctv' && isLiveStreamEnabled.value) { // Check isLiveStreamEnabled
//     stopLiveStream(); // Use the new unified stopLiveStream function
//   }
//   // Clear interval if it was running
//   if (intervalId.value) {
//     clearInterval(intervalId.value);
//   }
// });

const handleModeChange = async (newValue) => { // newValue is the new state of isLiveModeActive, already updated by v-model
  if (props.cameraType === 'cctv' ) {
    ls.set(`liveModeActive_${props.cameraUrl}_${props.label || 'default'}`, newValue);

  // The rest of the condition 'if (props.cameraType === 'cctv' && props.cameraUrl && props.cameraUrl.startsWith('rtsp://'))' was here
  // It's now the outer condition for setting ls and the subsequent logic.
  // The 'value' parameter is now 'newValue' for clarity.
  // The line 'isLiveModeActive.value = value;' is removed as v-model handles it.

    if (newValue) { // Switched to Live (isLiveModeActive.value is now true)
   
      if (intervalId.value) {
        clearInterval(intervalId.value);
        intervalId.value = null;
      }
      await nextTick();
      startLiveStream();
    } else {
      // Switched to Interval
      stopLiveStream();
      imageSrc.value = ''; // Clear current image to show skeleton/loading
      message.value = 'Loading Image...'; // Reset message for interval mode
      message.value = 'Loading Image...';
      // if (props.isInterval) {
        const intervalValue = ls.get("interval") || 5000;
        if (intervalId.value) clearInterval(intervalId.value);
        intervalId.value = setInterval(fetchCameraImage, intervalValue);
        await fetchCameraImage(); // Initial fetch for interval mode
      // } else {
      //   await fetchCameraImage(); // Fetch once if not interval mode
      // }
    }
  }
};

// Expose the getImage method to be callable from the parent
defineExpose({ getImage, fetchCameraImage });
</script>

<style scoped>
.camera-container {
  position: relative;
  width: 100%;
  /* Default height, can be overridden by props or specific styles */
  /* height: 200px; */
  height: 40dvh;
  background-color: #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  /* Added for inset shadow */
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.2);
}

.camera-view {
  width: 100%;
  height: 100%;

  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  /* Ensure content fits within rounded corners */
}

.camera-container video,
.camera-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  
  /* Ensures the video/image covers the area, might crop */
  border-radius: 8px;
  /* Apply to video/image itself if they are direct children */
}

.rounded-corner {
  border-radius: 8px;
  overflow: hidden;
}

.connection-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 20px;
  height: 20px;
  background-color: #ccc; /* Default grey */
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10; /* Ensure it's above the video/image */
}

.indicator-dot {
  width: 12px;
  height: 12px;
  background-color: red; /* Default to red (not connected) */
  border-radius: 50%;
  transition: background-color 0.3s ease;
}

.connection-indicator.connected .indicator-dot {
  background-color: limegreen; /* Green when connected */
}

.full-height {
  height: 100%;
  width: 100%;
}

.z-top {
  z-index: 1000; /* Ensure toggle is on top */
}
</style>
