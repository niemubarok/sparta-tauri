<template>
  <q-dialog
    ref="dialogRef"
    persistent
    no-esc-dismiss
    no-backdrop-dismiss
    @hide="onDialogHide"
  >
    <q-card 
      class="q-pa-xl" 
      style="min-width: 500px; max-width: 600px; border-radius: 15px"
    >
      <!-- Header -->
      <q-card-section class="text-center q-pb-md">
        <q-icon name="payments" size="3em" color="primary" />
        <div class="text-h4 text-weight-bold q-mt-md">Bayar Parkir</div>
        <div class="text-subtitle1 text-grey-7">{{ jenisKendaraan }}</div>
      </q-card-section>

      <!-- Tarif Display -->
      <q-card-section class="text-center q-py-lg">
        <div class="text-h2 text-weight-bold text-primary">
          {{ formatCurrency(biayaParkir) }}
        </div>
        <div class="text-subtitle2 text-grey-6 q-mt-sm">Tarif Parkir</div>
      </q-card-section>

      <!-- Payment Input -->
      <q-card-section class="q-pt-none">
        <q-input
          v-model.number="bayarAmount"
          type="number"
          label="Jumlah Bayar"
          filled
          :prefix="'Rp '"
          class="text-h5"
          :min="biayaParkir"
          autofocus
        />
        
        <!-- Quick amount buttons -->
        <div class="row q-gutter-sm q-mt-md">
          <q-btn 
            v-for="amount in quickAmounts"
            :key="amount"
            :label="formatCurrency(amount)"
            outline
            color="primary"
            size="sm"
            @click="bayarAmount = amount"
            class="col"
          />
        </div>
      </q-card-section>

      <!-- Kembalian -->
      <q-card-section v-if="kembalian > 0" class="text-center q-pt-none">
        <q-chip 
          color="positive" 
          text-color="white" 
          size="lg"
          class="q-pa-md"
        >
          <q-icon name="money" left />
          Kembalian: {{ formatCurrency(kembalian) }}
        </q-chip>
      </q-card-section>

      <!-- Action Buttons -->
      <q-card-actions align="center" class="q-pt-lg">
        <q-btn
          label="Batal"
          color="grey"
          flat
          @click="onCancel"
          class="q-px-lg"
        />
        <q-btn
          label="Bayar"
          color="primary"
          unelevated
          :disable="!isPaymentValid"
          @click="onPayment"
          class="q-px-xl"
        >
          <q-icon name="keyboard_return" right />
        </q-btn>
      </q-card-actions>

      <!-- Keyboard hint -->
      <q-card-section class="text-center q-pt-sm">
        <div class="text-caption text-grey-6">
          Tekan Enter untuk bayar • Esc untuk batal
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>


<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { useDialogPluginComponent, useQuasar } from "quasar";
import { useTransaksiStore } from "src/stores/transaksi-store";

const $q = useQuasar();
const transaksiStore = useTransaksiStore();
const { dialogRef, onDialogOK, onDialogCancel, onDialogHide } = useDialogPluginComponent();

// Payment data
const bayarAmount = ref(0);

// Computed properties
const biayaParkir = computed(() => transaksiStore.biayaParkir || 0);
const jenisKendaraan = computed(() => transaksiStore.selectedJenisKendaraan?.label || "Kendaraan");
const kembalian = computed(() => Math.max(0, bayarAmount.value - biayaParkir.value));
const isPaymentValid = computed(() => bayarAmount.value >= biayaParkir.value);

// Quick payment amounts
const quickAmounts = computed(() => {
  const tarif = biayaParkir.value;
  return [
    tarif, // Exact amount
    tarif + 5000, // +5k
    Math.ceil(tarif / 10000) * 10000, // Round up to nearest 10k
    50000, // Common amounts
    100000
  ].filter((amount, index, arr) => arr.indexOf(amount) === index && amount >= tarif)
   .sort((a, b) => a - b)
   .slice(0, 4);
});

// Format currency
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount);
};

// Event handlers
const onPayment = () => {
  if (!isPaymentValid.value) return;
  
  // Update transaction store
  transaksiStore.bayar = bayarAmount.value;
  
  // Emit success to parent
  onDialogOK({
    success: true,
    biayaParkir: biayaParkir.value,
    bayar: bayarAmount.value,
    kembalian: kembalian.value
  });
};

const onCancel = () => {
  onDialogCancel();
};

// Keyboard handling
const handleKeyDown = (event) => {
  switch (event.key) {
    case 'Enter':
      event.preventDefault();
      if (isPaymentValid.value) {
        onPayment();
      }
      break;
    case 'Escape':
      event.preventDefault();
      onCancel();
      break;
  }
};

// Lifecycle
onMounted(() => {
  // Set initial payment amount to exact tariff
  bayarAmount.value = biayaParkir.value;
  
  // Add keyboard listeners
  window.addEventListener('keydown', handleKeyDown);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyDown);
});

// Define emits
defineEmits([...useDialogPluginComponent.emits]);
</script>

<style scoped>
.q-card {
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}
</style>
