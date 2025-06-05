<template>
  <q-card flat class="bg-grey-3">
    <q-card-section>
      <Bar id="my-chart-id" :options="chartOptions" :data="chartData" />
    </q-card-section>
  </q-card>
</template>
<script setup>
import { Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
);

const props = defineProps({
  chartData: {
    type: Object,
    default: () => {
      return {
        labels: [
          "January",
          "February",
          "March",
          "April",
          "May",
          "June",
          "July",
        ],
        datasets: [
          {
            label: "Data Kunjungan Per Bulan",
            backgroundColor: "#f87979",
            data: [65, 59, 80, 81, 56, 55, 40],
          },
        ],
      };
    },
  },
});
// const chartData = {
//   labels: ["January", "February", "March", "April", "May", "June", "July"],
//   datasets: [
//     {
//       label: "Data Kunjungan Per Bulan",
//       backgroundColor: "#f87979",
//       data: [65, 59, 80, 81, 56, 55, 40],
//     },
//   ],
// };

const chartOptions = {
  responsive: true,
};
</script>
