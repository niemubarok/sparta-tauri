<template>
  <q-card>
    <q-card-section>
      <div class="text-h6 q-mb-md">
        <q-icon name="sync" class="q-mr-sm" />
        Remote Database Sync
      </div>
      
      <!-- Sync Status -->
      <div class="row items-center q-gutter-md q-mb-md">
        <q-chip 
          :color="syncStatus.connected ? 'green' : 'red'"
          text-color="white"
          :icon="syncStatus.connected ? 'cloud_done' : 'cloud_off'"
        >
          {{ syncStatus.connected ? 'Connected' : 'Disconnected' }}
        </q-chip>
        
        <q-chip 
          v-if="syncStatus.sync_active"
          color="blue"
          text-color="white"
          icon="sync"
        >
          Syncing...
        </q-chip>
        
        <div v-if="syncStatus.last_sync" class="text-caption text-grey-6">
          Last sync: {{ formatDateTime(syncStatus.last_sync) }}
        </div>
      </div>

      <!-- Error Message -->
      <q-banner 
        v-if="syncStatus.error_message"
        class="bg-red-1 text-red-8 q-mb-md"
        icon="error"
      >
        {{ syncStatus.error_message }}
      </q-banner>

      <!-- Sync Configuration -->
      <div class="q-gutter-md">
        <!-- URL Information -->
        <q-banner class="bg-blue-1 text-blue-8 q-mb-md" icon="info">
          <div class="text-body2">
            <strong>Database Server URL Format:</strong><br>
            • CouchDB Server: <code>http://localhost:5984</code><br>
            • Remote Server: <code>http://192.168.1.100:5984</code><br>
            • With auth: <code>http://username:password@server:5984</code><br>
            • <strong>Note:</strong> Enter base URL only (without database name)<br>
            • System will automatically connect to: transactions, kendaraan, tarif
          </div>
        </q-banner>

        <q-input
          v-model="syncConfig.remote_url"
          label="CouchDB Server URL (base URL only)"
          placeholder="http://localhost:5984"
          outlined
          :rules="[
            val => !!val || 'Server URL is required',
            val => (val.startsWith('http://') || val.startsWith('https://')) || 'URL must start with http:// or https://',
            val => !val.includes('/transactions') && !val.includes('/kendaraan') && !val.includes('/tarif') || 'Enter base URL only, without database name'
          ]"
          hint="Base server URL without database name"
          @focus="disableScanner"
          @blur="enableScanner"
        >
          <template v-slot:prepend>
            <q-icon name="link" />
          </template>
        </q-input>

        <div class="row q-gutter-md">
          <div class="col">
            <q-input
              v-model="syncConfig.username"
              label="Username (optional)"
              outlined
              @focus="disableScanner"
              @blur="enableScanner"
            >
              <template v-slot:prepend>
                <q-icon name="person" />
              </template>
            </q-input>
          </div>
          <div class="col">
            <q-input
              v-model="syncConfig.password"
              label="Password (optional)"
              type="password"
              outlined
              @focus="disableScanner"
              @blur="enableScanner"
            >
              <template v-slot:prepend>
                <q-icon name="lock" />
              </template>
            </q-input>
          </div>
        </div>

        <div class="row q-gutter-md">
          <div class="col">
            <q-toggle
              v-model="syncConfig.auto_sync"
              label="Auto Sync"
              color="primary"
            />
          </div>
          <div class="col">
            <q-toggle
              v-model="syncConfig.continuous"
              label="Continuous Sync"
              color="primary"
              :disable="!syncConfig.auto_sync"
            />
          </div>
        </div>

        <div class="row q-gutter-md">
          <div class="col">
            <q-input
              v-model.number="syncConfig.sync_interval"
              type="number"
              label="Sync Interval (minutes)"
              outlined
              min="1"
              max="1440"
              :disable="syncConfig.continuous || !syncConfig.auto_sync"
              @focus="disableScanner"
              @blur="enableScanner"
            />
          </div>
          <div class="col">
            <q-input
              v-model.number="syncConfig.retry_attempts"
              type="number"
              label="Retry Attempts"
              outlined
              min="1"
              max="10"
              @focus="disableScanner"
              @blur="enableScanner"
            />
          </div>
        </div>
      </div>

      <!-- Sync Statistics -->
      <div class="row q-gutter-md q-mt-md text-center">
        <div class="col">
          <div class="text-h5 text-primary">{{ syncStatus.docs_synced }}</div>
          <div class="text-caption">Documents Synced</div>
        </div>
        <div class="col">
          <div class="text-h5 text-orange">{{ syncStatus.pending_changes }}</div>
          <div class="text-caption">Pending Changes</div>
        </div>
        <div class="col">
          <div class="text-h5 text-purple">{{ conflictsCount }}</div>
          <div class="text-caption">Conflicts</div>
        </div>
      </div>
    </q-card-section>

    <q-card-actions align="center" class="q-pa-md">
      <q-btn
        color="primary"
        icon="save"
        label="Save Config"
        @click="saveSyncConfig"
        :loading="saving"
      />
      <q-btn
        color="green"
        icon="sync"
        label="Test Connection"
        @click="testConnection"
        :loading="testing"
        :disable="!syncConfig.remote_url"
      />
      <q-btn
        color="blue"
        icon="sync"
        label="Manual Sync"
        @click="triggerManualSync"
        :loading="syncing"
        :disable="!syncStatus.connected"
      />
      <q-btn
        v-if="conflictsCount > 0"
        color="red"
        icon="warning"
        label="Resolve Conflicts"
        @click="showConflictDialog = true"
      />
    </q-card-actions>

    <!-- Conflicts Dialog -->
    <q-dialog v-model="showConflictDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Sync Conflicts</div>
          <div class="text-body2 q-mt-md">
            {{ conflictsCount }} documents have sync conflicts. 
            This usually happens when the same document is modified in multiple places.
          </div>
        </q-card-section>

        <q-card-section v-if="conflicts.length > 0">
          <q-list bordered>
            <q-item 
              v-for="conflict in conflicts" 
              :key="conflict._id"
              class="q-mb-sm"
            >
              <q-item-section>
                <q-item-label>{{ conflict._id }}</q-item-label>
                <q-item-label caption>{{ conflict.type }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-btn
                  flat
                  color="primary"
                  label="Keep Local"
                  @click="resolveConflict(conflict._id)"
                />
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Close" v-close-popup />
          <q-btn 
            color="red" 
            label="Resolve All" 
            @click="resolveAllConflicts"
            :loading="resolvingConflicts"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'
import { databaseService, type SyncConfig, type SyncStatus } from '../services/database'
import { barcodeScanner } from '../services/barcode-scanner'

const $q = useQuasar()

// Reactive state
const syncConfig = ref<SyncConfig>({
  remote_url: '',
  username: '',
  password: '',
  auto_sync: false,
  sync_interval: 15,
  retry_attempts: 3,
  continuous: false
})

const syncStatus = ref<SyncStatus>({
  connected: false,
  last_sync: null,
  sync_active: false,
  error_message: null,
  docs_synced: 0,
  pending_changes: 0
})

const saving = ref(false)
const testing = ref(false)
const syncing = ref(false)
const resolvingConflicts = ref(false)
const showConflictDialog = ref(false)
const conflicts = ref<any[]>([])
const conflictsCount = ref(0)

// Initialize component
onMounted(async () => {
  await loadSyncConfig()
  loadSyncStatus()
  await loadConflicts()
  
  // Listen for sync status updates
  databaseService.addSyncStatusListener(handleSyncStatusUpdate)
})

// Cleanup
onUnmounted(() => {
  databaseService.removeSyncStatusListener(handleSyncStatusUpdate)
})

// Load sync configuration
async function loadSyncConfig() {
  try {
    const settings = await databaseService.getSettings()
    if (settings?.sync_config) {
      syncConfig.value = { ...settings.sync_config }
    }
  } catch (error) {
    console.error('Error loading sync config:', error)
    showError('Failed to load sync configuration')
  }
}

// Load sync status
function loadSyncStatus() {
  syncStatus.value = databaseService.getSyncStatus()
}

// Handle sync status updates
function handleSyncStatusUpdate(status: SyncStatus) {
  syncStatus.value = status
}

// Save sync configuration with conflict resolution
async function saveSyncConfig() {
  saving.value = true
  
  try {
    const success = await databaseService.updateSyncConfig(syncConfig.value)
    
    if (success) {
      // Reload sync configuration to get latest version
      await loadSyncConfig()
      
      $q.notify({
        type: 'positive',
        message: 'Sync configuration saved successfully',
        icon: 'check'
      })
    } else {
      throw new Error('Failed to save configuration')
    }
  } catch (error) {
    console.error('Error saving sync config:', error)
    
    // Try to reload configuration to sync with latest version
    try {
      await loadSyncConfig()
      $q.notify({
        type: 'warning',
        message: 'Configuration conflict detected, please try again',
        icon: 'warning'
      })
    } catch (reloadError) {
      showError('Failed to save sync configuration')
    }
  } finally {
    saving.value = false
  }
}

// Test connection
async function testConnection() {
  testing.value = true
  
  try {
    const success = await databaseService.initializeRemoteSync(syncConfig.value)
    
    if (success) {
      $q.notify({
        type: 'positive',
        message: 'Connection test successful',
        icon: 'check_circle'
      })
    } else {
      throw new Error('Connection failed')
    }
  } catch (error) {
    console.error('Connection test failed:', error)
    showError('Connection test failed')
  } finally {
    testing.value = false
  }
}

// Trigger manual sync
async function triggerManualSync() {
  syncing.value = true
  
  try {
    const success = await databaseService.triggerSync()
    
    if (success) {
      $q.notify({
        type: 'positive',
        message: 'Manual sync completed',
        icon: 'sync'
      })
      await loadConflicts()
    } else {
      throw new Error('Sync failed')
    }
  } catch (error) {
    console.error('Manual sync failed:', error)
    showError('Manual sync failed')
  } finally {
    syncing.value = false
  }
}

// Load conflicts
async function loadConflicts() {
  try {
    conflicts.value = await databaseService.getSyncConflicts()
    conflictsCount.value = conflicts.value.length
  } catch (error) {
    console.error('Error loading conflicts:', error)
  }
}

// Resolve individual conflict
async function resolveConflict(docId: string) {
  try {
    const success = await databaseService.resolveConflictLocal(docId)
    
    if (success) {
      $q.notify({
        type: 'positive',
        message: 'Conflict resolved',
        icon: 'check'
      })
      await loadConflicts()
    } else {
      throw new Error('Failed to resolve conflict')
    }
  } catch (error) {
    console.error('Error resolving conflict:', error)
    showError('Failed to resolve conflict')
  }
}

// Resolve all conflicts
async function resolveAllConflicts() {
  resolvingConflicts.value = true
  
  try {
    let resolved = 0
    
    for (const conflict of conflicts.value) {
      const success = await databaseService.resolveConflictLocal(conflict._id)
      if (success) resolved++
    }
    
    $q.notify({
      type: 'positive',
      message: `Resolved ${resolved} conflicts`,
      icon: 'check'
    })
    
    await loadConflicts()
    showConflictDialog.value = false
  } catch (error) {
    console.error('Error resolving conflicts:', error)
    showError('Failed to resolve conflicts')
  } finally {
    resolvingConflicts.value = false
  }
}

// Utility functions
function formatDateTime(dateString: string): string {
  return new Date(dateString).toLocaleString()
}

function showError(message: string) {
  $q.notify({
    type: 'negative',
    message,
    icon: 'error'
  })
}

// Scanner control functions for input fields
function disableScanner() {
  barcodeScanner.temporaryDisable()
}

function enableScanner() {
  barcodeScanner.temporaryEnable()
}
</script>

<style scoped>
.q-card {
  max-width: 800px;
}
</style>
