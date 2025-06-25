<template>
  <q-page padding>
    <div class="q-pa-md">
      <q-card>
        <q-tabs
          v-model="tab"
          dense
          class="text-grey"
          active-color="primary"
          indicator-color="primary"
          align="justify"
          narrow-indicator
        >
          <q-tab name="jenis" label="Jenis Kendaraan" icon="directions_car" />
          <q-tab name="blacklist" label="Blacklist Kendaraan" icon="block" />
        </q-tabs>

        <q-separator />

        <q-tab-panels v-model="tab" animated>
          <q-tab-panel name="jenis">
            <daftar-jenis-kendaraan />
          </q-tab-panel>

          <q-tab-panel name="blacklist">
            <blacklist-kendaraan />
          </q-tab-panel>
        </q-tab-panels>
      </q-card>
    </div>
  </q-page>
</template>

<script setup>
import { ref } from 'vue';
import DaftarJenisKendaraan from "src/components/DaftarJenisKendaraan.vue";
import BlacklistKendaraan from "src/components/BlacklistKendaraan.vue";

const tab = ref('jenis');
</script>
