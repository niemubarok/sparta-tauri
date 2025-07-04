<template>
  <q-dialog
    ref="dialogRef"
    maximized
    @hide="onDialogHide"
    :persistent="false"
    :no-esc-dismiss="false"
    :key="componentStore.settingsKey"
  >
    <div class="row justify-center items-center full-height">
      <q-card
        class="q-px-lg q-py-md glass relative"
        style="width: 95vw; max-width: 1400px; height: 90vh; overflow: hidden;"
      >
        <!-- Header -->
        <div class="row items-center q-mb-lg">
          <q-icon name="settings" size="md" color="primary" class="q-mr-md" />
          <div class="text-h5 text-weight-bold" style="color: #1976d2;">
            Pengaturan Sistem Parkir
          </div>
          <q-space />
          <q-btn
            round
            flat
            icon="close"
            color="grey-7"
            size="md"
            @click="dialogRef.hide()"
          />
        </div>

        <!-- Main Content with Scroll -->
        <div class="settings-content" style="height: calc(100% - 120px); overflow-y: auto;">
          <div class="row q-col-gutter-lg">
            <!-- Left Column -->
            <div class="col-12 col-lg-6">
              
              <!-- ALPR Settings Card -->
              <q-card class="settings-card q-mb-lg" flat bordered>
                <q-card-section>
                  <div class="settings-section-title">
                    <q-icon name="auto_awesome" class="q-mr-sm" />
                    Pengaturan ALPR
                  </div>
                  
                  <div class="q-mt-md">
                    <q-toggle
                      v-model="useExternalAlpr"
                      label="Gunakan Service ALPR Eksternal"
                      color="primary"
                      size="md"
                    />
                    <div class="text-caption text-grey-6 q-mt-xs q-ml-lg">
                      {{ useExternalAlpr ? 'Menggunakan service WebSocket ALPR eksternal' : 'Menggunakan service ALPR internal Tauri' }}
                    </div>
                  </div>

                  <div v-show="useExternalAlpr" class="q-mt-md">
                    <q-input
                      v-model="wsUrl"
                      label="WebSocket URL"
                      placeholder="ws://localhost:8001/ws"
                      outlined
                      dense
                    />
                  </div>
                </q-card-section>
              </q-card>

              <!-- CouchDB Settings Card -->
              <q-card class="settings-card q-mb-lg" flat bordered>
                <q-card-section>
                  <div class="settings-section-title">
                    <q-icon name="storage" class="q-mr-sm" />
                    Pengaturan CouchDB
                  </div>
                  
                  <div class="row q-col-gutter-md q-mt-md">
                    <div class="col-12 col-sm-6">
                      <q-input
                        v-model="couchDbUrl"
                        label="CouchDB Host/IP"
                        placeholder="localhost"
                        outlined
                        dense
                      />
                    </div>
                    <div class="col-12 col-sm-6">
                      <q-input
                        v-model="couchDbPort"
                        label="CouchDB Port"
                        placeholder="5984"
                        type="number"
                        outlined
                        dense
                      />
                    </div>
                    <div class="col-12 col-sm-6">
                      <q-input
                        v-model="couchDbUsername"
                        label="Username"
                        placeholder="admin"
                        outlined
                        dense
                      />
                    </div>
                    <div class="col-12 col-sm-6">
                      <q-input
                        v-model="couchDbPassword"
                        label="Password"
                        placeholder="admin"
                        type="password"
                        outlined
                        dense
                      />
                    </div>
                    <div class="col-12">
                      <div class="text-caption text-grey-6">
                        Current connection: {{ couchDbConnectionString }}
                      </div>
                      <q-btn
                        class="q-mt-sm"
                        color="primary"
                        size="sm"
                        label="Test Connection"
                        icon="sync"
                        @click="testCouchDbConnection"
                        :loading="testingCouchDbConnection"
                      />
                    </div>
                  </div>
                </q-card-section>
              </q-card>

              <!-- Gate Settings Card -->
              <q-card class="settings-card q-mb-lg" flat bordered>
                <q-card-section>
                  <div class="settings-section-title">
                    <q-icon name="door_front" class="q-mr-sm" />
                    Pengaturan Gerbang
                  </div>
                  
                  <div class="row q-col-gutter-md q-mt-md">
                    <div class="col-12 col-sm-6">
                      <q-input
                        v-model="gateName"
                        label="Nama Gerbang"
                        outlined
                        dense
                      />
                    </div>
                    <div class="col-12 col-sm-6">
                      <q-select
                        v-model="gateType"
                        :options="[
                          { label: 'Gerbang Masuk', value: 'entry' },
                          { label: 'Gerbang Keluar', value: 'exit' }
                        ]"
                        label="Tipe Gerbang"
                        outlined
                        dense
                        emit-value
                        map-options
                      />
                    </div>
                    <div class="col-12 col-sm-6">
                      <q-input
                        v-model="prefix"
                        label="Prefix Default"
                        placeholder="Contoh: A, B, C"
                        outlined
                        dense
                      />
                    </div>
                    <div class="col-12 col-sm-6">
                      <q-input
                        v-model="serialPort"
                        label="Serial Port"
                        placeholder="COM3 atau /dev/ttyUSB0"
                        outlined
                        dense
                        :rules="[val => !!val || 'Serial port wajib diisi']"
                      />
                    </div>
                  </div>
                </q-card-section>
              </q-card>

              <!-- Operation Mode Card -->
              <q-card class="settings-card q-mb-lg" flat bordered>
                <q-card-section>
                  <div class="settings-section-title">
                    <q-icon name="settings_applications" class="q-mr-sm" />
                    Mode Operasi
                  </div>
                  
                  <div class="row q-col-gutter-md q-mt-md">
                    <div class="col-12" :class="operationMode === 'manual' ? 'col-sm-6' : ''">
                      <q-select
                        v-model="operationMode"
                        :options="operationModeOptions"
                        label="Mode Operasi"
                        outlined
                        dense
                        emit-value
                        map-options
                      />
                      <div class="text-caption text-grey-6 q-mt-xs">
                        {{ operationMode === 'manless' ? 'Mode otomatis dengan ALPR tanpa petugas' : 'Mode manual dengan input petugas' }}
                      </div>
                    </div>
                    <div class="col-12 col-sm-6" v-show="operationMode === 'manual'">
                      <q-select
                        v-model="manualPaymentMode"
                        :options="manualPaymentModeOptions"
                        label="Mode Pembayaran"
                        outlined
                        dense
                        emit-value
                        map-options
                      />
                      <div class="text-caption text-grey-6 q-mt-xs">
                        {{ manualPaymentMode === 'prepaid' ? 'Bayar di depan dengan tarif tetap' : 'Bayar di belakang dengan tarif progresif' }}
                      </div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>

              <!-- Printer Settings Card -->
              <q-card class="settings-card q-mb-lg" flat bordered>
                <q-card-section>
                  <div class="settings-section-title">
                    <q-icon name="print" class="q-mr-sm" />
                    Pengaturan Printer & Test EPSON TM-T82X
                  </div>
                  
                  <!-- Quick Actions -->
                  <div class="row q-gutter-sm q-mt-md">
                    <q-btn
                      color="secondary"
                      label="Discover Printers"
                      icon="search"
                      @click="discoverPrinters"
                      :loading="discovering"
                      size="sm"
                    />
                    
                    <q-btn
                      color="info"
                      label="List Thermal"
                      icon="print"
                      @click="listThermalPrinters"
                      :loading="loadingPrinters"
                      size="sm"
                    />

                    <q-btn
                      color="primary"
                      label="Check EPSON"
                      icon="local_print_shop"
                      @click="checkEpsonPrinters"
                      :loading="checkingEpson"
                      size="sm"
                    />
                    
                    <q-btn
                      color="orange"
                      label="Clear Cache"
                      icon="refresh"
                      @click="clearPrinterCache"
                      :disable="discovering || loadingPrinters || checkingEpson"
                      size="sm"
                    />
                  </div>

                  <!-- Printer Selection -->
                  <div class="row q-col-gutter-md q-mt-md">
                    <div class="col-12 col-sm-6">
                      <q-select
                        v-model="selectedPrinter"
                        :options="availablePrinters"
                        label="Pilih Printer"
                        filled
                        emit-value
                        map-options
                        @update:model-value="onPrinterSelected"
                      >
                        <template v-slot:no-option>
                          <q-item>
                            <q-item-section class="text-grey">
                              Tidak ada printer ditemukan. Klik "Discover Printers".
                            </q-item-section>
                          </q-item>
                        </template>
                        
                        <template v-slot:prepend>
                          <q-icon 
                            :name="getSelectedPrinterIcon()"
                            :color="getSelectedPrinterColor()"
                          />
                        </template>
                        
                        <template v-slot:append>
                          <q-btn
                            flat
                            round
                            dense
                            icon="cable"
                            @click.stop="testPrinterConnection"
                            :loading="testingConnection"
                            :disable="!selectedPrinter"
                            title="Test printer connection"
                            size="sm"
                          />
                        </template>
                      </q-select>
                    </div>
                    
                    <div class="col-12 col-sm-6">
                      <q-select
                        v-model="paperSize"
                        :options="[
                          { label: '58mm (Kecil)', value: '58mm' },
                          { label: '80mm (Besar)', value: '80mm' }
                        ]"
                        label="Ukuran Kertas"
                        outlined
                        dense
                        emit-value
                        map-options
                      />
                    </div>
                  </div>

                  <!-- Test Section -->
                  <div class="row q-col-gutter-md q-mt-md">
                    <div class="col-12 col-sm-6">
                      <q-input
                        v-model="testBarcode"
                        label="Test Barcode"
                        outlined
                        dense
                        placeholder="SPARTA-TEST123"
                      >
                        <template v-slot:append>
                          <q-btn
                            flat
                            round
                            dense
                            icon="refresh"
                            @click="generateTestBarcode"
                            title="Generate random barcode"
                            size="sm"
                          />
                        </template>
                      </q-input>
                    </div>
                    
                    <div class="col-12 col-sm-6">
                      <q-toggle
                        v-model="autoPrint"
                        label="Auto Print Tiket"
                        color="primary"
                        size="md"
                      />
                    </div>
                  </div>
                  
                  <!-- Action Buttons -->
                  <div class="row q-gutter-sm q-mt-md">
                    <q-btn
                      color="primary"
                      label="Test Print"
                      icon="receipt"
                      @click="testPrintBarcode"
                      :loading="printing"
                      :disable="!testBarcode || !selectedPrinter"
                      size="sm"
                    />
                    
                    <q-btn
                      color="orange"
                      label="Test Connection"
                      icon="cable"
                      @click="testPrinterConnection"
                      :loading="testingConnection"
                      :disable="!selectedPrinter"
                      size="sm"
                    />

                    <q-btn
                      color="positive"
                      label="Set as Default"
                      icon="bookmark"
                      @click="setAsDefaultPrinter"
                      :disable="!selectedPrinter"
                      size="sm"
                    />
                  </div>

                  <!-- Current Default Printer -->
                  <div v-if="defaultPrinter" class="q-mt-md">
                    <q-chip 
                      icon="bookmark"
                      color="primary"
                      text-color="white"
                      size="sm"
                    >
                      Default: {{ defaultPrinter }}
                    </q-chip>
                  </div>

                  <!-- EPSON Printers Section -->
                  <div v-if="epsonPrinters.length > 0" class="q-mt-md">
                    <div class="text-subtitle2 q-mb-sm text-primary">
                      <q-icon name="local_print_shop" class="q-mr-xs" />
                      EPSON TM-T82X Found ({{ epsonPrinters.length }})
                    </div>
                    <q-list dense bordered class="rounded-borders">
                      <q-item
                        v-for="printer in epsonPrinters"
                        :key="printer"
                        clickable
                        @click="selectedPrinter = printer"
                        :class="selectedPrinter === printer ? 'bg-primary text-white' : ''"
                      >
                        <q-item-section avatar>
                          <q-icon name="local_print_shop" :color="selectedPrinter === printer ? 'white' : 'primary'" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>{{ printer }}</q-item-label>
                        </q-item-section>
                        <q-item-section side>
                          <q-btn
                            flat
                            round
                            dense
                            icon="print"
                            @click.stop="quickTestPrint(printer)"
                            :loading="printing === printer"
                            size="sm"
                            :color="selectedPrinter === printer ? 'white' : 'primary'"
                          />
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </div>

                  <!-- Status Messages -->
                  <div v-if="lastTestResult" class="q-mt-md">
                    <q-banner 
                      :class="lastTestResult.success ? 'bg-positive text-white' : 'bg-negative text-white'"
                      rounded
                    >
                      <template v-slot:avatar>
                        <q-icon :name="lastTestResult.success ? 'check_circle' : 'error'" />
                      </template>
                      {{ lastTestResult.message }}
                    </q-banner>
                  </div>
                </q-card-section>
              </q-card>

            </div>

            <!-- Right Column -->
            <div class="col-12 col-lg-6">
              
              <!-- Camera Settings Card -->
              <q-card class="settings-card q-mb-lg" flat bordered>
                <q-card-section>
                  <div class="settings-section-title">
                    <q-icon name="videocam" class="q-mr-sm" />
                    Pengaturan Kamera
                  </div>
                  
                  <!-- Camera Controls -->
                  <div class="row q-col-gutter-md q-mt-md">
                    <div class="col-12 col-sm-6">
                      <q-input
                        v-model.number="captureInterval"
                        type="number"
                        label="Interval Capture (ms)"
                        placeholder="5000 = 5 detik"
                        outlined
                        dense
                      />
                    </div>
                    <div class="col-12 col-sm-6">
                      <q-btn 
                        color="primary" 
                        label="Refresh Kamera" 
                        icon="refresh"
                        @click="getCameras"
                        size="md"
                        style="width: 100%"
                      />
                      <div class="text-caption text-center q-mt-xs">
                        {{ availableCameras.length }} kamera terdeteksi
                      </div>
                    </div>
                  </div>
                </q-card-section>
              </q-card>

              <!-- Camera Configurations -->
              <q-expansion-item
                v-for="(cameraType, index) in [
                  { name: 'plate', label: 'Kamera Plat Nomor', icon: 'pin' },
                  { name: 'driver', label: 'Kamera Driver', icon: 'person' },
                  { name: 'scanner', label: 'Kamera Scanner QR', icon: 'qr_code_scanner' }
                ]"
                :key="cameraType.name"
                :default-opened="index === 0"
                class="settings-expansion q-mb-md"
              >
                <template v-slot:header>
                  <q-item-section avatar>
                    <q-icon :name="cameraType.icon" color="primary" />
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-weight-medium">{{ cameraType.label }}</q-item-label>
                  </q-item-section>
                </template>

                <q-card flat bordered class="q-ma-sm">
                  <q-card-section>
                    <!-- Camera Type Selection -->
                    <div class="camera-config-section q-mb-md">
                      <div class="text-subtitle2 text-weight-medium q-mb-sm">Tipe Kamera</div>
                      <q-option-group
                        :model-value="cameraType.name === 'plate' ? plateCameraMode : 
                                     cameraType.name === 'driver' ? driverCameraMode : scannerCameraMode"
                        @update:model-value="val => {
                          if (cameraType.name === 'plate') plateCameraMode = val;
                          else if (cameraType.name === 'driver') driverCameraMode = val;
                          else scannerCameraMode = val;
                        }"
                        :options="[
                          { label: 'CCTV (IP Camera)', value: 'cctv' },
                          { label: 'USB Camera', value: 'usb' }
                        ]"
                        color="primary"
                        inline
                      />
                    </div>

                    <!-- USB Camera Selection -->
                    <div 
                      v-show="(cameraType.name === 'plate' && plateCameraMode === 'usb') || 
                              (cameraType.name === 'driver' && driverCameraMode === 'usb') || 
                              (cameraType.name === 'scanner' && scannerCameraMode === 'usb')"
                      class="camera-config-section q-mb-md"
                    >
                      <div class="text-subtitle2 text-weight-medium q-mb-sm">USB Kamera</div>
                      <q-select
                        :model-value="cameraType.name === 'plate' ? selectedPlateCam : 
                                      cameraType.name === 'driver' ? selectedDriverCam : selectedScannerCam"
                        @update:model-value="cameraType.name === 'plate' ? updatePlateCamera : 
                                           cameraType.name === 'driver' ? updateDriverCamera : updateScannerCamera"
                        :options="availableCameras"
                        label="Pilih USB Camera"
                        option-value="deviceId"
                        option-label="label"
                        clearable
                        emit-value
                        map-options
                        outlined
                        dense
                      />
                      <div class="text-caption text-grey-6 q-mt-xs" v-if="availableCameras.length === 0">
                        Tidak ada USB kamera terdeteksi. Klik "Refresh Kamera" untuk coba lagi.
                      </div>
                    </div>

                    <!-- CCTV Configuration -->
                    <div 
                      v-show="(cameraType.name === 'plate' && plateCameraMode === 'cctv') || 
                              (cameraType.name === 'driver' && driverCameraMode === 'cctv') || 
                              (cameraType.name === 'scanner' && scannerCameraMode === 'cctv')"
                      class="camera-config-section q-mb-md"
                    >
                      <div class="text-subtitle2 text-weight-medium q-mb-sm">Konfigurasi CCTV</div>
                      <div class="row q-col-gutter-sm">
                        <div class="col-12 col-sm-6">
                          <q-input
                            :model-value="cameraType.name === 'plate' ? plateCameraIp : 
                                         cameraType.name === 'driver' ? driverCameraIp : scannerCameraIp"
                            @update:model-value="val => {
                              if (cameraType.name === 'plate') plateCameraIp = val;
                              else if (cameraType.name === 'driver') driverCameraIp = val;
                              else scannerCameraIp = val;
                            }"
                            label="IP Address CCTV"
                            placeholder="192.168.1.100"
                            outlined
                            dense
                          />
                        </div>
                        <div class="col-12 col-sm-6">
                          <q-input
                            :model-value="cameraType.name === 'plate' ? plateCameraRtspPath : 
                                         cameraType.name === 'driver' ? driverCameraRtspPath : scannerCameraRtspPath"
                            @update:model-value="val => {
                              if (cameraType.name === 'plate') plateCameraRtspPath = val;
                              else if (cameraType.name === 'driver') driverCameraRtspPath = val;
                              else scannerCameraRtspPath = val;
                            }"
                            label="RTSP Path"
                            placeholder="/Streaming/Channels/101"
                            outlined
                            dense
                          />
                        </div>
                        <div class="col-12 col-sm-6">
                          <q-input
                            :model-value="cameraType.name === 'plate' ? plateCameraUsername : 
                                         cameraType.name === 'driver' ? driverCameraUsername : scannerCameraUsername"
                            @update:model-value="val => {
                              if (cameraType.name === 'plate') plateCameraUsername = val;
                              else if (cameraType.name === 'driver') driverCameraUsername = val;
                              else scannerCameraUsername = val;
                            }"
                            label="Username"
                            placeholder="admin"
                            outlined
                            dense
                          />
                        </div>
                        <div class="col-12 col-sm-6">
                          <q-input
                            :model-value="cameraType.name === 'plate' ? plateCameraPassword : 
                                         cameraType.name === 'driver' ? driverCameraPassword : scannerCameraPassword"
                            @update:model-value="val => {
                              if (cameraType.name === 'plate') plateCameraPassword = val;
                              else if (cameraType.name === 'driver') driverCameraPassword = val;
                              else scannerCameraPassword = val;
                            }"
                            label="Password"
                            type="password"
                            outlined
                            dense
                          />
                        </div>
                      </div>
                    </div>

                    <!-- Capture Mode Configuration -->
                    <div class="camera-config-section">
                      <div class="text-subtitle2 text-weight-medium q-mb-sm">Mode Capture Default</div>
                      <div class="row q-col-gutter-sm">
                        <div class="col-12 col-sm-4">
                          <q-select
                            :model-value="cameraType.name === 'plate' ? plateCameraDefaultMode : 
                                         cameraType.name === 'driver' ? driverCameraDefaultMode : scannerCameraDefaultMode"
                            @update:model-value="val => {
                              if (cameraType.name === 'plate') plateCameraDefaultMode = val;
                              else if (cameraType.name === 'driver') driverCameraDefaultMode = val;
                              else scannerCameraDefaultMode = val;
                            }"
                            :options="captureModeOptions"
                            label="Mode Default"
                            emit-value
                            map-options
                            outlined
                            dense
                          />
                          <div class="text-caption text-grey-6 q-mt-xs">
                            Metode capture default untuk kamera ini
                          </div>
                        </div>
                        <div class="col-12 col-sm-4">
                          <q-input
                            :model-value="cameraType.name === 'plate' ? plateCameraSnapshotUrl : 
                                         cameraType.name === 'driver' ? driverCameraSnapshotUrl : scannerCameraSnapshotUrl"
                            @update:model-value="val => {
                              if (cameraType.name === 'plate') plateCameraSnapshotUrl = val;
                              else if (cameraType.name === 'driver') driverCameraSnapshotUrl = val;
                              else scannerCameraSnapshotUrl = val;
                            }"
                            label="Custom Snapshot URL"
                            placeholder="/cgi-bin/snapshot.cgi"
                            outlined
                            dense
                          />
                        </div>
                        <div class="col-12 col-sm-4">
                          <q-input
                            :model-value="cameraType.name === 'plate' ? plateCameraHttpPort : 
                                         cameraType.name === 'driver' ? driverCameraHttpPort : scannerCameraHttpPort"
                            @update:model-value="val => {
                              if (cameraType.name === 'plate') plateCameraHttpPort = val;
                              else if (cameraType.name === 'driver') driverCameraHttpPort = val;
                              else scannerCameraHttpPort = val;
                            }"
                            type="number"
                            label="HTTP Port"
                            placeholder="80"
                            outlined
                            dense
                          />
                        </div>
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
              </q-expansion-item>

            </div>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="row justify-end q-pt-md" style="border-top: 1px solid #e0e0e0;">
          <q-btn
            @click="onSaveSettings"
            color="primary"
            size="lg"
            icon="save"
            label="Simpan Pengaturan"
            class="q-px-xl"
            :loading="false"
          />
        </div>
      </q-card>
    </div>
  </q-dialog>
