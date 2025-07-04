<!-- filepath: tauri/src/components/TicketPrintDialog.vue -->
<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" @show="onDialogShow" persistent>
    <q-card 
      ref="cardRef"
      class="ticket-print-card overflow-hidden" 
      style="min-width: 400px;"
      tabindex="0"
      autofocus
      @keydown="handleKeydown"
    >
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Cetak Tiket Parkir</div>
        <q-space />
        <q-chip 
          dense 
          class="bg-yellow-7 text-dark q-mr-sm" 
          label="Tekan ENTER untuk cetak"
        />
        <!-- <q-btn 
          flat 
          dense 
          icon="settings" 
          @click="showPrinterTest = true" 
          title="Test Printer"
          class="q-mr-sm"
        /> -->
        <q-btn icon="close" flat round dense @click="onDialogCancel" />
      </q-card-section>

      <q-card-section>
        <!-- Printer Status Banner -->
        <div v-if="printerStatus" class="q-mb-md">
          <q-banner 
            :class="printerStatus.success ? 'bg-positive' : 'bg-warning'"
            text-color="white"
            rounded
            dense
          >
            <template v-slot:avatar>
              <q-icon 
                :name="printerStatus.success ? 'local_print_shop' : 'warning'" 
                color="white" 
              />
            </template>
            {{ printerStatus.message }}
          </q-banner>
        </div>

        <!-- Current Printer Info -->
        <div v-if="currentPrinter" class="q-mb-md">
          <q-chip 
            :color="currentPrinter.includes('EPSON') || currentPrinter.includes('TM-T82') ? 'primary' : 'secondary'"
            text-color="white" 
            icon="print"
            dense
          >
            Printer: {{ currentPrinter }}
          </q-chip>
          
          <!-- <q-btn
            flat
            dense
            icon="cable"
            @click="testCurrentPrinter"
            :loading="testingPrinter"
            title="Test printer connection"
            class="q-ml-sm"
          /> -->
        </div>

        <!-- Ticket Preview -->
        <div class="ticket-preview q-pa-md" ref="ticketRef">
          <div class="ticket-header text-center q-mb-md">
            <div class="text-h6 text-weight-bold">{{ companyName }}</div>
            <div class="text-subtitle2">TIKET PARKIR</div>
            <div class="text-caption">{{ gateLocation }}</div>
          </div>

          <q-separator class="q-my-md" />

          <div class="ticket-content">
            <!-- Barcode -->
            <div class="text-center q-mb-md">
              <div class="barcode-container">
                <div class="barcode-text">{{ ticketNumber }}</div>
                <div class="barcode-lines">
                  <div v-for="n in 20" :key="n" class="barcode-line" 
                       :style="{ height: Math.random() * 30 + 20 + 'px' }"></div>
                </div>
                <div class="text-caption q-mt-xs">{{ barcodeData }}</div>
              </div>
            </div>

            <!-- Vehicle Information -->
            <div class="vehicle-info q-mb-md">
              <div class="row">
                <div class="col-6">
                  <div class="text-caption">Plat Nomor:</div>
                  <div class="text-weight-bold">{{ transaction?.plat_nomor }}</div>
                </div>
                <div class="col-6">
                  <div class="text-caption">Jenis Kendaraan:</div>
                  <div class="text-weight-bold">{{ transaction?.jenis_kendaraan }}</div>
                </div>
              </div>
            </div>

            <!-- Time Information -->
            <div class="time-info q-mb-md">
              <div class="row">
                <div class="col-6">
                  <div class="text-caption">Tanggal:</div>
                  <div class="text-weight-bold">{{ formatDate(entryTime) }}</div>
                </div>
                <div class="col-6">
                  <div class="text-caption">Waktu Masuk:</div>
                  <div class="text-weight-bold">{{ formatTime(entryTime) }}</div>
                </div>
              </div>
            </div>

            <!-- Payment Information -->
            <div class="payment-info q-mb-md">
              <div v-if="isPrepaidTransaction && isTransactionPaid">
                <!-- Mode Bayar Depan - Show tariff and paid status -->
                <div class="text-caption">Tarif Dibayar:</div>
                <div class="text-h6 text-weight-bold text-primary">
                  {{ formatCurrency(currentTariff) }}
                </div>
                <div class="text-caption text-positive">✓ LUNAS</div>
              </div>
              <div v-else-if="isPrepaidTransaction && !isTransactionPaid">
                <!-- Mode Bayar Depan tapi belum bayar -->
                <div class="text-caption">Tarif:</div>
                <div class="text-h6 text-weight-bold text-orange-8">
                  {{ formatCurrency(currentTariff) }}
                </div>
                <div class="text-caption text-orange-8 text-weight-bold">⚠ BELUM LUNAS</div>
              </div>
              <div v-else>
                <!-- Mode Bayar Belakang - Show message to pay at exit -->
                <div class="text-caption text-dark text-weight-bold">
                  💳 Bayar di Pintu Keluar
                </div>
                <div class="text-caption text-dark">
                  Tarif akan dihitung berdasarkan durasi parkir
                </div>
                <div class="text-caption text-grey-8">
                  Tarif dasar: {{ formatCurrency(currentTariff) }}
                </div>
              </div>
            </div>

            <!-- Footer -->
            <q-separator class="q-my-md" />
            <div class="ticket-footer text-center">
              <div class="text-caption">
                Simpan tiket ini untuk keluar parkir
              </div>
              <div class="text-caption">
                Petugas: {{ operatorName }}
              </div>
            </div>
          </div>
        </div>
      </q-card-section>

      <q-card-actions align="right" class="q-pa-md">
        <q-btn
          flat
          label="Batal"
          color="grey"
          @click="onDialogCancel"
          :disable="printing"
        >
          <q-badge
            color="grey-6"
            text-color="white"
            label="ESC"
            class="q-ml-xs"
          />
        </q-btn>
        
        <!-- <q-btn
          flat
          label="Test Print"
          color="orange"
          @click="testPrint"
          :loading="testPrinting"
          icon="bug_report"
          :disable="printing"
        /> -->
        
        <q-btn
          unelevated
          label="Cetak Tiket"
          color="primary"
          @click="onPrint"
          :loading="printing"
          icon="print"
          ref="printButtonRef"
        >
          <q-badge
            color="orange"
            text-color="white"
            label="ENTER"
            class="q-ml-xs"
          />
        </q-btn>
      </q-card-actions>
    </q-card>

    <!-- Printer Test Dialog -->
    <!-- <PrinterTestDialog 
      v-model="showPrinterTest"
      @hide="showPrinterTest = false"
    /> -->
  </q-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';
