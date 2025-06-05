<script setup lang="ts">
import { onMounted } from 'vue';
import { useSettingsService } from 'stores/settings-service';

defineOptions({ name: 'App' });

const settingsService = useSettingsService();

onMounted(async () => {
  await settingsService.initializeSettings();
  // Anda mungkin ingin menangani status isLoading atau error di sini
  // misalnya, menampilkan layar loading atau pesan error
  if (settingsService.error) {
    console.error('Failed to initialize settings:', settingsService.error);
    // Tampilkan notifikasi error ke pengguna jika perlu
  }
});
</script>

<template>
  <router-view />
</template>