</template>

<script setup>
import { useDialogPluginComponent, useQuasar, Notify } from "quasar";
// import SuccessCheckMark from "./SuccessCheckMark.vue";
import {
  onMounted,
  onUnmounted,
  computed,
  ref,
  watch,
  toRefs, // Ditambahkan
} from "vue";
import { useComponentStore } from "src/stores/component-store";
import { invoke } from '@tauri-apps/api/core';

import { useTransaksiStore } from "src/stores/transaksi-store";
import { useSettingsService } from 'stores/settings-service';
import LoginDialog from "src/components/LoginDialog.vue";
import ls from "localstorage-slim";

// Initialize cameras ref
const cameras = ref([]);
console.log('Cameras ref initialized:', cameras.value);

const wsUrl = ref(""); // Ganti dari backendUrl ke wsUrl
const useExternalAlpr = ref(false); // Tambahkan toggle ALPR mode

// CouchDB settings
const couchDbUrl = ref("");
const couchDbPort = ref(5984);
const couchDbUsername = ref("");
const couchDbPassword = ref("");
const testingCouchDbConnection = ref(false);

const componentStore = useComponentStore();
// const settingsStore = useSettingsStore(); // Tidak digunakan lagi, digantikan settingsService
const transaksiStore = useTransaksiStore();
const settingsService = useSettingsService();
const { gateSettings, activeGateId } = toRefs(settingsService);

