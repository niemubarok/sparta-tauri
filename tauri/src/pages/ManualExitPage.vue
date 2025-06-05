<template>
  <div class="exit-page" :class="{ 'dark-mode': isDark }">
    <div class="row q-pa-md q-col-gutter-md">
      <!-- Left Column -->
      <div class="col-12 col-md-8">
        <!-- Vehicle Info Card -->
        <q-card class="info-card">
          <q-card-section>
            <div class="text-h6">Vehicle Information</div>
            <div class="row q-col-gutter-md q-mt-sm">
              <div class="col-12 col-md-6">
                <q-input
                  v-model="plateNumber"
                  label="Plate Number"
                  @keyup.enter="searchVehicle"
                  class="q-mb-md"
                >
                  <template v-slot:append>
                    <q-btn
                      round
                      dense
                      flat
                      icon="search"
                      @click="searchVehicle"
                      :loading="isSearching"
                    />
                  </template>
                </q-input>

                <q-list v-if="vehicleData" bordered class="rounded-borders">
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Ticket Number</q-item-label>
                      <q-item-label>{{ vehicleData.ticket_number }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Vehicle Type</q-item-label>
                      <q-item-label>{{ vehicleData.vehicle_type }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Entry Time</q-item-label>
                      <q-item-label>{{ formatDateTime(vehicleData.entry_time) }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Duration</q-item-label>
                      <q-item-label>{{ calculateDuration(vehicleData.entry_time) }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>

              <div class="col-12 col-md-6">
                <!-- Entry Image -->
                <q-card bordered flat class="entry-image-card">
                  <q-card-section>
                    <div class="text-subtitle2">Entry Image</div>
                    <img
                      v-if="vehicleData?.entry_image"
                      :src="vehicleData.entry_image"
                      class="entry-image"
                    />
                    <div v-else class="no-image">No entry image available</div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Payment Card -->
        <q-card v-if="vehicleData" class="payment-card q-mt-md">
          <q-card-section>
            <div class="text-h6">Payment Details</div>
            <div class="row q-col-gutter-md q-mt-sm">
              <div class="col-12 col-md-6">
                <q-list bordered>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Base Rate</q-item-label>
                      <q-item-label>Rp {{ formatCurrency(baseRate) }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item v-if="additionalFee > 0">
                    <q-item-section>
                      <q-item-label caption>Additional Fee</q-item-label>
                      <q-item-label>Rp {{ formatCurrency(additionalFee) }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item class="text-weight-bold">
                    <q-item-section>
                      <q-item-label caption>Total Amount</q-item-label>
                      <q-item-label class="text-h5 text-primary">
                        Rp {{ formatCurrency(totalAmount) }}
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </div>

              <div class="col-12 col-md-6">
                <q-input
                  v-model="amountPaid"
                  label="Amount Paid"
                  type="number"
                  @update:model-value="calculateChange"
                  class="q-mb-md"
                />
                
                <div v-if="change > 0" class="change-amount q-pa-md text-center">
                  <div class="text-subtitle2">Change</div>
                  <div class="text-h5 text-positive">Rp {{ formatCurrency(change) }}</div>
                </div>

                <q-btn
                  color="primary"
                  class="full-width q-mt-md"
                  size="lg"
                  :disable="!canProcessPayment"
                  @click="processPayment"
                  :loading="isProcessing"
                >
                  Process Payment
                </q-btn>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Right Column -->
      <div class="col-12 col-md-4">
        <!-- Gate Control Card -->
        <q-card class="gate-control-card">
          <q-card-section>
            <div class="text-h6">Gate Control</div>
            <div class="row q-col-gutter-sm q-mt-md">
              <div class="col-12">
                <q-btn
                  color="primary"
                  class="full-width q-py-sm"
                  :disable="!canOpenGate"
                  :loading="isProcessing"
                  @click="openGate"
                  icon="door_front"
                  label="Open Gate"
                />
              </div>
              <div class="col-12">
                <q-btn
                  color="grey"
                  class="full-width q-py-sm"
                  @click="reset"
                  icon="refresh"
                  label="Reset"
                  :disable="isProcessing"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Transaction History -->
        <q-card class="history-card q-mt-md">
          <q-card-section>
            <div class="text-h6">Recent Transactions</div>
            <q-scroll-area style="height: 300px;" class="q-mt-sm">
              <q-list>
                <q-item v-for="transaction in recentTransactions" :key="transaction.id">
                  <q-item-section>
                    <q-item-label>{{ transaction.plate_number }}</q-item-label>
                    <q-item-label caption>
                      Amount: Rp {{ formatCurrency(transaction.amount) }}
                    </q-item-label>
                    <q-item-label caption>
                      {{ formatDateTime(transaction.timestamp) }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-scroll-area>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Notifications -->
    <q-dialog v-model="showSuccessDialog" persistent>
      <q-card class="success-dialog">
        <q-card-section class="row items-center">
          <q-avatar icon="check_circle" color="positive" text-color="white" />
          <span class="q-ml-sm">Payment processed successfully!</span>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Close" color="primary" v-close-popup @click="reset" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'src/boot/axios'
import { useThemeStore } from 'src/stores/theme'

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)
const $q = useQuasar()

// State
const plateNumber = ref('')
const vehicleData = ref(null)
const isSearching = ref(false)
const isProcessing = ref(false)
const amountPaid = ref(0)
const showSuccessDialog = ref(false)
const recentTransactions = ref([])

// Computed values
const baseRate = computed(() => vehicleData.value?.base_rate || 0)
const additionalFee = computed(() => vehicleData.value?.additional_fee || 0)
const totalAmount = computed(() => baseRate.value + additionalFee.value)
const change = computed(() => Math.max(0, amountPaid.value - totalAmount.value))
const canProcessPayment = computed(() => 
  vehicleData.value && 
  amountPaid.value >= totalAmount.value && 
  !isProcessing.value
)
const canOpenGate = computed(() => 
  vehicleData.value?.payment_status === 'PAID' && 
  !isProcessing.value
)

// Methods
const searchVehicle = async () => {
  if (!plateNumber.value) return

  try {
    isSearching.value = true
    const response = await api.get(`/parking/search/${plateNumber.value}`)
    vehicleData.value = response.data
    
    if (!vehicleData.value) {
      $q.notify({
        type: 'warning',
        message: 'No vehicle found with this plate number'
      })
    }
  } catch (error) {
    console.error('Error searching vehicle:', error)
    $q.notify({
      type: 'negative',
      message: 'Error searching vehicle'
    })
  } finally {
    isSearching.value = false
  }
}

const calculateChange = () => {
  // Change is computed automatically through the computed property
}

const processPayment = async () => {
  try {
    isProcessing.value = true
    const response = await api.post('/parking/payment', {
      ticket_number: vehicleData.value.ticket_number,
      amount_paid: amountPaid.value,
      total_amount: totalAmount.value
    })

    if (response.data.success) {
      showSuccessDialog.value = true
      await loadRecentTransactions()
      vehicleData.value.payment_status = 'PAID'
    }
  } catch (error) {
    console.error('Error processing payment:', error)
    $q.notify({
      type: 'negative',
      message: 'Error processing payment'
    })
  } finally {
    isProcessing.value = false
  }
}

const openGate = async () => {
  try {
    isProcessing.value = true
    await api.post('/parking/open-gate', {
      ticket_number: vehicleData.value.ticket_number
    })
    
    $q.notify({
      type: 'positive',
      message: 'Gate opened successfully'
    })

    // Auto reset after successful gate opening
    setTimeout(reset, 30000)
  } catch (error) {
    console.error('Error opening gate:', error)
    $q.notify({
      type: 'negative',
      message: 'Error opening gate'
    })
  } finally {
    isProcessing.value = false
  }
}

const reset = () => {
  plateNumber.value = ''
  vehicleData.value = null
  amountPaid.value = 0
  showSuccessDialog.value = false
}

const loadRecentTransactions = async () => {
  try {
    const response = await api.get('/parking/recent-transactions')
    recentTransactions.value = response.data
  } catch (error) {
    console.error('Error loading recent transactions:', error)
  }
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('id-ID').format(amount)
}

const formatDateTime = (datetime) => {
  return new Date(datetime).toLocaleString('id-ID')
}

const calculateDuration = (entryTime) => {
  const start = new Date(entryTime)
  const end = new Date()
  const diff = end - start
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  return `${hours} hours ${minutes} minutes`
}

// Lifecycle hooks
onMounted(async () => {
  await loadRecentTransactions()
})
</script>

<style scoped>
.exit-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  transition: background-color 0.3s ease;
}

.exit-page.dark-mode {
  background-color: #121212;
}

.info-card,
.payment-card,
.gate-control-card,
.history-card {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.dark-mode .info-card,
.dark-mode .payment-card,
.dark-mode .gate-control-card,
.dark-mode .history-card {
  background-color: #1e1e1e;
  color: #fff;
}

.entry-image {
  width: 100%;
  height: 200px;
  object-fit: contain;
  border-radius: 4px;
}

.no-image {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  border-radius: 4px;
  color: #666;
}

.dark-mode .no-image {
  background-color: #2d2d2d;
  color: #999;
}

.change-amount {
  background-color: #f0f9f0;
  border-radius: 8px;
}

.dark-mode .change-amount {
  background-color: #1a291a;
}

.success-dialog {
  min-width: 300px;
}

@media (max-width: 600px) {
  .text-h5 {
    font-size: 1.2rem !important;
  }

  .text-h6 {
    font-size: 1rem !important;
  }

  .entry-image {
    height: 150px;
  }
}
</style>