import { useDialogPluginComponent } from 'quasar';
import { formatCurrency, formatDate, formatTime } from 'src/utils/format-utils';
import { useTarifStore } from 'src/stores/tarif-store';
import { useGateStore } from 'src/stores/gate-store';
import { useTransaksiStore } from 'src/stores/transaksi-store';
import { useMembershipStore } from 'src/stores/membership-store';
import { invoke } from '@tauri-apps/api/core';
import { useSettingsService } from 'src/stores/settings-service';
import ls from 'localstorage-slim';
// import PrinterTestDialog from './PrinterTestDialog.vue';

// Quasar dialog composition
const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent();

const tarifStore = useTarifStore();
const gateStore = useGateStore();
const transaksiStore = useTransaksiStore();
const membershipStore = useMembershipStore();
const settingsService = useSettingsService();

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  transaction: {
    type: Object,
    default: null
  }
});

const emit = defineEmits([
  // Dialog events
  ...useDialogPluginComponent.emits,
  // Custom events
  'update:modelValue', 
  'printed', 
  'cancelled'
]);

// Reactive data
const printing = ref(false);
const testPrinting = ref(false);
const testingPrinter = ref(false);
const ticketRef = ref(null);
const showPrinterTest = ref(false);
const currentPrinter = ref('');
const printerStatus = ref(null);
const cardRef = ref(null); // Add cardRef
const printButtonRef = ref(null); // Add printButtonRef

// Computed
const entryTime = computed(() => new Date());

