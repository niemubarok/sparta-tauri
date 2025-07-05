<template>

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
    class="relative fixed-top window-height full-width overflow-hidden bg-primary"
  >
    <div
      v-if="!transaksiStore.isCheckedIn"
      class="flex row justify-between items-center q-pl-lg no-wrap q-pt-md"
      style="height: 150px"
    >
      <q-card  class="row items-center bg-grey-2" >
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

        <!-- <CompanyName /> -->
         <!-- <div style="width:150px"> -->

           <Logo />
          <!-- </div> -->
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
      <!-- <q-chip
      text-color="grey-3"
        class="bg-transparent"
        icon="place"
        :label="
          '(' +
          transaksiStore.lokasiPos.value +
          ') ' +
          transaksiStore.lokasiPos.label
        "
      /> -->
      
      <!-- Sync Status Indicator -->
      <q-chip
        v-if="isAdmin"
        :color="syncStatusColor"
        :text-color="syncStatusTextColor"
        :icon="syncStatusIcon"
        :label="syncStatusLabel"
        class="text-caption"
      >
        <q-tooltip>{{ syncStatusTooltip }}</q-tooltip>
      </q-chip>
      
      <Clock />
    </div>

    <!-- <div
      v-if="$q.screen.gt.sm && !transaksiStore.isCheckedIn"
      class="full-width q-pt-md"
    > -->
      <!-- <Quotes /> -->
    <!-- </div> -->

    <!-- KAMERA -->
    <div class="row justify-center items-center overflow-hidden q-mt-lg">
      <div class="col-12">
        <div
          v-if="!transaksiStore.isCheckedIn"
          ref="cardVideo"
          class="flex row justify-between content-center items-center q-px-sm relative bg-transparent overflow-hidden no-wrap"
          style="width: 100%; max-height: 62vh"
        >
          <div class="col-6 relative overflow-hidden">
            <q-chip
              class="absolute bg-transparent"
              icon="login"
              :label="`Kamera Masuk ${plateCameraCredentials.ip_address ? '(' + plateCameraCredentials.ip_address + ')' : '(Default)'}`"
              :color="plateCameraCredentials.ip_address && plateCameraCredentials.ip_address !== '192.168.10.25' ? 'positive' : 'warning'"
              text-color="white"
            />
           <Camera
              ref="entryCameraRef"
              :username="plateCameraCredentials.username"
              :password="plateCameraCredentials.password"
              :ipAddress="plateCameraCredentials.ip_address"
              :rtspStreamPath="gateSettings.PLATE_CAM_RTSP_PATH || 'Streaming/Channels/101'"
              :fileName="'entry'"
              cameraLocation="entry"
              :cameraType="plateCameraType"
              :deviceId="plateCameraDeviceId"
              @captured="onEntryCaptured"
              @error="onCameraError"
              class="camera-feed"
              label="Kamera Masuk"
              style="max-width: 100%; max-height: 52vh;"
            />
          </div>
          <div class="col-6 relative overflow-hidden q-ml-xs">
            <q-chip
              class="absolute bg-transparent"
              icon="logout"
              :label="`Kamera Keluar ${driverCameraCredentials.ip_address ? '(' + driverCameraCredentials.ip_address + ')' : '(Default)'}`"
              :color="driverCameraCredentials.ip_address && driverCameraCredentials.ip_address !== '192.168.10.26' ? 'positive' : 'warning'"
              text-color="white"
            />

            <Camera
              ref="exitCameraRef"
              class="rounded-corner"
              cameraLocation="exit"
              :username="driverCameraCredentials.username"
              :password="driverCameraCredentials.password"
              :ipAddress="driverCameraCredentials.ip_address"
              :rtspStreamPath="gateSettings.DRIVER_CAM_RTSP_PATH || 'Streaming/Channels/101'"
              :cameraType="driverCameraType"
              :deviceId="driverCameraType === 'usb' ? driverCameraDeviceId : undefined"
              :fileName="'exit'"
              label="Kamera Keluar"
              @error="onCameraError"
              style="max-width: 100%; max-height: 52vh;"
            />
          </div>
        </div>
      </div>
    </div>

    <div
      class="flex row justify-center fixed full-width no-wrap overflow-hidden bg-primary"
      style="bottom: 20px; max-width: 100vw;"
    >
      <div class="col-8 overflow-hidden">
        <q-input
          v-show="
            !componentStore.hideInputPlatNomor && !transaksiStore.isCheckedIn
          "
          input-class="input-box  text-black text-weight-bolder"
          class="input-box rounded-corner relative text-uppercase q-pa-md q-mb-xl bg-grey-2"
          input-style="height:90px;border:0"
          label-color="grey-9 text-body1 q-pb-sm"
          
          item-aligned
          borderless
          v-model="transaksiStore.platNomor"
          label="Masukkan Plat Nomor"
          ref="inputPlatNomorRef"
          autofocus
        
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
          <q-btn v-if="isAdmin" color="grey-8" size="sm" label="Daftar Transaksi" @click="onClickDashboard">
            <q-badge
              color="primary"
              text-color="white"
              label="F2"
              class="q-mx-xs"
            />
            <q-tooltip content-class="bg-primary">Dashboard Admin</q-tooltip>
          </q-btn>
          <q-btn v-if="isAdmin" color="grey-8" size="sm" label="Dashboard" @click="onClickDashboard">
            <q-badge
              color="primary"
              text-color="white"
              label="F3"
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
          v-if="isAdmin"
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
          <!-- <q-btn
            color="red-9 "
            size="sm"
            @click="onClickEmergency()"
            label="Emergency"
          > -->
            <!-- icon="settings" -->
            <!-- <q-badge
              color="primary"
              text-color="white"
              label="F12"
              class="q-ml-xs"
            />
          </q-btn> -->

          <!-- Test button untuk melihat gambar CCTV -->
          <!-- <ViewImagesButton
            v-if="transaksiStore.currentTransaction?.id"
            :transactionId="transaksiStore.currentTransaction.id"
            color="info"
            label="Lihat CCTV"
            icon="camera_alt"
            tooltip="Lihat gambar CCTV dari transaksi saat ini"
          /> -->

          <!-- Test button untuk capture manual -->
          <!-- <q-btn
            v-if="isAdmin"
            color="orange"
            size="sm"
            @click="testCaptureImages"
            label="Test Capture"
            icon="camera"
          >
            <q-tooltip>Test capture gambar dari kedua kamera</q-tooltip>
          </q-btn> -->

          <!-- Test button untuk koneksi kamera -->
          <!-- <q-btn
            v-if="isAdmin"
            color="purple"
            size="sm"
            @click="testCameraConnection"
            label="Test Koneksi"
            icon="wifi"
          >
            <q-tooltip>Test koneksi ke kamera CCTV</q-tooltip>
          </q-btn> -->

          <!-- Test button untuk member card -->
          <!-- <q-btn
            v-if="isAdmin"
            color="green"
            size="sm"
            @click="testMemberCard"
            label="Test Card"
            icon="credit_card"
          >
            <q-tooltip>Test kartu member</q-tooltip>
          </q-btn> -->

          <!-- Test button untuk database sync -->
          <!-- <q-btn
            v-if="isAdmin"
            color="purple"
            size="sm"
            @click="testDatabaseSync"
            label="Test Sync"
            icon="sync"
          >
            <q-tooltip>Test sinkronisasi database</q-tooltip>
          </q-btn> -->

          <!-- Reload camera config button -->
          <!-- <q-btn
            v-if="isAdmin"
            color="blue"
            size="sm"
            @click="reloadCameraConfig"
            label="Reload Config"
            icon="refresh"
          >
            <q-tooltip>Muat ulang konfigurasi kamera dari settings</q-tooltip>
          </q-btn> -->

          <!-- Dark Mode Toggle Button -->

<!-- <q-btn
  unelevated
  color="purple"
  text-color="white"
  icon="sync"
  label="Test Live Sync"
  class="q-mr-sm q-mb-sm"
  @click="testLiveSync"
  title="Test apakah live sync berjalan tanpa manual trigger"
/>

<q-btn
  unelevated
  color="orange"
  text-color="white"
  icon="refresh"
  label="Restart Sync"
  class="q-mr-sm q-mb-sm"
  @click="restartSyncInitialization"
  title="Restart semua sync initialization seperti pertama kali buka app"
