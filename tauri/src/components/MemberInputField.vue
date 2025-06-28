<template>
  <div class="member-input-field">
    <!-- Member Search Input -->
    <q-input
      v-model="searchQuery"
      :label="label"
      :placeholder="placeholder"
      outlined
      :readonly="readonly"
      clearable
      @update:model-value="onSearchChange"
      @keyup.enter="searchMember"
      @clear="clearMember"
      :loading="searching"
      :rules="rules"
    >
      <template v-slot:prepend>
        <q-icon name="card_membership" />
      </template>
      
      <template v-slot:append>
        <q-btn
          v-if="!selectedMember"
          round
          dense
          flat
          icon="search"
          @click="openMemberLookup"
          :disable="readonly"
        >
          <q-tooltip>Cari Member</q-tooltip>
        </q-btn>
        
        <q-btn
          v-if="selectedMember"
          round
          dense
          flat
          icon="visibility"
          @click="showMemberDetail = true"
        >
          <q-tooltip>Lihat Detail Member</q-tooltip>
        </q-btn>
      </template>
    </q-input>

    <!-- Member Info Display -->
    <div v-if="selectedMember" class="member-info q-mt-sm">
      <q-card flat bordered class="member-info-card">
        <q-card-section class="q-pa-sm">
          <div class="row items-center q-gutter-sm">
            <!-- Member Avatar -->
            <q-avatar size="40px" color="primary" text-color="white">
              {{ selectedMember.name.charAt(0).toUpperCase() }}
            </q-avatar>
            
            <!-- Member Basic Info -->
            <div class="col">
              <div class="text-weight-medium">{{ selectedMember.name }}</div>
              <div class="text-caption text-grey-6">{{ selectedMember.member_id }}</div>
            </div>
            
            <!-- Member Type -->
            <q-chip
              :color="getMembershipCategoryColor(selectedMember.membershipCategory)"
              text-color="white"
              dense
              size="sm"
            >
              {{ selectedMember.membershipType }}
            </q-chip>
            
            <!-- Status Badge -->
            <q-badge
              :color="getStatusColor(selectedMember.membershipStatus)"
              :label="getStatusLabel(selectedMember.membershipStatus)"
            />
          </div>
          
          <!-- Additional Info Row -->
          <div class="row items-center q-mt-sm q-gutter-sm">
            <!-- Discount Info -->
            <div v-if="selectedMember.hasDiscount && selectedMember.membershipStatus === 'active'" class="col-auto">
              <q-chip
                color="green"
                text-color="white"
                dense
                size="sm"
                icon="local_offer"
              >
                Diskon {{ selectedMember.discountPercentage }}%
              </q-chip>
            </div>
            
            <!-- Expiry Warning -->
            <div v-if="selectedMember.isExpiringSoon" class="col-auto">
              <q-chip
                color="orange"
                text-color="white"
                dense
                size="sm"
                icon="warning"
              >
                {{ selectedMember.daysUntilExpiry }} hari lagi
              </q-chip>
            </div>
            
            <!-- Vehicle Info -->
            <div class="col">
              <div class="text-caption text-grey-6">
                Kendaraan: {{ getVehiclesList(selectedMember.vehicles) }}
              </div>
            </div>
            
            <!-- Remove Button -->
            <q-btn
              flat
              round
              dense
              icon="close"
              size="sm"
              @click="clearMember"
              :disable="readonly"
            >
              <q-tooltip>Hapus Member</q-tooltip>
            </q-btn>
          </div>
          
          <!-- Parking Fee Info -->
          <div v-if="showFeeCalculation && parkingFee > 0" class="q-mt-sm">
            <q-separator class="q-mb-sm" />
            <div class="parking-fee-info">
              <div class="row items-center justify-between">
                <div class="col">
                  <div class="text-caption text-grey-6">Biaya Parkir:</div>
                  <div class="text-body2">
                    <span v-if="feeCalculation.isMemberDiscount" class="text-strike text-grey-6">
                      {{ formatCurrency(feeCalculation.originalFee) }}
                    </span>
                    <span class="text-weight-bold" :class="feeCalculation.isMemberDiscount ? 'text-green' : ''">
                      {{ formatCurrency(feeCalculation.finalFee) }}
                    </span>
                  </div>
                </div>
                <div v-if="feeCalculation.isMemberDiscount" class="col-auto">
                  <q-chip color="green" text-color="white" dense size="sm">
                    Hemat {{ formatCurrency(feeCalculation.discountAmount) }}
                  </q-chip>
                </div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- Member not found message -->
    <div v-if="searchPerformed && !selectedMember && !searching" class="q-mt-sm">
      <q-banner dense class="bg-grey-2 text-grey-7">
        <template v-slot:avatar>
          <q-icon name="info" />
        </template>
        Member tidak ditemukan untuk nomor polisi "{{ searchQuery }}"
      </q-banner>
    </div>

    <!-- Member Lookup Dialog -->
    <q-dialog v-model="showMemberLookup">
      <MemberLookupDialog
        :initial-search="searchQuery"
        @member-selected="onMemberSelected"
        @member-renewed="onMemberRenewed"
      />
    </q-dialog>

    <!-- Member Detail Dialog -->
    <q-dialog v-model="showMemberDetail">
      <q-card style="min-width: 400px;">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Detail Member</div>
        </q-card-section>
        
        <q-card-section v-if="selectedMember">
          <q-list>
            <q-item>
              <q-item-section>
                <q-item-label class="text-weight-medium">Nama</q-item-label>
                <q-item-label caption>{{ selectedMember.name }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label class="text-weight-medium">ID Member</q-item-label>
                <q-item-label caption>{{ selectedMember.member_id }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label class="text-weight-medium">Telepon</q-item-label>
                <q-item-label caption>{{ selectedMember.phone }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label class="text-weight-medium">Tipe Member</q-item-label>
                <q-item-label caption>
                  <q-chip
                    :color="getMembershipCategoryColor(selectedMember.membershipCategory)"
                    text-color="white"
                    dense
                  >
                    {{ selectedMember.membershipType }}
                  </q-chip>
                </q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label class="text-weight-medium">Berlaku Sampai</q-item-label>
                <q-item-label caption>{{ formatDate(selectedMember.end_date) }}</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item>
              <q-item-section>
                <q-item-label class="text-weight-medium">Kendaraan</q-item-label>
                <q-item-label caption>
                  <div class="q-gutter-xs">
                    <q-chip
                      v-for="(vehicle, index) in selectedMember.vehicles"
                      :key="index"
                      dense
                      square
                      color="blue-1"
                      text-color="primary"
                    >
                      {{ vehicle.license_plate }}
                    </q-chip>
                  </div>
                </q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
        
        <q-card-actions align="right">
          <q-btn flat label="Tutup" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import { memberGateIntegration } from 'src/utils/member-gate-integration'
import MemberLookupDialog from './MemberLookupDialog.vue'

const $q = useQuasar()

const props = defineProps({
  modelValue: {
    type: Object,
    default: null
  },
  plateNumber: {
    type: String,
    default: ''
  },
  parkingFee: {
    type: Number,
    default: 0
  },
  label: {
    type: String,
    default: 'Member'
  },
  placeholder: {
    type: String,
    default: 'Cari member berdasarkan nomor polisi atau ID member'
  },
  readonly: {
    type: Boolean,
    default: false
  },
  showFeeCalculation: {
    type: Boolean,
    default: false
  },
  rules: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits([
  'update:modelValue',
  'member-selected',
  'member-cleared',
  'fee-calculated'
])

// Reactive data
const searchQuery = ref('')
const selectedMember = ref(props.modelValue)
const searching = ref(false)
const searchPerformed = ref(false)
const showMemberLookup = ref(false)
const showMemberDetail = ref(false)

// Computed
const feeCalculation = computed(() => {
  if (!selectedMember.value || props.parkingFee <= 0) {
    return {
      originalFee: props.parkingFee,
      finalFee: props.parkingFee,
      discountAmount: 0,
      isMemberDiscount: false
    }
  }
  
  return memberGateIntegration.calculateMemberFee(props.parkingFee, selectedMember.value)
})

// Watch for external plate number changes
watch(() => props.plateNumber, (newPlateNumber) => {
  if (newPlateNumber && newPlateNumber !== searchQuery.value) {
    searchQuery.value = newPlateNumber
    searchMember()
  }
}, { immediate: true })

// Watch for selected member changes
watch(selectedMember, (newMember) => {
  emit('update:modelValue', newMember)
  
  if (newMember) {
    emit('member-selected', newMember)
    
    if (props.showFeeCalculation && props.parkingFee > 0) {
      emit('fee-calculated', feeCalculation.value)
    }
  } else {
    emit('member-cleared')
  }
}, { immediate: true })

// Watch for fee calculation changes
watch(feeCalculation, (newCalculation) => {
  if (props.showFeeCalculation) {
    emit('fee-calculated', newCalculation)
  }
}, { deep: true })

// Methods
const onSearchChange = (value) => {
  searchQuery.value = value
  if (!value) {
    clearMember()
  }
}

const searchMember = async () => {
  if (!searchQuery.value || searchQuery.value.trim() === '') {
    return
  }

  searching.value = true
  searchPerformed.value = false
  
  try {
    const member = await memberGateIntegration.checkMemberStatus(searchQuery.value.trim())
    
    if (member) {
      selectedMember.value = member
      
      $q.notify({
        type: 'positive',
        message: `Member ditemukan: ${member.name}`,
        timeout: 2000
      })
    } else {
      selectedMember.value = null
    }
    
    searchPerformed.value = true
  } catch (error) {
    console.error('Error searching member:', error)
    $q.notify({
      type: 'negative',
      message: 'Error mencari member'
    })
  } finally {
    searching.value = false
  }
}

const clearMember = () => {
  selectedMember.value = null
  searchQuery.value = ''
  searchPerformed.value = false
}

const openMemberLookup = () => {
  showMemberLookup.value = true
}

const onMemberSelected = (member) => {
  selectedMember.value = member
  searchQuery.value = member.member_id
  showMemberLookup.value = false
  
  $q.notify({
    type: 'positive',
    message: `Member dipilih: ${member.name}`
  })
}

const onMemberRenewed = (data) => {
  $q.notify({
    type: 'positive',
    message: `Membership ${data.member.name} diperpanjang ${data.months} bulan`
  })
  
  // Refresh member data
  if (selectedMember.value && selectedMember.value._id === data.member._id) {
    searchMember()
  }
}

// Helper functions
const getMembershipCategoryColor = (category) => {
  const colors = {
    'VIP': 'purple',
    'PREMIUM': 'orange',
    'REGULAR': 'blue',
    'CORPORATE': 'green'
  }
  return colors[category] || 'blue'
}

const getStatusColor = (status) => {
  const colors = {
    'active': 'green',
    'expiring': 'orange',
    'expired': 'red',
    'inactive': 'grey'
  }
  return colors[status] || 'grey'
}

const getStatusLabel = (status) => {
  const labels = {
    'active': 'Aktif',
    'expiring': 'Akan Berakhir',
    'expired': 'Kadaluarsa',
    'inactive': 'Tidak Aktif'
  }
  return labels[status] || 'Unknown'
}

const getVehiclesList = (vehicles) => {
  if (!vehicles || vehicles.length === 0) return '-'
  return vehicles.map(v => v.license_plate).join(', ')
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('id-ID', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount)
}
</script>

<style scoped>
.member-input-field {
  width: 100%;
}

.member-info-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-left: 4px solid var(--q-primary);
}

.parking-fee-info {
  background: rgba(33, 186, 69, 0.1);
  border-radius: 4px;
  padding: 8px;
}

.text-strike {
  text-decoration: line-through;
}

.text-green {
  color: #21ba45;
}
</style>
