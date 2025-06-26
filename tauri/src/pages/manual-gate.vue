<template>

  <div v-if="settingsService.isManlessMode">
      <EntryGatePage class="full-width q-pa-md" />
  </div>
  <div v-if="$q.screen.lt.md" class="text-h2">
    <q-card class="fixed-center glass">
      <img src="~assets/logo.png" />
      <q-card-section>
        <div class="text-h6">
          Silahkan buka halaman ini dengan resolusi di atas 1024px x 768px
        </div>
        <q-btn
          color="primary"
          icon="home"
          label="Home"
          @click="$router.push('/')"
        />
      </q-card-section>
    </q-card>
  </div>
  <div
    :key="componentStore.outGateKey"
    v-else
    class="relative fixed-top full-height full-width overflow-hidden"
    :class="darkMode ? 'bg-grey-8' : 'bg-grey-8'"
  >
    <div
      v-if="!transaksiStore.isCheckedIn"
      class="flex row justify-between items-center q-pl-lg no-wrap q-pt-md"
      style="height: 150px"
    >
      <q-card flat class="row items-center transparent">
        <!-- <q-img
          v-if="$q.screen.gt.sm"
          src="~assets/logo.png"
          spinner-color="primary"
          fit="fill"
          class="q-ml-sm rounded-corner"
          width="150px"
          height="150px"
          style="transform: scale(1.5)"
        /> -->

        <CompanyName />
      </q-card>

      <div class="content-end q-pr-md">
        <div class="flex row no-wrap justify-end">
          <ShinyCard
            class="bg-grey-7"
            title="Kendaraan Masuk"
            :jumlah="transaksiStore.vehicleInToday"
          />
          <!-- shortkey="F3" -->
          <ShinyCard
            :key="componentStore.vehicleOutKey"
            class="bg-grey-8 q-mx-md"
            title="Kendaraan Keluar"
            shortkey="F4"
            :jumlah="transaksiStore.totalVehicleOut"
          />
          <ShinyCard
            class="bg-grey-9"
            title="Kendaraan Parkir"
            :jumlah="transaksiStore.totalVehicleInside"
          />
          <!-- shortkey="F5" -->
        </div>
      </div>
    </div>
    <div
      class="window-width text-dark text-weight-bolder flex row q-pr-lg q-col-gutter-sm z-top overflow-hidden q-mb-md"
      :class="
        transaksiStore.isCheckedIn
          ? 'justify-start q-mt-md q-ml-md '
          : 'justify-end'
      "
    >
      
          <q-chip
          v-show="!componentStore.hideInputPlatNomor && !transaksiStore.isCheckedIn" 
            color="transparent"
            text-color="grey-3"
            :icon="settingsService.isPrepaidMode ? 'payment' : 'schedule'"
          >
            Mode: {{ settingsService.isPrepaidMode ? 'Bayar Depan (Prepaid)' : 'Bayar Belakang (Postpaid)' }}
          </q-chip>
      
        
      <q-chip text-color="grey-3" class="bg-transparent" icon="account_circle" :label="pegawai" />

      <q-chip
        class="bg-transparent"
        icon="work_history"
        text-color="grey-3"
        :label="ls.get('shift')"
      />
      <q-chip
      text-color="grey-3"
        class="bg-transparent"
        icon="place"
        :label="
          '(' +
          transaksiStore.lokasiPos.value +
          ') ' +
          transaksiStore.lokasiPos.label
        "
      />
      <Clock />
    </div>

    <!-- <div
      v-if="$q.screen.gt.sm && !transaksiStore.isCheckedIn"
      class="full-width q-pt-md"
    > -->
      <!-- <Quotes /> -->
    <!-- </div> -->

    <!-- KAMERA -->
    <div class="row justify-center items-center overflow-hidden">
      <div class="col-12">
        <div
          v-if="!transaksiStore.isCheckedIn"
          ref="cardVideo"
          class="flex row justify-between content-center items-center q-px-sm relative bg-transparent overflow-hidden q-gutter-md no-wrap"
          style="width: 100%; max-height: 62vh"
        >
          <div class="col-6 relative overflow-hidden q-mr-md">
            <q-chip
              class="absolute bg-transparent"
              icon="camera"
              label="Kamera Kendaraan"
            />
            <!-- <q-skeleton
              v-if="cameraInUrl == null || cameraInUrl == '-'"
              height="52vh"
              class="rounded-corner"
              width="49vw"
            /> -->
           <Camera
              ref="plateCameraRef"
              :username="gateSettings.PLATE_CAM_USERNAME"
              :password="gateSettings.PLATE_CAM_PASSWORD"
              :ipAddress="gateSettings.PLATE_CAM_IP"
              :fileName="'plate'"
              cameraLocation="plate"
              :cameraType="plateCameraType"
              :deviceId="plateCameraDeviceId"
              @captured="onPlateCaptured"
              @error="onCameraError"
              class="camera-feed"
              label="Kamera Kendaraan"
              style="max-width: 100%; max-height: 52vh;"
            />
            <!-- height: '62vh', -->
          </div>
          <div class="col-6 relative overflow-hidden q-ml-md">
            <q-chip
              class="absolute bg-transparent"
              icon="camera"
              label="Kamera Driver"
            />
            <!-- <q-skeleton
              v-if="cameraOut == null || cameraOut == '-'"
              width="49vw"
              height="52vh"
              class="rounded-corner" -->
            <!-- /> -->
            <!-- <CaemeraOut
              ref="cameraOutRef"
              :key="componentStore.cameraOutKey"
              class="rounded-corner"
              :style="{
                width: '49vw',
              }"
            /> -->

            <Camera
              :key="componentStore.cameraOutKey"
              ref="driverCameraRef"
              class="rounded-corner"
              cameraLocation="driver"
              :username="driverCameraType === 'cctv' ? gateSettings.DRIVER_CAM_USERNAME : undefined"
              :password="driverCameraType === 'cctv' ? gateSettings.DRIVER_CAM_PASSWORD : undefined"
              :ipAddress="driverCameraType === 'cctv' ? gateSettings.DRIVER_CAM_IP : undefined"
              :cameraType="driverCameraType"
              :deviceId="driverCameraType === 'usb' ? driverCameraDeviceId : undefined"
              :fileName="'driver'"
              label="Kamera Driver"
              @error="onCameraError"
              style="max-width: 100%; max-height: 52vh;"
            />
            <!-- :style="$q.screen.lt.md ? 'width: 49vw' : 'height: 52vh'" -->
          </div>
        </div>
      </div>
    </div>

    <div
      class="flex row justify-center fixed full-width no-wrap overflow-hidden bg-grey-8"
      style="bottom: 20px; max-width: 100vw;"
    >
      <div class="col-8 overflow-hidden">
        <q-input
          v-show="
            !componentStore.hideInputPlatNomor && !transaksiStore.isCheckedIn
          "
          input-class="input-box  text-black text-weight-bolder"
          class="input-box rounded-corner relative text-uppercase q-pa-md q-mb-xl bg-grey-1 text-dark"
          input-style="height:90px;border:0"
          label-color="black text-body1 q-pb-sm"
          color="bg-grey-2"
          item-aligned
          borderless
          v-model="transaksiStore.platNomor"
          label="Masukkan Plat Nomor"
          ref="inputPlatNomorRef"
          autofocus
          :rules="[
            (val) =>
              val
                ? transaksiStore.platNomor.length <= 9 ||
                  'Plat nomor terlalu banyak'
                : true,
          ]"
          @update:model-value="() => onInputPlatNomor()"
          @keydown.enter="onPressEnterPlatNomor()"
        >
          <template v-slot:prepend>
            <q-btn
              push
              label="F1"
              class="text-weight-bold q-mt-md bg-dark text-white"
            />
          </template>

          <template v-slot:append>
            <q-btn
              push
              :size="'xl'"
              class="q-mt-md q-mr-md bg-dark text-white"
              icon="keyboard_return"
              @click="onPressEnterPlatNomor()"
            />
          </template>
        </q-input>
      </div>
      <div
        class="full-width fixed-bottom-right bg-dark q-pa-sm row justify-between overflow-hidden"
        style="max-width: 100vw;"
      >
        <!-- v-if="componentStore.currentPage == 'outgate'"-->
        <div>
          <span class="text-weight-bolder text-grey-5">
            .::PINTU MASUK::.</span
          >
        </div>
        <div class="q-gutter-sm">
          <q-btn color="grey-8" size="sm" label="Dashboard" to="/">
            <q-badge
              color="primary"
              text-color="white"
              label="F2"
              class="q-mx-xs"
            />
            <q-tooltip content-class="bg-primary">Dashboard Admin</q-tooltip>
          </q-btn>
          <q-btn color="grey-8" size="sm" label="Log out">
            <q-badge
              color="primary"
              text-color="white"
              label="F5"
              class="q-mx-xs"
            />
            <q-tooltip content-class="bg-primary">Log out</q-tooltip>
          </q-btn>

          <q-btn
            color="grey-6"
            size="sm"
            @click="onClickSettings()"
            label="Settings"
            icon="settings"
          >
            <q-badge
              color="primary"
              text-color="white"
              label="F7"
              class="q-ml-xs"
            />
            <q-tooltip content-class="bg-primary">Settings</q-tooltip>
          </q-btn>

          <q-btn
            color="grey-7"
            size="sm"
            @click="onClickBukaManual()"
            label="Buka Manual"
          >
            <!-- icon="settings" -->
            <q-badge
              color="primary"
              text-color="white"
              label="F8"
              class="q-ml-xs"
            />
          </q-btn>
          <q-btn
            color="red-9 "
            size="sm"
            @click="onClickEmergency()"
            label="Emergency"
          >
            <!-- icon="settings" -->
            <q-badge
              color="primary"
              text-color="white"
              label="F12"
              class="q-ml-xs"
            />
          </q-btn>

          <!-- Dark Mode Toggle Button -->
         
        </div>

        <!-- <q-toggle
        v-model="darkMode"
        @update:model-value="darkModeToggle"
        color="green"
      /> -->
      </div>
    </div>
    <!-- <PaymentCard v-if="transaksiStore.isCheckedIn" @payment-completed="onPaymentCompleted"/> -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, onUpdated, watch } from "vue";
import { useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { useTransaksiStore } from "src/stores/transaksi-store";
import { useComponentStore } from "src/stores/component-store";
import { useSettingsService } from "src/stores/settings-service";
import { usePetugasStore } from "src/stores/petugas-store";
import { userStore } from "src/stores/user-store";
import LoginDialog from "src/components/LoginDialog.vue";
import ApiUrlDialog from "src/components/ApiUrlDialog.vue";
import { getTime, checkSubscriptionExpiration } from "src/utils/time-util";
import ls from "localstorage-slim";

//Components
import Clock from "../components/Clock.vue";
// import PaymentCard from "src/components/PaymentCard.vue";
import Quotes from "src/components/Quotes.vue";
import ShinyCard from "src/components/ShinyCard.vue";
import Camera from "src/components/Camera.vue";
import CompanyName from "src/components/CompanyName.vue";
import SettingsDialog from "src/components/SettingsDialog.vue";
import EntryGatePage from "src/pages/Gate.vue";

// dialogues
import TicketDialog from "src/components/TicketDialog.vue";
import KendaraanKeluarDialog from "src/components/KendaraanKeluarDialog.vue";
import JenisKendaraanDialog from "src/components/JenisKendaraanDialog.vue";

// import FotoKendaraan from "../components/FotoKendaraan.vue";
// import { useMorphStore } from "src/stores/morph-store";
// import JenisKendaraanCard from "../components/JenisKendaraanCard.vue";
// import NomorTiketCard from "src/components/CarMorph.vue";
// import InfoCard from "src/components/InfoCard.vue";
// import PetugasCard from "src/components/PetugasCard.vue";

const transaksiStore = useTransaksiStore();
const componentStore = useComponentStore();
const settingsService = useSettingsService();
const petugasStore = usePetugasStore();
const gateSettings = computed(() => settingsService.gateSettings);
const $q = useQuasar();

// Helper function to parse RTSP URL for credentials and IP
const parseRtspUrl = (url, settings, typePrefix) => { // typePrefix is 'PLATE' or 'DRIVER'
  const config = { username: 'admin', password: 'password', ip_address: '' }; // Defaults

  if (!url) return config;

  const settingsUsername = settings?.[`${typePrefix}_CAM_USERNAME`];
  const settingsPassword = settings?.[`${typePrefix}_CAM_PASSWORD`];
  const settingsIpAddress = settings?.[`${typePrefix}_CAM_IP_ADDRESS`];

  if (settingsUsername) config.username = settingsUsername;
  if (settingsPassword) config.password = settingsPassword;
  // If dedicated IP field exists, prioritize it
  if (settingsIpAddress) {
    config.ip_address = settingsIpAddress;
    // If all three (user, pass, ip) are from specific settings, no need to parse URL for them
    if (settingsUsername && settingsPassword) return config;
  }

  // Fallback to parsing from URL if not all parts are from specific settings
  // Regex: rtsp://(?:([^:]+)(?::([^@]+))?@)?([^/:]+)(?::\d+)?(?:/.*)?
  // Group 1: username (optional)
  // Group 2: password (optional, only if username is present)
  // Group 3: host (ip_address or hostname)
  const match = url.match(/rtsp:\/\/(?:([^:]+)(?::([^@]+))?@)?([^/:@]+)/);

  if (match) {
    // Only overwrite from URL if not already set by specific settings fields
    if (match[3] && !config.ip_address) { // host
      config.ip_address = match[3];
    }
    if (match[1] && !settingsUsername) { // username
      config.username = match[1];
    }
    if (match[2] && !settingsPassword) { // password
      config.password = match[2];
    }
  }
  return config;
};

const darkMode = ref(ls.get("darkMode") ?? false);
const darkModeToggle = () => {
  darkMode.value = !darkMode.value;
  ls.set("darkMode", darkMode.value);
  
  // Apply dark mode to Quasar
  $q.dark.set(darkMode.value);
};

const cardVideo = ref(null);
const pegawai = ls.get("pegawai") ? ls.get("pegawai").nama : null;

// Camera configuration similar to ManlessEntryGate.vue
const plateCameraType = computed(() => {
  console.log('Computing plateCameraType - DEVICE_ID:', gateSettings.value, 'IP:', gateSettings.value?.PLATE_CAM_IP);
  if (gateSettings.value?.PLATE_CAM_DEVICE_ID) return 'usb';
  if (gateSettings.value?.PLATE_CAM_IP) return 'cctv';
  return null;
});

const driverCameraType = computed(() => {
  console.log('Computing driverCameraType - DEVICE_ID:', gateSettings.value?.DRIVER_CAM_DEVICE_ID, 'IP:', gateSettings.value?.DRIVER_CAM_IP);
  if (gateSettings.value?.DRIVER_CAM_DEVICE_ID) return 'usb';
  if (gateSettings.value?.DRIVER_CAM_IP) return 'cctv';
  return null;
});

// Camera URLs and Device IDs from gateSettings
const plateCameraUrl = computed(() => gateSettings.value?.PLATE_CAM_IP || '');
const driverCameraUrl = computed(() => gateSettings.value?.DRIVER_CAM_IP || '');
const plateCameraDeviceId = computed(() => gateSettings.value?.PLATE_CAM_DEVICE_ID || null);
const driverCameraDeviceId = computed(() => gateSettings.value?.DRIVER_CAM_DEVICE_ID || null);

const plateCameraCredentials = computed(() => {
  return parseRtspUrl(gateSettings.value?.PLATE_CAM_IP, gateSettings.value, 'PLATE');
});

const driverCameraCredentials = computed(() => {
  return parseRtspUrl(gateSettings.value?.DRIVER_CAM_IP, gateSettings.value, 'DRIVER');
});

const cameraInFileName = `${ls.get("lokasiPos")?.value}_in_snapshot`;
const cameraOutFileName = "02_out_snapshot";

// Camera refs
const plateCameraRef = ref(null);
const driverCameraRef = ref(null);
const cameraOutRef = ref(null);
const router = useRouter();

const inputPlatNomorRef = ref(null);
const prefix = ref(ls.get("prefix"));
// defineExpose({
//   inputPlatNomorRef,
// });

// nopolInput.register(inputPlatNomorRef)

const testPrint = () => {
  window.electron.print();
};

const onClickKendaraanKeluar = () => {
  const dialog = $q.dialog({
    component: KendaraanKeluarDialog,
  });
  
  dialog.onOk(async (exitData) => {
    if (exitData && exitData.plateNumber) {
      try {
        // Find existing transaction
        const transactions = await transaksiStore.searchTransactionByPlateNumber(exitData.plateNumber);
        const entryTransaction = transactions.find(t => t.status === 0 && !t.waktu_keluar);
        
        if (entryTransaction) {
          // Set current transaction for exit processing
          transaksiStore.currentTransaction = entryTransaction;
          transaksiStore.platNomor = exitData.plateNumber;
          
          // Capture exit images
          await captureExitImages();
          
          // Process exit transaction
          await transaksiStore.processExitTransaction();
          
          // Update statistics
          await updateStatistics();
          
          // Open gate for exit
          componentStore.openGate();
          
        } else {
          $q.notify({
            type: 'warning',
            message: 'Tidak ditemukan transaksi masuk untuk kendaraan ini',
            position: 'top'
          });
        }
      } catch (error) {
        console.error('Error processing vehicle exit:', error);
        $q.notify({
          type: 'negative',
          message: 'Gagal memproses kendaraan keluar',
          position: 'top'
        });
      }
    }
  });
};

// Capture images for exit
const captureExitImages = async () => {
  try {
    // Capture driver image
    const driverImageData = await driverCameraRef.value?.getImage();
    if (driverImageData && typeof driverImageData === 'string') {
      transaksiStore.pic_body_keluar = driverImageData;
    }
    
    // Capture plate image
    const plateImageData = await plateCameraRef.value?.getImage();
    if (plateImageData && typeof plateImageData === 'string') {
      transaksiStore.pic_plat_keluar = plateImageData;
    }
  } catch (error) {
    console.error('Error capturing exit images:', error);
  }
};

// Reset form and focus back to input
const resetFormState = () => {
  transaksiStore.resetTransactionState();
  componentStore.hideInputPlatNomor = false;
  
  setTimeout(() => {
    inputPlatNomorRef.value?.focus();
  }, 100);
};

// Handle payment completion (called from PaymentCard)
const onPaymentCompleted = async () => {
  try {
    // Update statistics after payment
    await updateStatistics();
    
    // Reset form state
    resetFormState();
    
    $q.notify({
      type: 'positive',
      message: 'Transaksi berhasil diselesaikan',
      position: 'top'
    });
  } catch (error) {
    console.error('Error completing payment:', error);
  }
};

const onInputPlatNomor = () => {
  if (transaksiStore.platNomor.length >= 3) {
    const firstCharacter = transaksiStore.platNomor?.charAt(0);

    if (!isNaN(firstCharacter)) {
      transaksiStore.platNomor =
        prefix.value + transaksiStore.platNomor?.toUpperCase();
    } else {
      transaksiStore.platNomor = transaksiStore.platNomor?.toUpperCase();
    }
  }
  // console.log(platNomorModel.value.toUpperCase());
};

const onClickBukaManual = async () => {
  try {
    // Get image from driver camera
    const imageData = await driverCameraRef.value?.getImage();
    
    if (imageData) {
      let imageBase64;
      if (typeof imageData === 'string') {
        imageBase64 = imageData;
      } else if (imageData instanceof Blob) {
        const reader = new FileReader();
        reader.onload = () => {
          imageBase64 = reader.result;
          transaksiStore.pic_body_masuk = imageBase64;
        };
        reader.readAsDataURL(imageData);
      }

      if (typeof imageData === 'string') {
        transaksiStore.pic_body_masuk = imageBase64;
      }
    }
    
    // Use transaksi store method with current gate location
    const gateId = transaksiStore.lokasiPos.value || '01';
    const success = await transaksiStore.setManualOpenGate(gateId);
    
    if (success) {
      componentStore.openGate();
      await updateStatistics();
    }
  } catch (error) {
    console.error('Error in manual gate open:', error);
    $q.notify({
      type: 'negative',
      message: 'Gagal membuka gate secara manual',
      position: 'top'
    });
  }
};

const onClickEmergency = async () => {
  try {
    // Get image from driver camera
    const imageData = await driverCameraRef.value?.getImage();
    
    if (imageData) {
      let imageBase64;
      if (typeof imageData === 'string') {
        imageBase64 = imageData;
      } else if (imageData instanceof Blob) {
        const reader = new FileReader();
        reader.onload = () => {
          imageBase64 = reader.result;
          transaksiStore.pic_body_masuk = imageBase64;
        };
        reader.readAsDataURL(imageData);
      }

      if (typeof imageData === 'string') {
        transaksiStore.pic_body_masuk = imageBase64;
      }
    }
    
    // Set emergency plate number if not set
    if (!transaksiStore.platNomor) {
      transaksiStore.platNomor = 'EMERGENCY';
    }
    
    // Use transaksi store method with emergency flag
    const gateId = transaksiStore.lokasiPos.value || '01';
    const success = await transaksiStore.setManualOpenGate(gateId);
    
    if (success) {
      componentStore.openGate();
      await updateStatistics();
      
      $q.notify({
        type: 'warning',
        message: 'Gate dibuka dalam mode emergency',
        position: 'top',
        timeout: 3000
      });
    }
  } catch (error) {
    console.error('Error in emergency gate open:', error);
    $q.notify({
      type: 'negative',
      message: 'Gagal membuka gate emergency',
      position: 'top'
    });
  }
};

const onPressEnterPlatNomor = async () => {
  if (transaksiStore.platNomor.length < 4) {
    $q.notify({
      type: "negative",
      message: "Cek kembali plat nomor yang anda input",
      position: "bottom",
      timeout: 500,
    });
    return;
  }

  try {
    // Capture driver image before processing
    await captureDriverImage();
    
    // Get customer data
    await transaksiStore.getCustomerByNopol();
    const dataCustomer = transaksiStore.dataCustomer;

    // Check operation mode from settings service
    if (settingsService.isPrepaidMode) {
      // Prepaid mode - show vehicle selection with immediate payment
      const _jenisKendaraanDialog = $q.dialog({
        component: JenisKendaraanDialog,
        componentProps: {
          isPrepaidMode: true,
          customerData: dataCustomer
        }
      });

      _jenisKendaraanDialog.onOk(() => {
        // Payment completed in prepaid mode - process entry
        processEntry(true); // true = prepaid mode
      });
    } else if (settingsService.isPostpaidMode) {
      // Postpaid mode - traditional flow
      if (!dataCustomer) {
        // No customer found - show jenis kendaraan dialog
        const _jenisKendaraanDialog = $q.dialog({
          component: JenisKendaraanDialog,
          componentProps: {
            isPrepaidMode: false,
            customerData: null
          }
        });

        _jenisKendaraanDialog.onOk(() => {
          processEntry(false); // false = postpaid mode
        });
      } else {
        // Customer found - use existing vehicle type
        const jenis_kendaraan = {
          id: dataCustomer.id_jenis_kendaraan,
          label: dataCustomer.jenis_kendaraan,
        };
        transaksiStore.selectedJenisKendaraan = jenis_kendaraan;
        
        // Check subscription expiration
        const expiration = checkSubscriptionExpiration(dataCustomer.akhir);
        
        const _ticketDialog = $q.dialog({
          component: TicketDialog,
          componentProps: {
            title: jenis_kendaraan?.label,
            nama: dataCustomer?.nama,
            alamat: dataCustomer?.alamat,
            expiration: expiration,
          },
        });

        _ticketDialog.onOk(() => {
          processEntry(false); // false = postpaid mode
        });
      }
    } else {
      // Fallback to manual mode
      console.warn('Unknown operation mode, falling back to postpaid mode');
      const _jenisKendaraanDialog = $q.dialog({
        component: JenisKendaraanDialog,
        componentProps: {
          isPrepaidMode: false,
          customerData: dataCustomer
        }
      });

      _jenisKendaraanDialog.onOk(() => {
        processEntry(false);
      });
    }
  } catch (error) {
    console.error('Error processing plate number:', error);
    $q.notify({
      type: 'negative',
      message: 'Terjadi kesalahan saat memproses plat nomor',
      position: 'top'
    });
  }
};

// Process entry transaction
const processEntry = async (isPrepaidMode = false) => {
  try {
    await transaksiStore.processEntryTransaction(isPrepaidMode);
    
    // Update statistics
    await updateStatistics();
    
    // Open gate
    componentStore.openGate();
    
    // For postpaid mode, hide input and show payment card
    // For prepaid mode, payment is already done, just reset the form
    if (isPrepaidMode) {
      // Reset form for next vehicle in prepaid mode
      transaksiStore.resetTransactionState();
      componentStore.hideInputPlatNomor = false;
      
      // Focus back to plate input for next vehicle
      setTimeout(() => {
        inputPlatNomorRef.value?.focus();
      }, 1000);
    } else {
      // Hide input and show payment card for postpaid mode
      componentStore.hideInputPlatNomor = true;
    }
    
  } catch (error) {
    console.error('Error processing entry:', error);
    $q.notify({
      type: 'negative',
      message: 'Gagal memproses transaksi masuk',
      position: 'top'
    });
  }
};

// Update vehicle statistics
const updateStatistics = async () => {
  try {
    await transaksiStore.getCountVehicleInToday();
    await transaksiStore.getCountVehicleOutToday();
    await transaksiStore.getCountVehicleInside();
    
    // Force component updates
    componentStore.vehicleOutKey = Date.now();
    
    console.log('Statistics updated:', {
      vehicleIn: transaksiStore.vehicleInToday,
      vehicleOut: transaksiStore.totalVehicleOut,
      vehicleInside: transaksiStore.totalVehicleInside
    });
  } catch (error) {
    console.error('Error updating statistics:', error);
  }
};

const logout = async () => {
  try {
    // Use petugas store logout
    petugasStore.logout();
    
    // Also try to logout from user store if needed
    await userStore().logout();
    
    // Clear all login related data
    ls.remove("pegawai");
    ls.remove("shift");
    ls.remove("timeLogin");
    ls.remove("isAdmin");
    ls.remove("tanggal");
    
    // Redirect to login
    window.location.reload();
  } catch (error) {
    console.error('Error during logout:', error);
    // Force logout anyway
    ls.clear();
    window.location.reload();
  }
};

const isAdmin = ls.get("isAdmin") || false;

const handleKeyDown = (event) => {
  // console.log(event.key);
  if (componentStore.currentPage == "outgate") {
    if (event.key === "F1") {
      event.preventDefault();
      inputPlatNomorRef.value.focus();
    } else if (event.key === "F4") {
      event.preventDefault();
      onClickKendaraanKeluar();
    } else if (event.key === "F2") {
      event.preventDefault();
      if (isAdmin) {
        componentStore.currentPage = "daftar-transaksi";
        router.push("/daftar-transaksi");
      } else {
        $q.notify({
          type: "negative",
          message: "Anda tidak memiliki akses",
          position: "bottom",
        });
      }
    } else if (event.shiftKey === true && event.key === "R") {
      event.preventDefault();
      onClickKendaraanKeluar();
    } else if (event.key === "F5") {
      event.preventDefault();
      logout();
      window.location.replace("/");
    } else if (event.shiftKey === true && event.key === "D") {
      event.preventDefault();
      darkModeToggle();
    } else if (event.key === "F8") {
      event.preventDefault();
      onClickBukaManual();
    } else if (event.key === "F12") {
      event.preventDefault();
      onClickEmergency();
    } else if (event.key === "F7") {
      event.preventDefault();
      if (isAdmin) {
        onClickSettings();
      } else {
        $q.notify({
          type: "negative",
          message: "Anda tidak memiliki akses",
          position: "bottom",
        });
      }
    }
  }
};

const onClickSettings = () => {
  // if (!transaksiStore.isAdmin) {
  //   const dialog = $q.dialog({
  //     component: LoginDialog,
  //     // noBackdropDismiss: true,
  //     // persistent: true,
  //     componentProps: {
  //       type: "check",
  //       component: "SettingsDialog",
  //     },
  //   });
  //   console.log(dialog);
  //   dialog.update();
  // } else {
  const settingsDialog = $q.dialog({
    component: SettingsDialog,
    persistent: true,
    noEscDismiss: true,
  });

  settingsDialog.update();
  // }
};

const onCameraError = (err) => {
  console.error('Camera error:', err);
  $q.notify({
    type: 'negative',
    message: `Camera error: ${err.message || err}`,
    position: 'top',
    timeout: 3000
  });
};

// Handler untuk hasil capture kamera plat nomor
const onPlateCaptured = (capturedData) => {
  console.log('Plate captured:', capturedData);
  if (capturedData && capturedData.image) {
    transaksiStore.pic_plat_masuk = capturedData.image;
    console.log('Plate image saved to store');
  }
  if (capturedData && capturedData.plateNumber) {
    transaksiStore.platNomor = capturedData.plateNumber.toUpperCase();
    console.log('Plate number detected:', capturedData.plateNumber);
  }
};

// Handler untuk capture gambar driver saat entry
const captureDriverImage = async () => {
  try {
    const imageData = await driverCameraRef.value?.getImage();
    if (imageData) {
      let imageBase64;
      if (typeof imageData === 'string') {
        imageBase64 = imageData;
      } else if (imageData instanceof Blob) {
        const reader = new FileReader();
        reader.onload = () => {
          imageBase64 = reader.result;
          transaksiStore.pic_body_masuk = imageBase64;
        };
        reader.readAsDataURL(imageData);
      }
      
      if (typeof imageData === 'string') {
        transaksiStore.pic_body_masuk = imageBase64;
      }
    }
  } catch (error) {
    console.error('Error capturing driver image:', error);
  }
};

onMounted(async () => {
  // Initialize settings service similar to ManlessEntryGate.vue
  if (!settingsService.activeGateId) {
    await settingsService.initializeSettings();
  }

  // Initialize petugas store
  try {
    await petugasStore.loadFromLocal();
    if (petugasStore.daftarPetugas.length === 0) {
      console.log('Initializing petugas data...');
      await petugasStore.seedPetugasData();
    }
    console.log('Petugas store initialized');
  } catch (error) {
    console.error('Error initializing petugas store:', error);
  }

  // Debug: Check if gateSettings are loaded correctly
  console.log('Manual Gate - gateSettings:', gateSettings.value);
  console.log('Manual Gate - plateCameraType:', plateCameraType.value);
  console.log('Manual Gate - driverCameraType:', driverCameraType.value);
  console.log('Manual Gate - PLATE_CAM_IP:', gateSettings.value?.PLATE_CAM_IP);
  console.log('Manual Gate - DRIVER_CAM_IP:', gateSettings.value?.DRIVER_CAM_IP);
  console.log('Manual Gate - PLATE_CAM_DEVICE_ID:', gateSettings.value?.PLATE_CAM_DEVICE_ID);
  console.log('Manual Gate - DRIVER_CAM_DEVICE_ID:', gateSettings.value?.DRIVER_CAM_DEVICE_ID);
  console.log('Manual Gate - plateCameraDeviceId:', plateCameraDeviceId.value);
  console.log('Manual Gate - driverCameraDeviceId:', driverCameraDeviceId.value);

  // Initialize dark mode
  const savedDarkMode = ls.get("darkMode");
  if (savedDarkMode !== null) {
    darkMode.value = savedDarkMode;
    $q.dark.set(darkMode.value);
  }

  componentStore.currentPage = "outgate";
  
  // Watch for dark mode changes
  watch(darkMode, (newValue) => {
    $q.dark.set(newValue);
    ls.set("darkMode", newValue);
  }, { immediate: true });

  // Watch for selectedJenisKendaraan changes to auto-process entry
  watch(
    () => transaksiStore.selectedJenisKendaraan,
    async (newValue, oldValue) => {
      // Only process if we have a new selection and we're not already checked in
      if (newValue && !transaksiStore.isCheckedIn && transaksiStore.platNomor) {
        console.log('Jenis kendaraan selected:', newValue);
        // Use the current operation mode from settings
        const isPrepaidMode = settingsService.isPrepaidMode;
        await processEntry(isPrepaidMode);
      }
    }
  );
  
  // Initialize statistics using transaksi store
  try {
    await updateStatistics();
    console.log('Initial statistics loaded');
  } catch (error) {
    console.error('Error loading initial statistics:', error);
  }

  // Check required configurations
  // if (transaksiStore.lokasiPos.value === "-" || !transaksiStore.lokasiPos.value) {
  //   $q.notify({
  //     type: "warning",
  //     message: "Lokasi pos belum dikonfigurasi, silahkan buka settings",
  //     position: "top",
  //   });
  //   // Don't return, allow continued operation
  // }

  // if (!transaksiStore.API_URL || transaksiStore.API_URL === "-") {
  //   console.warn('API URL not configured, working in offline mode');
  //   $q.notify({
  //     type: "info",
  //     message: "Mode offline - API tidak terkonfigurasi",
  //     position: "top",
  //     timeout: 2000
  //   });
  // }

  // Check authentication
  if (!pegawai || !ls.get("shift")) {
    const dialog = $q.dialog({
      component: LoginDialog,
      noBackdropDismiss: true,
      persistent: true,
      componentProps: {
        type: "login",
        url: "/",
      },
    });
    dialog.update();
  }

  // Focus on input
  setTimeout(() => {
    inputPlatNomorRef.value?.focus();
  }, 500);

  window.addEventListener("keydown", handleKeyDown);

  // Set up periodic statistics update
  const statsInterval = setInterval(() => {
    updateStatistics();
  }, 30000); // Update every 30 seconds

  // Store interval for cleanup
  componentStore.statsInterval = statsInterval;
});

onUnmounted(() => {
  // Clean up camera intervals
  if (plateCameraRef.value) {
    plateCameraRef.value.stopInterval?.();
  }
  
  if (driverCameraRef.value) {
    driverCameraRef.value.stopInterval?.();
  }
  
  // Clean up statistics interval
  if (componentStore.statsInterval) {
    clearInterval(componentStore.statsInterval);
    componentStore.statsInterval = null;
  }
  
  // Remove event listener
  window.removeEventListener("keydown", handleKeyDown);
  
  // Reset transaction state when leaving page
  transaksiStore.resetTransactionState();
  
  console.log('Manual gate component unmounted');
});
</script>

<style>
:deep(.q-dialog__backdrop.fixed-full) {
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
}

.rounded-corner {
  border-radius: 10px;
}

/* Prevent horizontal and vertical scrolling */
html, body {
  overflow: hidden !important;
  max-width: 100vw !important;
  max-height: 100vh !important;
}

.q-layout {
  overflow: hidden !important;
}

/* Ensure all containers don't exceed viewport */
* {
  box-sizing: border-box;
}

.full-width {
  max-width: 100vw !important;
}

.full-height {
  max-height: 100vh !important;
}

/* Camera containers should not overflow */
.camera-feed {
  object-fit: contain !important;
  max-width: 100% !important;
  max-height: 100% !important;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Prevent any element from causing horizontal scroll */
.window-width {
  max-width: 100vw !important;
  overflow: hidden !important;
}

/* } */
</style>

<style scoped>
:deep(.input-box .q-field__control),
:deep(.input-box .q-field__append .q-field__marginal) {
  height: 100px;
  max-width: 70vw;
  padding-top: 10px;
  font-size: 5em;
  font-family: "Courier New", Courier, monospace;
  overflow: hidden;
}

/* Ensure input container doesn't overflow */
.input-box {
  max-width: 100% !important;
  overflow: hidden !important;
}

/* Camera spacing */
.camera-container {
  gap: 2rem !important;
}

/* Add some space between cameras */
.q-gutter-md > .col-6:first-child {
  padding-right: 1rem;
}

.q-gutter-md > .col-6:last-child {
  padding-left: 1rem;
}

/* Dark mode styles */
.dark-mode {
  background-color: var(--q-dark) !important;
  color: var(--q-dark-page) !important;
}

.light-mode {
  background-color: var(--q-primary) !important;
  color: var(--q-primary-page) !important;
}

/* Dark mode specific overrides */
body.body--dark {
  background-color: #1d1d1d !important;
}

body.body--dark .bg-primary {
  background-color: #1976d2 !important;
}

body.body--dark .bg-grey-5 {
  background-color: #424242 !important;
}

body.body--dark .text-dark {
  color: #ffffff !important;
}

body.body--dark .bg-dark {
  background-color: #121212 !important;
}

body.body--dark .bg-grey-2 {
  background-color: #303030 !important;
}

body.body--dark .bg-grey-3 {
  background-color: #424242 !important;
}

body.body--dark .bg-secondary {
  background-color: #424242 !important;
}

/* Light mode overrides */
body.body--light .bg-primary {
  background-color: #1976d2 !important;
}

body.body--light .bg-grey-5 {
  background-color: #f5f5f5 !important;
}

body.body--light .text-dark {
  color: #000000 !important;
}
</style>
