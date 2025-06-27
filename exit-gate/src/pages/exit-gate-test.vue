<template>
  <q-page class="flex column items-center justify-center bg-grey-1 q-pa-md">
    <!-- Simple Header -->
    <div class="text-h3 text-weight-bold text-primary q-mb-lg">
      Exit Gate System - Test
    </div>

    <!-- Basic Status -->
    <q-card class="q-mb-lg shadow-4" style="min-width: 400px">
      <q-card-section class="text-center">
        <div class="text-h5 q-mb-md">System Test</div>
        <div class="text-body1">
          If you can see this, the basic Vue component is working.
        </div>
      </q-card-section>
    </q-card>

    <!-- Test Services -->
    <q-card class="q-mb-lg shadow-4" style="min-width: 400px">
      <q-card-section>
        <div class="text-h6 q-mb-md">Service Status</div>
        <div class="q-gutter-md">
          <div>Database Service: {{ dbInitialized ? 'OK' : 'Loading...' }}</div>
          <div>Gate Service: {{ gateInitialized ? 'OK' : 'Loading...' }}</div>
          <div>Barcode Scanner: {{ scannerInitialized ? 'OK' : 'Loading...' }}</div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Navigation -->
    <q-card class="shadow-4" style="min-width: 400px">
      <q-card-section>
        <div class="text-h6 q-mb-md">Navigation Test</div>
        <div class="q-gutter-md">
          <q-btn 
            color="primary" 
            label="Go to Settings" 
            @click="$router.push('/Settings')"
          />
          <q-btn 
            color="secondary" 
            label="Load Full ExitGate" 
            @click="loadFullComponent"
          />
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Status flags
const dbInitialized = ref(false)
const gateInitialized = ref(false)
const scannerInitialized = ref(false)

onMounted(async () => {
  console.log('Test component mounted')
  
  try {
    // Test database service
    const { databaseService } = await import('../services/database')
    await databaseService.initialize()
    dbInitialized.value = true
    console.log('Database service initialized')
  } catch (error) {
    console.error('Database service error:', error)
  }

  try {
    // Test gate service
    const { gateService } = await import('../services/gate-service')
    gateInitialized.value = true
    console.log('Gate service initialized')
  } catch (error) {
    console.error('Gate service error:', error)
  }

  try {
    // Test barcode scanner
    const { barcodeScanner } = await import('../services/barcode-scanner')
    scannerInitialized.value = true
    console.log('Barcode scanner initialized')
  } catch (error) {
    console.error('Barcode scanner error:', error)
  }
})

function loadFullComponent() {
  router.push('/ExitGate')
}
</script>

<style scoped>
.q-page {
  min-height: 100vh;
}
</style>
