<template>
  <q-page padding>
    <div class="q-pa-md">
      <div class="row">
        <q-btn
        flat
        dense
        to="/"
        color="primary"
        icon="arrow_back"
        class="q-mb-md"
        />
        
        <h5 class="q-mt-none q-mb-md text-black">Manajemen Member</h5>
      </div>
      
      <div class="row justify-between q-mb-md">
        <q-input
          v-model="searchText"
          dense
          outlined
          placeholder="Cari member..."
          class="col-grow q-mr-sm"
        >
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
        
        <q-btn
          color="primary"
          icon="add"
          label="Tambah Member"
          @click="showAddNewMemberDialog = true"
        />
      </div>

      <q-table
        :rows="members"
        :columns="columns"
        row-key="index"
        :loading="loading"
        :filter="searchText"
      >
      <template v-slot:body-cell-index="props">
          <q-td :props="props">
            {{ props.pageIndex  + 1 }}
          </q-td>
        </template>
        <template v-slot:body-cell-membership_type="props">
          <q-td :props="props">
            {{ getMembershipTypeName(props.row.membership_type_id) }}
          </q-td>
        </template>
        <template v-slot:body-cell-status="props">
          <q-td :props="props">
            <q-badge
              :color="props.row.active ? 'green' : 'red'"
              text-color="white"
            >
              {{ props.row.active ? 'Active' : 'Inactive' }}
            </q-badge>
          </q-td>
        </template>
        <template v-slot:body-cell-actions="props">
          <q-td :props="props">
            <q-btn-group flat>
              <q-btn
                flat
                round
                color="primary"
                icon="edit"
                @click="editMember(props.row)"
              />
              <q-btn
                flat
                round
                color="negative"
                icon="delete"
                @click="confirmDelete(props.row)"
              />
            </q-btn-group>
          </q-td>
        </template>
        <template v-slot:body-cell-vehicles="props">
          <q-td :props="props">
            <div v-for="(vehicle, index) in props.row.vehicles" :key="index">
              <q-chip
                square
                size="sm"
                :icon="vehicle.type === 'Motor' ? 'two_wheeler' : 'directions_car'"
              >
                {{ vehicle.license_plate }}
              </q-chip>
            </div>
          </q-td>
        </template>
      </q-table>
    </div>

    <q-dialog v-model="showAddNewMemberDialog" persistent>
      <q-card style="min-width: 350px">
        <q-card-section>
          <div class="text-h6">{{ isEditing ? 'Edit Member' : 'Tambah Member Baru' }}</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="saveMember">
            <div class="row q-col-gutter-md">
              <q-input
                v-model="newMemberform.name"
                class="col-12"
                label="Nama"
                :rules="[val => !!val || 'Nama harus diisi']"
              />
              <q-input
                v-model="newMemberform.address"
                class="col-12"
                type="textarea"
                label="Alamat"
              />
              <q-input
                v-model="newMemberform.phone"
                class="col-12"
                label="Telepon"
              />

               <q-select
                v-model="newMemberform.membership_type_id"
                class="col-12"
                label="Jenis Member"
                :options="membershipTypes"
                emit-value
                map-options
                option-value="_id"
                option-label="name"
                :rules="[val => !!val || 'Jenis Member harus dipilih']"
              >
                <template v-slot:append>
                  <q-btn
                    flat
                    icon="add"
                    @click="showAddTypeDialog = true"
                    class="q-ml-sm"
                  />
                </template>
              </q-select>

              <div class="col-12">
                <div class="row items-center q-mb-sm">
                  <div class="text-subtitle2">Kendaraan</div>
                  <q-btn
                    flat
                    round
                    color="primary"
                    icon="add"
                    size="sm"
                    class="q-ml-sm"
                    @click="addVehicle"
                  />
                </div>
                
                <div 
                  v-for="(vehicle, index) in newMemberform.vehicles" 
                  :key="index"
                  class="row q-col-gutter-sm q-mb-sm"
                >
                  <q-select
                    v-model="vehicle.type"
                    class="col-5"
                    label="Jenis Kendaraan"
                    :options="['Mobil', 'Motor', 'Truk']"
                    :rules="[val => !!val || 'Jenis kendaraan harus dipilih']"
                  />
                    <q-input
                    v-model="vehicle.license_plate"
                    class="col-5"
                    label="Nomor Polisi"
                    :rules="[val => !!val || 'Nomor polisi harus diisi']"
                    />
                  <div class="col-2 flex items-center">
                    <q-btn
                      v-if="newMemberform.vehicles.length > 1"
                      flat
                      round
                      color="negative"
                      icon="delete"
                      size="sm"
                      @click="removeVehicle(index)"
                    />
                  </div>
                </div>
              </div>
             
              <q-input
                v-model="newMemberform.start_date"
                class="col-6"
                label="Tanggal Mulai"
                type="date"
                :rules="[val => !!val || 'Tanggal mulai harus diisi']"
              />
              <q-input
                v-model="newMemberform.end_date"
                class="col-6"
                label="Tanggal Berakhir"
                type="date"
                :rules="[val => !!val || 'Tanggal berakhir harus diisi']"
              />
              
            </div>
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Batal" color="primary" v-close-popup />
          <q-btn flat label="Simpan" color="primary" @click="saveMember" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="showAddTypeDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Tambah Jenis Member</div>
        </q-card-section>

        <q-card-section>
          <q-form @submit="saveNewType">
            <div class="row q-col-gutter-md">
              <q-input
                v-model="membershipStore.newTypeModel.name"
                class="col-12"
                label="Nama Jenis"
                :rules="[val => !!val || 'Nama jenis harus diisi']"
              />
              <q-input
                v-model="membershipStore.newTypeModel.price"
                class="col-12"
                label="Harga"
                type="number"
                :rules="[val => !!val || 'Harga harus diisi']"
              />
              
              <q-select
                v-model="membershipStore.newTypeModel.area_type"
                class="col-6"
                label="Tipe Area"
                :options="['Residensial', 'Komersial']"
                :rules="[val => !!val || 'Tipe area harus dipilih']"
              />
              <q-input
                v-model="membershipStore.newTypeModel.max_vehicles"
                class="col-6"
                label="Maksimal Kendaraan"
                type="number"
                min="1"
                :rules="[val => val > 0 || 'Harus lebih dari 0']"
              />
              <div class="col-6">
                <q-input
                  v-model="membershipStore.newTypeModel.operating_hours.start"
                  label="Jam Operasional Mulai"
                  type="time"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model="membershipStore.newTypeModel.operating_hours.end"
                  label="Jam Operasional Selesai"
                  type="time"
                />
              </div>
              <q-input
                v-model="membershipStore.newTypeModel.description"
                class="col-12"
                label="Deskripsi"
                type="textarea"
              />
              <q-select
                v-model="membershipStore.newTypeModel.facilities"
                class="col-12"
                label="Fasilitas"
                multiple
                :options="['CCTV', 'Keamanan', 'Valet', 'Cuci Mobil', 'Pengisian EV']"
              />
            </div>
          </q-form>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Batal" color="primary" v-close-popup />
          <q-btn flat label="Simpan" color="primary" @click="saveNewType" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useQuasar } from 'quasar'
