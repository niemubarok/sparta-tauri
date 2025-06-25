<template>
  <div class="demo-tarif-bertingkat">
    <q-card flat bordered>
      <q-card-section>
        <div class="text-h6 q-mb-md">
          <q-icon name="timeline" class="q-mr-sm" />
          Demo Tarif Bertingkat & Maksimal Per Hari
        </div>

        <!-- Example Cases -->
        <div class="row q-gutter-md">
          <!-- Motor Case -->
          <div class="col-md-4 col-sm-6 col-xs-12">
            <q-card flat bordered class="bg-blue-1">
              <q-card-section>
                <div class="text-subtitle1 text-weight-bold text-blue">
                  <q-icon name="motorcycle" class="q-mr-xs" />
                  Motor (MTR)
                </div>
                <div class="text-caption text-grey-7 q-mb-md">
                  Contoh tarif bertingkat dengan maksimal per hari
                </div>

                <q-list dense separator>
                  <q-item>
                    <q-item-section>
                      <q-item-label>Jam ke-1</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-item-label class="text-weight-bold">Rp 3.000</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label>Jam ke-2 dst</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-item-label class="text-weight-bold">Rp 1.000</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item class="bg-green-1">
                    <q-item-section>
                      <q-item-label class="text-green text-weight-bold">
                        <q-icon name="check_circle" size="xs" class="q-mr-xs" />
                        Max Per Hari
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-item-label class="text-green text-weight-bold">Rp 15.000</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>

                <q-btn 
                  @click="testMotor" 
                  color="blue" 
                  label="Test 8 Jam" 
                  size="sm" 
                  class="q-mt-md"
                  :loading="loadingMotor"
                  unelevated
                />
              </q-card-section>
            </q-card>
          </div>

          <!-- Mobil Case -->
          <div class="col-md-4 col-sm-6 col-xs-12">
            <q-card flat bordered class="bg-orange-1">
              <q-card-section>
                <div class="text-subtitle1 text-weight-bold text-orange">
                  <q-icon name="directions_car" class="q-mr-xs" />
                  Mobil (MBL)
                </div>
                <div class="text-caption text-grey-7 q-mb-md">
                  Tarif bertingkat dengan batas maksimal berbeda
                </div>

                <q-list dense separator>
                  <q-item>
                    <q-item-section>
                      <q-item-label>Jam ke-1</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-item-label class="text-weight-bold">Rp 5.000</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label>Jam ke-2 dst</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-item-label class="text-weight-bold">Rp 2.000</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item class="bg-green-1">
                    <q-item-section>
                      <q-item-label class="text-green text-weight-bold">
                        <q-icon name="check_circle" size="xs" class="q-mr-xs" />
                        Max Per Hari
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-item-label class="text-green text-weight-bold">Rp 25.000</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>

                <q-btn 
                  @click="testMobil" 
                  color="orange" 
                  label="Test 12 Jam" 
                  size="sm" 
                  class="q-mt-md"
                  :loading="loadingMobil"
                  unelevated
                />
              </q-card-section>
            </q-card>
          </div>

          <!-- Bus Case -->
          <div class="col-md-4 col-sm-6 col-xs-12">
            <q-card flat bordered class="bg-purple-1">
              <q-card-section>
                <div class="text-subtitle1 text-weight-bold text-purple">
                  <q-icon name="directions_bus" class="q-mr-xs" />
                  Bus (BUS)
                </div>
                <div class="text-caption text-grey-7 q-mb-md">
                  Tarif progresif dengan maksimal tertinggi
                </div>

                <q-list dense separator>
                  <q-item>
                    <q-item-section>
                      <q-item-label>Jam ke-1</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-item-label class="text-weight-bold">Rp 10.000</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label>Jam ke-2 dst</q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-item-label class="text-weight-bold">Rp 5.000</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item class="bg-green-1">
                    <q-item-section>
                      <q-item-label class="text-green text-weight-bold">
                        <q-icon name="check_circle" size="xs" class="q-mr-xs" />
                        Max Per Hari
                      </q-item-label>
                    </q-item-section>
                    <q-item-section side>
                      <q-item-label class="text-green text-weight-bold">Rp 50.000</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>

                <q-btn 
                  @click="testBus" 
                  color="purple" 
                  label="Test 15 Jam" 
                  size="sm" 
                  class="q-mt-md"
                  :loading="loadingBus"
                  unelevated
                />
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- Results -->
        <div v-if="testResult" class="q-mt-lg">
          <q-card flat bordered>
            <q-card-section>
              <div class="text-h6 q-mb-md">
                <q-icon name="receipt" class="q-mr-sm" />
                Hasil Perhitungan: {{ testResult.vehicleType }}
              </div>

              <div class="row q-gutter-md">
                <div class="col-md-6">
                  <q-list bordered separator>
                    <q-item-label header>Detail Tarif per Jam</q-item-label>
                    <q-item v-for="detail in testResult.details" :key="detail.jam_ke">
                      <q-item-section>
                        <q-item-label>{{ detail.description }}</q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-item-label class="text-weight-medium">
                          {{ formatCurrency(detail.tarif) }}
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </div>

                <div class="col-md-6">
                  <q-card flat bordered :class="testResult.isMaxPerHari ? 'bg-green-1' : 'bg-blue-1'">
                    <q-card-section>
                      <div class="text-center">
                        <div class="text-subtitle1" :class="testResult.isMaxPerHari ? 'text-green' : 'text-blue'">
                          {{ testResult.isMaxPerHari ? 'Dengan Maksimal Per Hari' : 'Tarif Normal' }}
                        </div>
                        <div class="text-h4 text-weight-bold" :class="testResult.isMaxPerHari ? 'text-green' : 'text-blue'">
                          {{ formatCurrency(testResult.totalFee) }}
                        </div>
                        <div v-if="testResult.isMaxPerHari" class="text-caption text-green">
                          Hemat {{ formatCurrency(testResult.savedAmount) }}!
                        </div>
                      </div>
                    </q-card-section>
                  </q-card>

                  <div class="q-mt-md text-caption text-grey-6">
                    <div><strong>Durasi:</strong> {{ testResult.duration }} jam</div>
                    <div><strong>Waktu Masuk:</strong> {{ formatDateTime(testResult.jamMasuk) }}</div>
                    <div><strong>Waktu Keluar:</strong> {{ formatDateTime(testResult.jamKeluar) }}</div>
                  </div>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useTarifStore } from 'src/stores/tarif-store';

