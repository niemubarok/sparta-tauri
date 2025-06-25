<template>
  <div class="daftar-tarif">
    <div class="row q-mb-md items-center">
      <div class="col">
        <div class="text-h6">Manajemen Tarif Bertingkat</div>
        <div class="text-caption text-grey-6">
          Kelola tarif jam pertama dan jam berikutnya untuk setiap jenis kendaraan
        </div>
      </div>
      <div class="col-auto">
        <q-btn
          color="primary"
          icon="add"
          label="Tambah Tarif"
          @click="showAddDialog = true"
          unelevated
        />
      </div>
    </div>

    <!-- Tarif Cards by Vehicle Type -->
    <div class="row q-gutter-md">
      <div 
        v-for="jenisKendaraan in groupedTarif" 
        :key="jenisKendaraan.id_mobil"
        class="col-md-6 col-sm-12"
      >
        <q-card flat bordered>
          <q-card-section>
            <div class="row items-center q-mb-md">
              <div class="col">
                <div class="text-h6">
                  <q-chip 
                    :color="getJenisKendaraanColor(jenisKendaraan.id_mobil)"
                    text-color="white"
                    icon="directions_car"
                  >
                    {{ getJenisKendaraanName(jenisKendaraan.id_mobil) }}
                  </q-chip>
                </div>
              </div>
              <div class="col-auto">
                <q-btn
                  icon="edit"
                  size="sm"
                  flat
                  round
                  @click="editVehicleTarif(jenisKendaraan.id_mobil)"
                />
              </div>
            </div>

            <!-- Progressive Tariff Display -->
            <q-list separator>
              <!-- First Hour Tariff -->
              <q-item>
                <q-item-section avatar>
                  <q-avatar color="primary" text-color="white" size="sm">
                    1
                  </q-avatar>
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold">Jam Pertama</q-item-label>
                  <q-item-label caption>Tarif jam ke-1</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label class="text-weight-bold text-primary">
                    {{ formatCurrency(jenisKendaraan.tarifs.find(t => t.jam_ke === 1)?.tarif || 0) }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <!-- Subsequent Hours Tariff -->
              <q-item>
                <q-item-section avatar>
                  <q-avatar color="orange" text-color="white" size="sm">
                    2+
                  </q-avatar>
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold">Jam Berikutnya</q-item-label>
                  <q-item-label caption>Tarif jam ke-2 dan seterusnya</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label class="text-weight-bold text-orange">
                    {{ formatCurrency(jenisKendaraan.tarifs.find(t => t.jam_ke === 2)?.tarif || 0) }}
                  </q-item-label>
                </q-item-section>
              </q-item>

              <!-- Maximum Per Day -->
              <q-item v-if="jenisKendaraan.maxPerHari" class="bg-green-1">
                <q-item-section avatar>
                  <q-avatar color="green" text-color="white" size="sm">
                    <q-icon name="check_circle" size="xs" />
                  </q-avatar>
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-weight-bold text-green">Maksimal Per Hari</q-item-label>
                  <q-item-label caption class="text-green">Batas maksimal tarif harian</q-item-label>
                </q-item-section>
                <q-item-section side>
                  <q-item-label class="text-weight-bold text-green">
                    {{ formatCurrency(jenisKendaraan.maxPerHari) }}
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
              <q-card flat class="bg-grey-1 q-ma-sm">
                <q-card-section class="q-pa-sm">
                  <div class="text-caption text-weight-bold q-mb-xs">Parkir 5 jam:</div>
                  <div class="text-caption">
                    • Jam ke-1: {{ formatCurrency(jenisKendaraan.tarifs.find(t => t.jam_ke === 1)?.tarif || 0) }}
                  </div>
                  <div class="text-caption">
                    • Jam ke-2-5: {{ formatCurrency((jenisKendaraan.tarifs.find(t => t.jam_ke === 2)?.tarif || 0) * 4) }}
                    (4 × {{ formatCurrency(jenisKendaraan.tarifs.find(t => t.jam_ke === 2)?.tarif || 0) }})
                  </div>
                  <q-separator class="q-my-xs" />
                  <div class="text-caption text-weight-bold">
                    Total: {{ formatCurrency(calculateExample(jenisKendaraan, 5)) }}
                  </div>
                </q-card-section>
              </q-card>
            </q-expansion-item>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Raw Table View (for detailed editing) -->
    <q-expansion-item
      icon="table_view"
      label="Tampilan Tabel Detail"
      class="q-mt-lg"
    >
      <q-table
        :rows="filteredTarif"
        :columns="columns"
        row-key="id"
        :loading="tarifStore.isLoading"
        :pagination="{ rowsPerPage: 10 }"
        binary-state-sort
        flat
        bordered
      >
        <template v-slot:body-cell-id_mobil="props">
          <q-td :props="props">
          <q-chip 
            :color="getJenisKendaraanColor(props.value)"
            text-color="white"
            dense
          >
            {{ getJenisKendaraanName(props.value) }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-tarif="props">
        <q-td :props="props" class="text-right">
          <span class="text-weight-bold">
            {{ formatCurrency(props.value) }}
          </span>
        </q-td>
      </template>

      <template v-slot:body-cell-tarif_denda="props">
        <q-td :props="props" class="text-right">
          <span class="text-red">
            {{ props.value ? formatCurrency(props.value) : '-' }}
          </span>
        </q-td>
      </template>

      <template v-slot:body-cell-tarif_member="props">
        <q-td :props="props" class="text-right">
          <span class="text-green">
            {{ props.value ? formatCurrency(props.value) : '-' }}
          </span>
        </q-td>
      </template>

      <template v-slot:body-cell-tarif_max_per_hari="props">
        <q-td :props="props" class="text-right">
          <span v-if="props.value" class="text-blue text-weight-bold">
            {{ formatCurrency(props.value) }}
          </span>
          <span v-else class="text-grey-5">-</span>
          <q-tooltip v-if="props.value">
            Maksimal tarif per hari untuk jenis kendaraan ini
          </q-tooltip>
        </q-td>
      </template>

      <template v-slot:body-cell-time_base="props">
        <q-td :props="props">
          {{ props.value }} menit
        </q-td>
      </template>

      <template v-slot:body-cell-status="props">
        <q-td :props="props">
          <q-chip
            :color="props.value === 1 ? 'positive' : 'negative'"
            text-color="white"
            dense
          >
            {{ props.value === 1 ? 'Aktif' : 'Tidak Aktif' }}
          </q-chip>
        </q-td>
      </template>

      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            flat
            round
            dense
            icon="edit"
            color="primary"
            @click="editTarif(props.row)"
            class="q-mr-xs"
          >
            <q-tooltip>Edit Tarif</q-tooltip>
          </q-btn>
          <q-btn
            flat
            round
            dense
            icon="delete"
            color="negative"
            @click="confirmDelete(props.row)"
          >
            <q-tooltip>Hapus Tarif</q-tooltip>
          </q-btn>
        </q-td>
      </template>
    </q-table>
    </q-expansion-item>

    <!-- Add/Edit Dialog -->
    <q-dialog v-model="showAddDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">
            {{ editingTarif ? 'Edit Tarif' : 'Tambah Tarif Baru' }}
          </div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form @submit="saveTarif" class="q-gutter-md">
            <q-select
              v-model="formData.id_mobil"
              :options="jenisKendaraanOptions"
              label="Jenis Kendaraan *"
              outlined
              emit-value
              map-options
              :rules="[val => !!val || 'Jenis kendaraan harus dipilih']"
            />

            <q-input
              v-model.number="formData.jam_ke"
              type="number"
              label="Jam Ke- *"
              outlined
              min="1"
              max="24"
              :rules="[
                val => !!val || 'Jam ke harus diisi',
                val => val >= 1 || 'Minimum jam ke-1',
                val => val <= 24 || 'Maksimum jam ke-24'
              ]"
            />

            <q-input
              v-model.number="formData.tarif"
              type="number"
              label="Tarif (Rp) *"
              outlined
              min="0"
              :rules="[
                val => val !== null || 'Tarif harus diisi',
                val => val >= 0 || 'Tarif tidak boleh negatif'
              ]"
            />

            <q-input
              v-model.number="formData.tarif_denda"
              type="number"
              label="Tarif Denda (Rp)"
              outlined
              min="0"
              hint="Opsional: Tarif denda untuk keterlambatan"
            />

            <q-input
              v-model.number="formData.tarif_member"
              type="number"
              label="Tarif Member (Rp)"
              outlined
              min="0"
              hint="Opsional: Tarif khusus untuk member"
            />

            <q-input
              v-model.number="formData.tarif_max_per_hari"
              type="number"
              label="Maksimal Tarif Per Hari (Rp)"
              outlined
              min="0"
              hint="Opsional: Batas maksimal tarif yang bisa dikenakan per hari"
            />

            <q-toggle
              v-model="formData.max_per_hari"
              label="Aktifkan Maksimal Per Hari"
              color="primary"
              left-label
              class="q-mb-md"
            />

            <q-input
              v-model.number="formData.time_base"
              type="number"
              label="Waktu Dasar (menit) *"
              outlined
              min="1"
              :rules="[
                val => !!val || 'Waktu dasar harus diisi',
                val => val >= 1 || 'Minimum 1 menit'
              ]"
            />

            <q-input
              v-model.number="formData.time_base_maks"
              type="number"
              label="Waktu Dasar Maksimal (menit)"
              outlined
              min="1"
              hint="Opsional: Batas maksimal untuk tarif ini"
            />

            <q-input
              v-model.number="formData.max_free_same_hour"
              type="number"
              label="Maksimal Gratis (menit)"
              outlined
              min="0"
              hint="Opsional: Waktu gratis dalam jam yang sama"
            />

            <q-select
              v-model="formData.status"
              :options="statusOptions"
              label="Status"
              outlined
              emit-value
              map-options
            />
          </q-form>
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="Batal" @click="closeDialog" />
          <q-btn 
            flat 
            label="Simpan" 
            @click="saveTarif"
            :loading="tarifStore.isLoading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Delete Confirmation Dialog -->
    <q-dialog v-model="showDeleteDialog" persistent>
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="warning" color="negative" text-color="white" />
          <span class="q-ml-sm">
            Apakah Anda yakin ingin menghapus tarif ini?
          </span>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Batal" @click="showDeleteDialog = false" />
          <q-btn 
            flat 
            label="Hapus" 
            color="negative" 
            @click="performDelete"
            :loading="tarifStore.isLoading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useTarifStore, type Tarif } from 'src/stores/tarif-store';
