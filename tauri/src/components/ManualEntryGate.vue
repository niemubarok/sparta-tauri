<!-- eslint-disable no-console -->
<script setup>
import { computed, onMounted, onUnmounted, onBeforeUnmount, ref, watch } from 'vue';
import { useQuasar } from 'quasar';
import { api, detectedPlates } from 'src/boot/axios';
import { invoke } from '@tauri-apps/api/core';
import ls from 'localstorage-slim';
import { useComponentStore } from 'src/stores/component-store';
import { useGateStore } from 'src/stores/gate-store';
import NotMemberCard from './NotMemberCard.vue';

// import { useManlessStore } from 'src/stores/manless-store'

// import { useCameraStore } from 'src/stores/camera-store'
import {useAlprStore} from 'src/stores/alpr-store';
import { useMembershipStore } from 'src/stores/membership-store';
import { useThemeStore } from '../stores/theme';
import { addTransaction, addTransactionAttachment } from 'src/boot/pouchdb';
import Camera from './Camera.vue';
import Clock from './Clock.vue';
import SettingsDialog from './SettingsDialog.vue';
import ConnectionIndicator from './ConnectionIndicator.vue';
import { useRouter } from 'vue-router';

// import PlatNomor from './PlatNomor.vue'

// import PlateNumber from './ALPRDetectedPlateNumber.vue'
import ALPRDetectedPlateNumber from './ALPRDetectedPlateNumber.vue';

const memberShipStore = useMembershipStore();
const themeStore = useThemeStore();
const componentStore = useComponentStore();
const alprStore = useAlprStore()


// const manlessStore = useManlessStore()

// const cameraStore = useCameraStore()

// Helper function to parse RTSP URL for credentials and IP
const parseRtspUrl = (url, settings, typePrefix) => { // typePrefix is 'PLATE' or 'DRIVER'
  const config = { username: 'admin', password: 'password', ip_address: '' }; // Defaults

  if (!url) return config;

  const settingsUsername = settings?.[`${typePrefix}_CAM_USERNAME`];
  const settingsPassword = settings?.[`${typePrefix}_CAM_PASSWORD`];
  const settingsIpAddress = settings?.[`${typePrefix}_CAM_IP_ADDRESS`];

  if (settingsUsername) config.username = settingsUsername;
  if (settingsPassword) config.password = settingsPassword;
  // If dedicated IP field exists, prioritize it
  if (settingsIpAddress) {
    config.ip_address = settingsIpAddress;
    // If all three (user, pass, ip) are from specific settings, no need to parse URL for them
    if (settingsUsername && settingsPassword) return config;
  }

  // Fallback to parsing from URL if not all parts are from specific settings
  // Regex: rtsp://(?:([^:]+)(?::([^@]+))?@)?([^/:]+)(?::\d+)?(?:/.*)?
  // Group 1: username (optional)
  // Group 2: password (optional, only if username is present)
  // Group 3: host (ip_address or hostname)
  const match = url.match(/rtsp:\/\/(?:([^:]+)(?::([^@]+))?@)?([^/:@]+)/);

  if (match) {
    // Only overwrite from URL if not already set by specific settings fields
    if (match[3] && !config.ip_address) { // host
      config.ip_address = match[3];
    }
    if (match[1] && !settingsUsername) { // username
      config.username = match[1];
    }
    if (match[2] && !settingsPassword) { // password
      config.password = match[2];
    }
  }
  return config;
};

const router = useRouter();
const gateStore = useGateStore();
const isDark = computed(() => gateSettings.value?.darkMode || themeStore.isDark);

import { useSettingsService } from 'src/stores/settings-service'; // Tambahkan import

const settingsService = useSettingsService();
const gateSettings = computed(() => settingsService.gateSettings);

// ALPR Mode settings
const useExternalAlpr = computed(() => gateSettings.value?.USE_EXTERNAL_ALPR || false);

const plateCameraType = computed(() => {
  if (gateSettings.value?.PLATE_CAM_DEVICE_ID) return 'usb';
  if (gateSettings.value?.PLATE_CAM_IP) return 'cctv';
  return null; // Return null when no camera is configured
});

const driverCameraType = computed(() => {
  if (gateSettings.value?.DRIVER_CAM_DEVICE_ID) return 'usb';
  if (gateSettings.value?.DRIVER_CAM_IP) return 'cctv';
  return null; // Return null when no camera is configured
});

// Camera URLs dan Device IDs diambil dari gateSettings
const plateCameraUrl = computed(() => gateSettings.value?.PLATE_CAM_IP || '');
const driverCameraUrl = computed(() => gateSettings.value?.DRIVER_CAM_IP || '');
const plateCameraDeviceId = computed(() => gateSettings.value?.PLATE_CAM_DEVICE_ID || null);
const driverCameraDeviceId = computed(() => gateSettings.value?.DRIVER_CAM_DEVICE_ID || null);

const plateCameraCredentials = computed(() => {
  return parseRtspUrl(gateSettings.value?.PLATE_CAM_IP, gateSettings.value, 'PLATE');
});

const driverCameraCredentials = computed(() => {
  return parseRtspUrl(gateSettings.value?.DRIVER_CAM_IP, gateSettings.value, 'DRIVER');
});

const base64String = ref('');

watch(
  () => base64String,
  (newValue) => {
    if (newValue) {
      plateCameraRef.value?.setManualBase64(newValue);
    }
  }
);

const toggleDarkMode = () => {
  themeStore.toggleDarkMode();
};

// const isServerConnected = ref(false);
// const isALPRConnected = computed(() => alprConnectionStatus.value)

const $q = useQuasar();

// Camera refs
const plateCameraRef = ref(null);
const driverCameraRef = ref(null);
const isProcessing = ref(false);
const activityLogs = ref([]);
const errorDialog = ref(false);
const isCapturing = ref(false);
const error = ref(null);
const plateResult = ref(null);
const plateImage = ref(null);

// Manual capture state variables
const uploadedImage = ref(null);
const manualCaptureMode = ref(false);
const uploading = ref(false);
const showUploadDialog = ref(false);
const fileModel = ref(null);

