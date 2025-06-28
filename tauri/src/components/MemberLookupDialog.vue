<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" persistent>
    <q-card class="member-lookup-card" style="min-width: 500px;">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Cek Status Member</div>
        <q-space />
        <q-btn icon="close" flat round dense @click="onDialogCancel" />
      </q-card-section>

      <q-card-section>
        <!-- Search Input -->
        <q-input
          v-model="searchQuery"
          outlined
          label="Nomor Polisi atau ID Member"
          placeholder="Masukkan nomor polisi (B1234XYZ) atau ID member"
          @keyup.enter="searchMember"
          autofocus
          clearable
          class="q-mb-md"
        >
          <template v-slot:prepend>
            <q-icon name="search" />
          </template>
          <template v-slot:append>
            <q-btn
              round
              dense
              flat
              icon="search"
              @click="searchMember"
              :loading="searching"
            />
          </template>
        </q-input>

        <!-- Member Result -->
        <div v-if="memberResult" class="member-result q-mb-md">
          <q-card flat bordered>
            <q-card-section class="bg-grey-1">
              <div class="row items-center q-gutter-md">
                <q-avatar size="60px" color="primary" text-color="white">
                  {{ memberResult.name.charAt(0).toUpperCase() }}
                </q-avatar>
                <div class="col">
                  <div class="text-h6 text-weight-bold">{{ memberResult.name }}</div>
                  <div class="text-body2 text-grey-7">{{ memberResult.member_id }}</div>
                  <div class="text-caption text-grey-6">{{ memberResult.phone }}</div>
                </div>
                <div class="text-right">
                  <q-chip
                    :color="getMembershipCategoryColor(memberResult.membershipCategory)"
                    text-color="white"
                    icon="card_membership"
                  >
                    {{ memberResult.membershipType }}
                  </q-chip>
                </div>
              </div>
            </q-card-section>

            <q-card-section>
              <!-- Status Information -->
              <div class="row q-col-gutter-md q-mb-md">
                <div class="col-6">
                  <q-item dense>
                    <q-item-section avatar>
                      <q-icon name="event" color="primary" />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label class="text-caption">Berlaku s/d</q-item-label>
                      <q-item-label class="text-weight-medium">
                        {{ formatDate(memberResult.end_date) }}
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </div>
                <div class="col-6">
                  <q-item dense>
                    <q-item-section avatar>
                      <q-icon 
                        :name="getStatusIcon(memberResult)" 
                        :color="getStatusColor(memberResult)" 
                      />
                    </q-item-section>
                    <q-item-section>
                      <q-item-label class="text-caption">Status</q-item-label>
                      <q-item-label 
                        class="text-weight-medium"
                        :class="`text-${getStatusColor(memberResult)}`"
                      >
                        {{ getStatusLabel(memberResult) }}
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </div>
              </div>

              <!-- Expiry Warning -->
              <q-banner
                v-if="memberResult.isExpiringSoon && !memberResult.isExpired"
                class="bg-orange-1 text-orange-8 q-mb-md"
                dense
                rounded
              >
                <template v-slot:avatar>
                  <q-icon name="warning" color="orange" />
                </template>
                Membership akan berakhir dalam {{ memberResult.daysUntilExpiry }} hari
              </q-banner>

              <q-banner
                v-if="memberResult.isExpired"
                class="bg-red-1 text-red-8 q-mb-md"
                dense
                rounded
              >
                <template v-slot:avatar>
                  <q-icon name="error" color="red" />
                </template>
                Membership sudah berakhir {{ Math.abs(memberResult.daysUntilExpiry) }} hari yang lalu
              </q-banner>

              <!-- Payment Status -->
              <div v-if="memberResult.payment_status" class="q-mb-md">
                <q-chip
                  :color="getPaymentStatusColor(memberResult.payment_status)"
                  text-color="white"
                  icon="payment"
                >
                  {{ getPaymentStatusLabel(memberResult.payment_status) }}
                </q-chip>
              </div>

              <!-- Discount Info -->
              <div v-if="memberResult.hasDiscount && !memberResult.isExpired" class="q-mb-md">
                <q-card flat class="bg-green-1">
                  <q-card-section class="q-pa-sm">
                    <div class="row items-center">
                      <q-icon name="local_offer" color="green" class="q-mr-sm" />
                      <div class="text-green-8 text-weight-medium">
                        Diskon Member {{ memberResult.discountPercentage }}%
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </div>

              <!-- Vehicles -->
              <div class="text-subtitle2 q-mb-sm">Kendaraan Terdaftar:</div>
              <div class="row q-gutter-sm">
                <q-chip
                  v-for="(vehicle, index) in memberResult.vehicles"
                  :key="index"
                  :color="vehicle.license_plate.toUpperCase() === searchQuery.toUpperCase() ? 'primary' : 'blue-1'"
                  :text-color="vehicle.license_plate.toUpperCase() === searchQuery.toUpperCase() ? 'white' : 'primary'"
                  :icon="getVehicleIcon(vehicle.type)"
                  square
                >
                  {{ vehicle.license_plate }}
                  <q-tooltip>{{ vehicle.type }} - {{ vehicle.brand }} {{ vehicle.model }}</q-tooltip>
                </q-chip>
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- No Result -->
        <div v-else-if="searchPerformed && !searching" class="text-center q-py-lg">
          <q-icon name="person_search" size="4rem" color="grey-4" />
          <div class="text-h6 text-grey-6 q-mt-md">
            Tidak ditemukan
          </div>
          <div class="text-body2 text-grey-5">
            Member dengan nomor polisi atau ID tersebut tidak ditemukan
          </div>
        </div>

        <!-- Loading -->
        <div v-if="searching" class="text-center q-py-lg">
          <q-spinner-dots size="2rem" color="primary" />
          <div class="text-body2 q-mt-md">Mencari member...</div>
        </div>
      </q-card-section>

      <q-card-actions align="right" class="q-pa-md">
        <q-btn
          flat
          label="Tutup"
          color="grey"
          @click="onDialogCancel"
        />
        <q-btn
          v-if="memberResult && !memberResult.isExpired"
          unelevated
          label="Gunakan Member"
          color="primary"
          @click="useMember"
          icon="check"
        />
        <q-btn
          v-if="memberResult && memberResult.isExpiringSoon"
          outline
          label="Perpanjang"
          color="orange"
          @click="renewMembership"
          icon="autorenew"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDialogPluginComponent, useQuasar } from 'quasar'
