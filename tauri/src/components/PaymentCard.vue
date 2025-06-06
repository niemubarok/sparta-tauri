<template>
  <div :ref="paymentCardKey" class="relative flex row justify-start full-width">
    <!-- <Clock class="absolute-top-left q-ma-md" /> -->
    <!-- card untuk transaksi pembayaran -->
    <div class="col-6">
      <q-card flat rounded class="bg-grey-4 relative">
        <!-- style="top: 5vh; width: 95vw; height: 91vh; border-radius: 10px" -->
        <!-- <div>
          <q-btn
            push
            class="z-top absolute-top-left q-ma-sm"
            text-color="grey-9"
            color="grey-1"
            no-caps
            label="shift + esc"
          >
          </q-btn>
        </div> -->
        <q-card-section>
          <q-card flat bordered class="glass">
            <!-- style="width: 60vw; height: 55vh" -->
            <MemberRibbon v-if="transaksiStore.isMember" />
            <div>
              <q-chip
                square
                class="bg-grey-4 rounded-corner text-primary text-body"
                >Detail Parkir</q-chip
              >
            </div>

            <!-- <q-card-section> -->
            <div class="flex row">
              <div class="col-6 q-ma-md">
                <div class="column">
                  <div class="col q-mb-md">
                    <!-- NOMOR TIKET -->
                    <q-chip
                      square
                      outline
                      class="q-py-lg text-h6 text-dark q-mb-md relative full-width"
                      :label="transaksiStore.nomorTiket"
                    >
                      <!-- style="border-color: ;" -->
                      <q-badge
                        color="primary"
                        text-color="white"
                        label="No. Tiket "
                        class="q-mb-md absolute-top-left"
                        style="top: -8px; left: 5px"
                      />
                    </q-chip>
                    <!-- JENIS KENDARAAN  -->
                    <q-chip
                      square
                      outline
                      class="q-py-lg text-h6 text-dark q-mb-sm relative full-width"
                      :label="transaksiStore.selectedJenisKendaraan?.label"
                    >
                      <!-- style="border-color: ;" -->
                      <!-- floating -->
                      <q-badge
                        color="primary"
                        text-color="white"
                        label="Jenis Kendaraan"
                        class="q-mb-md absolute-top-left"
                        style="top: -8px; left: 5px"
                      />
                    </q-chip>
                    <PlatNomor
                      style="transform: scale(1.1)"
                      class="q-mt-md q-ml-md"
                    />
                  </div>

                  <div class="flex justify-start q-mr-xl">
                    <!-- PLAT NOMOR  -->
                  </div>
                </div>
              </div>

              <div class="col-5 q-pl-md">
                <q-timeline color="secondary" layout="dense">
                  <q-timeline-entry
                    :title="tanggalMasuk"
                    subtitle="Tanggal Masuk"
                    icon="today"
                  />
                  <!-- side="right" -->
                  <q-timeline-entry
                    :title="waktuMasuk"
                    subtitle="Waktu Masuk"
                    icon="schedule"
                  />
                  <!-- side="right" -->

                  <q-timeline-entry
                    :title="transaksiStore.durasi"
                    subtitle="Lama Parkir"
                    icon="timer"
                  />
                  <!-- side="right" -->
                </q-timeline>
              </div>
            </div>
            <!-- </q-card-section> -->
          </q-card>

          <div class="column q-mt-sm">
            <!-- TOTAL BAYAR  -->
            <q-card
              bordered
              class="glass text-dark q-pr-sm q-mr-xl relative full-width"
            >
              <!-- style="width: 40vw" -->
              <q-card-section>
                <div class="text-h6 text-right">Biaya Parkir</div>
                <div
                  class="text-right text-weight-bold"
                  style="
                    font-size: clamp(2rem, 4rem, 5rem);
                    font-family: 'Courier Prime', monospace;
                  "
                >
                  {{
                    transaksiStore.biayaParkir
                      .toLocaleString("id-ID", {
                        style: "currency",
                        currency: "IDR",
                      })
                      .split(",")[0]
                  }}
                </div>
              </q-card-section>
            </q-card>
            <div class="row justify-end">
              <!-- <q-btn
                push
                class="col text-right text-wrap text-dark text-weight-bolder text-h4 bg-yellow q-mt-sm q-mr-sm"
                label="BAYAR CASHLESS"
                style="font-size: clamp(1rem, 1rem, 1rem)"
              >
                <q-btn
                  push
                  color="grey-9"
                  text-color="white"
                  label="shift"
                  class="text-weight-bolder text-body q-ml-sm"
                />
                <q-btn
                  push
                  color="grey-9"
                  text-color="white"
                  icon="keyboard_return"
                  class="text-weight-bolder text-body q-ml-sm"
                />
              </q-btn> -->
              <q-btn
                push
                class="col text-right text-dark text-weight-bolder text-h4 bg-yellow q-mt-sm"
                label="BAYAR CASH"
                style="font-size: clamp(1rem, 1rem, 1rem)"
              >
                <q-btn
                  push
                  color="grey-9"
                  text-color="white"
                  icon="keyboard_return"
                  class="text-weight-bolder text-body q-ml-sm"
                />
              </q-btn>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </div>

    <!-- FOTO KENDARAAN -->
    <div class="col-6 column justify-between fixed-top-right full-height">
      <div class="col-4 q-mb-md q-mr-md">
        <FotoKendaraan
          class="col-4"
          title="Foto Masuk"
          type="image"
          :url="picBodyMasuk"
        />
      </div>
      <!-- :style="{ width: '45vw', height: '30vh' }" -->
      <div class="col-6 items-end">
        <!-- :key="componentStore.cameraOutKey"  -->
        <Camera
          v-if="componentStore.currentPage === 'payment'"
          class="rounded-corner"
          camera-location="out"
          :camera-url="gateSettings.value?.DRIVER_CAM_URL || gateSettings.value?.SCANNER_CAM_URL || ''" 
          :file-name="cameraOutFileName"
          :isInterval="false"
          :style="{
            width: '49vw',
          }"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useTransaksiStore } from "src/stores/transaksi-store";
