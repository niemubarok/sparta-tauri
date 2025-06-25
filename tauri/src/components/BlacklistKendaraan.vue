<template>
  <q-card class="q-ml-xl">
    <q-card-section class="row">
      <div>
        <q-chip
          icon="block"
          label="Blacklist Kendaraan"
          class="text-weight-bolder"
        />
      </div>
      <q-space />
      <div class="q-gutter-sm">
        <q-btn
          color="primary"
          icon="add"
          label="Tambah Blacklist"
          @click="showAddDialog = true"
        />
      </div>
    </q-card-section>

    <q-virtual-scroll
      type="table"
      :style="$q.screen.gt.md ? 'height: 75vh' : 'height: 70vh'"
      :virtual-scroll-item-size="48"
      :virtual-scroll-sticky-size-start="48"
      :virtual-scroll-sticky-size-end="32"
      :items="activeBlacklist"
      :loading="isLoading"
      sort-by="no_pol"
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

      <template v-if="!activeBlacklist?.length" v-slot:after>
        <tr>
          <td align="center" colspan="5" class="text-grey-5">
            <h5>Tidak ada kendaraan dalam blacklist</h5>
          </td>
        </tr>
      </template>

      <template v-slot="{ item: row, index }">
        <tr :key="index" :class="index % 2 == 0 ? 'bg-white' : 'bg-grey-2'">
          <td class="text-weight-bold">{{ row.no_pol }}</td>
          <td>{{ row.alasan || '-' }}</td>
          <td>{{ formatDate(row.tanggal_dibuat) }}</td>
          <td>{{ row.created_by || '-' }}</td>
          <td align="right">
            <q-btn
              size="sm"
              color="green"
              icon="check"
              label="Hapus dari Blacklist"
              @click="removeFromBlacklist(row.no_pol)"
            />
          </td>
        </tr>
      </template>
    </q-virtual-scroll>

    <!-- Add Blacklist Dialog -->
    <q-dialog v-model="showAddDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Tambah ke Blacklist</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-form @submit="addToBlacklist" class="q-gutter-md">
            <q-input
              filled
              v-model="newBlacklist.no_pol"
              label="Plat Nomor"
              required
              :rules="[val => val && val.length > 0 || 'Plat nomor harus diisi']"
              ref="nopolInput"
            />
            <q-input
              filled
              v-model="newBlacklist.alasan"
              label="Alasan"
              type="textarea"
              rows="3"
              required
              :rules="[val => val && val.length > 0 || 'Alasan harus diisi']"
            />
          </q-form>
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="Batal" @click="cancelAdd" />
          <q-btn flat label="Simpan" @click="addToBlacklist" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Search Dialog -->
    <q-dialog v-model="showSearchDialog" persistent>
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Cek Status Blacklist</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            filled
            v-model="searchNopol"
            label="Plat Nomor"
            @keyup.enter="checkBlacklist"
            ref="searchInput"
          >
            <template v-slot:append>
              <q-btn
                round
                dense
                flat
                icon="search"
                @click="checkBlacklist"
              />
            </template>
          </q-input>
          
          <div v-if="searchResult !== null" class="q-mt-md">
            <q-chip
              :color="searchResult ? 'red' : 'green'"
              text-color="white"
              :icon="searchResult ? 'block' : 'check'"
            >
              {{ searchResult ? 'DALAM BLACKLIST' : 'TIDAK DALAM BLACKLIST' }}
            </q-chip>
          </div>
        </q-card-section>

        <q-card-actions align="right" class="text-primary">
          <q-btn flat label="Tutup" @click="closeSearch" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Floating Action Button -->
    <q-page-sticky position="bottom-right" :offset="[18, 18]">
      <q-fab
        icon="search"
        direction="up"
        color="primary"
        @click="showSearchDialog = true"
      >
        <q-fab-action
          @click="showSearchDialog = true"
          color="primary"
          icon="search"
          label="Cek Blacklist"
        />
      </q-fab>
    </q-page-sticky>
  </q-card>
</template>

<script setup>
import { useKendaraanStore } from "src/stores/kendaraan-store";
import { onMounted, ref, computed } from "vue";
import { useQuasar } from "quasar";

const $q = useQuasar();
const kendaraanStore = useKendaraanStore();

const isLoading = ref(false);
const showAddDialog = ref(false);
const showSearchDialog = ref(false);
const searchNopol = ref('');
const searchResult = ref(null);

const columns = [
  { name: "Plat Nomor", prop: "no_pol", align: "left" },
  { name: "Alasan", prop: "alasan", align: "left" },
  { name: "Tanggal", prop: "tanggal_dibuat", align: "left" },
  { name: "Dibuat Oleh", prop: "created_by", align: "left" },
  { name: "Aksi", prop: "aksi", align: "right" },
];

const newBlacklist = ref({
  no_pol: "",
  alasan: "",
});

const activeBlacklist = computed(() => kendaraanStore.activeBlacklist);

const formatDate = (dateString) => {
  if (!dateString) return '-';
  try {
    return new Date(dateString).toLocaleDateString('id-ID', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return dateString;
  }
};

const addToBlacklist = async () => {
  if (!newBlacklist.value.no_pol || !newBlacklist.value.alasan) {
    $q.notify({
      color: "negative",
      position: "top",
      message: "Plat nomor dan alasan harus diisi",
      icon: "report_problem",
    });
    return;
  }

  try {
    const success = await kendaraanStore.addToBlacklist(
      newBlacklist.value.no_pol,
      newBlacklist.value.alasan
    );
    
    if (success) {
      showAddDialog.value = false;
      newBlacklist.value = { no_pol: "", alasan: "" };
    }
  } catch (error) {
    console.error('Error adding to blacklist:', error);
    $q.notify({
      color: "negative",
      position: "top",
      message: "Terjadi kesalahan saat menambah blacklist",
      icon: "report_problem",
    });
  }
};

const removeFromBlacklist = async (noPol) => {
  $q.dialog({
    title: 'Konfirmasi',
    message: `Apakah Anda yakin ingin menghapus ${noPol} dari blacklist?`,
    cancel: true,
    persistent: true
  }).onOk(async () => {
    try {
      const success = await kendaraanStore.removeFromBlacklist(noPol);
      if (success) {
        $q.notify({
          message: "Berhasil dihapus dari blacklist",
          type: "positive",
          position: "top",
        });
      }
    } catch (error) {
      console.error('Error removing from blacklist:', error);
      $q.notify({
        message: "Gagal menghapus dari blacklist",
        type: "negative",
        position: "top",
      });
    }
  });
};

const checkBlacklist = () => {
  if (!searchNopol.value) {
    $q.notify({
      color: "negative",
      position: "top",
      message: "Masukkan plat nomor",
      icon: "report_problem",
    });
    return;
  }

  searchResult.value = kendaraanStore.isBlacklisted(searchNopol.value);
};

const cancelAdd = () => {
  showAddDialog.value = false;
  newBlacklist.value = { no_pol: "", alasan: "" };
};

const closeSearch = () => {
  showSearchDialog.value = false;
  searchNopol.value = '';
  searchResult.value = null;
};

onMounted(async () => {
  console.log('Loading blacklist data...');
  await kendaraanStore.getAllBlacklist();
  console.log('Blacklist data loaded:', kendaraanStore.blacklistKendaraan.length);
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