const $q = useQuasar();
defineEmits([...useDialogPluginComponent.emits]);

const { dialogRef } = useDialogPluginComponent();

// Dialog handlers
const onDialogHide = () => {
  // Dialog is closing, perform any cleanup if needed
  console.log('Settings dialog is closing');
};

// Handle Esc key press
const handleEscKey = () => {
  console.log('Esc key pressed in settings dialog');
  dialogRef.value?.hide();
};

// Pengaturan gerbang sekarang diambil dari gateSettings dan globalSettings
const gateName = ref('');
const gateType = ref('entry');
const manlessMode = ref(true);
const printerName = ref(null);
const paperSize = ref('58mm');
const autoPrint = ref(true);

// Printer test and discovery state
const availablePrinters = ref([]);
const discoveredDevices = ref([]);
const epsonPrinters = ref([]);
const selectedPrinter = ref('');
const defaultPrinter = ref('');
const testBarcode = ref('SPARTA-' + Date.now().toString(36).toUpperCase());
const lastTestResult = ref(null);

// Loading states
const discovering = ref(false);
const loadingPrinters = ref(false);
const checkingEpson = ref(false);
const testingConnection = ref(false);
const printing = ref(false);

// Cache untuk printer discovery
const printerCache = ref({
  printers: [],
  discoveredDevices: [],
  epsonPrinters: [],
  lastUpdate: null,
  cacheTimeout: 30000 // 30 seconds cache
});

