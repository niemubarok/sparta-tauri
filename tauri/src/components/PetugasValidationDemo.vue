<template>
  <q-card>
    <q-card-section>
      <div class="text-h6 q-mb-md">
        <q-icon name="verified_user" class="q-mr-sm" />
        Petugas Form with Validation
      </div>
      
      <q-form @submit="onSubmit" class="q-gutter-md">
        <div class="row q-gutter-md">
          <div class="col-12 col-md-5">
            <q-input
              v-model="form.nama"
              label="Nama Lengkap"
              filled
              :error="!!errors.nama"
              :error-message="errors.nama"
              @blur="validateField('nama')"
            />
          </div>
          
          <div class="col-12 col-md-6">
            <q-input
              v-model="form.username"
              label="Username"
              filled
              :error="!!errors.username"
              :error-message="errors.username"
              @blur="validateField('username')"
            />
          </div>
        </div>

        <div class="row q-gutter-md">
          <div class="col-12 col-md-5">
            <q-input
              v-model="form.password"
              label="Password"
              type="password"
              filled
              :error="!!errors.password"
              :error-message="errors.password"
              @blur="validateField('password')"
            />
          </div>
          
          <div class="col-12 col-md-6">
            <q-input
              v-model="form.no_hp"
              label="Nomor HP"
              filled
              :error="!!errors.no_hp"
              :error-message="errors.no_hp"
              @blur="validateField('no_hp')"
            />
          </div>
        </div>

        <div class="row q-gutter-md">
          <div class="col-12 col-md-5">
            <q-select
              v-model="form.level_code"
              label="Level User"
              :options="levelOptions"
              option-value="level_code"
              option-label="level_name"
              emit-value
              map-options
              filled
              :error="!!errors.level_code"
              :error-message="errors.level_code"
              @blur="validateField('level_code')"
            />
          </div>
          
          <div class="col-12 col-md-6">
            <q-toggle
              v-model="form.status"
              label="Status Aktif"
              :true-value="1"
              :false-value="0"
            />
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <q-btn
              type="submit"
              color="primary"
              label="Validate & Save"
              icon="save"
              :loading="loading"
              :disable="!isFormValid"
            />
            <q-btn
              color="grey"
              label="Reset"
              icon="refresh"
              class="q-ml-sm"
              @click="resetForm"
            />
          </div>
        </div>
      </q-form>

      <!-- Validation Summary -->
      <q-card v-if="validationResult" class="q-mt-md" :class="validationResult.isValid ? 'bg-green-1' : 'bg-red-1'">
        <q-card-section>
          <div class="text-subtitle1 q-mb-sm">
            <q-icon :name="validationResult.isValid ? 'check_circle' : 'error'" class="q-mr-sm" />
            Validation Result
          </div>
          
          <div v-if="validationResult.isValid" class="text-green-8">
            ✅ All fields are valid!
          </div>
          
          <div v-else>
            <div class="text-red-8 q-mb-sm">❌ Please fix the following errors:</div>
            <ul class="text-red-7">
              <li v-for="error in validationResult.errors" :key="error">{{ error }}</li>
            </ul>
          </div>
        </q-card-section>
      </q-card>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { usePetugasStore } from 'src/stores/petugas-store';

const $q = useQuasar();
const petugasStore = usePetugasStore();

const loading = ref(false);
const validationResult = ref(null);

const form = ref({
  nama: '',
  username: '',
  password: '',
  no_hp: '',
  level_code: '',
  status: 1
});

const errors = ref({
  nama: '',
  username: '',
  password: '',
  no_hp: '',
  level_code: ''
});

const levelOptions = computed(() => petugasStore.daftarLevel);

const isFormValid = computed(() => {
  return Object.values(errors.value).every(error => !error) &&
         Object.values(form.value).every(value => value !== '');
});

const validateField = async (fieldName) => {
  errors.value[fieldName] = '';
  
  // Custom validation per field
  switch (fieldName) {
    case 'nama':
      if (!form.value.nama || form.value.nama.trim().length < 2) {
        errors.value.nama = 'Nama minimal 2 karakter';
      }
      break;
      
    case 'username':
      if (!form.value.username || form.value.username.trim().length < 3) {
        errors.value.username = 'Username minimal 3 karakter';
      } else {
        // Check if username exists
        const exists = await petugasStore.isUsernameExists(form.value.username);
        if (exists) {
          errors.value.username = 'Username sudah digunakan';
        }
      }
      break;
      
    case 'password':
      if (!form.value.password || form.value.password.length < 6) {
        errors.value.password = 'Password minimal 6 karakter';
      }
      break;
      
    case 'no_hp':
      if (!form.value.no_hp || !/^[\d\+\-\s]+$/.test(form.value.no_hp)) {
        errors.value.no_hp = 'Nomor HP tidak valid';
      }
      break;
      
    case 'level_code':
      if (!form.value.level_code) {
        errors.value.level_code = 'Level user harus dipilih';
      }
      break;
  }
};

const validateForm = () => {
  const result = petugasStore.validatePetugas(form.value);
  validationResult.value = result;
  
  if (!result.isValid) {
    // Map validation errors to form fields
    result.errors.forEach(error => {
      if (error.includes('Nama')) errors.value.nama = error;
      if (error.includes('Username')) errors.value.username = error;
      if (error.includes('Password')) errors.value.password = error;
      if (error.includes('HP')) errors.value.no_hp = error;
      if (error.includes('Level')) errors.value.level_code = error;
    });
  }
  
  return result.isValid;
};

const onSubmit = async () => {
  loading.value = true;
  
  try {
    const isValid = validateForm();
    
    if (isValid) {
      await petugasStore.addMasterPetugasToDB(form.value);
      
      $q.notify({
        type: 'positive',
        message: 'Petugas berhasil ditambahkan',
        icon: 'check'
      });
      
      resetForm();
    } else {
      $q.notify({
        type: 'negative',
        message: 'Please fix validation errors',
        icon: 'error'
      });
    }
  } catch (error) {
    console.error('Error saving petugas:', error);
    $q.notify({
      type: 'negative',
      message: 'Failed to save petugas',
      caption: error.message,
      icon: 'error'
    });
  } finally {
    loading.value = false;
  }
};

const resetForm = () => {
  form.value = {
    nama: '',
    username: '',
    password: '',
    no_hp: '',
    level_code: '',
    status: 1
  };
  
  errors.value = {
    nama: '',
    username: '',
    password: '',
    no_hp: '',
    level_code: ''
  };
  
  validationResult.value = null;
};

onMounted(async () => {
  await petugasStore.loadFromLocal();
});
</script>
