<template>
  <div class="row q-gutter-lg justify-center" style="height: fit-content">
    <q-card
      class="cursor-pointer listCard bg-primary"
      @click="selectJenisKendaraan('mobil', 'A')"
    >
      <q-card-section class="text-center">
        <q-icon name="directions_car" class="text-white" size="15em"></q-icon>
        <div class="text-white text-h6 q-mt-md">Mobil</div>
        <q-chip color="yellow" text-color="dark" label="A" class="q-mt-sm" />
      </q-card-section>
    </q-card>

    <q-card
      class="cursor-pointer listCard bg-teal"
      @click="selectJenisKendaraan('motor', 'C')"
    >
      <q-card-section class="text-center">
        <q-icon name="two_wheeler" class="text-white" size="15em" />
        <div class="text-white text-h6 q-mt-md">Motor</div>
        <q-chip color="yellow" text-color="dark" label="C" class="q-mt-sm" />
      </q-card-section>
    </q-card>

    <q-card
      class="cursor-pointer listCard bg-orange"
      @click="selectJenisKendaraan('truk', 'D')"
    >
      <q-card-section class="text-center">
        <q-icon name="local_shipping" class="text-white" size="15em" />
        <div class="text-white text-h6 q-mt-md">Truk / Box</div>
        <q-chip color="yellow" text-color="dark" label="D" class="q-mt-sm" />
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useQuasar } from "quasar";
import { useTransaksiStore } from "src/stores/transaksi-store";
import { useComponentStore } from "src/stores/component-store";
import { useTarifStore } from "src/stores/tarif-store";
import PaymentDialog from "src/components/PaymentDialog.vue";
import ls from "localstorage-slim";

const $q = useQuasar();
const transaksiStore = useTransaksiStore();
const componentStore = useComponentStore();
const tarifStore = useTarifStore();

const selectedJenisKendaraan = ref("");

// Define emits for parent communication
const emit = defineEmits(['vehicle-selected', 'payment-completed']);

const selectJenisKendaraan = async (jenis, shortcut) => {
  try {
    // Set selected vehicle type
    const jenisKendaraanData = {
      id: getVehicleId(jenis),
      label: getVehicleLabel(jenis),
      shortcut: shortcut,
      tarif: getVehicleTariff(jenis)
    };

    transaksiStore.selectedJenisKendaraan = jenisKendaraanData;
    transaksiStore.biayaParkir = getVehicleTariff(jenis);
    transaksiStore.bayar = 0; // Initialize bayar amount
    selectedJenisKendaraan.value = jenis;

    // Ensure lokasiPos is set
    if (!transaksiStore.lokasiPos || !transaksiStore.lokasiPos.value) {
      transaksiStore.lokasiPos = { value: '01', label: 'Gate 1' };
      ls.set('lokasiPos', transaksiStore.lokasiPos);
    }

    // Set plate number if not set
    if (!transaksiStore.platNomor) {
      transaksiStore.platNomor = 'PREPAID-' + Date.now();
    }

    // Initialize current transaction for prepaid mode
    transaksiStore.currentTransaction = {
      id: 'PREPAID-' + Date.now(),
      no_pol: transaksiStore.platNomor,
      waktu_masuk: new Date().toISOString(),
      status: 0, // entry
      jenis_kendaraan: jenisKendaraanData.label
    };

    // Emit to parent that vehicle is selected
    emit('vehicle-selected', jenisKendaraanData);

    // For mode bayar di depan, immediately show payment dialog
    const paymentDialog = $q.dialog({
      component: PaymentDialog,
      persistent: true,
      noEscDismiss: true,
      noBackdropDismiss: true
    });

    paymentDialog.onOk(async (result) => {
      if (result.success) {
        // Payment completed, open gate
        await openGateAfterPayment();
        
        // Emit payment completed event
        emit('payment-completed', { success: true, ...result });
        
        $q.notify({
          type: 'positive',
          message: `Pembayaran berhasil. Kembalian: ${formatCurrency(result.kembalian)}`,
          position: 'top'
        });
      }
    });

    paymentDialog.onCancel(() => {
      // Reset state if payment is cancelled
      transaksiStore.resetTransactionState();
      selectedJenisKendaraan.value = "";
      
      $q.notify({
        type: 'info',
        message: 'Pembayaran dibatalkan',
        position: 'top'
      });
    });

  } catch (error) {
    console.error('Error selecting vehicle type:', error);
    $q.notify({
      type: 'negative',
      message: 'Terjadi kesalahan saat memilih jenis kendaraan',
      position: 'top'
    });
  }
};

const getVehicleId = (jenis) => {
  switch (jenis) {
    case 'mobil': return 1;
    case 'motor': return 2;
    case 'truk': return 3;
    default: return 1;
  }
};

const getVehicleLabel = (jenis) => {
  switch (jenis) {
    case 'mobil': return 'Mobil';
    case 'motor': return 'Motor';
    case 'truk': return 'Truk / Box';
    default: return 'Mobil';
  }
};

const getVehicleTariff = (jenis) => {
  try {
    // Get tariff from tarifStore based on vehicle type
    const jenisKendaraanId = getVehicleId(jenis);
    const tarif = tarifStore.getTarifByJenisKendaraan(jenisKendaraanId);
    
    if (tarif && tarif.tarif) {
      return tarif.tarif;
    }
    
    // Fallback to default values if not found in store
    switch (jenis) {
      case 'mobil': return 5000;
      case 'motor': return 2000;
      case 'truk': return 10000;
      default: return 5000;
    }
  } catch (error) {
    console.error('Error getting vehicle tariff from store:', error);
    // Fallback to default values
    switch (jenis) {
      case 'mobil': return 5000;
      case 'motor': return 2000;
      case 'truk': return 10000;
      default: return 5000;
    }
  }
};

const openGateAfterPayment = async () => {
  try {
    // Open gate using component store
    componentStore.openGate();
    
    // Create entry transaction for prepaid mode
    await transaksiStore.createEntryTransaction();
    
    // Update statistics
    await transaksiStore.getCountVehicleInToday();
    
    // Reset transaction state after a delay
    setTimeout(() => {
      transaksiStore.resetTransactionState();
      selectedJenisKendaraan.value = "";
    }, 3000);
    
  } catch (error) {
    console.error('Error opening gate after payment:', error);
  }
};

// Format currency helper
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount);
};

// Add keyboard support
const handleKeyDown = (event) => {
  const key = event.key.toUpperCase();
  
  switch (key) {
    case 'A':
      selectJenisKendaraan('mobil', 'A');
      break;
    case 'C':
      selectJenisKendaraan('motor', 'C');
      break;
    case 'D':
      selectJenisKendaraan('truk', 'D');
      break;
  }
};

// Lifecycle hooks
onMounted(async () => {
  // Load tarif data from store
  await tarifStore.loadTarifFromLocal();
  
  // Add keyboard event listener
  window.addEventListener('keydown', handleKeyDown);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyDown);
});
</script>
