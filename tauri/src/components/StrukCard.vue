<template>
  <div class="struk">
    <div class="struk-item">
      <span class="label">Nomor Struk:</span>
      <span class="value">{{ transaksiStore.nomorStruk }}</span>
    </div>
    <div class="struk-item">
      <span class="label">Plat Nomor:</span>
      <span class="value">{{ transaksiStore.nomorTiket }}</span>
    </div>
    <div class="struk-item">
      <span class="label">Waktu Masuk:</span>
      <span class="value">{{ transaksiStore.waktuMasuk }}</span>
    </div>
    <div class="struk-item">
      <span class="label">Waktu Keluar:</span>
      <span class="value">{{ transaksiStore.waktuKeluar }}</span>
    </div>
    <div class="struk-item">
      <span class="label">Lama Parkir:</span>
      <span class="value">{{ transaksiStore.lamaParkir }}</span>
    </div>
    <button class="cetak-btn" @click="cetakStruk">Cetak</button>
  </div>
</template>

<script setup>
import { useTransaksiStore } from "src/stores/transaksi-store";

const transaksiStore = useTransaksiStore();
</script>

<style scoped>
.struk {
  display: flex;
  flex-direction: column;
}

.struk-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.label {
  font-weight: bold;
}

.cetak-btn {
  margin-top: 20px;
  padding: 10px 20px;
  font-weight: bold;
  background-color: teal;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.cetak-btn:hover {
  background-color: darkcyan;
}
</style>
