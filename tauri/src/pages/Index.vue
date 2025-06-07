<template>
  <q-banner
    v-if="globalSettings?.isLicenseExpired === true"
    class="full-width fixed-center z-top q-mt-xl bg-red-6"
    style="height: 60vh"
  >
    <q-item class="q-pa-md">
      <q-item-section avatar>
        <q-icon
          name="warning"
          size="xl"
          color="white"
          style="width: 20vw; transform: scale(1.7)"
        />
      </q-item-section>
      <q-item-section>
        <q-item-label class="text-h3 text-white text-weight-bolder">
          Lisensi Berakhir
        </q-item-label>
        <q-item-label caption>
          <span class="text-h4 text-white text-weight-bolder">
            Silahkan hubungi vendor
          </span>
        </q-item-label>
      </q-item-section>
    </q-item>
  </q-banner>
  <q-page v-else class="column flex flex-center">
    <!-- <template v-slot:action>
        <q-btn flat color="{3:white}" label="{4:Dismiss}" />
        <q-btn flat color="{5:white}" label="{6:Update Credit Card}" />
      </template> -->
    <Logo />
    <div class="q-gutter-md">
      <q-btn
        push
        style="width: 300px; height: 100px"
        color="primary"
        icon="dashboard"
        label="DASHBOARD"
        @click="$router.push({ name: 'dashboard' })"
      >
        <q-btn
          push
          class="q-ma-md"
          color="white"
          text-color="primary"
          label="shift + g"
        />
      </q-btn>
      <q-btn
        push
        style="width: 300px; height: 100px"
        color="primary"
        icon="directions_car"
        label="Post Masuk"
        @click="onClickEntryGate()"
      >
        <q-btn
          push
          class="q-ma-md"
          color="white"
          text-color="primary"
          label="shift + i"
        />
      </q-btn>
      <q-btn
        push
        style="width: 300px; height: 100px"
        color="primary"
        icon="card_membership"
        label="Membership"
        @click="$router.push({ path: '/membership-management' })"
      >
        <q-btn
          push
          class="q-ma-md"
          color="white"
          text-color="primary"
          label="shift + m" 
        />
      </q-btn>
    
      <!-- icon="directions_car" -->
      <q-btn
        push
        style="width: 300px; height: 100px"
        color="primary"
        icon="directions_car"
        label="Post Keluar"
        @click="onClickExitGate()"
      >
        <q-btn
          push
          class="q-ma-md"
          color="white"
          text-color="primary"
          label="shift + O"
        />
      </q-btn>
      <q-btn
        push
        style="width: 300px; height: 100px"
        color="primary"
        icon="settings"
        label="Settings"
        @click="onClickSettings()"
      >
        <q-btn
          push
          class="q-ma-md"
          color="white"
          text-color="primary"
          label="shift + S"
        />
      </q-btn>
      <!-- @click="$router.push('/outgate')" -->
    </div>
  </q-page>
</template>

<script setup>
import { defineComponent, onBeforeMount, onMounted } from "vue";
import LoginDialog from "src/components/LoginDialog.vue";
import ApiUrlDialog from "src/components/ApiUrlDialog.vue";
import Logo from "src/components/Logo.vue";

import SettingsDialog from "src/components/SettingsDialog.vue";
import { useTransaksiStore } from "src/stores/transaksi-store";
import { useQuasar } from "quasar";
import { useSettingsService } from "src/stores/settings-service"; // Diubah
// import { onBeforeRouteLeave, onBeforeRouteEnter } from "vue-router";
import ls from "localstorage-slim";
import { useRouter } from "vue-router";
import { useGateStore } from "src/stores/gate-store";

const $q = useQuasar();
const router = useRouter();
const gateStore = useGateStore();
const isManlessMode = ls.get("manlessMode") || true;

const transaksiStore = useTransaksiStore();
const { globalSettings, gateSettings, loadGateSettings } = useSettingsService(); // Diubah

