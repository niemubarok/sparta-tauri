<template>
  <div class="calculator-tarif">
    <q-card flat bordered>
      <q-card-section>
        <div class="text-h6 q-mb-md">
          <q-icon name="calculate" class="q-mr-sm" />
          Kalkulator Tarif Parkir
        </div>

        <q-form class="q-gutter-md">
          <div class="row q-gutter-md">
            <div class="col-md-6 col-sm-12">
              <q-select
                v-model="selectedKendaraan"
                :options="jenisKendaraanOptions"
                label="Jenis Kendaraan *"
                outlined
                emit-value
                map-options
                @update:model-value="calculateFee"
              />
            </div>
            
            <div class="col-md-3 col-sm-6 col-xs-12">
              <q-input
                v-model="jamMasuk"
                type="datetime-local"
                label="Jam Masuk *"
                outlined
                @update:model-value="calculateFee"
              />
            </div>
            
            <div class="col-md-3 col-sm-6 col-xs-12">
              <q-input
                v-model="jamKeluar"
                type="datetime-local"
                label="Jam Keluar *"
                outlined
                @update:model-value="calculateFee"
              />
            </div>
          </div>

          <div class="row q-gutter-md">
            <div class="col-md-6 col-sm-12">
              <q-toggle
                v-model="isMember"
                label="Member"
                color="primary"
                @update:model-value="calculateFee"
              />
            </div>
          </div>
        </q-form>
      </q-card-section>

      <!-- Calculation Results -->
      <q-card-section v-if="calculationResult" class="q-pt-none">
        <q-separator class="q-mb-md" />
        
        <div class="text-h6 q-mb-md">Hasil Perhitungan</div>

        <!-- Duration Info -->
        <div class="row q-gutter-md q-mb-md">
          <div class="col">
            <q-card flat bordered class="bg-blue-1">
              <q-card-section class="text-center">
                <div class="text-h4 text-blue">{{ duration.hours }}</div>
                <div class="text-subtitle2">Jam</div>
              </q-card-section>
            </q-card>
          </div>
          <div class="col">
            <q-card flat bordered class="bg-green-1">
              <q-card-section class="text-center">
                <div class="text-h4 text-green">{{ duration.minutes }}</div>
                <div class="text-subtitle2">Menit</div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- Fee Breakdown -->
        <q-card flat bordered class="q-mb-md">
          <q-card-section>
            <div class="text-subtitle1 q-mb-md">Rincian Tarif:</div>
            
            <q-list>
              <q-item v-for="detail in calculationResult.details" :key="detail.jam_ke">
                <q-item-section>
                  <q-item-label>{{ detail.description }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label class="text-weight-medium">
                    {{ formatCurrency(detail.tarif) }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <q-separator class="q-my-sm" />

              <!-- Maximum Per Day Discount -->
              <q-item v-if="calculationResult.isMaxPerHari" class="bg-green-1">
                <q-item-section>
                  <q-item-label class="text-green text-weight-bold">
                    <q-icon name="check_circle" class="q-mr-xs" />
                    Maksimal Tarif Per Hari
                  </q-item-label>
                  <q-item-label caption class="text-green">
                    Biaya dipotong sesuai batas maksimal harian
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label class="text-green text-weight-bold">
                    {{ formatCurrency(calculationResult.maxTarif || 0) }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <!-- Member Discount -->
              <q-item v-if="isMember && memberTarif">
                <q-item-section>
                  <q-item-label class="text-green">Diskon Member</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label class="text-green text-weight-bold">
                    -{{ formatCurrency(calculationResult.totalFee - memberTarif.tarif_member) }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <!-- Overnight Fee -->
              <q-item v-if="calculationResult.isInap">
                <q-item-section>
                  <q-item-label class="text-orange">Tarif Inap</q-item-label>
                  <q-item-label caption>
                    Parkir semalam ({{ formatTime(tarifInap?.jam_mulai) }} - {{ formatTime(tarifInap?.jam_selesai) }})
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label class="text-orange text-weight-bold">
                    {{ formatCurrency(calculationResult.tarifInap || 0) }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-card-section>
        </q-card>

        <!-- Total Fee -->
        <q-card flat bordered :class="calculationResult.isInap ? 'bg-orange-1' : 'bg-primary'">
          <q-card-section class="text-center">
            <div class="text-subtitle1" :class="calculationResult.isInap ? 'text-orange' : 'text-white'">
              Total Biaya Parkir
            </div>
            <div class="text-h4 text-weight-bold" :class="calculationResult.isInap ? 'text-orange' : 'text-white'">
              {{ formatCurrency(finalFee) }}
            </div>
            <div v-if="calculationResult.isInap" class="text-caption text-orange">
              Tarif Inap Berlaku
            </div>
          </q-card-section>
        </q-card>
      </q-card-section>

      <!-- No Calculation Message -->
      <q-card-section v-else class="text-center text-grey-6">
        <q-icon name="info" size="3rem" class="q-mb-md" />
        <div>Pilih jenis kendaraan dan waktu untuk melihat perhitungan tarif</div>
      </q-card-section>
    </q-card>

    <!-- Tarif Reference -->
    <q-card flat bordered class="q-mt-md" v-if="selectedKendaraan">
      <q-card-section>
        <div class="text-subtitle1 q-mb-md">Referensi Tarif - {{ getJenisKendaraanName(selectedKendaraan) }}</div>
        
        <div class="row q-gutter-md">
          <!-- Regular Tariff -->
          <div class="col-md-6 col-sm-12">
            <q-list bordered separator>
              <q-item-label header>Tarif Normal</q-item-label>
              <q-item v-for="tarif in regularTariffs" :key="tarif.jam_ke">
                <q-item-section>
                  <q-item-label>Jam ke-{{ tarif.jam_ke }}</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label>{{ formatCurrency(tarif.tarif) }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <!-- Special Tariffs -->
          <div class="col-md-6 col-sm-12">
            <q-list bordered separator>
              <q-item-label header>Tarif Khusus</q-item-label>
              
              <q-item v-if="memberTarif">
                <q-item-section>
                  <q-item-label>Tarif Member</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label class="text-green">
                    {{ formatCurrency(memberTarif.tarif_member) }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <q-item v-if="tarifInap">
                <q-item-section>
                  <q-item-label>Tarif Inap</q-item-label>
                  <q-item-label caption>
                    {{ formatTime(tarifInap.jam_mulai) }} - {{ formatTime(tarifInap.jam_selesai) }}
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label class="text-orange">
                    {{ formatCurrency(tarifInap.tarif_inap) }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <q-item v-if="!memberTarif && !tarifInap">
                <q-item-section>
                  <q-item-label class="text-grey-6">
                    Tidak ada tarif khusus
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </div>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useTarifStore } from 'src/stores/tarif-store';
import { useKendaraanStore } from 'src/stores/kendaraan-store';

// Store instances
const tarifStore = useTarifStore();
const kendaraanStore = useKendaraanStore();

// Reactive state
const selectedKendaraan = ref<string>('');
const jamMasuk = ref<string>('');
const jamKeluar = ref<string>('');
const isMember = ref<boolean>(false);
const calculationResult = ref<any>(null);

// Set default values
const now = new Date();
const oneHourLater = new Date(now.getTime() + 60 * 60 * 1000);

jamMasuk.value = now.toISOString().slice(0, 16);
jamKeluar.value = oneHourLater.toISOString().slice(0, 16);

// Computed properties
const jenisKendaraanOptions = computed(() => 
  kendaraanStore.jenisKendaraanForSelect
);

const duration = computed(() => {
  if (!jamMasuk.value || !jamKeluar.value) {
    return { hours: 0, minutes: 0 };
  }

  const masuk = new Date(jamMasuk.value);
  const keluar = new Date(jamKeluar.value);
  const diffMs = keluar.getTime() - masuk.getTime();
  const diffMins = Math.max(0, Math.ceil(diffMs / (1000 * 60)));

  return {
    hours: Math.floor(diffMins / 60),
    minutes: diffMins % 60
  };
});

const regularTariffs = computed(() => {
  if (!selectedKendaraan.value) return [];
  return tarifStore.getTarifByMobil(selectedKendaraan.value);
});

const memberTarif = computed(() => {
  if (!selectedKendaraan.value) return null;
  return tarifStore.getTarifMember(selectedKendaraan.value);
});

const tarifInap = computed(() => {
  if (!selectedKendaraan.value) return null;
  return (tarifStore.activeTarifInap || []).find(t => t.id_mobil === selectedKendaraan.value);
});

const finalFee = computed(() => {
  if (!calculationResult.value) return 0;
  
  let fee = calculationResult.value.totalFee;
  
  // Apply member discount
  if (isMember.value && memberTarif.value) {
    fee = memberTarif.value.tarif_member;
  }
  
  return fee;
});

// Utility functions
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount);
};

const formatTime = (hour: number | undefined): string => {
  if (hour === undefined) return '-';
  return `${hour.toString().padStart(2, '0')}:00`;
};

const getJenisKendaraanName = (id: string): string => {
  const jenis = (kendaraanStore.jenisKendaraan || []).find((j: any) => j.id === id);
  return jenis?.jenis || id;
};

const calculateFee = (): void => {
  if (!selectedKendaraan.value || !jamMasuk.value || !jamKeluar.value) {
    calculationResult.value = null;
    return;
  }

  const masuk = new Date(jamMasuk.value);
  const keluar = new Date(jamKeluar.value);

  if (keluar <= masuk) {
    calculationResult.value = null;
    return;
  }

  calculationResult.value = tarifStore.calculateParkingFee(
    selectedKendaraan.value,
    masuk,
    keluar
  );
};

// Watch for changes to recalculate
watch([selectedKendaraan, jamMasuk, jamKeluar, isMember], () => {
  calculateFee();
});

// Lifecycle
onMounted(async () => {
  await tarifStore.loadTarifFromLocal();
  await kendaraanStore.loadJenisKendaraanFromLocal();
  
  // Set default vehicle if available
  if (kendaraanStore.jenisKendaraanForSelect.length > 0) {
    selectedKendaraan.value = kendaraanStore.jenisKendaraanForSelect[0].value;
  }
  
  calculateFee();
});
</script>

<style scoped>
.calculator-tarif {
  padding: 16px;
}
</style>
