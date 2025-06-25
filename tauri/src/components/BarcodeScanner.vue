<template>
  <q-card class="barcode-scanner-card">
    <q-card-section>
      <div class="row items-center q-mb-md">
        <q-icon name="qr_code_scanner" size="md" class="q-mr-sm" />
        <div class="text-h6">{{ title || 'Scan Barcode' }}</div>
        <q-space />
        <q-btn
          v-if="showToggle"
          :icon="isScanning ? 'stop' : 'play_arrow'"
          :color="isScanning ? 'negative' : 'positive'"
          :label="isScanning ? 'Stop' : 'Start'"
          size="sm"
          @click="toggleScanning"
        />
      </div>

      <!-- Camera Preview (if using camera) -->
      <div v-if="showCamera && isScanning" class="camera-container q-mb-md">
        <video ref="videoRef" autoplay muted class="camera-video"></video>
        <div class="scan-overlay">
          <div class="scan-line"></div>
          <div class="scan-corners">
            <div class="corner corner-tl"></div>
            <div class="corner corner-tr"></div>
            <div class="corner corner-bl"></div>
            <div class="corner corner-br"></div>
          </div>
        </div>
        <canvas ref="canvasRef" style="display: none;"></canvas>
      </div>

      <!-- Manual Input -->
      <q-input
        ref="inputRef"
        v-model="barcodeValue"
        :label="inputLabel || 'Scan atau ketik barcode'"
        outlined
        :autofocus="!showCamera"
        @update:model-value="onBarcodeInput"
        @keydown.enter="onEnterPressed"
        :readonly="isScanning && showCamera"
        class="barcode-input"
      >
        <template v-slot:prepend>
          <q-icon :name="isScanning ? 'qr_code_scanner' : 'edit'" />
        </template>
        <template v-slot:append>
          <q-btn
            round
            dense
            flat
            icon="search"
            @click="onSearchClicked"
            :loading="processing"
          />
          <q-btn
            v-if="barcodeValue"
            round
            dense
            flat
            icon="clear"
            @click="clearBarcode"
          />
        </template>
      </q-input>

      <!-- Status Messages -->
      <div class="q-mt-sm">
        <div v-if="isScanning" class="text-caption text-positive">
          <q-icon name="camera" class="q-mr-xs" />
          {{ scanningMessage || 'Scanning... Arahkan kamera ke barcode' }}
        </div>
        <div v-else-if="lastScannedTime" class="text-caption text-grey-6">
          <q-icon name="schedule" class="q-mr-xs" />
          Terakhir scan: {{ formatTime(lastScannedTime) }}
        </div>
        <div v-else class="text-caption text-grey-6">
          {{ helpText || 'Arahkan scanner ke barcode atau ketik manual' }}
        </div>
      </div>

      <!-- Recent Scans (Optional) -->
      <div v-if="showHistory && recentScans.length > 0" class="q-mt-md">
        <div class="text-subtitle2 q-mb-sm">Scan Terakhir:</div>
        <q-list dense>
          <q-item
            v-for="(scan, index) in recentScans.slice(0, 3)"
            :key="index"
            clickable
            @click="selectRecentScan(scan)"
            class="recent-scan-item"
          >
            <q-item-section>
              <q-item-label>{{ scan.code }}</q-item-label>
              <q-item-label caption>{{ formatTime(scan.timestamp) }}</q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-icon name="history" />
            </q-item-section>
          </q-item>
        </q-list>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { formatTime } from 'src/utils/format-utils';

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  title: {
    type: String,
    default: ''
  },
  inputLabel: {
    type: String,
    default: ''
  },
  helpText: {
    type: String,
    default: ''
  },
  scanningMessage: {
    type: String,
    default: ''
  },
  showCamera: {
    type: Boolean,
    default: false
  },
  showToggle: {
    type: Boolean,
    default: false
  },
  showHistory: {
    type: Boolean,
    default: true
  },
  autoClear: {
    type: Boolean,
    default: true
  },
  minLength: {
    type: Number,
    default: 5
  },
  processing: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue', 'scanned', 'search', 'cleared']);

// Reactive data
const barcodeValue = ref('');
const isScanning = ref(false);
const lastScannedTime = ref(null);
const recentScans = ref([]);

// Refs
const inputRef = ref(null);
const videoRef = ref(null);
const canvasRef = ref(null);

// Camera variables
let stream = null;
let scanInterval = null;

// Computed
const barcodeModel = computed({
  get: () => props.modelValue || barcodeValue.value,
  set: (val) => {
    barcodeValue.value = val;
    emit('update:modelValue', val);
  }
});

// Methods
const onBarcodeInput = (value) => {
  const cleanValue = value.toUpperCase().trim();
  barcodeModel.value = cleanValue;
  
  // Auto-submit if long enough and not camera scanning
  if (cleanValue.length >= props.minLength && !isScanning.value) {
    onSearchClicked();
  }
};

