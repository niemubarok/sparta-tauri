<template>
  <q-dialog ref="dialogRef" @show="onDialogShow" @hide="onDialogHide" persistent>
    <q-card
      class="q-mb-lg"
      ref="cardRef"
      tabindex="0"
      autofocus
      @keydown="handleKeydown"
      style="min-width:340px;max-width:420px;width:100%"
    >
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Informasi Kendaraan</div>
        <q-space />
  <q-btn icon="close" flat round dense @click="onDialogCancel" />
      </q-card-section>
      <q-card-section>
        <div class="q-mb-md text-center">
          <q-icon name="directions_car" size="48px" color="primary" />
        </div>
        <div class="q-mb-md text-center text-h6 text-weight-bold">
          Kendaraan Sudah Di Dalam
        </div>
        <div class="q-mb-md text-center text-subtitle1">
          Plat Nomor: <span class="text-primary text-weight-bold">{{ plateNumber }}</span>
        </div>
        <!-- <div class="q-mb-md text-center text-subtitle2">
          Status Pembayaran: <span class="text-positive text-weight-bold">LUNAS</span>
        </div> -->
      </q-card-section>
      <!-- <q-card-actions align="right" class="q-pa-md">
        <q-btn
          ref="enterBtn"
          push
          label="Buka Gate"
          color="primary"
          class="full-width text-weight-bold text-h6"
          size="lg"
          @click="onDialogOK"
          icon-right="keyboard_return"
          style="border-radius: 12px; min-height: 48px; letter-spacing: 1px;"
        >
        </q-btn>
      </q-card-actions> -->
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import { useDialogPluginComponent } from 'quasar';

const props = defineProps({
  plateNumber: {
    type: String,
    default: '',
  }
});

defineEmits([...useDialogPluginComponent.emits])

const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent();
const enterBtn = ref(null);
const cardRef = ref(null);

const setCardFocus = () => {
  let focusSet = false;
  if (enterBtn.value && enterBtn.value.$el) {
    const btn = enterBtn.value.$el.querySelector('button') || enterBtn.value.$el;
    if (btn) {
      btn.focus();
      focusSet = true;
    }
  }
  if (!focusSet && cardRef.value && cardRef.value.$el) {
    try {
      cardRef.value.$el.focus();
    } catch (e) {}
  }
};

const onDialogShow = async () => {
  await nextTick();
  setTimeout(() => {
    setCardFocus();
  }, 200);
};

const handleKeydown = (event) => {
  const key = event.key.toUpperCase();
  if (key === 'ENTER') {
    event.preventDefault();
    event.stopPropagation();
    onDialogOK();
  } else if (key === 'ESCAPE') {
    event.preventDefault();
    event.stopPropagation();
    onDialogCancel();
  }
};
</script>

<style scoped>
.text-positive {
  color: #059669 !important;
}
</style>
