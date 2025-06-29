<template>
  <q-page class="full-width flex column items-center justify-center bg-grey-1 q-pa-md">
    <!-- Header -->
    <div class="text-h3 text-weight-bold text-primary q-mb-lg">
      Exit Gate System
    </div>

    <!-- CCTV Camera Monitors -->
    <div class="full-width flex-center row q-gutter-md q-mb-lg" style="min-width: 800px">
      <div class="col-5">
        <q-card class="shadow-4">
          <q-card-section class="q-pa-sm">
            <Camera
              ref="plateExitCameraRef"
              :camera-type="'cctv'"
              :username="cameraSettings.PLATE_CAM_USERNAME || 'admin'"
              :password="cameraSettings.PLATE_CAM_PASSWORD || 'admin123'"
              :ip-address="cameraSettings.PLATE_CAM_IP || '192.168.1.100'"
              :rtsp-stream-path="cameraSettings.PLATE_CAM_SNAPSHOT_PATH || 'Streaming/Channels/1/picture'"
              :full-url="cameraSettings.PLATE_CAM_FULL_URL || ''"
              :is-interval="true"
              :interval-time="3000"
              label="Exit Plate Camera"
              camera-location="plate_exit"
              @captured="onPlateCaptured"
              @error="onCameraError"
            />
          </q-card-section>
        </q-card>
      </div>
      <div class="col-5">
        <q-card class="shadow-4">
          <q-card-section class="q-pa-sm">
            <Camera
              ref="driverExitCameraRef"
              :camera-type="'cctv'"
              :username="cameraSettings.DRIVER_CAM_USERNAME || 'admin'"
              :password="cameraSettings.DRIVER_CAM_PASSWORD || 'admin123'"
              :ip-address="cameraSettings.DRIVER_CAM_IP || '192.168.1.101'"
              :rtsp-stream-path="cameraSettings.DRIVER_CAM_SNAPSHOT_PATH || 'Streaming/Channels/1/picture'"
              :full-url="cameraSettings.DRIVER_CAM_FULL_URL || ''"
              :is-interval="true"
              :interval-time="3000"
              label="Exit Driver Camera"
              camera-location="driver_exit"
              @captured="onDriverCaptured"
              @error="onCameraError"
            />
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Status Display -->
    <q-card class="q-mb-lg shadow-4" style="min-width: 400px">
      <q-card-section class="text-center">
        <div class="text-h5 q-mb-md">System Status</div>
        
        <!-- Gate Status -->
        <div class="q-mb-md">
          <div class="text-subtitle2 q-mb-xs">Gate</div>
          <q-chip 
            :color="getStatusColor(gateStatus)" 
            text-color="white" 
            size="lg"
            :icon="getStatusIcon(gateStatus)"
          >
            {{ gateStatus }}
          </q-chip>
        </div>
        
        <!-- Sync Status -->
        <div class="q-mb-md">
          <div class="text-subtitle2 q-mb-xs">Database Sync</div>
          <q-chip 
            :color="syncStatus.connected ? 'green' : 'grey'" 
            text-color="white" 
            size="md"
            :icon="syncStatus.connected ? 'cloud_done' : 'cloud_off'"
          >
            {{ syncStatus.connected ? 'Online' : 'Offline' }}
          </q-chip>
          <q-chip 
            v-if="syncStatus.sync_active"
            color="blue"
            text-color="white"
            size="sm"
            icon="sync"
            class="q-ml-sm"
          >
            Syncing
          </q-chip>
        </div>
      </q-card-section>
    </q-card>

    <!-- Barcode Scanner Display -->
    <q-card class="q-mb-lg shadow-4" style="min-width: 400px">
      <q-card-section>
        <div class="text-h6 q-mb-md">
          <q-icon name="qr_code_scanner" class="q-mr-sm" />
          Barcode Scanner
        </div>
        <div class="text-center">
          <div v-if="processing" class="q-mb-md">
            <q-spinner-dots size="lg" color="primary" />
            <div class="text-body1 q-mt-sm">Processing transaction...</div>
          </div>
          <div v-else-if="!lastScan" class="text-grey-6">
            Waiting for barcode scan...
          </div>
          <div v-else>
            <div class="text-subtitle1 q-mb-xs">Last Scan:</div>
            <div class="text-h6 text-weight-bold">{{ lastScan.code }}</div>
            <div class="text-caption text-grey-6">
              {{ formatTime(lastScan.timestamp) }}
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Transaction Display -->
    <q-card v-if="currentTransaction" class="q-mb-lg shadow-4" style="min-width: 400px">
      <q-card-section>
        <div class="text-h6 q-mb-md text-green-8">
          <q-icon name="check_circle" class="q-mr-sm" />
          Exit Processed Successfully
        </div>
        <div class="row q-gutter-md">
          <div class="col">
            <div class="text-caption text-grey-6">License Plate</div>
            <div class="text-subtitle1">{{ currentTransaction.no_pol }}</div>
          </div>
          <div class="col">
            <div class="text-caption text-grey-6">Entry Time</div>
            <div class="text-subtitle1">{{ formatDateTime(currentTransaction.waktu_masuk) }}</div>
          </div>
        </div>
        <div class="row q-gutter-md q-mt-sm">
          <div class="col">
            <div class="text-caption text-grey-6">Vehicle Type</div>
            <div class="text-subtitle1">{{ getVehicleTypeName(currentTransaction.id_kendaraan) }}</div>
          </div>
          <div class="col">
            <div class="text-caption text-grey-6">Exit Fee</div>
            <div class="text-subtitle1 text-green-8">{{ formatCurrency(currentTransaction.bayar_keluar || 0) }}</div>
          </div>
        </div>
        <div class="q-mt-md text-center">
          <q-chip color="green" text-color="white" icon="directions_car" size="lg">
            Gate Opening...
          </q-chip>
        </div>
      </q-card-section>
    </q-card>

    <!-- Error Display -->
    <q-card v-if="errorMessage" class="q-mb-lg shadow-4 bg-red-1" style="min-width: 400px">
      <q-card-section>
        <div class="text-h6 text-red-8 q-mb-md">
          <q-icon name="error" class="q-mr-sm" />
          Error
        </div>
        <div class="text-body1">{{ errorMessage }}</div>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn color="red" flat label="Dismiss" @click="errorMessage = ''" />
      </q-card-actions>
    </q-card>

    <!-- Today's Statistics -->
    <q-card class="shadow-4" style="min-width: 400px">
      <q-card-section>
        <div class="text-h6 q-mb-md">
          <q-icon name="analytics" class="q-mr-sm" />
          Today's Statistics
        </div>
        <div class="row q-gutter-md text-center">
          <div class="col">
            <div class="text-h4 text-primary">{{ todayStats.totalExits }}</div>
            <div class="text-caption text-grey-6">Total Exits</div>
          </div>
          <div class="col">
            <div class="text-h4 text-green-8">{{ formatCurrency(todayStats.totalRevenue) }}</div>
            <div class="text-caption text-grey-6">Revenue</div>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Manual Controls (for testing) -->
    <q-card v-if="showManualControls" class="q-mt-lg shadow-4" style="min-width: 400px">
      <q-card-section>
        <div class="text-h6 q-mb-md">Manual Controls</div>
        
        <!-- Test Transaction Check -->
        <div class="q-mb-lg">
          <div class="text-subtitle2 q-mb-sm">Test Transaction Check</div>
          <div class="row q-gutter-sm items-center">
            <div class="col">
              <q-input
                v-model="testBarcodeInput"
                outlined
                dense
                placeholder="Enter barcode or license plate"
                label="Test Barcode/License Plate"
                :disable="processing"
              >
                <template v-slot:append>
                  <q-icon name="qr_code" />
                </template>
              </q-input>
            </div>
            <q-btn 
              color="teal" 
              icon="search"
              label="Check"
              @click="testCheckTransaction"
              :disable="!testBarcodeInput || processing"
              :loading="processing"
            />
          </div>
        </div>
        
        <!-- Gate Controls -->
        <div class="text-subtitle2 q-mb-sm">Gate Controls</div>
        <div class="row q-gutter-md">
          <q-btn 
            color="primary" 
            icon="input"
            label="Open Gate"
            @click="manualOpenGate"
            :disable="gateStatus === 'OPEN'"
          />
          <q-btn 
            color="secondary" 
            icon="output"
            label="Close Gate"
            @click="manualCloseGate"
            :disable="gateStatus === 'CLOSED'"
          />
          <q-btn 
            color="orange" 
            icon="science"
            label="Test Gate"
            @click="testGate"
          />
          <q-btn
            color="purple"
            icon="volume_up"
            label="Test Sound"
            @click="testGateSound"
          />
        </div>
      </q-card-section>
    </q-card>

    <!-- Settings Button -->
    <q-btn 
      class="fixed-bottom-right q-ma-lg"
      fab 
      color="primary" 
      icon="settings"
      @click="$router.push('/settings')"
    />
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'
import { databaseService, type ParkingTransaction, type VehicleType, type SyncStatus } from '../services/database'
import { barcodeScanner, type BarcodeResult } from '../services/barcode-scanner'
import { gateService, GateStatus } from '../services/gate-service'
import { audioService } from '../services/audio-service'
import { cameraService, type CameraCapture } from '../services/camera-service'
import Camera from '../components/Camera.vue'

