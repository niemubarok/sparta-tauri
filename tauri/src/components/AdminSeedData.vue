<template>
  <q-card class="q-ma-md">
    <q-card-section>
      <div class="text-h6 q-mb-md">
        <q-icon name="database" class="q-mr-sm" />
        Seed Data Management
      </div>
      <div class="text-caption text-grey-7 q-mb-md">
        Initialize database with default data. Use this only for initial setup or development.
      </div>
    </q-card-section>

    <q-card-section>
      <div class="row q-gutter-md">
        <!-- Petugas Seed -->
        <div class="col-12 col-md-5">
          <q-card bordered flat>
            <q-card-section>
              <div class="text-subtitle1 q-mb-sm">
                <q-icon name="person" class="q-mr-sm" />
                Petugas & Level Data
              </div>
              <div class="text-caption text-grey-7 q-mb-md">
                Creates default users and user levels
              </div>
              <q-list dense>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>• Administrator (admin/admin123)</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>• Petugas (petugas1/petugas123)</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>• Supervisor (supervisor/supervisor123)</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>• 4 User levels (ADM, SPV, PGS, CST)</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
              
              <div class="q-mt-md">
                <q-btn
                  color="primary"
                  label="Seed Petugas Data"
                  icon="person_add"
                  :loading="loadingPetugas"
                  @click="seedPetugasData"
                  class="full-width"
                />
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Kendaraan Seed -->
        <div class="col-12 col-md-6">
          <q-card bordered flat>
            <q-card-section>
              <div class="text-subtitle1 q-mb-sm">
                <q-icon name="directions_car" class="q-mr-sm" />
                Kendaraan Data
              </div>
              <div class="text-caption text-grey-7 q-mb-md">
                Creates vehicle types and sample blacklist
              </div>
              <q-list dense>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>• 5 Vehicle types (Motor, Mobil, Truk, Bus, Sepeda)</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>• Sample blacklist entries</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
              
              <div class="q-mt-md q-gutter-sm">
                <q-btn
                  color="positive"
                  label="Seed Vehicle Types"
                  icon="directions_car"
                  :loading="loadingKendaraan"
                  @click="seedKendaraanOnly"
                  class="full-width"
                />
                <q-btn
                  color="orange"
                  label="Seed All Kendaraan Data"
                  icon="local_parking"
                  :loading="loadingAllKendaraan"
                  @click="seedAllKendaraan"
                  class="full-width"
                />
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Tarif Seed -->
        <div class="col-12 col-md-6">
          <q-card bordered flat>
            <q-card-section>
              <div class="text-subtitle1 q-mb-sm">
                <q-icon name="attach_money" class="q-mr-sm" />
                Tarif Data
              </div>
              <div class="text-caption text-grey-7 q-mb-md">
                Creates parking tariffs for all vehicle types
              </div>
              <q-list dense>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>• Hourly tariffs (1-3 hours) for all vehicles</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>• Progressive pricing structure</q-item-label>
                  </q-item-section>
                </q-item>
                <q-item>
                  <q-item-section>
                    <q-item-label caption>• Penalty rates included</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
              
              <div class="q-mt-md">
                <q-btn
                  color="green"
                  label="Seed Tarif Data"
                  icon="attach_money"
                  :loading="loadingTarif"
                  @click="seedTarifData"
                  class="full-width"
                />
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Seed All Button -->
      <div class="row q-mt-md">
        <div class="col-12">
          <q-separator class="q-my-md" />
          <q-btn
            color="secondary"
            label="Seed All Data (Petugas + Kendaraan + Tarif)"
            icon="storage"
            size="lg"
            :loading="loadingAll"
            @click="seedAllData"
            class="full-width"
          />
        </div>
      </div>

      <!-- Status Section -->
      <div class="row q-mt-md" v-if="lastSeedResult">
        <div class="col-12">
          <q-separator class="q-my-md" />
          <q-banner 
            :class="lastSeedResult.success ? 'bg-green-1 text-green-8' : 'bg-red-1 text-red-8'"
            :icon="lastSeedResult.success ? 'check_circle' : 'error'"
            rounded
          >
            <div class="text-subtitle2">{{ lastSeedResult.title }}</div>
            <div class="text-caption">{{ lastSeedResult.message }}</div>
            <div class="text-caption text-grey-6">{{ lastSeedResult.timestamp }}</div>
          </q-banner>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref } from 'vue';