const onEnterPressed = () => {
  if (barcodeModel.value.trim()) {
    onSearchClicked();
  }
};

const onSearchClicked = () => {
  const code = barcodeModel.value.trim();
  if (code.length < props.minLength) {
    return;
  }

  // Add to recent scans
  addToRecentScans(code);
  
  // Emit scanned event
  emit('scanned', code);
  emit('search', code);
  
  // Update last scanned time
  lastScannedTime.value = new Date();
  
  // Auto clear if enabled
  if (props.autoClear) {
    setTimeout(() => {
      clearBarcode();
    }, 1000);
  }
};

const clearBarcode = () => {
  barcodeModel.value = '';
  emit('cleared');
  
  // Focus back to input
  setTimeout(() => {
    inputRef.value?.focus();
  }, 100);
};

const addToRecentScans = (code) => {
  // Remove if already exists
  recentScans.value = recentScans.value.filter(scan => scan.code !== code);
  
  // Add to beginning
  recentScans.value.unshift({
    code,
    timestamp: new Date()
  });
  
  // Keep only last 10
  if (recentScans.value.length > 10) {
    recentScans.value = recentScans.value.slice(0, 10);
  }
  
  // Save to localStorage
  localStorage.setItem('recentBarcodeScans', JSON.stringify(recentScans.value));
};

const selectRecentScan = (scan) => {
  barcodeModel.value = scan.code;
  onSearchClicked();
};

const loadRecentScans = () => {
  try {
    const saved = localStorage.getItem('recentBarcodeScans');
    if (saved) {
      recentScans.value = JSON.parse(saved).map(scan => ({
        ...scan,
        timestamp: new Date(scan.timestamp)
      }));
    }
  } catch (error) {
    console.error('Error loading recent scans:', error);
  }
};

// Camera functions
const toggleScanning = () => {
  if (isScanning.value) {
    stopScanning();
  } else {
    startScanning();
  }
};

const startScanning = async () => {
  if (!props.showCamera) return;
  
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' } // Use back camera if available
    });
    
    if (videoRef.value) {
      videoRef.value.srcObject = stream;
      isScanning.value = true;
      
      // Start scanning interval
      scanInterval = setInterval(scanBarcode, 500);
    }
  } catch (error) {
    console.error('Error accessing camera:', error);
    // Fallback to manual input
    isScanning.value = false;
  }
};

const stopScanning = () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
  
  if (scanInterval) {
    clearInterval(scanInterval);
    scanInterval = null;
  }
  
  isScanning.value = false;
};

const scanBarcode = () => {
  if (!videoRef.value || !canvasRef.value) return;
  
  const video = videoRef.value;
  const canvas = canvasRef.value;
  const ctx = canvas.getContext('2d');
  
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  
  // Here you would integrate with a barcode detection library
  // For now, this is a placeholder
  // Example: Use ZXing or QuaggaJS for actual barcode detection
};

// Lifecycle
onMounted(() => {
  loadRecentScans();
  
  // Focus on input after mount
  setTimeout(() => {
    if (!props.showCamera) {
      inputRef.value?.focus();
    }
  }, 100);
});

onUnmounted(() => {
  stopScanning();
});

// Watch for external value changes
watch(() => props.modelValue, (newValue) => {
  if (newValue !== barcodeValue.value) {
    barcodeValue.value = newValue || '';
  }
});
</script>

<style scoped>
.barcode-scanner-card {
  border-radius: 8px;
}

.camera-container {
  position: relative;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.camera-video {
  width: 100%;
  border-radius: 8px;
  background: #000;
}

.scan-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scan-line {
  position: absolute;
  width: 80%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #ff0000, transparent);
  animation: scan 2s linear infinite;
}

@keyframes scan {
  0% { transform: translateY(-100px); opacity: 0; }
  50% { opacity: 1; }
  100% { transform: translateY(100px); opacity: 0; }
}

.scan-corners {
  position: absolute;
  width: 200px;
  height: 200px;
  border: 2px solid #ff0000;
  border-radius: 8px;
  background: transparent;
}

.corner {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 3px solid #ff0000;
}

.corner-tl {
  top: -2px;
  left: -2px;
  border-right: none;
  border-bottom: none;
}

.corner-tr {
  top: -2px;
  right: -2px;
  border-left: none;
  border-bottom: none;
}

.corner-bl {
  bottom: -2px;
  left: -2px;
  border-right: none;
  border-top: none;
}

.corner-br {
  bottom: -2px;
  right: -2px;
  border-left: none;
  border-top: none;
}

.barcode-input {
  font-family: 'Courier New', monospace;
  font-weight: bold;
}

.recent-scan-item {
  border-radius: 4px;
  margin-bottom: 4px;
}

.recent-scan-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}
</style>
