<template>
  <div class="q-pa-md">
    <!-- Header -->
    <div class="row items-center justify-between q-mb-md">
      <div>
        <h4 class="q-my-none">Daftar Transaksi</h4>
        <p class="text-grey-6 q-my-none">
          Kelola dan lihat semua transaksi parkir
          <span v-if="loading" class="text-orange-6">
            <q-spinner-dots size="sm" class="q-ml-sm" />
            Memuat...
          </span>
         
        </p>
      </div>
      <div class="q-gutter-sm">
        <q-btn
          :color="isListeningToChanges ? 'green' : 'grey'"
          :icon="isListeningToChanges ? 'sync' : 'sync_disabled'"
          :label="isListeningToChanges ? 'Auto-sync ON' : 'Auto-sync OFF'"
          @click="toggleAutoSync"
          outline
          size="sm"
        >
          <q-tooltip>
            {{ isListeningToChanges ? 'Matikan auto-sync' : 'Aktifkan auto-sync' }}
          </q-tooltip>
        </q-btn>
        <q-btn
          color="primary"
          icon="refresh"
          label="Refresh"
          @click="refreshData"
          :loading="loading"
          :disable="loading"
        />
        <!-- <q-btn
          color="blue"
          icon="bug_report"
          label="Debug DB"
          @click="debugDatabase"
          v-if="isAdmin"
        /> -->
        <!-- <q-btn
          color="purple"
          icon="science"
          label="Add Test Data"
          @click="addTestData"
          v-if="isAdmin"
          :disable="loading"
        /> -->
        <q-btn
          color="orange"
          icon="exit_to_app"
          label="Process Exit All"
          @click="processExitAll"
          v-if="isAdmin"
          :disable="loading"
        />
        <q-btn
          color="green"
          icon="download"
          label="Export"
          @click="exportData"
          :disable="loading"
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
            <q-select
              v-model="filters.isMember"
              :options="memberOptions"
              label="Tipe Transaksi"
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
              <q-skeleton v-if="statsLoading || loading" type="text" width="60px" />
              <span v-else>{{ displayStatistics.totalTransaksi || 0 }}</span>
            </div>
            <div class="text-caption text-blue-8">Total Transaksi</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col">
        <q-card class="bg-purple-1">
          <q-card-section class="text-center">
            <div class="text-h4 text-purple">
              <q-skeleton v-if="statsLoading || loading" type="text" width="60px" />
              <span v-else>{{ displayStatistics.transaksiMember || 0 }}</span>
            </div>
            <div class="text-caption text-purple-8">Transaksi Member</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col">
        <q-card class="bg-indigo-1">
          <q-card-section class="text-center">
            <div class="text-h4 text-indigo">
              <q-skeleton v-if="statsLoading || loading" type="text" width="60px" />
              <span v-else>{{ displayStatistics.transaksiUmum || 0 }}</span>
            </div>
            <div class="text-caption text-indigo-8">Transaksi Umum</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col">
        <q-card class="bg-green-1">
          <q-card-section class="text-center">
            <div class="text-h4 text-green">
              <q-skeleton v-if="statsLoading || loading" type="text" width="60px" />
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
              <q-skeleton v-if="statsLoading || loading" type="text" width="60px" />
              <span v-else>{{ displayStatistics.transaksiAktif || 0 }}</span>
            </div>
            <div class="text-caption text-orange-8">Transaksi Aktif</div>
          </q-card-section>
        </q-card>
      </div>
      <div class="col">
        <q-card class="bg-teal-1">
          <q-card-section class="text-center">
            <div class="text-h4 text-teal">
              <q-skeleton v-if="statsLoading || loading" type="text" width="80px" />
              <span v-else>{{ formatCurrency(displayStatistics.totalPendapatan || 0) }}</span>
            </div>
            <div class="text-caption text-teal-8">Total Pendapatan</div>
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
      loading-label="Memuat data transaksi..."
      no-data-label="Tidak ada data transaksi"
    >
      <template v-slot:body-cell-member_status="props">
        <q-td :props="props">
          <q-badge
            :color="props.value ? 'purple' : 'blue-grey'"
            :label="props.value ? 'Member' : 'Umum'"
            :icon="props.value ? 'card_membership' : 'person'"
          />
        </q-td>
      </template>

      <template v-slot:body-cell-images="props">
        <q-td :props="props">
          <div class="q-gutter-xs">
            <q-btn
              v-if="hasImages(props.row)"
              round
              flat
              dense
              color="primary"
              icon="photo_library"
              @click="viewDetail(props.row)"
            >
              <q-tooltip>
                {{ getImageCount(props.row) }} Foto
              </q-tooltip>
            </q-btn>
            <q-btn
              v-else
              round
              flat
              dense
              color="grey"
              icon="no_photography"
              disable
            >
              <q-tooltip>
                Tidak ada foto
              </q-tooltip>
            </q-btn>
          </div>
        </q-td>
      </template>

      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <q-badge
            :color="getStatusColor(props.value)"
            :label="getStatusLabel(props.value)"
          />
        </q-td>
      </template>

      <template v-slot:body-cell-entry_time="props">
        <q-td :props="props">
          {{ formatDateTime(getEntryTime(props.row)) }}
        </q-td>
      </template>

      <template v-slot:body-cell-waktu_keluar="props">
        <q-td :props="props">
          {{ getExitTime(props.row) ? formatDateTime(getExitTime(props.row)) : '-' }}
        </q-td>
      </template>

      <template v-slot:body-cell-durasi="props">
        <q-td :props="props">
          {{ calculateDuration(getEntryTime(props.row), getExitTime(props.row)) }}
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
            v-if="props.row.status === 0 || props.row.status === 'in'"
            size="sm"
            color="green"
            icon="exit_to_app"
            @click="processExit(props.row)"
            flat
            round
          >
            <q-tooltip>Proses Keluar {{ props.row.type === 'member_entry' ? 'Member' : 'Parkir' }}</q-tooltip>
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
        <div class="full-width row flex-center text-grey-6 q-gutter-sm q-pa-xl">
          <div class="text-center">
            <q-icon size="3em" name="sentiment_neutral" class="q-mb-md" />
            <div class="text-h6 q-mb-sm">
              {{ hasActiveFilters ? 'Tidak ada data yang sesuai filter' : 'Belum ada transaksi' }}
            </div>
            <div class="text-body2 text-grey-5">
              {{ hasActiveFilters 
                ? 'Coba ubah atau hapus filter untuk melihat lebih banyak data'
                : 'Transaksi akan muncul di sini setelah ada kendaraan yang masuk'
              }}
            </div>
            <q-btn 
              v-if="hasActiveFilters"
              flat 
              color="primary" 
              label="Hapus Filter" 
              icon="clear_all"
              class="q-mt-md"
              @click="clearFilters"
            />
          </div>
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
                    <q-item-label class="text-h6 text-primary">{{ getPlateNumber(selectedTransaction) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="selectedTransaction?.type === 'member_entry'">
                  <q-item-section>
                    <q-item-label caption>Nama Member</q-item-label>
                    <q-item-label>{{ selectedTransaction.name || '-' }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item v-if="selectedTransaction?.type === 'member_entry'">
                  <q-item-section>
                    <q-item-label caption>Card Number</q-item-label>
                    <q-item-label>{{ selectedTransaction.card_number || '-' }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Jenis Kendaraan</q-item-label>
                    <q-item-label>{{ getVehicleType(selectedTransaction) }}</q-item-label>
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
                    <q-item-label>{{ selectedTransaction.petugas || selectedTransaction.created_by || '-' }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
            <div class="col-6">
              <q-list>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Waktu Masuk</q-item-label>
                    <q-item-label>{{ formatDateTime(getEntryTime(selectedTransaction)) }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Waktu Keluar</q-item-label>
                    <q-item-label>{{ getExitTime(selectedTransaction) ? formatDateTime(getExitTime(selectedTransaction)) : '-' }}</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>Durasi</q-item-label>
                    <q-item-label>{{ calculateDuration(getEntryTime(selectedTransaction), getExitTime(selectedTransaction)) }}</q-item-label>
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
          <!-- Images Section -->
<div v-if="hasImages(selectedTransaction)" class="q-mt-md">
  <q-separator class="q-mb-md" />
  
  <!-- Header dengan informasi gambar -->
  <div class="row items-center justify-between q-mb-md">
    <div class="text-h6">Foto CCTV</div>
    <div class="text-caption">Total: {{ getImageCount(selectedTransaction) }} foto</div>
  </div>

  <!-- List semua gambar -->
  <div class="row q-col-gutter-md">
    <div 
      v-for="(image, index) in getImageList(selectedTransaction)" 
      :key="index"
      class="col-12 col-md-6"
    >
      <q-card class="image-card cursor-pointer" @click="showImage('', image)">
        <q-card-section>
          <div class="text-subtitle2 q-mb-sm">{{ image.label }}</div>
          <q-img
            :src="image.src"
            style="height: 200px"
            fit="contain"
            class="rounded-borders"
            spinner-color="primary"
            spinner-size="lg"
          >
            <template v-slot:loading>
              <div class="text-subtitle1 text-grey-6">
                Memuat gambar...
              </div>
            </template>
            <template v-slot:error>
              <div class="text-subtitle1 text-grey-6">
                Gagal memuat gambar
              </div>
            </template>
          </q-img>
        </q-card-section>
      </q-card>
    </div>
  </div>
</div>

<!-- Info jika tidak ada gambar -->
<div v-if="!hasImages(selectedTransaction)" class="text-center q-pa-lg">
  <q-icon name="no_photography" size="lg" color="grey-5" />
  <div class="text-caption text-grey-6 q-mt-sm">
    Tidak ada foto tersedia
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
    <q-dialog v-model="showImageModal" maximized>
      <q-card class="bg-black">
        <q-card-section class="row items-center justify-between q-pa-md bg-dark text-white">
          <div class="text-h6">
            <q-icon name="photo" class="q-mr-sm" />
            Preview Gambar CCTV
          </div>
          <div class="q-gutter-sm">
            <q-btn 
              v-if="getImageList(selectedTransaction).length > 1"
              icon="navigate_before" 
              flat 
              round 
              dense 
              @click="navigateImage(-1)"
              :disable="currentImageIndex === 0"
            >
              <q-tooltip>Gambar Sebelumnya</q-tooltip>
            </q-btn>
            <q-chip 
              v-if="getImageList(selectedTransaction).length > 1"
              color="blue" 
              text-color="white"
              size="sm"
            >
              {{ currentImageIndex + 1 }} / {{ getImageList(selectedTransaction).length }}
            </q-chip>
            <q-btn 
              v-if="getImageList(selectedTransaction).length > 1"
              icon="navigate_next" 
              flat 
              round 
              dense 
              @click="navigateImage(1)"
              :disable="currentImageIndex === getImageList(selectedTransaction).length - 1"
            >
              <q-tooltip>Gambar Selanjutnya</q-tooltip>
            </q-btn>
            <q-btn icon="close" flat round dense v-close-popup>
              <q-tooltip>Tutup</q-tooltip>
            </q-btn>
          </div>
        </q-card-section>
        
        <q-card-section class="flex flex-center q-pa-none" style="height: calc(100vh - 80px)">
          <div class="text-center full-width">
            <!-- Image info -->
            <div class="text-white q-mb-md">
              <div class="text-subtitle1 text-weight-medium">
                {{ getCurrentImageInfo() }}
              </div>
              <div class="text-caption text-grey-4">
                Plat Nomor: {{ getPlateNumber(selectedTransaction) }} | 
                {{ getEntryTime(selectedTransaction) ? formatDateTime(getEntryTime(selectedTransaction)) : '' }}
              </div>
            </div>
            
            <!-- Main image -->
            <q-img
              :src="selectedImage"
              style="max-width: 90vw; max-height: 80vh"
              class="rounded-borders"
              fit="contain"
              spinner-color="white"
              spinner-size="lg"
            >
              <template v-slot:error>
                <div class="absolute-full flex flex-center bg-grey-8 text-white">
                  <div class="text-center">
                    <q-icon name="broken_image" size="xl" />
                    <div class="text-h6 q-mt-md">Gambar tidak dapat dimuat</div>
                    <div class="text-caption">Periksa koneksi atau file gambar</div>
                  </div>
                </div>
              </template>
            </q-img>
            
            <!-- Navigation thumbnails -->
            <div v-if="getImageList(selectedTransaction).length > 1" class="q-mt-md">
              <div class="row justify-center q-gutter-sm">
                <div 
                  v-for="(image, index) in getImageList(selectedTransaction)" 
                  :key="index"
                  class="cursor-pointer"
                  @click="selectImageByIndex(index)"
                >
                  <q-img
                    :src="image.src"
                    style="width: 80px; height: 60px"
                    class="rounded-borders"
                    :class="currentImageIndex === index ? 'image-selected' : 'image-thumbnail'"
                    fit="cover"
                  >
                    <div v-if="currentImageIndex === index" class="absolute-full bg-primary" style="opacity: 0.3"></div>
                  </q-img>
                  <div class="text-caption text-white q-mt-xs text-center" style="max-width: 80px">
                    {{ image.label }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Exit Processing Dialog -->
    <q-dialog v-model="showExitDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section class="row items-center">
          <q-avatar icon="exit_to_app" color="green" text-color="white" />
          <span class="q-ml-sm">Proses kendaraan keluar untuk plat nomor <strong>{{ getPlateNumber(exitTransaction) }}</strong>?</span>
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
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useTransaksiStore } from 'src/stores/transaksi-store'
import { invoke } from '@tauri-apps/api/core'
import { getTransactionAttachment, remoteDbs, changeHandlers } from 'src/boot/pouchdb'
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
const currentImageIndex = ref(0)
const exitTransaction = ref(null)
const showDetailDialog = ref(false)
const showImageModal = ref(false)
const showExitDialog = ref(false)
const hasInitialized = ref(false)

// Database change listener
const dbChangeListener = ref(null)
const lastRefreshTime = ref(Date.now())
const isListeningToChanges = ref(false)

// Computed statistics based on current filtered data
const computedStatistics = computed(() => {
  console.log("🚀 ~ computedStatistics ~ transaksiList.value:", transaksiList.value)
  if (!transaksiList.value.length) {
    return {
      totalTransaksi: 0,
      transaksiSelesai: 0,
      transaksiAktif: 0,
      totalPendapatan: 0,
      transaksiMember: 0,
      memberSelesai: 0,
      memberAktif: 0,
      transaksiUmum: 0,
      umumSelesai: 0,
      umumAktif: 0
    }
  }

  const totalTransaksi = pagination.value.rowsNumber || transaksiList.value.length
  // Support both legacy string status ('out') and new integer status (1) for completed transactions
  const selesai = transaksiList.value.filter(t => t.status === 1 ).length
  // Support both legacy string status ('in') and new integer status (0) for active transactions
  const aktif = transaksiList.value.filter(t => t.status === 0 ).length
  // Total pendapatan hanya dari transaksi yang sudah selesai (sudah bayar)
  
  // Separate member and regular transactions
  const memberTransactions = transaksiList.value.filter(t => t.type === 'member_entry' || t.is_member === true)
  const regularTransactions = transaksiList.value.filter(t => t.type === 'parking_transaction' && !t.is_member)
  
  // Total pendapatan dari semua transaksi yang tampil sesuai filter
  // Jika user filter status tertentu, maka pendapatan akan sesuai filter tersebut
  // Jika tidak ada filter status, maka pendapatan dari semua transaksi (aktif + selesai)
  const pendapatan = transaksiList.value.reduce((total, t) => total + (t.tarif || 0), 0)
  
  console.log("📊 Perhitungan pendapatan:", {
    totalData: transaksiList.value.length,
    dataWithTarif: transaksiList.value.filter(t => t.tarif > 0).length,
    totalPendapatan: pendapatan,
    detailTarif: transaksiList.value.map(t => ({ id: t.id, status: t.status, tarif: t.tarif }))
  })
  
  // Member transactions: support both legacy ('out'/1) and new integer (1) status
  const memberSelesai = memberTransactions.filter(t => t.status === 1 || t.status === 'out').length
  const memberAktif = memberTransactions.filter(t => t.status === 0 || t.status === 'in').length
  
  const umumSelesai = regularTransactions.filter(t => t.status === 1).length
  const umumAktif = regularTransactions.filter(t => t.status === 0).length

  return {
    totalTransaksi,
    transaksiSelesai: selesai,
    transaksiAktif: aktif,
    totalPendapatan: pendapatan,
    transaksiMember: memberTransactions.length,
    memberSelesai,
    memberAktif,
    transaksiUmum: regularTransactions.length,
    umumSelesai,
    umumAktif
  }
})

// Filters
const filters = ref({
  platNomor: '',
  status: null,
  tanggalMulai: '',
  tanggalAkhir: '',
  jenisKendaraan: null,
  isMember: null
})

// Pagination
const pagination = ref({
  sortBy: 'entry_time',
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
  totalPendapatan: 0,
  transaksiMember: 0,
  memberSelesai: 0,
  memberAktif: 0,
  transaksiUmum: 0,
  umumSelesai: 0,
  umumAktif: 0
})

// Options
const statusOptions = [
  { label: 'Aktif (Belum Keluar)', value: 0 },
  { label: 'Selesai', value: 1 },
  { label: 'Dibatalkan', value: 2 },
  // Legacy member status options (untuk data lama)
  { label: 'Aktif Member (Legacy)', value: 'in' },
  { label: 'Selesai Member (Legacy)', value: 'out' },
  { label: 'Dibatalkan Member (Legacy)', value: 'cancelled' }
]

const jenisKendaraanOptions = [
  { label: 'Mobil', value: 'Mobil' },
  { label: 'Motor', value: 'Motor' },
  { label: 'Truck/Box', value: 'Truck/Box' }
]

const memberOptions = [
  { label: 'Transaksi Member', value: true },
  { label: 'Transaksi Umum', value: false }
]

// Table columns
const getDisplayId = (transaction) => {
  // Tampilkan ID tanpa prefix 'transaction_' jika ada
  const id = transaction._id || transaction.id || ''
  return id.startsWith('transaction_') ? id.replace('transaction_', '') : id
}

const columns = [
  {
    name: 'id',
    required: true,
    label: 'ID',
    align: 'left',
    field: row => getDisplayId(row),
    sortable: true,
    style: 'width: 80px'
  },
  {
    name: 'plat_nomor',
    required: true,
    label: 'Plat Nomor',
    align: 'left',
    field: row => getPlateNumber(row),
    sortable: true,
    style: 'width: 120px'
  },
  {
    name: 'jenis_kendaraan',
    label: 'Jenis Kendaraan',
    align: 'left',
    field: row => getVehicleType(row),
    sortable: true
  },
  {
    name: 'member_status',
    label: 'Tipe',
    align: 'center',
    field: 'is_member',
    style: 'width: 80px'
  },
  {
    name: 'images',
    label: 'Gambar',
    align: 'center',
    field: '',
    style: 'width: 80px'
  },
  {
    name: 'entry_time',
    label: 'Waktu Masuk',
    align: 'left',
    field: row => getEntryTime(row),
    sortable: true,
    style: 'width: 160px'
  },
  {
    name: 'waktu_keluar',
    label: 'Waktu Keluar',
    align: 'left',
    field: row => getExitTime(row),
    sortable: true,
    style: 'width: 160px'
  },
  {
    name: 'durasi',
    label: 'Durasi',
    align: 'left',
    field: row => calculateDuration(getEntryTime(row), getExitTime(row)),
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
const setupDatabaseChangeListener = () => {
  try {
    console.log('🔄 Setting up database change listener for transactions...')
    
    // Setup listener untuk database transaksi
    const transactionsDb = remoteDbs.transactions
    
    if (!transactionsDb) {
      console.warn('⚠️ Transactions database not available')
      return
    }

    // Stop existing listener jika ada
    if (dbChangeListener.value) {
      try {
        dbChangeListener.value.cancel()
      } catch (error) {
        console.warn('Warning canceling previous listener:', error)
      }
    }

    // Setup new change listener
    dbChangeListener.value = transactionsDb.changes({
      since: 'now',
      live: true,
      include_docs: false, // Tidak perlu doc lengkap untuk detect changes
      timeout: false,
      heartbeat: 10000
    })

    dbChangeListener.value
      .on('change', (change) => {
        console.log('📊 Transaction database changed:', {
          id: change.id,
          rev: change.changes[0]?.rev,
          deleted: change.deleted,
          seq: change.seq
        })

        // Debounce refresh untuk menghindari terlalu sering refresh
        const now = Date.now()
        if (now - lastRefreshTime.value > 2000) { // Minimal 2 detik interval
          lastRefreshTime.value = now
          
          // Auto refresh data dengan delay kecil untuk memastikan data sudah tersinkron
          setTimeout(() => {
            console.log('🔄 Auto refreshing data due to database change...')
            refreshDataSilently()
          }, 500)

          // Show notification untuk user
          $q.notify({
            type: 'info',
            message: 'Data transaksi telah diperbarui',
            position: 'top-right',
            timeout: 2000,
            icon: 'sync',
            color: 'blue-5'
          })
        }
      })
      .on('error', (err) => {
        console.error('❌ Database change listener error:', err)
        isListeningToChanges.value = false
        
        // Auto restart listener setelah error
        setTimeout(() => {
          console.log('🔄 Restarting database change listener...')
          setupDatabaseChangeListener()
        }, 5000)
      })
      .on('complete', (info) => {
        console.log('✅ Database change listener completed:', info)
        isListeningToChanges.value = false
      })

    isListeningToChanges.value = true
    console.log('✅ Database change listener setup successfully')
    
  } catch (error) {
    console.error('❌ Failed to setup database change listener:', error)
    isListeningToChanges.value = false
  }
}

const stopDatabaseChangeListener = () => {
  if (dbChangeListener.value) {
    try {
      console.log('🛑 Stopping database change listener...')
      dbChangeListener.value.cancel()
      dbChangeListener.value = null
      isListeningToChanges.value = false
      console.log('✅ Database change listener stopped')
    } catch (error) {
      console.error('❌ Error stopping change listener:', error)
    }
  }
}

const toggleAutoSync = () => {
  if (isListeningToChanges.value) {
    stopDatabaseChangeListener()
    ls.set('daftarTransaksiAutoSync', false)
    $q.notify({
      type: 'info',
      message: 'Auto-sync dimatikan',
      position: 'top-right',
      timeout: 2000,
      icon: 'sync_disabled'
    })
  } else {
    setupDatabaseChangeListener()
    ls.set('daftarTransaksiAutoSync', true)
    $q.notify({
      type: 'positive',
      message: 'Auto-sync diaktifkan',
      position: 'top-right',
      timeout: 2000,
      icon: 'sync'
    })
  }
}

const refreshDataSilently = async () => {
  try {
    // Refresh tanpa loading indicator dan notification untuk auto-refresh
    await refreshData(true)
  } catch (error) {
    console.error('❌ Error in silent refresh:', error)
  }
}

const loadTransaksi = async (props = {}) => {
  try {
    // Prevent concurrent loading
    if (loading.value) {
      console.log('🔄 Loading already in progress, skipping...')
      return
    }
    
    loading.value = true
    
    // DEBUG: Log the initial state
    console.log('🚀 loadTransaksi called with:', props)
    console.log('🚀 Current filters state:', filters.value)
    console.log('🚀 hasActiveFilters:', hasActiveFilters.value)
    
    // Ensure database is ready before loading
    if (!transaksiStore.jenisKendaraan.value || transaksiStore.jenisKendaraan.value.length === 0) {
      console.log('🔧 Initializing vehicle types...')
      await transaksiStore.getJenisKendaraan()
    }
    
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
      jenisKendaraan: filters.value.jenisKendaraan || '',
      isMember: filters.value.isMember
    }

    console.log('🔍 Loading transaksi with filterParams:', filterParams)
    console.log('🔍 Are all filters empty?', {
      platNomor: !filterParams.platNomor,
      status: filterParams.status === null || filterParams.status === undefined,
      tanggalMulai: !filterParams.tanggalMulai,
      tanggalAkhir: !filterParams.tanggalAkhir,
      jenisKendaraan: !filterParams.jenisKendaraan,
      isMember: filterParams.isMember === null || filterParams.isMember === undefined
    })

    // Load transactions with timeout to prevent hanging
    const loadPromise = transaksiStore.getAllTransaksi(filterParams)
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Request timeout')), 30000)
    )
    
    const result = await Promise.race([loadPromise, timeoutPromise])
    
    console.log('🔍 Raw result from store:', result)
    
    // Update state with loaded data
    transaksiList.value = Array.isArray(result.data) ? result.data : []
    pagination.value.page = page
    pagination.value.rowsPerPage = rowsPerPage
    pagination.value.sortBy = sortBy || pagination.value.sortBy
    pagination.value.descending = descending !== undefined ? descending : pagination.value.descending
    pagination.value.rowsNumber = result.total || 0

    console.log('✅ Loaded transaksi:', transaksiList.value.length, 'total:', result.total)
    console.log('✅ Updated transaksiList:', transaksiList.value)

    // Update statistics with same filters (excluding pagination)
    await loadStatistics()
  } catch (error) {
    console.error('❌ Error loading transaksi:', error)
    
    // Set empty state on error
    transaksiList.value = []
    pagination.value.rowsNumber = 0
    
    const errorMessage = error.message === 'Request timeout' 
      ? 'Permintaan timeout, coba lagi' 
      : 'Gagal memuat data transaksi'
    
    $q.notify({
      type: 'negative',
      message: errorMessage,
      position: 'top',
      timeout: 3000
    })
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    // Prevent concurrent statistics loading
    if (statsLoading.value) {
      console.log('📊 Statistics loading already in progress, skipping...')
      return
    }
    
    statsLoading.value = true
    
    // Use same filters as main query but without pagination - clean empty values
    const statsParams = {
      platNomor: filters.value.platNomor?.trim() || '',
      status: filters.value.status,
      tanggalMulai: filters.value.tanggalMulai || '',
      tanggalAkhir: filters.value.tanggalAkhir || '',
      jenisKendaraan: filters.value.jenisKendaraan || '',
      isMember: filters.value.isMember
    }
    
    console.log('📊 Loading statistics with filters:', statsParams)
    
    // Load statistics with timeout
    const statsPromise = transaksiStore.getTransaksiStatistics(statsParams)
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Statistics timeout')), 15000)
    )
    
    const stats = await Promise.race([statsPromise, timeoutPromise])
    console.log('📊 Loaded statistics:', stats)
    
    // Validate stats structure before assigning
    if (stats && typeof stats === 'object') {
      statistics.value = {
        totalTransaksi: stats.totalTransaksi || 0,
        transaksiSelesai: stats.transaksiSelesai || 0,
        transaksiAktif: stats.transaksiAktif || 0,
        totalPendapatan: stats.totalPendapatan || 0,
        transaksiMember: stats.transaksiMember || 0,
        memberSelesai: stats.memberSelesai || 0,
        memberAktif: stats.memberAktif || 0,
        transaksiUmum: stats.transaksiUmum || 0,
        umumSelesai: stats.umumSelesai || 0,
        umumAktif: stats.umumAktif || 0
      }
    } else {
      throw new Error('Invalid statistics response')
    }
  } catch (error) {
    console.error('❌ Error loading statistics:', error)
    
    // Set default values on error
    statistics.value = {
      totalTransaksi: 0,
      transaksiSelesai: 0,
      transaksiAktif: 0,
      totalPendapatan: 0,
      transaksiMember: 0,
      memberSelesai: 0,
      memberAktif: 0,
      transaksiUmum: 0,
      umumSelesai: 0,
      umumAktif: 0
    }
    
    if (error.message !== 'Statistics timeout') {
      $q.notify({
        type: 'warning',
        message: 'Gagal memuat statistik',
        position: 'top',
        timeout: 2000
      })
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
    jenisKendaraan: null,
    isMember: null
  }
  onFilterChange()
}

const refreshData = async (silent = false) => {
  try {
    if (!silent) {
      console.log('🔄 Refreshing data with current filters:', filters.value)
      
      // Show refresh indication
      $q.notify({
        type: 'info',
        message: 'Memuat ulang data...',
        position: 'top',
        timeout: 1000,
        icon: 'refresh'
      })
    }
    
    // Use same logic as onMounted - ensure database is ready
    if (!transaksiStore.jenisKendaraan.value || transaksiStore.jenisKendaraan.value.length === 0) {
      if (!silent) console.log('🔧 Initializing vehicle types during refresh...')
      await transaksiStore.getJenisKendaraan()
    }
    
    await loadTransaksi()
    
    if (!silent) {
      $q.notify({
        type: 'positive',
        message: 'Data berhasil dimuat ulang',
        position: 'top',
        timeout: 2000,
        icon: 'check_circle'
      })
    }
  } catch (error) {
    console.error('❌ Error refreshing data:', error)
    if (!silent) {
      $q.notify({
        type: 'negative',
        message: 'Gagal memuat ulang data',
        position: 'top',
        timeout: 3000,
        icon: 'error'
      })
    }
  }
}

const debugDatabase = async () => {
  try {
    console.log('🔧 Debug: Starting database inspection...')
    
    // Import database directly
    const { remoteDbs } = await import('src/boot/pouchdb')
    const db = remoteDbs.transactions
    
    // Get all documents
    const result = await db.allDocs({
      include_docs: true,
      startkey: 'transaction_',
      endkey: 'transaction_\ufff0'
    })
    
    console.log('🔧 Debug: Total documents in database:', result.rows.length)
    
    // Analyze document types
    const docTypes = {}
    const statusBreakdown = {}
    
    result.rows.forEach(row => {
      const doc = row.doc
      const type = doc.type || 'unknown'
      docTypes[type] = (docTypes[type] || 0) + 1
      
      if (doc.status !== undefined) {
        const status = `${type}_${doc.status}`
        statusBreakdown[status] = (statusBreakdown[status] || 0) + 1
      }
    })
    
    console.log('🔧 Debug: Document types:', docTypes)
    console.log('🔧 Debug: Status breakdown:', statusBreakdown)
    
    // Show first few documents
    const sampleDocs = result.rows.slice(0, 5).map(row => ({
      id: row.doc._id,
      type: row.doc.type,
      status: row.doc.status,
      no_pol: row.doc.no_pol,
      plat_nomor: row.doc.plat_nomor,
      entry_time: row.doc.entry_time,
      tanggal: row.doc.tanggal
    }))
    
    console.log('🔧 Debug: Sample documents:', sampleDocs)
    
    // Test getAllTransaksi with no filters
    console.log('🔧 Debug: Testing getAllTransaksi with no filters...')
    const testResult = await transaksiStore.getAllTransaksi({
      page: 1,
      limit: 50
    })
    
    console.log('🔧 Debug: getAllTransaksi result:', testResult)
    
    $q.notify({
      type: 'info',
      message: `Database contains ${result.rows.length} documents. Check console for details.`,
      position: 'top',
      timeout: 5000
    })
    
  } catch (error) {
    console.error('🔧 Debug error:', error)
    $q.notify({
      type: 'negative',
      message: 'Debug failed: ' + error.message,
      position: 'top'
    })
  }
}

const viewDetail = async (transaction) => {
  selectedTransaction.value = transaction
  showDetailDialog.value = true
  
  // Load attachment images if they exist
  if (transaction._attachments) {
    const imageList = getImageList(transaction)
    
    // Load all images in parallel
    const loadPromises = imageList.map(async (image) => {
      if (image.isAttachment && !image.src) {
        try {
          const attachmentUrl = await loadAttachmentImage(image.transactionId, image.attachmentName)
          if (attachmentUrl) {
            image.src = attachmentUrl
            return { ...image, src: attachmentUrl }
          }
        } catch (error) {
          console.error('Error loading attachment for detail view:', error)
        }
      }
      return image
    })
    
    // Wait for all images to load
    try {
      const loadedImages = await Promise.all(loadPromises)
      // Update the images in the list with their loaded sources
      imageList.forEach((image, index) => {
        if (loadedImages[index] && loadedImages[index].src) {
          image.src = loadedImages[index].src
        }
      })
    } catch (error) {
      console.error('Error loading images:', error)
    }
  }
}

const showImage = async (imageSrc, imageObj = null) => {
  // Find the index of the selected image
  const imageList = getImageList(selectedTransaction.value)
  let index = -1
  
  if (imageObj) {
    // If imageObj is provided, find by object reference
    index = imageList.findIndex(img => img === imageObj)
    console.log('Opening image with src:', imageObj.src)
    selectedImage.value = imageObj.src // Use the existing src from the card
  } else {
    // Find by src
    index = imageList.findIndex(img => img.src === imageSrc)
    console.log('Opening image with imageSrc:', imageSrc)
    selectedImage.value = imageSrc
  }
  
  console.log('Selected image value:', selectedImage.value)
  currentImageIndex.value = index >= 0 ? index : 0
  showImageModal.value = true
}

// Get list of all images for current transaction
const getImageList = (transaction) => {
  if (!transaction || !transaction._attachments) return []

  const images = []
  const attachmentNames = Object.keys(transaction._attachments)
  const storedUrls = transaction._cachedImageUrls || {}

  // Add entry attachment if exists
  if (attachmentNames.includes('entry.jpg')) {
    images.push({
      src: storedUrls['entry.jpg'] || '', // Use cached URL if available
      label: 'Foto Masuk',
      type: 'entry',
      isAttachment: true,
      attachmentName: 'entry.jpg',
      transactionId: transaction._id
    })
  }

  // Add exit attachment if exists
  if (attachmentNames.includes('exit.jpg')) {
    images.push({
      src: storedUrls['exit.jpg'] || '', // Use cached URL if available
      label: 'Foto Keluar',
      type: 'exit',
      isAttachment: true,
      attachmentName: 'exit.jpg',
      transactionId: transaction._id
    })
  }

  // Add other image attachments
  attachmentNames.forEach(name => {
    if (name !== 'entry.jpg' && name !== 'exit.jpg' &&
        (name.includes('.jpg') || name.includes('.jpeg') || name.includes('.png'))) {
      let label = 'Gambar'
      if (name.includes('plate')) label = 'Foto Plat'
      else if (name.includes('driver')) label = 'Foto Driver'
      else if (name.includes('vehicle')) label = 'Foto Kendaraan'

      images.push({
        src: '', // Will be loaded async
        label,
        type: 'other',
        isAttachment: true,
        attachmentName: name,
        transactionId: transaction._id
      })
    }
  })

  return images
}

// Load attachment image data
const loadAttachmentImage = async (transactionId, attachmentName) => {
  try {
    const blob = await getTransactionAttachment(transactionId, attachmentName)
    const url = URL.createObjectURL(blob)
    
    // Cache the URL in the transaction object
    if (selectedTransaction.value && selectedTransaction.value._id === transactionId) {
      if (!selectedTransaction.value._cachedImageUrls) {
        selectedTransaction.value._cachedImageUrls = {}
      }
      selectedTransaction.value._cachedImageUrls[attachmentName] = url
    }
    
    return url
  } catch (error) {
    console.error('Error loading attachment:', error)
    return null
  }
}

// Navigate between images
const navigateImage = async (direction) => {
  const imageList = getImageList(selectedTransaction.value)
  const newIndex = currentImageIndex.value + direction
  
  if (newIndex >= 0 && newIndex < imageList.length) {
    currentImageIndex.value = newIndex
    const targetImage = imageList[newIndex]
    
    // Load attachment if needed
    if (targetImage.isAttachment && !targetImage.src) {
      try {
        const attachmentUrl = await loadAttachmentImage(targetImage.transactionId, targetImage.attachmentName)
        if (attachmentUrl) {
          targetImage.src = attachmentUrl
        }
      } catch (error) {
        console.error('Error loading attachment during navigation:', error)
      }
    }
    
    selectedImage.value = targetImage.src
  }
}

// Select image by index
const selectImageByIndex = async (index) => {
  const imageList = getImageList(selectedTransaction.value)
  if (index >= 0 && index < imageList.length) {
    currentImageIndex.value = index
    const targetImage = imageList[index]
    
    // Load attachment if needed
    if (targetImage.isAttachment && !targetImage.src) {
      try {
        const attachmentUrl = await loadAttachmentImage(targetImage.transactionId, targetImage.attachmentName)
        if (attachmentUrl) {
          targetImage.src = attachmentUrl
        }
      } catch (error) {
        console.error('Error loading attachment by index:', error)
      }
    }
    
    selectedImage.value = targetImage.src
  }
}

// Get current image info
const getCurrentImageInfo = () => {
  const imageList = getImageList(selectedTransaction.value)
  if (currentImageIndex.value >= 0 && currentImageIndex.value < imageList.length) {
    const currentImage = imageList[currentImageIndex.value]
    const isEntry = currentImage.type === 'entry'
    
    return `${currentImage.label} - ${isEntry ? 'Kamera Masuk' : 'Kamera Keluar'}`
  }
  return 'Detail Gambar'
}

const processExit = (transaction) => {
  exitTransaction.value = transaction
  showExitDialog.value = true
}

const confirmExit = async () => {
  processing.value = true
  try {
    // Handle both parking and member transactions
    const transactionId = exitTransaction.value.id || exitTransaction.value._id
    
    if (exitTransaction.value.type === 'member_entry') {
      // For member transactions, use different method if available
      if (transaksiStore.processManualExitMember) {
        await transaksiStore.processManualExitMember(transactionId)
      } else {
        await transaksiStore.processManualExit(transactionId)
      }
    } else {
      // For parking transactions
      await transaksiStore.processManualExit(transactionId)
    }
    
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

const printTicket = async (transaction) => {
  try {
    // Generate ticket number if not exists
    const ticketNumber = transaction.ticket_number || (() => {
      const now = new Date();
      const time = now.toTimeString().slice(0, 8).replace(/:/g, '');
      const sequence = String(Math.floor(Math.random() * 9999) + 1).padStart(4, '0');
      return `${time}${sequence}`;
    })();

    // Prepare ticket data for thermal printer - SEMUA FIELD HARUS camelCase sesuai serde
    const ticketData = {
      ticketNumber: ticketNumber,           // ✅ ticket_number
      platNomor: transaction.plat_nomor || transaction.no_pol,  // ✅ plat_nomor
      jenisKendaraan: transaction.jenis_kendaraan, // ✅ jenis_kendaraan  
      waktuMasuk: transaction.entry_time,  // ✅ entry_time
      tarif: transaction.tarif,             // ✅ tarif
      companyName: ls.get('companyName') || 'SISTEM PARKIR SPARTA',  // ✅ company_name
      gateLocation: ls.get('lokasiPos')?.label || 'PINTU MASUK',     // ✅ gate_location
      operatorName: ls.get('pegawai')?.nama || 'OPERATOR',           // ✅ operator_name
      isPaid: transaction.is_paid || transaction.bayar_masuk > 0,    // ✅ is_paid
      barcodeData: ticketNumber              // ✅ barcode_data
    };

    // Print thermal ticket
    await invoke('print_thermal_ticket', { 
      printerName: null, // will use default printer
      ticketData
    });
    
    // Notify success
    $q.notify({
      type: 'positive',
      message: 'Tiket berhasil dicetak',
      position: 'top'
    });

  } catch (error) {
    console.error('Error printing ticket:', error);
    $q.notify({
      type: 'negative',
      message: 'Gagal mencetak tiket',
      position: 'top'
    });
  }
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
      const { remoteDbs } = await import('src/boot/pouchdb')
      const db = remoteDbs.transactions
      
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
          entry_time: new Date(Date.now() - 4 * 3600000).toISOString(),
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
          entry_time: new Date(Date.now() - 3 * 3600000).toISOString(),
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

// Helper functions to handle different transaction types
const getVehicleType = (transaction) => {
  if (!transaction) return ''
  
  // For member transactions
  if (transaction.type === 'member_entry') {
    return transaction.vehicle?.type?.label || transaction.jenis_kendaraan?.label || ''
  }
  
  // For parking transactions
  return transaction.jenis_kendaraan || ''
}

const getPlateNumber = (transaction) => {
  if (!transaction) return ''
  
  // For member transactions
  if (transaction.type === 'member_entry') {
    return transaction.plat_nomor || transaction.vehicle?.license_plate || ''
  }
  
  // For parking transactions
  return transaction.plat_nomor || transaction.no_pol || ''
}

const getEntryTime = (transaction) => {
  if (!transaction) return ''
  
  // For member transactions
  if (transaction.type === 'member_entry') {
    return transaction.entry_time || ''
  }
  
  // For parking transactions
  return transaction.entry_time || ''
}

const getExitTime = (transaction) => {
  if (!transaction) return ''
  
  // For member transactions
  if (transaction.type === 'member_entry') {
    return transaction.exit_time || ''
  }
  
  // For parking transactions
  return transaction.waktu_keluar || ''
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
  
  // Handle negative duration (data issue)
  if (diffMs < 0) return 'Data tidak valid'
  
  const hours = Math.floor(diffMs / (1000 * 60 * 60))
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
  
  if (hours > 0) {
    return `${hours}j ${minutes}m`
  } else {
    return `${minutes}m`
  }
}

const getStatusColor = (status) => {
  // Handle member transaction status (string values - legacy format)
  if (typeof status === 'string') {
    switch (status.toLowerCase()) {
      case 'in': return 'orange'
      case 'out': return 'green'
      case 'cancelled': return 'red'
      default: return 'grey'
    }
  }
  
  // Handle both parking and member transaction status (numeric values)
  switch (status) {
    case 0: return 'orange' // Aktif/Masuk
    case 1: return 'green'  // Selesai/Keluar
    case 2: return 'red'    // Dibatalkan
    default: return 'grey'
  }
}

const getStatusLabel = (status) => {
  // Handle member transaction status (string values - legacy format)
  if (typeof status === 'string') {
    switch (status.toLowerCase()) {
      case 'in': return 'Aktif (Member)'
      case 'out': return 'Selesai (Member)'
      case 'cancelled': return 'Dibatalkan (Member)'
      default: return 'Unknown'
    }
  }
  
  // Handle both parking and member transaction status (numeric values)
  switch (status) {
    case 0: return 'Aktif'      // Aktif/Masuk (untuk parkir umum dan member)
    case 1: return 'Selesai'    // Selesai/Keluar (untuk parkir umum dan member)
    case 2: return 'Dibatalkan' // Dibatalkan
    default: return 'Unknown'
  }
}

const isAdmin = computed(() => ls.get('isAdmin') || false)

// Functions to load member transaction images from attachments
const loadMemberTransactionImages = async (transaction) => {
  if (!transaction || !transaction.is_member) return
  
  // Reset previous image data
  entryImageData.value = ''
  exitImageData.value = ''
  
  try {
    // Load entry image if it has attachment marker
    if (transaction.entry_pic && transaction.entry_pic.startsWith('ATTACHMENT:')) {
      loadingEntryImage.value = true
      const imageData = await transaksiStore.getTransactionImageData(transaction.id, 'entry')
      entryImageData.value = imageData
    }
    
  // exit_pic diabaikan, hanya attachment
  } catch (error) {
    console.error('Error loading member transaction images:', error)
    $q.notify({
      type: 'negative',
      message: 'Gagal memuat gambar member',
      position: 'top'
    })
  } finally {
    loadingEntryImage.value = false
    loadingExitImage.value = false
  }
}

// Get the actual image source from attachments
const getImageSrc = (transaction, imageType) => {
  if (!transaction || !transaction._attachments) return ''

  const attachmentNames = Object.keys(transaction._attachments)
  let attachmentKey = ''
  if (imageType === 'entry' && attachmentNames.includes('entry.jpg')) {
    attachmentKey = 'entry.jpg'
  } else if (imageType === 'exit' && attachmentNames.includes('exit.jpg')) {
    attachmentKey = 'exit.jpg'
  }
  
  if (attachmentKey) {
    const imageList = getImageList(transaction)
    const found = imageList.find(img => img.attachmentName === attachmentKey)
    if (found && found.src) return found.src
  }
  
  return ''
}

// Helper functions for images
const hasImages = (transaction) => {
  if (!transaction || !transaction._attachments) return false
  
  const names = Object.keys(transaction._attachments)
  return names.some(name => name.endsWith('.jpg') || name.endsWith('.jpeg') || name.endsWith('.png'))
}

const getImageCount = (transaction) => {
  if (!transaction || !transaction._attachments) return 0
  const names = Object.keys(transaction._attachments)
  let count = 0
  if (names.includes('entry.jpg')) count++
  if (names.includes('exit.jpg')) count++
  return count
}

// Computed for active filters
const hasActiveFilters = computed(() => {
  return !!(
    filters.value.platNomor?.trim() ||
    filters.value.status !== null ||
    filters.value.tanggalMulai ||
    filters.value.tanggalAkhir ||
    filters.value.jenisKendaraan ||
    filters.value.isMember !== null
  )
})

const activeFilterCount = computed(() => {
  let count = 0
  if (filters.value.platNomor?.trim()) count++
  if (filters.value.status !== null) count++
  if (filters.value.tanggalMulai) count++
  if (filters.value.tanggalAkhir) count++
  if (filters.value.jenisKendaraan) count++
  if (filters.value.isMember !== null) count++
  return count
})

// Use statistics from computed, bukan dari store untuk konsistensi dengan data yang ditampilkan
const displayStatistics = computed(() => {
  // Selalu gunakan computedStatistics yang menghitung dari data yang ditampilkan
  // Ini memastikan statistik konsisten dengan data yang user lihat di tabel
  return computedStatistics.value
})

// Lifecycle
onMounted(async () => {
  try {
    console.log('🚀 Initializing page...')
    
    // Use same logic as refreshData - just call refreshData directly
    await refreshData()
    
    // Setup database change listener setelah data pertama dimuat
    // Cek preferensi auto-sync dari localStorage (default true)
    const autoSyncEnabled = ls.get('daftarTransaksiAutoSync') !== false
    if (autoSyncEnabled) {
      setupDatabaseChangeListener()
    }
    
    hasInitialized.value = true
    console.log('✅ Page initialized successfully with change listener')
  } catch (error) {
    console.error('❌ Error initializing page:', error)
    
    $q.notify({
      type: 'negative',
      message: 'Gagal memuat halaman. Menyiapkan mode offline...',
      position: 'top',
      timeout: 5000,
      actions: [
        {
          label: 'Coba Lagi',
          color: 'white',
          handler: () => {
            window.location.reload()
          }
        }
      ]
    })
    
    // Set minimal state for offline mode
    transaksiList.value = []
    pagination.value.rowsNumber = 0
    statistics.value = {
      totalTransaksi: 0,
      transaksiSelesai: 0,
      transaksiAktif: 0,
      totalPendapatan: 0,
      transaksiMember: 0,
      memberSelesai: 0,
      memberAktif: 0,
      transaksiUmum: 0,
      umumSelesai: 0,
      umumAktif: 0
    }
  } finally {
    loading.value = false
  }
})

// Cleanup saat component di-unmount
onUnmounted(() => {
  console.log('🧹 Cleaning up page resources...')
  
  // Stop database change listener
  stopDatabaseChangeListener()
  
  // Clear any pending timers
  if (filterTimer) {
    clearTimeout(filterTimer)
    filterTimer = null
  }
  
  console.log('✅ Page cleanup completed')
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

/* Image styles */
.image-card {
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.image-card:hover {
  border-color: var(--q-primary);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.image-hover {
  transition: all 0.3s ease;
}

.image-hover:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.image-thumbnail {
  opacity: 0.7;
  transition: opacity 0.3s ease;
  border: 2px solid transparent;
}

.image-thumbnail:hover {
  opacity: 1;
  border-color: var(--q-primary);
}

.image-selected {
  border: 2px solid var(--q-primary);
  opacity: 1;
}

/* Custom loading spinner for images */
.q-img__loading {
  color: var(--q-primary);
}

/* Better responsive image containers */
@media (max-width: 768px) {
  .image-card {
    margin-bottom: 1rem;
  }
  
  .q-img {
    max-height: 150px !important;
  }
}

/* Animation for image modal */
.q-dialog__inner {
  transition: all 0.3s ease;
}

/* Enhance chip colors */
.q-chip--outline {
  border-width: 2px;
}
</style>
