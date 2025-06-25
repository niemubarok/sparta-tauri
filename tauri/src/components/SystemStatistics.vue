<template>
  <q-card>
    <q-card-section>
      <div class="text-h6 q-mb-md">
        <q-icon name="analytics" class="q-mr-sm" />
        System Statistics
      </div>
      
      <div class="row q-gutter-md">
        <!-- Petugas Statistics -->
        <div class="col-12 col-md-5">
          <q-card bordered flat class="bg-blue-1">
            <q-card-section>
              <div class="text-subtitle1 text-blue-8 q-mb-sm">
                <q-icon name="person" class="q-mr-sm" />
                Petugas Statistics
              </div>
              
              <div class="row q-gutter-sm">
                <div class="col">
                  <q-chip color="primary" text-color="white" icon="group">
                    Total: {{ petugasStats.total }}
                  </q-chip>
                </div>
                <div class="col">
                  <q-chip color="green" text-color="white" icon="check_circle">
                    Active: {{ petugasStats.active }}
                  </q-chip>
                </div>
                <div class="col">
                  <q-chip color="red" text-color="white" icon="cancel">
                    Inactive: {{ petugasStats.inactive }}
                  </q-chip>
                </div>
              </div>

              <q-separator class="q-my-sm" />
              
              <div class="text-caption text-grey-7 q-mb-xs">By Level:</div>
              <div class="row q-gutter-xs">
                <q-chip 
                  v-for="level in petugasStats.byLevel" 
                  :key="level.level"
                  dense
                  outline
                  color="blue-8"
                  :label="`${level.level}: ${level.count}`"
                />
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Kendaraan Statistics -->
        <div class="col-12 col-md-6">
          <q-card bordered flat class="bg-orange-1">
            <q-card-section>
              <div class="text-subtitle1 text-orange-8 q-mb-sm">
                <q-icon name="directions_car" class="q-mr-sm" />
                Kendaraan Statistics
              </div>
              
              <div class="row q-gutter-sm q-mb-sm">
                <div class="col">
                  <q-chip color="orange" text-color="white" icon="directions_car">
                    Types: {{ kendaraanStats.activeJenis }}
                  </q-chip>
                </div>
                <div class="col">
                  <q-chip color="red-8" text-color="white" icon="block">
                    Blacklist: {{ kendaraanStats.activeBlacklist }}
                  </q-chip>
                </div>
              </div>

              <q-separator class="q-my-sm" />
              
              <div class="text-caption text-grey-7 q-mb-xs">Average Tariff:</div>
              <q-chip 
                color="green-8" 
                text-color="white" 
                icon="attach_money"
                :label="`Rp ${kendaraanStats.avgTarif.toLocaleString()}`"
              />
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Tarif Statistics Row -->
      <div class="row q-mt-md">
        <div class="col-12">
          <q-card bordered flat class="bg-green-1">
            <q-card-section>
              <div class="text-subtitle1 text-green-8 q-mb-sm">
                <q-icon name="attach_money" class="q-mr-sm" />
                Tarif Statistics
              </div>
              
              <div class="row q-gutter-sm">
                <div class="col-auto">
                  <q-chip color="green" text-color="white" icon="schedule">
                    Regular: {{ tarifStats.totalRegular }}
                  </q-chip>
                </div>
                <div class="col-auto">
                  <q-chip color="orange" text-color="white" icon="nights_stay">
                    Inap: {{ tarifStats.totalInap }}
                  </q-chip>
                </div>
                <div class="col-auto">
                  <q-chip color="blue" text-color="white" icon="card_membership">
                    Member: {{ tarifStats.totalMember }}
                  </q-chip>
                </div>
                <div class="col-auto">
                  <q-chip color="purple" text-color="white" icon="money">
                    Min: {{ formatCurrency(tarifStats.minTarif) }}
                  </q-chip>
                </div>
                <div class="col-auto">
                  <q-chip color="red" text-color="white" icon="trending_up">
                    Max: {{ formatCurrency(tarifStats.maxTarif) }}
                  </q-chip>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Additional Stats Row -->
      <div class="row q-mt-md">
        <div class="col-12">
          <q-card bordered flat class="bg-grey-1">
            <q-card-section>
              <div class="text-subtitle1 q-mb-sm">
                <q-icon name="timeline" class="q-mr-sm" />
                Quick Actions
              </div>
              
              <div class="row q-gutter-sm">
                <q-btn
                  color="primary"
                  icon="refresh"
                  label="Refresh Stats"
                  @click="refreshStats"
                  :loading="loading"
                />
                <q-btn
                  color="secondary"
                  icon="person_add"
                  label="Add Petugas"
                  @click="$router.push('/petugas')"
                />
                <q-btn
                  color="orange"
                  icon="add_road"
                  label="Add Vehicle Type"
                  @click="$router.push('/kendaraan')"
                />
                <q-btn
                  color="green"
                  icon="attach_money"
                  label="Manage Tarif"
                  @click="$router.push('/tarif')"
                />
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { usePetugasStore } from 'src/stores/petugas-store';
import { useKendaraanStore } from 'src/stores/kendaraan-store';
import { useTarifStore } from 'src/stores/tarif-store';

const $q = useQuasar();
const petugasStore = usePetugasStore();
const kendaraanStore = useKendaraanStore();
const tarifStore = useTarifStore();

const loading = ref(false);

const petugasStats = computed(() => petugasStore.getPetugasStatistics);
const kendaraanStats = computed(() => kendaraanStore.getKendaraanStatistics);

const tarifStats = computed(() => {
  const regular = tarifStore.activeTarif;
  const inap = tarifStore.activeTarifInap;
  const member = tarifStore.activeTarifMember;
  
  const allTarifs = regular.map(t => t.tarif);
  
  return {
    totalRegular: regular.length,
    totalInap: inap.length,
    totalMember: member.length,
    minTarif: allTarifs.length > 0 ? Math.min(...allTarifs) : 0,
    maxTarif: allTarifs.length > 0 ? Math.max(...allTarifs) : 0
  };
});

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount);
};

const refreshStats = async () => {
  loading.value = true;
  try {
    await petugasStore.loadFromLocal();
    await kendaraanStore.loadJenisKendaraanFromLocal();
    await kendaraanStore.getAllBlacklist();
    await tarifStore.loadTarifFromLocal();
    
    $q.notify({
      type: 'positive',
      message: 'Statistics refreshed successfully',
      icon: 'refresh'
    });
  } catch (error) {
    console.error('Error refreshing stats:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to refresh statistics',
      icon: 'error'
    });
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  // Stats will be loaded by parent component
});
</script>
