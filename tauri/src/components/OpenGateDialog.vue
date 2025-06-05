<template>
  <q-dialog
    ref="dialogRef"
    persistent
    maximized
    transition-hide="scale"
    transition-show="scale"
    no-backdrop-dismiss
    @hide="hideDialog"
    class="q-pa-xl"
    content-css="dialog__backdrop"
  >
    <div class="q-pa-xl dialog__backdrop">
      <q-card
        class="bg-transparent no-shadow fixed-center"
        style="height: 55vh; width: 70vw"
      >
        <q-card-section class="row items-center justify-center">
          <q-card
            class="bg-white z-top"
            style="border-radius: 20px"
            transition-show="slide-down"
          >
            <q-card-section>
              <q-item class="q-pa-xl">
                <q-item-section top avatar>
                  <q-avatar
                    color="green-10"
                    text-color="white text-weight-bolder"
                    icon="check"
                    size="xl"
                  />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-h4 text-weight-bolder text-green-10"
                    >Pembayaran Berhasil</q-item-label
                  >
                </q-item-section>
              </q-item>
            </q-card-section>
          </q-card>
        </q-card-section>
        <!-- <q-separator spaced inset dark /> -->
        <q-card-section
          class="row items-center justify-center"
          style="margin-top: -70px"
        >
          <q-card
            flat
            class="glass q-mb-md q-pa-xl"
            transition-show="slide-down"
          >
            <q-card-section align="center">
              <div>
                <q-card
                  flat
                  class="text-h4 bg-primary text-white text-weight-bolder rounded-corner q-pa-lg"
                >
                  <!-- <q-item-section avatar> -->
                  <!-- <q-avatar
                    color="white"
                    text-color="primary text-weight-bolder"
                    icon="lock_open"
                    size="xl"
                  /> -->
                  <!-- </q-item-section>
                  <q-item-section> -->
                  <q-item-label>Buka Gate ?</q-item-label>
                  <!-- </q-item-section> -->
                </q-card>
              </div>
            </q-card-section>
            <q-card-section align="center">
              <q-btn
                size="xl"
                push
                style="width: 150px; height: 200px"
                label="Tidak"
                class="text-dark bg-grey-5 text-weight-bolder q-px-lg"
              >
                <q-badge color="transparent">
                  <q-btn push color="primary" label="ESC" />
                </q-badge>
              </q-btn>
              <!-- autofocus -->
              <q-btn
                size="xl"
                push
                label="Buka"
                @focus="openGateFocus = true"
                style="width: 200px; height: 200px"
                class="text-dark bg-grey-4 text-weight-bolder q-mx-md"
              >
                <!-- :class="openGateFocus ? 'bg-yellow text-dark' : 'text-dark'" -->
                <!-- @keydown.enter="onOpenGate()" -->
                <!-- color="bg-primary text-dark" -->
                <q-badge color="transparent">
                  <q-btn push color="primary" label="shift + " />
                  <q-btn push color="primary" icon="keyboard_return" />
                </q-badge>
              </q-btn>
              <!-- autofocus -->
              <q-btn
                size="xl"
                push
                label="Buka + Cetak Struk"
                @focus="openGateFocus = true"
                style="width: 200px; height: 200px"
                :class="openGateFocus ? 'bg-yellow text-dark' : 'text-dark'"
                class="text-dark bg-yellow text-weight-bolder"
              >
                <!-- @keydown.enter="onOpenGate()" -->
                <!-- color="bg-primary text-dark" -->
                <q-badge color="transparent">
                  <q-btn push color="primary" icon="keyboard_return" />
                </q-badge>
              </q-btn>
            </q-card-section>
          </q-card>
        </q-card-section>
      </q-card>

      <!-- <table ref="struk">
        <tr>
          <td class="label">Nomor Struk</td>
          <td class="value">: ${transaksiStore.nomorTiket}</td>
        </tr>
        <tr>
          <td class="label">Plat Nomor</td>
          <td class="value">: ${transaksiStore.platNomor}</td>
        </tr>
        <tr>
          <td class="label">Waktu Masuk</td>
          <td class="value">
            : ${new Date( transaksiStore.waktuMasuk ).toLocaleString("en-GB", {
            day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit",
            minute: "2-digit", })}
          </td>
        </tr>
        <tr>
          <td class="label">Waktu Keluar</td>
          <td class="value">
            : ${new Date( transaksiStore.waktuKeluar ).toLocaleString("en-GB", {
            day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit",
            minute: "2-digit", })}
          </td>
        </tr>
        <tr>
          <td class="label">Lama Parkir</td>
          <td class="value">: ${transaksiStore.durasi}</td>
        </tr>
        <tr>
          <td class="label">Biaya Parkir</td>
          <td class="value">: ${transaksiStore.biayaParkir}</td>
        </tr>
      </table> -->
    </div>
  </q-dialog>
</template>

<script setup>
import { useDialogPluginComponent, useQuasar } from "quasar";
// import SuccessCheckMark from "./SuccessCheckMark.vue";
import { onMounted, onBeforeUnmount, onBeforeMount, ref, inject } from "vue";
import { useTransaksiStore } from "src/stores/transaksi-store";
import { useComponentStore } from "src/stores/component-store";
// import { ipcRenderer } from "electron";

// import ls from "localstorage-slim";
// ls.config.encrypt = false;
const $q = useQuasar();
const transaksiStore = useTransaksiStore();
const componentStore = useComponentStore();

const openGateFocus = ref(false);
const isGateOpen = ref(false);
const { dialogRef, onDialogHide } = useDialogPluginComponent();
const onOpenGate = async () => {
  console.log("open gate");
  await componentStore.openGate();
  componentStore.setOutGateKey();
  transaksiStore.setCheckIn(false);
  transaksiStore.$reset();
  dialogRef.value.hide();
  if (isGateOpen.value == true) {
    setTimeout(async () => {
      await componentStore.closeGate();
      isGateOpen.value = false;
    }, 10000);
  }
};

const struk = ref(null);

// const cetakStruk = () => {
//   // struk.value.print();
//   transaksiStore.onClickCetakStruk();
// };

const handleKeyDown = (event) => {
  // console.log(event);
  if (event.key === "Escape") {
    event.preventDefault();
    componentStore.setOutGateKey();
    transaksiStore.setCheckIn(false);
    transaksiStore.$reset();
    dialogRef.value.hide();
  } else if (event.shiftKey === true && event.key === "Enter") {
    console.log("shift Enter");
    event.preventDefault();
    onOpenGate();
  } else if (event.key === "Enter") {
    event.preventDefault();
    console.log("Enter");
    transaksiStore.onClickCetakStruk();
    onOpenGate();
    dialogRef.value.hide();
  }
};

onMounted(async () => {
  window.addEventListener("keydown", handleKeyDown);
});

const hideDialog = () => {
  console.log("onDialogHide");
  // onDialogHide();
  window.removeEventListener("keydown", handleKeyDown);
  componentStore.isPaymentDialogMounted = false;
  componentStore.currentPage = "outgate";
};

defineEmits([
  // REQUIRED; need to specify some events that your
  // component will emit through useDialogPluginComponent()
  ...useDialogPluginComponent.emits,
]);
</script>

<style>
.glass {
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  background-color: rgba(238, 241, 239, 0.466);
  border-radius: 20px;
  border: 1px solid rgba(14, 13, 13, 0.125);
}

.q-dialog__backdrop {
  background-color: rgba(0, 0, 0, 0.73);
  backdrop-filter: blur(30px);
}
</style>