const $q = useQuasar()

// Reactive state
const gateStatus = ref<GateStatus>(GateStatus.CLOSED)
const lastScan = ref<BarcodeResult | null>(null)
const currentTransaction = ref<ParkingTransaction | null>(null)
const errorMessage = ref('')
const processing = ref(false)
const vehicleTypes = ref<VehicleType[]>([])
const syncStatus = ref<SyncStatus>({
  connected: false,
  last_sync: null,
  sync_active: false,
  error_message: null,
  docs_synced: 0,
  pending_changes: 0
})
const todayStats = ref({
  totalExits: 0,
  totalRevenue: 0
})

// Camera settings and references
const cameraSettings = ref({
  PLATE_CAM_USERNAME: 'admin',
  PLATE_CAM_PASSWORD: 'admin123',
  PLATE_CAM_IP: '192.168.1.100',
  PLATE_CAM_SNAPSHOT_PATH: 'Streaming/Channels/1/picture', // Changed to snapshot path
  PLATE_CAM_FULL_URL: '', // Full URL for plate camera
  DRIVER_CAM_USERNAME: 'admin',
  DRIVER_CAM_PASSWORD: 'admin123',
  DRIVER_CAM_IP: '192.168.1.101',
  DRIVER_CAM_SNAPSHOT_PATH: 'Streaming/Channels/1/picture', // Changed to snapshot path
  DRIVER_CAM_FULL_URL: '' // Full URL for driver camera
})

