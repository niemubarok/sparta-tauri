<template>
  <q-dialog
   :maximized="true"
    ref="dialogRef"
    @hide="onDialogHide"
    class="q-pa-xl"
    content-class="dialog__backdrop"
  >
    <!-- no-backdrop-dismiss
    no-route-dismiss -->
    <!-- :content-css="{ 'background-color': 'rgba(0, 0, 0, 0.9)' }" -->
    <div>
    <q-card
      style="width: 50vw; height: fit-content"
      class="q-px-md q-pt-md q-pb-md glass rounded-corner relative fixed-center"
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
      <!-- <q-icon name="close"  /> -->
      <!-- <q-item> -->
      <!-- <q-item-section avatar>
          <q-icon :name="props.icon" size="xl" />
        </q-item-section> -->
      <!-- <q-item-section> -->
      <!-- style="margin-left: -15px" -->
      <div>
        <q-chip
          :color="props.isPrepaidMode ? 'green' : 'blue'"
          text-color="white"
          class="text-body1 text-weight-bolder absolute-top-center q-pa-md"
          :label="props.isPrepaidMode 
            ? 'Pilih Jenis Kendaraan (Tekan shortcut atau Enter untuk default)' 
            : 'Pilih Jenis Kendaraan'"
        />
      </div>
      <!-- <div class="flex justify-center"> -->
        <!-- <member-card v-if="transaksiStore.isMember" /> -->
        <!-- <plat-nomor class="q-ma-lg" />
      </div> -->
      <div
        v-for="jenisKendaraan in jenisKendaraanOptions"
        :key="jenisKendaraan.id"
      >
        <q-item
          :class="
            defaultShortcut === jenisKendaraan?.shortcut && 'bg-yellow text-dark'
          "
          class="glass q-ma-md rounded-corner"
        >
          <q-item-section top avatar>
            <!-- <q-avatar color="primary" text-color="white" icon="bluetooth" /> -->
            <q-chip
              square
              class="bg-dark text-white text-weight-bolder q-px-md"
              :label="jenisKendaraan.shortcut"
            />
          </q-item-section>
          <q-item-section>
            <q-item-label class="text-h6">{{
              jenisKendaraan.label
            }}</q-item-label>
          </q-item-section>
        </q-item>
      </div>
    </q-card>
    </div>
  </q-dialog>
</template>

<script setup>
import { useDialogPluginComponent, useQuasar } from "quasar";
import { onMounted, onBeforeUnmount, onBeforeMount, ref } from "vue";
import { useTransaksiStore } from "src/stores/transaksi-store";
import { useTarifStore } from "src/stores/tarif-store";
import { useGateStore } from "src/stores/gate-store";
import MemberCard from "./MemberCard.vue";
import PlatNomor from "./PlatNomor.vue";
import { useComponentStore } from "src/stores/component-store";
import ls from "localstorage-slim";
// import { useClassesStore } from "src/stores/classes-store";

// ls.config.encrypt = false;
const transaksiStore = useTransaksiStore();
const componentStore = useComponentStore();
const tarifStore = useTarifStore();
const gateStore = useGateStore();
const $q = useQuasar();

const props = defineProps({
  title: String,
  icon: String,
  type: String,
  isPrepaidMode: {
    type: Boolean,
    default: false
  },
  customerData: {
    type: Object,
    default: null
  }
});

defineEmits([
  // REQUIRED; need to specify some events that your
  // component will emit through useDialogPluginComponent()
  ...useDialogPluginComponent.emits,
]);

const { dialogRef, onDialogOK } = useDialogPluginComponent();
const onDialogHide = () => {
  componentStore.hideInputPlatNomor = false;
  window.removeEventListener("keydown", handleKeydownOnJenisKendaraan);
  ticketDialogOpened.value = false; // Reset ticket dialog flag
  console.log('🚪 JenisKendaraanDialog hidden, cleanup completed');
};

const jenisKendaraanOptions = ref([]);
const jenisKendaraanModel = ref(null);
const jenisKendaraanRef = ref(null);
const defaultJenisKendaraan = ref(ls.get("defaultJenisKendaraan"));
const defaultShortcut = ref("C");
const matchingDefaultOption = ref(null);

