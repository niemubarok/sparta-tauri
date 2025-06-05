<script setup>
import { invoke } from '@tauri-apps/api/core'
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const serialData = ref('')
const error = ref(null)
const isListening = ref(false)

// Function to handle serial port listening
async function listenToSerial() {
  if (!isListening.value) return
  
  try {
    const response = await invoke('listen_to_serial', { portName: 'COM14' })
    if (response) {
      serialData.value = response
      console.log('Serial data received:', response)
    }
  } catch (err) {
    error.value = err.message
    console.error('Serial error:', err)
  }
  
  // Continue listening if still enabled
  if (isListening.value) {
    setTimeout(listenToSerial, 100) // Poll every 100ms
  }
}

const onCreateSerial = async () => {
  try {
    await invoke('create_serial_port', { portName: 'COM14' })
    isListening.value = true
    listenToSerial()
  } catch (err) {
    error.value = err.message
    console.error('Failed to create serial port:', err)
  }
}

// Add this function to handle cleanup
async function cleanupSerial() {
  isListening.value = false
  try {
    await invoke('close_serial')
  } catch (err) {
    console.error('Error closing serial:', err)
  }
}

// Modify the router-link to use a method instead
async function navigateToDashboard() {
  await cleanupSerial()
  router.push('/dashboard')
}

// Start listening when component mounts
onMounted(async () => {
  try {
    await invoke('create_serial_port', { portName: 'COM14' })
    isListening.value = true
    listenToSerial()
  } catch (err) {
    error.value = err.message
    console.error('Failed to create serial port:', err)
  }
})

// Modify onUnmounted to use the cleanup function
onUnmounted(() => {
  cleanupSerial()
})
</script>

<template>
  <q-page class="row items-center justify-evenly">
    <div class="column items-center q-gutter-y-md">
      <!-- Status display -->
      <div v-if="error" class="text-negative">
        Error: {{ error }}
      </div>
      <div v-if="serialData" class="text-positive">
        Received: {{ serialData }}
      </div>

      <!-- Connection status -->
      <div :class="{ 'text-positive': isListening, 'text-negative': !isListening }">
        Serial Port: {{ isListening ? 'Connected' : 'Disconnected' }}
      </div>

      <!-- Replace the router-link with a button -->
      <q-btn 
        color="primary" 
        icon="dashboard" 
        label="Go to Dashboard"
        @click="navigateToDashboard" 
      />

      <!-- Control buttons -->
      <q-btn color="primary" icon="check" label="Turn On Output 1"
        @click="invoke('write_serial', { data: '*OUT1ON#' })" />
      <q-btn color="primary" icon="check" label="Turn Off Output 1"
        @click="invoke('write_serial', { data: '*OUT1OFF#' })" />
      <q-btn color="primary" icon="check" label="create serial"
        @click="onCreateSerial" />
      <q-btn color="primary" icon="check" label="print struk" 
        @click="invoke('print_struk', { printer_name: '04' })" />
    </div>
  </q-page>
</template>