// Flag untuk prevent multiple concurrent discovery
const discoveryInProgress = ref(false);

// Operation mode settings
const operationMode = ref('manless');
const manualPaymentMode = ref('postpaid');
const prefix = ref(''); // Default prefix setting

// Operation mode options
const operationModeOptions = [
  { label: 'Mode Tanpa Petugas (Manless)', value: 'manless' },
  { label: 'Mode Manual (Dengan Petugas)', value: 'manual' }
];

const manualPaymentModeOptions = [
  { label: 'Bayar Belakang (Postpaid)', value: 'postpaid' },
  { label: 'Bayar Depan (Prepaid)', value: 'prepaid' }
];

// Pengaturan kamera sekarang diambil dari gateSettings
const selectedPlateCam = ref(null);
const plateCameraIp = ref('');
const plateCameraUsername = ref('');
const plateCameraPassword = ref('');
const plateCameraMode = ref('cctv'); // Default to CCTV

const selectedDriverCam = ref(null);
const driverCameraIp = ref('');
const driverCameraUsername = ref('');
const driverCameraPassword = ref('');
const driverCameraMode = ref('cctv'); // Default to CCTV

const selectedScannerCam = ref(null);
const scannerCameraIp = ref('');
const scannerCameraUsername = ref('');
const scannerCameraPassword = ref('');
const scannerCameraMode = ref('cctv'); // Default to CCTV
const plateCameraRtspPath = ref('');
const driverCameraRtspPath = ref('');
const scannerCameraRtspPath = ref('');
const captureInterval = ref(5000); // Default to 5 seconds

// Capture mode settings for each camera
const captureModeOptions = [
  { label: 'Auto (Detect Best)', value: 'auto' },
  { label: 'Snapshot (HTTP)', value: 'snapshot' },
  { label: 'RTSP (Stream)', value: 'rtsp' }
];

const plateCameraDefaultMode = ref('auto');
const plateCameraSnapshotUrl = ref('');
const plateCameraHttpPort = ref(80);

const driverCameraDefaultMode = ref('auto');
const driverCameraSnapshotUrl = ref('');
const driverCameraHttpPort = ref(80);

const scannerCameraDefaultMode = ref('auto');
const scannerCameraSnapshotUrl = ref('');
const scannerCameraHttpPort = ref(80);

// Add computed properties to determine camera types
const serialPort = ref(''); // Ditambahkan untuk input serial port
const plateCameraType = computed(() => {
  // Tipe kamera sekarang ditentukan secara dinamis berdasarkan keberadaan device ID atau URL
// dan disimpan melalui settingsService jika diperlukan, tidak lagi langsung di sini.
  return null
})

const driverCameraType = computed(() => {
  // Tipe kamera sekarang ditentukan secara dinamis dan disimpan melalui settingsService.
  return null
})

const scannerCameraType = computed(() => {
  // Tipe kamera sekarang ditentukan secara dinamis dan disimpan melalui settingsService.
  return null
})

// CouchDB connection string computed property
const couchDbConnectionString = computed(() => {
  const url = couchDbUrl.value || 'localhost';
  const port = couchDbPort.value || 5984;
  const username = couchDbUsername.value || 'admin';
  return `http://${username}:***@${url}:${port}`;
});

// Additional refs that need to be declared before the watcher
const selectedLocation = ref(null)
const parkingLocations = ref([])

// Computed property for camera availability
const availableCameras = computed(() => {
  console.log('Computing available cameras, current count:', cameras.value.length);
  return cameras.value || [];
});

// Watchers individual telah dihapus, penyimpanan dilakukan di onSaveSettings

// Watchers to sync form values with gateSettings changes
watch(gateSettings, (newSettings) => {
  if (newSettings) {
    gateName.value = newSettings.gateName || '';
    gateType.value = newSettings.gateType || 'entry';
    operationMode.value = newSettings.operationMode || 'manless';
    manualPaymentMode.value = newSettings.manualPaymentMode || 'postpaid';
    prefix.value = newSettings.prefix || ls.get('prefix') || '';
    printerName.value = newSettings.printerName || null;
    selectedPrinter.value = newSettings.selectedPrinter || newSettings.printerName || '';
    defaultPrinter.value = newSettings.defaultPrinter || '';
    paperSize.value = newSettings.paperSize || '58mm';
    autoPrint.value = newSettings.autoPrint || true;
    serialPort.value = newSettings.SERIAL_PORT || '';
    captureInterval.value = newSettings.CAPTURE_INTERVAL || 5000;
    wsUrl.value = newSettings.WS_URL || '';
    useExternalAlpr.value = newSettings.USE_EXTERNAL_ALPR || false;
    
    // Camera settings
    selectedPlateCam.value = newSettings.PLATE_CAM_DEVICE_ID || null;
    plateCameraIp.value = newSettings.PLATE_CAM_IP || '';
    plateCameraUsername.value = newSettings.PLATE_CAM_USERNAME || '';
    plateCameraPassword.value = newSettings.PLATE_CAM_PASSWORD || '';
    plateCameraRtspPath.value = newSettings.PLATE_CAM_RTSP_PATH || '';
    plateCameraDefaultMode.value = newSettings.PLATE_CAM_DEFAULT_MODE || 'auto';
    plateCameraSnapshotUrl.value = newSettings.PLATE_CAM_SNAPSHOT_URL || '';
    plateCameraHttpPort.value = newSettings.PLATE_CAM_HTTP_PORT || 80;
    plateCameraMode.value = newSettings.PLATE_CAM_MODE || 'cctv';
    
    selectedDriverCam.value = newSettings.DRIVER_CAM_DEVICE_ID || null;
    driverCameraIp.value = newSettings.DRIVER_CAM_IP || '';
    driverCameraUsername.value = newSettings.DRIVER_CAM_USERNAME || '';
    driverCameraPassword.value = newSettings.DRIVER_CAM_PASSWORD || '';
    driverCameraRtspPath.value = newSettings.DRIVER_CAM_RTSP_PATH || '';
    driverCameraDefaultMode.value = newSettings.DRIVER_CAM_DEFAULT_MODE || 'auto';
    driverCameraSnapshotUrl.value = newSettings.DRIVER_CAM_SNAPSHOT_URL || '';
    driverCameraHttpPort.value = newSettings.DRIVER_CAM_HTTP_PORT || 80;
    driverCameraMode.value = newSettings.DRIVER_CAM_MODE || 'cctv';
    
    selectedScannerCam.value = newSettings.SCANNER_CAM_DEVICE_ID || null;
    scannerCameraIp.value = newSettings.SCANNER_CAM_IP || '';
    scannerCameraUsername.value = newSettings.SCANNER_CAM_USERNAME || '';
    scannerCameraPassword.value = newSettings.SCANNER_CAM_PASSWORD || '';
    scannerCameraRtspPath.value = newSettings.SCANNER_CAM_RTSP_PATH || '';
    scannerCameraDefaultMode.value = newSettings.SCANNER_CAM_DEFAULT_MODE || 'auto';
    scannerCameraSnapshotUrl.value = newSettings.SCANNER_CAM_SNAPSHOT_URL || '';
    scannerCameraHttpPort.value = newSettings.SCANNER_CAM_HTTP_PORT || 80;
    scannerCameraMode.value = newSettings.SCANNER_CAM_MODE || 'cctv';
    
    // Former global settings
    wsUrl.value = newSettings.WS_URL || 'ws://localhost:8765';
    useExternalAlpr.value = newSettings.USE_EXTERNAL_ALPR || false;
    selectedLocation.value = newSettings.LOCATION || null;
    
    // CouchDB settings
    couchDbUrl.value = newSettings.COUCHDB_URL || 'localhost';
    couchDbPort.value = newSettings.COUCHDB_PORT || 5984;
    couchDbUsername.value = newSettings.COUCHDB_USERNAME || 'admin';
    couchDbPassword.value = newSettings.COUCHDB_PASSWORD || 'admin';
  }
}, { immediate: true, deep: true });

