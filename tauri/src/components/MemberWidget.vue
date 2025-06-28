<template>
  <q-card class="member-widget">
    <q-card-section class="bg-primary text-white">
      <div class="row items-center">
        <q-icon name="card_membership" size="2rem" class="q-mr-md" />
        <div>
          <div class="text-h6">Member</div>
          <div class="text-caption">Status Keanggotaan</div>
        </div>
        <q-space />
        <q-btn
          flat
          round
          icon="refresh"
          @click="loadData"
          :loading="loading"
          size="sm"
        />
      </div>
    </q-card-section>

    <q-card-section>
      <!-- Statistics Overview -->
      <div class="row q-col-gutter-sm q-mb-md">
        <div class="col-6">
          <q-item dense>
            <q-item-section avatar>
              <q-avatar color="blue" text-color="white" size="sm">
                <q-icon name="people" />
              </q-avatar>
            </q-item-section>
            <q-item-section>
              <q-item-label class="text-weight-bold">{{ statistics.totalMembers }}</q-item-label>
              <q-item-label caption>Total Member</q-item-label>
            </q-item-section>
          </q-item>
        </div>
        
        <div class="col-6">
          <q-item dense>
            <q-item-section avatar>
              <q-avatar color="green" text-color="white" size="sm">
                <q-icon name="check_circle" />
              </q-avatar>
            </q-item-section>
            <q-item-section>
              <q-item-label class="text-weight-bold">{{ statistics.activeMembers }}</q-item-label>
              <q-item-label caption>Aktif</q-item-label>
            </q-item-section>
          </q-item>
        </div>
        
        <div class="col-6">
          <q-item dense>
            <q-item-section avatar>
              <q-avatar color="orange" text-color="white" size="sm">
                <q-icon name="warning" />
              </q-avatar>
            </q-item-section>
            <q-item-section>
              <q-item-label class="text-weight-bold">{{ statistics.expiringSoon }}</q-item-label>
              <q-item-label caption>Akan Berakhir</q-item-label>
            </q-item-section>
          </q-item>
        </div>
        
        <div class="col-6">
          <q-item dense>
            <q-item-section avatar>
              <q-avatar color="purple" text-color="white" size="sm">
                <q-icon name="attach_money" />
              </q-avatar>
            </q-item-section>
            <q-item-section>
              <q-item-label class="text-weight-bold">{{ formatCurrency(statistics.totalRevenue) }}</q-item-label>
              <q-item-label caption>Pendapatan</q-item-label>
            </q-item-section>
          </q-item>
        </div>
      </div>

      <!-- Member Type Distribution -->
      <div class="q-mb-md">
        <div class="text-subtitle2 q-mb-sm">Distribusi Tipe Member</div>
        <div class="row q-gutter-xs">
          <q-chip
            v-for="(count, category) in membersByCategory"
            :key="category"
            :color="getCategoryColor(category)"
            text-color="white"
            dense
            square
          >
            {{ category }}: {{ count }}
          </q-chip>
        </div>
      </div>

      <!-- Recent Activity -->
      <div v-if="recentMembers.length > 0" class="q-mb-md">
        <div class="text-subtitle2 q-mb-sm">Member Terbaru</div>
        <q-list dense>
          <q-item
            v-for="member in recentMembers.slice(0, 3)"
            :key="member._id"
            dense
          >
            <q-item-section avatar>
              <q-avatar size="sm" color="primary" text-color="white">
                {{ member.name.charAt(0).toUpperCase() }}
              </q-avatar>
            </q-item-section>
            <q-item-section>
              <q-item-label lines="1">{{ member.name }}</q-item-label>
              <q-item-label caption>{{ member.member_id }}</q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-chip
                :color="getCategoryColor(member.membershipCategory)"
                text-color="white"
                dense
                size="sm"
              >
                {{ member.membershipCategory }}
              </q-chip>
            </q-item-section>
          </q-item>
        </q-list>
      </div>

      <!-- Expiring Members Alert -->
      <div v-if="expiringMembers.length > 0" class="q-mb-md">
        <q-banner class="bg-orange-1 text-orange-8" dense rounded>
          <template v-slot:avatar>
            <q-icon name="warning" color="orange" />
          </template>
          <div class="text-weight-medium q-mb-xs">
            {{ expiringMembers.length }} member akan berakhir dalam 7 hari
          </div>
          <div class="text-caption">
            <div
              v-for="member in expiringMembers.slice(0, 2)"
              :key="member._id"
            >
              • {{ member.name }} ({{ member.daysLeft }} hari)
            </div>
            <div v-if="expiringMembers.length > 2" class="text-weight-medium">
              dan {{ expiringMembers.length - 2 }} lainnya...
            </div>
          </div>
          <template v-slot:action>
            <q-btn
              flat
              dense
              color="orange"
              label="Lihat"
              @click="$emit('view-expiring')"
              size="sm"
            />
          </template>
        </q-banner>
      </div>
    </q-card-section>

    <q-card-actions>
      <q-btn
        flat
        color="primary"
        icon="search"
        label="Cek Member"
        @click="showMemberLookup"
        class="q-mr-sm"
      />
      <q-btn
        flat
        color="primary"
        icon="people"
        label="Kelola"
        @click="$emit('manage-members')"
      />
      <q-space />
      <q-btn
        flat
        color="primary"
        icon="person_add"
        label="Tambah"
        @click="$emit('add-member')"
      />
    </q-card-actions>

    <!-- Member Lookup Dialog -->
    <q-dialog v-model="showLookupDialog">
      <MemberLookupDialog
        @member-selected="onMemberSelected"
        @member-renewed="onMemberRenewed"
      />
    </q-dialog>
  </q-card>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'
