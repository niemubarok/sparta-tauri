<template>
  <q-card class="q-ml-xl">
    <q-card-section class="row">
      <div>
        <q-chip
          icon="person"
          label="Daftar Petugas"
          class="text-weight-bolder"
        />
      </div>
      <q-space />
      <div :style="!$q.screen.gt.sm ? '' : 'margin-top:10px;'">
        <q-space v-if="$q.screen.lt.sm" />
        <!-- <q-btn
          v-model:selected="todaySelected"
          style="z-index: 1"
          class="shadow-4 q-ma-sm"
          rounded
          :class="isToday ? 'bg-secondary text-white' : 'bg-grey-7 text-grey-2'"
          dark
          @click="todayBtn()"
          >username Ini</q-btn
        >
        <q-btn
          style="z-index: 2"
          icon="event"
          rounded
          :label="startDateSelected ? startDateLabel() : 'Pilih Tanggal'"
          :class="
            startDateSelected && !todaySelected
              ? 'bg-secondary text-white'
              : 'bg-grey-7 text-grey-2'
          "
        >
          <q-popup-proxy
            transition-show="scale"
            transition-hide="scale"
            class="z-max"
            @before-show="updateProxy"
          >
            <q-date v-model="proxyDate" :options="optionFn">
              <div class="row items-center justify-end q-gutter-sm">
                <q-btn
                  v-close-popup
                  label="Cancel"
                  color="primary"
                  flat
                  @click="
                    startDateSelected = false;
                    endDateSelected = false;
                  "
                />
                <q-btn
                  v-close-popup
                  label="OK"
                  color="primary"
                  flat
                  @click="save('start')"
                />
              </div>
            </q-date>
          </q-popup-proxy>
        </q-btn>
        <span class="q-mx-sm">s/d</span>
        <q-btn
          style="z-index: 2"
          icon="event"
          rounded
          :label="endDateSelected ? endDateLabel() : 'Pilih Tanggal'"
          :class="
            endDateSelected && !todaySelected
              ? 'bg-secondary text-white'
              : 'bg-grey-7 text-grey-2'
          "
        >
          <q-popup-proxy
            transition-show="scale"
            transition-hide="scale"
            class="z-max"
            @before-show="updateProxy"
          >
            <q-date v-model="proxyDate" :options="optionFn">
              <div class="row items-center justify-end q-gutter-sm">
                <q-btn v-close-popup label="Cancel" color="primary" flat />
                <q-btn
                  v-close-popup
                  label="OK"
                  color="primary"
                  flat
                  @click="save('end')"
                />
              </div>
            </q-date>
          </q-popup-proxy>
        </q-btn> -->
      </div>
    </q-card-section>

    <q-virtual-scroll
      type="table"
      :style="$q.screen.gt.md ? 'height: 75vh' : 'height: 70vh'"
      :virtual-scroll-item-size="48"
      :virtual-scroll-sticky-size-start="48"
      :virtual-scroll-sticky-size-end="32"
      :items="daftarPetugas"
      :loading="isLoading"
      sort-by="nama"
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

      <template v-if="!daftarPetugas?.length" v-slot:after>
        <tr>
          {{
            daftarPetugas
          }}
          <td align="center" colspan="7" class="text-grey-5">
            <h5>Tidak ada Data petugas</h5>
          </td>
        </tr>
      </template>
      <!-- class="glass-light" -->
      <template v-slot="{ item: row, index }">
        <tr :key="index" :class="index % 2 == 0 ? 'bg-white' : 'bg-grey-2'">
          <td>{{ row.id_petugas }}</td>
          <td align="left">
            <span class="text-subtitle2">{{ row.nama }}</span>
            <!-- v-if="isEditMode" -->
            <q-popup-edit
              v-model="row.nama"
              v-slot="scope"
              @save="(value) => update(row.id_petugas, 'nama', value)"
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
          <!-- <td align="center">
            <span class="text-center text-subtitle2">{{ row.no_hp }}</span>
          </td> -->
          <td align="left" width="140px">
            <div class="row justify-between">
              <span class="text-subtitle2"> {{ row.no_hp }}</span>
            </div>
            <q-popup-edit
              v-model="row.no_hp"
              v-slot="scope"
              @save="(value) => update(row.id_petugas, 'no_hp', value)"
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
          <td align="left">
            <span class="text-subtitle2"> {{ row.username }}</span>
            <q-popup-edit
              v-model="row.username"
              v-slot="scope"
              @save="(value) => update(row.id_petugas, 'username', value)"
            >
              <q-input filled v-model="scope.value" label="username" />
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
          <td align="left">
            <span class="text-subtitle2"> {{ row.password }}</span>
            <q-popup-edit
              v-model="row.password"
              v-slot="scope"
              @save="(value) => update(row.id_petugas, 'password', value)"
            >
              <q-input
                filled
                v-model="scope.value"
                type="password"
                label="Password"
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
          <td align="left">
            <span class="text-subtitle2"> {{ row.level_name }}</span>
            <q-popup-edit
              v-model="row.level_name"
              v-slot="scope"
              @save="(value) => update(row.id_petugas, 'level_code', value)"
            >
              <q-select
                v-model="scope.value"
                :options="[
                  { value: '0001', label: 'Administrator' },
                  { value: '0002', label: 'Leader' },
                  { value: '0003', label: 'Supervisor' },
                  { value: '0005', label: 'Cashier' },
                ]"
                label="Level Pegawai"
                filled
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
            <!-- <q-toggle
              v-if="row.status.value"
              v-model="row.status.value"
              :disable="row.level_code === '0001'"
              color="green"
              checked-icon="check"
              unchecked-icon="close"
              :true-value="1"
              :false-value="0"
              @update:model-value="
                (value) => update(row.id_petugas, 'status', value)
              "
            /> -->
            <!-- v-else -->
            <q-toggle
              v-model="row.status"
              :disable="row.level_code === '0001'"
              color="green"
              checked-icon="check"
              unchecked-icon="close"
              :true-value="1"
              :false-value="0"
              @update:model-value="
                (value) => update(row.id_petugas, 'status', value)
              "
            />
          </td>

          <td align="right">
            <q-badge
              @click="onDelete(row.id_petugas)"
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
      <add-button title="Tambah Petugas Baru" style="z-index: 12">
        <template #form>
          <q-form @reset="onReset" class="q-gutter-md">
            <q-input
              filled
              v-model="newPetugas.id_petugas"
              label="Nomor Induk Pegawai"
            />
            <q-input
              filled
              v-model="newPetugas.nama"
              label="Nama Lengkap Petugas"
            />
            <q-input
              filled
              v-model="newPetugas.no_hp"
              label="Nomor Handphone Petugas"
            />
            <q-input filled v-model="newPetugas.username" label="username" />
            <q-input filled v-model="newPetugas.password" label="password" />
            <q-select
              v-model="newPetugas.status"
              :options="[
                { value: 1, label: 'Aktif' },
                { value: 0, label: 'Tidak Aktif' },
              ]"
              emit-value
              map-options
              label="Status"
              filled
            />
            <q-select
              v-model="newPetugas.level_code"
              :options="[
                { value: '0001', label: 'Administrator' },
                { value: '0002', label: 'Leader' },
                { value: '0003', label: 'Supervisor' },
                { value: '0005', label: 'Cashier' },
              ]"
              emit-value
              map-options
              label="Level Pegawai"
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
// import { userStore } from "src/stores/user-store";
import { useComponentStore } from "src/stores/component-store";
import { useTransaksiStore } from "src/stores/transaksi-store";
import { onMounted, ref, computed } from "vue";
import { date, useQuasar } from "quasar";
import AddButton from "src/components/AddButton.vue";
import { userStore } from "src/stores/user-store";

