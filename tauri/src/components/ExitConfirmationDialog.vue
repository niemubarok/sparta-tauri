<template>
  <q-dialog v-model="showDialog" persistent>
    <q-card class="exit-confirmation-card" style="min-width: 600px; max-width: 800px;">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Konfirmasi Kendaraan Keluar</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup @click="onCancel" />
      </q-card-section>

      <q-card-section>
        <div class="row q-col-gutter-md" v-if="transaction">
          <!-- Vehicle Information -->
          <div class="col-12 col-md-6">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle1 text-weight-bold q-mb-md">Informasi Kendaraan</div>
                <q-list dense>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Plat Nomor</q-item-label>
                      <q-item-label class="text-h6">{{ transaction.plat_nomor }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Jenis Kendaraan</q-item-label>
                      <q-item-label>{{ transaction.jenis_kendaraan }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Waktu Masuk</q-item-label>
                      <q-item-label>{{ formatDateTime(transaction.waktu_masuk) }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item>
                    <q-item-section>
                      <q-item-label caption>Durasi Parkir</q-item-label>
                      <q-item-label class="text-weight-bold">{{ calculateDuration(transaction.waktu_masuk) }}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item v-if="transaction.ticket_number">
                    <q-item-section>
                      <q-item-label caption>Nomor Tiket</q-item-label>
                      <q-item-label>{{ transaction.ticket_number }}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>

          <!-- Payment Information -->
          <div class="col-12 col-md-6">
            <q-card flat bordered>
              <q-card-section>
                <div class="text-subtitle1 text-weight-bold q-mb-md">Informasi Pembayaran</div>
                
                <!-- For prepaid transactions -->
                <div v-if="transaction.is_prepaid">
                  <q-banner class="bg-positive text-white rounded-borders q-mb-md">
                    <template v-slot:avatar>
                      <q-icon name="check_circle" />
                    </template>
                    Sudah dibayar di depan
                  </q-banner>
                  <q-list dense>
                    <q-item>
                      <q-item-section>
                        <q-item-label caption>Tarif yang Dibayar</q-item-label>
                        <q-item-label class="text-h6">Rp {{ formatCurrency(transaction.tarif_dibayar || 0) }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </div>

                <!-- For regular transactions -->
                <div v-else>
                  <q-list dense>
                    <q-item>
                      <q-item-section>
                        <q-item-label caption>Tarif Dasar</q-item-label>
                        <q-item-label>Rp {{ formatCurrency(calculatedFee.baseFee) }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item v-if="calculatedFee.additionalFee > 0">
                      <q-item-section>
                        <q-item-label caption>Tarif Tambahan</q-item-label>
                        <q-item-label>Rp {{ formatCurrency(calculatedFee.additionalFee) }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-separator class="q-my-sm" />
                    <q-item>
                      <q-item-section>
                        <q-item-label caption>Total Tarif</q-item-label>
                        <q-item-label class="text-h6 text-primary">Rp {{ formatCurrency(calculatedFee.totalFee) }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>

                  <!-- Payment input for regular transactions -->
                  <div class="q-mt-md">
                    <q-input
                      v-model.number="amountPaid"
                      label="Jumlah Dibayar"
                      type="number"
                      outlined
                      :rules="[val => val >= calculatedFee.totalFee || 'Jumlah kurang dari total tarif']"
                      @update:model-value="calculateChange"
                    />
                    
                    <div v-if="change > 0" class="q-mt-sm q-pa-sm bg-positive text-white rounded-borders text-center">
                      <div class="text-caption">Kembalian</div>
                      <div class="text-h6">Rp {{ formatCurrency(change) }}</div>
                    </div>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-card-section>

      <q-card-actions align="right" class="q-pa-md">
        <q-btn
          flat
          label="Batal"
          color="grey"
          @click="onCancel"
          :disable="processing"
        />
        <q-btn
          unelevated
          label="Konfirmasi Keluar"
          color="primary"
          @click="onConfirm"
          :loading="processing"
          :disable="!canConfirm"
          icon="exit_to_app"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useTarifStore } from 'src/stores/tarif-store';
import { formatCurrency, formatDateTime } from 'src/utils/format-utils';

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

const emit = defineEmits(['update:modelValue', 'confirmed', 'cancelled']);

const tarifStore = useTarifStore();

// Reactive data
const processing = ref(false);
const amountPaid = ref(0);
const change = ref(0);

// Computed
const showDialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
});

const calculatedFee = computed(() => {
  if (!props.transaction || props.transaction.is_prepaid) {
    return { baseFee: 0, additionalFee: 0, totalFee: 0 };
  }

  const entryTime = new Date(props.transaction.waktu_masuk);
  const exitTime = new Date();
  const durationHours = Math.ceil((exitTime - entryTime) / (1000 * 60 * 60));
  
  // Get tariff based on vehicle type
  const vehicleType = props.transaction.jenis_kendaraan;
  const tariff = tarifStore.getTariffByVehicleType(vehicleType);
  
  if (!tariff) {
    return { baseFee: 5000, additionalFee: 0, totalFee: 5000 }; // Default fee
  }

  const baseFee = tariff.tarif_awal || 5000;
  const hourlyRate = tariff.tarif_perjam || 2000;
  
  let additionalFee = 0;
  if (durationHours > 1) {
    additionalFee = (durationHours - 1) * hourlyRate;
  }
  
  const totalFee = baseFee + additionalFee;
  
  return { baseFee, additionalFee, totalFee };
});

const canConfirm = computed(() => {
  if (!props.transaction) return false;
  
  if (props.transaction.is_prepaid) {
    return true; // Prepaid transactions can always be confirmed
  }
  
  return amountPaid.value >= calculatedFee.value.totalFee;
});

// Methods
const calculateDuration = (entryTime) => {
  const entry = new Date(entryTime);
  const now = new Date();
  const diffMs = now - entry;
  
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  
  if (hours > 0) {
    return `${hours} jam ${minutes} menit`;
  } else {
    return `${minutes} menit`;
  }
};

const calculateChange = () => {
  if (amountPaid.value >= calculatedFee.value.totalFee) {
    change.value = amountPaid.value - calculatedFee.value.totalFee;
  } else {
    change.value = 0;
  }
};

const onConfirm = async () => {
  processing.value = true;
  
  try {
    const paymentData = {
      transaction: props.transaction,
      amountPaid: props.transaction.is_prepaid ? props.transaction.tarif_dibayar : amountPaid.value,
      change: props.transaction.is_prepaid ? 0 : change.value,
      totalFee: props.transaction.is_prepaid ? props.transaction.tarif_dibayar : calculatedFee.value.totalFee,
      isPrepaid: props.transaction.is_prepaid || false
    };
    
    emit('confirmed', paymentData);
  } catch (error) {
    console.error('Error confirming exit:', error);
  } finally {
    processing.value = false;
  }
};

const onCancel = () => {
  emit('cancelled');
};

// Watch for transaction changes to reset payment amount
watch(() => props.transaction, (newTransaction) => {
  if (newTransaction && !newTransaction.is_prepaid) {
    amountPaid.value = calculatedFee.value.totalFee;
    calculateChange();
  } else {
    amountPaid.value = 0;
    change.value = 0;
  }
}, { immediate: true });
</script>

<style scoped>
.exit-confirmation-card {
  min-height: 400px;
}

.text-h6 {
  color: var(--q-primary);
}

.rounded-borders {
  border-radius: 8px;
}
</style>