// Watch for new detected plates from WebSocket
// (WebSocket logic removed, now handled by Tauri events)
watch(
  detectedPlates,
  (newPlates) => {
    if (newPlates && newPlates.length > 0) {
      const latestPlate = newPlates[0];
      if (latestPlate && latestPlate.plate_number) {
        plateResult.value = { ...latestPlate }; // Ensure reactivity by creating a new object
        capturedPlate.value = latestPlate.image_base64
          ? `data:image/jpeg;base64,${latestPlate.image_base64}`
          : null;
        console.log(
          'Auto-detected plate from WebSocket:',
          latestPlate.plate_number
        );
        // Ensure detectedPlates for UI is also updated if it's meant to show the latest single plate
        // This might be redundant if detectedPlates from boot/axios is the sole source for the list
      }
    } else {
      // Optional: Clear if no plates are detected via WebSocket
      // plateResult.value = null;
      // capturedPlate.value = null;
    }
  },
  { deep: true }
);

const displayedPlateInfo = ref([]); // New ref for UI display to avoid recursion

// Watch for changes in plateResult to update capturedPlate and displayedPlateInfo for UI consistency
watch(
  plateResult,
  (newResult) => {
    if (newResult && newResult.plate_number) {
      capturedPlate.value = newResult.plate_image
        ? `data:image/jpeg;base64,${newResult.plate_image}`
        : newResult.image_base64
        ? `data:image/jpeg;base64,${newResult.image_base64}`
        : null;
      // Update displayedPlateInfo ref used in the template
      displayedPlateInfo.value = [{ ...newResult }]; // Create a new object for the array item
    } else {
      capturedPlate.value = null;
      displayedPlateInfo.value = []; // Clear the list in UI if no plate result
    }
  },
  { deep: true }
);
const gateStatus = ref('CLOSED');
const gateStatusTranslated = computed(() => {
  return gateStatus.value === 'OPEN' ? 'BUKA' : 'TUTUP';
});
const isAutoCaptureActive = ref(true); // Auto capture flag
// const isDark = ref(false)

// Watch for dark mode changes and save to localStorage
watch(isDark, (newValue) => {
  ls.set('darkMode', newValue);
  document.body.classList.toggle('body--dark', newValue);
});

const onPushLoop1 = async () => {
 resetEntryGateState()

  if (gateStore.loop1 === false) {
    gateStore.onPushLoop1();

    // gateStore.loop1 = true;

    // if (plateCameraType.value === 'cctv') {
    //   await plateCameraRef.value?.fetchCameraImage();

    //   // Tunggu hingga data di gateStore.detectedPlates diperbarui
    //   await new Promise((resolve) => {
    //     const checkData = setInterval(() => {
    //       if (gateStore.detectedPlates.length > 0) {
    //         clearInterval(checkData);
    //         resolve();
    //       }
    //     }, 100); // Periksa setiap 100ms
    //   });

    //   plateResult.value = gateStore.detectedPlates[0];
    //   capturedPlate.value = `data:image/jpeg;base64,${plateResult.value?.plate_image}`;
    // }

    await onPlateCaptured();
  }

  gateStore.loop1 = false;
};

const onPushLoop2 = async () => {
  gateStore.onPushLoop2();
  manualOpen();
  // await onPlateCaptured()
};

const onPushLoop3 = () => {
  gateStore.onPushLoop3();
};

// Methods
const detectPlate = async () => {
  try {
    isCapturing.value = true;
    error.value = null;
    plateImage.value = null; // Reset plate image

    // Get image from camera
    const imageData = await plateCameraRef.value.getImage();
    console.log("🚀 ~ detectPlate ~ imageData:", imageData)
    if (!imageData) {
      throw new Error('Failed to capture image from camera');
    }    // Handle different types of image data
    let imageBase64;
    if (typeof imageData === 'string') {
      // If it's a string, check if it's a base64 data URL
      imageBase64 = imageData.startsWith('data:image') 
        ? imageData.split(',')[1]
        : imageData; // Assume it's already base64 without prefix
    } else {
      // If it's a File object, convert it to base64
      imageBase64 = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(imageData);
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = error => reject(error);
      });
    }

    if (!imageBase64) {
      throw new Error('Failed to get image data');
    }

    // Get camera ID for ALPR processing
    const cameraId = plateCameraType.value === 'usb'
      ? ls.get('plateCameraDevice') || 'plate_camera'
      : ls.get('plateCameraUrl') || 'plate_camera';

    // Use alprStore.processImage for both internal and external ALPR
    const alprResponse = await alprStore.processImage(imageBase64, cameraId);
      if (alprResponse && alprResponse.detectedPlate && alprResponse.detectedPlate.length > 0) {
      const bestMatch = alprResponse.detectedPlate[0];
      plateResult.value = bestMatch; // Store the whole object
      addActivityLog(`Plat terdeteksi: ${bestMatch.plate_number}`);
    } else if (alprResponse && alprResponse.success && alprResponse.detected_plates && alprResponse.detected_plates.length > 0) {
      // Handle direct response format (internal ALPR)
      const bestMatch = alprResponse.detected_plates[0];
      plateResult.value = bestMatch; // Store the whole object
      addActivityLog(`Plat terdeteksi: ${bestMatch.plate_number}`);
    } else {
      plateResult.value = null; // Clear previous result if no plate detected
      capturedPlate.value = null; // Clear previous image
      $q.notify({
        type: 'warning',
        message: 'No plate detected',
        position: 'top',
      });
    }
  } catch (err) {
    console.error('Error detecting plate:', err);
    error.value = 'Failed to process license plate';
    addActivityLog(`Error: ${error.value}`, true);

    $q.notify({
      type: 'negative',
      message: error.value,
      position: 'top',
    });
  } finally {
    isCapturing.value = false;
  }
};

