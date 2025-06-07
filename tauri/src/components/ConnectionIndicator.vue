<template>
  <div class="row q-gutter-sm">
    <!-- ALPR Mode Indicator -->
    <div 
      class="connection-indicator" 
      :class="[
        useExternalAlpr ? (isExternalAlprConnected ? 'connected' : 'disconnected') : 'connected',
        isDark ? 'dark' : 'light'
      ]"
    >
      <q-icon 
        :name="useExternalAlpr ? 'cloud' : 'computer'" 
        size="sm"
      />
      <span>{{ useExternalAlpr ? 'External ALPR' : 'Internal ALPR' }}</span>
      <div v-if="useExternalAlpr" class="text-caption connection-status">
        {{ isExternalAlprConnected ? 'Connected' : 'Disconnected' }}
      </div>
    </div>
    
    <!-- Database Connection Indicator -->
    <div 
      class="connection-indicator" 
      :class="[
        isCouchDBConnected ? 'connected' : 'disconnected',
        isDark ? 'dark' : 'light'
      ]"
    >
      <q-icon :name="iconCouchDB || couchDBIcon" />
      <span>{{ couchDBStatusText }}</span>
    </div>
  </div>
</template>

<script setup>
import { inject, computed, onMounted } from 'vue';
import { useSettingsService } from 'src/stores/settings-service';
import { useAlprStore } from 'src/stores/alpr-store';
import { isSyncing, lastSyncStatus, lastSyncError } from 'src/boot/pouchdb';

const settingsService = useSettingsService();
const alprStore = useAlprStore();

// Get gateSettings from the settings service
const gateSettings = computed(() => settingsService.gateSettings);

// ALPR mode and connection status - updated to use gateSettings
const useExternalAlpr = computed(() => gateSettings.value?.USE_EXTERNAL_ALPR || false);
const isExternalAlprConnected = computed(() => alprStore.isWsConnected);

// CouchDB connection status based on sync status
const isCouchDBConnected = computed(() => {
  // Connected if not in error/denied state
  return !['denied', 'error'].includes(lastSyncStatus.value);
});

const couchDBStatusText = computed(() => {
  if (lastSyncStatus.value === 'error') return 'Error';
  if (lastSyncStatus.value === 'denied') return 'Denied';
  if (isSyncing.value) return 'Syncing';
  // If not syncing and no error/denied, consider it connected (idle or completed)
  if (!isSyncing.value && !['error', 'denied'].includes(lastSyncStatus.value)) return 'DB Connected';
  return 'Connecting'; // Default or initial state (e.g. paused without error after initial load)
});

const couchDBIcon = computed(() => {
  if (lastSyncStatus.value === 'error' || lastSyncStatus.value === 'denied') return 'error_outline';
  if (isSyncing.value) return 'sync';
  // If not syncing and no error/denied, show 'storage' icon for connected/idle state
  if (!isSyncing.value && !['error', 'denied'].includes(lastSyncStatus.value)) return 'storage';
  return 'dns'; // Default/connecting icon
});

const isDark = inject('isDark', false)

defineProps({
  iconCCTV: {
    type: String,
    default: ''
  },
  iconCouchDB: {
    type: String,
    default: ''
  }
})

onMounted(() => {
  console.log("Gate settings for ALPR:", gateSettings.value)
})
</script>

<style scoped>
.connection-indicator {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  backdrop-filter: blur(4px);
  transition: all 0.3s ease;
}

.connection-indicator.light {
  background-color: rgba(255, 255, 255, 0.9);
  color: #000;
}

.connection-indicator.dark {
  background-color: rgba(30, 30, 30, 0.9);
  color: #fff;
}

.connection-indicator.connected.light {
  background-color: rgba(1, 128, 1, 0.89);
  color: #f3f8f3;
}

.connection-indicator.connected.dark {
  background-color: rgba(0, 200, 0, 0.2);
  color: #00ff00;
}

.connection-indicator.disconnected.light {
  background-color: rgba(255, 0, 0, 0.2);
  color: #8b0000;
}

.connection-indicator.disconnected.dark {
  background-color: rgba(255, 0, 0, 0.2);
  color: #ff6b6b;
}

.connection-status {
  margin-left: 4px;
  font-size: 10px;
}
</style>