import { useQuasar } from 'quasar';
import { usePetugasStore } from 'src/stores/petugas-store';
import { useKendaraanStore } from 'src/stores/kendaraan-store';
import { useTarifStore } from 'src/stores/tarif-store';

const $q = useQuasar();
const petugasStore = usePetugasStore();
const kendaraanStore = useKendaraanStore();
const tarifStore = useTarifStore();

const loadingPetugas = ref(false);
const loadingKendaraan = ref(false);
const loadingAllKendaraan = ref(false);
const loadingTarif = ref(false);
const loadingAll = ref(false);

const lastSeedResult = ref(null);

const showResult = (success, title, message) => {
  lastSeedResult.value = {
    success,
    title,
    message,
    timestamp: new Date().toLocaleString()
  };
};

const seedPetugasData = async () => {
  loadingPetugas.value = true;
  try {
    await petugasStore.seedLevelData();
    await petugasStore.seedPetugasData();
    
    $q.notify({
      type: 'positive',
      message: 'Petugas data seeded successfully',
      icon: 'check'
    });
    
    showResult(true, 'Petugas Data Seeded', 'Successfully created default users and levels');
  } catch (error) {
    console.error('Error seeding petugas data:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to seed petugas data',
      caption: error.message,
      icon: 'error'
    });
    
    showResult(false, 'Petugas Seed Failed', error.message);
  } finally {
    loadingPetugas.value = false;
  }
};

const seedKendaraanOnly = async () => {
  loadingKendaraan.value = true;
  try {
    await kendaraanStore.seedKendaraanData();
    
    $q.notify({
      type: 'positive',
      message: 'Vehicle types seeded successfully',
      icon: 'check'
    });
    
    showResult(true, 'Vehicle Types Seeded', 'Successfully created default vehicle types');
  } catch (error) {
    console.error('Error seeding kendaraan data:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to seed vehicle types',
      caption: error.message,
      icon: 'error'
    });
    
    showResult(false, 'Vehicle Types Seed Failed', error.message);
  } finally {
    loadingKendaraan.value = false;
  }
};

const seedAllKendaraan = async () => {
  loadingAllKendaraan.value = true;
  try {
    await kendaraanStore.seedAllKendaraanData();
    
    $q.notify({
      type: 'positive',
      message: 'All kendaraan data seeded successfully',
      icon: 'check'
    });
    
    showResult(true, 'All Kendaraan Data Seeded', 'Successfully created vehicle types, tariffs, and sample blacklist');
  } catch (error) {
    console.error('Error seeding all kendaraan data:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to seed kendaraan data',
      caption: error.message,
      icon: 'error'
    });
    
    showResult(false, 'Kendaraan Seed Failed', error.message);
  } finally {
    loadingAllKendaraan.value = false;
  }
};

const seedAllData = async () => {
  loadingAll.value = true;
  try {
    // Seed petugas first
    await petugasStore.seedLevelData();
    await petugasStore.seedPetugasData();
    
    // Then seed kendaraan
    await kendaraanStore.seedAllKendaraanData();
    
    // Finally seed tarif
    await tarifStore.seedTarifData();
    
    $q.notify({
      type: 'positive',
      message: 'All seed data created successfully',
      icon: 'check'
    });
    
    showResult(true, 'All Data Seeded', 'Successfully created all default data for the application');
  } catch (error) {
    console.error('Error seeding all data:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to seed all data',
      caption: error.message,
      icon: 'error'
    });
    
    showResult(false, 'All Data Seed Failed', error.message);
  } finally {
    loadingAll.value = false;
  }
};

const seedTarifData = async () => {
  loadingTarif.value = true;
  try {
    await tarifStore.seedTarifData();
    
    $q.notify({
      type: 'positive',
      message: 'Tarif data seeded successfully',
      icon: 'check'
    });
    
    showResult(true, 'Tarif Data Seeded', 'Successfully created default parking tariffs for all vehicle types');
  } catch (error) {
    console.error('Error seeding tarif data:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to seed tarif data',
      caption: error.message,
      icon: 'error'
    });
    
    showResult(false, 'Tarif Seed Failed', error.message);
  } finally {
    loadingTarif.value = false;
  }
};
</script>