import { useMembershipStore } from 'src/stores/membership-store'

// Quasar dialog composition
const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent()

const $q = useQuasar()
const membershipStore = useMembershipStore()

const props = defineProps({
  initialSearch: {
    type: String,
    default: ''
  }
})

const emit = defineEmits([
  // Dialog events
  ...useDialogPluginComponent.emits,
  // Custom events
  'memberSelected',
  'memberRenewed'
])

// Reactive data
const searchQuery = ref(props.initialSearch || '')
const memberResult = ref(null)
const searching = ref(false)
const searchPerformed = ref(false)

// Methods
const searchMember = async () => {
  if (!searchQuery.value.trim()) {
    $q.notify({
      type: 'warning',
      message: 'Masukkan nomor polisi atau ID member'
    })
    return
  }

  searching.value = true
  searchPerformed.value = false
  memberResult.value = null

  try {
    // Check if input looks like a license plate (contains letters and numbers)
    const isLicensePlate = /^[A-Z0-9\s]+$/i.test(searchQuery.value.trim())
    
    let member = null
    
    if (isLicensePlate) {
      // Search by license plate
      member = await membershipStore.checkMembershipWithDiscount(searchQuery.value.trim())
    } else {
      // Search by member ID
      const allMembers = await membershipStore.loadMembers()
      const foundMember = membershipStore.members.find(m => 
        m.member_id.toLowerCase() === searchQuery.value.toLowerCase().trim()
      )
      
      if (foundMember) {
        const membershipType = membershipStore.membershipTypes.find(t => t._id === foundMember.membership_type_id)
        const discount = membershipStore.calculateMemberDiscount(membershipType)
        
        member = {
          ...foundMember,
          isExpired: membershipStore.isExpired(foundMember.end_date),
          isExpiringSoon: membershipStore.isExpiringSoon(foundMember.end_date),
          daysUntilExpiry: membershipStore.calculateDaysUntilExpiry(foundMember.end_date),
          membershipType: membershipType ? membershipType.name : 'Unknown',
          membershipCategory: membershipType ? membershipType.category : 'REGULAR',
          hasDiscount: discount > 0,
          discountPercentage: discount
        }
      }
    }

    memberResult.value = member
    searchPerformed.value = true

    if (member) {
      $q.notify({
        type: 'positive',
        message: `Member ditemukan: ${member.name}`,
        timeout: 2000
      })
    }
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

const useMember = () => {
  if (memberResult.value) {
    emit('memberSelected', memberResult.value)
    onDialogOK(memberResult.value)
  }
}

const renewMembership = async () => {
  if (!memberResult.value) return

  $q.dialog({
    title: 'Perpanjang Membership',
    message: `Perpanjang membership ${memberResult.value.name} selama berapa bulan?`,
    prompt: {
      model: '12',
      type: 'number',
      min: 1,
      max: 60
    },
    cancel: true,
    persistent: true
  }).onOk(async (months) => {
    try {
      await membershipStore.renewMembership(memberResult.value._id, parseInt(months))
      
      $q.notify({
        type: 'positive',
        message: 'Membership berhasil diperpanjang'
      })
      
      emit('memberRenewed', {
        member: memberResult.value,
        months: parseInt(months)
      })
      
      // Refresh member data
      await searchMember()
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: 'Gagal memperpanjang membership'
      })
    }
  })
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

const getVehicleIcon = (type) => {
  const icons = {
    'Mobil': 'directions_car',
    'Motor': 'two_wheeler',
    'Truk': 'local_shipping',
    'Bus': 'directions_bus'
  }
  return icons[type] || 'directions_car'
}

const getStatusColor = (member) => {
  if (member.active === 0) return 'red'
  if (member.isExpired) return 'red'
  if (member.isExpiringSoon) return 'orange'
  return 'green'
}

const getStatusIcon = (member) => {
  if (member.active === 0) return 'cancel'
  if (member.isExpired) return 'error'
  if (member.isExpiringSoon) return 'warning'
  return 'check_circle'
}

const getStatusLabel = (member) => {
  if (member.active === 0) return 'Tidak Aktif'
  if (member.isExpired) return 'Kadaluarsa'
  if (member.isExpiringSoon) return 'Akan Berakhir'
  return 'Aktif'
}

const getPaymentStatusColor = (status) => {
  const colors = {
    'pending': 'orange',
    'paid': 'green',
    'overdue': 'red'
  }
  return colors[status] || 'grey'
}

const getPaymentStatusLabel = (status) => {
  const labels = {
    'pending': 'Pending',
    'paid': 'Lunas',
    'overdue': 'Terlambat'
  }
  return labels[status] || 'Unknown'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('id-ID', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Auto search if initial search provided
if (props.initialSearch) {
  searchMember()
}
</script>

<style scoped>
.member-lookup-card {
  max-width: 600px;
}

.member-result {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.text-green-8 {
  color: #2e7d32;
}

.text-orange-8 {
  color: #ef6c00;
}

.text-red-8 {
  color: #c62828;
}
</style>
