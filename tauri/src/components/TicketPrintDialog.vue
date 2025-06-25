<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" persistent>
    <q-card class="ticket-print-card" style="min-width: 400px;">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Cetak Tiket Parkir</div>
        <q-space />
        <q-chip 
          dense 
          class="bg-yellow-7 text-dark q-mr-sm" 
          label="Tekan ENTER untuk cetak"
        />
        <q-btn icon="close" flat round dense @click="onDialogCancel" />
      </q-card-section>

      <q-card-section>
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
                <div class="text-h6 text-weight-bold text-orange">
                  {{ formatCurrency(currentTariff) }}
                </div>
                <div class="text-caption text-warning">⚠ BELUM LUNAS</div>
              </div>
              <div v-else>
                <!-- Mode Bayar Belakang - Show message to pay at exit -->
                <div class="text-caption text-warning">
                  💳 Bayar di Pintu Keluar
                </div>
                <div class="text-caption">
                  Tarif akan dihitung berdasarkan durasi parkir
                </div>
                <div class="text-caption text-grey-6">
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
        <q-btn
          unelevated
          label="Cetak Tiket"
          color="primary"
          @click="onPrint"
          :loading="printing"
          icon="print"
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
  </q-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useDialogPluginComponent } from 'quasar';
import { formatCurrency, formatDate, formatTime } from 'src/utils/format-utils';
import { useTarifStore } from 'src/stores/tarif-store';
import { useSettingsService } from 'src/stores/settings-service';
import ls from 'localstorage-slim';

// Quasar dialog composition
const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent();

const tarifStore = useTarifStore();
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
const ticketRef = ref(null);

// Computed
// Note: showDialog is not needed when using dialog plugin

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
  
  return `${gate}${date}${time}${sequence}`;
});

const companyName = computed(() => {
  return ls.get('companyName') || 'SISTEM PARKIR';
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
const generateBarcode = () => {
  // Simple barcode generation for demo
  // In production, use a proper barcode library
  return ticketNumber.value;
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
    
    // Print using browser print API
    await printTicket();
    
    emit('printed', updatedTransaction);
    
    // For dialog usage, also call onDialogOK if available
    if (typeof onDialogOK === 'function') {
      onDialogOK(updatedTransaction);
    }
  } catch (error) {
    console.error('Error printing ticket:', error);
  } finally {
    printing.value = false;
  }
};

const printTicket = async () => {
  // Create print window with ticket content
  const printWindow = window.open('', '_blank');
  const ticketContent = ticketRef.value.innerHTML;
  
  const printHTML = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Tiket Parkir</title>
      <style>
        body {
          font-family: 'Courier New', monospace;
          font-size: 12px;
          margin: 0;
          padding: 10px;
          width: 80mm;
        }
        .ticket-header {
          text-align: center;
          margin-bottom: 10px;
        }
        .text-h6 {
          font-size: 16px;
          font-weight: bold;
        }
        .text-subtitle2 {
          font-size: 14px;
        }
        .text-caption {
          font-size: 10px;
          color: #666;
        }
        .text-weight-bold {
          font-weight: bold;
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
        .text-grey-6 {
          color: #757575;
        }
        .barcode-container {
          margin: 10px 0;
          text-align: center;
        }
        .barcode-text {
          font-size: 14px;
          font-weight: bold;
          margin-bottom: 5px;
        }
        .barcode-lines {
          display: flex;
          justify-content: center;
          align-items: end;
          height: 40px;
          margin: 5px 0;
        }
        .barcode-line {
          width: 2px;
          background: black;
          margin: 0 1px;
        }
        .vehicle-info, .time-info, .payment-info {
          margin: 10px 0;
        }
        .row {
          display: flex;
        }
        .col-6 {
          flex: 1;
        }
        .ticket-footer {
          text-align: center;
          margin-top: 10px;
          border-top: 1px dashed #666;
          padding-top: 10px;
        }
        hr {
          border: none;
          border-top: 1px dashed #666;
          margin: 10px 0;
        }
        @media print {
          body { margin: 0; }
        }
      </style>
    </head>
    <body>
      ${ticketContent}
    </body>
    </html>
  `;
  
  printWindow.document.write(printHTML);
  printWindow.document.close();
  
  // Wait for content to load, then print
  printWindow.onload = () => {
    printWindow.print();
    printWindow.close();
  };
};

// Keyboard event handler
const handleKeydown = (event) => {
  const key = event.key.toUpperCase();
  
  if (key === 'ENTER') {
    event.preventDefault();
    if (!printing.value) {
      onPrint();
    }
  } else if (key === 'ESCAPE') {
    event.preventDefault();
    if (!printing.value) {
      onDialogCancel();
    }
  }
};

// Watch for transaction changes
watch(() => props.transaction, (newTransaction) => {
  if (newTransaction) {
    console.log('TicketPrintDialog received transaction:', newTransaction);
  }
}, { immediate: true });

// Add keyboard event listeners
onMounted(async () => {
  window.addEventListener('keydown', handleKeydown);
  
  // Load tariff data when dialog opens
  try {
    await tarifStore.loadTarifBertingkat();
    await tarifStore.loadTarifPrepaid();
  } catch (error) {
    console.error('Error loading tariff data:', error);
  }
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.ticket-preview {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  max-width: 300px;
  margin: 0 auto;
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

.ticket-footer {
  border-top: 1px dashed #666;
  padding-top: 10px;
  margin-top: 15px;
}

.text-caption {
  color: #666;
  font-size: 10px;
}

.text-weight-bold {
  font-weight: bold;
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

.text-grey-6 {
  color: #757575;
}

.q-separator {
  border-top: 1px dashed #666;
  margin: 10px 0;
}
</style>
