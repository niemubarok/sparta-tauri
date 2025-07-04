<template>
  <q-page padding class="bg-grey-1">
    <div class="q-pa-md">
      <!-- Header -->
      <div class="row items-center justify-between q-mb-lg">
        <div class="row items-center">
          <q-btn
            flat
            dense
            to="/"
            color="primary"
            icon="arrow_back"
            class="q-mr-md"
          />
          <div>
            <h4 class="q-ma-none text-weight-bold">Manajemen Member</h4>
            <p class="text-grey-6 q-ma-none">Kelola data member dan keanggotaan</p>
          </div>
        </div>
        
        <div class="row q-gutter-sm">
          <q-btn
            color="orange"
            icon="add_business"
            label="Tipe Member"
            @click="showAddTypeDialog = true"
            outline
          />
          <q-btn
            color="primary"
            icon="person_add"
            label="Tambah Member"
            @click="openAddMemberDialog"
          />
          <q-btn
            color="primary"
            icon="upload"
            label="Upload Excel Bulk"
            @click="showUploadDialog = true"
            outline
          />
        </div>
      </div>

      <!-- Database Initializer (shown when no data exists) -->
      <DatabaseInitializer 
        v-if="members.length === 0 && membershipTypes.length === 0" 
        @member-database-initialized="handleDatabaseInitialized"
      />

      <!-- Statistics Cards -->
      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-xs-12 col-sm-6 col-md-3">
          <q-card class="bg-blue-1 text-primary">
            <q-card-section class="text-center">
              <div class="text-h6 text-weight-bold">{{ statistics.totalMembers }}</div>
              <div class="text-caption">Total Member</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-xs-12 col-sm-6 col-md-3">
          <q-card class="bg-green-1 text-positive">
            <q-card-section class="text-center">
              <div class="text-h6 text-weight-bold">{{ statistics.activeMembers }}</div>
              <div class="text-caption">Member Aktif</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-xs-12 col-sm-6 col-md-3">
          <q-card class="bg-orange-1 text-warning">
            <q-card-section class="text-center">
              <div class="text-h6 text-weight-bold">{{ statistics.expiringSoon }}</div>
              <div class="text-caption">Akan Berakhir</div>
            </q-card-section>
          </q-card>
        </div>
        <div class="col-xs-12 col-sm-6 col-md-3">
          <q-card class="bg-purple-1 text-purple">
            <q-card-section class="text-center">
              <div class="text-h6 text-weight-bold">{{ formatCurrency(statistics.totalRevenue) }}</div>
              <div class="text-caption">Total Pendapatan</div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Filters and Search -->
      <q-card class="q-mb-md">
        <q-card-section>
          <div class="row q-col-gutter-md items-end">
            <div class="col-xs-12 col-sm-6 col-md-4">
              <q-input
                v-model="searchText"
                dense
                outlined
                placeholder="Cari member, no polisi, atau telepon..."
                clearable
              >
                <template v-slot:prepend>
                  <q-icon name="search" />
                </template>
              </q-input>
            </div>
            
            <div class="col-xs-12 col-sm-6 col-md-3">
              <q-select
                v-model="filterType"
                outlined
                dense
                label="Filter Tipe"
                :options="membershipTypeOptions"
                emit-value
                map-options
                clearable
              />
            </div>
            
            <div class="col-xs-12 col-sm-6 col-md-2">
              <q-select
                v-model="filterStatus"
                outlined
                dense
                label="Status"
                :options="statusOptions"
                emit-value
                map-options
                clearable
              />
            </div>
            
            <div class="col-xs-12 col-sm-6 col-md-3">
              <div class="row q-gutter-sm">
                <q-btn
                  flat
                  icon="filter_list"
                  label="Reset Filter"
                  @click="resetFilters"
                />
                <q-btn
                  flat
                  icon="file_download"
                  label="Export"
                  @click="exportData"
                />
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card>

      <!-- Members Table -->
      <q-card>
        <q-table
          :rows="filteredMembers"
          :columns="columns"
          row-key="_id"
          :loading="loading"
          :pagination="{ rowsPerPage: 10 }"
          class="full-width"
        >
          <template v-slot:body-cell-index="props">
            <q-td :props="props">
              {{ props.pageIndex + 1 }}
            </q-td>
          </template>

          <template v-slot:body-cell-member_info="props">
            <q-td :props="props">
              <div class="row items-center q-gutter-sm">
                <q-avatar size="40px" color="primary" text-color="white">
                  {{ props.row.name.charAt(0).toUpperCase() }}
                </q-avatar>
                <div>
                  <div class="text-weight-medium">{{ props.row.name }}</div>
                  <div class="text-caption text-grey-6">{{ props.row.member_id }}</div>
                  <div class="text-caption text-grey-6">{{ props.row.phone }}</div>
                </div>
              </div>
            </q-td>
          </template>

          <template v-slot:body-cell-membership_type="props">
            <q-td :props="props">
              <q-chip
                :color="getMembershipCategoryColor(props.row.membershipCategory)"
                text-color="white"
                dense
              >
                {{ props.row.membershipType }}
              </q-chip>
            </q-td>
          </template>

          <template v-slot:body-cell-vehicles="props">
            <q-td :props="props">
              <div class="column q-gutter-xs">
                <q-chip
                  v-for="(vehicle, index) in props.row.vehicles"
                  :key="index"
                  square
                  size="sm"
                  :icon="getVehicleIcon(vehicle.type)"
                  color="blue-1"
                  text-color="primary"
                >
                  {{ vehicle.license_plate }}
                </q-chip>
              </div>
            </q-td>
          </template>

          <template v-slot:body-cell-status="props">
            <q-td :props="props">
              <div class="column q-gutter-xs">
                <q-badge
                  :color="getStatusColor(props.row)"
                  :label="getStatusLabel(props.row)"
                />
                <q-badge
                  v-if="props.row.payment_status"
                  :color="getPaymentStatusColor(props.row.payment_status)"
                  :label="getPaymentStatusLabel(props.row.payment_status)"
                />
              </div>
            </q-td>
          </template>

          <template v-slot:body-cell-expiry="props">
            <q-td :props="props">
              <div>
                <div class="text-body2">{{ formatDate(props.row.end_date) }}</div>
                <div 
                  class="text-caption"
                  :class="getExpiryTextClass(props.row)"
                >
                  {{ getExpiryText(props.row) }}
                </div>
              </div>
            </q-td>
          </template>

          <template v-slot:body-cell-actions="props">
            <q-td :props="props">
              <q-btn-group flat>
                <q-btn
                  flat
                  round
                  color="primary"
                  icon="visibility"
                  @click="viewMember(props.row)"
                  size="sm"
                >
                  <q-tooltip>Lihat Detail</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  round
                  color="primary"
                  icon="edit"
                  @click="editMember(props.row)"
                  size="sm"
                >
                  <q-tooltip>Edit</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  round
                  color="orange"
                  icon="autorenew"
                  @click="renewMembership(props.row)"
                  size="sm"
                >
                  <q-tooltip>Perpanjang</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  round
                  color="negative"
                  icon="delete"
                  @click="confirmDelete(props.row)"
                  size="sm"
                >
                  <q-tooltip>Hapus</q-tooltip>
                </q-btn>
              </q-btn-group>
            </q-td>
          </template>
        </q-table>
      </q-card>
    </div>

    <!-- Add/Edit Member Dialog -->
    <q-dialog v-model="showAddNewMemberDialog" persistent maximized>
      <q-card class="full-width full-height">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">{{ isEditing ? 'Edit Member' : 'Tambah Member Baru' }}</div>
        </q-card-section>

        <q-card-section class="q-pa-lg scroll" style="max-height: calc(100vh - 120px);">
          <q-form @submit.prevent="saveMember" class="q-gutter-md">
            <!-- Basic Information -->
            <div class="text-h6 text-primary q-mb-md">Informasi Dasar</div>
            <div class="row q-col-gutter-md">
              <q-input
                v-model="memberForm.member_id"
                class="col-xs-12 col-md-4"
                label="ID Member"
                outlined
                :readonly="isEditing"
                hint="Akan digenerate otomatis jika kosong"
              />
              <q-input
                v-model="memberForm.card_number"
                class="col-xs-12 col-md-4"
                label="Nomor Kartu (Card Number) *"
                outlined
                :rules="[val => !!val || 'Nomor kartu harus diisi']"
                hint="Nomor kartu fisik untuk tap di gate"
              />
              <q-input
                v-model="memberForm.name"
                class="col-xs-12 col-md-4"
                label="Nama Lengkap *"
                outlined
                :rules="[val => !!val || 'Nama harus diisi']"
              />
              <q-input
                v-model="memberForm.email"
                class="col-xs-12 col-md-6"
                label="Email"
                type="email"
                outlined
              />
              <q-input
                v-model="memberForm.phone"
                class="col-xs-12 col-md-6"
                label="Telepon *"
                outlined
                :rules="[val => !!val || 'Telepon harus diisi']"
              />
              <q-input
                v-model="memberForm.identity_number"
                class="col-xs-12 col-md-6"
                label="Nomor KTP/ID"
                outlined
              />
              <q-input
                v-model="memberForm.address"
                class="col-xs-12 col-md-6"
                type="textarea"
                label="Alamat"
                outlined
              />
            </div>

            <!-- Membership Information -->
            <div class="text-h6 text-primary q-mb-md q-mt-lg">Informasi Keanggotaan</div>
            <div class="row q-col-gutter-md">
              <q-select
                v-model="memberForm.membership_type_id"
                class="col-xs-12 col-md-6"
                label="Tipe Member *"
                :options="membershipTypes"
                emit-value
                map-options
                option-value="_id"
                option-label="name"
                outlined
                :rules="[val => !!val || 'Tipe Member harus dipilih']"
              >
                <template v-slot:append>
                  <q-btn
                    flat
                    icon="add"
                    @click="showAddTypeDialog = true"
                    size="sm"
                  />
                </template>
              </q-select>
              <q-select
                v-model="memberForm.payment_status"
                class="col-xs-12 col-md-6"
                label="Status Pembayaran"
                :options="paymentStatusOptions"
                emit-value
                map-options
                outlined
              />
              <q-input
                v-model="memberForm.start_date"
                class="col-xs-12 col-md-6"
                label="Tanggal Mulai *"
                type="date"
                outlined
                :rules="[val => !!val || 'Tanggal mulai harus diisi']"
              />
              <q-input
                v-model="memberForm.end_date"
                class="col-xs-12 col-md-6"
                label="Tanggal Berakhir *"
                type="date"
                outlined
                :rules="[val => !!val || 'Tanggal berakhir harus diisi']"
              />
              <q-input
                v-model="memberForm.notes"
                class="col-12"
                type="textarea"
                label="Catatan"
                outlined
              />
            </div>

            <!-- Vehicles Information -->
            <div class="text-h6 text-primary q-mb-md q-mt-lg">
              Data Kendaraan
              <q-btn
                flat
                round
                color="primary"
                icon="add"
                size="sm"
                class="q-ml-sm"
                @click="addVehicle"
              />
            </div>
            
            <div 
              v-for="(vehicle, index) in memberForm.vehicles" 
              :key="index"
              class="q-mb-md"
            >
              <q-card flat bordered>
                <q-card-section>
                  <div class="row q-col-gutter-md items-end">
                    <q-select
                      v-model="vehicle.type"
                      class="col-xs-12 col-sm-6 col-md-3"
                      label="Jenis Kendaraan *"
                      :options="vehicleTypeOptions"
                      outlined
                      :rules="[val => !!val || 'Jenis kendaraan harus dipilih']"
                    />
                    <q-input
                      v-model="vehicle.license_plate"
                      class="col-xs-12 col-sm-6 col-md-3"
                      label="Nomor Polisi *"
                      outlined
                      :rules="[val => !!val || 'Nomor polisi harus diisi']"
                    />
                    <q-input
                      v-model="vehicle.brand"
                      class="col-xs-12 col-sm-6 col-md-2"
                      label="Merk"
                      outlined
                    />
                    <q-input
                      v-model="vehicle.model"
                      class="col-xs-12 col-sm-6 col-md-2"
                      label="Model"
                      outlined
                    />
                    <q-input
                      v-model="vehicle.color"
                      class="col-xs-12 col-sm-6 col-md-1"
                      label="Warna"
                      outlined
                    />
                    <div class="col-xs-12 col-sm-6 col-md-1 flex items-center">
                      <q-btn
                        v-if="memberForm.vehicles.length > 1"
                        flat
                        round
                        color="negative"
                        icon="delete"
                        size="sm"
                        @click="removeVehicle(index)"
                      />
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <!-- Emergency Contact -->
             <div v-if="memberForm.emergency_contact">

               <div class="text-h6 text-primary q-mb-md q-mt-lg">Kontak Darurat</div>
               <div class="row q-col-gutter-md">
                 <q-input
                v-model="memberForm.emergency_contact.name"
                class="col-xs-12 col-md-4"
                label="Nama"
                outlined
              />
              <q-input
                v-model="memberForm.emergency_contact.phone"
                class="col-xs-12 col-md-4"
                label="Telepon"
                outlined
              />
              <q-input
              v-model="memberForm.emergency_contact.relationship"
              class="col-xs-12 col-md-4"
              label="Hubungan"
              outlined
              />
            </div>
            </div>
          </q-form>
        </q-card-section>

        <q-card-actions class="bg-grey-1" align="right">
          <q-btn flat label="Batal" color="primary" @click="closeAddMemberDialog" />
          <q-btn 
            label="Simpan" 
            color="primary" 
            @click="saveMember"
            :loading="loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Add Membership Type Dialog -->
    <q-dialog v-model="showAddTypeDialog" persistent>
      <q-card style="min-width: 600px">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Tambah Tipe Member</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit.prevent="saveNewType" class="q-gutter-md">
            <div class="row q-col-gutter-md">
              <q-input
                v-model="typeForm.name"
                class="col-12"
                label="Nama Tipe *"
                outlined
                :rules="[val => !!val || 'Nama tipe harus diisi']"
              />
              <q-select
                v-model="typeForm.category"
                class="col-6"
                label="Kategori"
                :options="membershipCategories"
                emit-value
                map-options
                outlined
              />
              <q-input
                v-model="typeForm.price"
                class="col-6"
                label="Harga *"
                type="number"
                min="0"
                outlined
                :rules="[val => val >= 0 || 'Harga harus >= 0']"
              />
              <q-select
                v-model="typeForm.area_type"
                class="col-6"
                label="Tipe Area"
                :options="areaTypeOptions"
                emit-value
                map-options
                outlined
              />
              <q-input
                v-model="typeForm.max_vehicles"
                class="col-6"
                label="Maksimal Kendaraan"
                type="number"
                min="1"
                outlined
                :rules="[val => val > 0 || 'Harus lebih dari 0']"
              />
              <q-input
                v-model="typeForm.duration_months"
                class="col-6"
                label="Durasi (Bulan)"
                type="number"
                min="1"
                outlined
              />
              <div class="col-3">
                <q-input
                  v-model="typeForm.operating_hours.start"
                  label="Jam Mulai"
                  type="time"
                  outlined
                />
              </div>
              <div class="col-3">
                <q-input
                  v-model="typeForm.operating_hours.end"
                  label="Jam Selesai"
                  type="time"
                  outlined
                />
              </div>
              <q-input
                v-model="typeForm.description"
                class="col-12"
                label="Deskripsi"
                type="textarea"
                outlined
              />
              <q-select
                v-model="typeForm.facilities"
                class="col-6"
                label="Fasilitas"
                multiple
                :options="facilityOptions"
                outlined
              />
              <q-select
                v-model="typeForm.benefits"
                class="col-6"
                label="Benefit"
                multiple
                :options="benefitOptions"
                outlined
              />
            </div>
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Batal" color="primary" @click="closeAddTypeDialog" />
          <q-btn 
            label="Simpan" 
            color="primary" 
            @click="saveNewType"
            :loading="loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Member Detail Dialog -->
    <q-dialog v-model="showMemberDetailDialog" maximized>
      <q-card class="full-width full-height">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Detail Member</div>
        </q-card-section>

        <q-card-section v-if="selectedMember" class="q-pa-lg">
          <div class="row q-col-gutter-lg">
            <!-- Member Info -->
            <div class="col-12 col-md-6">
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-h6 q-mb-md">Informasi Member</div>
                  <q-list>
                    <q-item>
                      <q-item-section>
                        <q-item-label class="text-weight-medium">ID Member</q-item-label>
                        <q-item-label caption>{{ selectedMember.member_id }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item>
                      <q-item-section>
                        <q-item-label class="text-weight-medium">Nama</q-item-label>
                        <q-item-label caption>{{ selectedMember.name }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item>
                      <q-item-section>
                        <q-item-label class="text-weight-medium">Email</q-item-label>
                        <q-item-label caption>{{ selectedMember.email || '-' }}</q-item-label>
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
                        <q-item-label class="text-weight-medium">Alamat</q-item-label>
                        <q-item-label caption>{{ selectedMember.address || '-' }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
              </q-card>
            </div>

            <!-- Membership Info -->
            <div class="col-12 col-md-6">
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-h6 q-mb-md">Informasi Keanggotaan</div>
                  <q-list>
                    <q-item>
                      <q-item-section>
                        <q-item-label class="text-weight-medium">Tipe Member</q-item-label>
                        <q-item-label caption>
                          <q-chip 
                            :color="getMembershipCategoryColor(selectedMember.membershipCategory)"
                            text-color="white"
                          >
                            {{ selectedMember.membershipType }}
                          </q-chip>
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item>
                      <q-item-section>
                        <q-item-label class="text-weight-medium">Periode</q-item-label>
                        <q-item-label caption>
                          {{ formatDate(selectedMember.start_date) }} - {{ formatDate(selectedMember.end_date) }}
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item>
                      <q-item-section>
                        <q-item-label class="text-weight-medium">Status</q-item-label>
                        <q-item-label caption>
                          <q-badge 
                            :color="getStatusColor(selectedMember)"
                            :label="getStatusLabel(selectedMember)"
                          />
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item>
                      <q-item-section>
                        <q-item-label class="text-weight-medium">Pembayaran</q-item-label>
                        <q-item-label caption>
                          <q-badge 
                            :color="getPaymentStatusColor(selectedMember.payment_status)"
                            :label="getPaymentStatusLabel(selectedMember.payment_status)"
                          />
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
              </q-card>
            </div>

            <!-- Vehicles -->
            <div class="col-12">
              <q-card flat bordered>
                <q-card-section>
                  <div class="text-h6 q-mb-md">Kendaraan Terdaftar</div>
                  <div class="row q-col-gutter-sm">
                    <div 
                      v-for="(vehicle, index) in selectedMember.vehicles"
                      :key="index"
                      class="col-12 col-sm-6 col-md-4"
                    >
                      <q-card flat bordered>
                        <q-card-section>
                          <div class="text-center">
                            <q-icon 
                              :name="getVehicleIcon(vehicle.type)"
                              size="2rem"
                              color="primary"
                            />
                            <div class="text-h6 q-mt-sm">{{ vehicle.license_plate }}</div>
                            <div class="text-caption">{{ vehicle.type?.label }}</div>
                            <div class="text-caption" v-if="vehicle.brand">
                              {{ vehicle.brand }} {{ vehicle.model }}
                            </div>
                            <div class="text-caption" v-if="vehicle.color">
                              {{ vehicle.color }}
                            </div>
                          </div>
                        </q-card-section>
                      </q-card>
                    </div>
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Tutup" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Dialog Upload Excel Bulk Input -->
    <q-dialog v-model="showUploadDialog">
      <q-card style="min-width:400px">
        <q-card-section class="bg-primary text-white">
          <div class="text-h6">Upload Excel Bulk Member</div>
        </q-card-section>
        <q-card-section>
          <p class="text-body2 q-mb-md">
            Silakan upload file Excel dengan format yang sesuai. 
            <a href="/template_bulk_member.xlsx.txt" target="_blank" class="text-primary">
              Download template Excel
            </a>
          </p>
          <q-uploader
            label="Pilih file Excel (*.xlsx)"
            accept=".xlsx,.xls"
            :auto-upload="false"
            @added="onExcelFileAdded"
            ref="excelUploader"
            style="width:100%"
          />
          <div v-if="excelUploadError" class="text-negative q-mt-sm">{{ excelUploadError }}</div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Batal" color="primary" v-close-popup @click="resetExcelUpload" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useQuasar } from 'quasar'
import { useMembershipStore } from 'src/stores/membership-store'
import DatabaseInitializer from 'src/components/DatabaseInitializer.vue'


import {  getCurrentInstance } from 'vue'
import * as XLSX from 'xlsx'

const showUploadDialog = ref(false)
const excelUploadError = ref('')
const excelUploader = ref(null)
const { proxy } = getCurrentInstance() || {}

function resetExcelUpload() {
  excelUploadError.value = ''
  showUploadDialog.value = false
  if (excelUploader.value) excelUploader.value.reset()
}

async function onExcelFileAdded(files) {
  excelUploadError.value = ''
  if (!files || !files.length) return
  const file = files[0]
  if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
    excelUploadError.value = 'File harus berformat .xlsx atau .xls'
    return
  }
  try {
    const data = await file.arrayBuffer()
    const workbook = XLSX.read(data, { type: 'array', cellDates: true })
    const sheetName = workbook.SheetNames[0]
    const sheet = workbook.Sheets[sheetName]
    const json = XLSX.utils.sheet_to_json(sheet, { defval: '' })
    
    // Validasi minimal kolom wajib: name, phone, membership_type_id
    const requiredFields = ['name', 'phone', 'membership_type_id']
    const invalidRows = json.filter(row => requiredFields.some(f => !row[f]))
    if (invalidRows.length > 0) {
      excelUploadError.value = 'Ada baris yang tidak lengkap (name, phone, membership_type_id wajib diisi)'
      return
    }

    // Proses bulk insert
    let success = 0, failed = 0
    for (const row of json) {
      try {
        const memberData = { ...row };

        // Convert date objects to ISO strings (YYYY-MM-DD)
        if (memberData.start_date instanceof Date) {
          memberData.start_date = memberData.start_date.toISOString().split('T')[0];
        }
        if (memberData.end_date instanceof Date) {
          memberData.end_date = memberData.end_date.toISOString().split('T')[0];
        }

        // 1. Reconstruct emergency_contact object
        memberData.emergency_contact = {
          name: row.emergency_contact_name || '',
          phone: row.emergency_contact_phone || '',
          relationship: row.emergency_contact_relationship || ''
        };
        delete memberData.emergency_contact_name;
        delete memberData.emergency_contact_phone;
        delete memberData.emergency_contact_relationship;

        // 2. Reconstruct vehicles array
        memberData.vehicles = [];
        const maxVehicles = 5; // Or get from config
        for (let i = 1; i <= maxVehicles; i++) {
          const license_plate = row[`vehicle_${i}_license_plate`];
          if (license_plate) {
            memberData.vehicles.push({
              license_plate: license_plate,
              type: row[`vehicle_${i}_type`] || '',
              brand: row[`vehicle_${i}_brand`] || '',
              model: row[`vehicle_${i}_model`] || '',
              color: row[`vehicle_${i}_color`] || ''
            });
          }
          // Delete the flat vehicle properties
          delete memberData[`vehicle_${i}_license_plate`];
          delete memberData[`vehicle_${i}_type`];
          delete memberData[`vehicle_${i}_brand`];
          delete memberData[`vehicle_${i}_model`];
          delete memberData[`vehicle_${i}_color`];
        }

        await membershipStore.addMember(memberData)
        success++
      } catch (e) {
        console.error('Failed to import row:', row, e);
        failed++
      }
    }
    resetExcelUpload()
    $q.notify({
      type: 'positive',
      message: `Import selesai: ${success} berhasil, ${failed} gagal.`
    })
  } catch (err) {
    excelUploadError.value = 'Gagal membaca file: ' + err.message
  }
}

const $q = useQuasar()
const membershipStore = useMembershipStore()

// Reactive references
const searchText = ref('')
const filterType = ref('')
const filterStatus = ref('')
const showAddNewMemberDialog = ref(false)
const showAddTypeDialog = ref(false)
const showMemberDetailDialog = ref(false
)
const isEditing = ref(false)
const selectedMember = ref(null)

// Use store computed properties
const members = computed(() => membershipStore.members)
const membershipTypes = computed(() => membershipStore.membershipTypes)
const membershipCategories = computed(() => membershipStore.membershipCategories)
const loading = computed(() => membershipStore.isLoading || membershipStore.isLoadingMembers || membershipStore.isLoadingTypes)
const statistics = computed(() => ({
  totalMembers: membershipStore.statistics.totalMembers,
  activeMembers: membershipStore.statistics.activeMembers,
  expiringSoon: membershipStore.statistics.expiringMembers,
  expiredMembers: membershipStore.statistics.expiredMembers,
  totalRevenue: membershipStore.statistics.totalRevenue,
  revenueThisMonth: membershipStore.statistics.revenueThisMonth
}))

// Form models
const memberForm = ref({
  member_id: '',
  card_number: '',
  name: '',
  email: '',
  phone: '',
  address: '',
  identity_number: '',
  vehicles: [{
    type: '',
    license_plate: '',
    brand: '',
    model: '',
    color: '',
    year: ''
  }],
  membership_type_id: '',
  start_date: '',
  end_date: '',
  payment_status: 'pending',
  notes: '',
  emergency_contact: {
    name: '',
    phone: '',
    relationship: ''
  },
  active: 1
})

const typeForm = ref({
  name: '',
  price: 0,
  category: 'REGULAR',
  area_type: 'residential',
  max_vehicles: 1,
  operating_hours: {
    start: '00:00',
    end: '23:59'
  },
  duration_months: 12,
  description: '',
  facilities: [],
  benefits: [],
  access_areas: []
})

// Options
const vehicleTypeOptions = [
  { label: 'Mobil', value: 'Mobil' },
  { label: 'Motor', value: 'Motor' },
  { label: 'Truk', value: 'Truk' },
  { label: 'Bus', value: 'Bus' }
]

const paymentStatusOptions = [
  { label: 'Pending', value: 'pending' },
  { label: 'Lunas', value: 'paid' },
  { label: 'Terlambat', value: 'overdue' }
]

const statusOptions = [
  { label: 'Aktif', value: 'active' },
  { label: 'Tidak Aktif', value: 'inactive' },
  { label: 'Akan Berakhir', value: 'expiring' },
  { label: 'Kadaluarsa', value: 'expired' }
]

const areaTypeOptions = [
  { label: 'Residensial', value: 'residential' },
  { label: 'Komersial', value: 'commercial' }
]

const facilityOptions = [
  'CCTV 24 Jam',
  'Keamanan',
  'Valet Parking',
  'Cuci Mobil',
  'Pengisian EV',
  'Wi-Fi Gratis',
  'Toilet Bersih',
  'Mushola',
  'Area Tunggu'
]

const benefitOptions = [
  'Diskon 10%',
  'Diskon 20%',
  'Gratis Valet',
  'Priority Access',
  'Extended Hours',
  'Guest Parking',
  'Premium Support'
]

// Computed properties for filtering
const membershipTypeOptions = computed(() => [
  { label: 'Semua Tipe', value: '' },
  ...membershipTypes.value.map(type => ({
    label: type.name,
    value: type._id
  }))
])

const filteredMembers = computed(() => {
  let filtered = members.value

  // Enrich members with membership type information
  filtered = filtered.map(member => {
    const membershipType = membershipTypes.value.find(type => type._id === member.membership_type_id)
    return {
      ...member,
      membershipType: membershipType?.name || 'Unknown',
      membershipCategory: membershipType?.category || 'REGULAR'
    }
  })

  // Search filter
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(member => 
      member.name.toLowerCase().includes(search) ||
      member.member_id.toLowerCase().includes(search) ||
      member.phone.includes(search) ||
      (member.email && member.email.toLowerCase().includes(search)) ||
      member.vehicles.some(vehicle => 
        vehicle.license_plate.toLowerCase().includes(search)
      )
    )
  }

  // Type filter
  if (filterType.value) {
    filtered = filtered.filter(member => 
      member.membership_type_id === filterType.value
    )
  }

  // Status filter
  if (filterStatus.value) {
    filtered = filtered.filter(member => {
      switch (filterStatus.value) {
        case 'active':
          return member.active === 1 && !membershipStore.isExpired(member.end_date)
        case 'inactive':
          return member.active === 0
        case 'expiring':
          return membershipStore.isExpiringSoon(member.end_date)
        case 'expired':
          return membershipStore.isExpired(member.end_date)
        default:
          return true
      }
    })
  }

  return filtered
})

// Table columns
const columns = [
  { 
    name: 'index', 
    label: 'No', 
    field: 'index',
    sortable: false,
    align: 'center'
  },
  { 
    name: 'member_info', 
    label: 'Member', 
    field: 'name', 
    sortable: true,
    align: 'left'
  },
  { 
    name: 'membership_type', 
    label: 'Tipe', 
    field: 'membership_type', 
    sortable: true,
    align: 'center'
  },
  { 
    name: 'vehicles', 
    label: 'Kendaraan', 
    field: 'vehicles',
    sortable: false,
    align: 'center'
  },
  { 
    name: 'expiry', 
    label: 'Berakhir', 
    field: 'end_date', 
    sortable: true,
    align: 'center'
  },
  { 
    name: 'status', 
    label: 'Status', 
    field: 'active',
    sortable: true,
    align: 'center'
  },
  { 
    name: 'actions', 
    label: 'Aksi', 
    field: 'actions',
    sortable: false,
    align: 'center'
  }
]

// Action functions
const openAddMemberDialog = () => {
  isEditing.value = false
  memberForm.value = {
    member_id: '',
    card_number: '',
    name: '',
    email: '',
    phone: '',
    address: '',
    identity_number: '',
    vehicles: [{
      type: '',
      license_plate: '',
      brand: '',
      model: '',
      color: '',
      year: ''
    }],
    membership_type_id: '',
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
    payment_status: 'pending',
    notes: '',
    emergency_contact: {
      name: '',
      phone: '',
      relationship: ''
    },
    active: 1
  }
  showAddNewMemberDialog.value = true
}

const closeAddMemberDialog = () => {
  showAddNewMemberDialog.value = false
  memberForm.value = {
    member_id: '',
    card_number: '',
    name: '',
    email: '',
    phone: '',
    address: '',
    identity_number: '',
    vehicles: [{
      type: '',
      license_plate: '',
      brand: '',
      model: '',
      color: '',
      year: ''
    }],
    membership_type_id: '',
    start_date: '',
    end_date: '',
    payment_status: 'pending',
    notes: '',
    emergency_contact: {
      name: '',
      phone: '',
      relationship: ''
    },
    active: 1
  }
}

const closeAddTypeDialog = () => {
  showAddTypeDialog.value = false
  typeForm.value = {
    name: '',
    price: 0,
    category: 'REGULAR',
    area_type: 'residential',
    max_vehicles: 1,
    operating_hours: {
      start: '00:00',
      end: '23:59'
    },
    duration_months: 12,
    description: '',
    facilities: [],
    benefits: [],
    access_areas: []
  }
}

const addVehicle = () => {
  if (!memberForm.value.membership_type_id) {
    $q.notify({
      type: 'warning',
      message: 'Pilih tipe membership terlebih dahulu'
    })
    return
  }
  
  const membershipType = membershipTypes.value.find(t => t._id === memberForm.value.membership_type_id)
  if (membershipType && memberForm.value.vehicles.length >= membershipType.max_vehicles) {
    $q.notify({
      type: 'warning',
      message: `Maksimal ${membershipType.max_vehicles} kendaraan untuk tipe membership ini`
    })
    return
  }
  
  memberForm.value.vehicles.push({
    type: '',
    license_plate: '',
    brand: '',
    model: '',
    color: '',
    year: ''
  })
}

const removeVehicle = (index) => {
  if (memberForm.value.vehicles.length > 1) {
    memberForm.value.vehicles.splice(index, 1)
  }
}

const viewMember = (member) => {
  // Enrich member data with membership type information
  const membershipType = membershipTypes.value.find(type => type._id === member.membership_type_id)
  selectedMember.value = {
    ...member,
    membershipType: membershipType?.name || 'Unknown',
    membershipCategory: membershipType?.category || 'REGULAR'
  }
  showMemberDetailDialog.value = true
}

const editMember = (member) => {
  console.log("🚀 ~ editMember ~ member:", member)
  isEditing.value = true
  memberForm.value = { ...member }
  showAddNewMemberDialog.value = true
}

const saveMember = async () => {
  try {
    const memberData = {
      ...memberForm.value,
      vehicles: memberForm.value.vehicles.map(vehicle => ({
        ...vehicle,
        license_plate: vehicle.license_plate.toUpperCase()
      }))
    }

    if (isEditing.value) {
      await membershipStore.updateMember(memberData._id, memberData)
    } else {
      await membershipStore.addMember(memberData)
    }
    
    $q.notify({
      type: 'positive',
      message: `Member ${isEditing.value ? 'berhasil diupdate' : 'berhasil ditambahkan'}`
    })
    
    closeAddMemberDialog()
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: `Gagal ${isEditing.value ? 'mengupdate' : 'menambahkan'} member`
    })
  }
}

