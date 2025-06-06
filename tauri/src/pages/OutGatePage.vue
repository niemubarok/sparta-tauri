<template>

  <div v-if="manlessMode">
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
    class="relative fixed-top full-height full-width"
    :class="darkMode ? 'bg-primary' : 'bg-grey-5'"
  >
    <div
      v-if="!transaksiStore.isCheckedIn"
      class="flex row justify-between items-center q-pl-lg no-wrap q-pt-md"
      style="height: 150px"
    >
      <q-card class="row items-center bg-grey-2">
        <q-img
          v-if="$q.screen.gt.sm"
          src="~assets/logo.png"
          spinner-color="primary"
          fit="fill"
          class="q-ml-sm rounded-corner"
          width="150px"
          height="150px"
          style="transform: scale(1.5)"
        />

        <CompanyName />
      </q-card>

      <div class="content-end q-pr-md">
        <div class="flex row no-wrap justify-end">
          <ShinyCard
            class="bg-indigo-10"
            title="Kendaraan Masuk"
            :jumlah="transaksiStore.vehicleInToday"
          />
          <!-- shortkey="F3" -->
          <ShinyCard
            :key="componentStore.vehicleOutKey"
            class="bg-teal-10 q-mx-md"
            title="Kendaraan Keluar"
            shortkey="F4"
            :jumlah="transaksiStore.totalVehicleOut"
          />
          <ShinyCard
            class="bg-deep-orange-10"
            title="Kendaraan Parkir"
            :jumlah="transaksiStore.totalVehicleInside"
          />
          <!-- shortkey="F5" -->
        </div>
      </div>
    </div>
    <div
      class="window-width text-dark text-weight-bolder flex row q-pr-lg q-col-gutter-sm z-top"
      :class="
        transaksiStore.isCheckedIn
          ? 'justify-start q-mt-md q-ml-md '
          : 'justify-end'
      "
    >
      <q-chip class="bg-transparent" icon="account_circle" :label="pegawai" />

      <q-chip
        class="bg-transparent"
        icon="work_history"
        :label="ls.get('shift')"
      />
      <q-chip
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

    <div
      v-if="$q.screen.gt.sm && !transaksiStore.isCheckedIn"
      class="full-width q-pt-md"
    >
      <!-- <Quotes /> -->
    </div>

    <!-- KAMERA -->
    <div class="row justify-center items-center">
      <div>
        <div
          v-if="!transaksiStore.isCheckedIn"
          ref="cardVideo"
          class="flex row justify-between content-center items-center q-px-sm relative bg-transparent"
          style="width: 100vw; max-height: 62vh"
        >
          <div class="col-6 relative">
            <q-chip
              class="absolute bg-transparent"
              icon="camera"
              label="Kamera Pintu Masuk"
            />
            <!-- <q-skeleton
              v-if="cameraInUrl == null || cameraInUrl == '-'"
              height="52vh"
              class="rounded-corner"
              width="49vw"
            /> -->
            <Camera
              :key="componentStore.cameraInKey"
              class="rounded-corner"
              camera-location="in"
              :camera-url="gateSettings?.PLATE_CAM_URL"
              :file-name="cameraInFileName"
              :style="{
                width: '49vw',
              }"
            />
            <!-- height: '62vh', -->
          </div>
          <div class="col-6 relative">
            <q-chip
              class="absolute bg-transparent"
              icon="camera"
              label="Kamera Pintu Keluar"
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
              class="rounded-corner"
              camera-location="out"
              :camera-url="gateSettings?.DRIVER_CAM_URL"
              :file-name="cameraOutFileName"
              :style="{
                width: '49vw',
              }"
            />
            <!-- :style="$q.screen.lt.md ? 'width: 49vw' : 'height: 52vh'" -->
          </div>
        </div>
      </div>
    </div>

    <div
      class="flex row justify-center fixed full-width no-wrap z-max"
      style="bottom: 20px"
    >
      <div class="col-8">
        <q-input
          v-show="
            !componentStore.hideInputPlatNomor && !transaksiStore.isCheckedIn
          "
          class="input-box rounded-corner relative text-uppercase q-pa-md q-mb-xl"
          :class="darkMode ? 'bg-grey-3 text-dark' : 'bg-secondary  text-white'"
          :input-class="
            darkMode
              ? 'input-box  text-dark text-weight-bolder'
              : 'input-box text-white text-weight-bolder'
          "
          input-style="height:10vh;border:0"
          :label-color="
            darkMode ? 'secondary text-h4 q-pb-xl' : 'yellow text-h4 q-pb-xl'
          "
          :color="darkMode ? 'bg-yellow' : 'bg-secondary '"
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
              class="text-weight-bold q-mt-md"
              :class="darkMode ? 'bg-dark text-white' : 'bg-grey-3 text-dark'"
            />
          </template>

          <template v-slot:append>
            <q-btn
              push
              :size="'xl'"
              class="q-mt-md q-mr-md"
              :class="darkMode ? 'bg-dark text-white' : 'bg-grey-3 text-dark'"
              icon="keyboard_return"
              @click="onPressEnterPlatNomor()"
            />
          </template>
        </q-input>
      </div>
      <div
        class="full-width fixed-bottom-right bg-dark q-pa-sm row justify-between"
      >
        <!-- v-if="componentStore.currentPage == 'outgate'"-->
        <div>
          <span class="text-weight-bolder text-grey-5">
            .::PINTU KELUAR::.</span
          >
        </div>
        <div class="q-gutter-sm">
          <q-btn color="grey-8" size="sm" label="Dashboard">
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
            @click="onClickBukaManual()"
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
        </div>

        <!-- <q-toggle
        v-model="darkMode"
        @update:model-value="darkModeToggle"
        color="green"
      /> -->
      </div>
    </div>
    <PaymentCard v-if="transaksiStore.isCheckedIn" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, onUpdated } from "vue";
