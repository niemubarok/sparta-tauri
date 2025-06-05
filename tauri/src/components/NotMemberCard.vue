<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide" persistent class="futuristic-dialog-wrapper full-width full-height" maximized>
    <q-card class="not-member-card text-white glassmorphism-effect column items-center justify-center">
      <q-card-section class="text-center q-pa-lg">
        <q-icon name="mdi-car-off" size="10em" class="q-mb-md icon-gradient" />
        <div class="text-h1 text-futuristic q-mb-sm">BUKAN PENGHUNI</div>
        <div class="text-h3 text-futuristic q-mt-md">
          <q-icon name="mdi-alert-circle-outline" size="1.5em" class="q-mr-sm" />Kendaraan Tidak Terdaftar
        </div>
      </q-card-section>

      <q-card-section class="q-pt-none q-px-xl">
        <p class="text-h2 text-center futuristic-text-body">
          Silakan hubungi petugas keamanan untuk bantuan lebih lanjut.
        </p>
      </q-card-section>

     </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { useQuasar, useDialogPluginComponent } from 'quasar';
import { ref, onMounted } from 'vue';

const props = defineProps({
  // You can define props here if needed from the parent
});

const $q = useQuasar();
const { dialogRef, onDialogHide, onDialogOK, onDialogCancel } = useDialogPluginComponent();

const contactSecurity = () => {
  $q.dialog({
    title: '<span class="text-futuristic">Informasi Kontak</span>',
    message: '<div class="text-futuristic-subtle">Silakan hubungi pos keamanan di nomor <strong>0812-3456-7890</strong> atau melalui interkom.</div>',
    html: true,
    ok: {
      push: true,
      label: 'Mengerti',
      color: 'primary',
      class: 'futuristic-dialog-button'
    },
    persistent: true,
    class: 'futuristic-dialog'
  }).onOk(() => {
    // console.log('OK')
  });
};

// Auto-close dialog after 10 seconds
onMounted(() => {
  setTimeout(() => {
    if (dialogRef.value) { // Check if dialog is active
      onDialogOK(); // or onDialogCancel() depending on desired behavior
    }
  }, 3000);
});

</script>

<style scoped lang="scss">
.futuristic-dialog-wrapper .q-dialog__inner {
  backdrop-filter: blur(5px); /* Optional: add blur to the background of the dialog itself */
}

.not-member-card {
  border-radius: 0; /* Full screen, no radius needed */
  border: none; /* No border for full screen */
  box-shadow: none; /* No shadow for full screen */
  width: 100%;
  height: 100%;
  display: flex; /* Added for centering content */
  flex-direction: column; /* Added for centering content */
  align-items: center; /* Added for centering content */
  justify-content: center; /* Added for centering content */
}

.glassmorphism-effect {
  background: rgba(15, 18, 26, 0.85); /* Darker, more opaque for full screen */
  backdrop-filter: blur(10px); /* Stronger blur for full screen */
  -webkit-backdrop-filter: blur(10px);
  /* border: 1px solid rgba(25, 28, 36, 0.3); // Not needed for full screen */
}

.glassmorphism-effect {
  background: rgba(25, 28, 36, 0.6); /* Darker, slightly transparent background */
  border-radius: 16px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(7.5px);
  -webkit-backdrop-filter: blur(7.5px);
  border: 1px solid rgba(25, 28, 36, 0.3);
}

.text-futuristic {
  font-family: 'Orbitron', sans-serif; /* Example futuristic font */
  font-weight: 700;
  letter-spacing: 1.5px; /* Increased spacing */
  color: #00e5ff; /* Neon blue */
  text-shadow: 0 0 8px #00e5ff, 0 0 15px #00e5ff, 0 0 25px #00e5ff; /* Enhanced shadow */
}

.text-futuristic-subtle {
  font-family: 'Roboto Condensed', sans-serif; /* Cleaner, modern font */
  color: #b0bec5; /* Light grey-blue */
}

.futuristic-text-body {
  font-family: 'Roboto Condensed', sans-serif;
  color: #cfd8dc; /* Lighter grey for body */
  line-height: 1.7;
}

.icon-gradient {
  background: linear-gradient(45deg, #00e5ff, #ff00ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 5px #00e5ff) drop-shadow(0 0 10px #ff00ff); /* Enhanced glow */
}

.futuristic-button {
  font-family: 'Orbitron', sans-serif;
  color: #00e5ff;
  border: 1px solid #00e5ff;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 8px 16px; /* Added padding for better touch targets */
  &:hover {
    background-color: rgba(0, 229, 255, 0.1);
    box-shadow: 0 0 10px #00e5ff, 0 0 20px #00e5ff;
  }
}

.futuristic-button--close {
  color: #ff5252; /* Reddish color for close/cancel */
  border-color: #ff5252;
  &:hover {
    background-color: rgba(255, 82, 82, 0.1);
    box-shadow: 0 0 10px #ff5252, 0 0 20px #ff5252;
  }
}

/* Styling for the dialog */
:global(.futuristic-dialog .q-dialog__title) {
  font-family: 'Orbitron', sans-serif;
  color: #00e5ff;
}

:global(.futuristic-dialog .q-dialog__message) {
  font-family: 'Roboto Condensed', sans-serif;
  color: #cfd8dc;
}

:global(.futuristic-dialog-button .q-btn__content) {
  font-family: 'Orbitron', sans-serif;
  text-transform: uppercase;
}

/* Import Orbitron font if not already available globally */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto+Condensed:wght@300;400;700&display=swap');

</style>