// Compute the correct tariff based on operation mode and vehicle type
const currentTariff = computed(() => {
  if (!props.transaction) return 0;
  
  // If prepaid mode and already paid, use the paid amount
  if (props.transaction.is_prepaid && props.transaction.bayar_masuk) {
    return props.transaction.bayar_masuk;
  }
  
  // Get tariff from tarif store based on operation mode
  const vehicleId = props.transaction.id_mobil || props.transaction.id_kendaraan;
  if (!vehicleId) return props.transaction.tarif || 0;
  
  if (settingsService.isPrepaidMode) {
    // Use prepaid tariff
    const prepaidTariff = tarifStore.activeTarifPrepaid.find(t => t.id_mobil === vehicleId);
    return prepaidTariff?.tarif_prepaid || props.transaction.tarif || 0;
  } else {
    // Use progressive tariff (basic rate)
    const progressiveTariff = tarifStore.activeTarif.find(t => t.id_mobil === vehicleId);
    return progressiveTariff?.tarif || props.transaction.tarif || 0;
  }
});

const isPrepaidTransaction = computed(() => {
  return props.transaction?.is_prepaid || settingsService.isPrepaidMode;
});

const isTransactionPaid = computed(() => {
  return props.transaction?.is_paid || (props.transaction?.bayar_masuk > 0);
});

const ticketNumber = computed(() => {
  if (!props.transaction) return '';
  
  // Generate ticket number: GATE + DATE + TIME + SEQUENCE
  const now = new Date();
  const gate = ls.get('lokasiPos')?.value || '01';
  const date = now.toISOString().slice(0, 10).replace(/-/g, '');
  const time = now.toTimeString().slice(0, 8).replace(/:/g, '');
  const sequence = String(Math.floor(Math.random() * 9999) + 1).padStart(4, '0');
  
  return `${time}${sequence}`;
});

const barcodeData = computed(() => {
  // Generate barcode data for the ticket
  return `${ticketNumber.value}`;
});

const companyName = computed(() => {
  return ls.get('companyName') || 'SISTEM PARKIR SPARTA';
});

const gateLocation = computed(() => {
  const lokasi = ls.get('lokasiPos');
  return lokasi ? `${lokasi.label} - PINTU MASUK` : 'PINTU MASUK';
});

const operatorName = computed(() => {
  const pegawai = ls.get('pegawai');
  return pegawai?.nama || 'OPERATOR';
});

// Methods
const refreshStoreData = async () => {
  try {
    console.log('🔄 Refreshing store data after print...');
    
    // Refresh membership store
    if (membershipStore.loadMembers) {
      await membershipStore.loadMembers();
      console.log('✅ Membership store refreshed');
    }
    
    // Refresh tarif store 
    if (tarifStore.loadTarifFromLocal) {
      await tarifStore.loadTarifFromLocal();
      console.log('✅ Tarif store refreshed');
    }
    
    // Refresh transaksi counters
    if (transaksiStore.getCountVehicleInToday) {
      await transaksiStore.getCountVehicleInToday();
      console.log('✅ Vehicle count refreshed');
    }
    
    console.log('🎉 All stores refreshed successfully');
  } catch (error) {
    console.error('❌ Error refreshing store data:', error);
  }
};

const onDialogShow = async () => {
  console.log('🎫 TicketPrintDialog shown, attempting to set focus...');
  
  // Wait for dialog to be fully rendered
  await nextTick();
  
  setTimeout(() => {
    setDialogFocus();
  }, 200);
};

const setDialogFocus = () => {
  let focusSet = false;
  
  // Try to focus the card element
  if (cardRef.value && cardRef.value.$el) {
    try {
      cardRef.value.$el.focus();
      focusSet = true;
      console.log('✅ Focus set on card element');
    } catch (error) {
      console.warn('❌ Failed to focus card element:', error);
    }
  }
  
  // Fallback: focus the dialog container
  if (!focusSet && dialogRef.value && dialogRef.value.$el) {
    try {
      const dialogContent = dialogRef.value.$el.querySelector('.q-card');
      if (dialogContent) {
        dialogContent.focus();
        focusSet = true;
        console.log('✅ Focus set on dialog content');
      }
    } catch (error) {
      console.warn('❌ Failed to focus dialog content:', error);
    }
  }
  
  // Last resort: focus the print button
  if (!focusSet && printButtonRef.value && printButtonRef.value.$el) {
    try {
      printButtonRef.value.$el.focus();
      console.log('✅ Focus set on print button');
    } catch (error) {
      console.warn('❌ Failed to focus print button:', error);
    }
  }
};

const generateBarcode = () => {
  return barcodeData.value;
};

