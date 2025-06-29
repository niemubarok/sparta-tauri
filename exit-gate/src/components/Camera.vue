<template>
  <div class="camera-container">
    <q-chip v-if="label"
      style="border-radius:8px; top: 0px; left: 0px; font-size:medium; background-color: rgba(0, 0, 0, 0.5);"
      class="text-white absolute inset-shadow" :label="label" />
    <div class="connection-indicator" :class="{ 'connected': cameraStatus }">
      <div class="indicator-dot"></div>
    </div>

    <div v-if="cameraType === 'cctv'" class="camera-view">
      <q-skeleton v-if="!imageSrc" class="full-height">
        <template v-slot:default>
          <div class="absolute-center text-center text-grey-7">
            <q-icon 
              :name="cameraStatus ? 'camera_alt' : 'camera_off'" 
              :color="cameraStatus ? 'grey-6' : 'red-6'"
              size="xl" 
            />
            <div class="q-mt-sm">{{ message }}</div>
            <div v-if="!cameraStatus && message.includes('check settings')" class="q-mt-xs text-caption">
              Check camera settings
            </div>
          </div>
        </template>
      </q-skeleton>

      <img v-else-if="imageSrc && typeof imageSrc === 'string' && imageSrc.startsWith('data:image')" 
           :src="imageSrc" 
           alt="CCTV image" 
           @error="handleImageError" />
    </div>
    <div v-else class="camera-view">
      <q-skeleton class="full-height">
        <template v-slot:default>
          <div class="absolute-center text-center text-grey-7">
            <q-icon name="camera_off" size="xl" />
            <div>No camera configured</div>
          </div>
        </template>
      </q-skeleton>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { invoke } from '@tauri-apps/api/core'

const props = defineProps({
  cameraLocation: String,
  fileName: String,
  cameraType: {
    type: String,
    default: 'cctv',
  },
  label: {
    type: String,
    default: 'Camera',
  },
  username: {
    type: String,
    default: 'admin',
  },
  password: {
    type: String,
    default: 'admin123',
  },
  ipAddress: {
    type: String,
    default: '192.168.1.100'
  },
  rtspStreamPath: {
    type: String,
    default: 'Streaming/Channels/1/picture' // Default snapshot path
  },
  fullUrl: {
    type: String,
    default: '' // Full URL for camera (e.g., http://username:password@192.168.1.11/ISAPI/Streaming/channels/101/picture)
  },
  isInterval: {
    type: Boolean,
    default: true,
  },
  intervalTime: {
    type: Number,
    default: 5000,
  }
})

const emit = defineEmits(['captured', 'error'])

const imageSrc = ref('')
const cameraStatus = ref(true)
const message = ref('Loading Image...')
const intervalId = ref(null)
const retryCount = ref(0)
const maxRetries = 3

// Method to get image from CCTV camera
const getImage = async () => {
  try {
    if (props.cameraType === 'cctv') {
      const imageData = await fetchCameraImage()
      if (imageData) {
        // Convert base64 to blob for consistency with camera-service expectations
        const base64Data = imageData.replace(/^data:image\/[a-z]+;base64,/, '')
        const binaryString = atob(base64Data)
        const bytes = new Uint8Array(binaryString.length)
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i)
        }
        const blob = new Blob([bytes], { type: 'image/jpeg' })
        return blob
      }
    }
    throw new Error('Failed to capture image from camera')
  } catch (error) {
    console.error('Error capturing image:', error)
    emit('error', error)
    throw error
  }
}

