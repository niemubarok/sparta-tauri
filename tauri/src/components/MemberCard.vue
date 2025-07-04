



<template>
  <q-dialog v-model="showDialog" ref="dialogRef" @show="onDialogShow" >
    <q-card
      class="card membercard-bg q-mb-lg"
      ref="cardRef"
      tabindex="0"
      autofocus
      @keydown="handleKeydown"
      style="min-width:340px;max-width:420px;width:100%"
    >
      <MemberRibbon :endDate="props.endDate" />
      <div class="card-border-top"></div>
      <div class="column q-pa-md text-dark flex items-center">
        <PlatNomor v-if="plateNumber" :plate-number="plateNumber" style="transform: scale(1.25); margin-bottom: 0.5rem;" />
      </div>
      <div class="column items-start q-px-xl q-py-md">
        <div class="member-info-row">
          <span class="member-label">Nama</span>
          <span class="member-value">{{ props.nama }}</span>
        </div>
        <div class="member-info-row">
          <span class="member-label">Jenis Member</span>
          <span class="member-type-chip">{{ props.jenisMember || '-' }}</span>
        </div>
        <div class="member-info-row">
          <span class="member-label">Masa Berlaku</span>
          <span class="member-value"
            :class="{
              expired: membershipStore.isExpired(endDate),
              'expiring-soon': !membershipStore.isExpiringSoon(endDate),
              valid: !membershipStore.isExpired(endDate) && !membershipStore.isExpiringSoon(endDate)
            }"
          >
            {{ props.isExpired ? 'Expired' : props.endDate || '-' }}
          </span>
        </div>
      </div>
      <div class="membercard-footer" style="flex-direction: column; align-items: stretch; gap: 0.5rem;">
        <q-btn 
          ref="enterBtn"
          label="Enter"
          color="primary"
          class="full-width q-mb-xs text-weight-bold text-h6"
          size="lg"
          @click="onDialogOK"
          icon="login"
          style="border-radius: 12px; min-height: 48px; letter-spacing: 1px;"
        />
        <span class="text-caption text-grey-7" style="align-self: flex-end;">Member Card</span>
      </div>
    </q-card>
  </q-dialog>
</template>

<script setup>
import {  useMembershipStore } from "src/stores/membership-store";
import MemberRibbon from "./MemberRibbon.vue";
import PlatNomor from "./PlatNomor.vue";
import { computed, ref, defineExpose, onMounted, nextTick } from 'vue';
import { useDialogPluginComponent } from 'quasar';

const props = defineProps({
  nama: String,
  jenisMember: String,
  endDate: String,
  plateNumber: {
    type: String,
    default: "",
  },
});

const membershipStore = useMembershipStore();

const {dialogRef, onDialogOK} = useDialogPluginComponent()

// Expiring soon logic (7 days)
// const isExpiringSoon = computed(() => {
//   if (!props.endDate) return false;
//   return membershipStore.isExpiringSoon();
// });

// Ref dan expose untuk autofocus dari parent


const enterBtn = ref(null);
const cardRef = ref(null);
// const dialogRef = ref(null);
const showDialog = ref(true); // Dialog tampil default

// Autofocus ke tombol Enter saat mount
const setCardFocus = () => {
  let focusSet = false;
  // Prioritas: tombol Enter
  if (enterBtn.value && enterBtn.value.$el) {
    const btn = enterBtn.value.$el.querySelector('button') || enterBtn.value.$el;
    if (btn) {
      btn.focus();
      focusSet = true;
    }
  }
  // Fallback: card
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

defineEmits([{...useDialogPluginComponent.emits}])

// Keyboard handler: Enter = emit enter, Escape = tutup dialog
const handleKeydown = (event) => {
  const key = event.key.toUpperCase();
  if (key === 'ENTER') {
    event.preventDefault();
    event.stopPropagation();
    if (enterBtn.value && enterBtn.value.$el) {
      onDialogOK();
      enterBtn.value.$el.click();
    }
  } else if (key === 'ESCAPE') {
    event.preventDefault();
    event.stopPropagation();
   dialogRef.value.hide();
  }
};

defineExpose({
  focusEnter: () => {
    setCardFocus();
  }
});
</script>


<style scoped lang="scss">
.card {
  margin-bottom: 1.5rem;
  min-width: 340px;
  max-width: 420px;
  width: 100%;
  height: auto;
  border-radius: 22px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.18), 0 1.5px 8px 0 rgba(0,0,0,0.08);
  background: linear-gradient(135deg, #f8fafc 60%, #e0e7ff 100%);
  overflow: hidden;
  border: 1.5px solid #e0e7ff;
  position: relative;
  transition: box-shadow 0.2s;
}
.card:hover {
  box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.22), 0 2px 12px 0 rgba(0,0,0,0.12);
}
.card-border-top {
  width: 100%;
  height: 8px;
  background: linear-gradient(90deg, #6366f1 0%, #06b6d4 100%);
  margin-bottom: 0.5rem;
}
.member-info-row {
  display: flex;
  align-items: center;
  margin-bottom: 0.7rem;
}
.member-label {
  min-width: 120px;
  font-weight: 600;
  color: #6366f1;
  font-size: 1rem;
}
.member-value {
  font-size: 1.1rem;
  font-weight: 500;
  color: #22223b;
  margin-left: 0.5rem;
}
.member-type-chip {
  background: linear-gradient(90deg, #f59e42 0%, #fbbf24 100%);
  color: #fff;
  font-weight: 700;
  border-radius: 8px;
  padding: 2px 16px;
  font-size: 1rem;
  margin-left: 0.5rem;
  box-shadow: 0 2px 8px 0 rgba(251,191,36,0.08);
}
.expired {
  color: #e11d48 !important;
  font-weight: 700;
}
.expiring-soon {
  color: #f59e42 !important;
  font-weight: 700;
}
.valid {
  color: #059669 !important;
  font-weight: 700;
}
.membercard-bg {
  background: linear-gradient(120deg, #f8fafc 60%, #e0e7ff 100%);
}
.membercard-footer {
  width: 100%;
  margin-top: 1.2rem;
  padding: 0.7rem 1.5rem 0.2rem 1.5rem;
  background: rgba(99,102,241,0.08);
  border-bottom-left-radius: 22px;
  border-bottom-right-radius: 22px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.5rem;
}
</style>