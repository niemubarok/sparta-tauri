<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import ManualEntryGate from 'src/components/ManualEntryGate.vue'
// import { useSettingsStore } from 'src/stores/settings-store'
import ls from 'localstorage-slim'
import ManualExitPage from './ManualExitPage.vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// const settingsStore = useSettingsStore()
const isManlessMode = ref(ls.get('manlessMode') || true)
const componentKey = ref(Date.now()) // Use timestamp for unique key
const isVisible = ref(true) // Control visibility

// Force component re-render when mode changes
// const handleModeChange = e => {
//     if (e.key === 'manlessMode') {
//         isManlessMode.value = e.newValue === 'true'
//         componentKey.value = Date.now() // Force re-render with new timestamp
//     }
// }

// Watch for route changes and handle component visibility
// watch(() => router.currentRoute.value.path, (newPath) => {
//   if (newPath !== '/manual-entry-gate') {
//     // Hide component and force cleanup when leaving entry-gate route
//     isVisible.value = false
//     componentKey.value = Date.now()
//   } else {
//     // Show component when entering entry-gate route
//     isVisible.value = true
//     componentKey.value = Date.now()
//   }
// })

// onMounted(() => {
//     window.addEventListener('storage', handleModeChange)
//     isVisible.value = true
//     componentKey.value = Date.now()
// })

// onUnmounted(() => {
//     window.removeEventListener('storage', handleModeChange)
//     isVisible.value = false
// })
</script>

<template>
        <ManualEntryGate
          :key="componentKey"
          class="full-width q-pa-md"
        />
</template>

<style scoped>
.exit-gate-container {
  width: 100%;
  height: 100%;
  position: relative;
}
</style>