const fetchCameraImage = async () => {
  try {
    // Check if we have camera configuration (either full URL or individual components)
    if (!props.fullUrl && !props.ipAddress) {
      console.warn('Camera not configured - no URL or IP provided')
      message.value = 'Camera not configured - check settings'
      cameraStatus.value = false
      return null
    }
    
    // Prepare request arguments
    const args = {}
    
    if (props.fullUrl) {
      // Use full URL if provided
      args.full_url = props.fullUrl
    } else {
      // Use individual components
      args.username = props.username || null
      args.password = props.password || null
      args.ip_address = props.ipAddress
      args.snapshot_path = props.rtspStreamPath
    }

    // console.log('📸 Capturing CCTV image with config:', {
    //   ...args,
    //   password: args.password ? '***' : null,
    //   full_url: args.full_url ? args.full_url.replace(/:[^:]+@/, ':***@') : undefined,
    //   cameraType: props.cameraType,
    //   label: props.label
    // })
    
    // Use Tauri invoke to capture image from CCTV with timeout
    const response = await Promise.race([
      invoke('capture_cctv_image', { args }), // Wrap args in object
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('CCTV capture timeout')), 10000) // Increase timeout to 10 seconds
      )
    ])
    
    if (response && response.is_success && response.base64) {
      imageSrc.value = response.base64
      message.value = ''
      retryCount.value = 0
      cameraStatus.value = true
      
      // Emit captured event
      emit('captured', {
        image: response.base64,
        timestamp: new Date().toISOString(),
        camera: props.label
      })
      
      return response.base64
    } else {
      const errorMsg = response?.message || 'Unknown error from CCTV camera'
      handleCameraError(errorMsg)
      return null
    }
  } catch (error) {
    // console.error('❌ Error fetching CCTV image:', {
    //   error,
    //   errorMessage: error.message,
    //   ipAddress: props.ipAddress,
    //   fullUrl: props.fullUrl ? props.fullUrl.replace(/:[^:]+@/, ':***@') : undefined,
    //   label: props.label
    // })
    
    handleCameraError(error.message)
    return null
  }
}

const handleCameraError = (errorMsg) => {
  // Handle specific RTSP errors
  if (errorMsg.includes('5XX Server Error') || errorMsg.includes('Server returned 5XX')) {
    message.value = 'Camera server error - check IP and credentials'
  } else if (errorMsg.includes('Connection refused') || errorMsg.includes('Network unreachable')) {
    message.value = 'Camera connection refused - check network'
  } else if (errorMsg.includes('Authentication failed') || errorMsg.includes('401')) {
    message.value = 'Camera auth failed - check username/password'
  } else if (errorMsg.includes('timeout')) {
    message.value = 'Camera connection timeout'
  } else {
    message.value = `CCTV Error: ${errorMsg}`
  }
  
  cameraStatus.value = false
  
  if (retryCount.value < maxRetries) {
    retryCount.value++
    message.value += ` (Retry ${retryCount.value}/${maxRetries})`
    setTimeout(fetchCameraImage, 2000)
  } else {
    message.value = 'Camera connection failed - check settings'
    emit('error', new Error(errorMsg))
  }
}

const handleImageError = (e) => {
  console.error('Image load error:', e)
  message.value = 'Invalid image data'
  cameraStatus.value = false
}

// Initialize camera on mount
onMounted(async () => {
  if (props.cameraType === 'cctv') {
    const displayUrl = props.fullUrl ? 
      props.fullUrl.replace(/:[^:]+@/, ':***@') : 
      props.ipAddress
    console.log(`📸 Starting CCTV camera: ${props.label} (${displayUrl})`)
    
    // Initial fetch
    await fetchCameraImage()
    
    // Start interval if enabled
    if (props.isInterval) {
      intervalId.value = setInterval(() => {
        // console.log(`📷 Interval capture for ${props.label}`)
        fetchCameraImage()
      }, props.intervalTime)
    }
  }
})

// Cleanup on unmount
onUnmounted(() => {
  // console.log(`🧹 Cleaning up Camera component: ${props.label}`)
  
  if (intervalId.value) {
    clearInterval(intervalId.value)
    intervalId.value = null
  }
})

// Expose methods for parent component
defineExpose({ 
  getImage, 
  fetchCameraImage,
  refresh: fetchCameraImage 
})
</script>

<style scoped>
.camera-container {
  position: relative;
  width: 100%;
  height: 40vh;
  background-color: #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.2);
}

.camera-view {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.camera-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.connection-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 20px;
  height: 20px;
  background-color: #ccc;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.indicator-dot {
  width: 12px;
  height: 12px;
  background-color: red;
  border-radius: 50%;
  transition: background-color 0.3s ease;
}

.connection-indicator.connected .indicator-dot {
  background-color: limegreen;
}

.full-height {
  height: 100%;
  width: 100%;
}

.inset-shadow {
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
}
</style>
