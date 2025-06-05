<template>
  <div class="struk">
    <div class="struk-item">
      <q-chip class="label">Nomor Struk</q-chip>
      <q-chip class="value">: {{ transaksiStore.nomorTiket }}</q-chip>
    </div>
    <div class="struk-item">
      <q-chip class="label">Plat Nomor</q-chip>
      <q-chip class="value">: {{ transaksiStore.platNomor }}</q-chip>
    </div>
    <div class="struk-item">
      <q-chip class="label">Waktu Masuk</q-chip>
      <q-chip class="value">: {{ transaksiStore.waktuMasuk }}</q-chip>
    </div>
    <div class="struk-item">
      <q-chip class="label">Waktu Keluar</q-chip>
      <q-chip class="value">: 16:00:00 {{ transaksiStore.waktuKeluar }}</q-chip>
    </div>
    <div class="struk-item">
      <q-chip class="label">Lama Parkir</q-chip>
      <q-chip class="value">: 2 Jam {{ transaksiStore.lamaParkir }}</q-chip>
    </div>
    <div class="struk-item">
      <q-chip class="label">Biaya Parkir</q-chip>
      <q-chip class="value">: {{ transaksiStore.biayaParkir }}</q-chip>
    </div>
  </div>
</template>

<script setup>
import { useTransaksiStore } from "src/stores/transaksi-store";

const transaksiStore = useTransaksiStore();
</script>

<style scoped>
.struk {
  display: flex-start;
  flex-direction: column;
  width: 600px;
}
/* background-color: aliceblue; */

.struk-item {
  display: flex;
  margin-bottom: 10px;
  background-color: transparent;
}

.label {
  font-weight: bold;
  width: 100px;
  background-color: transparent;
}
.value {
  font-weight: bold;
  width: 100px;
  background-color: transparent;
}
</style>
