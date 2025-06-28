<template>
  <q-card class="q-mb-lg">
    <q-card-section class="bg-blue-1">
      <div class="text-h6 text-primary">
        <q-icon name="database" class="q-mr-sm" />
        Inisialisasi Database Member
      </div>
      <p class="text-grey-7 q-mb-none">
        Database member belum diinisialisasi. Klik tombol di bawah untuk membuat struktur database dan data contoh.
      </p>
    </q-card-section>

    <q-card-section>
      <div class="row q-col-gutter-md">
        <div class="col-xs-12 col-md-6">
          <q-btn
            color="primary"
            icon="rocket_launch"
            label="Inisialisasi dengan Data Contoh"
            @click="initializeWithSampleData"
            :loading="isInitializing"
            :disable="isInitializing"
            class="full-width"
          />
          <p class="text-caption text-grey-6 q-mt-sm">
            Membuat struktur database dan menambahkan data contoh (4 tipe membership, 2 member contoh)
          </p>
        </div>
        
        <div class="col-xs-12 col-md-6">
          <q-btn
            color="secondary"
            icon="settings"
            label="Inisialisasi Database Kosong"
            @click="initializeEmptyDatabase"
            :loading="isInitializing"
            :disable="isInitializing"
            outline
            class="full-width"
          />
          <p class="text-caption text-grey-6 q-mt-sm">
            Hanya membuat struktur database tanpa data contoh
          </p>
        </div>
      </div>
    </q-card-section>

    <q-card-section v-if="initStatus" class="q-pt-none">
      <q-banner 
        :class="`bg-${initStatus.type}-1 text-${initStatus.type}`"
        rounded
      >
        <template v-slot:avatar>
          <q-icon 
            :name="initStatus.type === 'positive' ? 'check_circle' : 'error'" 
            :color="initStatus.type"
          />
        </template>
        {{ initStatus.message }}
      </q-banner>
    </q-card-section>
  </q-card>
</template>

<script>
import { ref } from 'vue'
import { useMembershipStore } from 'src/stores/membership-store'
import { useQuasar } from 'quasar'

export default {
  name: 'DatabaseInitializer',
  emits: ['member-database-initialized'],
  
  setup(props, { emit }) {
    const $q = useQuasar()
    const membershipStore = useMembershipStore()
    
    const isInitializing = ref(false)
    const initStatus = ref(null)
    
    const initializeWithSampleData = async () => {
      try {
        isInitializing.value = true
        initStatus.value = null
        
        $q.loading.show({
          message: 'Menginisialisasi database member dengan data contoh...'
        })
        
        // Initialize store first
        await membershipStore.initializeStore()
        
        // Initialize with sample data
        const result = await membershipStore.initializeSampleData()
        
        if (result) {
          initStatus.value = {
            type: 'positive',
            message: '✅ Database member berhasil diinisialisasi dengan data contoh!'
          }
          
          $q.notify({
            type: 'positive',
            message: 'Database member berhasil diinisialisasi dengan data contoh',
            icon: 'check_circle'
          })
          
          // Emit event to parent
          emit('member-database-initialized', { withSampleData: true })
        } else {
          initStatus.value = {
            type: 'warning',
            message: '⚠️ Database sudah memiliki data, inisialisasi dibatalkan'
          }
        }
      } catch (error) {
        console.error('Failed to initialize database with sample data:', error)
        
        initStatus.value = {
          type: 'negative',
          message: `❌ Gagal menginisialisasi database: ${error.message}`
        }
        
        $q.notify({
          type: 'negative',
          message: 'Gagal menginisialisasi database member',
          caption: error.message,
          icon: 'error'
        })
      } finally {
        isInitializing.value = false
        $q.loading.hide()
      }
    }
    
    const initializeEmptyDatabase = async () => {
      try {
        isInitializing.value = true
        initStatus.value = null
        
        $q.loading.show({
          message: 'Menginisialisasi struktur database member...'
        })
        
        // Initialize store (this will create indexes and load existing data)
        await membershipStore.initializeStore()
        
        initStatus.value = {
          type: 'positive',
          message: '✅ Struktur database member berhasil diinisialisasi!'
        }
        
        $q.notify({
          type: 'positive',
          message: 'Struktur database member berhasil diinisialisasi',
          icon: 'check_circle'
        })
        
        // Emit event to parent
        emit('member-database-initialized', { withSampleData: false })
      } catch (error) {
        console.error('Failed to initialize empty database:', error)
        
        initStatus.value = {
          type: 'negative',
          message: `❌ Gagal menginisialisasi struktur database: ${error.message}`
        }
        
        $q.notify({
          type: 'negative',
          message: 'Gagal menginisialisasi struktur database',
          caption: error.message,
          icon: 'error'
        })
      } finally {
        isInitializing.value = false
        $q.loading.hide()
      }
    }
    
    return {
      isInitializing,
      initStatus,
      initializeWithSampleData,
      initializeEmptyDatabase
    }
  }
}
</script>