import { useMembershipStore } from 'src/stores/membership-store'

const $q = useQuasar()
const membershipStore = useMembershipStore()
const searchText = ref('')
const showAddNewMemberDialog = ref(false)
const isEditing = ref(false)

// Use store refs
const members = computed(() => membershipStore.members)
const membershipTypes = computed(() => membershipStore.membershipTypes)
const loading = computed(() => membershipStore.loading)

const columns = [
  { 
    name: 'index', 
    label: 'No', 
    field: 'index',
    sortable: true
  },
  { name: 'name', label: 'Nama', field: 'name', sortable: true },
  { name: 'address', label: 'Alamat', field: 'address', sortable: true },
  { name: 'phone', label: 'Telepon', field: 'phone', sortable: true },
  { 
    name: 'vehicles', 
    label: 'Kendaraan', 
    field: 'vehicles',
    format: val => val.map(v => `${v.type} (${v.license_plate})`).join(', ')
  },
  { name: 'membership_type', label: 'Tipe Member', field: row => getMembershipTypeName(row.membership_type_id) },
  { name: 'start_date', label: 'Tanggal Mulai', field: 'start_date', sortable: true },
  { name: 'end_date', label: 'Tanggal Berakhir', field: 'end_date', sortable: true },
  { name: 'status', label: 'Status', field: row => row.active ? 'Active' : 'Inactive' },
  { name: 'actions', label: 'Actions', field: 'actions' }
]

