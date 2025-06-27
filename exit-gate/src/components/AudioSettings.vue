<template>
  <q-card>
    <q-card-section>
      <div class="text-h6 q-mb-md">
        <q-icon name="volume_up" class="q-mr-sm" />
        Audio Settings
      </div>
      
      <!-- Audio Enable/Disable -->
      <div class="row items-center q-mb-md">
        <q-toggle
          v-model="audioEnabled"
          label="Enable Audio"
          color="primary"
          @update:model-value="updateAudioEnabled"
        />
        <q-chip 
          :color="audioEnabled ? 'green' : 'grey'"
          text-color="white"
          :icon="audioEnabled ? 'volume_up' : 'volume_off'"
          class="q-ml-md"
        >
          {{ audioEnabled ? 'Enabled' : 'Disabled' }}
        </q-chip>
      </div>

      <!-- Volume Control -->
      <div class="q-mb-lg">
        <div class="text-subtitle2 q-mb-sm">Volume: {{ Math.round(volume * 100) }}%</div>
        <q-slider
          v-model="volume"
          :min="0"
          :max="1"
          :step="0.1"
          color="primary"
          track-color="grey-3"
          thumb-color="primary"
          @change="updateVolume"
          :disable="!audioEnabled"
        />
      </div>

      <!-- Sound Test Buttons -->
      <div class="text-subtitle1 q-mb-md">Test Sounds</div>
      <div class="row q-gutter-md q-mb-lg">
        <q-btn
          color="blue"
          icon="qr_code_scanner"
          label="Scan"
          @click="testSound('scan')"
          :loading="testingSound === 'scan'"
          :disable="!audioEnabled"
          size="sm"
        />
        <q-btn
          color="green"
          icon="check_circle"
          label="Success"
          @click="testSound('success')"
          :loading="testingSound === 'success'"
          :disable="!audioEnabled"
          size="sm"
        />
        <q-btn
          color="orange"
          icon="input"
          label="Gate Open"
          @click="testSound('gate_open')"
          :loading="testingSound === 'gate_open'"
          :disable="!audioEnabled"
          size="sm"
        />
        <q-btn
          color="purple"
          icon="output"
          label="Gate Close"
          @click="testSound('gate_close')"
          :loading="testingSound === 'gate_close'"
          :disable="!audioEnabled"
          size="sm"
        />
        <q-btn
          color="red"
          icon="error"
          label="Error"
          @click="testSound('error')"
          :loading="testingSound === 'error'"
          :disable="!audioEnabled"
          size="sm"
        />
      </div>

      <!-- Text-to-Speech Test -->
      <div class="text-subtitle1 q-mb-md">Text-to-Speech</div>
      <div class="row q-gutter-md q-mb-lg">
        <div class="col">
          <q-input
            v-model="testMessage"
            label="Test Message"
            outlined
            placeholder="Pintu terbuka, silakan lewat"
            :disable="!audioEnabled"
            @focus="disableScanner"
            @blur="enableScanner"
          />
        </div>
        <div class="col-auto">
          <q-btn
            color="primary"
            icon="record_voice_over"
            label="Speak"
            @click="testSpeech"
            :loading="testingSpeech"
            :disable="!audioEnabled"
          />
        </div>
      </div>

      <!-- Advanced Settings -->
      <q-expansion-item
        icon="settings"
        label="Advanced Audio Settings"
        class="q-mb-md"
      >
        <div class="q-pa-md">
          <!-- Voice Settings -->
          <div class="text-subtitle2 q-mb-sm">Voice Settings</div>
          <div class="row q-gutter-md q-mb-md">
            <div class="col">
              <q-select
                v-model="voiceLanguage"
                :options="languageOptions"
                label="Language"
                outlined
                emit-value
                map-options
                @update:model-value="updateVoiceSettings"
              />
            </div>
            <div class="col">
              <q-input
                v-model.number="speechRate"
                type="number"
                label="Speech Rate"
                outlined
                min="0.5"
                max="2.0"
                step="0.1"
                @update:model-value="updateVoiceSettings"
                @focus="disableScanner"
                @blur="enableScanner"
              />
            </div>
            <div class="col">
              <q-input
                v-model.number="speechPitch"
                type="number"
                label="Speech Pitch"
                outlined
                min="0.5"
                max="2.0"
                step="0.1"
                @update:model-value="updateVoiceSettings"
                @focus="disableScanner"
                @blur="enableScanner"
              />
            </div>
          </div>

          <!-- Custom Sound Messages -->
          <div class="text-subtitle2 q-mb-sm">Custom Voice Messages</div>
          <div class="q-gutter-md">
            <q-input
              v-model="customMessages.gateOpen"
              label="Gate Open Message"
              outlined
              placeholder="Pintu terbuka, silakan lewat"
              @focus="disableScanner"
              @blur="enableScanner"
            />
            <q-input
              v-model="customMessages.exitSuccess"
              label="Exit Success Message"
              outlined
              placeholder="Terima kasih, selamat jalan"
              @focus="disableScanner"
              @blur="enableScanner"
            />
            <q-input
              v-model="customMessages.error"
              label="Error Message"
              outlined
              placeholder="Terjadi kesalahan, silakan coba lagi"
              @focus="disableScanner"
              @blur="enableScanner"
            />
          </div>
        </div>
      </q-expansion-item>

      <!-- Audio Statistics -->
      <div class="row q-gutter-md text-center q-mt-md">
        <div class="col">
          <div class="text-h6 text-primary">{{ audioStats.soundsPlayed }}</div>
          <div class="text-caption">Sounds Played</div>
        </div>
        <div class="col">
          <div class="text-h6 text-green">{{ audioStats.speechCount }}</div>
          <div class="text-caption">Speech Events</div>
        </div>
        <div class="col">
          <div class="text-h6 text-orange">{{ audioStats.errors }}</div>
          <div class="text-caption">Audio Errors</div>
        </div>
      </div>
    </q-card-section>

    <q-card-actions align="center" class="q-pa-md">
      <q-btn
        color="primary"
        icon="save"
        label="Save Settings"
        @click="saveAudioSettings"
        :loading="saving"
      />
      <q-btn
        color="blue"
        icon="play_circle"
        label="Test All Sounds"
        @click="testAllSounds"
        :loading="testingAll"
        :disable="!audioEnabled"
      />
      <q-btn
        color="grey"
        icon="refresh"
        label="Reset to Default"
        @click="resetAudioSettings"
      />
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { audioService } from '../services/audio-service'
import { barcodeScanner } from '../services/barcode-scanner'

