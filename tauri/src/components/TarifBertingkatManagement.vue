<template>
  <div class="tarif-bertingkat-management">
    <div class="row q-mb-md items-center">
      <div class="col">
        <div class="text-h6">Manajemen Tarif Bertingkat</div>
        <div class="text-caption text-grey-6">
          Kelola tarif jam pertama dan jam berikutnya dengan maksimal per hari
        </div>
      </div>
      <div class="col-auto">
        <q-btn
          color="primary"
          icon="add"
          label="Tambah Tarif Bertingkat"
          @click="showAddDialog = true"
          unelevated
        />
      </div>
    </div>

    <!-- Vehicle Type Cards -->
    <div class="row q-gutter-md">
      <div 
        v-for="vehicleGroup in groupedTarif" 
        :key="vehicleGroup.id_mobil"
        class="col-md-4 col-sm-6 col-xs-12"
      >
        <q-card flat bordered>
          <q-card-section>
            <div class="row items-center q-mb-md">
              <div class="col">
                <div class="text-h6">
                  <q-chip 
                    :color="getJenisKendaraanColor(vehicleGroup.id_mobil)"
                    text-color="white"
                    icon="directions_car"
                  >
                    {{ getJenisKendaraanName(vehicleGroup.id_mobil) }}
                  </q-chip>
                </div>
              </div>
              <div class="col-auto">
                <q-btn
                  flat
                  round
                  icon="edit"
                  size="sm"
                  @click="editVehicleGroup(vehicleGroup)"
                />
              </div>
            </div>

            <!-- Progressive Tariff Structure -->
            <q-list bordered separator>
              <q-item-label header class="text-weight-bold">
                Struktur Tarif Bertingkat
              </q-item-label>
              
              <!-- First Hour -->
              <q-item class="bg-blue-1">
                <q-item-section avatar>
                  <q-icon name="looks_one" color="blue" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold">Jam Pertama</q-item-label>
                  <q-item-label caption>Tarif jam ke-1</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label class="text-blue text-weight-bold text-h6">
                    {{ formatCurrency(vehicleGroup.jam_pertama?.tarif || 0) }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <!-- Subsequent Hours -->
              <q-item class="bg-orange-1">
                <q-item-section avatar>
                  <q-icon name="more_horiz" color="orange" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold">Jam Berikutnya</q-item-label>
                  <q-item-label caption>Tarif jam ke-2 dan seterusnya</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label class="text-orange text-weight-bold text-h6">
                    {{ formatCurrency(vehicleGroup.jam_berikutnya?.tarif || 0) }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <!-- Maximum Per Day -->
              <q-item v-if="vehicleGroup.jam_pertama?.tarif_max_per_hari" class="bg-green-1">
                <q-item-section avatar>
                  <q-icon name="check_circle" color="green" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold text-green">Maksimal Per Hari</q-item-label>
                  <q-item-label caption class="text-green">Batas maksimal tarif harian</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label class="text-green text-weight-bold text-h6">
                    {{ formatCurrency(vehicleGroup.jam_pertama.tarif_max_per_hari) }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </q-list>

            <!-- Example Calculation -->
            <q-expansion-item
              icon="calculate"
              label="Contoh Perhitungan"
              class="q-mt-md"
            >
              <q-card flat class="bg-grey-1">
                <q-card-section>
                  <div class="text-subtitle2 q-mb-sm">Parkir 5 jam:</div>
                  <q-list dense>
                    <q-item>
                      <q-item-section>
                        <q-item-label caption>Jam ke-1</q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-item-label>{{ formatCurrency(vehicleGroup.jam_pertama?.tarif || 0) }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item>
                      <q-item-section>
                        <q-item-label caption>Jam ke-2 s/d 5</q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-item-label>{{ formatCurrency((vehicleGroup.jam_berikutnya?.tarif || 0) * 4) }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-separator />
                    <q-item>
                      <q-item-section>
                        <q-item-label class="text-weight-bold">Total</q-item-label>
                      </q-item-section>
                      <q-item-section side>
                        <q-item-label class="text-weight-bold">
                          {{ formatCurrency((vehicleGroup.jam_pertama?.tarif || 0) + ((vehicleGroup.jam_berikutnya?.tarif || 0) * 4)) }}
                        </q-item-label>
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

    <!-- Add/Edit Dialog -->
    <q-dialog v-model="showAddDialog" persistent>
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">
            {{ editingGroup ? 'Edit Tarif Bertingkat' : 'Tambah Tarif Bertingkat' }}
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form @submit="saveTarifBertingkat" class="q-gutter-md">
            <q-select
              v-model="formData.id_mobil"
              :options="jenisKendaraanOptions"
              label="Jenis Kendaraan *"
              outlined
              emit-value
              map-options
              :rules="[val => !!val || 'Jenis kendaraan harus dipilih']"
            />

            <div class="row q-gutter-md">
              <div class="col">
                <q-input
                  v-model.number="formData.tarif_jam_pertama"
                  type="number"
                  label="Tarif Jam Pertama (Rp) *"
                  outlined
                  min="0"
                  :rules="[
                    val => val !== null || 'Tarif jam pertama harus diisi',
                    val => val >= 0 || 'Tarif tidak boleh negatif'
                  ]"
                />
              </div>
              <div class="col">
                <q-input
                  v-model.number="formData.tarif_jam_berikutnya"
                  type="number"
                  label="Tarif Jam Berikutnya (Rp) *"
                  outlined
                  min="0"
                  :rules="[
                    val => val !== null || 'Tarif jam berikutnya harus diisi',
                    val => val >= 0 || 'Tarif tidak boleh negatif'
                  ]"
                />
              </div>
            </div>

            <q-input
              v-model.number="formData.tarif_max_per_hari"
              type="number"
              label="Maksimal Tarif Per Hari (Rp)"
              outlined
              min="0"
              hint="Opsional: Batas maksimal tarif yang bisa dikenakan per hari"
            />

            <q-toggle
              v-model="formData.max_per_hari_aktif"
              label="Aktifkan Maksimal Per Hari"
              color="primary"
              left-label
            />

            <div class="row q-gutter-md">
              <div class="col">
                <q-input
                  v-model.number="formData.tarif_denda"
                  type="number"
                  label="Tarif Denda (Rp)"
                  outlined
                  min="0"
                  hint="Opsional: Tarif denda untuk keterlambatan"
                />
              </div>
              <div class="col">
                <q-input
                  v-model.number="formData.tarif_member"
                  type="number"
                  label="Diskon Member (%)"
                  outlined
                  min="0"
                  max="100"
                  hint="Opsional: Persentase diskon untuk member"
                />
              </div>
            </div>
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Batal" @click="closeDialog" />
          <q-btn color="primary" label="Simpan" @click="saveTarifBertingkat" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useTarifStore } from 'src/stores/tarif-store';
import { useKendaraanStore } from 'src/stores/kendaraan-store';

// Store instances
const tarifStore = useTarifStore();
const kendaraanStore = useKendaraanStore();

// Reactive state
const showAddDialog = ref(false);
const editingGroup = ref<any>(null);
const formData = ref({
  id_mobil: '',
  tarif_jam_pertama: 0,
  tarif_jam_berikutnya: 0,
  tarif_max_per_hari: null as number | null,
  max_per_hari_aktif: false,
  tarif_denda: null as number | null,
  tarif_member: null as number | null
});

// Computed properties
const groupedTarif = computed(() => {
  const groups: any[] = [];
  const tarifByVehicle = new Map();

  // Group tariffs by vehicle type
  tarifStore.activeTarif.forEach(tarif => {
    if (!tarifByVehicle.has(tarif.id_mobil)) {
      tarifByVehicle.set(tarif.id_mobil, {
        id_mobil: tarif.id_mobil,
        jam_pertama: null,
        jam_berikutnya: null,
        tariffs: []
      });
    }
    
    const group = tarifByVehicle.get(tarif.id_mobil);
    group.tariffs.push(tarif);
    
    if (tarif.jam_ke === 1) {
      group.jam_pertama = tarif;
    } else if (tarif.jam_ke === 2) {
      group.jam_berikutnya = tarif;
    }
  });

  return Array.from(tarifByVehicle.values());
});

const jenisKendaraanOptions = computed(() => 
  kendaraanStore.jenisKendaraanForSelect
);

// Methods
const editVehicleGroup = (group: any) => {
  editingGroup.value = group;
  formData.value = {
    id_mobil: group.id_mobil,
    tarif_jam_pertama: group.jam_pertama?.tarif || 0,
    tarif_jam_berikutnya: group.jam_berikutnya?.tarif || 0,
    tarif_max_per_hari: group.jam_pertama?.tarif_max_per_hari || null,
    max_per_hari_aktif: !!(group.jam_pertama?.max_per_hari),
    tarif_denda: group.jam_pertama?.tarif_denda || null,
    tarif_member: group.jam_pertama?.tarif_member || null
  };
  showAddDialog.value = true;
};

const saveTarifBertingkat = async () => {
  try {
    // Save first hour tariff
    const jamPertamaData = {
      id_mobil: formData.value.id_mobil,
      jam_ke: 1,
      tarif: formData.value.tarif_jam_pertama,
      time_base: 60,
      tarif_max_per_hari: formData.value.max_per_hari_aktif ? formData.value.tarif_max_per_hari || undefined : undefined,
      max_per_hari: formData.value.max_per_hari_aktif ? 1 : 0,
      tarif_denda: formData.value.tarif_denda || undefined,
      tarif_member: formData.value.tarif_member || undefined,
      status: 1
    };

    // Save subsequent hours tariff
    const jamBerikutnyaData = {
      id_mobil: formData.value.id_mobil,
      jam_ke: 2,
      tarif: formData.value.tarif_jam_berikutnya,
      time_base: 60,
      tarif_max_per_hari: formData.value.max_per_hari_aktif ? formData.value.tarif_max_per_hari || undefined : undefined,
      max_per_hari: 0,
      tarif_denda: formData.value.tarif_denda || undefined,
      tarif_member: formData.value.tarif_member || undefined,
      status: 1
    };

    if (editingGroup.value) {
      // Update existing
      if (editingGroup.value.jam_pertama) {
        await tarifStore.editTarif({ ...editingGroup.value.jam_pertama, ...jamPertamaData });
      } else {
        await tarifStore.addTarif(jamPertamaData);
      }

      if (editingGroup.value.jam_berikutnya) {
        await tarifStore.editTarif({ ...editingGroup.value.jam_berikutnya, ...jamBerikutnyaData });
      } else {
        await tarifStore.addTarif(jamBerikutnyaData);
      }
    } else {
      // Add new
      await tarifStore.addTarif(jamPertamaData);
      await tarifStore.addTarif(jamBerikutnyaData);
    }

    closeDialog();
  } catch (error) {
    console.error('Error saving tarif bertingkat:', error);
  }
};

const closeDialog = () => {
  showAddDialog.value = false;
  editingGroup.value = null;
  formData.value = {
    id_mobil: '',
    tarif_jam_pertama: 0,
    tarif_jam_berikutnya: 0,
    tarif_max_per_hari: null,
    max_per_hari_aktif: false,
    tarif_denda: null,
    tarif_member: null
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
  await kendaraanStore.getAllJenisKendaraan();
});
</script>

<style scoped>
.tarif-bertingkat-management {
  padding: 16px;
}
</style>