import { useKendaraanStore } from 'src/stores/kendaraan-store';

// Store instances
const tarifStore = useTarifStore();
const kendaraanStore = useKendaraanStore();

// Reactive state
const showAddDialog = ref(false);
const showDeleteDialog = ref(false);
const editingTarif = ref<Tarif | null>(null);
const deletingTarif = ref<Tarif | null>(null);
const selectedJenisKendaraan = ref<string | null>(null);
const statusFilter = ref<number | null>(null);

// Form data
const defaultFormData = {
  id_mobil: '',
  jam_ke: 1,
  tarif: 0,
  tarif_denda: null as number | null,
  tarif_member: null as number | null,
  tarif_max_per_hari: null as number | null,
  max_per_hari: 0 as number,
  time_base: 60,
  time_base_maks: null as number | null,
  max_free_same_hour: null as number | null,
  status: 1
};

const formData = ref<{
  id_mobil: string;
  jam_ke: number;
  tarif: number;
  tarif_denda: number | null;
  tarif_member: number | null;
  tarif_max_per_hari: number | null;
  max_per_hari: number;
  time_base: number;
  time_base_maks: number | null;
  max_free_same_hour: number | null;
  status: number;
}>({ ...defaultFormData });

// Table columns
const columns = [
  {
    name: 'id_mobil',
    label: 'Jenis Kendaraan',
    field: 'id_mobil',
    align: 'left' as const,
    sortable: true
  },
  {
    name: 'jam_ke',
    label: 'Jam Ke-',
    field: 'jam_ke',
    align: 'center' as const,
    sortable: true
  },
  {
    name: 'tarif',
    label: 'Tarif Normal',
    field: 'tarif',
    align: 'right' as const,
    sortable: true
  },
  {
    name: 'tarif_denda',
    label: 'Tarif Denda',
    field: 'tarif_denda',
    align: 'right' as const,
    sortable: true
  },
  {
    name: 'tarif_member',
    label: 'Tarif Member',
    field: 'tarif_member',
    align: 'right' as const,
    sortable: true
  },
  {
    name: 'tarif_max_per_hari',
    label: 'Max Per Hari',
    field: 'tarif_max_per_hari',
    align: 'right' as const,
    sortable: true
  },
  {
    name: 'time_base',
    label: 'Waktu Dasar',
    field: 'time_base',
    align: 'center' as const,
    sortable: true
  },
  {
    name: 'status',
    label: 'Status',
    field: 'status',
    align: 'center' as const,
    sortable: true
  },
  {
    name: 'actions',
    label: 'Aksi',
    field: 'actions',
    align: 'center' as const,
    sortable: false
  }
];

