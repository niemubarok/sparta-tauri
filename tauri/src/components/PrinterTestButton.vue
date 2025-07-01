<template>
  <q-btn 
    color="primary" 
    label="Test Printer Settings" 
    icon="print"
    @click="showTestDialog"
  />
  
  <q-dialog v-model="showDialog" maximized>
    <SettingsDialog @hide="showDialog = false" />
  </q-dialog>
</template>

<script setup>
import { ref } from 'vue';
import SettingsDialog from './SettingsDialog.vue';

const showDialog = ref(false);

const showTestDialog = () => {
  showDialog.value = true;
};
</script>