// Handle plate capture event from Camera component
const onPlateCaptured = async () => {
  //   const plateNumber = bestConfidenceDetectedPlate.value;
  // if (!plateNumber) {
  //   addActivityLog('No plate number detected', true);
  //   return;
  // }

  // Capture driver image first
  try {
    const driverCameraAvailable =
      ls.get('driverCameraDevice') || ls.get('driverCameraUrl');
    if (driverCameraAvailable) {
      const driverImage = await driverCameraRef.value.getImage();

      // Convert to base64
      const reader = new FileReader();
      reader.readAsDataURL(driverImage);
      reader.onloadend = () => {
        capturedDriver.value = reader.result;
      };
    }
  } catch (err) {
    console.error('Failed to capture driver image:', err);
  }

  // Continue with plate detection
  // Try detection up to 5 times
  for (let i = 0; i < 5; i++) {
    await detectPlate();
    if (plateResult.value && plateResult.value?.confidence >= 0.8) {
       addActivityLog(
          `Plat ${plateResult.value?.plate_number} terdeteksi dengan waktu ${plateResult.value?.processing_time?.toFixed(2)}s`
        );
      addDetectedPlate(plateResult.value);
      const isMember = await checkMembership(plateResult.value?.plate_number);
      console.log("🚀 ~ onPlateCaptured ~ isMember:", isMember)

      if (isMember) {
        addActivityLog(
          `Plat ${plateResult.value?.plate_number} terdeteksi sebagai member`
        );

        // Open gate for valid member
        if (gateStatus.value === 'CLOSED') {
          gateStatus.value = 'OPEN';
          addActivityLog(
            `Pintu dibuka otomatis untuk plat ${plateResult.value?.plate_number}`
          );

          // Save transaction for valid member
          const transactionData = {
            plate_number: plateResult.value.plate_number,
            confidence: plateResult.value.confidence,
            processing_time: plateResult.value.processing_time,
            is_member: true,
            gate_status: 'OPEN',
          };
          await saveTransactionToLocal(transactionData);
        }

        // setTimeout(() => {
        //   // Reset state after successful detection
        //   resetEntryGateState();
        //   gateStore.loop1 = false; // Reset loop state
        // }, 3000); // Adjust timeout as needed
        // Exit loop after successful member detection
        break;
      }

      // Log processing time if available
      if (plateResult.value?.processing_time) {
        addActivityLog(
          `ALPR processing time ${plateResult.value?.processing_time?.toFixed(
            2
          )}s`
        );
      }
    }

    // Show dialog if no valid member found after all attempts
    if (i === 4 && gateStatus.value === 'CLOSED') {
      addActivityLog(`Tidak ada member valid terdeteksi setelah ${i + 1} percobaan`, true);

      // if(!manualCaptureMode.value){
      $q.dialog({
        component: NotMemberCard,
        // componentProps: { /* pass any props to NotMemberCard here */ }
      })
        .onOk(() => {
          console.log('NotMemberCard dialog closed with OK');
          resetEntryGateState()
          // Reset state and close dialog
          // / Reset gate status
        })
        .onCancel(() => {
          console.log('NotMemberCard dialog closed with Cancel');
        })
        .onDismiss(() => {
          console.log(
            'NotMemberCard dialog dismissed (closed by timeout or other means)'
          );
        });
      // }
    }
  }

  // await new Promise(resolve => setTimeout(resolve, 1000));
};

const manualOpen = async () => {
  try {
    // isProcessing.value = true;
    // error.value = null;

    // await alpr.post('/transactions/manual-open-gate', {
    //   gateId: '01'
    // })

    // if (gateStore.loop1) {
      gateStore.writeToPort('entry', ' *OPEN1#')
      // gateStore.writeToPort('entry', ' *OUT1OFF#')
      gateStatus.value = 'OPEN';
      gateStore.loop2 = true;
      addActivityLog('Pintu dibuka secara manual oleh operator');
    // }

    // Auto close after 30 seconds
    setTimeout(() => {
      if (gateStatus.value === 'OPEN') {
        gateStatus.value = 'CLOSED';
        gateStore.loop2 = false;
        addActivityLog('Pintu ditutup otomatis setelah timeout');
      }
    }, 3000);
  } catch (err) {
    console.error('Manual open error:', err);
    error.value = 'Failed to open gate manually';
    errorDialog.value = true;
    addActivityLog('Gagal membuka pintu secara manual', true);

    $q.notify({
      type: 'negative',
      message: error.value,
    });
  } finally {
    isProcessing.value = false;
  }
};

const resetEntryGateState = ()=>{
  plateResult.value = null;
          capturedPlate.value = null;
          detectedPlates.value = [];
          gateStore.detectedPlates = [];
          gateStatus.value = 'CLOSED'; 
}

const openSettings = () => {
  const dialog = $q.dialog({
    component: SettingsDialog,
    componentProps: { persistent: true },
  });
  dialog.onOk(() => {
    // Refresh settings after dialog closes
    plateCameraUrl.value = ls.get('plateCameraUrl') || '';
    driverCameraUrl.value = ls.get('driverCameraUrl') || '';
  });
};

const addActivityLog = (message, isError = false) => {
  activityLogs.value.unshift({
    message,
    timestamp: new Date().toLocaleTimeString(),
    isError,
  });

  // Keep only last 100 logs
  if (activityLogs.value.length > 100) {
    activityLogs.value = activityLogs.value.slice(0, 100);
  }
};

// const detectedPlates = ref([])
const capturedPlate = ref(null);
const capturedDriver = ref(null);
// const showNotMemberDialog = ref(false) // No longer needed as we use $q.dialog

// const bestConfidenceDetectedPlate = ref(null)
// This function might need re-evaluation based on whether `detectedPlates` (the ref)
// is for a list of multiple detections or just the single best one.
// The new watcher for `plateResult` now updates `detectedPlates.value = [newResult]`,
// effectively making `detectedPlates` (the ref) always show the single current `plateResult`.
// If a list of multiple detections is needed, this function and its usage should be revised.
const addDetectedPlate = (plate) => {
  const {
    plate_number,
    confidence,
    processing_time,
    plate_image,
    image_base64,
  } = plate;
  if (plate_number) {
    const plateData = {
      plate_number,
      confidence: confidence ? parseFloat(confidence).toFixed(2) : 0,
      processing_time: processing_time
        ? parseFloat(processing_time).toFixed(2)
        : 0,
      plate_image, // ensure image data is part of the object
      image_base64,
    };
    // If detectedPlates (ref) is meant to be a list, then push or unshift here.
    // For now, it's being set by the plateResult watcher to a single item array.
    // Example for a list: detectedPlates.value.unshift(plateData);
    // if (detectedPlates.value.length > 3) detectedPlates.value.pop();
    console.log('addDetectedPlate called with:', plateData);
  }
};