// Computed properties
const groupedTarif = computed(() => {
  const groups: Record<string, {
    id_mobil: string;
    tarifs: Tarif[];
    maxPerHari?: number;
  }> = {};

  tarifStore.activeTarif.forEach((tarif: Tarif) => {
    if (!groups[tarif.id_mobil]) {
      groups[tarif.id_mobil] = {
        id_mobil: tarif.id_mobil,
        tarifs: [],
        maxPerHari: tarif.tarif_max_per_hari
      };
    }
    groups[tarif.id_mobil].tarifs.push(tarif);
  });

  // Sort tarifs by jam_ke within each group
  Object.values(groups).forEach(group => {
    group.tarifs.sort((a, b) => a.jam_ke - b.jam_ke);
  });

  return Object.values(groups);
});

const filteredTarif = computed(() => {
  let result = tarifStore.activeTarif;

  if (selectedJenisKendaraan.value) {
    result = result.filter((tarif: Tarif) => tarif.id_mobil === selectedJenisKendaraan.value);
  }

  if (statusFilter.value !== null) {
    result = result.filter((tarif: Tarif) => tarif.status === statusFilter.value);
  }

  return result;
});

// Functions
const calculateExample = (jenisKendaraan: { tarifs: Tarif[] }, hours: number): number => {
  const firstHour = jenisKendaraan.tarifs.find((t: Tarif) => t.jam_ke === 1);
  const subsequentHour = jenisKendaraan.tarifs.find((t: Tarif) => t.jam_ke === 2);
  
  if (!firstHour || !subsequentHour) return 0;
  
  return firstHour.tarif + (subsequentHour.tarif * (hours - 1));
};