const onPrint = async () => {
  printing.value = true;
  
  try {
    // Update transaction with ticket number
    const updatedTransaction = {
      ...props.transaction,
      ticket_number: ticketNumber.value,
      barcode: generateBarcode()
    };
    
    // Print thermal ticket with barcode
    await printThermalTicket();
    
    // Open gate after successful print
    await gateStore.writeToPort('entry', '*open#');
    
    emit('printed', updatedTransaction);
    
    // Refresh store data instead of reloading page
    await refreshStoreData();
    
    // For dialog usage, also call onDialogOK if available
    if (typeof onDialogOK === 'function') {
      onDialogOK(updatedTransaction);
    }
  } catch (error) {
    console.error('Error printing ticket:', error);
  } finally {
    printing.value = false;
    // window.location.reload() //- let parent handle refresh
  }
};

const printThermalTicket = async () => {
  try {
    // Prepare ticket data for thermal printer - SEMUA FIELD HARUS camelCase sesuai serde
    const ticketData = {
      ticketNumber: ticketNumber.value,           // ✅ ticket_number
      platNomor: props.transaction?.plat_nomor || '',           // ✅ plat_nomor
      jenisKendaraan: props.transaction?.jenis_kendaraan || '', // ✅ jenis_kendaraan  
      waktuMasuk: formatTime(entryTime.value),                 // ✅ waktu_masuk
      tarif: currentTariff.value,                              // ✅ tarif
      companyName: companyName.value,                          // ✅ company_name
      gateLocation: gateLocation.value,                        // ✅ gate_location
      operatorName: operatorName.value,                        // ✅ operator_name
      isPaid: isTransactionPaid.value,                         // ✅ is_paid
      barcodeData: generateBarcode()                           // ✅ barcode_data
    };

    console.log('Printing thermal ticket with data:', ticketData);

    // Print to thermal printer (EPSON TM-T82X)
    const result = await invoke('print_thermal_ticket', { 
      ticketData,
      printerName: currentPrinter.value || null
    });
    
    console.log('Thermal print result:', result);
    
    // Update printer status
    printerStatus.value = {
      success: true,
      message: result.message || 'Tiket berhasil dicetak!'
    };
    
  } catch (error) {
    console.error('Error printing to thermal printer:', error);
    
    // Update printer status
    printerStatus.value = {
      success: false,
      message: `Error: ${error}`
    };
    
    // Fallback to browser print if available
    console.log('Attempting fallback to browser print...');
    await printTicketBrowser();
    
    throw error;
  }
};

const printTicketBrowser = async () => {
  try {
    // Browser fallback printing
    await new Promise((resolve) => {
      setTimeout(() => {
        window.print();
        resolve();
      }, 100);
    });
  } catch (error) {
    console.error('Browser print fallback failed:', error);
    throw new Error('Semua metode print gagal');
  }
};

const testPrint = async () => {
  testPrinting.value = true;
  
  try {
    const testBarcodeData = `TEST-${Date.now().toString(36).toUpperCase()}`;
    
    const result = await invoke('test_print_barcode', { 
      barcodeData: testBarcodeData,
      printerName: currentPrinter.value || null
    });
    
    printerStatus.value = {
      success: true,
      message: 'Test print berhasil - Printer siap digunakan'
    };
    
  } catch (error) {
    console.error('Test print error:', error);
    
    printerStatus.value = {
      success: false,
      message: `Test print gagal: ${error}`
    };
  } finally {
    testPrinting.value = false;
  }
};

const testCurrentPrinter = async () => {
  if (!currentPrinter.value) {
    return;
  }
  
  testingPrinter.value = true;
  
  try {
    const result = await invoke('test_printer_connection', { 
      printerIdentifier: currentPrinter.value 
    });
    
    printerStatus.value = {
      success: true,
      message: `Koneksi ke ${currentPrinter.value} berhasil`
    };
    
  } catch (error) {
    console.error('Printer connection test error:', error);
    
    printerStatus.value = {
      success: false,
      message: `Koneksi ke ${currentPrinter.value} gagal: ${error}`
    };
  } finally {
    testingPrinter.value = false;
  }
};