// Printer utility functions
const getSelectedPrinterIcon = () => {
  if (!selectedPrinter.value) return 'print';
  return (selectedPrinter.value.includes('EPSON') || selectedPrinter.value.includes('TM-T82')) 
    ? 'local_print_shop' : 'print';
};

const getSelectedPrinterColor = () => {
  if (!selectedPrinter.value) return 'grey';
  return (selectedPrinter.value.includes('EPSON') || selectedPrinter.value.includes('TM-T82')) 
    ? 'primary' : 'secondary';
};

// Cache management functions
const isCacheValid = () => {
  if (!printerCache.value.lastUpdate) return false;
  const now = Date.now();
  return (now - printerCache.value.lastUpdate) < printerCache.value.cacheTimeout;
};

const loadFromCache = () => {
  if (isCacheValid()) {
    availablePrinters.value = [...printerCache.value.printers];
    discoveredDevices.value = [...printerCache.value.discoveredDevices];
    epsonPrinters.value = [...printerCache.value.epsonPrinters];
    console.log('📦 Loaded printer data from cache');
    return true;
  }
  return false;
};

const saveToCache = () => {
  printerCache.value = {
    printers: [...availablePrinters.value],
    discoveredDevices: [...discoveredDevices.value],
    epsonPrinters: [...epsonPrinters.value],
    lastUpdate: Date.now(),
    cacheTimeout: 30000
  };
  console.log('💾 Saved printer data to cache');
};

const withConcurrencyControl = async (operation, timeoutMs = 10000) => {
  if (discoveryInProgress.value) {
    console.log('⚠️ Discovery already in progress, waiting...');
    
    const startTime = Date.now();
    while (discoveryInProgress.value && (Date.now() - startTime) < timeoutMs) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    if (discoveryInProgress.value) {
      console.error('❌ Discovery timed out, forcing reset');
      discoveryInProgress.value = false;
      throw new Error('Discovery operation timed out');
    }
    
    if (loadFromCache()) {
      return;
    }
  }
  
  discoveryInProgress.value = true;
  try {
    await operation();
    saveToCache();
  } finally {
    discoveryInProgress.value = false;
  }
};

// Printer discovery functions
const discoverPrinters = async () => {
  if (loadFromCache()) {
    console.log('📦 Using cached printer data');
    
    Notify.create({
      type: 'positive',
      message: `Menggunakan data cache: ${discoveredDevices.value.length} device`,
      timeout: 2000
    });
    return;
  }
  
  await withConcurrencyControl(async () => {
    discovering.value = true;
    
    try {
      console.log('🔍 Starting printer discovery...');
      
      const devices = await Promise.race([
        invoke('discover_thermal_printers'),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Discovery timeout after 8 seconds')), 8000)
        )
      ]);
      
      discoveredDevices.value = devices;
      
      availablePrinters.value = devices.map(device => ({
        label: device.name,
        value: device.name
      }));
      
      console.log('✅ Discovery completed:', devices.length, 'devices found');
      
      Notify.create({
        type: 'positive',
        message: `Ditemukan ${devices.length} device`,
        timeout: 3000
      });
    } catch (error) {
      console.error('❌ Discover printers error:', error);
      
      const fallbackDevices = [{
        name: "Manual Entry",
        connection_type: "manual",
        port: "manual",
        status: "available"
      }];
      
      discoveredDevices.value = fallbackDevices;
      availablePrinters.value = fallbackDevices.map(device => ({
        label: device.name,
        value: device.name
      }));
      
      Notify.create({
        type: 'warning',
        message: `Discovery gagal: ${error.message || error}. Menggunakan fallback.`,
        timeout: 5000
      });
    } finally {
      discovering.value = false;
    }
  });
};

const listThermalPrinters = async () => {
  if (loadFromCache() && availablePrinters.value.length > 0) {
    console.log('📦 Using cached thermal printer list');
    
    Notify.create({
      type: 'positive',
      message: `Menggunakan data cache: ${availablePrinters.value.length} printer`,
      timeout: 2000
    });
    return;
  }
  
  await withConcurrencyControl(async () => {
    loadingPrinters.value = true;
    
    try {
      console.log('📝 Starting thermal printer list...');
      
      const result = await Promise.race([
        invoke('list_thermal_printers'),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('List timeout after 6 seconds')), 6000)
        )
      ]);
      
      availablePrinters.value = result.map(printer => ({
        label: printer,
        value: printer
      }));
      
      discoveredDevices.value = [];
      
      console.log('✅ Thermal printer list completed:', result.length, 'printers found');
      
      Notify.create({
        type: 'positive',
        message: `Ditemukan ${result.length} printer`,
        timeout: 3000
      });
    } catch (error) {
      console.error('❌ List printers error:', error);
      
      const fallbackPrinters = [
        { label: 'Manual Entry', value: 'Manual Entry' },
        { label: 'EPSON TM-T82X', value: 'EPSON TM-T82X' }
      ];
      
      availablePrinters.value = fallbackPrinters;
      
      Notify.create({
        type: 'warning',
        message: `List printer gagal: ${error.message || error}. Menggunakan fallback.`,
        timeout: 5000
      });
    } finally {
      loadingPrinters.value = false;
    }
  });
};

const checkEpsonPrinters = async () => {
  if (loadFromCache() && epsonPrinters.value.length > 0) {
    console.log('📦 Using cached EPSON printer data');
    
    Notify.create({
      type: 'positive',
      message: `Cache: ${epsonPrinters.value.length} EPSON printer`,
      timeout: 2000
    });
    return;
  }
  
  await withConcurrencyControl(async () => {
    checkingEpson.value = true;
    
    try {
      console.log('🖨️ Starting EPSON printer check...');
      
      const result = await Promise.race([
        invoke('check_epson_printers'),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('EPSON check timeout after 5 seconds')), 5000)
        )
      ]);
      
      epsonPrinters.value = result.filter(name => !name.includes('No EPSON'));
      
      if (epsonPrinters.value.length > 0) {
        console.log('✅ EPSON check completed:', epsonPrinters.value.length, 'EPSON printers found');
        
        Notify.create({
          type: 'positive',
          message: `Ditemukan ${epsonPrinters.value.length} EPSON printer`,
          timeout: 3000
        });
        
        if (!selectedPrinter.value) {
          selectedPrinter.value = epsonPrinters.value[0];
        }
      } else {
        console.log('⚠️ No EPSON printers found');
        Notify.create({
          type: 'warning',
          message: 'Tidak ada EPSON TM-T82X yang ditemukan',
          timeout: 3000
        });
      }
    } catch (error) {
      console.error('❌ Check EPSON printers error:', error);
      
      epsonPrinters.value = ['EPSON TM-T82X (Fallback)'];
      
      Notify.create({
        type: 'warning',
        message: `EPSON check gagal: ${error.message || error}. Menggunakan fallback.`,
        timeout: 5000
      });
    } finally {
      checkingEpson.value = false;
    }
  });
};