const plateExitCameraRef = ref(null)
const driverExitCameraRef = ref(null)
const capturedExitImages = ref({
  plateImage: null,
  driverImage: null
})

// Show manual controls in development
const showManualControls = ref(true)

// Test input for checking transactions
const testBarcodeInput = ref('')

// Load camera settings from database
async function loadCameraSettings() {
  try {
    const settings = await databaseService.getSettings()
    if (settings) {
      cameraSettings.value = {
        PLATE_CAM_USERNAME: settings.plate_camera_username || 'admin',
        PLATE_CAM_PASSWORD: settings.plate_camera_password || 'admin123',
        PLATE_CAM_IP: settings.plate_camera_ip || '192.168.1.100',
        PLATE_CAM_SNAPSHOT_PATH: settings.plate_camera_snapshot_path || 'Streaming/Channels/1/picture',
        PLATE_CAM_FULL_URL: settings.plate_camera_full_url || '',
        DRIVER_CAM_USERNAME: settings.driver_camera_username || 'admin',
        DRIVER_CAM_PASSWORD: settings.driver_camera_password || 'admin123',
        DRIVER_CAM_IP: settings.driver_camera_ip || '192.168.1.101',
        DRIVER_CAM_SNAPSHOT_PATH: settings.driver_camera_snapshot_path || 'Streaming/Channels/1/picture',
        DRIVER_CAM_FULL_URL: settings.driver_camera_full_url || ''
      }
      console.log('📸 Camera settings loaded:', cameraSettings.value)
    }
  } catch (error) {
    console.error('Error loading camera settings:', error)
    // Use defaults if loading fails
  }
}

// Auto-clear transaction timer
let clearTransactionTimer: number | null = null

