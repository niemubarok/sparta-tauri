<template>
  <div>
    <Suspense>
      <template v-if="isManlessMode">
        <ManlessExitGate
          class="full-width q-pa-md"
          :key="componentKey"
        />
      </template>
      <template v-else>
        <ExitPage :key="componentKey" />
      </template>
      
      <template #fallback>
        <div class="flex flex-center">
          <q-spinner size="3em" />
          <span class="q-ml-md">Loading...</span>
        </div>
      </template>
    </Suspense>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import ManlessExitGate from 'src/components/ManlessExitGate.vue'
import ExitPage from './ManualExitPage.vue'

import ls from 'localstorage-slim'

// const settingsStore = useSettingsStore(); // Tidak digunakan, manlessMode diambil dari localStorage
const isManlessMode = ref(ls.get('manlessMode') || true)
const componentKey = ref(0)

// Force component re-render when mode changes
const handleModeChange = (e) => {
  if (e.key === 'manlessMode') {
    isManlessMode.value = e.newValue === 'true'
    componentKey.value++ // Force re-render
  }
}

onMounted(() => {
  window.addEventListener('storage', handleModeChange)
})

onUnmounted(() => {
  window.removeEventListener('storage', handleModeChange)
})
</script>

<style scoped>
.exit-gate-container {
  width: 100%;
  height: 100%;
  position: relative;
}
</style>