import { useComponentStore } from "src/stores/component-store";
import { useSettingsService } from "src/stores/settings-service"; // Diubah
import FotoKendaraan from "src/components/FotoKendaraan.vue";
import { format, useQuasar } from "quasar";
import CameraOut from "./CameraOut.vue";
import Clock from "./Clock.vue";
import PaymentDialogComponent from "./PaymentDialog.vue";
import OpenGateDialogComponent from "./OpenGateDialog.vue";
import ls from "localstorage-slim";
import PlatNomor from "./PlatNomor.vue";
import MemberRibbon from "./MemberRibbon.vue";
import Camera from "./Camera.vue";

import axios from "axios";

const $q = useQuasar();
const transaksiStore = useTransaksiStore();
const componentStore = useComponentStore();
const { gateSettings, globalSettings } = useSettingsService(); // Diubah
// TODO: Periksa apakah fetchCameraImage ada di settingsService atau perlu diimplementasikan ulang.
// const buttonBatal = ref(false);
const cameraOut = ls.get("cameraOut") || null;
const cameraOutFileName = `${ls.get("lokasiPos").value}_out_snapshot` || null;
const cameraOutRef = ref(null);
// const bayarParkir = () => {
//   // logika bayar parkir
// };

const waktuMasuk = ref(
  new Date(transaksiStore.waktuMasuk)
    .toLocaleTimeString("id-ID", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })
    .replace(/\./g, ":")
);