const saveTransactionToLocal = async (transactionData) => {
  try {
    const response = await addTransaction({
      _id: new Date().toISOString(), // Unique ID for PouchDB
      ...transactionData,
      entry_time: new Date().toISOString(),
      status: '1', // 1 for antry 0 for exit
    });

    // 2. Tambahkan attachment gambar jika ada
    if (transactionData.plate_image_base64) {
      await addTransactionAttachment(
        response.id,
        response.rev,
        'plate.jpg',
        transactionData.plate_image_base64
      );
    }
    if (transactionData.driver_image_base64) {
      await addTransactionAttachment(
        response.id,
        response.rev,
        'driver.jpg',
        transactionData.driver_image_base64
      );
    }
    if (transactionData.vehicle_image_base64) {
      await addTransactionAttachment(
        response.id,
        response.rev,
        'vehicle.jpg',
        transactionData.vehicle_image_base64
      );
    }


    addActivityLog(`Transaksi ${response.id} disimpan secara lokal.`);
    console.log('Transaction saved locally:', response);
    return response;
  } catch (err) {
    addActivityLog('Gagal menyimpan transaksi secara lokal.', true);
    console.error('Error saving transaction locally:', err);
    $q.notify({
      type: 'negative',
      message: 'Failed to save transaction to local database.',
    });
    throw err;
  }
};

// const sendDataToBackend = async () => {
//   try {
//     const formData = new FormData();

//     // Get images directly as File objects
//     if (plateCameraRef.value) {
//       const plateImage = await plateCameraRef.value.getImage();
//       formData.append('plate_image', plateImage, 'plate.jpg');
//     }

//     if (driverCameraRef.value) {
//       const driverImage = await driverCameraRef.value.getImage();
//       formData.append('driver_image', driverImage, 'driver.jpg');
//     }

//     // Append other data
//     formData.append('detected_plates', JSON.stringify(detectedPlates.value));
//     formData.append('location', 'ENTRY_GATE_1');
//     formData.append('operator', 'SYSTEM');

//     const response = await api.post('/manless/store', formData, {
//       headers: { 'Content-Type': 'multipart/form-data' },
//     });

//     console.log('Data saved successfully:', response.data);
//   } catch (error) {
//     console.error('Error saving data to backend:', error);
//   }
// };

const checkMembership = async (plateNumber) => {
  try {
    const member = await memberShipStore.checkMembership(plateNumber);
    if (member) {
      addActivityLog(`Plat ${plateNumber} adalah member yang valid`);

      return true;
    } else {
      addActivityLog(`Plat ${plateNumber} bukan member yang valid`, true);

      return false;
    }
  } catch (error) {
    console.error('Error checking membership:', error);
    addActivityLog('Gagal memeriksa keanggotaan', true);

    return false;
  }
};

// await sendDataToBackend();
// Send data to backend after detection

// Example of saving transaction after successful plate detection and member check:
if (plateResult.value && plateResult.value.plate_number) {
  const transactionPayload = {
    plate_number: plateResult.value.plate_number,
    plate_image_base64: capturedPlate.value
      ? capturedPlate.value.split(',')[1]
      : null,
    driver_image_base64: capturedDriver.value
      ? capturedDriver.value.split(',')[1]
      : null,
    // Add other relevant data from plateResult or component state
    confidence: plateResult.value.confidence,
    processing_time_ms: plateResult.value.processing_time_ms,
    timestamp: new Date().toISOString(),
    gate_id: 'ENTRY_GATE_1', // Example gate ID
    vehicle_type: 'mobil', // Example, determine this based on logic
  };
  await saveTransactionToLocal(transactionPayload);
}
// }

const onCameraError = (err) => {
  error.value = `Camera error: ${err.message}`;
  errorDialog.value = true;
  addActivityLog(error.value, true);

  // $q.notify({
  //   type: 'negative',
  //   message: error.value
  // })
};

const dismissError = () => {
  errorDialog.value = false;
  error.value = null;
};

const openSettingsFromError = () => {
  dismissError();
  openSettings();
};

const handleSerialData = async (data) => {
  if (data) {
    if(data === '*IN1ON#') {      await onPushLoop1()
      addActivityLog('Pintu dibuka oleh perintah serial');
    } else if (data === '*IN1OFF#') {
      gateStore.loop1 = false;
      gateStatus.value = 'CLOSED';
      addActivityLog('Pintu ditutup oleh perintah serial');
    } else if (data === '*OUT1ON#') {
      gateStore.loop2 = true;
      gateStatus.value = 'OPEN';
      addActivityLog('Pintu dibuka oleh perintah serial');
    } else if (data === '*OUT1OFF#') {
      gateStore.loop2 = false;
      gateStatus.value = 'CLOSED';
      addActivityLog('Pintu ditutup oleh perintah serial');
    }
    // await onPlateCaptured();
    // gateStatus.value = 'OPEN';
    // await gateStore.writeToPort('entry', '*OUT1ON#');

    // addActivityLog('Gate opened by serial command');
  }
    console.log("🚀 ~ handleSerialData ~ 'Gate opened by serial command':", 'Gate opened by serial command')
};

// Add setup serial listener function
const setupSerialListener = () => {
  const portConfig = {
    portName : gateSettings.value.SERIAL_PORT,
    type: 'entry'
  }
  gateStore.initializeSerialPort(portConfig)
    .catch((error) => {
      console.error('Error listening to serial port:', error);
    });
};

onMounted(async () => {
  // Pastikan settingsService sudah diinisialisasi
  if (!settingsService.activeGateId) {
    await settingsService.initializeSettings();
  }

  // Initialize ALPR store from settings
  await alprStore.initializeFromSettings();
  
  // Connect to external ALPR if enabled
  if (useExternalAlpr.value) {
    try {
      await alprStore.connectWebSocket();
    } catch (error) {
      console.error('Failed to connect to external ALPR:', error);
      $q.notify({
        type: 'warning',
        message: 'Failed to connect to external ALPR service. Using internal ALPR.',
        position: 'top'
      });
    }
  }

  setupSerialListener();

  // await manlessStore.getCameraFeed()
  // await gateStore.initializeSerialPort({
  //   portName: ls.get('serialPort'), // Sesuaikan dengan port entry gate
  //   type: 'entry',
  // });

  // setupSerialListener()
  // Load dark mode preference
  // isDark.value = ls.get('darkMode') || false
  document.body.classList.toggle('body--dark', isDark.value);

  // ALPR connection is now handled by WebSocket in boot/axios.ts
  // updateIntervals();

  // Load camera URLs from settings
  // plateCameraUrl.value = ls.get('plateCameraUrl') || '';
  // driverCameraUrl.value = ls.get('driverCameraUrl') || '';

  // Add initial log
  addActivityLog('Manless entry system initialized');
});


