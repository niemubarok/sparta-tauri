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
              <q-skeleton v-if="statsLoading" type="text" width="60px" />
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
              <q-skeleton v-if="statsLoading" type="text" width="60px" />
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
              <q-skeleton v-if="statsLoading" type="text" width="60px" />
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
        <q-card class="bg-teal-1">
          <q-card-section class="text-center">
            <div class="text-h4 text-teal">
              <q-skeleton v-if="statsLoading" type="text" width="80px" />
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
            <q-chip
              v-if="hasImages(props.row)"
              :color="getImageCount(props.row) === 2 ? 'green' : 'orange'"
              text-color="white"
              icon="camera_alt"
              :label="getImageCount(props.row)"
              size="sm"
              clickable
              @click="viewDetail(props.row)"
            >
              <q-tooltip>{{ getImageCount(props.row) }} gambar tersedia ({{ getImageCount(props.row) === 2 ? 'Masuk & Keluar' : getImageCount(props.row) === 1 ? 'Masuk saja' : 'Lengkap' }}) - Klik untuk lihat detail</q-tooltip>
            </q-chip>
            <q-chip
              v-else
              color="grey-5"
              text-color="white"
              icon="no_photography"
              label="0"
              size="sm"
            >
              <q-tooltip>Tidak ada gambar</q-tooltip>
            </q-chip>
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

      <template v-slot:body-cell-waktu_masuk="props">
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
          <div v-if="hasImages(selectedTransaction)" class="q-mt-md">
            <q-separator class="q-mb-md" />
            
            <!-- Header dengan informasi gambar -->
            <div class="row items-center justify-between q-mb-md">
              <div class="text-subtitle1 text-weight-medium">
                <q-icon name="camera_alt" class="q-mr-sm" />
                Dokumentasi CCTV Transaksi
              </div>
              <q-chip 
                color="blue" 
                text-color="white" 
                icon="info"
                :label="`${getImageCount(selectedTransaction)} Gambar`"
                size="sm"
              />
            </div>

            <!-- Foto Masuk -->
            <div v-if="selectedTransaction.entry_pic" class="q-mb-lg">
              <div class="text-subtitle2 q-mb-md text-positive">
                <q-icon name="login" class="q-mr-xs" />
                Foto Saat Masuk Parkir
                <q-badge v-if="selectedTransaction.is_member" color="purple" class="q-ml-sm">
                  Member
                </q-badge>
              </div>
              <div class="row justify-center">
                <div class="col-md-8 col-xs-12">
                  <q-card flat bordered class="image-card">
                    <q-card-section class="q-pa-sm">
                      <div class="text-caption text-weight-medium q-mb-xs text-blue-8 text-center">
                        <q-icon name="camera_alt" class="q-mr-xs" size="sm" />
                        Foto Kamera Masuk
                      </div>
                      
                      <!-- Loading state for member transactions -->
                      <div v-if="loadingEntryImage" class="flex flex-center q-pa-xl">
                        <q-spinner-hourglass size="50px" color="primary" />
                        <div class="text-caption q-ml-md">Memuat gambar...</div>
                      </div>
                      
                      <!-- Image display -->
                      <q-img
                        v-else
                        :src="getImageSrc(selectedTransaction, 'entry')"
                        style="height: 300px; max-width: 100%"
                        class="rounded-borders cursor-pointer image-hover"
                        @click="showImage(getImageSrc(selectedTransaction, 'entry'))"
                        fit="contain"
                        spinner-color="primary"
                        loading="lazy"
                      >
                        <div class="absolute-bottom text-subtitle2 text-center bg-dark text-white q-pa-xs">
                          Klik untuk memperbesar
                        </div>
                        <template v-slot:error>
                          <div class="absolute-full flex flex-center bg-grey-3 text-grey-7">
                            <div class="text-center">
                              <q-icon name="broken_image" size="md" />
                              <div class="text-caption">Gambar tidak dapat dimuat</div>
                            </div>
                          </div>
                        </template>
                      </q-img>
                    </q-card-section>
                  </q-card>
                </div>
              </div>
            </div>

            <!-- Foto Keluar -->
            <div v-if="selectedTransaction.exit_pic">
              <div class="text-subtitle2 q-mb-md text-negative">
                <q-icon name="logout" class="q-mr-xs" />
                Foto Saat Keluar Parkir
                <q-badge v-if="selectedTransaction.is_member" color="purple" class="q-ml-sm">
                  Member
                </q-badge>
              </div>
              <div class="row justify-center">
                <div class="col-md-8 col-xs-12">
                  <q-card flat bordered class="image-card">
                    <q-card-section class="q-pa-sm">
                      <div class="text-caption text-weight-medium q-mb-xs text-red-8 text-center">
                        <q-icon name="camera_alt" class="q-mr-xs" size="sm" />
                        Foto Kamera Keluar
                      </div>
                      
                      <!-- Loading state for member transactions -->
                      <div v-if="loadingExitImage" class="flex flex-center q-pa-xl">
                        <q-spinner-hourglass size="50px" color="primary" />
                        <div class="text-caption q-ml-md">Memuat gambar...</div>
                      </div>
                      
                      <!-- Image display -->
                      <q-img
                        v-else
                        :src="getImageSrc(selectedTransaction, 'exit')"
                        style="height: 300px; max-width: 100%"
                        class="rounded-borders cursor-pointer image-hover"
                        @click="showImage(getImageSrc(selectedTransaction, 'exit'))"
                        fit="contain"
                        spinner-color="primary"
                        loading="lazy"
                      >
                        <div class="absolute-bottom text-subtitle2 text-center bg-dark text-white q-pa-xs">
                          Klik untuk memperbesar
                        </div>
                        <template v-slot:error>
                          <div class="absolute-full flex flex-center bg-grey-3 text-grey-7">
                            <div class="text-center">
                              <q-icon name="broken_image" size="md" />
                              <div class="text-caption">Gambar tidak dapat dimuat</div>
                            </div>
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
                Tidak ada dokumentasi gambar untuk transaksi ini
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
import { ref, onMounted, computed, watch } from 'vue'
import { useQuasar } from 'quasar'
import { useTransaksiStore } from 'src/stores/transaksi-store'
import { getTransactionAttachment } from 'src/boot/pouchdb'
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