const $q = useQuasar()

// Reactive state
const audioEnabled = ref(true)
const volume = ref(0.7)
const testingSound = ref<string | null>(null)
const testingSpeech = ref(false)
const testingAll = ref(false)
const saving = ref(false)

const testMessage = ref('Pintu terbuka, silakan lewat')
const voiceLanguage = ref('id-ID')
const speechRate = ref(1.0)
const speechPitch = ref(1.0)

const customMessages = ref({
  gateOpen: 'Pintu terbuka, silakan lewat',
  exitSuccess: 'Terima kasih, selamat jalan',
  error: 'Terjadi kesalahan, silakan coba lagi'
})

const audioStats = ref({
  soundsPlayed: 0,
  speechCount: 0,
  errors: 0
})

const languageOptions = [
  { label: 'Indonesian', value: 'id-ID' },
  { label: 'English', value: 'en-US' },
  { label: 'Javanese', value: 'jv-ID' }
]

// Initialize component
onMounted(() => {
  loadAudioSettings()
})

// Load audio settings
function loadAudioSettings() {
  const config = audioService.getConfig()
  audioEnabled.value = config.enabled
  volume.value = config.volume
}

// Update audio enabled state
function updateAudioEnabled(enabled: boolean) {
  audioService.setEnabled(enabled)
  if (enabled) {
    $q.notify({
      type: 'positive',
      message: 'Audio enabled',
      icon: 'volume_up'
    })
  } else {
    $q.notify({
      type: 'info',
      message: 'Audio disabled',
      icon: 'volume_off'
    })
  }
}

// Update volume
function updateVolume(newVolume: number) {
  audioService.setVolume(newVolume)
}

// Update voice settings
function updateVoiceSettings() {
  // Voice settings will be applied when speaking
}

// Test individual sound
async function testSound(type: 'scan' | 'success' | 'gate_open' | 'gate_close' | 'error') {
  testingSound.value = type
  
  try {
    const success = await audioService.playSound(type)
    if (success) {
      audioStats.value.soundsPlayed++
      $q.notify({
        type: 'positive',
        message: `${type.replace('_', ' ')} sound played`,
        icon: 'volume_up'
      })
    } else {
      throw new Error('Sound playback failed')
    }
  } catch (error) {
    audioStats.value.errors++
    $q.notify({
      type: 'negative',
      message: `Failed to play ${type} sound`,
      icon: 'error'
    })
  } finally {
    testingSound.value = null
  }
}

// Test speech
async function testSpeech() {
  testingSpeech.value = true
  
  try {
    const success = await audioService.speak(testMessage.value, {
      lang: voiceLanguage.value,
      rate: speechRate.value,
      pitch: speechPitch.value
    })
    
    if (success) {
      audioStats.value.speechCount++
      $q.notify({
        type: 'positive',
        message: 'Text-to-speech played',
        icon: 'record_voice_over'
      })
    } else {
      throw new Error('Speech synthesis failed')
    }
  } catch (error) {
    audioStats.value.errors++
    $q.notify({
      type: 'negative',
      message: 'Failed to play speech',
      icon: 'error'
    })
  } finally {
    testingSpeech.value = false
  }
}

// Test all sounds
async function testAllSounds() {
  testingAll.value = true
  
  try {
    await audioService.testAllSounds()
    $q.notify({
      type: 'positive',
      message: 'All sounds test completed',
      icon: 'check'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Sound test failed',
      icon: 'error'
    })
  } finally {
    testingAll.value = false
  }
}

// Save audio settings
async function saveAudioSettings() {
  saving.value = true
  
  try {
    audioService.updateConfig({
      enabled: audioEnabled.value,
      volume: volume.value
    })
    
    $q.notify({
      type: 'positive',
      message: 'Audio settings saved',
      icon: 'save'
    })
  } catch (error) {
    $q.notify({
      type: 'negative',
      message: 'Failed to save audio settings',
      icon: 'error'
    })
  } finally {
    saving.value = false
  }
}

// Reset audio settings
function resetAudioSettings() {
  $q.dialog({
    title: 'Reset Audio Settings',
    message: 'Are you sure you want to reset all audio settings to default?',
    cancel: true,
    persistent: true
  }).onOk(() => {
    audioEnabled.value = true
    volume.value = 0.7
    voiceLanguage.value = 'id-ID'
    speechRate.value = 1.0
    speechPitch.value = 1.0
    
    audioService.updateConfig({
      enabled: true,
      volume: 0.7
    })
    
    $q.notify({
      type: 'info',
      message: 'Audio settings reset to default',
      icon: 'refresh'
    })
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