onBeforeUnmount(() => {
  // Stop listening to serial port
  gateStore.closeSerialPort('entry')
    .then(() => {
      console.log('Serial port closed successfully');
    })
    .catch((error) => {
      console.error('Error closing serial port:', error);
    });

  // Stop camera intervals
  if (plateCameraRef.value) {
    plateCameraRef.value.stopInterval();
  }
  
  // Clear all refs and states
  resetEntryGateState();
  
  // Clear activity logs
  activityLogs.value = [];
  
  // Reset processing states
  isProcessing.value = false;
  isCapturing.value = false;
  manualCaptureMode.value = false;
  uploading.value = false;
  showUploadDialog.value = false;
  
  // Clear file refs
  fileModel.value = null;
  uploadedImage.value = null;
  
  // Reset gate status
  gateStatus.value = 'CLOSED';
});

onUnmounted(() => {
  // Disconnect from external ALPR if connected
  if (useExternalAlpr.value) {
    alprStore.disconnect();
  }
  
  // Additional cleanup
  console.log('ManlessEntryGate component unmounted');
});


// Clean up on component destroy
// onUnmounted(async () => {
//   // await gateStore.closeSerialPort('entry');

//   // Stop any ongoing camera operations
//   if (plateCameraRef.value) {
//     plateCameraRef.value.stopInterval();
//   }

//   // Clean up intervals
//   // clearInterval(backendConnectionInterval);
//   // ALPR connection cleanup is now handled by WebSocket in boot/axios.ts
// });

watch(
  () => gateStore.serialInputs?.entry,
  async (newVal) => {
    if (newVal) {
      console.log('Entry gate input:', newVal);

      // Handle entry gate input
      await handleSerialData(newVal);
    }
  }
);

// Watch for ALPR mode changes and handle connection
watch(useExternalAlpr, async (newValue, oldValue) => {
  if (newValue !== oldValue) {
    if (newValue) {
      // Switch to external ALPR
      try {
        await alprStore.connectWebSocket();
        $q.notify({
          type: 'positive',
          message: 'Connected to external ALPR service',
          position: 'top'
        });
      } catch (error) {
        console.error('Failed to connect to external ALPR:', error);
        $q.notify({
          type: 'warning',
          message: 'Failed to connect to external ALPR service. Using internal ALPR.',
          position: 'top'
        });
      }
    } else {
      // Switch to internal ALPR
      alprStore.disconnect();
      $q.notify({
        type: 'info',
        message: 'Switched to internal ALPR service',
        position: 'top'
      });
    }
  }
}, { immediate: false });

// Watch WebSocket connection status for external ALPR
// watch(() => alprStore.isWsConnected, (newStatus) => {
//   if (useExternalAlpr.value && !newStatus) {
//     // Connection lost while in external mode
//     $q.notify({
//       type: 'warning',
//       message: 'External ALPR connection lost. Check WebSocket service.',
//       position: 'top'
//     });
//   }
// }, { immediate: true });

// Manual capture functions
const toggleManualCaptureMode = () => {
  manualCaptureMode.value = !manualCaptureMode.value;
  if (!manualCaptureMode.value) {
    // Reset uploaded image when switching back to camera mode
    uploadedImage.value = null;
    plateResult.value = null;
    fileModel.value = null;
    showUploadDialog.value = false;
  } else {
    // Reset plate result when switching to upload mode
    plateResult.value = null;
  }
};

const handleImageUpload = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  const reader = new FileReader();
  reader.onload = async (e) => {
    uploadedImage.value = e.target.result;
    // Auto process ALPR after upload
    await processUploadedImage();
  };
  reader.readAsDataURL(file);
};

const handleFileSelect = (file) => {
  if (!file) return;
  
  const reader = new FileReader();
  reader.onload = (e) => {
    uploadedImage.value = e.target.result;
  };
  reader.readAsDataURL(file);
};

const processUploadedImage = async () => {
  if (!uploadedImage.value) return;
  
  uploading.value = true;
  try {
    const base64Image = uploadedImage.value.split(',')[1];
    
    // Use alprStore.processImage for both internal and external ALPR
    const result = await alprStore.processImage(base64Image, 'manual_upload');
    console.log("🚀 ~ processUploadedImage ~ result:", result);

    // Handle the result similar to camera detection
    if (result && result.detectedPlate && result.detectedPlate.length > 0) {
      const bestMatch = result.detectedPlate[0];
      plateResult.value = bestMatch;
      addActivityLog(`Manual upload - Plate terdeteksi: ${bestMatch.plate_number}`);
      addActivityLog(
          `Plat ${plateResult.value?.plate_number} terdeteksi dengan waktu ${plateResult.value?.processing_time?.toFixed(2)}s`
        );
      
      // Close upload dialog after successful detection
      showUploadDialog.value = false;
      
      // // Check membership
      // const isMember = await checkMembership(bestMatch.plate_number);
      // console.log("🚀 ~ processUploadedImage ~ isMember:", isMember);

      // if (isMember) {
      //   addActivityLog(`Plate ${bestMatch.plate_number} is a valid member`);
      //   gateStatus.value = 'OPEN';
        
      //   // Auto close gate after 5 seconds
      //   setTimeout(() => {
      //     gateStatus.value = 'CLOSED';
      //     addActivityLog('Pintu ditutup otomatis');
      //   }, 5000);
      // } else {
      //   addActivityLog(`Plate ${bestMatch.plate_number} is not a member`, true);
      //   // Show not member dialog
      //   $q.dialog({
      //     component: NotMemberCard,
      //     componentProps: {
      //       plateNumber: bestMatch.plate_number,
      //       plateImage: uploadedImage.value,
      //       onPayment: () => {
      //         gateStatus.value = 'OPEN';
      //         setTimeout(() => {
      //           gateStatus.value = 'CLOSED';
      //           addActivityLog('Pintu ditutup setelah pembayaran');
      //         }, 5000);
      //       }
      //     }
      //   });
      // }
    } else {
      plateResult.value = null;
      addActivityLog('Tidak ada plate terdeteksi pada gambar', true);
      $q.notify({
        type: 'warning',
        message: 'No license plate detected in uploaded image',
      });
    }
  } catch (error) {
    console.error('Error processing uploaded image:', error);
    plateResult.value = null;
    addActivityLog(`Error processing uploaded image: ${error.message}`, true);
    $q.notify({
      type: 'negative',
      message: `Error processing uploaded image: ${error}`,
    });
  } finally {
    uploading.value = false;
  }
};