// Printer testing functions
const testPrintBarcode = async () => {
  printing.value = true;
  lastTestResult.value = null;
  
  try {
    const result = await invoke('test_print_barcode', { 
      barcodeData: testBarcode.value,
      printerName: selectedPrinter.value
    });
    
    lastTestResult.value = result;
    
    Notify.create({
      type: 'positive',
      message: result.message || 'Test print berhasil!',
      timeout: 3000
    });
  } catch (error) {
    console.error('Test print error:', error);
    
    lastTestResult.value = {
      success: false,
      message: error.toString()
    };
    
    Notify.create({
      type: 'negative',
      message: `Test print gagal: ${error}`,
      timeout: 5000
    });
  } finally {
    printing.value = false;
  }
};

const quickTestPrint = async (printerName) => {
  printing.value = printerName;
  
  try {
    const result = await invoke('test_print_barcode', { 
      barcodeData: `QUICK-TEST-${Date.now().toString(36).toUpperCase()}`,
      printerName: printerName
    });
    
    Notify.create({
      type: 'positive',
      message: `Quick test berhasil: ${result.message}`,
      timeout: 3000
    });
  } catch (error) {
    Notify.create({
      type: 'negative',
      message: `Quick test gagal: ${error}`,
      timeout: 5000
    });
  } finally {
    printing.value = false;
  }
};

const testPrinterConnection = async () => {
  testingConnection.value = true;
  lastTestResult.value = null;
  
  try {
    const result = await invoke('test_printer_connection', { 
      printerIdentifier: selectedPrinter.value 
    });
    
    lastTestResult.value = result;
    
    Notify.create({
      type: 'positive',
      message: result.message,
      timeout: 3000
    });
  } catch (error) {
    console.error('Test connection error:', error);
    
    lastTestResult.value = {
      success: false,
      message: error.toString()
    };
    
    Notify.create({
      type: 'negative',
      message: `Test connection gagal: ${error}`,
      timeout: 5000
    });
  } finally {
    testingConnection.value = false;
  }
};

// Printer management functions
const setAsDefaultPrinter = async () => {
  try {
    const result = await invoke('set_default_printer', { 
      printerName: selectedPrinter.value 
    });
    
    defaultPrinter.value = selectedPrinter.value;
    
    Notify.create({
      type: 'positive',
      message: result.message || 'Printer default berhasil diset!'
    });
  } catch (error) {
    console.error('Set default printer error:', error);
    Notify.create({
      type: 'negative',
      message: `Gagal set default printer: ${error}`
    });
  }
};

const getDefaultPrinter = async () => {
  try {
    const result = await invoke('get_default_printer');
    defaultPrinter.value = result;
    if (!selectedPrinter.value) {
      selectedPrinter.value = result;
    }
    
    Notify.create({
      type: 'info',
      message: `Default printer: ${result}`,
      timeout: 2000
    });
  } catch (error) {
    console.log('No default printer set');
    Notify.create({
      type: 'warning',
      message: 'Tidak ada default printer yang diset'
    });
  }
};

// Utility functions
const generateTestBarcode = () => {
  const timestamp = Date.now().toString(36).toUpperCase();
  const random = Math.random().toString(36).substring(2, 7).toUpperCase();
  testBarcode.value = `SPARTA-${timestamp}-${random}`;
};

const clearPrinterCache = () => {
  printerCache.value = {
    printers: [],
    discoveredDevices: [],
    epsonPrinters: [],
    lastUpdate: null,
    cacheTimeout: 30000
  };
  
  availablePrinters.value = [];
  discoveredDevices.value = [];
  epsonPrinters.value = [];
  selectedPrinter.value = '';
  lastTestResult.value = null;
  
  discoveryInProgress.value = false;
  
  Notify.create({
    type: 'info',
    message: 'Cache printer berhasil dibersihkan',
    timeout: 2000
  });
};

const onPrinterSelected = (selectedPrinterName) => {
  console.log('Selected printer:', selectedPrinterName);
  printerName.value = selectedPrinterName; // Update the printerName for settings
  lastTestResult.value = null;
};

const onSaveSettings = async () => {
  console.log('onSaveSettings started - saving all settings...');
  
  try {
    // Combine all settings into one object
    const settingsToSave = {
      // Gate-specific settings
      gateName: gateName.value,
      gateType: gateType.value,
      operationMode: operationMode.value,
      manualPaymentMode: manualPaymentMode.value,
      prefix: prefix.value,
      SERIAL_PORT: serialPort.value,
      printerName: selectedPrinter.value || printerName.value,
      selectedPrinter: selectedPrinter.value,
      defaultPrinter: defaultPrinter.value,
      paperSize: paperSize.value,
      autoPrint: autoPrint.value,
      PLATE_CAM_DEVICE_ID: selectedPlateCam.value,
      PLATE_CAM_IP: plateCameraIp.value,
      PLATE_CAM_USERNAME: plateCameraUsername.value,
      PLATE_CAM_PASSWORD: plateCameraPassword.value,
      PLATE_CAM_RTSP_PATH: plateCameraRtspPath.value,
      PLATE_CAM_DEFAULT_MODE: plateCameraDefaultMode.value,
      PLATE_CAM_SNAPSHOT_URL: plateCameraSnapshotUrl.value,
      PLATE_CAM_HTTP_PORT: plateCameraHttpPort.value,
      PLATE_CAM_MODE: plateCameraMode.value,
      DRIVER_CAM_DEVICE_ID: selectedDriverCam.value,
      DRIVER_CAM_IP: driverCameraIp.value,
      DRIVER_CAM_USERNAME: driverCameraUsername.value,
      DRIVER_CAM_PASSWORD: driverCameraPassword.value,
      DRIVER_CAM_RTSP_PATH: driverCameraRtspPath.value,
      DRIVER_CAM_DEFAULT_MODE: driverCameraDefaultMode.value,
      DRIVER_CAM_SNAPSHOT_URL: driverCameraSnapshotUrl.value,
      DRIVER_CAM_HTTP_PORT: driverCameraHttpPort.value,
      DRIVER_CAM_MODE: driverCameraMode.value,
      SCANNER_CAM_DEVICE_ID: selectedScannerCam.value,
      SCANNER_CAM_IP: scannerCameraIp.value,
      SCANNER_CAM_USERNAME: scannerCameraUsername.value,
      SCANNER_CAM_PASSWORD: scannerCameraPassword.value,
      SCANNER_CAM_RTSP_PATH: scannerCameraRtspPath.value,
      SCANNER_CAM_DEFAULT_MODE: scannerCameraDefaultMode.value,
      SCANNER_CAM_SNAPSHOT_URL: scannerCameraSnapshotUrl.value,
      SCANNER_CAM_HTTP_PORT: scannerCameraHttpPort.value,
      SCANNER_CAM_MODE: scannerCameraMode.value,
      CAPTURE_INTERVAL: parseInt(captureInterval.value, 10) || 5000,
      
      // Former global settings now in gate settings
      WS_URL: wsUrl.value || 'ws://localhost:8765',
      USE_EXTERNAL_ALPR: useExternalAlpr.value || false,
      LOCATION: selectedLocation.value,
      
      // CouchDB settings
      COUCHDB_URL: couchDbUrl.value || 'localhost',
      COUCHDB_PORT: parseInt(couchDbPort.value, 10) || 5984,
      COUCHDB_USERNAME: couchDbUsername.value || 'admin',
      COUCHDB_PASSWORD: couchDbPassword.value || 'admin',
    };
    
    console.log('Saving consolidated settings:', settingsToSave);
    
    // Debug camera settings specifically
    console.log('Camera settings being saved:', {
      PLATE_CAM_MODE: plateCameraMode.value,
      PLATE_CAM_IP: plateCameraIp.value,
      DRIVER_CAM_MODE: driverCameraMode.value,
      DRIVER_CAM_IP: driverCameraIp.value,
      SCANNER_CAM_MODE: scannerCameraMode.value,
      SCANNER_CAM_IP: scannerCameraIp.value
    });
    
    await settingsService.saveGateSettings(settingsToSave);
    
    // Save prefix to localStorage
    ls.set('prefix', prefix.value);
    
    console.log('Settings saved successfully');
    
    // Update CouchDB connections if settings changed
    try {
      const { updateRemoteUrl, reinitializeRemoteDatabases } = await import('src/boot/pouchdb');
      updateRemoteUrl();
      await reinitializeRemoteDatabases();
      console.log('CouchDB connections updated successfully');
    } catch (dbError) {
      console.warn('Failed to update CouchDB connections:', dbError);
    }
    
    // Show success notification
    $q.notify({
      type: 'positive',
      message: 'Settings saved successfully!',
      position: 'top'
    });
    
    // Close dialog first
    dialogRef.value.hide();
    
    // Wait a bit for settings to be saved and reactive system to update
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Refresh settings to ensure they're loaded correctly
    await settingsService.initializeSettings();
    
    // Only reload if absolutely necessary (can be removed if reactive updates work well)
    // setTimeout(() => {
    //   window.location.reload();
    // }, 1000);
    
  } catch (error) {
    console.error('Failed to save settings:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to save settings. Please try again.',
      position: 'top'
    });
  }
};