// Store instance
const tarifStore = useTarifStore();

// Reactive state
const loadingMotor = ref(false);
const loadingMobil = ref(false);
const loadingBus = ref(false);
const testResult = ref<any>(null);

// Test functions
const testMotor = async () => {
  loadingMotor.value = true;
  try {
    const jamMasuk = new Date();
    jamMasuk.setHours(8, 0, 0, 0); // 08:00
    const jamKeluar = new Date(jamMasuk);
    jamKeluar.setHours(16, 0, 0, 0); // 16:00 (8 jam)
    
    const result = tarifStore.calculateParkingFee('MTR', jamMasuk, jamKeluar);
    
    // Calculate saved amount if max per day applied
    const normalTotal = result.details.reduce((sum, detail) => sum + detail.tarif, 0);
    const savedAmount = result.isMaxPerHari ? normalTotal - result.totalFee : 0;
    
    testResult.value = {
      vehicleType: 'Motor (MTR)',
      duration: 8,
      jamMasuk,
      jamKeluar,
      ...result,
      savedAmount
    };
  } finally {
    loadingMotor.value = false;
  }
};

const testMobil = async () => {
  loadingMobil.value = true;
  try {
    const jamMasuk = new Date();
    jamMasuk.setHours(7, 0, 0, 0); // 07:00
    const jamKeluar = new Date(jamMasuk);
    jamKeluar.setHours(19, 0, 0, 0); // 19:00 (12 jam)
    
    const result = tarifStore.calculateParkingFee('MBL', jamMasuk, jamKeluar);
    
    // Calculate saved amount if max per day applied
    const normalTotal = result.details.reduce((sum, detail) => sum + detail.tarif, 0);
    const savedAmount = result.isMaxPerHari ? normalTotal - result.totalFee : 0;
    
    testResult.value = {
      vehicleType: 'Mobil (MBL)',
      duration: 12,
      jamMasuk,
      jamKeluar,
      ...result,
      savedAmount
    };
  } finally {
    loadingMobil.value = false;
  }
};

const testBus = async () => {
  loadingBus.value = true;
  try {
    const jamMasuk = new Date();
    jamMasuk.setHours(6, 0, 0, 0); // 06:00
    const jamKeluar = new Date(jamMasuk);
    jamKeluar.setHours(21, 0, 0, 0); // 21:00 (15 jam)
    
    const result = tarifStore.calculateParkingFee('BUS', jamMasuk, jamKeluar);
    
    // Calculate saved amount if max per day applied
    const normalTotal = result.details.reduce((sum, detail) => sum + detail.tarif, 0);
    const savedAmount = result.isMaxPerHari ? normalTotal - result.totalFee : 0;
    
    testResult.value = {
      vehicleType: 'Bus (BUS)',
      duration: 15,
      jamMasuk,
      jamKeluar,
      ...result,
      savedAmount
    };
  } finally {
    loadingBus.value = false;
  }
};

// Utility functions
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount);
};

const formatDateTime = (date: Date): string => {
  return new Intl.DateTimeFormat('id-ID', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};
</script>

<style scoped>
.demo-tarif-bertingkat {
  max-width: 100%;
}
</style>
