<template>
  <q-dialog
    :maximized="true"
    ref="dialogRef"
    @hide="onDialogHide"
    class="q-pa-xl"
    content-class="dialog__backdrop"
  >
    <!-- :content-css="{ 'background-color': 'rgba(0, 0, 0, 0.9)' }" -->
    <div>
      <q-card
        style="width: 70vw; height: fit-content"
        class="q-px-md q-pt-xl q-pb-md glass rounded-corner relative fixed-center"
      >
        <!-- <div>
        <q-avatar
          size="40px"
          class="cursor-pointer z-top absolute-top-right q-ma-sm"
          text-color="grey-7"
          color="grey-5"
          icon="close"
          @click="dialogRef.hide()"
        />
      </div> -->
        <div>
          <q-chip
            class="bg-yellow-7 text-h6 text-weight-bolder absolute-top-left"
            :label="props.title"
          />
        </div>
        <div class="flex justify-center">
          <member-card
            v-if="transaksiStore.isMember"
            :nama="props.nama"
            :expiration="props.expiration"
            :ribbonText="props.ribbonText"
          />
          <plat-nomor v-else class="q-ma-md" style="transform: scale(2)" />
        </div>

        <q-input
          borderless
          class="input-box bg-primary rounded-corner relative q-pa-sm"
          input-class="input-box text-white"
          label-color="yellow text-h3"
          color="teal"
          v-model="transaksiStore.nomorTiket"
          label="Scan Nomor Struk"
          ref="strukRef"
          :rules="[
            (val) => (val ? val.length >= 4 || 'Nomor ticket kurang' : true),
          ]"
          @keydown.enter="onSaveSettings(props.type)"
          autofocus
        >
          <template v-slot:append>
            <q-btn
              push
              :size="'xl'"
              class="q-mt-xl q-mr-lg bg-white text-dark"
              icon="keyboard_return"
            />
          </template>
        </q-input>
      </q-card>
    </div>
  </q-dialog>
</template>

<script setup>
import { useDialogPluginComponent, useQuasar } from "quasar";
import { onMounted, onBeforeUnmount, onBeforeMount, ref } from "vue";
import { useTransaksiStore } from "src/stores/transaksi-store";
import MemberCard from "./MemberCard.vue";
import PlatNomor from "./PlatNomor.vue";
import TarifDialog from "./TarifDialog.vue";
import { useComponentStore } from "src/stores/component-store";

import {
  calculateParkingDuration,
  checkSubscriptionExpiration,
} from "src/utils/time-util";
import ls from "localstorage-slim";

// ls.config.encrypt = false;
const $q = useQuasar();
const transaksiStore = useTransaksiStore();
const componentStore = useComponentStore();

const props = defineProps({
  title: String,
  nama: String,
  expiration: String,
  ribbonText: String,
});

defineEmits([...useDialogPluginComponent.emits]);

const { dialogRef } = useDialogPluginComponent();
// const jenisKendaraanModel = ref(null);
// const jenisKendaraanRef = ref(null);

// const handleKeydownOnJenisKendaraan = (event) => {
//   console.log(event.key);
//   const key = event.key;
//   const matchingOption = jenisKendaraanOptions.value.find(
//     (option) => option.value === key.toUpperCase()
//   );
//   // (option) => console.log(option.value === key.toUpperCase())
//   if (matchingOption) {
//     jenisKendaraanModel.value = matchingOption.value;
//     jenisKendaraanRef.value.hidePopup();
//   }
// };

// onMounted(() => {
//   jenisKendaraanOptions.value = transaksiStore.jenisKendaraan.map((item) => {
//     return {
//       label: item.nama,
//       value: item.id,
//     };
//   });
//   // jenisKendaraanOptions.value = transaksiStore.jenisKendaraan;
// });

