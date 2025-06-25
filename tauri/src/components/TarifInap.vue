<template>
  <div class="tarif-inap">
    <div class="row q-mb-md items-center">
      <div class="col">
        <div class="text-h6">Tarif Inap</div>
        <div class="text-caption text-grey-6">
          Kelola tarif parkir inap berdasarkan jenis kendaraan
        </div>
      </div>
      <div class="col-auto">
        <q-btn
          color="primary"
          icon="add"
          label="Tambah Tarif Inap"
          @click="showAddDialog = true"
          unelevated
        />
      </div>
    </div>

    <!-- Tarif Inap Table -->
    <q-table
      :rows="tarifStore.activeTarifInap"
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

      <template v-slot:body-cell-tarif_inap="props">
        <q-td :props="props" class="text-right">
          <span class="text-weight-bold">
            {{ formatCurrency(props.value) }}
          </span>
        </q-td>
      </template>

      <template v-slot:body-cell-jam_mulai="props">
        <q-td :props="props">
          {{ formatTime(props.value) }}
        </q-td>
      </template>

      <template v-slot:body-cell-jam_selesai="props">
        <q-td :props="props">
          {{ formatTime(props.value) }}
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
    </q-table>

    <!-- Add Dialog -->
    <q-dialog v-model="showAddDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Tambah Tarif Inap Baru</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form @submit="saveTarifInap" class="q-gutter-md">
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
              v-model.number="formData.tarif_inap"
              type="number"
              label="Tarif Inap (Rp) *"
              outlined
              min="0"
              :rules="[
                val => val !== null || 'Tarif inap harus diisi',
                val => val >= 0 || 'Tarif tidak boleh negatif'
              ]"
            />

            <div class="row q-gutter-md">
              <div class="col">
                <q-input
                  v-model.number="formData.jam_mulai"
                  type="number"
                  label="Jam Mulai Inap *"
                  outlined
                  min="0"
                  max="23"
                  hint="Format 24 jam (0-23)"
                  :rules="[
                    val => val !== null || 'Jam mulai harus diisi',
                    val => val >= 0 && val <= 23 || 'Jam harus antara 0-23'
                  ]"
                />
              </div>
              <div class="col">
                <q-input
                  v-model.number="formData.jam_selesai"
                  type="number"
                  label="Jam Selesai Inap *"
                  outlined
                  min="0"
                  max="23"
                  hint="Format 24 jam (0-23)"
                  :rules="[
                    val => val !== null || 'Jam selesai harus diisi',
                    val => val >= 0 && val <= 23 || 'Jam harus antara 0-23'
                  ]"
                />
              </div>
            </div>

            <q-input
              v-model="formData.tanggal"
              type="date"
              label="Tanggal Berlaku"
              outlined
              hint="Kosongkan untuk berlaku setiap hari"
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
            @click="saveTarifInap"
            :loading="tarifStore.isLoading"
          />
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

// Form data
const defaultFormData = {
  id_mobil: '',
  tarif_inap: 0,
  jam_mulai: 22,
  jam_selesai: 6,
  tanggal: '',
  status: 1
};

const formData = ref({ ...defaultFormData });

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
    name: 'tarif_inap',
    label: 'Tarif Inap',
    field: 'tarif_inap',
    align: 'right' as const,
    sortable: true
  },
  {
    name: 'jam_mulai',
    label: 'Jam Mulai',
    field: 'jam_mulai',
    align: 'center' as const,
    sortable: true
  },
  {
    name: 'jam_selesai',
    label: 'Jam Selesai',
    field: 'jam_selesai',
    align: 'center' as const,
    sortable: true
  },
  {
    name: 'status',
    label: 'Status',
    field: 'status',
    align: 'center' as const,
    sortable: true
  }
];

// Computed properties
const jenisKendaraanOptions = computed(() => 
  kendaraanStore.jenisKendaraanForSelect
);

const statusOptions = [
  { label: 'Aktif', value: 1 },
  { label: 'Tidak Aktif', value: 0 }
];

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
  formData.value = { ...defaultFormData };
};

const saveTarifInap = async (): Promise<void> => {
  const cleanedData = {
    ...formData.value,
    tanggal: formData.value.tanggal || undefined
  };

  const success = await tarifStore.addTarifInap(cleanedData);
  if (success) {
    closeDialog();
  }
};

// Lifecycle
onMounted(async () => {
  await kendaraanStore.loadJenisKendaraanFromLocal();
});
</script>

<style scoped>
.tarif-inap {
  padding: 16px;
}
</style>