const openUploadDialog = () => {
  showUploadDialog.value = true;
};

const closeUploadDialog = () => {
  showUploadDialog.value = false;
  uploadedImage.value = null;
  plateResult.value = null;
  fileModel.value = null;
};

const clearUploadedImage = () => {
  uploadedImage.value = null;
  plateResult.value = null;
  fileModel.value = null;
};

// Navigate to home and cleanup
const goHome = async () => {
  try {
    console.log('Starting navigation to home...');
    
    // Reset all states
    resetEntryGateState();
    
    // Clear all storages
    ls.remove('gateMode');
    ls.remove('manlessMode');
    
    // Reset gate store
    gateStore.$reset(); // If using Pinia store reset
    
    // Force component destruction
    await nextTick();
    
    // Navigate with force
    await router.replace('/');
    
    // Force page reload as last resort
    setTimeout(() => {
      window.location.reload();
    }, 100);
    
  } catch (error) {
    console.error('Error navigating to home:', error);
    // Force reload on error
    window.location.href = '/';
  }
};

// ...existing code...
</script>

<template>
  <div class="manless-entry" :class="{ 'dark-mode': isDark }">
    <!-- Header Section -->
    <div class="row q-mb-md">
      <div class="col-12">
        <q-card
          flat
          class="q-px-sm q-pt-sm"
          :class="isDark ? 'text-white' : 'bg-white text-primary'"
          style="height: 50px"
        >
          <!-- <q-card-section> -->
          <div class="row items-center justify-between">
            <div class="text-h5">Pintu Masuk</div>
            <div class="row items-center q-gutter-md">
              <Clock />
              <q-toggle
                :model-value="isDark"
                color="yellow"
                icon="dark_mode"
                class="text-white"
                @update:model-value="toggleDarkMode"
              />
              <ConnectionIndicator class="indicator-item" />
              <q-btn
                flat
                dense
                color="primary"
                icon="home"
                @click="goHome"
              />
              <!-- <ConnectionIndicator :is-connected="isALPRConnected" label="ALPR" class="indicator-item" icon="videocam"
                iconOff="videocam_off" /> -->
            </div>
          </div>
          <!-- </q-card-section> -->
        </q-card>
      </div>
    </div>

    <!-- Camera Section -->
    <div class="row q-col-gutter-xs">
      <!-- Left side - License Plate Camera -->
      <div class="col-12 col-md-6">
        <q-card flat class="camera-card bg-transparent">
          <!-- <div class="q-ma-sm">
          </div> -->
          <!-- <q-card-section class="plate-camera-container"> -->
          <!-- <div class="row items-center justify-between q-mb-sm"> -->
          <!-- <q-badge outline color="dark" text-color="dark" class="text-body1 "  :class="{'text-white': isDark}">License Plate Camera</q-badge> -->
          <!-- <div class="text-h6">License Plate Camera</div> -->          <div class="absolute-bottom-left z-top q-ma-lg">
            <q-btn
              dense
              push
              :color="manualCaptureMode ? 'primary' : 'white'"
              :text-color="manualCaptureMode ? 'white' : 'primary'"
              :label="manualCaptureMode ? 'Mode Kamera' : 'Mode Upload'"
              class="text-bold q-mr-sm"
              :icon="manualCaptureMode ? 'videocam' : 'upload'"
              @click="toggleManualCaptureMode"
            />
           
            <q-btn
              v-if="manualCaptureMode"
              dense
              push
              label="Upload Gambar"
              color="white"
              text-color="primary"
              class="text-bold"
              icon="image"
              @click="openUploadDialog"
            />
          </div>
          <!-- </div> -->

