import { defineStore } from 'pinia'
import { invoke } from '@tauri-apps/api/core'
import { useSettingsService } from './settings-service'

export const useCameraStore = defineStore('camera', {
    state: () => ({
        settingService: useSettingsService(),
        imgSrc: '', // For general image capture, e.g., interval
        imgSrc2: '', // Potentially for a second camera or alternative view
        liveStreamFrame: '', // Specifically for live stream frames if needed globally
        activeStreamUnlisteners: new Map(), // Stores unlisten functions for active streams
    }),

    actions: {
        setActiveStreamUnlistener(cameraLocation, unlistenFn) {
            // If there's an existing unlistener for this location, call it first
            if (this.activeStreamUnlisteners.has(cameraLocation)) {
                const oldUnlisten = this.activeStreamUnlisteners.get(cameraLocation);
                oldUnlisten();
                console.log(`Old unlistener for ${cameraLocation} called and removed.`);
            }
            this.activeStreamUnlisteners.set(cameraLocation, unlistenFn);
            console.log(`Active unlistener set for ${cameraLocation}`);
        },

        removeActiveStreamUnlistener(cameraLocation) {
            if (this.activeStreamUnlisteners.has(cameraLocation)) {
                const unlisten = this.activeStreamUnlisteners.get(cameraLocation);
                unlisten(); // Call the unlisten function to stop listening to events
                this.activeStreamUnlisteners.delete(cameraLocation);
                console.log(`Unlistener for ${cameraLocation} called and removed.`);
            } else {
                console.log(`No active unlistener found for ${cameraLocation} to remove.`);
            }
        },
        async captureImageFromCCTV(type) {
            // await this.settingService.loadGateSettings()
            // try {
                const response = await invoke('capture_cctv_image', { args: this.settingService.cctvConfig[type] });
                if (response.is_success && response.base64) {
                    return response.base64;
                } else {
                    throw new Error(response.message || 'Failed to capture image');
                }
            // } catch (error) {
            //     console.error("Error capturing image:", error);
            //     throw error;
            // }
        },
    },
})