// Image loading states for member transactions
const loadingEntryImage = ref(false)
const loadingExitImage = ref(false)
const entryImageData = ref('')
const exitImageData = ref('')

// Computed statistics based on current filtered data
const computedStatistics = computed(() => {
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
  const selesai = transaksiList.value.filter(t => t.status === 1 || t.status === 'out').length
  // Support both legacy string status ('in') and new integer status (0) for active transactions
  const aktif = transaksiList.value.filter(t => t.status === 0 || t.status === 'in').length
  const pendapatan = transaksiList.value
    .filter(t => t.status === 1 || t.status === 'out')
    .reduce((total, t) => total + (t.tarif || 0), 0)

  // Separate member and regular transactions
  const memberTransactions = transaksiList.value.filter(t => t.type === 'member_entry' || t.is_member === true)
  const regularTransactions = transaksiList.value.filter(t => t.type === 'parking_transaction' && !t.is_member)
  
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
    name: 'waktu_masuk',
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
      jenisKendaraan: filters.value.jenisKendaraan || '',
      isMember: filters.value.isMember
    }

    console.log('🔍 Loading transaksi with filterParams:', filterParams)
    console.log('🔍 Current filters.value:', filters.value)
    console.log('🔍 Member filter (isMember):', filters.value.isMember)

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
      jenisKendaraan: filters.value.jenisKendaraan || '',
      isMember: filters.value.isMember
    }
    
    console.log('📊 Loading statistics with filters:', statsParams)
    console.log('📊 Member filter in stats:', statsParams.isMember)
    console.log('📊 Member filter type:', typeof statsParams.isMember, 'value:', statsParams.isMember)
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
      totalPendapatan: 0,
      transaksiMember: 0,
      memberSelesai: 0,
      memberAktif: 0,
      transaksiUmum: 0,
      umumSelesai: 0,
      umumAktif: 0
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

const refreshData = () => {
  console.log('Refreshing data with current filters:', filters.value)
  loadTransaksi()
}

const viewDetail = async (transaction) => {
  selectedTransaction.value = transaction
  
  // Load attachment images if they exist
  if (transaction._attachments) {
    const imageList = getImageList(transaction)
    
    for (const image of imageList) {
      if (image.isAttachment && !image.src) {
        try {
          const attachmentUrl = await loadAttachmentImage(image.transactionId, image.attachmentName)
          if (attachmentUrl) {
            image.src = attachmentUrl
          }
        } catch (error) {
          console.error('Error loading attachment for detail view:', error)
        }
      }
    }
  }
  
  showDetailDialog.value = true
}

