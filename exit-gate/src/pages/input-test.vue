<template>
  <q-page class="q-pa-md">
    <div class="row justify-center">
      <div class="col-12 col-md-6">
        <q-card class="q-mb-lg">
          <q-card-section>
            <div class="text-h6 q-mb-md">Input Field Test</div>
            
            <!-- Scanner Status -->
            <div class="q-mb-md">
              <q-chip 
                :color="scannerStatus.enabled ? 'green' : 'red'"
                text-color="white"
                :icon="scannerStatus.enabled ? 'qr_code_scanner' : 'block'"
              >
                Scanner {{ scannerStatus.enabled ? 'Enabled' : 'Disabled' }}
              </q-chip>
              
              <q-chip 
                :color="scannerStatus.manuallyDisabled ? 'orange' : 'blue'"
                text-color="white"
                icon="info"
                class="q-ml-sm"
              >
                {{ scannerStatus.manuallyDisabled ? 'Temporarily Disabled' : 'Active' }}
              </q-chip>
            </div>

            <!-- Test Input Fields -->
            <div class="q-gutter-md">
              <q-input
                v-model="testInput1"
                label="Test Input 1 (Regular)"
                outlined
                hint="Try typing here - scanner should not interfere"
              />

              <q-input
                v-model="testInput2"
                label="Test Input 2 (With Focus/Blur)"
                outlined
                hint="This input has focus/blur events"
                @focus="onInputFocus"
                @blur="onInputBlur"
              />

              <q-input
                v-model="testInput3"
                type="number"
                label="Test Input 3 (Number)"
                outlined
                hint="Number input test"
              />

              <q-input
                v-model="testInput4"
                type="password"
                label="Test Input 4 (Password)"
                outlined
                hint="Password input test"
              />

              <q-select
                v-model="testSelect"
                :options="selectOptions"
                label="Test Select"
                outlined
                emit-value
                map-options
                hint="Select field test"
              />
            </div>

            <!-- Scanner Control -->
            <div class="q-mt-lg">
              <q-btn
                :color="scannerStatus.enabled ? 'red' : 'green'"
                :icon="scannerStatus.enabled ? 'stop' : 'play_arrow'"
                :label="scannerStatus.enabled ? 'Disable Scanner' : 'Enable Scanner'"
                @click="toggleScanner"
                class="q-mr-md"
              />

              <q-btn
                color="purple"
                icon="qr_code_scanner"
                label="Test Scan"
                @click="testScan"
              />
            </div>

            <!-- Last Scan Result -->
            <div v-if="lastScan" class="q-mt-lg">
              <q-separator class="q-mb-md" />
              <div class="text-subtitle2">Last Scan Result:</div>
              <div class="text-body2">
                <strong>Code:</strong> {{ lastScan.code }}<br>
                <strong>Valid:</strong> {{ lastScan.isValid ? 'Yes' : 'No' }}<br>
                <strong>Time:</strong> {{ lastScan.timestamp.toLocaleString() }}
              </div>
            </div>

            <!-- Debug Info -->
            <div class="q-mt-lg">
              <q-separator class="q-mb-md" />
              <div class="text-subtitle2">Debug Info:</div>
              <div class="text-body2">
                <strong>Current Path:</strong> {{ currentPath }}<br>
                <strong>Input Values:</strong><br>
                - Input 1: "{{ testInput1 }}"<br>
                - Input 2: "{{ testInput2 }}"<br>
                - Input 3: "{{ testInput3 }}"<br>
                - Input 4: "{{ testInput4 }}"<br>
                - Select: "{{ testSelect }}"
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Navigation -->
        <div class="text-center">
          <q-btn
            color="primary"
            icon="arrow_back"
            label="Back to Main"
            @click="$router.push('/')"
          />
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'
import { barcodeScanner, type BarcodeResult } from '../services/barcode-scanner'

const $q = useQuasar()

// Reactive state
const testInput1 = ref('')
const testInput2 = ref('')
const testInput3 = ref('')
const testInput4 = ref('')
const testSelect = ref('')

const scannerStatus = ref({
  enabled: true,
  manuallyDisabled: false
})

const lastScan = ref<BarcodeResult | null>(null)
const currentPath = ref('')

const selectOptions = [
  { label: 'Option 1', value: 'opt1' },
  { label: 'Option 2', value: 'opt2' },
  { label: 'Option 3', value: 'opt3' }
]

// Initialize component
onMounted(() => {
  updateScannerStatus()
  updateCurrentPath()
  
  // Add barcode listener
  barcodeScanner.addListener(onBarcodeScanned)
  
  // Update path on hash change
  window.addEventListener('hashchange', updateCurrentPath)
})

onUnmounted(() => {
  // Remove barcode listener
  barcodeScanner.removeListener(onBarcodeScanned)
  window.removeEventListener('hashchange', updateCurrentPath)
})

// Update scanner status
function updateScannerStatus() {
  scannerStatus.value = {
    enabled: barcodeScanner.isEnabled(),
    manuallyDisabled: false // We don't have access to private property, but that's OK for testing
  }
}

// Update current path
function updateCurrentPath() {
  currentPath.value = window.location.hash || window.location.pathname
}

// Handle barcode scan
function onBarcodeScanned(result: BarcodeResult) {
  lastScan.value = result
  
  $q.notify({
    type: result.isValid ? 'positive' : 'warning',
    message: `Scanned: ${result.code}`,
    icon: 'qr_code_scanner'
  })
}

// Toggle scanner
function toggleScanner() {
  if (scannerStatus.value.enabled) {
    barcodeScanner.disable()
    $q.notify({
      type: 'info',
      message: 'Scanner disabled',
      icon: 'stop'
    })
  } else {
    barcodeScanner.enable()
    $q.notify({
      type: 'positive',
      message: 'Scanner enabled',
      icon: 'play_arrow'
    })
  }
  
  updateScannerStatus()
}

// Test scan
function testScan() {
  const testCode = 'TEST' + Math.floor(Math.random() * 1000)
  barcodeScanner.simulateScan(testCode)
}

// Input focus/blur handlers
function onInputFocus() {
  console.log('Input focused - scanner should be disabled')
  $q.notify({
    type: 'info',
    message: 'Input focused',
    icon: 'edit'
  })
}

function onInputBlur() {
  console.log('Input blurred - scanner should be enabled')
  $q.notify({
    type: 'info',
    message: 'Input blurred',
    icon: 'edit_off'
  })
}
</script>

<style scoped>
.q-page {
  background-color: #f5f5f5;
}
</style>
