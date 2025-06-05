<template>
  <q-card
    class="items-center bg-dark q-pa-xs"
    style="max-width: 20vw; height: 80px"
  >
    <!-- style="min-width: 200px" -->
    <q-chip
      class="rounded-corner q-px-lg bg-white text-h4 text-dark justify-center relative full-width"
      style="box-shadow: inset 0px 0px 10px rgba(0, 0, 0, 0.2)"
    >
      <q-badge
        style="top: -10px; left: 7px"
        class="bg-dark text-white absolute-top-left inset-shadow"
        :label="badge"
      />
      <span
        class="full-width text-center text-weight-bolder"
        style="text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5)"
      >
        {{
          plate_number
            ? plate_number.replace(/(\D)(\d+)(\D)/, "$1 $2 $3")
            : ""
        }}
      </span>
    </q-chip>
  </q-card>
</template>

<script setup>
import { useTransaksiStore } from "src/stores/transaksi-store";
const props = defineProps({
  plate_number: {
    type: String,
    required: true,
  },
  badge: {
    type: String,
    default: "ALPR",
  },
});
const transaksiStore = useTransaksiStore();
</script>
