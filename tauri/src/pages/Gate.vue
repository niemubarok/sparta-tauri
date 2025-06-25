<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import ManlessEntryGate from 'src/components/ManlessEntryGate.vue'

import OutGatePage from 'src/pages/manual-gate.vue'
import ls from 'localstorage-slim'


const isManlessMode = ref(ls.get('manlessMode') || true)
const componentKey = ref(0)

// Force component re-render when mode changes
const handleModeChange = e => {
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

<template>
  <div>
    <Suspense>
      <template v-if="isManlessMode">
        <ManlessEntryGate 
          :key="componentKey" 
          class="full-width q-pa-md"
        />
      </template>
      <template v-else>
        <OutGatePage :key="componentKey" />
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

<style scoped>
.entry-gate-container {
  width: 100%;
  height: 100%;
  position: relative;
}
</style>