const onSerialPortDialogHide = () => {
  // window.addEventListener("keydown", handleKeyDownOnSettingDialog);
};

const onCameraInDialogHide = () => {
  // window.location.reload();
  // window.addEventListener("keydown", handleKeyDownOnSettingDialog);
};
const onCameraOutDialogHide = () => {
  // window.location.reload();
  // window.addEventListener("keydown", handleKeyDownOnSettingDialog);
};


const getCameras = async () => {
  try {
    console.log('Starting camera enumeration...');
    
    // First, try to enumerate devices without requesting permission
    let devices = await navigator.mediaDevices.enumerateDevices();
    console.log('Initial device enumeration (before permission):', devices);
    
    // Check if we have detailed labels (permission already granted)
    const hasDetailedLabels = devices.some(device => 
      device.kind === 'videoinput' && device.label && device.label !== ''
    );
    
    if (!hasDetailedLabels) {
      console.log('No detailed labels found, requesting camera permissions...');
      try {
        // Request permission to get detailed device labels
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        // Stop the stream immediately after getting permission
        stream.getTracks().forEach(track => track.stop());
        console.log('Camera permission granted, re-enumerating devices...');
        
        // Re-enumerate devices after permission is granted
        devices = await navigator.mediaDevices.enumerateDevices();
      } catch (permissionError) {
        console.warn('Camera permission denied, using basic device info:', permissionError);
        // Continue with basic device info even if permission is denied
      }
    }

    console.log('Final device enumeration:', devices);
    
    // Filter and map video input devices
    const videoCameras = devices
      .filter(device => device.kind === 'videoinput')
      .map((device, index) => ({
        deviceId: device.deviceId,
        label: device.label || `Camera ${index + 1}`,
        value: device.deviceId // Add value for q-select compatibility
      }));
    
    cameras.value = videoCameras;
    console.log('Available cameras set to:', cameras.value);
    
    // Show notification about camera detection
    if (videoCameras.length > 0) {
      $q.notify({
        type: 'positive',
        message: `Found ${videoCameras.length} camera(s)`,
        position: 'top',
        timeout: 2000
      });
    } else {
      $q.notify({
        type: 'warning',
        message: 'No cameras detected. Please check if cameras are connected.',
        position: 'top',
        timeout: 3000
      });
    }
    
  } catch (error) {
    console.error('Error getting cameras:', error);
    $q.notify({
      type: 'negative',
      message: 'Could not access camera devices. Please check browser permissions.',
      position: 'top'
    });
    
    // Set empty array as fallback
    cameras.value = [];
  }
};

const updatePlateCamera = (cam) => {
  // USB camera selected, clear CCTV IP if needed
  if (cam && plateCameraMode.value === 'usb') {
    plateCameraIp.value = '';
  }
};

const updateDriverCamera = (cam) => {
  // USB camera selected, clear CCTV IP if needed
  if (cam && driverCameraMode.value === 'usb') {
    driverCameraIp.value = '';
  }
};

const updateScannerCamera = (cam) => {
  // USB camera selected, clear CCTV IP if needed
  if (cam && scannerCameraMode.value === 'usb') {
    scannerCameraIp.value = '';
  }
};

// backendUrl, alprUrl, dan wsUrl sekarang diambil dari globalSettings dan tidak lagi disimpan secara lokal di sini.
// Inisialisasi sudah dilakukan di atas dengan `globalSettings.value?.API_IP` dll.

const updateBackendUrl = (val) => {
  // Tidak perlu menyimpan di sini, akan disimpan di onSaveSettings
  // backendUrl.value akan diupdate oleh v-model
}

const updateAlprUrl = (val) => {
  // Pengaturan ALPR_IP sekarang ditangani oleh backend Tauri.
}

const updateWSUrl = (val) => {
  // Tidak perlu menyimpan di sini, akan disimpan di onSaveSettings
  console.log('WebSocket URL updated in UI:', val);
}

const updateExternalAlprSetting = (val) => {
  // Tidak perlu menyimpan di sini, akan disimpan di onSaveSettings
  console.log('External ALPR setting updated in UI:', val);
}

const updateLocation = (val) => {
  transaksiStore.lokasiPos = val
}

// CouchDB functions
const testCouchDbConnection = async () => {
  testingCouchDbConnection.value = true;
  
  try {
    const testUrl = `http://${couchDbUrl.value || 'localhost'}:${couchDbPort.value || 5984}`;
    const username = couchDbUsername.value || 'admin';
    const password = couchDbPassword.value || 'admin';
    
    // Create Basic Authentication header
    const credentials = btoa(`${username}:${password}`);
    
    // Test connection using fetch with Authorization header
    const response = await fetch(testUrl, {
      method: 'GET',
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      Notify.create({
        type: 'positive',
        message: `CouchDB Connection Successful! Version: ${data.version}`,
        timeout: 3000
      });
      
      // Update remote databases with new settings
      const { reinitializeRemoteDatabases } = await import('src/boot/pouchdb');
      await reinitializeRemoteDatabases();
      
      Notify.create({
        type: 'positive',
        message: 'Database connections updated successfully!',
        timeout: 2000
      });
    } else {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
  } catch (error) {
    console.error('CouchDB connection test failed:', error);
    Notify.create({
      type: 'negative',
      message: `Connection failed: ${error.message}`,
      timeout: 5000
    });
  } finally {
    testingCouchDbConnection.value = false;
  }
};

onMounted(async () => {
  console.log('SettingsDialog onMounted started');
  
  // Add keyboard event listener for Esc key
  const handleKeydown = (event) => {
    if (event.key === 'Escape') {
      console.log('Esc key pressed, closing settings dialog');
      handleEscKey();
    }
  };
  
  document.addEventListener('keydown', handleKeydown);
  
  // Store reference for cleanup
  window.settingsDialogKeydownHandler = handleKeydown;
  
  try {
    // Initialize prefix from localStorage
    prefix.value = ls.get('prefix') || '';
    
    // Initialize settings first
    console.log('Initializing settings...');
    await settingsService.initializeSettings();
    console.log('Settings initialized successfully');
    
    // Wait a bit to ensure reactive state is updated
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Get cameras after settings are initialized
    console.log('Starting camera enumeration...');
    await getCameras(); 
    console.log('Camera enumeration completed, camera count:', cameras.value.length);
    
    // Initialize printer discovery
    console.log('Starting printer initialization...');
    try {
      // Check if cache is available first
      if (loadFromCache()) {
        console.log('📦 Loaded printer data from cache');
      } else {
        // Start with checking EPSON printers first (fastest usually)
        await checkEpsonPrinters();
        
        // Get default printer
        await getDefaultPrinter();
      }
    } catch (error) {
      console.error('❌ Error during printer initialization:', error);
      Notify.create({
        type: 'warning',
        message: 'Gagal inisialisasi printer. Gunakan tombol discovery manual.',
        timeout: 3000
      });
    }
    console.log('Printer initialization completed');
    
    // The form values will be automatically updated by the watcher
    // when gateSettings changes, so we don't need to manually set them here
    console.log('Current settings after initialization:', gateSettings.value);
    console.log('Current camera list:', cameras.value);
    
  } catch (error) {
    console.error('Error initializing settings dialog:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to load settings. Please try again.',
      position: 'top'
    });
  }
});

onUnmounted(() => {
  // Clean up keyboard event listener
  if (window.settingsDialogKeydownHandler) {
    document.removeEventListener('keydown', window.settingsDialogKeydownHandler);
    delete window.settingsDialogKeydownHandler;
    console.log('SettingsDialog: Keyboard event listener cleaned up');
  }
});
</script>

<style scoped>
.glass {
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  background-color: rgba(255, 255, 255, 0.98);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.125);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

:deep(.q-dialog__backdrop.fixed-full) {
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
}

.settings-content {
  padding: 0 8px;
}

.settings-content::-webkit-scrollbar {
  width: 8px;
}

.settings-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

.settings-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
}