const editVehicleTarif = (idMobil: string): void => {
  // Find first tariff for this vehicle type to edit
  const tarif = tarifStore.activeTarif.find((t: Tarif) => t.id_mobil === idMobil);
  if (tarif) {
    editTarif(tarif);
  }
};
const jenisKendaraanOptions = computed(() => 
  kendaraanStore.jenisKendaraanForSelect
);

const statusOptions = [
  { label: 'Aktif', value: 1 },
  { label: 'Tidak Aktif', value: 0 }
];

// Utility functions
const formatCurrency = (amount: number | undefined): string => {
  if (amount === undefined || amount === null) return 'Rp 0';
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount);
};

const getJenisKendaraanName = (id: string): string => {
  const jenis = (kendaraanStore.jenisKendaraan || []).find((j: any) => j.id === id);
  return jenis?.jenis || id;
};

const getJenisKendaraanColor = (id: string): string => {
  const colors: Record<string, string> = {
    'MTR': 'blue',
    'MBL': 'green',
    'TRK': 'orange',
    'BUS': 'purple',
    'SPD': 'teal'
  };
  return colors[id] || 'grey';
};

// Dialog methods
const closeDialog = (): void => {
  showAddDialog.value = false;
  editingTarif.value = null;
  formData.value = { ...defaultFormData };
};

const editTarif = (tarif: Tarif): void => {
  editingTarif.value = tarif;
  formData.value = {
    id_mobil: tarif.id_mobil,
    jam_ke: tarif.jam_ke,
    tarif: tarif.tarif,
    tarif_denda: tarif.tarif_denda || null,
    tarif_member: tarif.tarif_member || null,
    tarif_max_per_hari: tarif.tarif_max_per_hari || null,
    max_per_hari: tarif.max_per_hari || 0,
    time_base: tarif.time_base,
    time_base_maks: tarif.time_base_maks || null,
    max_free_same_hour: tarif.max_free_same_hour || null,
    status: tarif.status || 1
  };
  showAddDialog.value = true;
};

const confirmDelete = (tarif: Tarif): void => {
  deletingTarif.value = tarif;
  showDeleteDialog.value = true;
};

const performDelete = async (): Promise<void> => {
  if (!deletingTarif.value) return;

  const success = await tarifStore.deleteTarif(deletingTarif.value.id);
  if (success) {
    showDeleteDialog.value = false;
    deletingTarif.value = null;
  }
};

const saveTarif = async (): Promise<void> => {
  // Clean form data
  const cleanedData = {
    ...formData.value,
    tarif_denda: formData.value.tarif_denda || undefined,
    tarif_member: formData.value.tarif_member || undefined,
    tarif_max_per_hari: formData.value.tarif_max_per_hari || undefined,
    max_per_hari: formData.value.max_per_hari || undefined,
    time_base_maks: formData.value.time_base_maks || undefined,
    max_free_same_hour: formData.value.max_free_same_hour || undefined
  };

  let success = false;

  if (editingTarif.value) {
    // Update existing tarif
    success = await tarifStore.editTarif({
      ...editingTarif.value,
      ...cleanedData
    });
  } else {
    // Add new tarif
    success = await tarifStore.addTarif(cleanedData);
  }

  if (success) {
    closeDialog();
  }
};

// Lifecycle
onMounted(async () => {
  await tarifStore.loadTarifFromLocal();
  await kendaraanStore.loadJenisKendaraanFromLocal();
});
</script>

<style scoped>
.daftar-tarif {
  padding: 16px;
}
</style>
