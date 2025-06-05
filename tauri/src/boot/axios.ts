/* eslint-disable no-console */
/* eslint-disable import/no-mutable-exports */
import { boot } from 'quasar/wrappers'
import type { AxiosInstance } from 'axios'
import axios from 'axios'
import ls from 'localstorage-slim'
import type { Ref } from 'vue'
import { ref } from 'vue'
import { Notify } from 'quasar'
import { listen } from '@tauri-apps/api/event'

// Create global connection status for ALPR only
export const isBackendConnected: Ref<boolean> = ref(false)
export const isAlprConnected: Ref<boolean> = ref(false)

// ALPR connection status and data
export const alprConnectionStatus: Ref<boolean> = ref(false)
export const detectedPlates: Ref<any[]> = ref([])
export const cameraList: Ref<any[]> = ref([])

// Default config type
interface AxiosConfig { headers: { 'Content-Type': string } }

// Default config
const defaultConfig: AxiosConfig = { headers: { 'Content-Type': 'application/json' } }

// Create axios instances with default config
const api: AxiosInstance = axios.create({ 
    ...defaultConfig,
    baseURL: ls.get('API_URL') || process.env.API_SERVICE_URL,
})

const alpr: AxiosInstance = axios.create({ 
    ...defaultConfig,
    baseURL: ls.get('ALPR_URL') || process.env.ALPR_SERVICE_URL, 
})

// Add response interceptors for ALPR server
alpr.interceptors.response.use(
    response => {
        isAlprConnected.value = true
        return response
    },
    error => {
        if (!error.response || error.code === 'ERR_NETWORK') {
            isAlprConnected.value = false
        }
        return Promise.reject(error)
    },
)

// Initialize Tauri ALPR listeners
let alprListeners: (()=> void)[] = []

const initializeALPRListeners = async() => {
    try {
        // Listen for ALPR connection status
        const unlistenStatus = await listen('alpr-connection-status', (event: any) => {
            alprConnectionStatus.value = event.payload
            isAlprConnected.value = event.payload
            console.log('ALPR Connection Status:', event.payload)
        })
        alprListeners.push(unlistenStatus)

        // Listen for plate detection events
        const unlistenPlates = await listen('plate-detected', (event: any) => {
            const plateData = event.payload
            console.log('Plate detected:', plateData)
            detectedPlates.value.unshift(plateData)
            if (detectedPlates.value.length > 10) {
                detectedPlates.value = detectedPlates.value.slice(0, 10)
            }
            Notify.create({
                type: 'positive',
                message: `Plat terdeteksi: ${plateData.plate_number}`,
                position: 'top-right',
                timeout: 3000,
                icon: 'videocam',
            })
        })
        alprListeners.push(unlistenPlates)

        // Listen for camera list updates
        const unlistenCameras = await listen('camera-list-updated', (event: any) => {
            cameraList.value = event.payload
            console.log('Camera list updated:', event.payload)
        })
        alprListeners.push(unlistenCameras)
    }
    catch (error) {
        console.error('Failed to initialize ALPR listeners:', error)
    }
}

// Cleanup ALPR listeners
const cleanupALPRListeners = () => {
    alprListeners.forEach(unlisten => unlisten())
    alprListeners = []
}

export { api, alpr, initializeALPRListeners, cleanupALPRListeners }