.settings-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.5);
}

.settings-card {
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.3s ease;
}

.settings-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.settings-section-title {
  font-size: 16px;
  font-weight: 700;
  color: #1976d2;
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.settings-expansion {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.settings-expansion :deep(.q-expansion-item__container) {
  border-radius: 8px;
}

.settings-expansion :deep(.q-item) {
  padding: 12px 16px;
  background-color: #f5f7fa;
  color: #212121;
  font-weight: 500;
}

.settings-expansion :deep(.q-item:hover) {
  background-color: #e3f2fd;
  color: #1565c0;
  font-weight: 600;
}

.camera-config-section {
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e1e5e9;
}

.camera-config-section .text-subtitle2 {
  color: #1976d2;
  font-weight: 700;
  margin-bottom: 8px;
}

/* Input field improvements */
:deep(.q-field--outlined .q-field__control) {
  border-radius: 8px;
  background-color: #ffffff;
}

:deep(.q-field--outlined .q-field__control:before) {
  border-color: #e0e0e0;
}

:deep(.q-field--dense .q-field__control) {
  height: 40px;
  background-color: #ffffff;
}

:deep(.q-field--focused .q-field__control) {
  background-color: #ffffff !important;
}

:deep(.q-field--focused .q-field__native) {
  color: #424242 !important;
}

:deep(.q-select__dropdown-icon) {
  color: #1976d2;
}

/* Toggle improvements */
:deep(.q-toggle__inner) {
  color: #1976d2;
}

/* Button improvements */
:deep(.q-btn) {
  border-radius: 8px;
  text-transform: none;
  font-weight: 500;
}

/* Responsive adjustments */
@media (max-width: 1023px) {
  .settings-content {
    padding: 0 4px;
  }
  
  .settings-card {
    margin-bottom: 16px !important;
  }
}

@media (max-width: 599px) {
  .row.q-col-gutter-sm > .col-12:not(:last-child) {
    margin-bottom: 8px;
  }
  
  .camera-config-section {
    padding: 8px;
  }
  
  .settings-section-title {
    font-size: 14px;
  }
}

/* Animation for expansion items */
.settings-expansion :deep(.q-expansion-item__content) {
  transition: all 0.3s ease;
}

/* Status indicators */
.text-caption {
  font-size: 12px;
  line-height: 1.4;
  color: #616161 !important;
  font-weight: 500;
}

/* Ensure proper text contrast */
:deep(.q-item-label) {
  color: #212121 !important;
  font-weight: 500;
}

:deep(.q-expansion-item__label) {
  color: #212121 !important;
  font-weight: 600;
}

/* Input label improvements */
:deep(.q-field__label) {
  color: #424242 !important;
  font-weight: 500;
}

:deep(.q-field--focused .q-field__label) {
  color: #1976d2 !important;
  font-weight: 600;
}

/* Card section improvements */
:deep(.q-card__section) {
  padding: 16px 20px;
}

/* Text color improvements for better visibility */
:deep(.q-field__control) {
  color: #212121;
}

:deep(.q-field__native) {
  color: #212121 !important;
  font-weight: 500;
}

:deep(.q-input .q-field__native) {
  color: #212121 !important;
  font-weight: 500;
}

:deep(.q-select .q-field__native) {
  color: #212121 !important;
  font-weight: 500;
}

:deep(.q-field__input) {
  color: #212121 !important;
  font-weight: 500;
}

:deep(.q-toggle__label) {
  color: #212121 !important;
  font-weight: 500;
}

/* Placeholder text */
:deep(.q-field__input::placeholder) {
  color: #757575 !important;
  font-weight: 400;
}

:deep(input::placeholder) {
  color: #757575 !important;
  font-weight: 400;
}

/* Selected option text in dropdowns */
:deep(.q-select__selection) {
  color: #212121 !important;
  font-weight: 500;
}

/* Dropdown options */
:deep(.q-menu .q-item) {
  color: #212121 !important;
}

/* Input text when typing */
:deep(input[type="text"]) {
  color: #212121 !important;
  font-weight: 500;
}

:deep(input[type="number"]) {
  color: #212121 !important;
  font-weight: 500;
}

:deep(input[type="password"]) {
  color: #212121 !important;
  font-weight: 500;
}

/* Ensure all input elements have proper contrast */
:deep(.q-field .q-field__control .q-field__native) {
  color: #212121 !important;
  background-color: transparent !important;
  font-weight: 500;
}

:deep(.q-field .q-field__control input) {
  color: #212121 !important;
  background-color: transparent !important;
  font-weight: 500;
}

/* Fix for autofilled inputs */
:deep(input:-webkit-autofill) {
  -webkit-text-fill-color: #212121 !important;
  -webkit-box-shadow: 0 0 0px 1000px #ffffff inset !important;
}

:deep(input:-webkit-autofill:focus) {
  -webkit-text-fill-color: #212121 !important;
  -webkit-box-shadow: 0 0 0px 1000px #ffffff inset !important;
}

/* Ensure text remains visible in all states */
:deep(.q-field--readonly .q-field__native) {
  color: #212121 !important;
}

:deep(.q-field--disable .q-field__native) {
  color: #616161 !important;
}

/* Force text visibility in all scenarios */
* {
  -webkit-text-fill-color: initial !important;
}

:deep(.q-field__native),
:deep(.q-field__input),
:deep(input) {
  -webkit-text-fill-color: #212121 !important;
  color: #212121 !important;
  font-weight: 500;
}

/* Specific fixes for different input types */
:deep(.q-select .q-field__native span) {
  color: #212121 !important;
  font-weight: 500;
}

/* Override any inherited transparency */
:deep(.q-field__control) {
  background-color: #ffffff !important;
}

:deep(.q-field--outlined .q-field__control) {
  background-color: #ffffff !important;
}

/* Help text improvements */
.text-grey-6 {
  color: #616161 !important;
  font-weight: 400;
}

/* Separator styling */
:deep(.q-separator) {
  background-color: #e0e0e0;
  opacity: 0.6;
}

/* Button text improvements */
:deep(.q-btn .q-btn__content) {
  color: inherit !important;
  font-weight: 500;
}

/* Card content text */
:deep(.q-card__section) {
  color: #212121;
}

/* General text improvements */
:deep(.q-item__label) {
  color: #212121 !important;
  font-weight: 500;
}

/* Option group text */
:deep(.q-option-group .q-option__label) {
  color: #212121 !important;
  font-weight: 500;
}

/* Chip text */
:deep(.q-chip) {
  font-weight: 500;
}

/* Banner text */
:deep(.q-banner) {
  font-weight: 500;
}
</style>
