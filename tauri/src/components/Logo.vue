<template>
  <div>
    <img alt="logo" src="~assets/logo_uhamka.webp" style="width: 40vw; height: 50%" />
  </div>
</template>

<!-- <script setup>
// import { useSettingsStore } from "src/stores/settings-store"; // Tidak digunakan
import { ref, onMounted } from "vue";
import axios from "axios";
import { useTransaksiStore } from "src/stores/transaksi-store";

const settingsStore = useSettingsStore();
const transaksiStore = useTransaksiStore();
const logoUrl = ref("");

onMounted(async () => {
  const getPicBodyMasuk = await axios.post(
    transaksiStore.API_URL + "/transactions/pic",
    {
      no_pol: "B000",
    }
  );
  logoUrl.value = getPicBodyMasuk.data;
});
</script> -->
