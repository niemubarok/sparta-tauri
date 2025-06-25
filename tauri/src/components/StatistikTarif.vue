<template>
  <div class="statistik-tarif">
    <!-- Summary Cards -->
    <div class="row q-gutter-md q-mb-md">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-h6 q-mb-md">Ringkasan Tarif</div>
            <div class="row q-gutter-md">
              <div class="col">
                <div class="text-h4 text-primary">{{ totalTarifRegular }}</div>
                <div class="text-caption">Total Tarif Reguler</div>
              </div>
              <div class="col">
                <div class="text-h4 text-orange">{{ totalTarifInap }}</div>
                <div class="text-caption">Total Tarif Inap</div>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Tariff by Vehicle Type -->
    <div class="row q-gutter-md q-mb-md">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-h6 q-mb-md">Tarif per Jenis Kendaraan</div>
            <q-list>
              <q-item v-for="jenis in jenisKendaraanStats" :key="jenis.id">
                <q-item-section avatar>
                  <q-avatar :color="jenis.color" text-color="white" icon="directions_car" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ jenis.nama }}</q-item-label>
                  <q-item-label caption>
                    {{ jenis.jumlahTarif }} tarif tersedia
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <div class="text-right">
                    <div class="text-subtitle2">{{ formatCurrency(jenis.tarifTerendah) }}</div>
                    <div class="text-caption text-grey-6">Tarif terendah</div>
                  </div>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Price Range Analysis -->
    <div class="row q-gutter-md q-mb-md">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-h6 q-mb-md">Analisis Rentang Harga</div>
            <div class="row q-gutter-md">
              <div class="col-md-4 col-sm-6 col-xs-12">
                <q-card flat class="bg-green-1">
                  <q-card-section class="text-center">
                    <div class="text-h5 text-green">{{ formatCurrency(priceAnalysis.min) }}</div>
                    <div class="text-caption">Tarif Terendah</div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-md-4 col-sm-6 col-xs-12">
                <q-card flat class="bg-blue-1">
                  <q-card-section class="text-center">
                    <div class="text-h5 text-blue">{{ formatCurrency(priceAnalysis.average) }}</div>
                    <div class="text-caption">Tarif Rata-rata</div>
                  </q-card-section>
                </q-card>
              </div>
              <div class="col-md-4 col-sm-6 col-xs-12">
                <q-card flat class="bg-red-1">
                  <q-card-section class="text-center">
                    <div class="text-h5 text-red">{{ formatCurrency(priceAnalysis.max) }}</div>
                    <div class="text-caption">Tarif Tertinggi</div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Hourly Rate Distribution -->
    <div class="row q-gutter-md q-mb-md">
      <div class="col-12">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-h6 q-mb-md">Distribusi Tarif per Jam</div>
            <q-list>
              <q-item v-for="hour in hourlyDistribution" :key="hour.jam_ke">
                <q-item-section>
                  <q-item-label>Jam ke-{{ hour.jam_ke }}</q-item-label>
                </q-item-section>
                <q-item-section>
                  <q-linear-progress
                    :value="hour.percentage / 100"
                    color="primary"
                    size="20px"
                    class="q-mt-sm"
                  >
                    <div class="absolute-full flex flex-center">
                      <q-badge color="white" text-color="primary" :label="`${hour.count} tarif`" />
                    </div>
                  </q-linear-progress>
                </q-item-section>
                <q-item-section side>
                  <div class="text-subtitle2">{{ formatCurrency(hour.averagePrice) }}</div>
                  <div class="text-caption">Rata-rata</div>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Special Tariffs Summary -->
    <div class="row q-gutter-md">
      <div class="col-md-6 col-sm-12">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-h6 q-mb-md">Tarif Inap</div>
            <q-list v-if="tarifInapSummary.length > 0">
              <q-item v-for="inap in tarifInapSummary" :key="inap.id">
                <q-item-section avatar>
                  <q-avatar color="orange" text-color="white" icon="nights_stay" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ inap.nama_jenis }}</q-item-label>
                  <q-item-label caption>
                    {{ formatTime(inap.jam_mulai) }} - {{ formatTime(inap.jam_selesai) }}
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <div class="text-subtitle2">{{ formatCurrency(inap.tarif_inap) }}</div>
                </q-item-section>
              </q-item>
            </q-list>
            <div v-else class="text-center text-grey-6 q-py-md">
              Belum ada tarif inap yang dikonfigurasi
            </div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-md-6 col-sm-12">
        <q-card flat bordered>
          <q-card-section>
            <div class="text-h6 q-mb-md">Tarif Member</div>
            <q-list v-if="tarifMemberSummary.length > 0">
              <q-item v-for="member in tarifMemberSummary" :key="member.id">
                <q-item-section avatar>
                  <q-avatar color="green" text-color="white" icon="card_membership" />
                </q-item-section>
                <q-item-section>
                  <q-item-label>{{ member.nama_jenis }}</q-item-label>
                  <q-item-label caption>
                    {{ member.diskon_persen ? `Diskon ${member.diskon_persen}%` : 'Tarif tetap' }}
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <div class="text-subtitle2">{{ formatCurrency(member.tarif_member) }}</div>
                </q-item-section>
              </q-item>
            </q-list>
            <div v-else class="text-center text-grey-6 q-py-md">
              Belum ada tarif member yang dikonfigurasi
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Refresh Button -->
    <div class="text-center q-mt-md">
      <q-btn
        color="primary"
        icon="refresh"
        label="Refresh Data"
        @click="refreshData"
        :loading="tarifStore.isLoading"
        unelevated
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useTarifStore } from 'src/stores/tarif-store';
import { useKendaraanStore } from 'src/stores/kendaraan-store';

