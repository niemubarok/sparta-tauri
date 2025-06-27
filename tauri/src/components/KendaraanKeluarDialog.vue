<template>
  <q-dialog
    :maximized="true"
    ref="dialogRef"
    @hide="onDialogHide"
    content-class="dialog__backdrop relative"
  >
    <!-- :maximized="true" -->
    <!-- class="q-pa-sm" -->
    <div>
      <q-card
        style="width: 80vw; height: fit-content"
        class="q-pa-sm dark-glass fixed-center relative"
      >
        <div class="absolute-top-left q-pl-md q-pt-sm">
          <q-btn
            push
            color="grey-1"
            text-color="grey-8"
            label="ESC"
            class="text-weight-bolder text-subtitle2"
          />
        </div>
        <div
          class="text-center text-weight-bolder text-grey-2 text-h5 q-ml-md q-mb-md"
        >
          .:: Detail Kendaraan Keluar ::.
        </div>
        <div class="flex justify-center">
          <div class="row items-start full-width">
            <q-card class="full-width q-pa-md" flat bordered>
              <q-item>
                <q-item-section avatar>
                  <q-avatar>
                    <img src="https://cdn.quasar.dev/img/boy-avatar.png" />
                  </q-avatar>
                </q-item-section>

                <q-item-section>
                  <q-item-label>{{ ls.get("pegawai").nama }}</q-item-label>
                  <q-item-label caption>
                    <q-chip
                      class="q-px-sm"
                      square
                      dense
                      :label="'Shift: ' + ls.get('shift')"
                    />
                  </q-item-label>
                </q-item-section>

                <q-item-section side>
                  <div class="row">
                    <q-chip
                      square
                      class="bg-primary text-white text-weight-bolder q-py-lg q-pr-md"
                      label="Total"
                    >
                      <q-chip
                        square
                        class="q-pa-md text-h6 text-weight-bold q-ml-md"
                        style="margin-right: -10px"
                        :label="totalUangMasuk"
                      />
                    </q-chip>
                  </div>
                </q-item-section>
              </q-item>

              <q-separator />
              <!-- {{ kendaraanKeluar }} -->
              <div v-if="kendaraanKeluar?.count == 0" class="q-mt-md">
                <q-card flat class="bg-grey-3 text-grey-6">
                  <q-card-section>
                    <div class="text-h6">
                      Belum ada Kendaraan Keluar di shift ini
                    </div>
                  </q-card-section>
                </q-card>
              </div>
              <div v-else class="q-mt-md">
                <q-table
                  bordered
                  :rows="kendaraanKeluar"
                  :columns="tableColumns"
                  row-key="nama"
                  class="no-shadow rounded-corner"
                >
                  <template v-slot:header="props">
                    <q-tr
                      :props="props"
                      class="text-weight-bolder bg-primary text-white"
                    >
                      <q-td>Jenis Kendaraan</q-td>
                      <q-td align="center">Jumlah</q-td>
                      <q-td align="center">Uang Masuk</q-td>
                    </q-tr>
                  </template>
                  <template v-slot:body="props">
                    <q-tr
                      :props="props"
                      :class="props.rowIndex % 2 == 0 ? 'bg-grey-2' : ''"
                      class="text-weight-bolder"
                    >
                      <q-td key="nama" :props="props">
                        <span class="text-h5">
                          {{ props.row.nama }}
                        </span>
                      </q-td>
                      <q-td
                        key="count"
                        :props="props"
                        align="center"
                        class="text-h4 row justify-center"
                      >
                        <span class="text-h5">
                          {{ props.row.count }}
                        </span>
                      </q-td>
                      <q-td
                        key="uang_masuk"
                        :props="props"
                        style="width: 200px"
                      >
                        <div class="row justify-between">
                          <span class="text-h5"> Rp </span>
                          <span class="text-h5">
                            {{ props.row.uang_masuk.toLocaleString("id-ID") }}
                          </span>
                        </div>
                      </q-td>
                    </q-tr>
                  </template>
                </q-table>
              </div>
            </q-card>
          </div>
        </div>
      </q-card>
    </div>
  </q-dialog>
