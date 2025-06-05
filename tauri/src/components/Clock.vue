<template>
  <!-- <div> -->
  <!-- <q-card flat class="bg-transparent">
      <q-card-section> -->
  <q-chip square class="bg-transparent">
    <span class="text-primary text-weight-bolder"> {{ day }}, {{ date }} </span>
  </q-chip>
  <q-chip square class="bg-transparent q-mr-md" style="width: 120px">
    <h4 class="text-weight-bolder text-secondary digital-7">
      {{ hours }}<span class="text-grey">:</span>{{ minutes
      }}<span class="text-grey">:</span>{{ seconds }}
    </h4>
  </q-chip>
  <!-- </q-card-section>
    </q-card> -->
  <!-- {{ dateTime() }} -->
  <!-- </div> -->
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from "vue";
import {
  compareTime,
  getDayName,
  getTime,
  setTime,
} from "src/utils/time-util.js";

const hours = ref(0);
const minutes = ref(0);
const seconds = ref(0);
const date = ref("");
const day = ref("");

const setClock = () => {
  day.value = getTime().day;
  date.value = getTime().fullDate;
  hours.value = getTime().hours;
  minutes.value = getTime().minutes;
  seconds.value = getTime().seconds;
};

setInterval(() => setClock(), 1000);

onBeforeUnmount(() => {
  clearInterval();
});
</script>
