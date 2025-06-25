<template>
  <q-page class="tarif-page">
    <div class="q-pa-md">
      <!-- Page Header -->
      <div class="row items-center q-mb-lg">
        <div class="col">
          <div class="text-h4 text-weight-bold">
            <q-icon name="attach_money" class="q-mr-sm" />
            Manajemen Tarif
          </div>
          <div class="text-subtitle1 text-grey-7">
            Kelola semua jenis tarif parkir dan simulasi perhitungan
          </div>
        </div>
        <div class="col-auto">
          <q-btn
            color="grey-8"
            icon="home"
            label="Home"
            to="/"
            unelevated
            class="q-mr-sm"
          />
          <q-btn
            color="primary"
            icon="analytics"
            label="Statistik Tarif"
            @click="showStatistics = true"
            unelevated
            class="q-mr-sm"
          />
        </div>
      </div>

      <!-- Navigation Tabs -->
      <q-tabs
        v-model="currentTab"
        dense
        class="text-grey"
        active-color="primary"
        indicator-color="primary"
        align="justify"
        narrow-indicator
      >
        <q-tab name="regular" label="Tarif Reguler" icon="schedule" />
        <q-tab name="bertingkat" label="Tarif Bertingkat" icon="trending_up" />
        <q-tab name="prepaid" label="Tarif Prepaid" icon="payments" />
        <q-tab name="demo" label="Demo Bertingkat" icon="timeline" />
        <q-tab name="inap" label="Tarif Inap" icon="nights_stay" />
        <q-tab name="calculator" label="Kalkulator" icon="calculate" />
      </q-tabs>

      <q-separator />

      <!-- Tab Panels -->
      <q-tab-panels v-model="currentTab" animated>
        <!-- Regular Tariff Panel -->
        <q-tab-panel name="regular" class="q-pa-none">
          <DaftarTarif />
        </q-tab-panel>

        <!-- Tariff Bertingkat Management Panel -->
        <q-tab-panel name="bertingkat" class="q-pa-none">
          <TarifBertingkatManagement />
        </q-tab-panel>

        <!-- Prepaid Tariff Management Panel -->
        <q-tab-panel name="prepaid" class="q-pa-none">
          <TarifPrepaidManagement />
        </q-tab-panel>

        <!-- Demo Tariff Panel -->
        <q-tab-panel name="demo" class="q-pa-none">
          <DemoTarifBertingkat />
        </q-tab-panel>

        <!-- Overnight Tariff Panel -->
        <q-tab-panel name="inap" class="q-pa-none">
          <TarifInap />
        </q-tab-panel>

        <!-- Calculator Panel -->
        <q-tab-panel name="calculator" class="q-pa-none">
          <CalculatorTarif />
        </q-tab-panel>
      </q-tab-panels>
    </div>

    <!-- Statistics Dialog -->
    <q-dialog v-model="showStatistics" position="right" full-height>
      <q-card style="width: 400px">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Statistik Tarif</div>
          <q-space />
          <q-btn icon="close" flat round dense @click="showStatistics = false" />
        </q-card-section>

        <q-card-section>
          <StatistikTarif />
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useTarifStore } from 'src/stores/tarif-store';
import DaftarTarif from 'src/components/DaftarTarif.vue';
import TarifBertingkatManagement from 'src/components/TarifBertingkatManagement.vue';
import TarifPrepaidManagement from 'src/components/TarifPrepaidManagement.vue';
import DemoTarifBertingkat from 'src/components/DemoTarifBertingkat.vue';
import TarifInap from 'src/components/TarifInap.vue';
import CalculatorTarif from 'src/components/CalculatorTarif.vue';
import StatistikTarif from 'src/components/StatistikTarif.vue';

// Store instance
const tarifStore = useTarifStore();

// Reactive state
const currentTab = ref('regular');
const showStatistics = ref(false);

// Lifecycle
onMounted(async () => {
  await tarifStore.loadTarifFromLocal();
});
</script>

<style scoped>
.tarif-page {
  background-color: #f5f5f5;
}
</style>