const onClickTicket = async (type) => {
  // Remove keydown event listener before proceeding
  window.removeEventListener("keydown", handleKeydownOnJenisKendaraan);

  if (props.isPrepaidMode) {
    // Return selected vehicle type for prepaid mode
    dialogRef.value.hide();
    onDialogOK({ 
      success: true, 
      isPrepaid: true,
      selectedVehicle: transaksiStore.selectedJenisKendaraan
    });
  } else {
    // Postpaid mode - traditional flow
    transaksiStore.isCheckedIn = true;
    componentStore.hideInputPlatNomor = true;
    dialogRef.value.hide();
    onDialogOK({ success: true, isPrepaid: false });
  }
};

const ticketDialogOpened = ref(false)

const handleKeydownOnJenisKendaraan = (event) => {
  const key = event.key.toUpperCase();
  
  // Cari berdasarkan shortcut
  const matchingOption = jenisKendaraanOptions.value.find(
    (option) => option?.shortcut?.toUpperCase() === key
  );

  if (key === "ESCAPE") {
    dialogRef.value.hide();
  }

  if (key === "ENTER" && !ticketDialogOpened.value) {
    ticketDialogOpened.value = true;
    // Gunakan default option
    console.log("🚀 ~ handleKeydownOnJenisKendaraan ~ matchingDefaultOption.value:", matchingDefaultOption.value)
    if (matchingDefaultOption.value) {
      jenisKendaraanModel.value = matchingDefaultOption.value.id;
      transaksiStore.selectedJenisKendaraan = matchingDefaultOption.value;
      onClickTicket(matchingDefaultOption.value.label);
      // Only auto-hide in postpaid mode, prepaid mode handles dialog closing in onClickTicket
      if (!props.isPrepaidMode) {
        dialogRef.value.hide();
      }
    }
  } else if (matchingOption && !ticketDialogOpened.value) {
    ticketDialogOpened.value = true;
    // Gunakan option yang sesuai dengan shortcut
    console.log("matchingOption", matchingOption);
    jenisKendaraanModel.value = matchingOption.id;
    transaksiStore.selectedJenisKendaraan = matchingOption;
    onClickTicket(matchingOption.label);
    // Only auto-hide in postpaid mode, prepaid mode handles dialog closing in onClickTicket
    if (!props.isPrepaidMode) {
      dialogRef.value.hide();
    }
  }
};

onMounted(async () => {
  // Load vehicle types and tariff data
  transaksiStore.jenisKendaraan = await transaksiStore.getJenisKendaraan();
  jenisKendaraanOptions.value = transaksiStore.jenisKendaraan;
  
  // Load prepaid tariffs if in prepaid mode
  if (props.isPrepaidMode) {
    try {
      await tarifStore.loadTarifPrepaidFromLocal();
    } catch (error) {
      console.error('Error loading prepaid tariffs:', error);
    }
  }
  
  // Cek default jenis kendaraan dari local storage
  const savedDefault = ls.get("defaultJenisKendaraan");
  if (savedDefault && savedDefault.shortcut) {
    matchingDefaultOption.value = jenisKendaraanOptions.value.find(
      (option) => option.shortcut === "C"
    );
    // if (matchingDefaultOption.value) {
    //   defaultShortcut.value = matchingDefaultOption.value.shortcut;
    // }
  }
  
  // Jika tidak ada default yang tersimpan, gunakan yang pertama
  if (!matchingDefaultOption.value && jenisKendaraanOptions.value.length > 0) {
    matchingDefaultOption.value = jenisKendaraanOptions.value[1];
    defaultShortcut.value = "C";
  }

  // console.log(transaksiStore.jenisKendaraan);

  window.addEventListener("keydown", handleKeydownOnJenisKendaraan);
});

// onUnmounted(() => {
// //   window.removeEventListener("keydown", handleKeydownOnJenisKendaraan);
// // });
</script>

<style scoped>
:deep(.q-dialog__backdrop.fixed-full) {
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
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
