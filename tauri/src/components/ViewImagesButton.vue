<template>
  <q-btn
    :color="color"
    :size="size"
    :icon="icon"
    :label="label"
    :flat="flat"
    :round="round"
    :dense="dense"
    @click="showImages"
    :disable="!transactionId"
  >
    <q-tooltip v-if="tooltip">{{ tooltip }}</q-tooltip>
  </q-btn>
</template>

<script setup>
import { useQuasar } from 'quasar';
import TransactionImagesDialog from './TransactionImagesDialog.vue';

const props = defineProps({
  transactionId: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: 'primary'
  },
  size: {
    type: String,
    default: 'sm'
  },
  icon: {
    type: String,
    default: 'camera_alt'
  },
  label: {
    type: String,
    default: ''
  },
  flat: {
    type: Boolean,
    default: true
  },
  round: {
    type: Boolean,
    default: false
  },
  dense: {
    type: Boolean,
    default: false
  },
  tooltip: {
    type: String,
    default: 'Lihat gambar CCTV'
  }
});

const $q = useQuasar();

const showImages = () => {
  if (!props.transactionId) {
    $q.notify({
      type: 'warning',
      message: 'ID transaksi tidak valid',
      position: 'top'
    });
    return;
  }

  $q.dialog({
    component: TransactionImagesDialog,
    componentProps: {
      transactionId: props.transactionId
    }
  });
};
</script>