<Camera
              v-if="!manualCaptureMode"
              ref="plateCameraRef"
              :username="gateSettings.PLATE_CAM_USERNAME"
              :password="gateSettings.PLATE_CAM_PASSWORD"
              :ipAddress="gateSettings.PLATE_CAM_IP"
              :fileName="'plate'"
              cameraLocation="plate"
              :cameraType="plateCameraType"
              :deviceId="plateCameraDeviceId"
              @captured="onPlateCaptured"
              @error="onCameraError"
              class="camera-feed"
              label="Kamera Kendaraan"
            />
              <!-- Manual Upload Image Display -->
            <div v-else class="camera-feed manual-upload-container">
              <div v-if="!uploadedImage" class="upload-placeholder">
                <q-icon name="image" size="xl" color="grey-5" />                <div class="text-h6 text-grey-5 q-mt-md">Upload gambar untuk deteksi plat</div>
                <div class="text-body2 text-grey-6">Klik tombol "Upload Gambar" di bawah</div>
              </div>
              <div v-else class="uploaded-image-container">
                <img :src="uploadedImage" alt="Uploaded image" class="uploaded-image" />
                <q-btn
                  icon="clear"
                  dense flat round
                  @click="clearUploadedImage"
                  class="absolute-top-right q-ma-xs"
                  style="z-index: 1; background-color: rgba(0,0,0,0.6);"
                  color="white"
                >
                  <q-tooltip>Hapus Gambar</q-tooltip>
                </q-btn>                <div v-if="uploading" class="processing-overlay">
                  <q-spinner color="primary" size="3em" />
                  <div class="text-white q-mt-md">Memproses ALPR...</div>
                </div>
              </div>
            </div>
              <q-btn
              v-if="plateCameraType === 'cctv' && !base64String && !manualCaptureMode"
              icon="refresh"
              dense flat round
              @click="plateCameraRef?.fetchCameraImage()"
              class="absolute-top-right q-ma-xs"
              style="z-index: 1; background-color: rgba(0,0,0,0.3); margin-top: 35px;"
              color="white"
            >
              <q-tooltip>Refresh Gambar CCTV</q-tooltip>
            </q-btn>

          <!-- :cropArea="{ x: 200, y: 50, width: 400, height: 200 }" -->          
           <div v-if="plateResult?.plate_number && (capturedPlate || (manualCaptureMode && plateResult))">
            <q-card
              class="plate-detection-overlay bg-dark q-pa-xs"
              :class="{ 'bg-white ': isDark }"
            >
              <q-badge
                style="top: -10px; left: 7px"
                class="bg-dark text-white absolute-top-left inset-shadow"
                label="Plat Terdeteksi"
              />
              <!-- <q-card-section> -->
              <img
                :src="capturedPlate"
                alt="Detected Plate"
                class="plate-detection-image"
              />
              <!-- </q-card-section> -->
            </q-card>
          </div>

          <!-- </q-card-section> -->
        </q-card>
      </div>

      <!-- Right side - Driver Camera -->
      <div class="col-12 col-md-6">
        <q-card flat class="camera-card bg-transparent">            <Camera
              ref="driverCameraRef"
              :cameraUrl="driverCameraUrl"
              :username="gateSettings.DRIVER_CAM_USERNAME"
              :password="gateSettings.DRIVER_CAM_PASSWORD"
              :ipAddress="gateSettings.DRIVER_CAM_IP"
              :fileName="'driver'"
              :isInterval="false"
              cameraLocation="driver"
              :cameraType="driverCameraType"
              :deviceId="driverCameraDeviceId"
              @error="onCameraError"
              class="camera-feed"
              label="Kamera Pengemudi"
            />            <q-btn
              v-if="driverCameraType === 'cctv'"
              icon="refresh"
              dense flat round
              @click="driverCameraRef?.fetchCameraImage()"
              class="absolute-top-right q-ma-xs"
              style="z-index: 1; background-color: rgba(0,0,0,0.3); margin-top: 35px;"
              color="white"
            >
              <q-tooltip>Refresh Gambar CCTV</q-tooltip>
            </q-btn>
        </q-card>
      </div>
    </div>

    <!-- Control Panel Section -->
    <div class="row q-col-gutter-md q-mt-sm">
      <!-- Gate Control -->
      <div class="col-8 column justify-between">
        <!-- detected plates -->

        <q-card class="control-card q-mt-md col">
          <div>
            <q-badge
              class="absolute text-body2 text-white"
              :class="{ 'text-white': isDark }"
            >
              Plat Terdeteksi
            </q-badge>
          </div>
          <q-card-section>
            <!-- Plate Detection Overlay -->
            <transition
              enter-active-class="animate__animated animate__zoomIn"
              leave-active-class="animate__animated animate__zoomOut"
            >
              <div class="row items-center justify-center q-ml-xl">
                <template v-if="displayedPlateInfo.length">
                  <q-card
                    v-for="plate in displayedPlateInfo"
                    :key="plate.plate_number || index"
                    flat
                    class="q-pa-md bg-transparent"
                  >
                    <div class="row items-center q-gutter-sm">
                      <ALPRDetectedPlateNumber
                        :key="plate.plate_number || index"
                        :plate_number="plate?.plate_number"
                        :badge="plate?.confidence"
                      />
                    </div>
                  </q-card>
                </template>
                <template v-else>
                  <q-card
                    v-for="n in 3"
                    :key="n"
                    flat
                    class="q-pa-md bg-transparent"
                  >
                    <div class="column items-center q-gutter-sm">
                      <!-- <q-skeleton type="text" width="50px" height="24px" animation="wave" /> -->
                      <q-skeleton
                        type="text"
                        width="120px"
                        height="10dvh"
                        animation="wave"
                      />
                    </div>
                  </q-card>
                </template>
              </div>
            </transition>
          </q-card-section>
        </q-card>
        <q-card class="control-card q-mt-sm">
          <q-card-section>
            <div class="row items-center justify-between">
              <div
                class="gate-status text-h5"
                :class="{
                  'text-positive': gateStatus === 'OPEN',
                  'text-negative': gateStatus === 'CLOSED',
                }"
              >
                <q-chip
                  outline
                  :color="gateStatus === 'OPEN' ? 'positive' : 'negative'"
                  text-color="white"
                  class="text-h6"
                  icon="door_front"
                >
                  Status Gate: {{ gateStatusTranslated }}
                </q-chip>
              </div>
              <div class="row q-gutter-md">
                <q-btn
                  dense
                  push
                  :color="gateStore.loop1 ? 'positive' : 'grey-7'"
                  icon="loop"
                  label="Loop 1"
                  :loading="isProcessing"
                  class="text-bold"
                  size="md"
                  @click="onPushLoop1"
                />
                <q-btn
                  dense
                  push
                  :color="gateStore.loop2 ? 'positive' : 'grey-7'"
                  label="BUKA PINTU"
                  :loading="isProcessing"
                  class="text-bold"
                  size="md"
                  @click="onPushLoop2"
                />
                <q-btn
                  dense
                  push
                  :color="gateStore.loop3 ? 'positive' : 'grey-7'"
                  icon="loop"
                  label="Loop 3"
                  :loading="isProcessing"
                  class="text-bold"
                  size="md"
                  @click="onPushLoop3"
                />
                <q-btn
                  dense
                  push
                  color="primary"
                  icon="settings"
                  class="text-bold"
                  size="md"
                  @click="openSettings"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Activity Log -->
      <div class="col-4 q-mt-md">
        <q-card
          class="log-card q-pt-md"
          :class="{ 'bg-dark text-white': isDark }"
        >
          <div>
            <q-badge
              style="top: 0px; left: 0px"
              class="absolute text-body2 text-white"
              :class="{ 'text-white': isDark }"
            >
              Aktivitas Terbaru
            </q-badge>
          </div>
          <q-card-section>
            <q-scroll-area style="height: 25dvh">
              <q-list dense>
                <q-item
                  v-for="(log, index) in activityLogs.slice(0, 10)"
                  :key="index"
                >
                  <q-item-section>
                    <q-item-label
                      :class="{
                        'text-negative': log.isError,
                        'text-white': isDark && !log.isError,
                        'text-dark': !isDark && !log.isError,
                      }"
                    >
                      {{ log.message }}
                    </q-item-label>
                    <q-item-label caption :class="{ 'text-grey-5': isDark }">
                      {{ log.timestamp }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </q-scroll-area>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Error Display -->
    <!-- <q-dialog v-model="errorDialog">
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="error" color="negative" text-color="white" />
          <span class="q-ml-sm">{{ error }}</span>
        </q-card-section>
        <q-card-actions align="right" class="q-gutter-sm">
          <q-btn 
            flat 
            icon="settings" 
            label="Settings" 
            color="primary" 
            @click="openSettingsFromError"
          />
          <q-btn 
            flat 
            label="Dismiss" 
            color="primary" 
            v-close-popup
            />
        </q-card-actions>
      </q-card>
    </q-dialog> -->

  <q-dialog v-model="showCctvImageDialog">
    <q-card style="width: 700px; max-width: 80vw;">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Gambar CCTV - {{ currentCctvConfig?.name }}</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-img
          v-if="cctvImageUrl"
          :src="cctvImageUrl"
          spinner-color="primary"
          style="height: 400px; max-width: 100%"
          fit="contain"
        />
        <div v-else class="text-center q-pa-md">
          <q-spinner-dots color="primary" size="40px" />
          <p>Memuat gambar...</p>
        </div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Tutup" color="primary" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <!-- Upload Image Dialog -->
  <q-dialog v-model="showUploadDialog">
    <q-card style="width: 500px; max-width: 80vw;">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Upload Gambar untuk ALPR</div>
        <q-space />
        <q-btn icon="close" flat round dense @click="closeUploadDialog" />
      </q-card-section>

      <q-card-section class="q-pt-none">
        <div class="text-center">
          <q-file
            v-model="fileModel"
            label="Pilih file gambar"
            accept="image/*"
            outlined
            @update:model-value="handleFileSelect"
            class="q-mb-md"
          >
            <template v-slot:prepend>
              <q-icon name="image" />
            </template>          </q-file>
          
          <div v-if="uploading" class="q-mt-md text-center">
            <q-spinner color="primary" size="2em" />
            <div class="text-body2 q-mt-sm">Memproses ALPR...</div>
          </div>
        </div>
      </q-card-section>

      <q-card-actions align="right">        <q-btn flat label="Batal" color="grey" @click="closeUploadDialog" />
        <q-btn 
          flat 
          label="Proses ALPR" 
          color="primary" 
          :disable="!uploadedImage || uploading"
          :loading="uploading"
          @click="processUploadedImage"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

  </div>
</template>

<style scoped>
.indicator-item {
  backdrop-filter: blur(4px);
}

.connection-indicator {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  z-index: 10;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  transition: all 0.3s ease;
}

/* Add pulse animation */
.connection-indicator::before {
  content: '';
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: rgb(99, 252, 132);
  animation: pulse 1.5s ease infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(99, 252, 132, 0.7);
  }

  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(99, 252, 132, 0);
  }

  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(99, 252, 132, 0);
  }
}