const loadDefaultPrinter = async () => {
  try {
    const printer = await invoke('get_default_printer');
    currentPrinter.value = printer;
    
    console.log('Default printer loaded:', printer);
    
    // Test connection to default printer
    // if (printer && printer !== 'Manual Entry') {
    //   await testCurrentPrinter();
    // }
  } catch (error) {
    console.error('Failed to load default printer:', error);
    
    // Try to discover printers
    try {
      const printers = await invoke('list_thermal_printers');
      if (printers.length > 0) {
        currentPrinter.value = printers[0];
        console.log('Using first available printer:', printers[0]);
      }
    } catch (discoverError) {
      console.error('Failed to discover printers:', discoverError);
      
      printerStatus.value = {
        success: false,
        message: 'Tidak ada printer thermal yang terdeteksi'
      };
    }
  }
};

// Improved keyboard handler - now attached directly to the card
const handleKeydown = (event) => {
  const key = event.key.toUpperCase();
  
  if (key === 'ENTER') {
    event.preventDefault();
    event.stopPropagation(); // Prevent event bubbling
    if (!printing.value && !testPrinting.value) {
      onPrint();
    }
  } else if (key === 'ESCAPE') {
    event.preventDefault();
    event.stopPropagation();
    if (!printing.value && !testPrinting.value) {
      onDialogCancel();
    }
  } else if (key === 'F2') {
    event.preventDefault();
    event.stopPropagation();
    if (!printing.value && !testPrinting.value) {
      testPrint();
    }
  }
};

// Updated onMounted with improved focus handling
onMounted(async () => {
  await nextTick();
  
  // Wait a bit longer for dialog to fully render
  setTimeout(() => {
    setDialogFocus();
  }, 300); // Increased delay to 300ms for better reliability
  
  try {
    await tarifStore.loadTarifPrepaidFromLocal();
    await tarifStore.loadTarifMemberFromLocal();
  } catch (error) {
    console.error('Error loading tariff data:', error);
  }
  
  await loadDefaultPrinter();
});

// Remove window event listener cleanup
onUnmounted(() => {
});
</script>

<style scoped>
.ticket-print-card {
  outline: none; /* Remove default focus outline */
}

.ticket-print-card:focus {
  box-shadow: 0 0 0 2px #1976d2; /* Add custom focus indicator */
}

.ticket-preview {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  max-width: 300px;
  margin: 0 auto;
  color: #000000;
}

.ticket-preview .text-h6 {
  color: #000000;
}

.ticket-preview .text-subtitle2 {
  color: #000000;
}

.ticket-header {
  border-bottom: 1px dashed #666;
  padding-bottom: 10px;
}

.barcode-container {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
}

.barcode-text {
  font-size: 14px;
  font-weight: bold;
  letter-spacing: 2px;
  color: #000000;
}

.barcode-lines {
  display: flex;
  justify-content: center;
  align-items: end;
  height: 40px;
  margin: 10px 0;
}

.barcode-line {
  width: 2px;
  background: black;
  margin: 0 1px;
  transition: height 0.3s ease;
}

.barcode-line:nth-child(odd) {
  background: black;
}

.barcode-line:nth-child(even) {
  background: black;
  opacity: 0.7;
}

.vehicle-info, .time-info, .payment-info {
  margin: 15px 0;
}

.vehicle-info .text-caption,
.time-info .text-caption,
.payment-info .text-caption {
  color: #666666;
  font-weight: 500;
}

.vehicle-info .text-weight-bold,
.time-info .text-weight-bold,
.payment-info .text-weight-bold {
  color: #000000;
}

.ticket-footer {
  border-top: 1px dashed #666;
  padding-top: 10px;
  margin-top: 15px;
}

.ticket-footer .text-caption {
  color: #000000;
}

.text-caption {
  color: #333333;
  font-size: 10px;
}

.text-weight-bold {
  font-weight: bold;
  color: #000000;
}

.text-primary {
  color: #1976d2;
}

.text-positive {
  color: #21ba45;
}

.text-warning {
  color: #f2c037;
}

.text-orange {
  color: #ff9800;
}

.text-orange-8 {
  color: #e65100;
}

.text-grey-8 {
  color: #424242;
}

.text-dark {
  color: #000000;
}

.q-separator {
  border-top: 1px dashed #666;
  margin: 10px 0;
}

.q-banner {
  border-radius: 8px;
}
</style>