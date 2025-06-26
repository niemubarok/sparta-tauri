<template>
  <div class="q-pa-md">
    <!-- Header -->
    <div class="row items-center justify-between q-mb-md">
      <div>
        <h4 class="q-my-none">Daftar Transaksi</h4>
        <p class="text-grey-6 q-my-none">Kelola dan lihat semua transaksi parkir</p>
      </div>
      <div class="q-gutter-sm">
        <q-btn
          color="primary"
          icon="refresh"
          label="Refresh"
          @click="refreshData"
          :loading="loading"
        />
        <q-btn
          color="purple"
          icon="science"
          label="Add Test Data"
          @click="addTestData"
          v-if="isAdmin"
        />
        <q-btn
          color="orange"
          icon="exit_to_app"
          label="Process Exit All"
          @click="processExitAll"
          v-if="isAdmin"
        />
        <q-btn
          color="green"
          icon="download"
          label="Export"
          @click="exportData"
        />
        <q-btn
          color="grey-8"
          icon="home"
          label="Kembali"
          to="/"
        />
      </div>
    </div>

    <!-- Filter Section -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="row q-gutter-md items-end">
          <div class="col-md-2 col-xs-12">
            <q-input
              v-model="filters.platNomor"
              label="Plat Nomor"
              outlined
              dense
              clearable
              @update:model-value="debouncedFilterChange"
              placeholder="Masukkan plat nomor..."
            />
          </div>
          <div class="col-md-2 col-xs-12">
            <q-select
              v-model="filters.status"
              :options="statusOptions"
              label="Status"
              outlined
              dense
              clearable
              emit-value
              map-options
              @update:model-value="onFilterChange"
            />
          </div>
          <div class="col-md-2 col-xs-12">
            <q-input
              v-model="filters.tanggalMulai"
              label="Tanggal Mulai"
              type="date"
              outlined
              dense
              @update:model-value="onFilterChange"
            />
          </div>
          <div class="col-md-2 col-xs-12">
            <q-input
              v-model="filters.tanggalAkhir"
              label="Tanggal Akhir"
              type="date"
              outlined
              dense
              @update:model-value="onFilterChange"
            />
          </div>
          <div class="col-md-2 col-xs-12">
            <q-select
              v-model="filters.jenisKendaraan"
              :options="jenisKendaraanOptions"
              label="Jenis Kendaraan"
              outlined
              dense
              clearable
              emit-value
              map-options
              @update:model-value="onFilterChange"
            />
          </div>
          <div class="col-md-2 col-xs-12">
            <q-btn
              color="negative"
              icon="clear"
              label="Clear"
              @click="clearFilters"
              outline
              :disable="!hasActiveFilters"
            />
            <q-badge 
              v-if="hasActiveFilters" 
              color="red" 
              floating 
              rounded
            >
              {{ activeFilterCount }}
            </q-badge>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Statistics Cards -->
    <div class="row q-gutter-md q-mb-md">
      <div class="col">
        <q-card class="bg-blue-1">
          <q-card-section class="text-center">
            <div class="text-h4 text-blue">
              <q-skeleton v-if="statsLoading" type="text" width="60px" />
              <span v-else>{{ displayStatistics.totalTransaksi || 0 }}</span>
            </div>
            <div class="text-caption text-blue-8">Total Transaksi</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col">
        <q-card class="bg-green-1">
          <q-card-section class="text-center">
            <div class="text-h4 text-green">
              <q-skeleton v-if="statsLoading" type="text" width="60px" />
              <span v-else>{{ displayStatistics.transaksiSelesai || 0 }}</span>
            </div>
            <div class="text-caption text-green-8">Transaksi Selesai</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col">
        <q-card class="bg-orange-1">
          <q-card-section class="text-center">
            <div class="text-h4 text-orange">
              <q-skeleton v-if="statsLoading" type="text" width="60px" />
              <span v-else>{{ displayStatistics.transaksiAktif || 0 }}</span>
            </div>
            <div class="text-caption text-orange-8">Transaksi Aktif</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col">
        <q-card class="bg-purple-1">
          <q-card-section class="text-center">
            <div class="text-h4 text-purple">
              <q-skeleton v-if="statsLoading" type="text" width="80px" />
              <span v-else>{{ formatCurrency(displayStatistics.totalPendapatan || 0) }}</span>
            </div>
            <div class="text-caption text-purple-8">Total Pendapatan</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Data Table -->
    <q-table
      :rows="transaksiList"
      :columns="columns"
      row-key="id"
      :loading="loading"
      :pagination="pagination"
      @request="onRequest"
      binary-state-sort
      :rows-per-page-options="[10, 25, 50, 100]"
      class="my-sticky-header-table"
    >
      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <q-badge
            :color="getStatusColor(props.value)"
            :label="getStatusLabel(props.value)"
          />
        </q-td>
      </template>

      <template v-slot:body-cell-waktu_masuk="props">
        <q-td :props="props">
          {{ formatDateTime(props.value) }}
        </q-td>
      </template>

      <template v-slot:body-cell-waktu_keluar="props">
        <q-td :props="props">
          {{ props.value ? formatDateTime(props.value) : '-' }}
        </q-td>
      </template>

      <template v-slot:body-cell-durasi="props">
        <q-td :props="props">
          {{ calculateDuration(props.row.waktu_masuk, props.row.waktu_keluar) }}
        </q-td>
      </template>

      <template v-slot:body-cell-tarif="props">
        <q-td :props="props">
          {{ formatCurrency(props.value) }}
        </q-td>
      </template>

      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            size="sm"
            color="primary"
            icon="visibility"
            @click="viewDetail(props.row)"
            flat
            round
          >
            <q-tooltip>Lihat Detail</q-tooltip>
          </q-btn>
          <q-btn
            v-if="props.row.status === 0"
            size="sm"
            color="green"
            icon="exit_to_app"
            @click="processExit(props.row)"
            flat
            round
          >
            <q-tooltip>Proses Keluar</q-tooltip>
          </q-btn>
          <q-btn
            size="sm"
            color="orange"
            icon="print"
            @click="printTicket(props.row)"
            flat
            round
          >
            <q-tooltip>Print Tiket</q-tooltip>
          </q-btn>
          <q-btn
            v-if="isAdmin"
            size="sm"
            color="negative"
            icon="delete"
            @click="deleteTransaction(props.row)"
            flat
            round
          >
            <q-tooltip>Hapus</q-tooltip>
          </q-btn>
        </q-td>
      </template>

      <template v-slot:no-data="{ message }">
        <div class="full-width row flex-center text-grey-6 q-gutter-sm">
          <q-icon size="2em" name="sentiment_dissatisfied" />
          <span>{{ message }}</span>
        </div>
      </template>
    </q-table>

    <!-- Detail Dialog -->
    <q-dialog v-model="showDetailDialog" persistent>
      <q-card style="min-width: 600px">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Detail Transaksi</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section v-if="selectedTransaction">
          <div class="row q-gutter-md">
            <div class="col-6">
              <q-list>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>ID Transaksi</q-item-label>
                    <q-item-label>{{ selectedTransaction.id }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Plat Nomor</q-item-label>
                    <q-item-label class="text-h6 text-primary">{{ selectedTransaction.plat_nomor }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Jenis Kendaraan</q-item-label>
                    <q-item-label>{{ selectedTransaction.jenis_kendaraan }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Status</q-item-label>
                    <q-item-label>
                      <q-badge
                        :color="getStatusColor(selectedTransaction.status)"
                        :label="getStatusLabel(selectedTransaction.status)"
                      />
                    </q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Petugas</q-item-label>
                    <q-item-label>{{ selectedTransaction.petugas || '-' }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
            <div class="col-6">
              <q-list>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Waktu Masuk</q-item-label>
                    <q-item-label>{{ formatDateTime(selectedTransaction.waktu_masuk) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Waktu Keluar</q-item-label>
                    <q-item-label>{{ selectedTransaction.waktu_keluar ? formatDateTime(selectedTransaction.waktu_keluar) : '-' }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Durasi</q-item-label>
                    <q-item-label>{{ calculateDuration(selectedTransaction.waktu_masuk, selectedTransaction.waktu_keluar) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Tarif</q-item-label>
                    <q-item-label class="text-h6 text-green">{{ formatCurrency(selectedTransaction.tarif) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Lokasi</q-item-label>
                    <q-item-label>{{ selectedTransaction.lokasi || '-' }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>

          <!-- Images Section -->
          <div v-if="selectedTransaction.pic_plat_masuk || selectedTransaction.pic_body_masuk" class="q-mt-md">
            <q-separator class="q-mb-md" />
            <div class="text-subtitle2 q-mb-md">Foto Masuk</div>
            <div class="row q-gutter-md">
              <div v-if="selectedTransaction.pic_plat_masuk" class="col">
                <div class="text-caption q-mb-xs">Foto Plat Masuk</div>
                <q-img
                  :src="selectedTransaction.pic_plat_masuk"
                  style="height: 200px; width: 300px"
                  class="rounded-borders cursor-pointer"
                  @click="showImage(selectedTransaction.pic_plat_masuk)"
                />
              </div>
              <div v-if="selectedTransaction.pic_body_masuk" class="col">
                <div class="text-caption q-mb-xs">Foto Kendaraan Masuk</div>
                <q-img
                  :src="selectedTransaction.pic_body_masuk"
                  style="height: 200px; width: 300px"
                  class="rounded-borders cursor-pointer"
                  @click="showImage(selectedTransaction.pic_body_masuk)"
                />
              </div>
            </div>
          </div>

          <div v-if="selectedTransaction.pic_plat_keluar || selectedTransaction.pic_body_keluar" class="q-mt-md">
            <div class="text-subtitle2 q-mb-md">Foto Keluar</div>
            <div class="row q-gutter-md">
              <div v-if="selectedTransaction.pic_plat_keluar" class="col">
                <div class="text-caption q-mb-xs">Foto Plat Keluar</div>
                <q-img
                  :src="selectedTransaction.pic_plat_keluar"
                  style="height: 200px; width: 300px"
                  class="rounded-borders cursor-pointer"
                  @click="showImage(selectedTransaction.pic_plat_keluar)"
                />
              </div>
              <div v-if="selectedTransaction.pic_body_keluar" class="col">
                <div class="text-caption q-mb-xs">Foto Kendaraan Keluar</div>
                <q-img
                  :src="selectedTransaction.pic_body_keluar"
                  style="height: 200px; width: 300px"
                  class="rounded-borders cursor-pointer"
                  @click="showImage(selectedTransaction.pic_body_keluar)"
                />
              </div>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn
            color="orange"
            icon="print"
            label="Print Tiket"
            @click="printTicket(selectedTransaction)"
          />
          <q-btn flat label="Tutup" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Image Dialog -->
    <q-dialog v-model="showImageModal">
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section>
          <q-img
            :src="selectedImage"
            style="max-width: 80vw; max-height: 80vh"
            class="rounded-borders"
          />
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Exit Processing Dialog -->
    <q-dialog v-model="showExitDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section class="row items-center">
          <q-avatar icon="exit_to_app" color="green" text-color="white" />
          <span class="q-ml-sm">Proses kendaraan keluar untuk plat nomor <strong>{{ exitTransaction?.plat_nomor }}</strong>?</span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Batal" color="primary" v-close-popup />
          <q-btn
            label="Proses Keluar"
            color="green"
            @click="confirmExit"
            :loading="processing"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useQuasar } from 'quasar'
import { useTransaksiStore } from 'src/stores/transaksi-store'
import ls from 'localstorage-slim'

// Utility function for date formatting (alternative to date-fns)
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('id-ID', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const $q = useQuasar()
const transaksiStore = useTransaksiStore()

// Debounce timer
let filterTimer = null

// Reactive data
const loading = ref(false)
const statsLoading = ref(false)
const processing = ref(false)
const transaksiList = ref([])
const selectedTransaction = ref(null)
const selectedImage = ref('')
const exitTransaction = ref(null)
const showDetailDialog = ref(false)
const showImageModal = ref(false)
const showExitDialog = ref(false)

// Computed statistics based on current filtered data
const computedStatistics = computed(() => {
  if (!transaksiList.value.length) {
    return {
      totalTransaksi: 0,
      transaksiSelesai: 0,
      transaksiAktif: 0,
      totalPendapatan: 0
    }
  }

  const totalTransaksi = pagination.value.rowsNumber || transaksiList.value.length
  const selesai = transaksiList.value.filter(t => t.status === 1).length
  const aktif = transaksiList.value.filter(t => t.status === 0).length
  const pendapatan = transaksiList.value
    .filter(t => t.status === 1)
    .reduce((total, t) => total + (t.tarif || 0), 0)

  return {
    totalTransaksi,
    transaksiSelesai: selesai,
    transaksiAktif: aktif,
    totalPendapatan: pendapatan
  }
})

// Filters
const filters = ref({
  platNomor: '',
  status: null,
  tanggalMulai: '',
  tanggalAkhir: '',
  jenisKendaraan: null
})

// Pagination
const pagination = ref({
  sortBy: 'waktu_masuk',
  descending: true,
  page: 1,
  rowsPerPage: 25,
  rowsNumber: 0
})

// Statistics
const statistics = ref({
  totalTransaksi: 0,
  transaksiSelesai: 0,
  transaksiAktif: 0,
  totalPendapatan: 0
})

// Options
const statusOptions = [
  { label: 'Aktif (Belum Keluar)', value: 0 },
  { label: 'Selesai', value: 1 },
  { label: 'Dibatalkan', value: 2 }
]

const jenisKendaraanOptions = [
  { label: 'Mobil', value: 'Mobil' },
  { label: 'Motor', value: 'Motor' },
  { label: 'Truck/Box', value: 'Truck/Box' }
]

// Table columns
const columns = [
  {
    name: 'id',
    required: true,
    label: 'ID',
    align: 'left',
    field: 'id',
    sortable: true,
    style: 'width: 80px'
  },
  {
    name: 'plat_nomor',
    required: true,
    label: 'Plat Nomor',
    align: 'left',
    field: 'plat_nomor',
    sortable: true,
    style: 'width: 120px'
  },
  {
    name: 'jenis_kendaraan',
    label: 'Jenis Kendaraan',
    align: 'left',
    field: 'jenis_kendaraan',
    sortable: true
  },
  {
    name: 'waktu_masuk',
    label: 'Waktu Masuk',
    align: 'left',
    field: 'waktu_masuk',
    sortable: true,
    style: 'width: 160px'
  },
  {
    name: 'waktu_keluar',
    label: 'Waktu Keluar',
    align: 'left',
    field: 'waktu_keluar',
    sortable: true,
    style: 'width: 160px'
  },
  {
    name: 'durasi',
    label: 'Durasi',
    align: 'left',
    field: row => calculateDuration(row.waktu_masuk, row.waktu_keluar),
    style: 'width: 100px'
  },
  {
    name: 'tarif',
    label: 'Tarif',
    align: 'right',
    field: 'tarif',
    sortable: true,
    style: 'width: 100px'
  },
  {
    name: 'status',
    label: 'Status',
    align: 'center',
    field: 'status',
    sortable: true,
    style: 'width: 100px'
  },
  {
    name: 'petugas',
    label: 'Petugas',
    align: 'left',
    field: 'petugas',
    sortable: true
  },
  {
    name: 'actions',
    label: 'Aksi',
    align: 'center',
    field: '',
    style: 'width: 150px'
  }
]

// Methods
const loadTransaksi = async (props = {}) => {
  loading.value = true
  try {
    const { page = pagination.value.page, rowsPerPage = pagination.value.rowsPerPage, sortBy, descending } = props.pagination || {}
    
    // Build filter parameters - make sure to clean empty values
    const filterParams = {
      page,
      limit: rowsPerPage,
      sortBy: sortBy || pagination.value.sortBy,
      sortOrder: (descending !== undefined ? descending : pagination.value.descending) ? 'desc' : 'asc',
      // Clean filter values
      platNomor: filters.value.platNomor?.trim() || '',
      status: filters.value.status,
      tanggalMulai: filters.value.tanggalMulai || '',
      tanggalAkhir: filters.value.tanggalAkhir || '',
      jenisKendaraan: filters.value.jenisKendaraan || ''
    }

    console.log('🔍 Loading transaksi with filterParams:', filterParams)
    console.log('🔍 Current filters.value:', filters.value)

    const result = await transaksiStore.getAllTransaksi(filterParams)
    
    transaksiList.value = result.data || []
    pagination.value.page = page
    pagination.value.rowsPerPage = rowsPerPage
    pagination.value.sortBy = sortBy || pagination.value.sortBy
    pagination.value.descending = descending !== undefined ? descending : pagination.value.descending
    pagination.value.rowsNumber = result.total || 0

    console.log('Loaded transaksi:', transaksiList.value.length, 'total:', result.total)

    // Update statistics with same filters (excluding pagination)
    await loadStatistics()
  } catch (error) {
    console.error('Error loading transaksi:', error)
    $q.notify({
      type: 'negative',
      message: 'Gagal memuat data transaksi',
      position: 'top'
    })
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    statsLoading.value = true
    // Use same filters as main query but without pagination - clean empty values
    const statsParams = {
      platNomor: filters.value.platNomor?.trim() || '',
      status: filters.value.status,
      tanggalMulai: filters.value.tanggalMulai || '',
      tanggalAkhir: filters.value.tanggalAkhir || '',
      jenisKendaraan: filters.value.jenisKendaraan || ''
    }
    
    console.log('📊 Loading statistics with filters:', statsParams)
    const stats = await transaksiStore.getTransaksiStatistics(statsParams)
    console.log('📊 Loaded statistics:', stats)
    statistics.value = stats
  } catch (error) {
    console.error('Error loading statistics:', error)
    // Set default values on error
    statistics.value = {
      totalTransaksi: 0,
      transaksiSelesai: 0,
      transaksiAktif: 0,
      totalPendapatan: 0
    }
  } finally {
    statsLoading.value = false
  }
}

const onRequest = (props) => {
  loadTransaksi(props)
}

const onFilterChange = () => {
  console.log('🔍 Filter changed:', filters.value)
  // Clear existing timer
  if (filterTimer) {
    clearTimeout(filterTimer)
  }
  
  // Reset to first page when filtering
  pagination.value.page = 1
  
  // Apply filter immediately for non-text fields or call debounced for text
  loadTransaksi()
}

const debouncedFilterChange = () => {
  console.log('🔍 Debounced filter change for plat nomor:', filters.value.platNomor)
  // Clear existing timer
  if (filterTimer) {
    clearTimeout(filterTimer)
  }
  
  // Set new timer
  filterTimer = setTimeout(() => {
    pagination.value.page = 1
    loadTransaksi()
  }, 500) // 500ms delay for text input
}

const clearFilters = () => {
  filters.value = {
    platNomor: '',
    status: null,
    tanggalMulai: '',
    tanggalAkhir: '',
    jenisKendaraan: null
  }
  onFilterChange()
}

const refreshData = () => {
  console.log('Refreshing data with current filters:', filters.value)
  loadTransaksi()
}

const viewDetail = (transaction) => {
  selectedTransaction.value = transaction
  showDetailDialog.value = true
}

const showImage = (imageSrc) => {
  selectedImage.value = imageSrc
  showImageModal.value = true
}

const processExit = (transaction) => {
  exitTransaction.value = transaction
  showExitDialog.value = true
}

const confirmExit = async () => {
  processing.value = true
  try {
    await transaksiStore.processManualExit(exitTransaction.value.id)
    $q.notify({
      type: 'positive',
      message: 'Kendaraan berhasil diproses keluar',
      position: 'top'
    })
    showExitDialog.value = false
    refreshData()
  } catch (error) {
    console.error('Error processing exit:', error)
    $q.notify({
      type: 'negative',
      message: 'Gagal memproses kendaraan keluar',
      position: 'top'
    })
  } finally {
    processing.value = false
  }
}

const deleteTransaction = async (transaction) => {
  $q.dialog({
    title: 'Konfirmasi Hapus',
    message: `Apakah Anda yakin ingin menghapus transaksi untuk plat nomor ${transaction.plat_nomor}?`,
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      await transaksiStore.deleteTransaction(transaction.id)
      $q.notify({
        type: 'positive',
        message: 'Transaksi berhasil dihapus',
        position: 'top'
      })
      refreshData()
    } catch (error) {
      console.error('Error deleting transaction:', error)
      $q.notify({
        type: 'negative',
        message: 'Gagal menghapus transaksi',
        position: 'top'
      })
    }
  })
}

const printTicket = (transaction) => {
  // Implement print functionality
  transaksiStore.printTicket(transaction)
}

const exportData = async () => {
  try {
    loading.value = true
    await transaksiStore.exportTransaksi(filters.value)
    $q.notify({
      type: 'positive',
      message: 'Data berhasil diekspor',
      position: 'top'
    })
  } catch (error) {
    console.error('Error exporting data:', error)
    $q.notify({
      type: 'negative',
      message: 'Gagal mengekspor data',
      position: 'top'
    })
  } finally {
    loading.value = false
  }
}

const addTestData = async () => {
  try {
    console.log('🧪 Adding test data with revenue...')
    
    // Use the store function if available, otherwise use direct approach
    if (transaksiStore.addSampleDataForTesting) {
      await transaksiStore.addSampleDataForTesting()
    } else {
      // Direct database access as fallback
      const { localDbs } = await import('src/boot/pouchdb')
      const db = localDbs.transactions
      
      const testTransactions = [
        {
          _id: `transaction_${Date.now()}_1`,
          type: 'parking_transaction',
          id: `${Date.now()}_1`,
          no_pol: 'B1234TEST',
          id_kendaraan: 1,
          status: 1, // Completed
          id_pintu_masuk: '01',
          id_pintu_keluar: '01',
          waktu_masuk: new Date(Date.now() - 4 * 3600000).toISOString(),
          waktu_keluar: new Date(Date.now() - 30 * 60000).toISOString(),
          id_op_masuk: 'ADMIN',
          id_op_keluar: 'ADMIN',
          id_shift_masuk: 'SHIFT1',
          id_shift_keluar: 'SHIFT1',
          kategori: 'UMUM',
          status_transaksi: '0',
          jenis_system: 'MANUAL',
          tanggal: new Date().toISOString().split('T')[0],
          bayar_masuk: 0,
          bayar_keluar: 20000, // 4 hours * 5000
          sinkron: 0,
          upload: 0,
          manual: 1,
          veri_check: 0
        },
        {
          _id: `transaction_${Date.now()}_2`,
          type: 'parking_transaction',
          id: `${Date.now()}_2`,
          no_pol: 'B5678TEST',
          id_kendaraan: 2,
          status: 1, // Completed
          id_pintu_masuk: '01',
          id_pintu_keluar: '01',
          waktu_masuk: new Date(Date.now() - 3 * 3600000).toISOString(),
          waktu_keluar: new Date(Date.now() - 15 * 60000).toISOString(),
          id_op_masuk: 'ADMIN',
          id_op_keluar: 'ADMIN',
          id_shift_masuk: 'SHIFT1',
          id_shift_keluar: 'SHIFT1',
          kategori: 'UMUM',
          status_transaksi: '0',
          jenis_system: 'MANUAL',
          tanggal: new Date().toISOString().split('T')[0],
          bayar_masuk: 0,
          bayar_keluar: 6000, // 3 hours * 2000
          sinkron: 0,
          upload: 0,
          manual: 1,
          veri_check: 0
        }
      ]
      
      for (const transaction of testTransactions) {
        await db.put(transaction)
      }
    }
    
    $q.notify({
      type: 'positive',
      message: 'Test data dengan revenue berhasil ditambahkan (Total: Rp 26,000)',
      position: 'top'
    })
    
    console.log('✅ Expected total revenue: Rp 26,000 (20,000 + 6,000)')
    
    // Refresh the data
    refreshData()
  } catch (error) {
    console.error('Error adding test data:', error)
    $q.notify({
      type: 'negative',
      message: 'Gagal menambahkan test data: ' + error.message,
      position: 'top'
    })
  }
}

const processExitAll = async () => {
  try {
    console.log('🚪 Processing exit for all active transactions...')
    
    if (transaksiStore.processExitAllActiveTransactions) {
      const processedCount = await transaksiStore.processExitAllActiveTransactions()
      
      $q.notify({
        type: 'positive',
        message: `Berhasil memproses keluar ${processedCount} transaksi aktif`,
        position: 'top'
      })
    } else {
      $q.notify({
        type: 'warning',
        message: 'Fungsi tidak tersedia',
        position: 'top'
      })
    }
    
    // Refresh the data
    refreshData()
  } catch (error) {
    console.error('Error processing exit all:', error)
    $q.notify({
      type: 'negative',
      message: 'Gagal memproses keluar transaksi: ' + error.message,
      position: 'top'
    })
  }
}

// Utility functions
const formatDateTime = (dateTime) => {
  return formatDate(dateTime)
}

const formatCurrency = (amount) => {
  if (!amount) return 'Rp 0'
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount)
}

const calculateDuration = (masuk, keluar) => {
  if (!masuk) return '-'
  if (!keluar) return 'Sedang parkir'
  
  const start = new Date(masuk)
  const end = new Date(keluar)
  const diffMs = end - start
  
  const hours = Math.floor(diffMs / (1000 * 60 * 60))
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
  
  if (hours > 0) {
    return `${hours}j ${minutes}m`
  } else {
    return `${minutes}m`
  }
}

const getStatusColor = (status) => {
  switch (status) {
    case 0: return 'orange'
    case 1: return 'green'
    case 2: return 'red'
    default: return 'grey'
  }
}

const getStatusLabel = (status) => {
  switch (status) {
    case 0: return 'Aktif'
    case 1: return 'Selesai'
    case 2: return 'Dibatalkan'
    default: return 'Unknown'
  }
}

const isAdmin = computed(() => ls.get('isAdmin') || false)

// Computed for active filters
const hasActiveFilters = computed(() => {
  return !!(
    filters.value.platNomor?.trim() ||
    filters.value.status !== null ||
    filters.value.tanggalMulai ||
    filters.value.tanggalAkhir ||
    filters.value.jenisKendaraan
  )
})

const activeFilterCount = computed(() => {
  let count = 0
  if (filters.value.platNomor?.trim()) count++
  if (filters.value.status !== null) count++
  if (filters.value.tanggalMulai) count++
  if (filters.value.tanggalAkhir) count++
  if (filters.value.jenisKendaraan) count++
  return count
})

// Use statistics from store, fallback to computed if needed
const displayStatistics = computed(() => {
  if (statsLoading.value) {
    return statistics.value
  }
  
  // If we have statistics from store, use them, otherwise use computed
  if (statistics.value.totalTransaksi > 0 || 
      statistics.value.transaksiSelesai > 0 || 
      statistics.value.transaksiAktif > 0 || 
      statistics.value.totalPendapatan > 0) {
    return statistics.value
  }
  
  return computedStatistics.value
})

// Lifecycle
onMounted(() => {
  console.log('🚀 Component mounted, loading data...')
  
  // Don't set default dates - let user choose
  // This prevents unwanted filtering on first load
  console.log('🔍 Initial filters:', filters.value)
  
  loadTransaksi()
})
</script>

<style scoped>
.my-sticky-header-table {
  /* height or max-height is important */
  height: 70vh;
}

.my-sticky-header-table .q-table__top,
.my-sticky-header-table .q-table__bottom,
.my-sticky-header-table thead tr:first-child th {
  /* bg color is important for th; just specify one */
  background-color: white;
}

.my-sticky-header-table thead tr th {
  position: sticky;
  z-index: 1;
}

.my-sticky-header-table thead tr:first-child th {
  top: 0;
}

/* this is when the loading indicator appears */
.my-sticky-header-table.q-table--loading thead tr:last-child th {
  /* height of all previous header rows */
  top: 48px;
}

.cursor-pointer {
  cursor: pointer;
}

.cursor-pointer:hover {
  opacity: 0.8;
}
</style>