const onSaveSettings = async () => {
  // console.log(ls.get("jenisTarif").toLowerCase() === "manual");
  // return
  if (transaksiStore.nomorTiket.length < 4) {
    $q.notify({
      type: "negative",
      message: "Nomor tiket tidak valid",
      position: "top",
      timeout: 1000,
    });
    return;
  }

  console.log(transaksiStore.nomorTiket);

  try {
    const transaksi = await transaksiStore.getTransaksiByNopol(
      transaksiStore.nomorTiket
    );


    if (transaksi.length) {
      const waktuMasuk = new Date(transaksi[0].entry_time);
      const waktuKeluar = new Date();
      const lamaParkir = calculateParkingDuration(waktuMasuk);
      transaksiStore.durasi =
        lamaParkir.days > 0
          ? lamaParkir.additionalHourAfter24 !== 0
            ? `${lamaParkir.days} Hari ${lamaParkir.additionalHourAfter24} Jam ${lamaParkir.minutes} Menit`
            : `${lamaParkir.days} Hari ${lamaParkir.minutes} Menit`
          : lamaParkir.hours > 0
          ? `${lamaParkir.hours} Jam ${lamaParkir.minutes} Menit`
          : `${lamaParkir.minutes} Menit`;

      transaksiStore.waktuMasuk = transaksi[0].entry_time;
      transaksiStore.waktuKeluar = waktuKeluar.toISOString();

      if(transaksi[0].status === 0){
        $q.notify({
          type: "negative",
          message: "Nomor Struk Sudah Terpakai",
          position: "top",
        })
    
      }else if(ls.get("jenisTarif") === "Manual"){
        const tarifDialog = $q.dialog({
          component: TarifDialog,
          noBackdropDismiss: true,
          persistent: true,
        })
        componentStore.currentPage = "tarifDialog";
        tarifDialog.update();
        dialogRef.value.hide();
        return
      }else {
        await transaksiStore.calculateParkingFee(waktuMasuk, waktuKeluar);
     
      componentStore.currentPage = "payment";

      transaksiStore.setCheckIn(true);

      dialogRef.value.hide();
    }
    } else {
      $q.notify({
        type: "negative",
        message: "Nomor Struk Tidak Ditemukan",
      });
      transaksiStore.nomorTiket = "";
    }
  } catch (error) {
    console.log(error);
    $q.notify({
      type: "negative",
      message: error,
    });
  }
};
const onDialogHide = () => {
  console.log(componentStore.currentPage);
  // componentStore.hideInputPlatNomor = false;
  transaksiStore.dataCustomer = "";
};

// const onInputTicket = () => {
//   if (transaksiStore.platNomor.length >= 3) {
//     const firstCharacter = transaksiStore.platNomor?.charAt(0);

//     if (!isNaN(firstCharacter)) {
//       transaksiStore.platNomor = "B" + transaksiStore.platNomor?.toUpperCase();
//     } else {
//       transaksiStore.platNomor = transaksiStore.platNomor?.toUpperCase();
//     }
//   }
//   // console.log(platNomorModel.value.toUpperCase());
// };

const handleKeydownOnInputTicket = (event) => {
  if (event.key === "Escape") {
    dialogRef.value.hide();
  }
};

onMounted(() => {
  transaksiStore.nomorTiket = "";
  window.addEventListener("keydown", handleKeydownOnInputTicket);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKeydownOnInputTicket);
});

// const jenisKendaraanValue = computed(()=>;

// const filterJenisKendaraan = (val, update) => {
//   if (val === '') {
//     update(() => {
//       jenisKendaraanOptions.value =  jenisKendaraanValue
//     })
//     return
//   }
//   update(() => {
//           const needle = val.toLowerCase()
//           jenisKendaraanOptions.value = jenisKendaraanValue.filter(v => v.toLowerCase().indexOf(needle) > -1)
//         })
//       }
</script>

<style scoped>
:deep(.q-dialog__backdrop.fixed-full) {
  background-color: rgba(0, 0, 0, 0.432);
  backdrop-filter: blur(30px);
}
.glass {
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  background-color: rgba(255, 255, 255, 0.301);
  border-radius: 20px;
  border: 1px solid rgba(14, 13, 13, 0.125);
}

/* :deep(.input-box .q-field__append), */
:deep(.input-box .q-field__control),
:deep(.input-box .q-field__append .q-field__marginal) {
  height: 10vh;
  width: 80vw;
  font-size: 2rem;
  font-family: "Courier New", Courier, monospace;
}
</style>
