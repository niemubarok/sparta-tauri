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
      class="q-px-md q-pt-xl q-pb-md glass rounded-corner relative fixed-center"
    >
      <div>
        <q-avatar
          size="40px"
          class="cursor-pointer z-top absolute-top-right q-ma-sm"
          text-color="grey-7"
          color="grey-5"
          icon="close"
          @click="dialogRef.hide()"
        />
      </div>
      <!-- <q-icon name="close"  /> -->
      <!-- <q-item> -->
      <!-- <q-item-section avatar>
          <q-icon :name="props.icon" size="xl" />
        </q-item-section> -->
      <!-- <q-item-section> -->
      <!-- style="margin-left: -15px" -->
      <div>
        <q-chip
          class="bg-yellow-7 text-h6 text-weight-bolder absolute-top-left q-pa-md"
          label="Pilih Jenis Kendaraan"
        />
      </div>
      <div class="flex justify-center">
        <!-- <member-card v-if="transaksiStore.isMember" /> -->
        <plat-nomor class="q-ma-lg" />
      </div>

      <div
        v-for="jenisKendaraan in jenisKendaraanOptions"
        :key="jenisKendaraan.id"
      >
        <q-item
          :class="
            defaultShortcut === jenisKendaraan.shortcut && 'bg-yellow text-dark'
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
// import SuccessCheckMark from "./SuccessCheckMark.vue";
import { onMounted, onBeforeUnmount, onBeforeMount, ref } from "vue";
import { useTransaksiStore } from "src/stores/transaksi-store";
import MemberCard from "./MemberCard.vue";
import PlatNomor from "./PlatNomor.vue";
import { useComponentStore } from "src/stores/component-store";
import TicketDialog from "src/components/TicketDialog.vue";
import ls from "localstorage-slim";
// import { useClassesStore } from "src/stores/classes-store";

// ls.config.encrypt = false;
const transaksiStore = useTransaksiStore();
const componentStore = useComponentStore();
const $q = useQuasar();

const props = defineProps({
  title: String,
  icon: String,
  type: String,
});

defineEmits([
  // REQUIRED; need to specify some events that your
  // component will emit through useDialogPluginComponent()
  ...useDialogPluginComponent.emits,
]);

const { dialogRef } = useDialogPluginComponent();
const onDialogHide = () => {
  componentStore.hideInputPlatNomor = false;
  window.removeEventListener("keydown", handleKeydownOnJenisKendaraan);
};

const jenisKendaraanOptions = ref([]);
const jenisKendaraanModel = ref(null);
const jenisKendaraanRef = ref(null);
const defaultJenisKendaraan = ref(ls.get("defaultJenisKendaraan"));
const defaultShortcut = ref("A");
const matchingDefaultOption = ref(null);

const onClickTicket = (type) => {
  // transaksiStore.setCheckIn(true);
  const dialog = $q.dialog({
    component: TicketDialog,
    // noBackdropDismiss: true,
    // persistent: true,
    componentProps: {
      title: type,
    },
  });

  dialog.update();
  // componentStore.hideInputPlatNomor = true;
};

const handleKeydownOnJenisKendaraan = (event) => {
  const key = event.key;
  const matchingOption = jenisKendaraanOptions.value.find(
    (option) => option?.shortcut === key.toUpperCase()
  );

  if (key === "Escape") {
    dialogRef.value.hide();
  }

  if (key === "Enter") {
    // const matchingDefaultOption = jenisKendaraanOptions.value.find(
    //   (option) => option.shortcut === defaultJenisKendaraan.value.shortcut
    // );

    // console.log("matchingDefaultOption", matchingDefaultOption);
    // console.log("matchingOption", matchingOption);
    jenisKendaraanModel.value = matchingDefaultOption.value.id;
    transaksiStore.selectedJenisKendaraan = matchingDefaultOption.value;
    // console.log(transaksiStore.selectedJenisKendaraan);
    onClickTicket(matchingDefaultOption.value.label);
    dialogRef.value.hide();
  } else if (matchingOption) {
    // console.log("matchingOption", matchingOption);
    jenisKendaraanModel.value = matchingOption.id;
    transaksiStore.selectedJenisKendaraan = matchingOption;
    onClickTicket(matchingOption.label);
    dialogRef.value.hide();
  }
};

onMounted(async () => {
  transaksiStore.jenisKendaraan = await transaksiStore.getJenisKendaraan();
  jenisKendaraanOptions.value = transaksiStore.jenisKendaraan;
  matchingDefaultOption.value = jenisKendaraanOptions.value.find(
    (option) => option.shortcut === defaultJenisKendaraan.value.shortcut
  );
  defaultShortcut.value = matchingDefaultOption.value.shortcut;

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
