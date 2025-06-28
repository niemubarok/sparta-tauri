import { defineStore } from 'pinia'
import { ref } from "vue";
import ls from "localstorage-slim";
import { invoke } from '@tauri-apps/api/core'
import {useSettingsService} from "./settings-service";
import {useCameraStore} from "./camera-store";

export const useGateStore = defineStore('gate', {
  state: () => ({
    settingService: useSettingsService(),
    cameraStore: useCameraStore(),
    serialConnected: ref(false),
    serialInputs: ref({}),
    loop1: ref(false),
    loop2: ref(false),
    loop3: ref(false),
    audioPlayer: ref(null),
    detectedPlates: ref([]),
  }),

  actions: {
    async playAudio(filename) {
      try {
        const { resolve } = await import('@tauri-apps/api/path');
        const { resourceDir } = await import('@tauri-apps/api/path');
        const audioPath = await resolve(await resourceDir(), `audio/${filename}.wav`);
        console.log("🚀 ~ playAudio ~ audioPath:", audioPath);
        await invoke('play_audio', { filePath: audioPath });
      } catch (error) {
        console.error("Error playing audio:", error);
      }
    },
    async initializeSerialPort(portConfig) {
      const { portName, type } = portConfig;

      try {
        await invoke('close_serial');
        // Create serial port using Tauri command
        await invoke('create_serial_port', { portName });
        this.serialConnected = true;

        // Start listening for data
        this.startSerialListener(portName, type);

      } catch (err) {
        console.error(`Error initializing ${type} port:`, err);
        this.serialConnected = false;
      }
    },

    async startSerialListener(portName, type) {
      const pollSerial = async () => {
        if (!this.serialConnected) return;

        try {
          const data = await invoke('listen_to_serial', { portName });
          if (data) {
            this.serialInputs[type] = data;

            // Handle different port types
            // switch (type) {
            //   case 'entry':
            //     this.handleEntryGate(data);
            //     break;
            //   case 'exit':
            //     this.handleExitGate(data);
            //     break;
            // }
          }
        } catch (err) {
          console.error('Serial read error:', err);
        }

        // Continue polling
        setTimeout(pollSerial, 100);
      };

      pollSerial();
    },

    async closeSerialPort() {
      try {
        await invoke('close_serial');
        this.serialConnected = false;
      } catch (err) {
        console.error('Error closing serial port:', err);
      }
    },

    async writeToPort(type, data) {
      console.log("🚀 ~ writeToPort ~ data:", data)
      try {
        if (this.serialConnected) {
          await invoke('write_serial', { data });
        }
      } catch (err) {
        console.error('Error writing to serial port:', err);
      }
    },
    onPushLoop1() {
      this.loop1 = !this.loop1;
      if (this.loop1) {
        this.playAudio('welcome').catch((error) => {
          console.error("Error playing audio:", error);
        });
      }
      // else {
      //   this.playAudio('loop1-off');
      // }
      console.log("loop1", this.loop1);
    },
    onPushLoop2() {
      this.loop2 = !this.loop2;
      if (this.loop2) {
        this.playAudio('masuk');
      }
    },
    onPushLoop3() {
      this.loop3 = !this.loop3;
      this.loop1 = false;
      this.loop2 = false;
      this.playAudio('keluar');
    },

    async handleEntryGate(data) {
      // Handle entry gate specific logic
      console.log("Entry gate data:", data);
      // console.log("🚀 ~ handleEntryGate ~ this.settingService.cctvConfig.PLATE:", await this.cameraStore.captureImageFromCCTV('PLATE'))
    
      this.onPushLoop1()
      // Trigger plate capture or other actions
    },

    handleExitGate(data) {
      // Handle exit gate specific logic
      console.log("Exit gate data:", data);
      // Trigger payment process or other actions
    }
  }
})