const onClickDemoPage = () => {


  // if (ls.get("lokasiPos") === null) {
  //   $q.notify({
  //     type: "negative",
  //     message: "Silahkan Isi Lokasi POS terlebih dahulu di menu Settings",
  //     position: "top",
  //     timeout: 3000,
  //   });
  //   return;
  // } else {
    // const dialog = $q.dialog({
    //   component: LoginDialog,
    //   noBackdropDismiss: true,
    //   persistent: true,
    //   componentProps: {
    //     type: "login",
    //     url: "/outgate",
    //   },
    // });
    // dialog.update();
  // }
};

const onClickEntryGate = () => {
  console.log("🚀 ~ onClickEntryGate ~ gateSettings.value?.gateType:", gateSettings.gateType)
  if (gateSettings.gateType.toLowerCase() === 'entry') { // Diubah
    router.push({ path: "/entry-gate" });
  } else {
    $q.notify({
      type: "warning",
      message: "Mode gerbang saat ini bukan 'Entry'. Silakan ubah di pengaturan.",
      position: "top",
    });
  }
};

const onClickExitGate = () => {
  console.log("🚀 ~ onClickExitGate ~ gateSettings.value?.gateType:", gateSettings.gateType)
  if (gateSettings.gateType.toLowerCase() === 'exit') { // Diubah
    router.push({ path: "/exit-gate" });
  } else {
    $q.notify({
      type: "warning",
      message: "Mode gerbang saat ini bukan 'Exit'. Silakan ubah di pengaturan.",
      position: "top",
    });
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

const handleKeyDown = (event) => {
  if (event.shiftKey && event.key === "O") {
    event.preventDefault();
    onClickDemoPage();
  } else if (event.shiftKey === true && event.key === "S") {
    event.preventDefault();
    onClickSettings();
  }
};

onMounted(async () => {
  // Clear any gate-related states when entering home page
  ls.remove('gateMode');
  
  // Reset gate store states
  gateStore.loop1 = false;
  gateStore.loop2 = false;
  gateStore.loop3 = false;
  gateStore.detectedPlates = [];
  
  // console.log(transaksiStore.API_URL);
  // console.log(`🚀 ~ onMounted ~ gateSettings.value?.gateType:`, gateSettings.value?.gateType) // Diubah
  // Navigasi otomatis berdasarkan gateType dari settingsStore akan dihapus dari sini
  // karena pengguna harus secara eksplisit memilih gerbang dari halaman Index.
  // Jika ingin navigasi otomatis, logika berikut bisa diaktifkan kembali:
  // if (gateSettings.value?.gateType === "entry") { // Diubah
  //    router.push({ path: "/entry-gate" });
  // } else if(gateSettings.value?.gateType === "exit") { // Diubah
  //    router.push({ path: "/exit-gate" });
  // }

  loadGateSettings()

  // if (ls.get('WS_URL') === null && ls.get('API_URL') === null) {
  //   const dialog = $q.dialog({
  //     component: ApiUrlDialog,
  //     noBackdropDismiss: true,
  //   });

  //   dialog.update();
  //   $q.notify({
  //     type: "negative",
  //     message: "Silahkan Isi URL API terlebih dahulu",
  //     position: "top",
  //   });
  // } else {
    // await loadAllSettings(); // Diubah

    // if (globalSettings.value?.isLicenseExpired === false) { // Diubah
    //   window.addEventListener("keydown", handleKeyDown);
    // }

   
  // }
});

// onBeforeRouteLeave(() => {
//   window.removeEventListener("keydown", handleKeyDown);
// });

// Router guard to ensure proper cleanup when entering Index page
// onBeforeRouteEnter((to, from, next) => {
//   // Clear gate mode when entering home page
//   if (from.path === '/entry-gate' || from.path === '/exit-gate') {
//     ls.remove('gateMode');
//     ls.remove('manlessMode');
//   }
//   next();
// });

defineComponent({
  name: "IndexPage",
});
</script>