const newMemberform = ref({
  name: '',
  vehicles: [{ 
    type: '',
    license_plate: ''
  }],
  membership_type_id: '',
  start_date: '',
  end_date: '',
  address: '',
  phone: '',
  active: 1
})

const getMembershipTypeName = (id) => {
  const type = membershipTypes.value.find(t => t._id === id)
  return type ? type.name : ''
}

const showAddTypeDialog = ref(false)


// Add this new method
const saveNewType = async () => {
  console.log("🚀 ~ saveNewType ~ newTypeModel:", membershipStore.newTypeModel)
  try {
    await membershipStore.addMembershipType(membershipStore.newTypeModel)
    $q.notify({
      type: 'positive',
      message: 'Membership type added successfully'
    })
    showAddTypeDialog.value = false
    membershipStore.newTypeModel= {
      name: '',
      price: 0,
      area_type: '', // 'residential' or 'commercial'
      max_vehicles: 1, // Maximum vehicles allowed
      operating_hours: {
        start: '00:00',
        end: '23:59'
      },
      description: '', // Additional notes/description
      facilities: [] // Array of included facilities/features
    }
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to add membership type'
    })
  }
}

const editMember = (member) => {
  isEditing.value = true
  newMemberform.value = { ...member }
  showAddNewMemberDialog.value = true
}

const saveMember = async () => {
  try {
    const memberData = {
        ...newMemberform.value,
        vehicles: newMemberform.value.vehicles.map(vehicle => ({
          ...vehicle,
          license_plate: vehicle.license_plate.toUpperCase()
        }))
      }
    // console.log("🚀 ~ saveMember ~ memberData:", memberData)
    // return
    if (isEditing.value) {
      await membershipStore.updateMember(memberData._id, memberData)
    } else {
      await membershipStore.addMember(memberData)
    }
    
    $q.notify({
      type: 'positive',
      message: `Member ${isEditing.value ? 'updated' : 'added'} successfully`
    })
    
    showAddNewMemberDialog.value = false
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: `Failed to ${isEditing.value ? 'update' : 'add'} member`
    })
  }
}

const confirmDelete = (member) => {
  $q.dialog({
    title: 'Confirm Deletion',
    message: `Are you sure you want to delete member ${member.nama}?`,
    ok: 'Delete',
    cancel: 'Cancel'
  }).onOk(async () => {
    try {
      await membershipStore.deleteMember(member._id)
      $q.notify({
        type: 'positive',
        message: 'Member deleted successfully'
      })
    } catch (error) {
      $q.notify({
        type: 'negative',
        message: 'Failed to delete member'
      })
    }
  })
}

const addVehicle = () => {
  const membershipType = membershipTypes.value.find(t => t._id === newMemberform.value.membership_type._id)
  if (!membershipType) {
    $q.notify({
      type: 'warning',
      message: 'Pilih tipe membership terlebih dahulu'
    })
    return
  }
  
  if (newMemberform.value.vehicles.length >= membershipType.max_vehicles) {
    $q.notify({
      type: 'warning',
      message: `Maksimal ${membershipType.max_vehicles} kendaraan untuk tipe membership ini`
    })
    return
  }
  
  newMemberform.value.vehicles.push({ type: '', license_plate: '' })
}

const removeVehicle = (index) => {
  newMemberform.value.vehicles.splice(index, 1)
}

onMounted(async () => {
  await Promise.all([
    membershipStore.loadMembers(),
    membershipStore.loadMembershipTypes()
  ])
})
</script>