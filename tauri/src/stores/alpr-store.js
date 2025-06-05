import { acceptHMRUpdate, defineStore } from 'pinia'
import { invoke } from '@tauri-apps/api/core'
import { listen } from '@tauri-apps/api/event'
import { useCameraStore } from './camera-store'

export const useAlprStore = defineStore('alprStore', {
    state: () => ({
        cameraStore: useCameraStore(),
        cctvImage: null,
        cctvError: null,
        lastCaptureTime: null,
        alprResults: null,
        isProcessing: false,
    }),

    getters: {
        hasDetections: state => {
            return state.alprResults?.detectedPlate?.length > 0
        },
    },

    actions: {
        async getImageFromCCTV(config) {
            try {
                const response = await invoke('capture_cctv_image', {
                    config: {
                        username: config.username,
                        password: config.password,
                        ip_address: config.ipAddress,
                    },
                })

                if (response.isSuccess && response.base64) {
                    this.cctvImage = response.base64
                    this.lastCaptureTime = response.timestamp
                    this.cctvError = null

                    return response.base64
                }
                else {
                    this.cctvError = response.message || 'Failed to capture image'
                    this.cctvImage = null
                    throw new Error(this.cctvError)
                }
            }
            catch (error) {
                this.cctvError = error instanceof Error ? error.message : 'Unknown error occurred'
                this.cctvImage = null
                throw error
            }
        },

        async sendImageToAlpr(imageBase64, cameraId = '') {
            try {
                this.isProcessing = true
                this.alprResults = null

                // Use Tauri invoke to process ALPR image
                const result = await invoke('process_alpr_image', {
                    base64_image: imageBase64,
                    camera_id: cameraId,
                })

                // The result should match the structure from Rust backend
                this.isProcessing = false
                if (result && result.detected_plates && result.detected_plates.length > 0) {
                    this.alprResults = {
                        processedImage: result.plate_image,
                        detectedPlate: result.detected_plates,
                        processingTime: result.processing_time,
                    }
                    return this.alprResults
                } else {
                    this.cctvError = result && result.message ? result.message : 'No plate detected'
                    throw new Error(this.cctvError)
                }
            } catch (error) {
                this.isProcessing = false
                this.cctvError = error instanceof Error ? error.message : 'Failed to process image'
                throw error
            }
        },

        async captureAndProcess(config) {
            const imageData = await this.cameraStore.captureImageFromCCTV('PLATE');
            if (!imageData) {
                throw new Error('Failed to capture image from camera');
            }

            // Use image data directly if it's already base64, otherwise convert
            const imageBase64 = imageData.startsWith('data:image')
                ? imageData.split(',')[1]
                : await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.readAsDataURL(imageData);
                    reader.onload = () => resolve(reader.result.split(',')[1]);
                    reader.onerror = error => reject(error);
                });

            if (!imageBase64) {
                throw new Error('Failed to get image data');
            }


            const result = await invoke('process_alpr_image', {
                base64Image: imageBase64,
                cameraId: 'PLATE',
            });
            console.log("🚀 ~ handleEntryGate ~ result:", result);
        },

        resetState() {
            this.cctvImage = null
            this.cctvError = null
            this.lastCaptureTime = null
            this.alprResults = null
            this.isProcessing = false
        },
    },
})

if (import.meta.hot) {
    import.meta.hot.accept(acceptHMRUpdate(useAlprStore, import.meta.hot))
}
