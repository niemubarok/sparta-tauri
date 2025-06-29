<template>
  <div>
    <!-- v-if="$q.screen.gt.sm" -->
    <q-chip
      flat
      class="text-h4 text-weight-bolder bg-yellow-5 text-blue-5"
      label="UHAMKA"
    />
  </div>
</template>

<script setup>

import { onMounted } from "vue";
import ls from "localstorage-slim";

// const settingsStore = useSettingsStore(); // Tidak digunakan, companyName diambil dari process.env
const companyName = process.env.COMPANY_NAME?.toUpperCase()

onMounted(async () => {});
</script>
