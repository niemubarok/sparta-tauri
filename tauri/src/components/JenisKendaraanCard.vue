<template>
  <div class="row q-gutter-lg justify-center" style="height: fit-content">
    <q-card
      class="cursor-pointer listCard bg-primary"
      @click="jenisKendaraan = 'mobil'"
    >
      <q-card-section>
        <q-icon name="directions_car" class="text-white" size="15em"></q-icon>
        <div class="text-white">Mobil</div>
      </q-card-section>
    </q-card>

    <q-card
      class="cursor-pointer listCard bg-teal"
      @click="jenisKendaraan = 'motor'"
    >
      <q-card-section>
        <q-icon name="two_wheeler" class="text-white" size="15em" />
        <div class="text-white">Motor</div>
      </q-card-section>
    </q-card>

    <q-card
      class="cursor-pointer listCard bg-orange"
      @click="jenisKendaraan = 'truk'"
    >
      <q-card-section>
        <q-icon name="local_shipping" class="text-white" size="15em" />
        <div class="text-white">Truk / Box</div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref } from "vue";

const selectedJenisKendaraan = ref("");
</script>