import { useMembershipStore } from 'src/stores/membership-store'
import MemberLookupDialog from './MemberLookupDialog.vue'

const $q = useQuasar()
const membershipStore = useMembershipStore()

defineEmits([
  'view-expiring',
  'manage-members', 
  'add-member',
  'member-checked'
])

// Reactive data
const loading = ref(false)
const showLookupDialog = ref(false)
const refreshInterval = ref(null)

// Computed
const statistics = computed(() => membershipStore.statistics)
const members = computed(() => membershipStore.members)
const membershipTypes = computed(() => membershipStore.membershipTypes)

const membersByCategory = computed(() => {
  const categories = {}
  
  members.value.forEach(member => {
    const category = member.membershipCategory || 'REGULAR'
    categories[category] = (categories[category] || 0) + 1
  })
  
  return categories
})

const recentMembers = computed(() => {
  return [...members.value]
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    .slice(0, 5)
})

const expiringMembers = computed(() => {
  return members.value
    .filter(member => {
      const daysUntil = membershipStore.calculateDaysUntilExpiry(member.end_date)
      return daysUntil !== null && daysUntil <= 7 && daysUntil > 0
    })
    .map(member => ({
      ...member,
      daysLeft: membershipStore.calculateDaysUntilExpiry(member.end_date)
    }))
    .sort((a, b) => a.daysLeft - b.daysLeft)
})

// Methods
const loadData = async () => {
  loading.value = true
  try {
    await Promise.all([
      membershipStore.loadMembers(),
      membershipStore.loadMembershipTypes()
    ])
  } catch (error) {
    console.error('Error loading member data:', error)
    $q.notify({
      type: 'negative',
      message: 'Error loading member data'
    })
  } finally {
    loading.value = false
  }
}

const showMemberLookup = () => {
  showLookupDialog.value = true
}

const onMemberSelected = (member) => {
  $q.notify({
    type: 'positive',
    message: `Member dipilih: ${member.name}`,
    timeout: 2000
  })
  
  // Emit event for parent component
  $emit('member-checked', member)
}

const onMemberRenewed = (data) => {
  $q.notify({
    type: 'positive',
    message: `Membership ${data.member.name} diperpanjang ${data.months} bulan`,
    timeout: 3000
  })
  
  // Reload data
  loadData()
}

const getCategoryColor = (category) => {
  const colors = {
    'VIP': 'purple',
    'PREMIUM': 'orange',
    'REGULAR': 'blue',
    'CORPORATE': 'green'
  }
  return colors[category] || 'blue'
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount)
}

// Auto-refresh data every 5 minutes
const startAutoRefresh = () => {
  refreshInterval.value = setInterval(() => {
    loadData()
  }, 5 * 60 * 1000) // 5 minutes
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// Lifecycle
onMounted(async () => {
  await loadData()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.member-widget {
  height: 100%;
}

.text-orange-8 {
  color: #ef6c00;
}
</style>