import { useRouter } from "vue-router";
import { useQuasar } from "quasar";
import { useTransaksiStore } from "src/stores/transaksi-store";
import { useComponentStore } from "src/stores/component-store";
import { useSettingsService } from "src/stores/settings-service";
import { userStore } from "src/stores/user-store";
import LoginDialog from "src/components/LoginDialog.vue";
import ApiUrlDialog from "src/components/ApiUrlDialog.vue";
import { getTime, checkSubscriptionExpiration } from "src/utils/time-util";
import ls from "localstorage-slim";

//Components
import Clock from "../components/Clock.vue";
import PaymentCard from "src/components/PaymentCard.vue";
import Quotes from "src/components/Quotes.vue";
import ShinyCard from "src/components/ShinyCard.vue";
import CaemeraOut from "src/components/CameraOut.vue";
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
const { gateSettings, loadGateSettings } = settingsService;
const $q = useQuasar();

const manlessMode = ref(ls.get("manlessMode") || false);

const darkMode = ref(ls.get("darkMode")) || ref(false);
const darkModeToggle = () => {
  ls.set("darkMode", darkMode.value);
};

const cardVideo = ref(null);
const pegawai = ls.get("pegawai") ? ls.get("pegawai").nama : null;

// const cameraInUrl = ls.get("cameraInUrl") || null;
// const cameraOutUrl = ls.get("cameraOutUrl") || null;
const cameraInFileName = `${ls.get("lokasiPos")?.value}_in_snapshot`;
const cameraOutFileName = "02_out_snapshot";

const cameraOut = ls.get("cameraOut") || null;
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
  // persistent: true,

  dialog.update();
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
  const videoRef = cameraOutRef.value?.$refs.videoRef;
  // transaksiStore.waktuMasuk = waktuMasuk.value;

  if (videoRef !== undefined) {
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    context.drawImage(videoRef, 0, 0, canvas.width, canvas.height);

    const imageBase64 = canvas.toDataURL("image/png");

    transaksiStore.pic_body_keluar = imageBase64;
    // console.log(transaksiStore.pic_body_keluar);
  }
  await transaksiStore.setManualOpenGate();
  componentStore.openGate();
};
const onClickEmergency = async () => {
  const videoRef = cameraOutRef.value?.$refs.videoRef;
  // transaksiStore.waktuMasuk = waktuMasuk.value;

  if (videoRef !== undefined) {
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    context.drawImage(videoRef, 0, 0, canvas.width, canvas.height);

    const imageBase64 = canvas.toDataURL("image/png");

    transaksiStore.pic_body_keluar = imageBase64;
    // console.log(transaksiStore.pic_body_keluar);
  }
  await transaksiStore.setManualOpenGate();
  componentStore.openGate();
};

