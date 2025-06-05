<template>
  <q-page
    class="flex column flex-start card-gradient"
    style="overflow-y: auto"
    padding
  >
    <div class="full-width flex row flex-center">
      <template v-for="data in dataPenjualan" :key="data.caption">
        <!-- :number="data.number" -->
        <CardNumber
          :caption="data.caption"
          icon="logout"
          class="col-md col-xs-11 q-my-sm q-mx-sm"
          style="height: 20vh"
        />
      </template>
    </div>
    <div class="row">
      <!-- <BarChart
        class="col q-ma-md"
        :chart-data="reportStore().kunjunganPerBulan"
      />
      <BarChart
        class="col q-ma-md"
        :chart-data="reportStore().kunjunganPerMinggu"
      /> -->
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import GrowingNumber from "src/components/GrowingNumber.vue";
import CardNumber from "src/components/CardNumber.vue";
// import BarChart from "src/components/BarChart.vue";
// import { chartStore } from "src/stores/chart-store";
// import { reportStore } from "src/stores/report-store";
// import { wahanaStore } from "src/stores/wahana-store";

// onMounted(async () => {
//   if (wahanaStore().daftarWahana?.length === 0) {
//     await wahanaStore().getWahanaFromDB();
//   }
//   await reportStore().getLaporanPendapatan();
//   await reportStore().getLaporanKunjungan();
//   await reportStore().getLaporanKunjunganWahana();
// });

// Menggunakan komputasi dinamis untuk properti number
const dataPenjualan = ref([
  // {
  //   caption: "Jumlah Wahana",
  //   get number() {
  //     return wahanaStore().daftarWahana?.length;
  //   },
  //   icon: "",
  // },
  {
    caption: "Pengunjung Hari Ini",
    // get number() {
    //   return reportStore().kunjunganPerHari;
    // },
    icon: "trending_up",
  },
  {
    caption: "Pengunjung Bulan Ini",
    // get number() {
    //   return reportStore().kunjunganPerBulan;
    // },
    icon: "trending_up",
  },
  {
    caption: "Pendapatan Hari Ini ",
    // get number() {
    //   return reportStore().pendapatanPerHari;
    // },
    icon: "trending_up",
  },
  // {
  //   caption: "Pendapatan / Bulan ",
  //   get number() {
  //     return reportStore().pendapatanPerBulan;
  //   },
  //   icon: "trending_up",
  // },
]);
</script>