const showImage = async (imageSrc, imageObj = null) => {
  // Find the index of the selected image
  const imageList = getImageList(selectedTransaction.value)
  let index = -1
  
  if (imageObj) {
    // If imageObj is provided, find by object reference
    index = imageList.findIndex(img => img === imageObj)
    
    // Load attachment if needed
    if (imageObj.isAttachment && !imageObj.src) {
      try {
        const attachmentUrl = await loadAttachmentImage(imageObj.transactionId, imageObj.attachmentName)
        if (attachmentUrl) {
          imageObj.src = attachmentUrl
          imageSrc = attachmentUrl
        }
      } catch (error) {
        console.error('Error loading attachment for image view:', error)
        $q.notify({
          type: 'negative',
          message: 'Gagal memuat gambar attachment',
          position: 'top'
        })
        return
      }
    }
  } else {
    // Find by src
    index = imageList.findIndex(img => img.src === imageSrc)
  }
  
  selectedImage.value = imageSrc
  currentImageIndex.value = index >= 0 ? index : 0
  showImageModal.value = true
}

// Get list of all images for current transaction
const getImageList = (transaction) => {
  if (!transaction) return []
  
  const images = []
  
  // Handle old format (direct fields)
  if (transaction.entry_pic) {
    images.push({
      src: transaction.entry_pic,
      label: 'Foto Masuk',
      type: 'entry',
      isAttachment: false
    })
  }
  
  if (transaction.exit_pic) {
    images.push({
      src: transaction.exit_pic,
      label: 'Foto Keluar',
      type: 'exit',
      isAttachment: false
    })
  }
  
  // Handle new format (attachments) - placeholder for now
  if (transaction._attachments) {
    const attachmentNames = Object.keys(transaction._attachments)
    
    // Add entry attachment if exists
    if (attachmentNames.includes('entry.jpg')) {
      images.push({
        src: '', // Will be loaded async
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
        src: '', // Will be loaded async
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
  }
  
  return images
}

// Load attachment image data
const loadAttachmentImage = async (transactionId, attachmentName) => {
  try {
    const blob = await getTransactionAttachment(transactionId, attachmentName)
    const url = URL.createObjectURL(blob)
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
  return transaction.waktu_masuk || ''
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
    
    // Load exit image if it has attachment marker
    if (transaction.exit_pic && transaction.exit_pic.startsWith('ATTACHMENT:')) {
      loadingExitImage.value = true
      const imageData = await transaksiStore.getTransactionImageData(transaction.id, 'exit')
      exitImageData.value = imageData
    }
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

// Get the actual image source (for both parking and member transactions)
const getImageSrc = (transaction, imageType) => {
  if (!transaction) return ''
  
  const imageField = imageType === 'entry' ? 'entry_pic' : 'exit_pic'
  const imageValue = transaction[imageField]
  
  if (!imageValue) return ''
  
  // If it's a member transaction with attachment marker, use loaded image data
  if (transaction.is_member && imageValue.startsWith('ATTACHMENT:')) {
    return imageType === 'entry' ? entryImageData.value : exitImageData.value
  }
  
  // For parking transactions, return the direct image data
  return imageValue
}

// Helper functions for images
const hasImages = (transaction) => {
  if (!transaction) return false
  
  // Check for direct image data (parking transactions)
  const hasDirectImages = !!(transaction.entry_pic && !transaction.entry_pic.startsWith('ATTACHMENT:')) || 
                         !!(transaction.exit_pic && !transaction.exit_pic.startsWith('ATTACHMENT:'))
  
  // Check for attachment markers (member transactions)
  const hasAttachmentMarkers = !!(transaction.entry_pic && transaction.entry_pic.startsWith('ATTACHMENT:')) ||
                              !!(transaction.exit_pic && transaction.exit_pic.startsWith('ATTACHMENT:'))
  
  return hasDirectImages || hasAttachmentMarkers
}

const getImageCount = (transaction) => {
  if (!transaction) return 0
  let count = 0
  
  // Count direct images (parking transactions) or attachment markers (member transactions)
  if (transaction.entry_pic) count++
  if (transaction.exit_pic) count++
  
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

// Use statistics from store, fallback to computed if needed
const displayStatistics = computed(() => {
  if (statsLoading.value) {
    return statistics.value
  }
  
  // If we have statistics from store, use them, otherwise use computed
  if (statistics.value.totalTransaksi > 0 || 
      statistics.value.transaksiSelesai > 0 || 
      statistics.value.transaksiAktif > 0 || 
      statistics.value.totalPendapatan > 0 ||
      statistics.value.transaksiMember > 0 ||
      statistics.value.transaksiUmum > 0) {
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

// Auto-load member transaction images when transaction is selected
watch(() => selectedTransaction.value, async (newTransaction) => {
  if (newTransaction && newTransaction.is_member) {
    console.log('🖼️ Auto-loading member transaction images for:', newTransaction._id)
    await loadMemberTransactionImages(newTransaction)
  }
}, { immediate: true })
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
