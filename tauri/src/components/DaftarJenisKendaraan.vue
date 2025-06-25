<template>
  <q-card class="q-ml-xl">
    <q-card-section class="row">
      <div>
        <q-chip
          icon="directions_car"
          label="Daftar Jenis Kendaraan"
          class="text-weight-bolder"
        />
      </div>
      <q-space />
    </q-card-section>

    <q-virtual-scroll
      type="table"
      :style="$q.screen.gt.md ? 'height: 75vh' : 'height: 70vh'"
      :virtual-scroll-item-size="48"
      :virtual-scroll-sticky-size-start="48"
      :virtual-scroll-sticky-size-end="32"
      :items="jenisKendaraan"
      :loading="isLoading"
      sort-by="jenis"
    >
      <template v-slot:before>
        <thead class="thead-sticky">
          <tr class="text-left bg-grey-8">
            <th
              class="text-h4 text-weight-bolder text-white"
              v-for="col in columns"
              :key="'1--' + col.name"
              :align="col.align"
            >
              {{ col.name }}
            </th>
          </tr>
        </thead>
      </template>

      <template v-if="!jenisKendaraan?.length" v-slot:after>
        <tr>
          <td align="center" colspan="8" class="text-grey-5">
            <h5>Tidak ada Data jenis kendaraan</h5>
          </td>
        </tr>
      </template>

      <template v-slot="{ item: row, index }">
        <tr :key="index" :class="index % 2 == 0 ? 'bg-white' : 'bg-grey-2'">
          <td>{{ row.id }}</td>
          <td align="left">
            <span class="text-subtitle2">{{ row.jenis }}</span>
            <q-popup-edit
              v-model="row.jenis"
              v-slot="scope"
              @save="(value) => update(row.id, 'jenis', value)"
            >
              <q-input
                v-model="scope.value"
                dense
                autofocus
                counter
                @keyup.enter="scope.set"
              />
              <div class="float-right">
                <q-btn
                  size="sm"
                  color="red-9"
                  flat
                  icon="close"
                  @click="scope.cancel"
                />
                <q-btn
                  size="sm"
                  color="green-9"
                  flat
                  icon="check"
                  @click="scope.set"
                />
              </div>
            </q-popup-edit>
          </td>
          <td align="right">
            <span class="text-subtitle2">{{ formatCurrency(row.tarif || 0) }}</span>
            <q-popup-edit
              v-model="row.tarif"
              v-slot="scope"
              @save="(value) => update(row.id, 'tarif', parseFloat(value) || 0)"
            >
              <q-input
                v-model="scope.value"
                type="number"
                dense
                autofocus
                prefix="Rp "
                @keyup.enter="scope.set"
              />
              <div class="float-right">
                <q-btn
                  size="sm"
                  color="red-9"
                  flat
                  icon="close"
                  @click="scope.cancel"
                />
                <q-btn
                  size="sm"
                  color="green-9"
                  flat
                  icon="check"
                  @click="scope.set"
                />
              </div>
            </q-popup-edit>
          </td>
          <td align="right">
            <span class="text-subtitle2">{{ formatCurrency(row.tarif_denda || 0) }}</span>
            <q-popup-edit
              v-model="row.tarif_denda"
              v-slot="scope"
              @save="(value) => update(row.id, 'tarif_denda', parseFloat(value) || 0)"
            >
              <q-input
                v-model="scope.value"
                type="number"
                dense
                autofocus
                prefix="Rp "
                @keyup.enter="scope.set"
              />
              <div class="float-right">
                <q-btn
                  size="sm"
                  color="red-9"
                  flat
                  icon="close"
                  @click="scope.cancel"
                />
                <q-btn
                  size="sm"
                  color="green-9"
                  flat
                  icon="check"
                  @click="scope.set"
                />
              </div>
            </q-popup-edit>
          </td>
          <td align="center">
            <q-toggle
              v-model="row.need_access"
              color="green"
              checked-icon="check"
              unchecked-icon="close"
              :true-value="1"
              :false-value="0"
              @update:model-value="
                (value) => update(row.id, 'need_access', value)
              "
            />
          </td>
          <td align="left">
            <span class="text-subtitle2">{{ row.keterangan || '-' }}</span>
            <q-popup-edit
              v-model="row.keterangan"
              v-slot="scope"
              @save="(value) => update(row.id, 'keterangan', value)"
            >
              <q-input
                v-model="scope.value"
                dense
                autofocus
                @keyup.enter="scope.set"
              />
              <div class="float-right">
                <q-btn
                  size="sm"
                  color="red-9"
                  flat
                  icon="close"
                  @click="scope.cancel"
                />
                <q-btn
                  size="sm"
                  color="green-9"
                  flat
                  icon="check"
                  @click="scope.set"
                />
              </div>
            </q-popup-edit>
          </td>
          <td align="center">
            <q-toggle
              v-model="row.status"
              color="green"
              checked-icon="check"
              unchecked-icon="close"
              :true-value="1"
              :false-value="0"
              @update:model-value="
                (value) => update(row.id, 'status', value)
              "
            />
          </td>
          <td align="right">
            <q-badge
              @click="onDelete(row.id)"
              text-color="white"
              class="q-ml-md cursor-pointer bg-transparent"
            >
              <q-icon name="delete" color="red" />
            </q-badge>
          </td>
        </tr>
      </template>
    </q-virtual-scroll>

    <q-card-section>
      <add-button title="Tambah Jenis Kendaraan Baru" style="z-index: 12">
        <template #form>
          <q-form @reset="onReset" class="q-gutter-md">
            <q-input
              filled
              v-model="newJenisKendaraan.jenis"
              label="Nama Jenis Kendaraan"
              required
            />
            <q-input
              filled
              v-model.number="newJenisKendaraan.tarif"
              type="number"
              label="Tarif per Jam"
              prefix="Rp "
              required
            />
            <q-input
              filled
              v-model.number="newJenisKendaraan.tarif_denda"
              type="number"
              label="Tarif Denda"
              prefix="Rp "
            />
            <q-select
              v-model="newJenisKendaraan.need_access"
              :options="[
                { value: 0, label: 'Tidak Perlu Akses Khusus' },
                { value: 1, label: 'Perlu Akses Khusus' },
              ]"
              emit-value
              map-options
              label="Akses Khusus"
              filled
            />
            <q-input
              filled
              v-model="newJenisKendaraan.keterangan"
              label="Keterangan"
              type="textarea"
              rows="3"
            />
            <q-select
              v-model="newJenisKendaraan.status"
              :options="[
                { value: 1, label: 'Aktif' },
                { value: 0, label: 'Tidak Aktif' },
              ]"
              emit-value
              map-options
              label="Status"
              filled
            />
          </q-form>
        </template>
        <template #button>
          <div class="row">
            <q-btn
              label="Simpan"
              type="submit"
              color="primary"
              @click="onSubmit"
            />
            <q-btn
              label="Reset"
              type="reset"
              color="secondary"
              flat
              class="q-ml-md"
              @click="onReset"
            />
          </div>
        </template>
      </add-button>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { useKendaraanStore } from "src/stores/kendaraan-store";