/* Add red color for disconnected state */
.connection-indicator.disconnected::before {
  background-color: rgb(255, 82, 82);
  animation: pulse-red 1.5s ease infinite;
}

@keyframes pulse-red {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(255, 82, 82, 0.7);
  }

  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(255, 82, 82, 0);
  }

  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(255, 82, 82, 0);
  }
}

.connection-indicator.connected {
  background-color: rgba(0, 128, 0, 0.6);
}

.connection-indicator.disconnected {
  background-color: rgba(255, 0, 0, 0.6);
}

.manless-entry {
  height: 100vh;
  min-height: 100vh;
  background-color: #f5f5f5;
  transition: background-color 0.3s ease;
  overflow-y: auto;
  padding: 0.3rem;
}

.manless-entry.dark-mode {
  background-color: #121212;
}

.dark-mode .camera-card,
.dark-mode .control-card,
.dark-mode .log-card {
  background-color: rgba(30, 30, 30, 0.95) !important;
  color: #fff;
}

.camera-card,
.control-card,
.log-card,
.header-card {
  border-radius: 5px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s ease, color 0.3s ease;
}

.dark-mode .camera-feed {
  background-color: #1e1e1e;
  border: 1px solid #333;
}

.camera-feed {
  border-radius: 4px;
  overflow: hidden;
  background-color: #ffffff;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.plate-result {
  background-color: rgba(0, 0, 0, 0.02);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.dark-mode .plate-result {
  background-color: rgba(255, 255, 255, 0.05);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.plate-image {
  max-width: 200px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.dark-mode .plate-image {
  border-color: #333;
}

.header-card {
  background: linear-gradient(135deg, var(--q-primary) 0%, var(--q-dark) 100%);
}

.dark-mode .header-card {
  background: linear-gradient(135deg, #1e1e1e 0%, #000 100%);
}

.q-card {
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.95);
  transition: background-color 0.3s ease, color 0.3s ease;
}

.dark-mode .q-card {
  background-color: rgba(30, 30, 30, 0.95);
  color: #fff;
}

.plate-camera-container {
  position: relative;
}

.plate-detection-overlay {
  position: absolute;
  bottom: 16px;
  right: 16px;
  width: min(200px, 90%);
  height: auto;
  pointer-events: none;
  z-index: 100;
}

.plate-detection-image {
  width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transform-origin: bottom right;
}

/* Add animate.css classes for zoom animation */
.animate__animated {
  animation-duration: 0.5s;
}

.animate__zoomIn {
  animation-name: zoomIn;
}

.animate__zoomOut {
  animation-name: zoomOut;
}

@keyframes zoomIn {
  from {
    opacity: 0;
    transform: scale3d(0.3, 0.3, 0.3);
  }

  to {
    opacity: 1;
    transform: scale3d(1, 1, 1);
  }
}

@keyframes zoomOut {
  from {
    opacity: 1;
  }

  to {
    opacity: 0;
    transform: scale3d(0.3, 0.3, 0.3);
  }
}

/* Add responsive styles */
@media (max-width: 600px) {
  .text-h5 {
    font-size: 1.2rem !important;
  }

  .text-h6 {
    font-size: 1rem !important;
  }

  .q-btn {
    padding: 4px 8px;
  }

  .q-card-section {
    padding: 12px !important;
  }

  .plate-detection-overlay {
    position: relative;
    bottom: auto;
    right: auto;
    width: 100%;
    margin-top: 1rem;
  }

  .camera-feed {
    min-height: 200px;
  }

  .q-scroll-area {
    height: 200px !important;
  }
}

@media (min-width: 601px) and (max-width: 1024px) {
  .camera-feed {
    min-height: 300px;
  }

  .plate-detection-overlay {
    width: 250px;
  }
}

/* Manual upload styles */
.manual-upload-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40vh;
}

.upload-placeholder {
  text-align: center;
  padding: 2rem;
}

.uploaded-image-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.uploaded-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.processing-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}
</style>