// Store instances
const tarifStore = useTarifStore();
const kendaraanStore = useKendaraanStore();

// Computed properties
const totalTarifRegular = computed(() => tarifStore.activeTarif.length);
const totalTarifInap = computed(() => tarifStore.activeTarifInap.length);

const jenisKendaraanStats = computed(() => {
  const stats = (kendaraanStore.jenisKendaraan || []).map((jenis: any) => {
    const tarifForJenis = (tarifStore.activeTarif || []).filter((t: any) => t.id_mobil === jenis.id);
    const tarifTerendah = tarifForJenis.length > 0 
      ? Math.min(...tarifForJenis.map((t: any) => t.tarif))
      : 0;

    const colors: Record<string, string> = {
      'MTR': 'blue',
      'MBL': 'green',
      'TRK': 'orange',
      'BUS': 'purple',
      'SPD': 'teal'
    };

    return {
      id: jenis.id,
      nama: jenis.jenis,
      jumlahTarif: tarifForJenis.length,
      tarifTerendah,
      color: colors[jenis.id] || 'grey'
    };
  });

  return stats.filter((s: any) => s.jumlahTarif > 0);
});

const priceAnalysis = computed(() => {
  const tarifs = (tarifStore.activeTarif || []).map(t => t.tarif);
  
  if (tarifs.length === 0) {
    return { min: 0, max: 0, average: 0 };
  }

  const min = Math.min(...tarifs);
  const max = Math.max(...tarifs);
  const average = Math.round(tarifs.reduce((a, b) => a + b, 0) / tarifs.length);

  return { min, max, average };
});

const hourlyDistribution = computed(() => {
  const distribution: Record<number, { count: number; total: number }> = {};
  
  // Initialize distribution
  for (let i = 1; i <= 24; i++) {
    distribution[i] = { count: 0, total: 0 };
  }

  // Calculate distribution
  (tarifStore.activeTarif || []).forEach(tarif => {
    distribution[tarif.jam_ke].count++;
    distribution[tarif.jam_ke].total += tarif.tarif;
  });

  const maxCount = Math.max(...Object.values(distribution).map(d => d.count));

  return Object.entries(distribution)
    .filter(([, data]) => data.count > 0)
    .map(([jam_ke, data]) => ({
      jam_ke: parseInt(jam_ke),
      count: data.count,
      averagePrice: Math.round(data.total / data.count),
      percentage: maxCount > 0 ? (data.count / maxCount) * 100 : 0
    }))
    .sort((a, b) => a.jam_ke - b.jam_ke);
});

const tarifInapSummary = computed(() => {
  return (tarifStore.activeTarifInap || []).map((inap: any) => {
    const jenis = (kendaraanStore.jenisKendaraan || []).find((j: any) => j.id === inap.id_mobil);
    return {
      ...inap,
      nama_jenis: jenis?.jenis || inap.id_mobil
    };
  });
});

const tarifMemberSummary = computed(() => {
  return (tarifStore.activeTarifMember || []).map((member: any) => {
    const jenis = (kendaraanStore.jenisKendaraan || []).find((j: any) => j.id === member.id_mobil);
    return {
      ...member,
      nama_jenis: jenis?.jenis || member.id_mobil
    };
  });
});

// Utility functions
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount);
};

const formatTime = (hour: number): string => {
  return `${hour.toString().padStart(2, '0')}:00`;
};

const refreshData = async (): Promise<void> => {
  await tarifStore.loadTarifFromLocal();
  await kendaraanStore.loadJenisKendaraanFromLocal();
};

// Lifecycle
onMounted(async () => {
  await refreshData();
});
</script>

<style scoped>
.statistik-tarif {
  padding: 16px;
}
</style>