const tanggalMasuk = ref(
  new Date(transaksiStore.waktuMasuk).toLocaleString("id-ID", {
    // weekday: "long",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  })
);
// const lokasiPos = ref(ls.get("lokasiPos")?.label);
// const componentStore.isPaymentDialogMounted ref(false);

const onClickBayar = async () => {
  // const video = videoRef.value;
  // const videoRef = cameraOutRef.value?.$refs.videoRef;
  // transaksiStore.waktuMasuk = waktuMasuk.value;

  // if (videoRef !== undefined) {
  // const canvas = document.createElement("canvas");
  // const context = canvas.getContext("2d");
  // context.drawImage(videoRef, 0, 0, canvas.width, canvas.height);

  // const imageBase64 = canvas.toDataURL("image/png");

  // // transaksiStore.pic_body_keluar = gateSettings.value?.DRIVER_CAM_URL || gateSettings.value?.SCANNER_CAM_URL || ''; // Diubah, dikomentari karena pic_body_keluar sepertinya untuk base64 image, bukan URL
  // }

  // console.log("isPaymentDialogMounted:", !isPaymentDialogMounted);
  // console.log("transaksiStore.isMember:", transaksiStore.isMember);
  // console.log(
  //   "transaksiStore.isMemberExpired:",
  //   transaksiStore.isMemberExpired
  // );
  // console.log(
  //   "componentStore.currentPage === 'payment':",
  //   componentStore.currentPage === "payment"
  // );

  if (
    componentStore.currentPage === "payment"
    // &&
    // componentStore.isPaymentDialogMounted === false
  ) {
    // if (!transaksiStore.isMember) {
    //   const paymentDialog = $q.dialog({
    //     component: PaymentDialogComponent,
    //     noBackdropDismiss: true,
    //     // noEscDismiss: true,
    //     // persistent: true,
    //   });

    //   paymentDialog.update();
    //   componentStore.isPaymentDialogMounted = true;
    // } else if (transaksiStore.isMember && transaksiStore.isMemberExpired) {
    //   const paymentDialog = $q.dialog({
    //     component: PaymentDialogComponent,
    //     noBackdropDismiss: true,
    //     // noEscDismiss: true,
    //     // persistent: true,
    //   });
    //   componentStore.isPaymentDialogMounted = true;
    //   paymentDialog.update();
    // } else {
    // console.log("kesini");
    // if (componentStore.currentPage === "payment") {
    try {
      // TODO: Ganti dengan implementasi dari settingsService atau logika baru
      // const image = await settingsService.fetchCameraImage( 
      //   cameraOutFileName, 
      //   gateSettings.value?.DRIVER_CAM_URL || gateSettings.value?.SCANNER_CAM_URL || '' 
      // );
      // Untuk sementara, kita akan log dan set ke null
      console.warn('fetchCameraImage from settingsStore needs to be replaced with settingsService equivalent.');
      const image = null;
      transaksiStore.pic_body_keluar = image;
    } catch (error) {
      console.error("Error fetching camera image:", error);
      // Handle the error appropriately, e.g., set a default image or log the error
      transaksiStore.pic_body_keluar = null; // Contoh set gambar default
    }

    // const isBase64 = (str) => {
    //   if (typeof str !== "string" || !str) return false; // Pastikan str adalah string dan tidak kosong
    //   const notBase64 = /[^A-Z0-9+\/=]/i;
    //   const isPadded = str.endsWith("="); // Sekarang aman untuk memanggil endsWith
    //   return !notBase64.test(str) && isPadded;
    // };

    // console.log(isBase64(transaksiStore.pic_body_keluar));
    // console.log(transaksiStore.pic_body_keluar);

    const updateTransaksi = await transaksiStore.updateTableTransaksi();
    if (updateTransaksi == 200) {
      const openGateDialog = $q.dialog({
        component: OpenGateDialogComponent,
        noBackdropDismiss: true,
      });

      openGateDialog.update();

      window.removeEventListener("keydown", handleKeyDown);
      // }
      // componentStore.isPaymentDialogMounted = true;
      // }
    }
  }
};

let pressedKeys = "";
const targetKeys = "BUKA MANUAL";
const picBodyMasuk = ref();

const handleKeyDown = (event) => {
  // console.log(event.key);

  if (componentStore.currentPage === "payment") {
    if (event.key === "Enter") {
      event.preventDefault();
      onClickBayar();
      pressedKeys = "";
    }
    if (event.shiftKey === true && event.key === "Escape") {
      event.preventDefault();
      if (componentStore.isPaymentDialogMounted === false) {
        onClosePaymentCard();
      }
      pressedKeys = "";
    } else {
      // Add the pressed key to the string of pressed keys
      pressedKeys += event ?? event.key.toUpperCase();

      // Check if the pressed keys match the target keys
      if (pressedKeys === targetKeys) {
        // Call the function to execute
        console.log("Buka Manual");
      }

      // Reset the pressed keys string if it doesn't match the target keys
      if (!targetKeys.startsWith(pressedKeys)) {
        pressedKeys = "";
      }
    }
  }
};

const onClosePaymentCard = () => {
  componentStore.currentPage = "outgate";
  componentStore.setOutGateKey();
  transaksiStore.setCheckIn(false);
  transaksiStore.$reset();
  window.removeEventListener("keydown", handleKeyDown);
};
onMounted(async () => {
  // console.log(transaksiStore.waktuMasuk);
  console.log(componentStore.currentPage);
  try {
    const getPicBodyMasuk = await axios.post(
      transaksiStore.API_URL + "/transactions/pic",
      {
        no_pol: transaksiStore.nomorTiket,
      }
    );

    const contentType = getPicBodyMasuk.data.startsWith("data:image/png")
      ? "png"
      : "jpg";
    if (!getPicBodyMasuk.data.startsWith("data:image")) {
      picBodyMasuk.value =
        `data:image/${contentType};base64,` + getPicBodyMasuk.data;
    } else {
      picBodyMasuk.value = getPicBodyMasuk.data;
    }
  } catch (error) {
    console.error(error);
  }
  window.addEventListener("keydown", handleKeyDown);
  componentStore.currentPage = "payment";
});
</script>

<style scoped>
.glass {
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  background-color: rgba(255, 255, 255, 0.76);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.125);
}

.gradient-primary {
  background-color: hsla(239, 100%, 80%, 1);
  background-image: radial-gradient(
      at 24% 1%,
      hsla(275, 100%, 28%, 1) 0px,
      transparent 50%
    ),
    radial-gradient(at 19% 98%, hsla(258, 96%, 28%, 1) 0px, transparent 50%),
    radial-gradient(at 24% 48%, hsla(292, 56%, 54%, 1) 0px, transparent 50%),
    radial-gradient(at 9% 13%, hsla(225, 86%, 64%, 1) 0px, transparent 50%),
    radial-gradient(at 64% 45%, hsla(275, 80%, 37%, 1) 0px, transparent 50%),
    radial-gradient(at 49% 37%, hsla(225, 42%, 48%, 1) 0px, transparent 50%),
    radial-gradient(at 76% 5%, hsla(14, 74%, 66%, 1) 0px, transparent 50%);
}
</style>