const saveNewType = async () => {
  try {
    await membershipStore.addMembershipType(typeForm.value)
    $q.notify({
      type: 'positive',
      message: 'Tipe membership berhasil ditambahkan'
    })
    closeAddTypeDialog()
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Gagal menambahkan tipe membership'
    })
  }
}

const renewMembership = async (member) => {
  console.log("🚀 ~ renewMembership ~ member:", member)
  $q.dialog({
    title: 'Perpanjang Membership',
    message: `Perpanjang membership ${member.name} selama berapa bulan?`,
    prompt: {
      model: '12',
      type: 'number'
    },
    cancel: true,
    persistent: true
  }).onOk(async (months) => {
    console.log("🚀 ~ renewMembership ~ months:", months)
    try {
      await membershipStore.renewMembership(member._id, parseInt(months))
      $q.notify({
        type: 'positive',
        message: 'Membership berhasil diperpanjang'
      })
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: 'Gagal memperpanjang membership'
      })
    }
  })
}

const confirmDelete = (member) => {
  $q.dialog({
    title: 'Konfirmasi Hapus',
    message: `Yakin ingin menghapus member ${member.name}?`,
    ok: 'Hapus',
    cancel: 'Batal',
    color: 'negative'
  }).onOk(async () => {
    try {
      await membershipStore.deleteMember(member._id)
      $q.notify({
        type: 'positive',
        message: 'Member berhasil dihapus'
      })
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: 'Gagal menghapus member'
      })
    }
  })
}