// Initialize services
onMounted(async () => {
  try {
    // Initialize database
    await databaseService.initialize()
    
    // Load camera settings from database
    await loadCameraSettings()
    
    // Initialize camera
    await cameraService.initializeWebcam()
    
    // Load vehicle types
    vehicleTypes.value = await databaseService.getVehicleTypes()
    
    // Load today's statistics
    await loadTodayStats()
    
    // Setup barcode scanner
    barcodeScanner.addListener(handleBarcodeScanned)
    
    // Setup gate status listener
    gateService.addStatusListener(handleGateStatusChange)
    gateStatus.value = gateService.getStatus()
    
    // Setup sync status listener
    databaseService.addSyncStatusListener(handleSyncStatusChange)
    syncStatus.value = databaseService.getSyncStatus()
    
    console.log('Exit gate system initialized')
  } catch (error) {
    console.error('Failed to initialize exit gate system:', error)
    showError('Failed to initialize system')
  }
})

// Cleanup on unmount
onUnmounted(() => {
  barcodeScanner.destroy()
  gateService.destroy()
  cameraService.destroy()
  databaseService.removeSyncStatusListener(handleSyncStatusChange)
  
  // Clear transaction timer
  if (clearTransactionTimer) {
    clearTimeout(clearTransactionTimer)
  }
})

// Handle barcode scan
async function handleBarcodeScanned(result: BarcodeResult) {
  lastScan.value = result
  
  // Play scan sound
  try {
    await audioService.playScanSound()
  } catch (error) {
    console.warn('Failed to play scan sound:', error)
  }
  
  if (!result.isValid) {
    showError('Invalid barcode format')
    // Play error sound for invalid barcode
    try {
      await audioService.playErrorSound()
    } catch (error) {
      console.warn('Failed to play error sound:', error)
    }
    return
  }
  
  console.log('Barcode scanned:', result.code)
  
  try {
    // Find transaction by barcode
    const transaction = await databaseService.findTransactionByBarcode(result.code)
    
    if (transaction) {
      currentTransaction.value = transaction
      console.log('Transaction found:', transaction)
      
      // Automatically process exit for found transaction
      await processExit()
    } else {
      showError(`No active transaction found for barcode: ${result.code}`)
      // Play error sound for transaction not found
      try {
        await audioService.playErrorSound()
      } catch (error) {
        console.warn('Failed to play error sound:', error)
      }
    }
  } catch (error) {
    console.error('Error finding transaction:', error)
    showError('Error looking up transaction')
    // Play error sound for lookup error
    try {
      await audioService.playErrorSound()
    } catch (error) {
      console.warn('Failed to play error sound:', error)
    }
  }
}

// Handle gate status changes
function handleGateStatusChange(status: GateStatus) {
  gateStatus.value = status
}

// Handle sync status changes
function handleSyncStatusChange(status: SyncStatus) {
  syncStatus.value = status
}