</template>

<script setup>
import { useDialogPluginComponent } from "quasar";
// import SuccessCheckMark from "./SuccessCheckMark.vue";
import { onMounted, onBeforeUnmount, onBeforeMount, ref } from "vue";
import { useTransaksiStore } from "src/stores/transaksi-store";
import MemberCard from "./MemberCard.vue";
import PlatNomor from "./PlatNomor.vue";
import { useComponentStore } from "src/stores/component-store";
import ls from "localstorage-slim";
// import { useClassesStore } from "src/stores/classes-store";

// ls.config.encrypt = false;
const transaksiStore = useTransaksiStore();
const componentStore = useComponentStore();
const totalUangMasuk = ref(0);

const kendaraanKeluar = ref([]);

defineEmits([...useDialogPluginComponent.emits]);

const { dialogRef } = useDialogPluginComponent();

onMounted(async () => {
  try {
    kendaraanKeluar.value = await transaksiStore.getVehicleOutDetailsToday();
    
    // Add safety check for kendaraanKeluar
    if (kendaraanKeluar.value && Array.isArray(kendaraanKeluar.value) && kendaraanKeluar.value.length > 0) {
      totalUangMasuk.value = kendaraanKeluar.value
        .reduce((total, item) => total + parseInt(item.uang_masuk || 0), 0)
        .toLocaleString("id-ID", {
          style: "currency",
          currency: "IDR",
        })
        .split(",")[0];
    } else {
      // If no data or not an array, set default values
      kendaraanKeluar.value = [];
      totalUangMasuk.value = "Rp 0";
    }
  } catch (error) {
    console.error('Error loading vehicle out data:', error);
    // Set default values on error
    kendaraanKeluar.value = [];
    totalUangMasuk.value = "Rp 0";
  }

  const handleKeyDown = (event) => {
    // console.log(event.key);
    if (componentStore.currentPage == "outgate") {
      if (event.key === "Escape") {
        event.preventDefault();
        dialogRef.value.hide();
        componentStore.setOutGateKey();
      }
    }
  };

  window.addEventListener("keydown", handleKeyDown);
});
const onDialogHide = () => {};
</script>

<style scoped>
:deep(.q-dialog__backdrop.fixed-full) {
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
}
.glass {
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  background-color: rgba(255, 255, 255, 0.863);
  border: 1px solid rgba(14, 13, 13, 0.125);
  border-radius: 10px;
}

.dark-glass {
  border-radius: 10px;

  background-color: #083517;
  background: linear-gradient(
    0deg,
    rgba(40, 44, 52, 1) 0%,
    rgba(17, 0, 32, 0.5) 100%
  );
  backdrop-filter: blur(7px);
  -webkit-backdrop-filter: blur(7px);
}
</style>

<style lang="sass">
.sticky-header-table
  /* height or max-height is important */
  height: 310px

  .q-table__top,
  .q-table__bottom,
  thead tr:first-child th
    /* bg color is important for th; just specify one */
    background-color: #E2DFE4

  thead tr th
    position: sticky
    z-index: 1
  thead tr:first-child th
    top: 0

  /* this is when the loading indicator appears */
  &.q-table--loading thead tr:last-child th
    /* height of all previous header rows */
    top: 48px

  /* prevent scrolling behind sticky top row on focus */
  tbody
    /* height of all previous header rows */
    scroll-margin-top: 48px
/* :deep(.input-box .q-field__append), */
/* :deep(.input-box .q-field__control),
// :deep(.input-box .q-field__append .q-field__marginal) {
//   height: 10vh;
//   width: 80vw;
//   font-size: 2rem;
//   font-family: "Courier New", Courier, monospace;
// } */
</style>