/> -->
          <!-- Status Debug Panel (only for admin) -->
          <q-btn
            v-if="isAdmin"
            color="teal"
            size="sm"
            @click="showSystemStatus"
            label="System Status"
            icon="info"
          >
            <q-tooltip>Lihat status sistem dan komponen</q-tooltip>
          </q-btn>

          <!-- Manual Sync Button (only for admin) -->
          <!-- <q-btn
            v-if="isAdmin"
            color="purple"
            size="sm"
            @click="testManualSync"
            label="Force Sync"
            icon="sync"
          >
            <q-tooltip>Paksa sinkronisasi manual ke server</q-tooltip>
          </q-btn> -->

          <!-- Transaction Verification Button (only for admin) -->
          <!-- <q-btn
            v-if="isAdmin && transaksiStore.currentTransaction?.id"
            color="indigo"
            size="sm"
            @click="testTransactionVerification"
            label="Verify Transaction"
            icon="verified"
          >
            <q-tooltip>Verifikasi transaksi terakhir di server</q-tooltip>
          </q-btn> -->
        </div>

        <!-- <q-toggle
        v-model="darkMode"
        @update:model-value="darkModeToggle"
        color="green"
      /> -->
      </div>
    </div>
    <!-- <PaymentCard v-if="transaksiStore.isCheckedIn" @payment-completed="onPaymentCompleted"/> -->
    
    <!-- Camera Debugger (only for admin) -->
    <!-- <CameraDebugger
      :plateCameraType="plateCameraType"
      :driverCameraType="driverCameraType"
      :plateCameraCredentials="plateCameraCredentials"
      :driverCameraCredentials="driverCameraCredentials"
      :plateCameraRef="entryCameraRef"
      :driverCameraRef="exitCameraRef"
    /> -->
  </div>

  <!-- MemberCard dialog -->
  <!-- <q-dialog v-model="showMemberDialog" >
    <MemberCard :plate-number="transaksiStore.platNomor" :nama="currentMember.name" :jenis-member="currentMember.membershipType" :end-date="currentMember.end_date" @enter="focusEnter"/>
   
  </q-dialog> -->
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, onUpdated, watch } from "vue";
import { useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { useTransaksiStore } from "src/stores/transaksi-store";
import { useComponentStore } from "src/stores/component-store";
import { useSettingsService } from "src/stores/settings-service";
import { usePetugasStore } from "src/stores/petugas-store";
import { useGateStore } from "src/stores/gate-store";
import { userStore } from "src/stores/user-store";
import { useMembershipStore } from "src/stores/membership-store";
import LoginDialog from "src/components/LoginDialog.vue";
import Logo from "src/components/Logo.vue";
import ApiUrlDialog from "src/components/ApiUrlDialog.vue";
import { getTime, checkSubscriptionExpiration } from "src/utils/time-util";
import ls from "localstorage-slim";
import { syncSingleDatabase, getSyncStatus, isSyncing, lastSyncStatus, lastSyncError, forceSyncAllDatabases, safeSyncTransaction, checkRemoteConnection, forceSyncAndVerifyTransaction } from "src/boot/pouchdb"
import MemberCard from "src/components/MemberCard.vue";

//Components
import Clock from "../components/Clock.vue";
// import PaymentCard from "src/components/PaymentCard.vue";
import Quotes from "src/components/Quotes.vue";
import ShinyCard from "src/components/ShinyCard.vue";
import Camera from "src/components/Camera.vue";
import CompanyName from "src/components/CompanyName.vue";
import SettingsDialog from "src/components/SettingsDialog.vue";
// Card Reader integration (keyboard wedge detection)
import mitt from 'mitt';
const emitter = mitt();

// Simulasi event kartu member terbaca
// emitter.emit('card-read', { cardNumber: '1234567890' });

// Card reader buffer & detection logic
let cardBuffer = '';
let cardTimer = null;
const CARD_MIN_LENGTH = 6; // minimal panjang card_number
const CARD_MAX_LENGTH = 32; // maksimal panjang card_number
const CARD_INPUT_TIMEOUT = 50; // ms antar karakter (card reader cepat)
const CARD_END_TIMEOUT = 150; // ms setelah input terakhir dianggap selesai

function isCardInput(char) {
  // Card reader biasanya hanya angka, kadang ada prefix/suffix
  return /[0-9A-Za-z]/.test(char);
}

function resetCardBuffer() {
  cardBuffer = '';
  if (cardTimer) {
    clearTimeout(cardTimer);
    cardTimer = null;
  }
}

function handleCardInput(char) {
  if (!isCardInput(char)) {
    if (cardBuffer.length > 0) {
      console.log('🔄 Invalid char detected, resetting card buffer:', char);
    }
    resetCardBuffer();
    return;
  }
  cardBuffer += char;
  console.log('📝 Card buffer:', cardBuffer);
  
  if (cardTimer) clearTimeout(cardTimer);
  cardTimer = setTimeout(async () => {
    // Jika buffer cukup panjang, anggap sebagai card reader
    if (
      cardBuffer.length >= CARD_MIN_LENGTH &&
      cardBuffer.length <= CARD_MAX_LENGTH
    ) {
      console.log('💳 Card detected from keyboard wedge:', cardBuffer);
      // Trigger proses kartu member
      await handleMemberCardTap(cardBuffer);
      // Setelah proses tap kartu, tetap fokus di input plat nomor
      setTimeout(() => {
        inputPlatNomorRef.value?.focus && inputPlatNomorRef.value.focus();
      }, 100);
    } else {
      console.log('⚠️ Card buffer length invalid:', cardBuffer.length);
    }
    resetCardBuffer();
  }, CARD_END_TIMEOUT);
}

// Card reader initialization flag dengan status yang lebih detail
const cardReaderStatus = ref({
  ready: false,
  initialized: false,
  error: null
});

const serialPortStatus = ref({
  ready: false,
  initialized: false,
  error: null
});

const membershipStoreStatus = ref({
  ready: false,
  membersLoaded: false,
  error: null
});


const currentMember = ref(null)
const showMemberDialog = ref(false)

const onClickDashboard = () => {
  // Only allow admin to access dashboard
  if (isAdmin.value) {
    componentStore.startingApp = false;
    router.push('/');
  } else {
    $q.notify({
      type: "negative",
      message: "Anda tidak memiliki akses ke Dashboard",
      position: "bottom",
    });
  }
};

// Listen card reader event (mitt, for simulation/testing only)
const initializeCardReader = async (retryCount = 0) => {
  const maxRetries = 3;
  
  try {
    console.log(`🔧 Initializing card reader (attempt ${retryCount + 1}/${maxRetries + 1})...`);
    
    // Check if membership store is ready first
    if (!membershipStoreStatus.value.ready) {
      console.warn('⚠️ Membership store not ready yet, waiting...');
      if (retryCount < maxRetries) {
        setTimeout(() => initializeCardReader(retryCount + 1), 1000);
        return;
      } else {
        throw new Error('Membership store not ready after max retries');
      }
    }
    
    // Clean up any existing listeners
    try {
      emitter.off('card-read');
      window.removeEventListener('keydown', cardReaderKeydownHandler, true);
    } catch (cleanupError) {
      console.log('🧹 Cleanup completed (some listeners may not have existed)');
    }
    
    emitter.on('card-read', async (payload) => {
      if (!payload?.cardNumber) return;
      if (!cardReaderStatus.value.ready) {
        console.warn('⚠️ Card reader not ready yet, ignoring tap');
        return;
      }
      await handleMemberCardTap(payload.cardNumber);
    });

    // Listen global keydown for card reader (keyboard wedge)
    window.addEventListener('keydown', cardReaderKeydownHandler, true);
    
    cardReaderStatus.value = {
      ready: true,
      initialized: true,
      error: null
    };
    
    console.log('✅ Card reader initialized and ready');
    
    // Show success notification
    $q.notify({
      type: 'positive',
      message: 'Card reader siap digunakan',
      position: 'top',
      timeout: 2000,
      icon: 'credit_card'
    });
    
  } catch (error) {
    console.error('❌ Failed to initialize card reader:', error);
    cardReaderStatus.value = {
      ready: false,
      initialized: false,
      error: error.message
    };
    
    // Show error notification
    $q.notify({
      type: 'negative',
      message: `Gagal inisialisasi card reader: ${error.message}`,
      position: 'top',
      timeout: 5000
    });
    
    // Retry if not max attempts
    if (retryCount < maxRetries) {
      console.log(`🔄 Retrying card reader initialization in 2 seconds...`);
      setTimeout(() => initializeCardReader(retryCount + 1), 2000);
    }
  }
};

function cardReaderKeydownHandler(e) {
  // Ignore if modifier pressed or not visible
  if (e.altKey || e.ctrlKey || e.metaKey) return;
  // Only process visible gate page
  if (componentStore.currentPage !== 'outgate') return;
  // Check if card reader is ready
  if (!cardReaderStatus.value.ready) {
    console.warn('⚠️ Card reader not ready yet, ignoring keydown');
    return;
  }
  // Tetap proses card reader meskipun fokus di input plat nomor
  if (e.key.length === 1) {
    handleCardInput(e.key);
    // Jangan preventDefault, biar input manual tetap bisa
    // e.preventDefault();
    // e.stopPropagation();
  }
}

// Fungsi utama: handle tap kartu member
import { localDbs, addTransaction, addTransactionAttachment } from 'src/boot/pouchdb';

const findMemberByCardNumber = (cardNumber) => {
  // Debug: log search attempt
  console.log('🔍 Searching for card number:', cardNumber);
  console.log('📋 Available members:', membershipStore.members.length);
  
  // Debug: log all card numbers in store
  membershipStore.members.forEach((member, index) => {
    console.log(`Member ${index + 1}:`, {
      name: member.name,
      card_number: member.card_number,
      member_id: member.member_id,
      active: member.active
    });
  });
  
  // Cari member di state store
  const foundMember = membershipStore.members.find(m => m.card_number === cardNumber);
  
  if (foundMember) {
    console.log('✅ Member found:', foundMember.name);
  } else {
    console.log('❌ Member not found for card number:', cardNumber);
  }
  
  return foundMember;
};

const cardTapping = ref(false)
const processingMemberTransaction = ref(false)

const handleMemberCardTap = async (member) => {
  try {
    cardTapping.value = true
    processingMemberTransaction.value = true

    console.log('🎫 Member card tapped:', member.card_number);
    console.log('� Card reader ready:', cardReaderStatus.value);
    console.log('�📊 Membership store state:', {
      membersLoaded: membershipStore.members.length,
      isLoading: membershipStore.isLoading,
      storeInitialized: !!membershipStore.db
    });
    console.log('🏛️ Component store state:', {
      currentPage: componentStore.currentPage,
      hideInputPlatNomor: componentStore.hideInputPlatNomor
    });
    
    // Pastikan system ready
    // if (!cardReaderStatus.value.ready) {
    //   console.warn('⚠️ Card reader not ready, aborting...');
    //   $q.notify({
    //     type: 'warning',
    //     message: 'System belum siap, silakan coba lagi',
    //     position: 'top',
    //   });
    //   return;
    // }
    
    // Pastikan membership store sudah ter-load
    if (membershipStore.members.length === 0) {
      console.log('⚠️ No members in store, attempting to reload...');
      await membershipStore.loadMembers();
      
      // Check again after reload
      if (membershipStore.members.length === 0) {
        console.error('❌ Still no members after reload');
        $q.notify({
          type: 'negative',
          message: 'Tidak dapat memuat data member',
          position: 'top',
        });
        return;
      }
    }
    
    // Cari member berdasarkan nomor kartu
    // const member = findMemberByCardNumber(cardNumber);
    if (!member) {
      $q.notify({
        type: 'negative',
        message: 'Kartu tidak terdaftar sebagai member',
        position: 'top',
      });
      return;
    }
    
    console.log('👤 Member found:', member);
    
    // Cek status aktif dan masa berlaku
    if (!member.active || membershipStore.isExpired(member.end_date)) {
      $q.notify({
        type: 'warning',
        message: 'Member tidak aktif atau sudah kadaluarsa',
        position: 'top',
      });
      return;
    }
    
    // Set plate number dari data member (jika ada)
    if (member.vehicles && member.vehicles.length > 0) {
      transaksiStore.platNomor = member.vehicles[0].plate_number || member.vehicles[0].license_plate || 'MEMBER';
    } else {
      transaksiStore.platNomor = 'MEMBER';
    }
    
    console.log('🚗 Plate number set to:', transaksiStore.platNomor);
    
    // Set jenis kendaraan dari data member
    if (member.vehicles && member.vehicles.length > 0 && member.vehicles[0].vehicle_type) {
      transaksiStore.selectedJenisKendaraan = {
        id: member.vehicles[0].vehicle_type_id || 1,
        label: member.vehicles[0].vehicle_type || member.vehicles[0].type || 'Motor'
      };
    } else {
      // Default ke Motor jika tidak ada data kendaraan
      transaksiStore.selectedJenisKendaraan = {
        id: 1,
        label: 'Motor'
      };
    }
    
    console.log('🏍️ Vehicle type set to:', transaksiStore.selectedJenisKendaraan);
    
    // Capture gambar masuk dengan optimasi kecepatan
    console.log('📸 Starting image capture for member transaction...');
    captureEntryImages(false); // Use normal mode for member transactions
    
    // Don't wait for image capture to complete - proceed immediately
    console.log('✅ Member transaction proceeding without waiting for image capture');
    
    // Simpan transaksi ke database transactions
    await saveMemberTransaction(member);
    
    // Show member details dialog instead of auto-opening gate
    currentMember.value = member
    
    // showMemberDialog.value = true
   

    // Reset form setelah small delay untuk memastikan semua proses selesai
    setTimeout(() => {
      resetFormState();
    }, 500);
    
    await updateStatistics();

    await gateStore.openGate();
    
  } catch (error) {
    console.error('Error handleMemberCardTap:', error);
    $q.notify({
      type: 'negative',
      message: 'Gagal memproses kartu member',
      position: 'top',
    });
  } finally {
    cardTapping.value = false;
    processingMemberTransaction.value = false;
  }
};

// Simpan transaksi member ke database transactions
const saveMemberTransaction = async (member) => {
  try {
    // Debug: Check if entry_pic exists before saving
    console.log('🖼️ Checking entry_pic before saving:', {
      hasEntryPic: !!transaksiStore.entry_pic,
      entryPicLength: transaksiStore.entry_pic?.length || 0,
      entryPicPreview: transaksiStore.entry_pic?.substring(0, 50) + '...' || 'null'
    });

    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    const id = `${timestamp}${random}` 
    
    // Data transaksi member (tanpa gambar dulu)
    const trx = {
      _id: `transaction_${id}`,
      type: 'member_entry',
      member_id: member.member_id,
      name: member.name,
      card_number: member.card_number,
      no_pol: transaksiStore.platNomor,
      entry_time: new Date().toISOString(),
      vehicle: member.vehicles?.[0] || null,
      jenis_kendaraan: transaksiStore.selectedJenisKendaraan || { id: 1, label: 'Motor' },
      membership_type_id: member.membership_type_id,
      created_by: pegawai || 'system',
      lokasi: transaksiStore.lokasiPos?.label || '',
      status: 0,
      is_member: true,
      tarif: 0, // Member tidak dikenakan tarif
      payment_status: 'paid', // Member sudah bayar melalui membership
      has_image: !!transaksiStore.entry_pic // Flag untuk menandai apakah ada gambar
    };
    
    // Debug: Check transaction object before saving
    console.log('💾 Transaction object to save:', {
      id: trx._id,
      member_name: trx.name,
      plate: trx.plat_nomor,
      type: trx.type,
      has_image: trx.has_image
    });
    
    // 1. Simpan transaksi dulu dengan immediate sync
    const response = await addTransaction(trx, true); // Enable immediate sync
    console.log('✅ Member transaction saved successfully with immediate sync:', response);
    
    // Debug: Check what ID was actually saved
    console.log('🆔 Transaction ID comparison:', {
      originalId: trx._id,
      responseId: response.id,
      responseRev: response.rev
    });
    
    // 2. Try to verify sync with timeout
    setTimeout(async () => {
      try {
        console.log('🔍 Verifying transaction sync to server...');
        const syncSuccess = await safeSyncTransaction(response.id);
        if (syncSuccess) {
          console.log('✅ Transaction successfully synced to server');
          $q.notify({
            type: 'positive',
            message: 'Transaksi berhasil disinkronisasi ke server',
            position: 'top',
            timeout: 2000,
            icon: 'cloud_done'
          });
        } else {
          console.warn('⚠️ Transaction sync verification failed');
          $q.notify({
            type: 'warning',
            message: 'Transaksi tersimpan lokal, sync ke server akan dilakukan nanti',
            position: 'top',
            timeout: 3000,
            icon: 'cloud_queue'
          });
        }
      } catch (verifyError) {
        console.error('❌ Sync verification error:', verifyError);
      }
    }, 2000); // Check sync after 2 seconds
    
    // 2. Simpan gambar sebagai attachment jika ada
    if (transaksiStore.entry_pic) {
      try {
        // Remove data:image/jpeg;base64, prefix if exists
        let base64Data = transaksiStore.entry_pic;
        if (base64Data.includes(',')) {
          base64Data = base64Data.split(',')[1];
        }
        
        console.log('💾 Saving attachment with cleaned base64 data:', {
          originalLength: transaksiStore.entry_pic.length,
          cleanedLength: base64Data.length,
          hasPrefix: transaksiStore.entry_pic !== base64Data
        });
        
        // Use response.id to ensure we use the actual saved document ID
        await addTransactionAttachment(
          response.id,
          response.rev,
          'entry.jpg',
          base64Data,
          'image/jpeg'
        );
        
        console.log('✅ Entry image attachment saved successfully');
        
        // Debug: Verify attachment was saved by trying to read it back
        try {
          const { getTransactionAttachment } = await import('src/boot/pouchdb');
          const testBlob = await getTransactionAttachment(response.id, 'entry.jpg');
          console.log('🔍 Attachment verification successful:', {
            transactionId: response.id,
            attachmentName: 'entry.jpg',
            blobSize: testBlob.size,
            blobType: testBlob.type
          });
        } catch (verificationError) {
          console.error('❌ Attachment verification failed:', verificationError);
        }
      } catch (attachmentError) {
        console.error('❌ Error saving entry image attachment:', attachmentError);
        // Don't throw error, just log it - transaction continues without image
        console.log('📝 Transaction saved successfully without image attachment');
        $q.notify({
          type: 'info',
          message: 'Transaksi tersimpan berhasil, gambar tidak dapat disimpan',
          position: 'top',
          timeout: 3000
        });
      }
    } else {
      console.log('📝 No entry image to save as attachment - transaction saved without image');
    }
    
  } catch (err) {
    console.error('❌ Error saving member transaction:', err);
    throw err;
  }
};

// dialogues
import TicketDialog from "src/components/TicketDialog.vue";
import KendaraanKeluarDialog from "src/components/KendaraanKeluarDialog.vue";
import JenisKendaraanDialog from "src/components/JenisKendaraanDialog.vue";
import VehicleInsideDialog from "src/components/VehicleInsideDialog.vue";

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
const membershipStore = useMembershipStore();


const gateStore = useGateStore()
const gateSettings = computed(() => settingsService.gateSettings);
const $q = useQuasar();

// Initialize dark mode from localStorage with proper default
const darkMode = ref(false);

// Initialize dark mode immediately when script loads
const initializeDarkMode = () => {
  const savedDarkMode = ls.get("darkMode");
  if (savedDarkMode !== null && savedDarkMode !== undefined) {
    darkMode.value = savedDarkMode;
  } else {
    // Default to system preference if available
    darkMode.value = window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false;
    ls.set("darkMode", darkMode.value);
  }
  
  // Apply immediately to prevent flash
  $q.dark.set(darkMode.value);
  console.log('🌙 Dark mode initialized:', darkMode.value);
};

const darkModeToggle = () => {
  darkMode.value = !darkMode.value;
  ls.set("darkMode", darkMode.value);
  $q.dark.set(darkMode.value);
  console.log('🌙 Dark mode toggled to:', darkMode.value);
};

// Initialize dark mode immediately
initializeDarkMode();

const entryCameraRef = ref(null);
const exitCameraRef = ref(null);
const cardVideo = ref(null);
const pegawai = ls.get("pegawai") ? ls.get("pegawai").nama : null;

// Camera configuration similar to ManlessEntryGate.vue
const plateCameraType = computed(() => {
  // Check the explicit camera mode setting first
  if (gateSettings.value?.PLATE_CAM_MODE) {
    console.log('🎥 Plate camera mode from settings:', gateSettings.value.PLATE_CAM_MODE);
    return gateSettings.value.PLATE_CAM_MODE; // 'usb' or 'cctv'
  }
  // Fallback to legacy detection for backwards compatibility
  if (gateSettings.value?.PLATE_CAM_DEVICE_ID) {
    console.log('🎥 Plate camera mode detected: USB (legacy)');
    return 'usb';
  }
  if (gateSettings.value?.PLATE_CAM_IP) {
    console.log('🎥 Plate camera mode detected: CCTV (legacy)');
    return 'cctv';
  }
  console.log('🎥 Plate camera mode: CCTV (default)');
  return 'cctv'; // Default to cctv if no specific config
});

const driverCameraType = computed(() => {
  // Check the explicit camera mode setting first
  if (gateSettings.value?.DRIVER_CAM_MODE) {
    console.log('🎥 Driver camera mode from settings:', gateSettings.value.DRIVER_CAM_MODE);
    return gateSettings.value.DRIVER_CAM_MODE; // 'usb' or 'cctv'
  }
  // Fallback to legacy detection for backwards compatibility
  if (gateSettings.value?.DRIVER_CAM_DEVICE_ID) {
    console.log('🎥 Driver camera mode detected: USB (legacy)');
    return 'usb';
  }
  if (gateSettings.value?.DRIVER_CAM_IP) {
    console.log('🎥 Driver camera mode detected: CCTV (legacy)');
    return 'cctv';
  }
  console.log('🎥 Driver camera mode: CCTV (default)');
  return 'cctv'; // Default to cctv if no specific config
});

// Camera URLs and Device IDs from gateSettings
const plateCameraUrl = computed(() => gateSettings.value?.PLATE_CAM_IP || '');
const driverCameraUrl = computed(() => gateSettings.value?.DRIVER_CAM_IP || '');
const plateCameraDeviceId = computed(() => gateSettings.value?.PLATE_CAM_DEVICE_ID || null);
const driverCameraDeviceId = computed(() => gateSettings.value?.DRIVER_CAM_DEVICE_ID || null);

const plateCameraCredentials = computed(() => {
  // Prioritaskan konfigurasi yang sudah ada di settings-service
  const config = {
    username: gateSettings.value?.PLATE_CAM_USERNAME || 'admin',
    password: gateSettings.value?.PLATE_CAM_PASSWORD || 'admin123',
    ip_address: gateSettings.value?.PLATE_CAM_IP || ''
  };
  
  // Jika tidak ada IP di settings, gunakan default untuk testing
  if (!config.ip_address) {
    config.ip_address = '192.168.10.25';
  }
  
  return config;
});

const driverCameraCredentials = computed(() => {
  // Prioritaskan konfigurasi yang sudah ada di settings-service
  const config = {
    username: gateSettings.value?.DRIVER_CAM_USERNAME || 'admin',
    password: gateSettings.value?.DRIVER_CAM_PASSWORD || 'admin123',
    ip_address: gateSettings.value?.DRIVER_CAM_IP || ''
  };
  
  // Jika tidak ada IP di settings, gunakan default untuk testing
  if (!config.ip_address) {
    config.ip_address = '192.168.10.26';
  }
  
  return config;
});

const cameraInFileName = `${ls.get("lokasiPos")?.value}_in_snapshot`;
const cameraOutFileName = "02_out_snapshot";

// Camera refs
const cameraOutRef = ref(null);
const router = useRouter();

const inputPlatNomorRef = ref(null);
const prefix = ref(ls.get("prefix")) || 'B';

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
          
          // // Capture exit images
          // await captureExitImages();
          
          // // Process exit transaction
          // await transaksiStore.processExitTransaction();
          
          // Update statistics
          // await updateStatistics();
          
          // Open gate for exit
          // componentStore.openGate();
          
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
    console.log('📸 Capturing exit images from exit camera...');
    
    // Clear any existing entry image to prevent contamination
    transaksiStore.entry_pic = null;
    console.log('🧹 Cleared entry_pic before exit capture');
    
    // Check if exit camera ref exists and is available
    if (!exitCameraRef.value) {
      console.warn('⚠️ Exit camera ref not available, continuing without exit image');
      transaksiStore.exit_pic = null;
      
      // $q.notify({
      //   type: 'info',
      //   message: 'Kamera keluar tidak tersedia, transaksi tetap dilanjutkan',
      //   position: 'top',
      //   timeout: 2000
      // });
      return;
    }
    
    // Capture exit image with error handling
    console.log('📷 Attempting to capture exit image from exitCameraRef...');
    const exitImageData = await exitCameraRef.value?.getImage();
    
    console.log('📷 Exit capture result:', {
      hasData: !!exitImageData,
      dataType: typeof exitImageData,
      dataLength: exitImageData?.length || 0
    });
    
    if (exitImageData && typeof exitImageData === 'string') {
      transaksiStore.exit_pic = exitImageData;
      console.log('✅ Exit image captured and saved to exit_pic');
      console.log('📊 Debug: exit_pic set to:', transaksiStore.exit_pic ? 'Base64 image data' : 'null');
      console.log('📊 Debug: entry_pic is:', transaksiStore.entry_pic ? 'Base64 image data' : 'null');
      
      $q.notify({
        type: 'positive',
        message: 'Gambar keluar berhasil diambil',
        position: 'top',
        timeout: 2000
      });
    } else {
      console.warn('⚠️ No exit image data received, continuing without image');
      transaksiStore.exit_pic = null;
      console.log('📊 Debug: exit_pic set to null');
      console.log('📊 Debug: entry_pic is:', transaksiStore.entry_pic ? 'Base64 image data' : 'null');
      
      // $q.notify({
      //   type: 'info',
      //   message: 'Tidak dapat mengambil gambar keluar, transaksi tetap dilanjutkan',
      //   position: 'top',
      //   timeout: 2000
      // });
    }
    
    // Final debug check
    console.log('📊 Final image state after exit capture:', {
      hasEntryPic: !!transaksiStore.entry_pic,
      hasExitPic: !!transaksiStore.exit_pic,
      entryPicLength: transaksiStore.entry_pic?.length || 0,
      exitPicLength: transaksiStore.exit_pic?.length || 0
    });
    
    console.log('✅ Exit image capture process completed');
    
  } catch (error) {
    console.error('❌ Error capturing exit images:', error);
    transaksiStore.exit_pic = null;
    transaksiStore.entry_pic = null; // Also clear entry pic on error
    console.log('📊 Debug: Both images set to null (error case)');
    console.log('📊 Debug: entry_pic is:', transaksiStore.entry_pic ? 'Base64 image data' : 'null');
    console.log('📊 Debug: exit_pic is:', transaksiStore.exit_pic ? 'Base64 image data' : 'null');
    
    // $q.notify({
    //   type: 'info',
    //   message: 'Kamera keluar tidak tersedia, transaksi tetap dilanjutkan',
    //   position: 'top',
    //   timeout: 2000
    // });
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
// const onPaymentCompleted = async () => {
//   try {
//     // Update statistics after payment
//     await updateStatistics();
    
//     // Reset form state
//     resetFormState();
    
//     $q.notify({
//       type: 'positive',
//       message: 'Transaksi berhasil diselesaikan',
//       position: 'top'
//     });
//   } catch (error) {
//     console.error('Error completing payment:', error);
//   }
// };

const onInputPlatNomor = () => {
  if (transaksiStore.platNomor.length >= 3) {
    const firstCharacter = transaksiStore.platNomor?.charAt(0);

    if (!isNaN(firstCharacter) && prefix.value && transaksiStore.platNomor.length < 6) {
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
    // Always open gate first for manual operation
    gateStore.writeToPort('entry', ' *OPEN1#');
    
    // Start image capture in fast mode (background)
    captureEntryImages(true); // true = fast mode, non-blocking
    
    // Use transaksi store method with current gate location
    const gateId = transaksiStore.lokasiPos.value || '01';
    const success = await transaksiStore.setManualOpenGate(gateId);
    
    if (success) {
      gateStore.writeToPort('entry', "open");
      await updateStatistics();
      
      $q.notify({
        type: 'positive',
        message: 'Gate berhasil dibuka secara manual',
        position: 'top',
        timeout: 2000
      });
    }
  } catch (error) {
    console.error('Error in manual gate open:', error);
    $q.notify({
      type: 'warning',
      message: 'Gate dibuka, tapi gagal menyimpan data transaksi',
      position: 'top',
      timeout: 3000
    });
  }
};

const onClickEmergency = async () => {
  try {
    // Set emergency plate number if not set
    if (!transaksiStore.platNomor) {
      transaksiStore.platNomor = 'EMERGENCY';
    }
    
    // Always open gate first for emergency
    gateStore.writeToPort('entry', ' *OPEN1#');
    
    // Start image capture in fast mode (background)
    captureEntryImages(true); // true = fast mode, non-blocking
    
    // Use transaksi store method with emergency flag
    const gateId = transaksiStore.lokasiPos.value || '01';
    const success = await transaksiStore.setManualOpenGate(gateId);
    
    if (success) {
      componentStore.openGate();
      await updateStatistics();
    }
    
    $q.notify({
      type: 'warning',
      message: 'Gate dibuka dalam mode emergency',
      position: 'top',
      timeout: 3000
    });
    
  } catch (error) {
    console.error('Error in emergency gate open:', error);
    $q.notify({
      type: 'warning',
      message: 'Gate dibuka emergency, tapi gagal menyimpan data',
      position: 'top',
      timeout: 3000
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
    // const loadingNotify = $q.notify({
    //   type: 'ongoing',
    //   message: 'Mengecek status member...',
    //   position: 'center',
    //   timeout: 0,
    //   spinner: true
    // });

    // Cek apakah plat nomor adalah member
    await membershipStore.loadMembers();
    const member = membershipStore.getMemberByPlatOrCard(transaksiStore.platNomor);
    // console.log("🚀 ~ onPressEnterPlatNomor ~ member:", member)
    
    let platNomorToCheck = transaksiStore.platNomor.toUpperCase().trim();
    if(member && member.vehicles && member.vehicles.length > 0) {
      // Jika member memiliki kendaraan, gunakan plat nomor kendaraan pertama
      platNomorToCheck = member.vehicles[0].plate_number || member.vehicles[0].license_plate || platNomorToCheck;
    }
    console.log("🚀 ~ onPressEnterPlatNomor ~ platNomorToCheck:", platNomorToCheck)
    // Cek apakah plat nomor sudah ada di dalam parkiran
    const existingTransactions = await transaksiStore.searchTransactionByPlateNumber(platNomorToCheck);
    console.log("🚀 ~ onPressEnterPlatNomor ~ existingTransactions:", existingTransactions)
    // return
    const activeTransactions = existingTransactions.filter(trx => {
      // trx.status === 0 dan waktu_masuk masih di hari yang sama
      const isActive = trx.waktu_masuk && (new Date(trx.waktu_masuk)).toDateString() === (new Date()).toDateString();
      return isActive;
    });
    if (activeTransactions.length > 0) {
      // loadingNotify();
      const activeTransaction = activeTransactions[0];
      const transactionType = activeTransaction.type === 'member_entry' ? 'Member' : 'Parkir';
      // $q.notify({
      //   type: "warning",
      //   message: `Plat nomor ${platNomorToCheck} sudah ada di dalam parkiran (${transactionType})`,
      //   position: "center",
      //   timeout: 3000,
      // });

      $q.dialog({
        // title: 'Plat Nomor Sudah Ada',
        // message: `Plat nomor <strong>${platNomorToCheck}</strong> sudah ada di dalam parkiran (${transactionType}).`,
        // ok: {
          // label: 'Tutup',
          component:VehicleInsideDialog,
          componentProps: {
            plateNumber: platNomorToCheck,
          },
          // handler: () => {
          //   // Handle OK button click
          // }
        
      }).onOk(async () => {
        console.log("🚀 ~ onPressEnterPlatNomor ~ onOk:")
        // Fokus kembali ke input plat nomor setelah dialog ditutup
        await gateStore.openGate()
        setTimeout(() => {
          inputPlatNomorRef.value?.focus && inputPlatNomorRef.value.focus();
        }, 100);
      });
      return;
    }

    // Jika ditemukan member
    if (member && member.member_id) {
      // console.log("🚀 ~ onPressEnterPlatNomor ~ member:", member)
      // Set data member ke currentMember dan tampilkan dialog
      currentMember.value = member;
      // showMemberDialog.value = true;
      // loadingNotify();
       $q.dialog({
      component: MemberCard,
      componentProps: {
        // plateNumber: transaksiStore.platNomor,
        nama: member.name,
        jenisMember: member.membership_type || 'Umum',
        endDate: member.end_date ? member.end_date : 'Tidak diketahui',
        plateNumber: platNomorToCheck || 'Tidak diketahui'
      },
      // persistent: true,
      transitionShow: 'slide-up',
      transitionHide: 'slide-down',
    }).onOk(() => {
        // console.log("🚀 ~ onPressEnterPlatNomor ~ onOk:")
        // Fokus kembali ke input plat nomor setelah dialog ditutup
        handleMemberCardTap(member);
        setTimeout(() => {
          inputPlatNomorRef.value?.focus && inputPlatNomorRef.value.focus();
        }, 100);
      });
      // Tidak langsung proses entry, tunggu operator klik Enter di dialog
      return;
    }

    // Jika bukan member, proses seperti umum
    // loadingNotify();
    // Proses umum seperti biasa
    // Start image capture in fast mode (non-blocking for speed)
    const capturePromise = captureEntryImages(true);
    // Get customer data in parallel with image capture
    // const customerPromise = transaksiStore.getCustomerByNopol();
    // await customerPromise;
    // const dataCustomer = transaksiStore.dataCustomer;

    if (settingsService.isPrepaidMode) {
      const _jenisKendaraanDialog = $q.dialog({
        component: JenisKendaraanDialog,
        componentProps: {
          isPrepaidMode: true,
          // customerData: dataCustomer
        }
      });
      _jenisKendaraanDialog.onOk(() => {
        console.log("🚀 ~ _jenisKendaraanDialog.onOk ~ onOk:")
        processEntry(true);
      });
    } else if (settingsService.isPostpaidMode) {
      if (!dataCustomer) {
        const _jenisKendaraanDialog = $q.dialog({
          component: JenisKendaraanDialog,
          componentProps: {
            isPrepaidMode: false,
            customerData: null
          }
        });
        _jenisKendaraanDialog.onOk(() => {
          processEntry(false);
        });
      } else {
        const jenis_kendaraan = {
          id: dataCustomer.id_jenis_kendaraan,
          label: dataCustomer.jenis_kendaraan,
        };
        transaksiStore.selectedJenisKendaraan = jenis_kendaraan;
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
          console.log("🚀 ~ _ticketDialog.onOk ~ onOk:")
          processEntry(false);
        });
      }
    }
  } catch (error) {
    console.error('Error processing plate number:', error);
    $q.notify({
      type: 'info',
      message: 'Memproses transaksi...',
      position: 'top',
      timeout: 1500
    });
    try {
      await transaksiStore.getCustomerByNopol();
      const dataCustomer = transaksiStore.dataCustomer;
      if (settingsService.isPrepaidMode) {
        const _jenisKendaraanDialog = $q.dialog({
          component: JenisKendaraanDialog,
          componentProps: {
            isPrepaidMode: true,
            customerData: dataCustomer
          }
        });
        _jenisKendaraanDialog.onOk(() => processEntry(true));
      } else if (settingsService.isPostpaidMode) {
        if (!dataCustomer) {
          const _jenisKendaraanDialog = $q.dialog({
            component: JenisKendaraanDialog,
            componentProps: {
              isPrepaidMode: false,
              customerData: null
            }
          });
          _jenisKendaraanDialog.onOk(() => processEntry(false));
        } else {
          const jenis_kendaraan = {
            id: dataCustomer.id_jenis_kendaraan,
            label: dataCustomer.jenis_kendaraan,
          };
          transaksiStore.selectedJenisKendaraan = jenis_kendaraan;
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
          _ticketDialog.onOk(() => processEntry(false));
        }
      }
    } catch (fallbackError) {
      console.error('Fallback processing also failed:', fallbackError);
      $q.notify({
        type: 'negative',
        message: 'Gagal memproses transaksi',
        position: 'top',
        timeout: 2000
      });
    }
  }
};




// Process entry transaction
const processEntry = async (isPrepaidMode = false) => {
  // Prevent duplicate processing
  if (transaksiStore.isProcessing) {
    return;
  }

  try {
    transaksiStore.isProcessing = true;
    
    await transaksiStore.processEntryTransaction(isPrepaidMode);

    syncSingleDatabase('transactions')
    
    // Update statistics
    await updateStatistics();
    
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
    console.error('❌ Error processing entry:', error);
    $q.notify({
      type: 'negative',
      message: 'Gagal memproses transaksi masuk',
      position: 'top'
    });
  } finally {
    transaksiStore.isProcessing = false;
  }
};

// Update vehicle statistics
const updateStatistics = async () => {
  try {
    await transaksiStore.getCountVehicleInToday();
    await transaksiStore.getCountVehicleOutToday();
    await transaksiStore.getCountVehicleInside();
    
    // Note: Removed componentStore.vehicleOutKey = Date.now(); 
    // as it was causing Camera components to recreate and start new intervals
    
  } catch (error) {
    console.error('Error updating statistics:', error);
  }
};

const logout = async () => {
  try {
    // Use petugas store logout
    petugasStore.logout();
    
    // Also try to logout from user store if needed
    // await userStore().logout();
    
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

const isAdmin = ref(ls.get("isAdmin")) || false;

// Computed properties for sync status indicator
const syncStatusColor = computed(() => {
  if (!isSyncing.value) {
    switch (lastSyncStatus.value) {
      case 'complete':
      case 'paused':
        return 'positive';
      case 'error':
      case 'denied':
        return 'negative';
      case 'active':
        return 'warning';
      default:
        return 'grey';
    }
  }
  return 'warning';
});

const syncStatusTextColor = computed(() => {
  return syncStatusColor.value === 'grey' ? 'black' : 'white';
});

const syncStatusIcon = computed(() => {
  if (isSyncing.value) {
    return 'sync';
  }
  
  switch (lastSyncStatus.value) {
    case 'complete':
      return 'cloud_done';
    case 'paused':
      return 'cloud_queue';
    case 'error':
    case 'denied':
      return 'cloud_off';
    case 'active':
      return 'sync';
    default:
      return 'cloud';
  }
});

const syncStatusLabel = computed(() => {
  if (isSyncing.value) {
    return 'Syncing...';
  }
  
  switch (lastSyncStatus.value) {
    case 'complete':
      return 'Synced';
    case 'paused':
      return 'Paused';
    case 'error':
      return 'Error';
    case 'denied':
      return 'Denied';
    case 'active':
      return 'Active';
    default:
      return 'Unknown';
  }
});

const syncStatusTooltip = computed(() => {
  let status = `Status: ${syncStatusLabel.value}`;
  if (lastSyncError.value) {
    status += `\nError: ${lastSyncError.value.message || lastSyncError.value}`;
  }
  return status;
});

const goToDaftarTransaksi = ()=>{
   if (isAdmin.value) {
        componentStore.currentPage = "daftar-transaksi";
        router.push("/daftar-transaksi");
      } else {
        $q.notify({
          type: "negative",
          message: "Anda tidak memiliki akses",
          position: "bottom",
        });
      }
}

const handleKeyDown = (event) => {
  // console.log(event.key);
  if (componentStore.currentPage == "outgate") {
    if (event.key === "F1") {
      event.preventDefault();
      inputPlatNomorRef.value.focus();
    // } else if (event.key === "F4") {
    //   event.preventDefault();
    //   onClickKendaraanKeluar();
    }else if (event.key === "F3") {
      console.log("🚀 ~ handleKeyDown ~ event.key:", event.key)
      event.preventDefault();
      onClickDashboard();
    } else if (event.key === "F2") {
      event.preventDefault();
      goToDaftarTransaksi()
    // } else if (event.shiftKey === true && event.key === "R") {
    //   event.preventDefault();
    //   onClickKendaraanKeluar();
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
      if (isAdmin.value) {
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
  });

  settingsDialog.update();
  // }
};

const onCameraError = (err) => {
  console.error('Camera error:', err);
  // $q.notify({
  //   type: 'warning',
  //   message: `Kamera tidak tersedia, aplikasi tetap berjalan tanpa gambar`,
  //   position: 'top',
  //   timeout: 2000
  // });
  
  // Set status kamera error tapi aplikasi tetap lanjut
  console.log('⚠️ Camera error handled, application continues without image capture');
};

// Handler untuk hasil capture kamera masuk
const onEntryCaptured = (capturedData) => {
  if (capturedData && capturedData.image) {
    transaksiStore.entry_pic = capturedData.image;
  }
  if (capturedData && capturedData.plateNumber) {
    transaksiStore.platNomor = capturedData.plateNumber.toUpperCase();
  }
};

// Handler untuk capture gambar entry saat entry dengan timeout cepat
const captureEntryImage = async (timeoutMs = 2000) => {
  try {
    console.log('📷 Attempting to capture entry image with timeout:', timeoutMs + 'ms');
    
    // Clear any existing exit image to prevent contamination
    transaksiStore.exit_pic = null;
    console.log('🧹 Cleared exit_pic before entry capture');
    
    // Check if camera ref exists and is available
    if (!entryCameraRef.value) {
      console.warn('⚠️ Entry camera ref not available, continuing without image');
      transaksiStore.entry_pic = null;
      return;
    }
    
    // Race between camera capture and timeout
    const imageData = await Promise.race([
      entryCameraRef.value?.getImage(),
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Camera timeout')), timeoutMs)
      )
    ]);
    
    console.log('📷 Image data received:', {
      imageData: !!imageData,
      type: typeof imageData,
      isBlob: imageData instanceof Blob,
      length: typeof imageData === 'string' ? imageData.length : 'N/A'
    });
    
    if (imageData) {
      let imageBase64;
      if (typeof imageData === 'string') {
        imageBase64 = imageData;
        transaksiStore.entry_pic = imageBase64;
        console.log('✅ String image saved to entry_pic');
      } else if (imageData instanceof Blob) {
        console.log('🔄 Converting Blob to base64...');
        
        // Fast blob to base64 conversion with timeout
        imageBase64 = await Promise.race([
          new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(imageData);
          }),
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Blob conversion timeout')), 1000)
          )
        ]);
        
        transaksiStore.entry_pic = imageBase64;
        console.log('✅ Blob image converted and saved to entry_pic');
        console.log('📊 Debug: entry_pic set to:', transaksiStore.entry_pic ? 'Base64 image data' : 'null');
        console.log('📊 Debug: exit_pic is:', transaksiStore.exit_pic ? 'Base64 image data' : 'null');
      }
    } else {
      console.warn('⚠️ No image data received from camera, continuing without image');
      transaksiStore.entry_pic = null;
      console.log('📊 Debug: entry_pic set to null');
      console.log('📊 Debug: exit_pic is:', transaksiStore.exit_pic ? 'Base64 image data' : 'null');
    }
  } catch (error) {
    console.error('❌ Error capturing entry image:', error.message);
    console.log('📝 Setting entry_pic to null and continuing without image');
    transaksiStore.entry_pic = null;
    console.log('📊 Debug: entry_pic set to null (error case)');
    console.log('📊 Debug: exit_pic is:', transaksiStore.exit_pic ? 'Base64 image data' : 'null');
    
    // Don't throw error, just continue without image
    if (error.message !== 'Camera timeout') {
      // $q.notify({
      //   type: 'info',
      //   message: 'Kamera tidak tersedia, transaksi tetap dilanjutkan',
      //   position: 'top',
      //   timeout: 1500
      // });
    }
  }
};

// Handler untuk capture gambar saat entry dengan optimasi kecepatan
const captureEntryImages = async (fastMode = false) => {
  const timeoutMs = fastMode ? 1000 : 2000; // Faster timeout for quick operations
  
  try {
    console.log('📸 Starting capture entry images (fast mode:', fastMode + ')...');
    
    // Start capture in background - don't wait for it to complete
    const capturePromise = captureEntryImage(timeoutMs);
    
    if (fastMode) {
      // In fast mode, start capture but don't wait for completion
      capturePromise.then(() => {
        console.log('🖼️ Background image capture completed');
        if (transaksiStore.entry_pic) {
          $q.notify({
            type: 'positive',
            message: 'Gambar berhasil diambil',
            position: 'top',
            timeout: 1500
          });
        }
      }).catch(() => {
        console.log('📝 Background image capture failed, continuing without image');
      });
      
      // Return immediately for fast processing
      console.log('⚡ Fast mode: continuing without waiting for image capture');
      return;
    } else {
      // Normal mode: wait for capture with timeout
      await capturePromise;
      
      // Debug: Check if image was captured successfully
      console.log('🖼️ After capture - entry_pic status:', {
        hasEntryPic: !!transaksiStore.entry_pic,
        entryPicLength: transaksiStore.entry_pic?.length || 0,
        entryPicType: typeof transaksiStore.entry_pic
      });
      
      if (transaksiStore.entry_pic) {
        $q.notify({
          type: 'positive',
          message: 'Gambar masuk berhasil diambil',
          position: 'top',
          timeout: 2000
        });
      } else {
        console.warn('⚠️ No entry image captured, continuing without image');
        // $q.notify({
        //   type: 'info',
        //   message: 'Kamera tidak tersedia, transaksi dilanjutkan tanpa gambar',
        //   position: 'top',
        //   timeout: 1500
        // });
      }
    }
  } catch (error) {
    console.error('❌ Error capturing entry image:', error);
    console.log('📝 Continuing without image capture');
    
    // Set entry_pic to null and continue
    transaksiStore.entry_pic = null;
    
    if (!fastMode) {
      // $q.notify({
      //   type: 'info',
      //   message: 'Kamera tidak tersedia, transaksi dilanjutkan tanpa gambar',
      //   position: 'top',
      //   timeout: 1500
      // });
    }
  }
};

// Test function untuk capture gambar manual
const testCaptureImages = async () => {
  try {
    $q.notify({
      type: 'info',
      message: 'Mengambil gambar test dari kamera...',
      position: 'top',
      timeout: 2000
    });

    await captureEntryImages();
    
    // Show captured images info
    const entryImageStatus = transaksiStore.entry_pic ? '✅ Berhasil' : '❌ Gagal';
    
    $q.dialog({
      title: '📸 Test Capture Results',
      message: `
        <div style="text-align: left;">
          <p><strong>🚗 Kamera Masuk:</strong> ${entryImageStatus}</p>
          <br>
          <p><em>Gambar tersimpan sementara di memory. Buat transaksi untuk menyimpan ke database.</em></p>
        </div>
      `,
      html: true,
      ok: {
        label: 'OK',
        color: 'primary'
      }
    });
    
  } catch (error) {
    console.error('❌ Error in test capture:', error);
    $q.notify({
      type: 'negative',
      message: 'Gagal melakukan test capture',
      position: 'top'
    });
  }
};

// Test function untuk koneksi kamera
const testCameraConnection = async () => {
  try {
    $q.notify({
      type: 'info',
      message: 'Testing koneksi kamera...',
      position: 'top',
      timeout: 2000
    });

    // Test plate camera using fetchCameraImage method
    let plateStatus = '❌ Gagal';
    let plateError = '';
    try {
      const plateResult = await entryCameraRef.value?.fetchCameraImage();
      if (plateResult) {
        plateStatus = '✅ Berhasil';
      }
    } catch (error) {
      console.error('Plate camera test failed:', error);
      plateError = error.message || 'Unknown error';
    }

    // Test driver camera using fetchCameraImage method
    let driverStatus = '❌ Gagal';
    let driverError = '';
    try {
      const driverResult = await driverCameraRef.value?.fetchCameraImage();
      if (driverResult) {
        driverStatus = '✅ Berhasil';
      }
    } catch (error) {
      console.error('Driver camera test failed:', error);
      driverError = error.message || 'Unknown error';
    }

    $q.dialog({
      title: '🔗 Test Koneksi Kamera',
      message: `
        <div style="text-align: left;">
          <p><strong>🚗 Kamera Plat Nomor:</strong> ${plateStatus}</p>
          <p><strong>Config:</strong> ${plateCameraCredentials.value.username}@${plateCameraCredentials.value.ip_address}</p>
          <p><strong>RTSP Path:</strong> ${gateSettings.value?.PLATE_CAM_RTSP_PATH || 'Default'}</p>
          ${plateError ? `<p class="text-negative"><small>Error: ${plateError}</small></p>` : ''}
          <br>
          <p><strong>👤 Kamera Driver:</strong> ${driverStatus}</p>
          <p><strong>Config:</strong> ${driverCameraCredentials.value.username}@${driverCameraCredentials.value.ip_address}</p>
          <p><strong>RTSP Path:</strong> ${gateSettings.value?.DRIVER_CAM_RTSP_PATH || 'Default'}</p>
          ${driverError ? `<p class="text-negative"><small>Error: ${driverError}</small></p>` : ''}
          <br>
          <p><small><em>Jika gagal, periksa konfigurasi di Settings (F7)</em></small></p>
        </div>
      `,
      html: true,
      ok: {
        label: 'OK',
        color: 'primary'
      }
    });
    
  } catch (error) {
    console.error('❌ Error testing camera connection:', error);
    $q.notify({
      type: 'negative',
      message: 'Gagal melakukan test koneksi',
      position: 'top'
    });
  }
};

// Function untuk reload konfigurasi kamera
const reloadCameraConfig = async () => {
  try {
    $q.notify({
      type: 'info',
      message: 'Memuat ulang konfigurasi kamera...',
      position: 'top',
      timeout: 2000
    });

    // Reload settings
    await settingsService.initializeSettings();
    
    $q.notify({
      type: 'positive',
      message: 'Konfigurasi kamera berhasil dimuat ulang',
      position: 'top',
      timeout: 2000
    });
    
  } catch (error) {
    console.error('❌ Error reloading camera config:', error);
    $q.notify({
      type: 'negative',
      message: 'Gagal memuat ulang konfigurasi kamera',
      position: 'top'
    });
  }
};

// Test function untuk kartu member
// Test function untuk sinkronisasi database
const testDatabaseSync = async () => {
  try {
    $q.notify({
      type: 'info',
      message: 'Testing sinkronisasi database...',
      position: 'top',
      timeout: 2000
    });

    const { forceSyncAllDatabases, getSyncStatus, checkTransactionInRemote } = await import('src/boot/pouchdb');
    
    // Check current sync status
    const currentStatus = getSyncStatus();
    console.log('📊 Current sync status:', currentStatus);
    
    // Force manual sync
    console.log('🔄 Starting forced sync...');
    await forceSyncAllDatabases();
    
    // Verify recent transactions are synced
    const recentTransactions = transaksiStore.transactionHistory.slice(0, 3);
    console.log('🔍 Checking recent transactions in remote database...');
    
    for (const transaction of recentTransactions) {
      const exists = await checkTransactionInRemote(transaction.id);
      console.log(`Transaction ${transaction.id} in remote:`, exists ? '✅ Found' : '❌ Not found');
    }
    
    $q.notify({
      type: 'positive',
      message: 'Test sinkronisasi selesai, lihat console untuk detail',
      position: 'top',
      });
     
  } catch (error) {
    console.error('❌ Error testing database sync:', error);
  }
};

const testMemberCard = async () => {
  try {
    $q.notify({
      type: 'info',
      message: 'Testing kartu member...',
      position: 'top',
      timeout: 2000
    });

    // Cari member pertama yang ada di database untuk testing
    await membershipStore.loadMembers();
    const firstMember = membershipStore.members[0];
    
    if (!firstMember) {
      $q.notify({
        type: 'warning',
        message: 'Tidak ada data member untuk testing. Pastikan membership store ter-load.',
        position: 'top',
        timeout: 3000
      });
      return;
    }

    const testCardNumber = firstMember.card_number;
    console.log('🧪 Testing member card with number:', testCardNumber);
    console.log('👤 Testing with member:', firstMember.name);
    
    await handleMemberCardTap(testCardNumber);
    
  } catch (error) {
    console.error('❌ Error testing member card:', error);
    $q.notify({
      type: 'negative',
      message: 'Gagal melakukan test kartu member',
      position: 'top'
    });
  }
};

// Initialize serial port with retry mechanism
const initializeSerialPort = async (retryCount = 0) => {
  const maxRetries = 3;
  
  try {
    console.log(`� Initializing serial port (attempt ${retryCount + 1}/${maxRetries + 1})...`);
    
    const portConfig = {
      portName: gateSettings.value?.SERIAL_PORT || "COM1",
      type: 'entry'
    };
    console.log("🚀 ~ initializeSerialPort ~ portConfig.gateSettings.value?.SERIAL_PORT:", gateSettings)
    console.log("🚀 ~ initializeSerialPort ~ gateSettings.SERIAL_PORT :", gateSettings.value?.SERIAL_PORT)
    
    await gateStore.initializeSerialPort(portConfig);
    
    serialPortStatus.value = {
      ready: true,
      initialized: true,
      error: null
    };
    
    console.log('✅ Serial port initialized successfully');
    
    $q.notify({
      type: 'positive',
      message: 'Serial port siap',
      position: 'top',
      timeout: 2000,
      icon: 'usb'
    });
    
  } catch (error) {
    console.error(`❌ Failed to initialize serial port (attempt ${retryCount + 1}):`, error);
    
    serialPortStatus.value = {
      ready: false,
      initialized: false,
      error: error.message
    };
    
    // Retry if not max attempts
    if (retryCount < maxRetries) {
      console.log(`🔄 Retrying serial port initialization in 2 seconds...`);
      setTimeout(() => initializeSerialPort(retryCount + 1), 2000);
    } else {
      $q.notify({
        type: 'warning',
        message: `Serial port gagal inisialisasi: ${error.message}`,
        position: 'top',
        timeout: 5000
      });
    }
  }
};

// Initialize membership store with proper error handling
const initializeMembershipStore = async (retryCount = 0) => {
  const maxRetries = 3;
  
  try {
    console.log(`👥 Initializing membership store (attempt ${retryCount + 1}/${maxRetries + 1})...`);
    
    await membershipStore.initializeStore();
    await membershipStore.loadMembers();
    
    membershipStoreStatus.value = {
      ready: true,
      membersLoaded: membershipStore.members.length > 0,
      error: null
    };
    
    console.log('✅ Membership store initialized with', membershipStore.members.length, 'members');
    
    // Now safe to initialize card reader
    await initializeCardReader();
    
  } catch (error) {
    console.error(`❌ Failed to initialize membership store (attempt ${retryCount + 1}):`, error);
    
    membershipStoreStatus.value = {
      ready: false,
      membersLoaded: false,
      error: error.message
    };
    
    // Retry if not max attempts
    if (retryCount < maxRetries) {
      console.log(`🔄 Retrying membership store initialization in 2 seconds...`);
      setTimeout(() => initializeMembershipStore(retryCount + 1), 2000);
    } else {
      $q.notify({
        type: 'negative',
        message: `Membership store gagal inisialisasi: ${error.message}`,
        position: 'top',
        timeout: 5000
      });
    }
  }
};

onMounted(async () => {
  console.log('🚀 Component mounting started...');
  
  // Set current page first
  componentStore.currentPage = "outgate";
  console.log('✅ Current page set to outgate');
  
  // Initialize settings service first
  try {
    if (!settingsService.activeGateId) {
      await settingsService.initializeSettings();
    }
    console.log('✅ Settings service initialized');
  } catch (error) {
    console.error('❌ Failed to initialize settings service:', error);
  }

  // Initialize petugas store
  try {
    await petugasStore.loadFromLocal();
    if (petugasStore.daftarPetugas.length === 0) {
      await petugasStore.seedPetugasData();
    }
    console.log('✅ Petugas store initialized');
  } catch (error) {
    console.error('❌ Error initializing petugas store:', error);
  }

  // Initialize serial port (non-blocking)
  initializeSerialPort();

  // Initialize membership store and card reader (critical for card functionality)
  initializeMembershipStore();

  // Debug: Check if gateSettings are loaded correctly
  console.log('🎥 Camera configuration loaded:', {
    gateSettings: !!gateSettings.value,
    plateCameraMode: gateSettings.value?.PLATE_CAM_MODE,
    driverCameraMode: gateSettings.value?.DRIVER_CAM_MODE,
    plateCameraType: plateCameraType.value,
    driverCameraType: driverCameraType.value,
    plateCameraIP: gateSettings.value?.PLATE_CAM_IP,
    driverCameraIP: gateSettings.value?.DRIVER_CAM_IP,
    plateCameraDeviceID: gateSettings.value?.PLATE_CAM_DEVICE_ID,
    driverCameraDeviceID: gateSettings.value?.DRIVER_CAM_DEVICE_ID
  });

  // Check camera configuration and show notification if needed
  const missingCameraConfigs = [];
  if (!gateSettings.value?.PLATE_CAM_IP && !gateSettings.value?.PLATE_CAM_DEVICE_ID) {
    missingCameraConfigs.push('Kamera Plat Nomor');
  }
  if (!gateSettings.value?.DRIVER_CAM_IP && !gateSettings.value?.DRIVER_CAM_DEVICE_ID) {
    missingCameraConfigs.push('Kamera Driver');
  }

  if (missingCameraConfigs.length > 0) {
    $q.notify({
      type: 'warning',
      message: `${missingCameraConfigs.join(' dan ')} belum dikonfigurasi. Silakan buka Settings (F7) untuk mengatur CCTV.`,
      position: 'top',
      timeout: 5000,
      actions: [
        { 
          label: 'Buka Settings', 
          color: 'white',
          handler: () => {
            if (isAdmin.value) {
              onClickSettings();
            }
          }
        }
      ]
    });
  }

  // Dark mode is already initialized before onMounted
  // Just ensure it's applied correctly
  // $q.dark.set(darkMode.value);
  
  // // Watch for dark mode changes
  // watch(darkMode, (newValue) => {
  //   $q.dark.set(newValue);
  //   ls.set("darkMode", newValue);
  //   console.log('🌙 Dark mode watcher triggered:', newValue);
  // }, { immediate: false }); // Don't trigger immediately since already initialized

  // Watch for camera configuration changes
  watch([plateCameraCredentials, driverCameraCredentials], ([newPlateCredentials, newDriverCredentials], [oldPlateCredentials, oldDriverCredentials]) => {
    if (oldPlateCredentials && oldDriverCredentials) { // Only run after initial load
      // Optionally show notification when camera config changes
      const hasPlateConfig = newPlateCredentials.ip_address && newPlateCredentials.ip_address !== '192.168.10.25';
      const hasDriverConfig = newDriverCredentials.ip_address && newDriverCredentials.ip_address !== '192.168.10.26';
      
      if (hasPlateConfig && hasDriverConfig) {
        $q.notify({
          type: 'positive',
          message: 'Konfigurasi CCTV berhasil dimuat',
          position: 'top',
          timeout: 2000
        });
      }
    }
  }, { deep: true });

  // Watch for camera type changes
  watch([plateCameraType, driverCameraType], ([newPlateType, newDriverType], [oldPlateType, oldDriverType]) => {
    if (oldPlateType && oldDriverType) { // Only run after initial load
      console.log('🎥 Camera types changed:', {
        plateCamera: `${oldPlateType} → ${newPlateType}`,
        driverCamera: `${oldDriverType} → ${newDriverType}`,
        plateCameraMode: gateSettings.value?.PLATE_CAM_MODE,
        driverCameraMode: gateSettings.value?.DRIVER_CAM_MODE
      });
      
      $q.notify({
        type: 'info',
        message: `Kamera diperbarui: Plat=${newPlateType.toUpperCase()}, Driver=${newDriverType.toUpperCase()}`,
        position: 'top',
        timeout: 3000
      });
    }
  });

  // Watch for selectedJenisKendaraan changes to auto-process entry
  watch(
    () => transaksiStore.selectedJenisKendaraan,
    async (newValue, oldValue) => {
      // Only process if we have a new selection and we're not already checked in
      if (newValue && !transaksiStore.isCheckedIn && transaksiStore.platNomor) {
        // Use the current operation mode from settings
        // const isPrepaidMode = settingsService.isPrepaidMode;
        // await processEntry(isPrepaidMode);
      }
    }
  );
  
  // Initialize statistics using transaksi store
  try {
    await updateStatistics();
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
  
  console.log('✅ Component mounting completed');
});


// Tambahkan function setelah testSyncConnectivity_

const testLiveSync = async () => {
  console.log('🧪 Testing live sync functionality...');
  
  $q.notify({
    type: 'info',
    message: 'Testing live sync, tunggu 30 detik...',
    position: 'top',
    timeout: 2000
  });
  
  try {
    const { activeSyncHandlers, syncSingleDatabase } = await import('src/boot/pouchdb');
    
    // Check active sync handlers
    const activeCount = activeSyncHandlers.size;
    const expectedCount = Object.keys(await import('src/boot/pouchdb').then(m => m.localDbs)).length;
    
    console.log(`📊 Active sync handlers: ${activeCount}/${expectedCount}`);
    
    if (activeCount < expectedCount) {
      console.warn('⚠️ Some sync handlers missing, restarting...');
      
      // Restart missing handlers
      const { localDbs } = await import('src/boot/pouchdb');
      Object.keys(localDbs).forEach(dbName => {
        if (!activeSyncHandlers.has(dbName)) {
          console.log(`🔄 Restarting sync for ${dbName}...`);
          syncSingleDatabase(dbName);
        }
      });
    }
    
    // Create test transaction untuk test live sync
    const testTransaction = {
      _id: `test-live-sync-${Date.now()}`,
      type: 'parking_transaction', 
      test_data: true,
      created_at: new Date().toISOString(),
      status: 0
    };
    
    console.log('🧪 Creating test transaction for live sync test...');
    const { addTransaction } = await import('src/boot/pouchdb');
    await addTransaction(testTransaction, false); // No immediate sync
    
    console.log('✅ Test transaction created, live sync should handle it automatically');
    console.log('⏰ Wait 30 seconds and check CouchDB admin panel for the test transaction');
    
    $q.notify({
      type: 'positive',
      message: 'Live sync test started - cek console dan CouchDB panel',
      position: 'top',
      timeout: 5000
    });
    
  } catch (error) {
    console.error('❌ Live sync test failed:', error);
    
    $q.notify({
      type: 'negative',
      message: `Live sync test error: ${error.message}`,
      position: 'top',
      timeout: 5000
    });
  }
};

// Function untuk restart sync initialization
const restartSyncInitialization = async () => {
  console.log('🔄 Starting sync initialization restart...');
  
  try {
    $q.notify({
      type: 'info',
      message: 'Restarting sync initialization...',
      position: 'top',
      timeout: 3000
    });
    
    const { restartSyncInitialization: restartSync } = await import('src/boot/pouchdb');
    await restartSync();
    
    console.log('✅ Sync initialization restarted successfully');
    
    $q.notify({
      type: 'positive',
      message: 'Sync initialization restarted successfully!',
      position: 'top',
      timeout: 5000
    });
    
  } catch (error) {
    console.error('❌ Restart sync initialization failed:', error);
    
    $q.notify({
      type: 'negative',
      message: `Restart sync failed: ${error.message}`,
      position: 'top',
      timeout: 5000
    });
  }
};

onUnmounted(() => {
  console.log('🧹 Cleaning up component...');
  
  // Clean up card reader
  cardReaderStatus.value = {
    ready: false,
    initialized: false,
    error: null
  };
  
  try {
    emitter.off('card-read');
    window.removeEventListener('keydown', cardReaderKeydownHandler, true);
    console.log('✅ Card reader listeners cleaned up');
  } catch (error) {
    console.log('⚠️ Card reader cleanup had issues (may not have been initialized)');
  }
  
  // Reset card buffer
  resetCardBuffer();
  
  // Clean up camera intervals
  if (entryCameraRef.value) {
    entryCameraRef.value.stopInterval?.();
  }
  
  if (exitCameraRef.value) {
    exitCameraRef.value.stopInterval?.();
  }
  
  // Clean up statistics interval
  if (componentStore.statsInterval) {
    clearInterval(componentStore.statsInterval);
    componentStore.statsInterval = null;
  }
  
  // Remove main event listener
  window.removeEventListener("keydown", handleKeyDown);
  
  // Reset transaction state when leaving page
  transaksiStore.resetTransactionState();
  
  console.log('✅ Component cleanup completed');
});

// Function untuk menampilkan status sistem
const showSystemStatus = () => {
  const syncStatus = getSyncStatus();
  const status = {
    darkMode: darkMode.value,
    cardReader: cardReaderStatus.value,
    serialPort: serialPortStatus.value,
    membershipStore: {
      ...membershipStoreStatus.value,
      totalMembers: membershipStore.members.length
    },
    currentPage: componentStore.currentPage,
    gateSettings: !!gateSettings.value,
    cameraConfig: {
      plateCamera: !!plateCameraCredentials.value.ip_address,
      driverCamera: !!driverCameraCredentials.value.ip_address,
      plateCameraType: plateCameraType.value,
      driverCameraType: driverCameraType.value,
      plateCameraMode: gateSettings.value?.PLATE_CAM_MODE || 'Not Set',
      driverCameraMode: gateSettings.value?.DRIVER_CAM_MODE || 'Not Set'
    },
    sync: syncStatus
  };

  $q.dialog({
    title: '🔍 System Status',
    message: `
      <div style="text-align: left; font-family: monospace; font-size: 12px;">
        <h6>☁️ Database Sync Status</h6>
        <p>Is Syncing: ${status.sync.isSyncing ? '🔄 Yes' : '✅ No'}</p>
        <p>Last Status: ${status.sync.lastSyncStatus}</p>
        <p>Last Error: ${status.sync.lastSyncError?.message || 'None'}</p>
        
        <h6>🌙 Dark Mode</h6>
        <p>Status: ${status.darkMode ? '✅ Dark' : '☀️ Light'}</p>
        
        <h6>💳 Card Reader</h6>
        <p>Ready: ${status.cardReader.ready ? '✅' : '❌'}</p>
        <p>Initialized: ${status.cardReader.initialized ? '✅' : '❌'}</p>
        <p>Error: ${status.cardReader.error || 'None'}</p>
        
        <h6>🔌 Serial Port</h6>
        <p>Ready: ${status.serialPort.ready ? '✅' : '❌'}</p>
        <p>Initialized: ${status.serialPort.initialized ? '✅' : '❌'}</p>
        <p>Error: ${status.serialPort.error || 'None'}</p>
        
        <h6>👥 Membership Store</h6>
        <p>Ready: ${status.membershipStore.ready ? '✅' : '❌'}</p>
        <p>Members Loaded: ${status.membershipStore.membersLoaded ? '✅' : '❌'}</p>
        <p>Total Members: ${status.membershipStore.totalMembers}</p>
        <p>Error: ${status.membershipStore.error || 'None'}</p>
        
        <h6>🏢 General</h6>
        <p>Current Page: ${status.currentPage}</p>
        <p>Gate Settings: ${status.gateSettings ? '✅' : '❌'}</p>
        
        <h6>📷 Camera Configuration</h6>
        <p>Plate Camera IP: ${status.cameraConfig.plateCamera ? '✅' : '❌'}</p>
        <p>Driver Camera IP: ${status.cameraConfig.driverCamera ? '✅' : '❌'}</p>
        <p><strong>Plate Camera Mode:</strong> ${status.cameraConfig.plateCameraMode} → ${status.cameraConfig.plateCameraType}</p>
        <p><strong>Driver Camera Mode:</strong> ${status.cameraConfig.driverCameraMode} → ${status.cameraConfig.driverCameraType}</p>
      </div>
    `,
    html: true,
    ok: {
      label: 'Close',
      color: 'primary'
    },
    cancel: {
      label: 'Test Sync',
      color: 'positive',
      handler: () => {
        testManualSync();
      }
    }
  });
};

// Test manual sync dengan connection check
const testManualSync = async () => {
  try {
    const loadingNotify = $q.notify({
      type: 'ongoing',
      message: 'Mengecek koneksi dan memulai sync manual...',
      position: 'top',
      timeout: 0,
      spinner: true
    });

    // Check remote connection first
    const isConnected = await checkRemoteConnection();
    if (!isConnected) {
      loadingNotify();
      $q.notify({
        type: 'negative',
        message: 'Tidak dapat terhubung ke server database',
        position: 'top',
        timeout: 5000,
        icon: 'cloud_off'
      });
      return;
    }

    // Update loading message
    loadingNotify({
      type: 'ongoing',
      message: 'Koneksi berhasil, melakukan sync...',
      position: 'top',
      timeout: 0,
      spinner: true
    });

    await forceSyncAllDatabases();
    
    loadingNotify();
    $q.notify({
      type: 'positive',
      message: 'Sync manual berhasil diselesaikan',
      position: 'top',
      timeout: 3000,
      icon: 'cloud_done'
    });
  } catch (error) {
    console.error('❌ Manual sync error:', error);
    $q.notify({
      type: 'negative',
      message: `Error sync manual: ${error.message || error}`,
      position: 'top',
      timeout: 5000,
      icon: 'error'
    });
  }
};

// Test transaction verification
const testTransactionVerification = async () => {
  try {
    // Get the latest transaction ID from store
    if (!transaksiStore.currentTransaction?.id) {
      $q.notify({
        type: 'warning',
        message: 'Tidak ada transaksi aktif untuk diverifikasi',
        position: 'top'
      });
      return;
    }

    const transactionId = `transaction_${transaksiStore.currentTransaction.id}`;
    
    const loadingNotify = $q.notify({
      type: 'ongoing',
      message: 'Memverifikasi transaksi di server...',
      position: 'top',
      timeout: 0,
      spinner: true
    });

    const exists = await forceSyncAndVerifyTransaction(transactionId);
    
    loadingNotify();
    
    if (exists) {
      $q.notify({
        type: 'positive',
        message: 'Transaksi berhasil disinkronisasi ke server',
        position: 'top',
        timeout: 3000,
        icon: 'cloud_done'
      });
    } else {
      $q.notify({
        type: 'negative',
        message: 'Transaksi tidak ditemukan di server setelah sync',
        position: 'top',
        timeout: 5000,
        icon: 'cloud_off'
      });
    }
  } catch (error) {
    console.error('Transaction verification failed:', error);
    $q.notify({
      type: 'negative',
      message: 'Verifikasi transaksi gagal: ' + (error.message || error),
      position: 'top',
      timeout: 5000
    });
  }
};

// ...existing functions...
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

/* Light mode input styling */
:deep(.input-box .q-field__native) {
  font-weight: bold !important;
  letter-spacing: 2px;
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

</style>