// Process vehicle exit - updated to use new enhanced method
async function processExit() {
  if (!currentTransaction.value) {
    showError('No transaction selected')
    return
  }
  
  processing.value = true
  
  try {
    // Use the new enhanced exit processing method
    const result = await databaseService.processVehicleExit(
      currentTransaction.value.no_pol,
      'SYSTEM', // Operator ID
      'EXIT_GATE_01' // Gate ID
    )
    
    if (!result.success) {
      throw new Error(result.message || 'Failed to process exit')
    }
    
    // Update current transaction with the processed result
    currentTransaction.value = result.transaction || currentTransaction.value
    
    // Capture images from CCTV cameras
    try {
      await captureExitImages()
      
      // Convert captured images to base64 and save to transaction
      let exitImageBase64 = null
      
      if (capturedExitImages.value.plateImage) {
        // If plate image is a blob, convert to base64
        if (capturedExitImages.value.plateImage && typeof capturedExitImages.value.plateImage === 'object' && 'size' in capturedExitImages.value.plateImage) {
          const reader = new FileReader()
          exitImageBase64 = await new Promise<string>((resolve) => {
            reader.onload = () => resolve(reader.result as string)
            reader.readAsDataURL(capturedExitImages.value.plateImage as unknown as Blob)
          })
        } else if (typeof capturedExitImages.value.plateImage === 'string') {
          exitImageBase64 = capturedExitImages.value.plateImage
        }
      }
      
      // Update transaction with exit image
      if (exitImageBase64) {
        await databaseService.exitTransaction(currentTransaction.value._id, {
          waktu_keluar: currentTransaction.value.waktu_keluar || new Date().toISOString(),
          bayar_keluar: result.fee,
          exit_pic: exitImageBase64 // Save exit image as base64 string
        })
        console.log('✅ Exit image saved to transaction')
      } else {
        // Update transaction without image
        await databaseService.exitTransaction(currentTransaction.value._id, {
          waktu_keluar: currentTransaction.value.waktu_keluar || new Date().toISOString(),
          bayar_keluar: result.fee
        })
        console.log('⚠️ Transaction updated without exit image')
      }
    } catch (cameraError) {
      console.warn('Camera capture failed:', cameraError)
      // Continue with exit process even if camera fails - update transaction without image
      await databaseService.exitTransaction(currentTransaction.value._id, {
        waktu_keluar: currentTransaction.value.waktu_keluar || new Date().toISOString(),
        bayar_keluar: result.fee
      })
    }
    
    // Open the gate
    const gateOpened = await gateService.openGate(10) // Auto-close after 10 seconds
    
    if (gateOpened) {
      $q.notify({
        type: 'positive',
        message: `Exit processed successfully for ${currentTransaction.value.no_pol}. Fee: ${formatCurrency(result.fee || 0)}`,
        icon: 'check_circle'
      })
      
      // Play exit success sound
      try {
        await audioService.playExitSuccessSound()
      } catch (error) {
        console.warn('Failed to play success sound:', error)
      }
      
      // Clear current transaction after displaying success
      setTimeout(() => {
        currentTransaction.value = null
      }, 3000)
      
      // Auto-clear transaction display after 5 seconds
      if (clearTransactionTimer) {
        clearTimeout(clearTransactionTimer)
      }
      clearTransactionTimer = window.setTimeout(() => {
        currentTransaction.value = null
        lastScan.value = null
      }, 5000)
      
      // Reload statistics
      await loadTodayStats()
    } else {
      throw new Error('Failed to open gate')
    }
  } catch (error) {
    console.error('Error processing exit:', error)
    showError('Failed to process exit')
  } finally {
    processing.value = false
  }
}

// Cancel current transaction
function cancelTransaction() {
  currentTransaction.value = null
  errorMessage.value = ''
  
  // Clear timer if exists
  if (clearTransactionTimer) {
    clearTimeout(clearTransactionTimer)
    clearTransactionTimer = null
  }
}

// Calculate exit fee (basic implementation)
function calculateExitFee(transaction: ParkingTransaction): number {
  const vehicleType = vehicleTypes.value.find(vt => vt.id_kendaraan === transaction.id_kendaraan)
  return vehicleType?.tarif || 0
}

// Load today's statistics
async function loadTodayStats() {
  try {
    const stats = await databaseService.getTodayExitStats()
    todayStats.value = stats
  } catch (error) {
    console.error('Error loading today stats:', error)
  }
}

// Manual gate controls
async function manualOpenGate() {
  await gateService.openGate(10)
}

async function manualCloseGate() {
  await gateService.closeGate()
}

async function testGate() {
  await gateService.testGate(3)
}

async function testGateSound() {
  try {
    await audioService.playGateOpenSound()
    setTimeout(async () => {
      await audioService.playGateCloseSound()
    }, 1000)
  } catch (error) {
    console.error('Failed to test gate sounds:', error)
    showError('Failed to play gate sounds')
  }
}

// Test transaction check function
async function testCheckTransaction() {
  if (!testBarcodeInput.value.trim()) {
    showError('Please enter a barcode or license plate')
    return
  }
  
  processing.value = true
  
  try {
    // Clear any previous transaction
    currentTransaction.value = null
    errorMessage.value = ''
    
    const inputValue = testBarcodeInput.value.trim()
    console.log('Testing transaction check for:', inputValue)
    
    // Try to find transaction by barcode first
    let transaction = await databaseService.findTransactionByBarcode(inputValue)
    
    // If not found by barcode, try by license plate
    if (!transaction) {
      transaction = await databaseService.findTransactionByPlate(inputValue)
    }
    
    if (transaction) {
      currentTransaction.value = transaction
      console.log('✅ Transaction found:', transaction)
      
      // Show transaction details
      $q.notify({
        type: 'positive',
        message: `Transaction found for ${transaction.no_pol}`,
        icon: 'check_circle',
        timeout: 3000
      })
      
      // Play scan sound
      try {
        await audioService.playScanSound()
      } catch (error) {
        console.warn('Failed to play scan sound:', error)
      }
      
      // Ask if user wants to process exit
      $q.dialog({
        title: 'Transaction Found',
        message: `Do you want to process exit for vehicle ${transaction.no_pol}?`,
        cancel: true,
        persistent: true
      }).onOk(async () => {
        await processExit()
      })
      
    } else {
      showError(`No active transaction found for: ${inputValue}`)
      console.log('❌ No transaction found for:', inputValue)
      
      // Play error sound
      try {
        await audioService.playErrorSound()
      } catch (error) {
        console.warn('Failed to play error sound:', error)
      }
      
      // Show additional info
      $q.notify({
        type: 'info',
        message: 'Checked both barcode and license plate - no active transaction found',
        timeout: 5000
      })
    }
    
  } catch (error) {
    console.error('Error checking transaction:', error)
    showError('Error checking transaction: ' + (error instanceof Error ? error.message : String(error)))
    
    // Play error sound
    try {
      await audioService.playErrorSound()
    } catch (error) {
      console.warn('Failed to play error sound:', error)
    }
  } finally {
    processing.value = false
  }
}