const $q = useQuasar();
const isLoading = ref(true);
const columns = [
  { name: "NIP", prop: "nip", align: "left" },
  { name: "Nama Petugas", prop: "nama", align: "left" },
  { name: "No. HP", prop: "no_phone", align: "left" },
  { name: "Username", prop: "username", align: "left" },
  { name: "Password", prop: "password", align: "left" },
  { name: "Level Pegawai", prop: "level_name", align: "left" },
  { name: "Status", prop: "status", align: "center" },
  { name: "Hapus", prop: "hapus", align: "right" },
];

const newPetugas = ref({
  id_petugas: "",
  nama: "",
  no_hp: 0,
  username: "",
  password: "",
  status: "",
  level_code: "",
});

const onReset = () => {
  newPetugas.value = {
    id_petugas: "",
    nama: "",
    no_hp: 0,
    username: "",
    password: "",
    status: "",
    level_code: "",
  };
};

const onSubmit = async () => {
  try {
    if (
      newPetugas.value.nama &&
      newPetugas.value.password &&
      newPetugas.value.username &&
      newPetugas.value.status &&
      newPetugas.value.level_code
    ) {
      console.log(newPetugas.value);
      await userStore().addMasterPetugasToDB(newPetugas.value);
      onReset();
      useComponentStore().nextMorph();
    } else {
      $q.notify({
        color: "negative",
        position: "top",
        message: "Semua field harus diisi ",
        icon: "report_problem",
      });
    }
  } catch (error) {}
};

const update = async (id, column, value) => {
  console.log(id, column, value);
  const editMasterPetugas = await userStore().editMasterPetugasOnDB(
    id,
    column,
    value
  );
  if (editMasterPetugas) {
    $q.notify({
      message: "Berhasil di ubah",
      type: "positive",
      position: "top",
    });
  }
};

const onDelete = async (id) => {
  console.log(id);
  const deleted = await userStore().deleteMasterPetugasFromDB(id);
  if (deleted) {
    $q.notify({
      message: "Berhasil di hapus",
      type: "positive",
      position: "top",
    });
  } else {
    $q.notify({
      message: "Gagal hapus data",
      type: "negative",
      position: "top",
    });
  }
};

const daftarPetugas = computed(() => {
  return userStore().daftarPetugas.sort((a, b) => a.nama.localeCompare(b.nama));
});

onMounted(async () => {
  await userStore().getAllPetugas();
  isLoading.value = false;
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