const onPressEnterPlatNomor = async () => {
  if (transaksiStore.platNomor.length < 4) {
    $q.notify({
      type: "negative",
      message: "Cek kembali plat nomor yang anda input",
      position: "bottom",
      timeout: 500,
    });
  } else {
    await transaksiStore.getCustomerByNopol();
    const dataCustomer = ref(transaksiStore.dataCustomer);

    // checkSubscriptionExpiration();
    if (dataCustomer.value == "") {
      const _jenisKendaraanDialog = $q.dialog({
        component: JenisKendaraanDialog,
        noBackdropDismiss: true,
        persistent: true,
      });

      _jenisKendaraanDialog.update();
    } else {
      const jenis_kendaraan = {
        id: dataCustomer.value?.id_jenis_kendaraan,
        label: dataCustomer.value?.jenis_kendaraan,
      };
      transaksiStore.selectedJenisKendaraan = jenis_kendaraan;
      const expiration = checkSubscriptionExpiration(dataCustomer.value?.akhir);
      console.log(transaksiStore.isMemberExpired);
      const _ticketDialog = $q.dialog({
        component: TicketDialog,
        // noBackdropDismiss: true,
        // persistent: true,
        componentProps: {
          title: jenis_kendaraan?.label,
          nama: dataCustomer.value?.nama,
          alamat: dataCustomer.value?.alamat,
          expiration: expiration,
        },
      });

      _ticketDialog.update();
      // componentStore.hideInputPlatNomor = true;
    }
  }
};

const logout = async () => {
  await userStore().logout();
  ls.remove("pegawai");
  ls.remove("shift");
  ls.remove("timeLogin");
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
      darkMode.value = !darkMode.value;
      darkModeToggle();
    } else if (event.key === "F8") {
      event.preventDefault();
      onClickBukaManual();
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

onMounted(async () => {
  componentStore.currentPage = "outgate";
  // await transaksiStore.getCountVehicleInToday();
  // await transaksiStore.getCountVehicleOutToday();
  // await transaksiStore.getCountVehicleInside();
  // const totalVehicleOut = Array.isArray(vehicleOut)
  //   ? vehicleOut.reduce((total, count) => total + Number(count.count), 0)
  //   : 0;
  // console.log(totalVehicleOut);
  // vehicleOutToday.value = totalVehicleOut;
  // // console.log(vehicleOutToday.value);
  // vehicleInside.value = await transaksiStore.getCountVehicleInside();

  // if (transaksiStore.lokasiPos === "-") {
  //   onClickSettings();
  //   // $q.notify({
  //   //   type: "negative",
  //   //   message: "Silahkan pilih lokasi terlebih dahulu",
  //   //   position: "center",
  //   // });
  // } else
  if (!transaksiStore.API_URL || transaksiStore.API_URL === "-") {
    const dialog = $q.dialog({
      component: ApiUrlDialog,
      noBackdropDismiss: true,
    });

    dialog.update();
    $q.notify({
      type: "negative",
      message: "Silahkan Isi URL API terlebih dahulu",
      position: "top",
    });

    return;
  }

  if (transaksiStore.lokasiPos === "-") {
    onClickSettings();
    return;
  }
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

  // inputPlatNomorRef ? inputPlatNomorRef.value.focus() : "";

  window.addEventListener("keydown", handleKeyDown);

  // if ($q.platform.is.mobile) {
  //   router.push("/");
  // }
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

/* } */
</style>

<style scoped>
:deep(.input-box .q-field__control),
:deep(.input-box .q-field__append .q-field__marginal) {
  height: 10vh;
  width: 70vw;
  padding-top: 10px;
  font-size: 80px;
  font-family: "Courier New", Courier, monospace;
}
</style>
