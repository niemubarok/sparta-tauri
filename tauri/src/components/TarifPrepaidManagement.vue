<template>
  <div class="tarif-prepaid-management">
    <div class="row q-mb-md items-center">
      <div class="col">
        <div class="text-h6">Manajemen Tarif Prepaid</div>
        <div class="text-caption text-grey-6">
          Kelola tarif flat yang dibayar di awal (bayar depan) untuk kendaraan prepaid
        </div>
      </div>
      <div class="col-auto">
        <q-btn
          color="positive"
          icon="add"
          label="Tambah Tarif Prepaid"
          @click="showAddPrepaidDialog = true"
          unelevated
        />
      </div>
    </div>

    <!-- Prepaid Tariff Cards -->
    <div class="row q-gutter-md">
      <div 
        v-for="prepaidTarif in groupedPrepaidTarif" 
        :key="prepaidTarif.id_mobil"
        class="col-md-4 col-sm-6 col-xs-12"
      >
        <q-card flat bordered>
          <q-card-section>
            <div class="row items-center q-mb-md">
              <div class="col">
                <div class="text-h6">
                  <q-chip 
                    :color="getJenisKendaraanColor(prepaidTarif.id_mobil)"
                    text-color="white"
                    icon="payments"
                  >
                    {{ getJenisKendaraanName(prepaidTarif.id_mobil) }}
                  </q-chip>
                </div>
              </div>
              <div class="col-auto">
                <q-btn
                  flat
                  round
                  icon="edit"
                  size="sm"
                  @click="editPrepaidTarif(prepaidTarif)"
                />
              </div>
            </div>

            <!-- Prepaid Tariff Structure -->
            <q-list bordered separator>
              <q-item-label header class="text-weight-bold">
                Tarif Prepaid (Bayar Depan)
              </q-item-label>
              
              <!-- Flat Rate -->
              <q-item class="bg-green-1">
                <q-item-section avatar>
                  <q-icon name="attach_money" color="green" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold">Tarif Flat</q-item-label>
                  <q-item-label caption>Bayar sekali di awal</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label class="text-green text-weight-bold text-h6">
                    {{ formatCurrency(prepaidTarif.tarif_prepaid || 0) }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <!-- Valid Duration -->
              <q-item v-if="prepaidTarif.durasi_berlaku" class="bg-blue-1">
                <q-item-section avatar>
                  <q-icon name="schedule" color="blue" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold text-blue">Durasi Berlaku</q-item-label>
                  <q-item-label caption class="text-blue">Lama waktu parkir yang dibayar</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label class="text-blue text-weight-bold text-h6">
                    {{ prepaidTarif.durasi_berlaku }} jam
                  </q-item-label>
                </q-item-section>
              </q-item>

              <!-- Additional Fee After Duration -->
              <q-item v-if="prepaidTarif.tarif_tambahan" class="bg-orange-1">
                <q-item-section avatar>
                  <q-icon name="add_circle" color="orange" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold text-orange">Tarif Tambahan</q-item-label>
                  <q-item-label caption class="text-orange">Jika melebihi durasi berlaku</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label class="text-orange text-weight-bold text-h6">
                    {{ formatCurrency(prepaidTarif.tarif_tambahan) }}/jam
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>

            <!-- Example Scenarios -->
            <q-expansion-item
              icon="info"
              label="Contoh Skenario"
              class="q-mt-md"
            >
              <q-card flat class="bg-grey-1">
                <q-card-section>
                  <div class="text-subtitle2 q-mb-sm">Skenario Prepaid:</div>
                  <q-list dense>
                    <q-item>
                      <q-item-section>
                        <q-item-label caption>Parkir {{ prepaidTarif.durasi_berlaku || 2 }} jam (dalam durasi)</q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-item-label>{{ formatCurrency(prepaidTarif.tarif_prepaid || 0) }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item v-if="prepaidTarif.tarif_tambahan">
                      <q-item-section>
                        <q-item-label caption>Parkir {{ (prepaidTarif.durasi_berlaku || 2) + 2 }} jam (lebih {{ (prepaidTarif.durasi_berlaku || 2) + 2 - (prepaidTarif.durasi_berlaku || 2) }} jam)</q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-item-label>{{ formatCurrency((prepaidTarif.tarif_prepaid || 0) + (prepaidTarif.tarif_tambahan * 2)) }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
              </q-card>
            </q-expansion-item>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Add/Edit Prepaid Dialog -->
    <q-dialog v-model="showAddPrepaidDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">
            {{ editingPrepaidTarif ? 'Edit Tarif Prepaid' : 'Tambah Tarif Prepaid' }}
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form @submit="saveTarifPrepaid" class="q-gutter-md">
            <q-select
              v-model="prepaidFormData.id_mobil"
              :options="jenisKendaraanOptions"
              label="Jenis Kendaraan *"
              outlined
              emit-value
              map-options
              :rules="[val => !!val || 'Jenis kendaraan harus dipilih']"
            />

            <q-input
              v-model.number="prepaidFormData.tarif_prepaid"
              type="number"
              label="Tarif Prepaid (Rp) *"
              outlined
              min="0"
              hint="Tarif flat yang dibayar di awal"
              :rules="[
                val => val !== null || 'Tarif prepaid harus diisi',
                val => val >= 0 || 'Tarif tidak boleh negatif'
              ]"
            />

            <q-input
              v-model.number="prepaidFormData.durasi_berlaku"
              type="number"
              label="Durasi Berlaku (Jam)"
              outlined
              min="1"
              hint="Lama waktu parkir yang dibayar (jam)"
            />

            <q-input
              v-model.number="prepaidFormData.tarif_tambahan"
              type="number"
              label="Tarif Tambahan Per Jam (Rp)"
              outlined
              min="0"
              hint="Tarif per jam jika melebihi durasi berlaku"
            />

            <q-toggle
              v-model="prepaidFormData.berlaku_tanpa_batas"
              label="Berlaku Tanpa Batas Waktu"
              color="primary"
              left-label
            />
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Batal" @click="closePrepaidDialog" />
          <q-btn color="positive" label="Simpan" @click="saveTarifPrepaid" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useTarifStore, type TarifPrepaid } from 'src/stores/tarif-store';
import { useKendaraanStore } from 'src/stores/kendaraan-store';

// Store instances
const tarifStore = useTarifStore();
const kendaraanStore = useKendaraanStore();

// Prepaid state
const showAddPrepaidDialog = ref(false);
const editingPrepaidTarif = ref<any>(null);
const prepaidFormData = ref({
  id_mobil: '',
  tarif_prepaid: 0,
  durasi_berlaku: 8, // Default 8 hours
  tarif_tambahan: 0,
  berlaku_tanpa_batas: false
});

// Computed properties
const jenisKendaraanOptions = computed(() => 
  kendaraanStore.jenisKendaraanForSelect
);

const groupedPrepaidTarif = computed(() => {
  const groups: any[] = [];
  const tarifByVehicle = new Map();

  // Group prepaid tariffs by vehicle type
  tarifStore.activeTarifPrepaid.forEach(tarif => {
    if (!tarifByVehicle.has(tarif.id_mobil)) {
      tarifByVehicle.set(tarif.id_mobil, {
        id_mobil: tarif.id_mobil,
        tarif_prepaid: tarif.tarif_prepaid,
        durasi_berlaku: tarif.durasi_berlaku,
        tarif_tambahan: tarif.tarif_tambahan,
        berlaku_tanpa_batas: tarif.berlaku_tanpa_batas
      });
    }
  });

  return Array.from(tarifByVehicle.values());
});

// Prepaid methods
const editPrepaidTarif = (prepaidTarif: any) => {
  // Find the complete tariff object from store
  const completeTariff = tarifStore.daftarTarifPrepaid.find(t => t.id_mobil === prepaidTarif.id_mobil);
  editingPrepaidTarif.value = completeTariff || prepaidTarif;
  
  prepaidFormData.value = {
    id_mobil: prepaidTarif.id_mobil,
    tarif_prepaid: prepaidTarif.tarif_prepaid || 0,
    durasi_berlaku: prepaidTarif.durasi_berlaku || 8,
    tarif_tambahan: prepaidTarif.tarif_tambahan || 0,
    berlaku_tanpa_batas: prepaidTarif.berlaku_tanpa_batas || false
  };
  showAddPrepaidDialog.value = true;
};

const saveTarifPrepaid = async () => {
  try {
    const tarifPrepaidData = {
      id_mobil: prepaidFormData.value.id_mobil,
      tarif_prepaid: prepaidFormData.value.tarif_prepaid,
      durasi_berlaku: prepaidFormData.value.durasi_berlaku,
      tarif_tambahan: prepaidFormData.value.tarif_tambahan,
      berlaku_tanpa_batas: prepaidFormData.value.berlaku_tanpa_batas,
      status: 1,
      created_by: 'SYSTEM'
    };

    if (editingPrepaidTarif.value && editingPrepaidTarif.value.id) {
      // Update existing prepaid tariff - ensure we have the complete object with ID
      const existingTariff = tarifStore.daftarTarifPrepaid.find(t => t.id_mobil === editingPrepaidTarif.value.id_mobil);
      if (existingTariff) {
        await tarifStore.editTarifPrepaid({
          ...existingTariff,
          ...tarifPrepaidData
        });
      } else {
        // If not found in store, create new one
        await tarifStore.addTarifPrepaid(tarifPrepaidData);
      }
    } else {
      // Add new prepaid tariff
      await tarifStore.addTarifPrepaid(tarifPrepaidData);
    }
    
    closePrepaidDialog();
  } catch (error) {
    console.error('Error saving prepaid tariff:', error);
  }
};

const closePrepaidDialog = () => {
  showAddPrepaidDialog.value = false;
  editingPrepaidTarif.value = null;
  prepaidFormData.value = {
    id_mobil: '',
    tarif_prepaid: 0,
    durasi_berlaku: 8,
    tarif_tambahan: 0,
    berlaku_tanpa_batas: false
  };
};

const getJenisKendaraanName = (id: string): string => {
  const jenis = kendaraanStore.jenisKendaraan.find(j => j.id === id);
  return jenis?.jenis || id;
};

const getJenisKendaraanColor = (id: string): string => {
  const colors: { [key: string]: string } = {
    'MTR': 'blue',
    'MBL': 'orange', 
    'BUS': 'purple',
    'TRK': 'red',
    'SPD': 'green'
  };
  return colors[id] || 'grey';
};

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount);
};

// Lifecycle
onMounted(async () => {
  await tarifStore.loadTarifFromLocal();
  await tarifStore.loadTarifPrepaidFromLocal();
  await kendaraanStore.getAllJenisKendaraan();
});
</script>

<style scoped>
.tarif-prepaid-management {
  padding: 16px;
}
</style>
