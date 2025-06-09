import { acceptHMRUpdate, defineStore } from 'pinia'
import { invoke } from '@tauri-apps/api/core'
import { listen } from '@tauri-apps/api/event'
import { watch } from 'vue'
import { useCameraStore } from './camera-store'
import { useSettingsService } from './settings-service'

export const useAlprStore = defineStore('alprStore', {
    state: () => ({
        cameraStore: useCameraStore(),
        settingsService: useSettingsService(),
        cctvImage: null,
        cctvError: null,
        lastCaptureTime: null,
        alprResults: null,
        isProcessing: false,
        wsConnection: null,
        wsUrl: 'ws://localhost:8765', // Default value, akan diupdate dari settings
        isWsConnected: false,
        useExternalAlpr: false, // flag untuk menentukan menggunakan ALPR internal atau eksternal
        wsReconnectAttempts: 0,
        maxReconnectAttempts: 5,
        reconnectTimeout: null,
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

        async connectWebSocket() {
            if (this.wsConnection) {
                console.log('WebSocket connection already exists');
                return
            }

            try {
                // Update WebSocket URL from settings
                await this.settingsService.initializeSettings();
                const globalSettings = this.settingsService.globalSettings;
                if (globalSettings && globalSettings.WS_URL) {
                    this.wsUrl = globalSettings.WS_URL;
                }

                console.log('Attempting to connect to WebSocket server at:', this.wsUrl);
                const ws = new WebSocket(this.wsUrl)

                ws.onopen = () => {
                    this.isWsConnected = true
                    this.wsReconnectAttempts = 0
                    console.log('Successfully connected to ALPR WebSocket server')
                    
                    // Send immediate health check
                    this.sendHealthCheck()
                }

                ws.onclose = (event) => {
                    this.isWsConnected = false
                    this.wsConnection = null
                    console.log('Disconnected from ALPR WebSocket server', {
                        code: event.code,
                        reason: event.reason,
                        wasClean: event.wasClean
                    })
                    this.tryReconnect()
                }

                ws.onerror = (error) => {
                    console.error('WebSocket error:', error)
                    this.cctvError = 'WebSocket connection error'
                }

                ws.onmessage = (event) => {
                    try {
                        const response = JSON.parse(event.data)
                        if (response.message_type === 'alpr_result') {
                            this.handleAlprResponse(response.payload)
                        } else if (response.message_type === 'error') {
                            this.cctvError = response.payload.error
                            this.isProcessing = false
                        }
                    } catch (error) {
                        console.error('Error processing WebSocket message:', error)
                        this.cctvError = 'Error processing server response'
                        this.isProcessing = false
                    }
                }

                this.wsConnection = ws
            } catch (error) {
                console.error('Error connecting to WebSocket:', error)
                this.cctvError = 'Failed to connect to ALPR server'
                this.tryReconnect()
            }
        },

        tryReconnect() {
            if (this.wsReconnectAttempts >= this.maxReconnectAttempts) {
                console.error('Max reconnection attempts reached')
                return
            }

            this.wsReconnectAttempts++
            const delay = Math.min(1000 * Math.pow(2, this.wsReconnectAttempts), 30000)

            this.reconnectTimeout = setTimeout(() => {
                console.log(`Attempting to reconnect... (${this.wsReconnectAttempts})`)
                this.connectWebSocket()
            }, delay)
        },

        async sendImageToAlprExternal(imageBase64, cameraId = '') {
            if (!this.isWsConnected) {
                throw new Error('Not connected to ALPR server')
            }

            try {
                this.isProcessing = true
                this.alprResults = null

                const message = {
                    message_type: 'process_image',
                    payload: {
                        image: imageBase64,
                        camera_id: cameraId
                    }
                }

                this.wsConnection.send(JSON.stringify(message))
                
                // Response will be handled by onmessage event
                return new Promise((resolve, reject) => {
                    const timeout = setTimeout(() => {
                        reject(new Error('ALPR processing timeout'))
                    }, 30000) // 30 seconds timeout

                    const messageHandler = (event) => {
                        try {
                            const response = JSON.parse(event.data)
                            if (response.message_type === 'alpr_result') {
                                clearTimeout(timeout)
                                this.wsConnection.removeEventListener('message', messageHandler)
                                resolve(response.payload)
                            } else if (response.message_type === 'error') {
                                clearTimeout(timeout)
                                this.wsConnection.removeEventListener('message', messageHandler)
                                reject(new Error(response.payload.error))
                            }
                        } catch (error) {
                            // Keep listening for the correct response
                        }
                    }

                    this.wsConnection.addEventListener('message', messageHandler)
                })
            } catch (error) {
                this.isProcessing = false
                this.cctvError = error instanceof Error ? error.message : 'Failed to process image'
                throw error
            }
        },

        handleAlprResponse(result) {
            this.isProcessing = false
            if (result && result.detected_plates && result.detected_plates.length > 0) {
                this.alprResults = {
                    processedImage: result.plate_image,
                    detectedPlate: result.detected_plates,
                    processingTime: result.processing_time,
                }
            } else {
                this.cctvError = 'No plate detected'
            }
        },

        async processImage(imageBase64, cameraId = '') {
            try {
                this.isProcessing = true;
                this.alprResults = null;
                console.log(`Processing image using ${this.settingsService.gateSettings.USE_EXTERNAL_ALPR ? 'external' : 'internal'} ALPR service`);

                let result;
                if (this.settingsService.gateSettings.USE_EXTERNAL_ALPR) {
                    if (!this.wsConnection || this.wsConnection.readyState !== WebSocket.OPEN) {
                        throw new Error('WebSocket not connected');
                    }

                    // Check and clean the base64 data
                    let cleanedBase64 = imageBase64;
                    if (imageBase64.includes(',')) {
                        cleanedBase64 = imageBase64.split(',')[1];
                    }

                    const message = {
                        message_type: 'process_image',
                        payload: {
                            image: cleanedBase64,
                            camera_id: cameraId
                        }
                    };
                    
                    result = await new Promise((resolve, reject) => {
                        const timeout = setTimeout(() => {
                            reject(new Error('ALPR processing timeout'));
                        }, 30000);

                        const messageHandler = (event) => {
                            try {
                                const response = JSON.parse(event.data);
                                console.log('Received ALPR response:', response);
                                
                                if (response.message_type === 'alpr_result') {
                                    clearTimeout(timeout);
                                    this.wsConnection.removeEventListener('message', messageHandler);
                                    resolve(response.payload);
                                } else if (response.message_type === 'error') {
                                    clearTimeout(timeout);
                                    this.wsConnection.removeEventListener('message', messageHandler);
                                    reject(new Error(response.payload.message || 'ALPR processing failed'));
                                }
                            } catch (error) {
                                console.error('Error processing WebSocket message:', error);
                            }
                        };

                        this.wsConnection.addEventListener('message', messageHandler);
                        this.wsConnection.send(JSON.stringify(message));
                    });
                } else {
                    result = await invoke('process_alpr_image', {
                        base64Image: imageBase64,
                        cameraId: cameraId,
                    });
                }

                console.log('Processing ALPR result:', result);

                // Handle response sama untuk eksternal dan internal
                if (result && result.success && Array.isArray(result.detected_plates)) {
                    if (result.detected_plates.length > 0) {
                        // Ambil plate pertama untuk plate_image dan processing_time
                        const firstPlate = result.detected_plates[0];
                        this.alprResults = {
                            processedImage: firstPlate.plate_image || result.plate_image,
                            detectedPlate: result.detected_plates,
                            processingTime: firstPlate.processing_time || result.processing_time
                        };
                        console.log('ALPR Results:', this.alprResults);
                        return this.alprResults;
                    }
                }
                
                // Jika tidak ada plate atau error
                throw new Error(result?.message || 'No plate detected');
            } catch (error) {
                console.error('ALPR processing error:', error);
                this.isProcessing = false;
                this.cctvError = error instanceof Error ? error.message : 'Failed to process image';
                throw error;
            } finally {
                this.isProcessing = false;
            }
        },

        disconnect() {
            if (this.wsConnection) {
                this.wsConnection.close()
                this.wsConnection = null
                this.isWsConnected = false
            }
            if (this.reconnectTimeout) {
                clearTimeout(this.reconnectTimeout)
                this.reconnectTimeout = null
            }
            this.wsReconnectAttempts = 0
        },

        updateAlprMode(useExternal) {
            this.useExternalAlpr = useExternal
            if (useExternal && !this.isWsConnected) {
                this.connectWebSocket()
            } else if (!useExternal) {
                this.disconnect()
            }
        },

        async initializeFromSettings() {
            try {
                await this.settingsService.initializeSettings();
                const globalSettings = this.settingsService.globalSettings;
                if (globalSettings && globalSettings.WS_URL) {
                    this.wsUrl = globalSettings.WS_URL;
                    console.log('WebSocket URL updated from settings:', this.wsUrl);
                }
                if (globalSettings && typeof globalSettings.USE_EXTERNAL_ALPR === 'boolean') {
                    this.useExternalAlpr = globalSettings.USE_EXTERNAL_ALPR;
                    console.log('ALPR mode updated from settings:', this.useExternalAlpr ? 'external' : 'internal');
                }

                // Setup watchers for settings changes
                this.setupSettingsWatchers();
            } catch (error) {
                console.error('Error initializing ALPR store from settings:', error);
            }
        },

        setupSettingsWatchers() {
            // Watch for changes in global settings
            watch(
                () => this.settingsService.globalSettings,
                (newSettings, oldSettings) => {
                    if (newSettings) {
                        // Update WebSocket URL if changed
                        if (newSettings.WS_URL !== this.wsUrl) {
                            console.log('WebSocket URL changed, updating:', newSettings.WS_URL);
                            this.wsUrl = newSettings.WS_URL;
                            
                            // Reconnect if using external ALPR and connected
                            if (this.useExternalAlpr && this.isWsConnected) {
                                this.disconnect();
                                setTimeout(() => this.connectWebSocket(), 1000);
                            }
                        }

                        // Update ALPR mode if changed
                        if (newSettings.USE_EXTERNAL_ALPR !== this.useExternalAlpr) {
                            console.log('ALPR mode changed:', newSettings.USE_EXTERNAL_ALPR ? 'external' : 'internal');
                            this.updateAlprMode(newSettings.USE_EXTERNAL_ALPR);
                        }
                    }
                },
                { deep: true, immediate: false }
            );
        },

        resetState() {
            this.cctvImage = null
            this.cctvError = null
            this.lastCaptureTime = null
            this.alprResults = null
            this.isProcessing = false
            this.disconnect()
        },

        async sendHealthCheck() {
            if (!this.wsConnection || this.wsConnection.readyState !== WebSocket.OPEN) {
                console.log('Cannot send health check - WebSocket not connected');
                return;
            }

            const message = {
                message_type: 'health_check',
                payload: {}
            };

            try {
                console.log('Sending health check to server');
                this.wsConnection.send(JSON.stringify(message));
            } catch (error) {
                console.error('Error sending health check:', error);
            }
        },
    },
})

if (import.meta.hot) {
    import.meta.hot.accept(acceptHMRUpdate(useAlprStore, import.meta.hot))
}