// Methods
const handleDatabaseInitialized = async () => {
  try {
    // Reload store data after database initialization
    await membershipStore.initializeStore()
    $q.notify({
      type: 'positive',
      message: 'Data member telah dimuat ulang'
    })
  } catch (error) {
    console.error('Failed to reload member data:', error)
  }
}

const resetFilters = () => {
  searchText.value = ''
  filterType.value = ''
  filterStatus.value = ''
}

const exportData = () => {
  // TODO: Implement export functionality
  $q.notify({
    type: 'info',
    message: 'Fitur export sedang dalam pengembangan'
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
  if (membershipStore.isExpired(member.end_date)) return 'red'
  if (membershipStore.isExpiringSoon(member.end_date)) return 'orange'
  return 'green'
}

const getStatusLabel = (member) => {
  if (member.active === 0) return 'Tidak Aktif'
  if (membershipStore.isExpired(member.end_date)) return 'Kadaluarsa'
  if (membershipStore.isExpiringSoon(member.end_date)) return 'Akan Berakhir'
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

const getExpiryTextClass = (member) => {
  if (membershipStore.isExpired(member.end_date)) return 'text-negative'
  if (membershipStore.isExpiringSoon(member.end_date)) return 'text-warning'
  return 'text-positive'
}

const getExpiryText = (member) => {
  const days = membershipStore.calculateDaysUntilExpiry(member.end_date)
  if (days === null) return '-'
  if (days < 0) return `Lewat ${Math.abs(days)} hari`
  if (days === 0) return 'Hari ini'
  if (days === 1) return 'Besok'
  return `${days} hari lagi`
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('id-ID')
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR'
  }).format(amount || 0)
}

// Lifecycle
onMounted(async () => {
  try {
    await membershipStore.initializeStore()
  } catch (error) {
    console.error('Failed to initialize membership store:', error)
    $q.notify({
      type: 'negative',
      message: 'Gagal memuat data membership'
    })
  }
})
</script>