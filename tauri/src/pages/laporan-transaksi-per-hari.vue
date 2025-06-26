<template>
  <q-page padding>
    <div class="q-mb-md">
      <q-btn 
        icon="home" 
        label="Kembali ke Home" 
        color="primary" 
        to="/"
      />
    </div>
    <LaporanTransaksiPertanggal />
  </q-page>
</template>

<script setup>
import LaporanTransaksiPertanggal from "src/components/LaporanTransaksiPertanggal.vue";
</script>