// Utility functions
function getStatusColor(status: GateStatus): string {
  switch (status) {
    case GateStatus.OPEN: return 'green'
    case GateStatus.OPENING: return 'orange'
    case GateStatus.CLOSING: return 'orange'
    case GateStatus.ERROR: return 'red'
    default: return 'grey'
  }
}

function getStatusIcon(status: GateStatus): string {
  switch (status) {
    case GateStatus.OPEN: return 'lock_open'
    case GateStatus.OPENING: return 'hourglass_empty'
    case GateStatus.CLOSING: return 'hourglass_empty'
    case GateStatus.ERROR: return 'error'
    default: return 'lock'
  }
}

function getVehicleTypeName(id: number): string {
  const vehicleType = vehicleTypes.value.find(vt => vt.id_kendaraan === id)
  return vehicleType?.nama_kendaraan || 'Unknown'
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString()
}

function formatDateTime(dateString: string): string {
  return new Date(dateString).toLocaleString()
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR'
  }).format(amount)
}

function showError(message: string) {
  errorMessage.value = message
  $q.notify({
    type: 'negative',
    message,
    icon: 'error'
  })
  
  // Play error sound
  try {
    audioService.playErrorSound()
  } catch (error) {
    console.warn('Failed to play error sound:', error)
  }
}

// Camera event handlers
function onPlateCaptured(capturedData: any) {
  // console.log('📸 Plate camera captured:', capturedData)
  capturedExitImages.value.plateImage = capturedData.image
 
}

function onDriverCaptured(capturedData: any) {
  // console.log('📸 Driver camera captured:', capturedData)
  capturedExitImages.value.driverImage = capturedData.image
  
 
}

function onCameraError(error: any) {

}

// Capture images when barcode is scanned
async function captureExitImages() {
  try {
    console.log('📸 Capturing exit images from CCTV cameras...')
    
    // Capture from both cameras in parallel
    const capturePromises = []
    
    if (plateExitCameraRef.value && 'getImage' in plateExitCameraRef.value) {
      capturePromises.push(
        (plateExitCameraRef.value as any).getImage().then((image: any) => {
          if (image) {
            console.log('✅ Plate exit image captured')
            capturedExitImages.value.plateImage = image
          }
        }).catch((error: any) => {
          console.warn('⚠️ Plate camera capture failed:', error)
        })
      )
    }
    
    if (driverExitCameraRef.value && 'getImage' in driverExitCameraRef.value) {
      capturePromises.push(
        (driverExitCameraRef.value as any).getImage().then((image: any) => {
          if (image) {
            console.log('✅ Driver exit image captured')
            capturedExitImages.value.driverImage = image
          }
        }).catch((error: any) => {
          console.warn('⚠️ Driver camera capture failed:', error)
        })
      )
    }
    
    // Wait for all captures with timeout
    await Promise.race([
      Promise.allSettled(capturePromises),
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Camera capture timeout')), 8000) // Increased timeout for CCTV
      )
    ])
    
    console.log('📸 Exit image capture completed')
    
  } catch (error) {
    console.error('❌ Error capturing exit images:', error)
    $q.notify({
      type: 'info',
      message: 'Camera capture timeout - continuing without images',
      timeout: 2000
    })
  }
}
</script>

<style scoped>
.q-page {
  min-height: 100vh;
}
</style>
