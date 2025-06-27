<template>
  <q-page class="flex column items-center justify-center bg-grey-1 q-pa-md">
    <!-- Header -->
    <div class="text-h3 text-weight-bold text-primary q-mb-lg">
      Exit Gate System
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
          <div v-if="!lastScan" class="text-grey-6">
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
          Transaction Found
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
      </q-card-section>
      <q-card-actions align="center" class="q-pa-md">
        <q-btn 
          color="green" 
          size="lg" 
          icon="exit_to_app"
          label="Process Exit"
          :loading="processing"
          @click="processExit"
        />
        <q-btn 
          color="grey" 
          size="lg" 
          icon="cancel"
          label="Cancel"
          :disable="processing"
          @click="cancelTransaction"
        />
      </q-card-actions>
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

// Show manual controls in development
const showManualControls = ref(true)

// Initialize services
onMounted(async () => {
  try {
    // Initialize database
    await databaseService.initialize()
    
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
  databaseService.removeSyncStatusListener(handleSyncStatusChange)
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
    } else {
      showError(`No active transaction found for barcode: ${result.code}`)
    }
  } catch (error) {
    console.error('Error finding transaction:', error)
    showError('Error looking up transaction')
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

// Process vehicle exit
async function processExit() {
  if (!currentTransaction.value) {
    showError('No transaction selected')
    return
  }
  
  processing.value = true
  
  try {
    // Calculate exit fee (you may want to implement time-based pricing)
    const exitFee = calculateExitFee(currentTransaction.value)
    
    // Update transaction in database
    const success = await databaseService.exitTransaction(currentTransaction.value._id, {
      waktu_keluar: new Date().toISOString(),
      bayar_keluar: exitFee
    })
    
    if (!success) {
      throw new Error('Failed to update transaction')
    }
    
    // Open the gate
    const gateOpened = await gateService.openGate(10) // Auto-close after 10 seconds
    
    if (gateOpened) {
      $q.notify({
        type: 'positive',
        message: `Exit processed successfully for ${currentTransaction.value.no_pol}`,
        icon: 'check_circle'
      })
      
      // Play exit success sound
      try {
        await audioService.playExitSuccessSound()
      } catch (error) {
        console.warn('Failed to play success sound:', error)
      }
      
      // Clear current transaction
      currentTransaction.value = null
      
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
</script>

<style scoped>
.q-page {
  min-height: 100vh;
}
</style>