import { useComponentStore } from "src/stores/component-store";
import { onMounted, ref, computed } from "vue";
import { useQuasar } from "quasar";
import AddButton from "src/components/AddButton.vue";

const $q = useQuasar();
const kendaraanStore = useKendaraanStore();
const componentStore = useComponentStore();

const isLoading = computed(() => kendaraanStore.isLoading);

const columns = [
  { name: "ID", prop: "id", align: "left" },
  { name: "Jenis Kendaraan", prop: "jenis", align: "left" },
  { name: "Tarif/Jam", prop: "tarif", align: "right" },
  { name: "Tarif Denda", prop: "tarif_denda", align: "right" },
  { name: "Akses Khusus", prop: "need_access", align: "center" },
  { name: "Keterangan", prop: "keterangan", align: "left" },
  { name: "Status", prop: "status", align: "center" },
  { name: "Hapus", prop: "hapus", align: "right" },
];

const newJenisKendaraan = ref({
  jenis: "",
  tarif: 0,
  tarif_denda: 0,
  need_access: 0,
  keterangan: "",
  status: 1,
});

const onReset = () => {
  newJenisKendaraan.value = {
    jenis: "",
    tarif: 0,
    tarif_denda: 0,
    need_access: 0,
    keterangan: "",
    status: 1,
  };
};

const onSubmit = async () => {
  try {
    if (newJenisKendaraan.value.jenis && newJenisKendaraan.value.tarif > 0) {
      console.log('Adding new jenis kendaraan:', newJenisKendaraan.value);
      const success = await kendaraanStore.addJenisKendaraan(newJenisKendaraan.value);
      if (success) {
        onReset();
        componentStore.nextMorph();
      }
    } else {
      $q.notify({
        color: "negative",
        position: "top",
        message: "Nama jenis kendaraan dan tarif harus diisi",
        icon: "report_problem",
      });
    }
  } catch (error) {
    console.error('Error submitting jenis kendaraan:', error);
    $q.notify({
      color: "negative",
      position: "top",
      message: "Terjadi kesalahan saat menyimpan data",
      icon: "report_problem",
    });
  }
};

const update = async (id, column, value) => {
  console.log('Updating jenis kendaraan:', id, column, value);
  const success = await kendaraanStore.editJenisKendaraan(id, column, value);
  if (success) {
    $q.notify({
      message: "Berhasil diubah",
      type: "positive",
      position: "top",
    });
  } else {
    $q.notify({
      message: "Gagal mengubah data",
      type: "negative",
      position: "top",
    });
  }
};

const onDelete = async (id) => {
  console.log('Deleting jenis kendaraan:', id);
  
  // Confirm deletion
  $q.dialog({
    title: 'Konfirmasi',
    message: 'Apakah Anda yakin ingin menghapus jenis kendaraan ini?',
    cancel: true,
    persistent: true
  }).onOk(async () => {
    const success = await kendaraanStore.deleteJenisKendaraan(id);
    if (success) {
      $q.notify({
        message: "Berhasil dihapus",
        type: "positive",
        position: "top",
      });
    } else {
      $q.notify({
        message: "Gagal menghapus data",
        type: "negative",
        position: "top",
      });
    }
  });
};

const jenisKendaraan = computed(() => {
  return (kendaraanStore.jenisKendaraan || []).sort((a, b) => a.jenis.localeCompare(b.jenis));
});

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR'
  }).format(amount);
};

onMounted(async () => {
  console.log('Loading jenis kendaraan data...');
  await kendaraanStore.getAllJenisKendaraan();
  console.log('Jenis kendaraan data loaded:', kendaraanStore.jenisKendaraan.length);
});
</script>

<style lang="sass">
.thead-sticky tr > *,
.tfoot-sticky tr > *
  position: sticky
  opacity: 1
  z-index: 1

.thead-sticky tr:last-child > *
  top: 0

.tfoot-sticky tr:first-child > *
  bottom: 0
</style>
