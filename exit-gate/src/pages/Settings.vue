<template>
  <q-page class="q-pa-md">
    <div class="row justify-center">
      <div class="col-12 col-md-8 col-lg-6">
        <!-- Header -->
        <div class="text-h4 text-weight-bold q-mb-lg">
          <q-icon name="settings" class="q-mr-sm" />
          Gate Settings
        </div>

        <!-- Serial Port Settings -->
        <q-card class="q-mb-lg">
          <q-card-section>
            <div class="text-h6 q-mb-md">Serial Port Configuration</div>
            
            <div class="row q-gutter-md">
              <div class="col">
                <q-select
                  v-model="settings.serial_port"
                  :options="availablePorts"
                  label="Serial Port"
                  outlined
                  emit-value
                  map-options
                  :loading="loadingPorts"
                >
                  <template v-slot:append>
                    <q-btn 
                      flat 
                      round 
                      icon="refresh" 
                      @click="refreshPorts"
                      :loading="loadingPorts"
                    />
                  </template>
                </q-select>
              </div>
              <div class="col">
                <q-select
                  v-model="settings.baud_rate"
                  :options="baudRateOptions"
                  label="Baud Rate"
                  outlined
                  emit-value
                  map-options
                />
              </div>
            </div>

            <div class="row q-gutter-md q-mt-md">
              <div class="col">
                <q-input
                  v-model.number="settings.gate_timeout"
                  type="number"
                  label="Auto-close timeout (seconds)"
                  outlined
                  min="1"
                  max="60"
                  @focus="disableScanner"
                  @blur="enableScanner"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- GPIO Settings (Raspberry Pi) -->
         <!-- v-if="gpioAvailable" -->
        <q-card class="q-mb-lg" >
          <q-card-section>
            <div class="text-h6 q-mb-md">
              <q-icon name="memory" class="q-mr-sm" />
              GPIO Configuration (Raspberry Pi)
            </div>
            
            <div class="row q-gutter-md q-mb-md">
              <div class="col-12">
                <q-select
                  v-model="settings.control_mode"
                  :options="controlModeOptions"
                  label="Gate Control Mode"
                  outlined
                  emit-value
                  map-options
                />
              </div>
            </div>

            <div v-if="settings.control_mode === 'gpio'" class="q-mt-md">
              <div class="text-subtitle2 q-mb-md">
                <q-icon name="memory" class="q-mr-sm" />
                GPIO Pin Configuration
              </div>
              
              <!-- Power GPIO -->
              <q-card flat bordered class="q-mb-md">
                <q-card-section>
                  <div class="text-subtitle2 text-primary q-mb-sm">
                    <q-icon name="power" class="q-mr-sm" />
                    Power GPIO
                  </div>
                  <div class="row q-gutter-md">
                    <div class="col">
                      <q-input
                        v-model.number="settings.power_gpio_pin"
                        type="number"
                        label="Power GPIO Pin"
                        outlined
                        min="1"
                        max="40"
                        hint="Pin untuk kontrol power sistem"
                        @focus="disableScanner"
                        @blur="enableScanner"
                      />
                    </div>
                    <div class="col">
                      <q-toggle
                        v-model="settings.power_gpio_enabled"
                        label="Enable Power GPIO"
                        left-label
                      />
                    </div>
                  </div>
                  <div class="q-mt-sm">
                    <q-btn
                      :loading="testing"
                      @click="testPowerGpio"
                      color="red"
                      outline
                      icon="power"
                      label="Test Power GPIO"
                      size="sm"
                      :disable="!settings.power_gpio_enabled || !settings.power_gpio_pin"
                    />
                  </div>
                </q-card-section>
              </q-card>

              <!-- Busy GPIO -->
              <q-card flat bordered class="q-mb-md">
                <q-card-section>
                  <div class="text-subtitle2 text-orange q-mb-sm">
                    <q-icon name="hourglass_empty" class="q-mr-sm" />
                    Busy GPIO
                  </div>
                  <div class="row q-gutter-md">
                    <div class="col">
                      <q-input
                        v-model.number="settings.busy_gpio_pin"
                        type="number"
                        label="Busy GPIO Pin"
                        outlined
                        min="1"
                        max="40"
                        hint="Pin untuk indikator busy/sibuk"
                        @focus="disableScanner"
                        @blur="enableScanner"
                      />
                    </div>
                    <div class="col">
                      <q-toggle
                        v-model="settings.busy_gpio_enabled"
                        label="Enable Busy GPIO"
                        left-label
                      />
                    </div>
                  </div>
                  <div class="q-mt-sm">
                    <q-btn
                      :loading="testing"
                      @click="testBusyGpio"
                      color="orange"
                      outline
                      icon="hourglass_empty"
                      label="Test Busy GPIO"
                      size="sm"
                      :disable="!settings.busy_gpio_enabled || !settings.busy_gpio_pin"
                    />
                  </div>
                </q-card-section>
              </q-card>

              <!-- Live GPIO -->
              <q-card flat bordered class="q-mb-md">
                <q-card-section>
                  <div class="text-subtitle2 text-green q-mb-sm">
                    <q-icon name="radio_button_checked" class="q-mr-sm" />
                    Live GPIO
                  </div>
                  <div class="row q-gutter-md">
                    <div class="col">
                      <q-input
                        v-model.number="settings.live_gpio_pin"
                        type="number"
                        label="Live GPIO Pin"
                        outlined
                        min="1"
                        max="40"
                        hint="Pin untuk indikator sistem live/aktif"
                        @focus="disableScanner"
                        @blur="enableScanner"
                      />
                    </div>
                    <div class="col">
                      <q-toggle
                        v-model="settings.live_gpio_enabled"
                        label="Enable Live GPIO"
                        left-label
                      />
                    </div>
                  </div>
                  <div class="q-mt-sm">
                    <q-btn
                      :loading="testing"
                      @click="testLiveGpio"
                      color="green"
                      outline
                      icon="radio_button_checked"
                      label="Test Live GPIO"
                      size="sm"
                      :disable="!settings.live_gpio_enabled || !settings.live_gpio_pin"
                    />
                  </div>
                </q-card-section>
              </q-card>

              <!-- Gate Trigger GPIO -->
              <q-card flat bordered class="q-mb-md">
                <q-card-section>
                  <div class="text-subtitle2 text-primary q-mb-sm">
                    <q-icon name="input" class="q-mr-sm" />
                    Gate Trigger GPIO
                  </div>
                  <div class="row q-gutter-md">
                    <div class="col">
                      <q-input
                        v-model.number="settings.gate_trigger_gpio_pin"
                        type="number"
                        label="Gate Trigger GPIO Pin"
                        outlined
                        min="1"
                        max="40"
                        hint="Pin untuk trigger buka/tutup gate"
                        @focus="disableScanner"
                        @blur="enableScanner"
                      />
                    </div>
                    <div class="col">
                      <q-toggle
                        v-model="settings.gate_trigger_gpio_enabled"
                        label="Enable Gate Trigger"
                        left-label
                      />
                    </div>
                  </div>
                  <div class="row q-gutter-md q-mt-sm">
                    <div class="col">
                      <q-toggle
                        v-model="settings.gpio_active_high"
                        label="Active High"
                        left-label
                      />
                      <div class="text-caption text-grey-6 q-mt-xs">
                        Check if relay activates on HIGH signal
                      </div>
                    </div>
                    <div class="col">
                      <q-input
                        v-model.number="settings.gpio_pulse_duration"
                        type="number"
                        label="Pulse Duration (ms)"
                        outlined
                        min="100"
                        max="5000"
                        hint="Durasi aktif GPIO trigger"
                        @focus="disableScanner"
                        @blur="enableScanner"
                      />
                    </div>
                  </div>
                  <div class="q-mt-sm">
                    <q-btn
                      :loading="testing"
                      @click="testGateTriggerGpio"
                      color="primary"
                      outline
                      icon="input"
                      label="Test Gate Trigger"
                      size="sm"
                      :disable="!settings.gate_trigger_gpio_enabled || !settings.gate_trigger_gpio_pin"
                    />
                  </div>
                </q-card-section>
              </q-card>

              <!-- GPIO Control Actions -->
              <q-card flat bordered class="q-mb-md">
                <q-card-section>
                  <div class="text-subtitle2 q-mb-md">
                    <q-icon name="settings" class="q-mr-sm" />
                    GPIO Control Actions
                  </div>
                  
                  <div class="row q-gutter-sm">
                    <q-btn
                      @click="checkGpioStatus"
                      color="info"
                      outline
                      icon="info"
                      label="Check GPIO Status"
                    />
                    <q-btn
                      :loading="testing"
                      @click="testAllGpio"
                      color="purple"
                      outline
                      icon="play_circle"
                      label="Test All GPIO"
                    />
                    <q-btn
                      @click="resetGpioConfig"
                      color="grey"
                      outline
                      icon="refresh"
                      label="Reset GPIO Config"
                    />
                  </div>
                </q-card-section>
              </q-card>

              <!-- GPIO Pin Reference -->
              <div class="q-mt-lg">
                <q-expansion-item
                  icon="pin_drop"
                  label="Raspberry Pi GPIO Pin Reference"
                  header-class="text-primary"
                >
                  <div class="q-pa-md">
                    <div class="text-subtitle2 q-mb-md">Recommended GPIO Pins for Exit Gate:</div>
                    <div class="row q-gutter-md">
                      <div class="col">
                        <q-list dense>
                          <q-item>
                            <q-item-section>
                              <q-item-label caption>Recommended Configuration:</q-item-label>
                              <q-item-label>GPIO 18 (Pin 12) - Gate Trigger</q-item-label>
                              <q-item-label>GPIO 24 (Pin 18) - Power GPIO</q-item-label>
                              <q-item-label>GPIO 23 (Pin 16) - Busy GPIO</q-item-label>
                              <q-item-label>GPIO 25 (Pin 22) - Live GPIO</q-item-label>
                            </q-item-section>
                          </q-item>
                        </q-list>
                      </div>
                      <div class="col">
                        <q-list dense>
                          <q-item>
                            <q-item-section>
                              <q-item-label caption>Avoid these pins:</q-item-label>
                              <q-item-label>GPIO 2,3 (I2C)</q-item-label>
                              <q-item-label>GPIO 10,11 (SPI)</q-item-label>
                              <q-item-label>GPIO 14,15 (UART)</q-item-label>
                            </q-item-section>
                          </q-item>
                        </q-list>
                      </div>
                    </div>
                  </div>
                </q-expansion-item>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Camera Settings -->
        <q-card class="q-mb-lg">
          <q-card-section>
            <div class="text-h6 q-mb-md">Camera Configuration</div>
            
            <div class="row q-gutter-md">
              <div class="col-12">
                <q-toggle
                  v-model="settings.camera_enabled"
                  label="Enable Camera System"
                  left-label
                />
              </div>
            </div>

            <div v-if="settings.camera_enabled" class="q-mt-md">
              <div class="row q-gutter-md">
                <div class="col">
                  <q-toggle
                    v-model="settings.webcam_enabled"
                    label="Enable Webcam"
                    left-label
                  />
                </div>
                <div class="col">
                  <q-toggle
                    v-model="settings.cctv_enabled"
                    label="Enable CCTV"
                    left-label
                  />
                </div>
              </div>

              <div v-if="settings.cctv_enabled" class="q-mt-md">
                <!-- Plate Camera Configuration -->
                <div class="text-subtitle2 q-mb-md">
                  <q-icon name="camera_alt" class="q-mr-sm" />
                  Plate Camera Configuration
                </div>
                
                <div class="row q-gutter-md q-mb-md">
                  <div class="col">
                    <q-input
                      v-model="settings.plate_camera_ip"
                      label="Camera IP Address"
                      placeholder="192.168.1.11"
                      outlined
                      @focus="disableScanner"
                      @blur="enableScanner"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="settings.plate_camera_username"
                      label="Username"
                      placeholder="admin"
                      outlined
                      @focus="disableScanner"
                      @blur="enableScanner"
                    />
                  </div>
                </div>
                
                <div class="row q-gutter-md q-mb-md">
                  <div class="col">
                    <q-input
                      v-model="settings.plate_camera_password"
                      label="Password"
                      type="password"
                      placeholder="admin123"
                      outlined
                      @focus="disableScanner"
                      @blur="enableScanner"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="settings.plate_camera_snapshot_path"
                      label="Snapshot Path"
                      placeholder="ISAPI/Streaming/channels/101/picture"
                      outlined
                      @focus="disableScanner"
                      @blur="enableScanner"
                    />
                  </div>
                </div>
                
                <div class="row q-gutter-md q-mb-md">
                  <div class="col-12">
                    <q-input
                      v-model="settings.plate_camera_full_url"
                      label="Full URL (Optional - overrides above settings)"
                      placeholder="http://username:password@192.168.1.11/ISAPI/Streaming/channels/101/picture"
                      outlined
                      @focus="disableScanner"
                      @blur="enableScanner"
                    />
                  </div>
                </div>

                <!-- Driver Camera Configuration -->
                <div class="text-subtitle2 q-mb-md q-mt-lg">
                  <q-icon name="account_circle" class="q-mr-sm" />
                  Driver Camera Configuration
                </div>
                
                <div class="row q-gutter-md q-mb-md">
                  <div class="col">
                    <q-input
                      v-model="settings.driver_camera_ip"
                      label="Camera IP Address"
                      placeholder="192.168.1.12"
                      outlined
                      @focus="disableScanner"
                      @blur="enableScanner"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="settings.driver_camera_username"
                      label="Username"
                      placeholder="admin"
                      outlined
                      @focus="disableScanner"
                      @blur="enableScanner"
                    />
                  </div>
                </div>
                
                <div class="row q-gutter-md q-mb-md">
                  <div class="col">
                    <q-input
                      v-model="settings.driver_camera_password"
                      label="Password"
                      type="password"
                      placeholder="admin123"
                      outlined
                      @focus="disableScanner"
                      @blur="enableScanner"
                    />
                  </div>
                  <div class="col">
                    <q-input
                      v-model="settings.driver_camera_snapshot_path"
                      label="Snapshot Path"
                      placeholder="ISAPI/Streaming/channels/101/picture"
                      outlined
                      @focus="disableScanner"
                      @blur="enableScanner"
                    />
                  </div>
                </div>
                
                <div class="row q-gutter-md q-mb-md">
                  <div class="col-12">
                    <q-input
                      v-model="settings.driver_camera_full_url"
                      label="Full URL (Optional - overrides above settings)"
                      placeholder="http://username:password@192.168.1.12/ISAPI/Streaming/channels/101/picture"
                      outlined
                      @focus="disableScanner"
                      @blur="enableScanner"
                    />
                  </div>
                </div>
              </div>

              <div class="row q-gutter-md q-mt-md">
                <div class="col">
                  <q-slider
                    v-model="settings.image_quality"
                    :min="0.1"
                    :max="1"
                    :step="0.1"
                    label
                    label-always
                    color="primary"
                  />
                  <div class="text-caption text-center">Image Quality: {{ Math.round(settings.image_quality * 100) }}%</div>
                </div>
                <div class="col">
                  <q-input
                    v-model.number="settings.capture_timeout"
                    type="number"
                    label="Capture timeout (ms)"
                    outlined
                    min="5000"
                    max="30000"
                    step="1000"
                    hint="Minimum 5 seconds, recommended 10-15 seconds for network cameras"
                    @focus="disableScanner"
                    @blur="enableScanner"
                  />
                </div>
              </div>

              <div class="row q-gutter-md q-mt-md">
                <q-btn
                  color="primary"
                  icon="videocam"
                  label="Test Webcam"
                  :loading="testingCamera.webcam"
                  :disable="!settings.webcam_enabled || testingCamera.cctv"
                  @click="testWebcam"
                />
                <q-btn
                  color="secondary"
                  icon="camera_alt"
                  label="Test CCTV"
                  :loading="testingCamera.cctv"
                  :disable="!settings.cctv_enabled || (!settings.plate_camera_full_url && !settings.plate_camera_ip) || testingCamera.webcam"
                  @click="testCCTV"
                />
                <q-btn
                  color="teal"
                  icon="update"
                  label="Update CCTV Config"
                  @click="updateCctvSettingsInDb"
                  flat
                />
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Connection Status -->
        <q-card class="q-mb-lg">
          <q-card-section>
            <div class="text-h6 q-mb-md">Connection Status</div>
            
            <div class="row items-center q-gutter-md">
              <q-chip 
                :color="connectionStatus.connected ? 'green' : 'red'"
                text-color="white"
                :icon="connectionStatus.connected ? 'link' : 'link_off'"
              >
                {{ connectionStatus.connected ? 'Connected' : 'Disconnected' }}
              </q-chip>
              
              <q-btn
                :color="connectionStatus.connected ? 'red' : 'green'"
                :icon="connectionStatus.connected ? 'link_off' : 'link'"
                :label="connectionStatus.connected ? 'Disconnect' : 'Connect'"
                @click="toggleConnection"
                :loading="connecting"
              />
            </div>
            
            <div v-if="connectionStatus.message" class="q-mt-md text-body2">
              {{ connectionStatus.message }}
            </div>
          </q-card-section>
        </q-card>

        <!-- Gate Test -->
        <q-card class="q-mb-lg">
          <q-card-section>
            <div class="text-h6 q-mb-md">Gate Test</div>
            <p class="text-body2 text-grey-6 q-mb-md">
              Test the gate operation to ensure it's working properly.
            </p>
            
            <div class="row q-gutter-md">
              <q-btn
                color="primary"
                icon="input"
                label="Open Gate"
                @click="testOpenGate"
                :disable="!connectionStatus.connected"
                :loading="testing"
              />
              <q-btn
                color="secondary"
                icon="output"
                label="Close Gate"
                @click="testCloseGate"
                :disable="!connectionStatus.connected"
                :loading="testing"
              />
              <q-btn
                color="orange"
                icon="science"
                label="Full Test"
                @click="testFullCycle"
                :disable="!connectionStatus.connected"
                :loading="testing"
              />
            </div>
          </q-card-section>
        </q-card>

        <!-- Barcode Scanner Settings -->
        <q-card class="q-mb-lg">
          <q-card-section>
            <div class="text-h6 q-mb-md">Barcode Scanner Settings</div>
            
            <div class="row q-gutter-md q-mb-md">
              <div class="col">
                <q-toggle
                  v-model="scannerEnabled"
                  label="Enable Barcode Scanner"
                  @update:model-value="toggleScanner"
                />
              </div>
              <div class="col">
                <q-chip 
                  :color="scannerEnabled ? 'green' : 'red'"
                  text-color="white"
                  :icon="scannerEnabled ? 'qr_code_scanner' : 'block'"
                >
                  Scanner {{ scannerEnabled ? 'Enabled' : 'Disabled' }}
                </q-chip>
              </div>
            </div>
            
            <div class="row q-gutter-md">
              <div class="col">
                <q-input
                  v-model.number="barcodeConfig.minLength"
                  type="number"
                  label="Minimum barcode length"
                  outlined
                  min="1"
                  max="50"
                  @focus="disableScanner"
                  @blur="enableScanner"
                />
              </div>
              <div class="col">
                <q-input
                  v-model.number="barcodeConfig.maxLength"
                  type="number"
                  label="Maximum barcode length"
                  outlined
                  min="1"
                  max="50"
                  @focus="disableScanner"
                  @blur="enableScanner"
                />
              </div>
            </div>
            
            <div class="row q-gutter-md q-mt-md">
              <div class="col">
                <q-input
                  v-model.number="barcodeConfig.timeout"
                  type="number"
                  label="Scan timeout (ms)"
                  outlined
                  min="50"
                  max="1000"
                  @focus="disableScanner"
                  @blur="enableScanner"
                />
              </div>
              <div class="col">
                <q-btn
                  color="purple"
                  icon="qr_code_scanner"
                  label="Test Scanner"
                  @click="testBarcodeScanner"
                  :disable="!scannerEnabled"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Database Stats -->
        <q-card class="q-mb-lg">
          <q-card-section>
            <div class="text-h6 q-mb-md">Database Statistics</div>
            
            <div class="row q-gutter-md text-center">
              <div class="col">
                <div class="text-h5 text-primary">{{ dbStats.totalTransactions }}</div>
                <div class="text-caption">Total Transactions</div>
              </div>
              <div class="col">
                <div class="text-h5 text-green">{{ dbStats.activeTransactions }}</div>
                <div class="text-caption">Active (In Parking)</div>
              </div>
              <div class="col">
                <div class="text-h5 text-orange">{{ dbStats.exitedToday }}</div>
                <div class="text-caption">Exited Today</div>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- Remote Sync Configuration -->
        <sync-manager class="q-mb-lg" />

        <!-- Audio Configuration -->
        <audio-settings class="q-mb-lg" />

        <!-- Action Buttons -->
        <div class="row q-gutter-md">
          <q-btn
            color="primary"
            icon="save"
            label="Save Settings"
            size="lg"
            @click="saveSettings"
            :loading="saving"
          />
          <q-btn
            color="grey"
            icon="refresh"
            label="Reset to Default"
            size="lg"
            @click="resetSettings"
          />
          <q-btn
            color="secondary"
            icon="arrow_back"
            label="Back to Main"
            size="lg"
            @click="$router.push('/')"
          />
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useQuasar } from 'quasar'
import { databaseService, type GateSettings } from '../services/database'
import { gateService } from '../services/gate-service'
import { barcodeScanner, type ScannerConfig } from '../services/barcode-scanner'
import { cameraService, updateCctvSettings } from '../services/camera-service'
import SyncManager from '../components/SyncManager.vue'
import AudioSettings from '../components/AudioSettings.vue'

const $q = useQuasar()

// Reactive state
const settings = ref<GateSettings>({
  _id: 'settings_gate',
  type: 'gate_settings',
  serial_port: 'COM1',
  baud_rate: 9600,
  gate_timeout: 10,
  camera_enabled: false,
  webcam_enabled: false,
  cctv_enabled: false,
  image_quality: 80,
  capture_timeout: 10000, // Increase default timeout to 10 seconds
  // CCTV Camera settings
  plate_camera_ip: '',
  plate_camera_username: 'admin',
  plate_camera_password: 'admin123',
  plate_camera_snapshot_path: 'ISAPI/Streaming/channels/101/picture',
  plate_camera_full_url: '',
  driver_camera_ip: '',
  driver_camera_username: 'admin',
  driver_camera_password: 'admin123',
  driver_camera_snapshot_path: 'ISAPI/Streaming/channels/101/picture',
  driver_camera_full_url: '',
  // GPIO configuration
  gpio_pin: 18,
  gpio_active_high: true,
  control_mode: 'serial',
  power_gpio_pin: 24,
  power_gpio_enabled: false,
  busy_gpio_pin: 23,
  busy_gpio_enabled: false,
  live_gpio_pin: 25,
  live_gpio_enabled: false,
  gate_trigger_gpio_pin: 18,
  gate_trigger_gpio_enabled: false,
  gpio_pulse_duration: 500,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
})

const scannerEnabled = ref(true)
const availablePorts = ref<string[]>([])
const loadingPorts = ref(false)
const saving = ref(false)
const testing = ref(false)
const gpioAvailable = ref(false)
const connecting = ref(false)
const testingCamera = ref({
  webcam: false,
  cctv: false
})

// GPIO control options
const controlModeOptions = ref([
  { label: 'Serial Communication', value: 'serial' },
  { label: 'GPIO (Raspberry Pi)', value: 'gpio' }
])

const baudRateOptions = [
  { label: '9600', value: 9600 },
  { label: '19200', value: 19200 },
  { label: '38400', value: 38400 },
  { label: '57600', value: 57600 },
  { label: '115200', value: 115200 }
]

// Status tracking
const connectionStatus = ref({
  connected: false,
  message: 'Not connected'
})

const dbStats = ref({
  totalTransactions: 0,
  activeTransactions: 0,
  exitedToday: 0
})

// Barcode scanner configuration
const barcodeConfig = ref<ScannerConfig>({
  minLength: 6,
  maxLength: 20,
  timeout: 300,
  suffix: 'Enter'
})

// Initialize component
onMounted(async () => {
  // Disable barcode scanner when entering settings page
  barcodeScanner.temporaryDisable()
  
  await loadSettings()
  await refreshPorts()
  await loadDatabaseStats()
  loadBarcodeConfig()
  checkConnectionStatus()
  
  // Check GPIO availability
  gpioAvailable.value = await gateService.isRaspberryPi()
  
  // Initialize scanner state
  scannerEnabled.value = barcodeScanner.isEnabled()
})

// Cleanup when leaving component
onUnmounted(() => {
  // Re-enable barcode scanner when leaving settings page
  barcodeScanner.temporaryEnable()
})

// Load current settings
async function loadSettings() {
  try {
    const currentSettings = await databaseService.getSettings()
    if (currentSettings) {
      settings.value = currentSettings
    }
  } catch (error) {
    console.error('Error loading settings:', error)
    showError('Failed to load settings')
  }
}

// Save settings with conflict resolution
async function saveSettings() {
  saving.value = true
  
  try {
    const success = await databaseService.updateSettings(settings.value)
    
    if (success) {
      // Update barcode scanner config
      barcodeScanner.updateConfig(barcodeConfig.value)
      
      // Reload settings to get the latest version
      await loadSettings()
      
      $q.notify({
        type: 'positive',
        message: 'Settings saved successfully',
        icon: 'check'
      })
    } else {
      throw new Error('Failed to save settings')
    }
  } catch (error) {
    console.error('Error saving settings:', error)
    
    // Try to reload settings to sync with latest version
    try {
      await loadSettings()
      $q.notify({
        type: 'warning',
        message: 'Settings conflict detected, please try again',
        icon: 'warning'
      })
    } catch (reloadError) {
      showError('Failed to save settings')
    }
  } finally {
    saving.value = false
  }
}

// Reset to default settings
async function resetSettings() {
  $q.dialog({
    title: 'Reset Settings',
    message: 'Are you sure you want to reset all settings to default values?',
    cancel: true,
    persistent: true
  }).onOk(async () => {
    settings.value = {
      _id: 'settings_gate',
      type: 'gate_settings',
      serial_port: 'COM1',
      baud_rate: 9600,
      gate_timeout: 10,
      camera_enabled: false,
      webcam_enabled: false,
      cctv_enabled: false,
      image_quality: 80,
      capture_timeout: 5000,
      // GPIO configuration
      gpio_pin: 18,
      gpio_active_high: true,
      control_mode: 'serial',
      power_gpio_pin: 24,
      power_gpio_enabled: false,
      busy_gpio_pin: 23,
      busy_gpio_enabled: false,
      live_gpio_pin: 25,
      live_gpio_enabled: false,
      gate_trigger_gpio_pin: 18,
      gate_trigger_gpio_enabled: false,
      gpio_pulse_duration: 500,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    
    barcodeConfig.value = {
      minLength: 6,
      maxLength: 20,
      timeout: 100
    }
    
    await saveSettings()
  })
}

// Refresh available serial ports
async function refreshPorts() {
  loadingPorts.value = true
  
  try {
    const ports = await gateService.getAvailablePorts()
    availablePorts.value = ports
  } catch (error) {
    console.error('Error refreshing ports:', error)
    showError('Failed to refresh serial ports')
  } finally {
    loadingPorts.value = false
  }
}

// Toggle serial connection
async function toggleConnection() {
  connecting.value = true
  
  try {
    if (connectionStatus.value.connected) {
      // Disconnect
      await gateService.closeSerial()
      connectionStatus.value = {
        connected: false,
        message: 'Disconnected from serial port'
      }
    } else {
      // Connect
      const success = await gateService.configureSerial({
        port: settings.value.serial_port,
        baud_rate: settings.value.baud_rate
      })
      
      connectionStatus.value = {
        connected: success,
        message: success ? 'Connected to serial port' : 'Failed to connect'
      }
    }
  } catch (error) {
    console.error('Error toggling connection:', error)
    connectionStatus.value = {
      connected: false,
      message: 'Connection error'
    }
  } finally {
    connecting.value = false
  }
}

// Toggle barcode scanner
function toggleScanner(enabled: boolean) {
  scannerEnabled.value = enabled
  if (enabled) {
    barcodeScanner.enable()
    $q.notify({
      type: 'positive',
      message: 'Barcode scanner enabled',
      icon: 'qr_code_scanner'
    })
  } else {
    barcodeScanner.disable()
    $q.notify({
      type: 'info',
      message: 'Barcode scanner disabled',
      icon: 'block'
    })
  }
}

// Check current connection status
function checkConnectionStatus() {
  const config = gateService.getSerialConfig()
  connectionStatus.value = {
    connected: config !== null,
    message: config ? `Connected to ${config.port}` : 'Not connected'
  }
}

// Test gate operations
async function testOpenGate() {
  testing.value = true
  try {
    await gateService.openGate()
    $q.notify({
      type: 'positive',
      message: 'Gate opened successfully',
      icon: 'check'
    })
  } catch (error) {
    showError('Failed to open gate')
  } finally {
    testing.value = false
  }
}

async function testCloseGate() {
  testing.value = true
  try {
    await gateService.closeGate()
    $q.notify({
      type: 'positive',
      message: 'Gate closed successfully',
      icon: 'check'
    })
  } catch (error) {
    showError('Failed to close gate')
  } finally {
    testing.value = false
  }
}

async function testFullCycle() {
  testing.value = true
  try {
    await gateService.testGate(3)
    $q.notify({
      type: 'positive',
      message: 'Gate test completed successfully',
      icon: 'check'
    })
  } catch (error) {
    showError('Gate test failed')
  } finally {
    testing.value = false
  }
}

// Test barcode scanner
function testBarcodeScanner() {
  barcodeScanner.simulateScan('TEST123456')
  $q.notify({
    type: 'info',
    message: 'Test barcode simulated: TEST123456',
    icon: 'qr_code_scanner'
  })
}

// Load barcode scanner config
function loadBarcodeConfig() {
  barcodeConfig.value = barcodeScanner.getConfig()
}

// Load database statistics
async function loadDatabaseStats() {
  try {
    // This is a simplified implementation
    // You might want to create specific methods in databaseService for these stats
    const todayStats = await databaseService.getTodayExitStats()
    
    dbStats.value = {
      totalTransactions: 0, // Implement this method
      activeTransactions: 0, // Implement this method
      exitedToday: todayStats.totalExits
    }
  } catch (error) {
    console.error('Error loading database stats:', error)
  }
}

// Utility functions
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

// Camera test functions
async function testWebcam() {
  testingCamera.value.webcam = true
  
  try {
    // Update camera service settings first
    cameraService.updateSettings({
      webcam_enabled: settings.value.webcam_enabled,
      image_quality: settings.value.image_quality / 100, // Convert percentage to decimal
      capture_timeout: settings.value.capture_timeout
    })
    
    const success = await cameraService.testWebcam()
    
    if (success) {
      $q.notify({
        type: 'positive',
        message: 'Webcam test successful!',
        icon: 'videocam'
      })
    } else {
      $q.notify({
        type: 'negative',
        message: 'Webcam test failed. Please check camera permissions.',
        icon: 'error'
      })
    }
  } catch (error) {
    console.error('Webcam test error:', error)
    $q.notify({
      type: 'negative',
      message: 'Webcam test failed: ' + error,
      icon: 'error'
    })
  } finally {
    testingCamera.value.webcam = false
  }
}

async function testCCTV() {
  testingCamera.value.cctv = true
  
  try {
    // Update camera service settings first
    cameraService.updateSettings({
      cctv_enabled: settings.value.cctv_enabled,
      plate_camera_ip: settings.value.plate_camera_ip,
      plate_camera_username: settings.value.plate_camera_username,
      plate_camera_password: settings.value.plate_camera_password,
      plate_camera_snapshot_path: settings.value.plate_camera_snapshot_path,
      plate_camera_full_url: settings.value.plate_camera_full_url,
      image_quality: settings.value.image_quality / 100, // Convert percentage to decimal
      capture_timeout: settings.value.capture_timeout
    })
    
    const success = await cameraService.testCCTV()
    
    if (success) {
      $q.notify({
        type: 'positive',
        message: 'CCTV test successful!',
        icon: 'camera_alt'
      })
    } else {
      $q.notify({
        type: 'negative',
        message: 'CCTV test failed. Please check camera configuration and network connection.',
        icon: 'error'
      })
    }
  } catch (error) {
    console.error('CCTV test error:', error)
    $q.notify({
      type: 'negative',
      message: 'CCTV test failed: ' + error,
      icon: 'error'
    })
  } finally {
    testingCamera.value.cctv = false
  }
}

// Update CCTV settings in database
async function updateCctvSettingsInDb() {
  try {
    console.log('🔧 Updating CCTV settings in database...')
    
    // First ensure the fields exist, then save current form values
    await updateCctvSettings()
    await saveSettings() // Save the current form values
    
    // Reload settings from database
    await loadSettings()
    
    $q.notify({
      type: 'positive',
      message: 'CCTV settings updated successfully!',
      icon: 'camera_alt'
    })
  } catch (error) {
    console.error('Error updating CCTV settings:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to update CCTV settings: ' + error,
      icon: 'error'
    })
  }
}

// Test GPIO configuration
async function testGpio() {
  testing.value = true
  try {
    // Validate configuration first
    if (!settings.value.gpio_pin || settings.value.gpio_active_high === undefined) {
      throw new Error('GPIO pin and active_high must be configured')
    }
    
    // Configure GPIO first
    const gpioConfig = {
      pin: settings.value.gpio_pin,
      active_high: settings.value.gpio_active_high
    }
    
    const configSuccess = await gateService.configureGpio(gpioConfig)
    if (!configSuccess) {
      throw new Error('Failed to configure GPIO')
    }
    
    const result = await gateService.testGpio()
    
    if (result) {
      $q.notify({
        type: 'positive',
        message: `GPIO test successful on pin ${settings.value.gpio_pin}`,
        icon: 'check'
      })
    } else {
      $q.notify({
        type: 'negative',
        message: 'GPIO test failed. Please check the configuration.',
        icon: 'error'
      })
    }
  } catch (error) {
    console.error('GPIO test error:', error)
    $q.notify({
      type: 'negative',
      message: 'GPIO test failed: ' + error,
      icon: 'error'
    })
  } finally {
    testing.value = false
  }
}

// Test sensor GPIO
async function testPowerGpio() {
  testing.value = true
  try {
    if (!settings.value.power_gpio_pin) {
      throw new Error('Power GPIO pin must be configured')
    }
    
    const result = await gateService.testPowerGpio({
      pin: settings.value.power_gpio_pin,
      active_high: settings.value.gpio_active_high ?? true,
      pulse_duration: settings.value.gpio_pulse_duration || 500
    })
    
    if (result) {
      $q.notify({
        type: 'positive',
        message: `Power GPIO test successful on pin ${settings.value.power_gpio_pin}`,
        icon: 'check'
      })
    } else {
      $q.notify({
        type: 'negative',
        message: 'Power GPIO test failed. Please check the configuration.',
        icon: 'error'
      })
    }
  } catch (error) {
    console.error('Power GPIO test error:', error)
    $q.notify({
      type: 'negative',
      message: 'Power GPIO test failed: ' + error,
      icon: 'error'
    })
  } finally {
    testing.value = false
  }
}

// Test busy GPIO
async function testBusyGpio() {
  testing.value = true
  try {
    if (!settings.value.busy_gpio_pin) {
      throw new Error('Busy GPIO pin must be configured')
    }
    
    const result = await gateService.testBusyGpio({
      pin: settings.value.busy_gpio_pin,
      active_high: settings.value.gpio_active_high ?? true,
      pulse_duration: settings.value.gpio_pulse_duration || 500
    })
    
    if (result) {
      $q.notify({
        type: 'positive',
        message: `Busy GPIO test successful on pin ${settings.value.busy_gpio_pin}`,
        icon: 'check'
      })
    } else {
      $q.notify({
        type: 'negative',
        message: 'Busy GPIO test failed. Please check the configuration.',
        icon: 'error'
      })
    }
  } catch (error) {
    console.error('Busy GPIO test error:', error)
    $q.notify({
      type: 'negative',
      message: 'Busy GPIO test failed: ' + error,
      icon: 'error'
    })
  } finally {
    testing.value = false
  }
}

// Test live GPIO
async function testLiveGpio() {
  testing.value = true
  try {
    if (!settings.value.live_gpio_pin) {
      throw new Error('Live GPIO pin must be configured')
    }
    
    const result = await gateService.testLiveGpio({
      pin: settings.value.live_gpio_pin,
      active_high: settings.value.gpio_active_high ?? true,
      pulse_duration: settings.value.gpio_pulse_duration || 500
    })
    
    if (result) {
      $q.notify({
        type: 'positive',
        message: `Live GPIO test successful on pin ${settings.value.live_gpio_pin}`,
        icon: 'check'
      })
    } else {
      $q.notify({
        type: 'negative',
        message: 'Live GPIO test failed. Please check the configuration.',
        icon: 'error'
      })
    }
  } catch (error) {
    console.error('Live GPIO test error:', error)
    $q.notify({
      type: 'negative',
      message: 'Live GPIO test failed: ' + error,
      icon: 'error'
    })
  } finally {
    testing.value = false
  }
}

// Test gate trigger GPIO
async function testGateTriggerGpio() {
  testing.value = true
  try {
    if (!settings.value.gate_trigger_gpio_pin) {
      throw new Error('Gate trigger GPIO pin must be configured')
    }
    
    const result = await gateService.testGateTriggerGpio({
      pin: settings.value.gate_trigger_gpio_pin,
      active_high: settings.value.gpio_active_high ?? true,
      pulse_duration: settings.value.gpio_pulse_duration || 500
    })
    
    if (result) {
      $q.notify({
        type: 'positive',
        message: `Gate trigger GPIO test successful on pin ${settings.value.gate_trigger_gpio_pin}`,
        icon: 'check'
      })
    } else {
      $q.notify({
        type: 'negative',
        message: 'Gate trigger GPIO test failed. Please check the configuration.',
        icon: 'error'
      })
    }
  } catch (error) {
    console.error('Gate trigger GPIO test error:', error)
    $q.notify({
      type: 'negative',
      message: 'Gate trigger GPIO test failed: ' + error,
      icon: 'error'
    })
  } finally {
    testing.value = false
  }
}

// Test all GPIO pins
async function testAllGpio() {
  testing.value = true
  
  try {
    const tests = []
    
    if (settings.value.power_gpio_enabled && settings.value.power_gpio_pin) {
      tests.push({ name: 'Power', test: () => testPowerGpio() })
    }
    
    if (settings.value.busy_gpio_enabled && settings.value.busy_gpio_pin) {
      tests.push({ name: 'Busy', test: () => testBusyGpio() })
    }
    
    if (settings.value.live_gpio_enabled && settings.value.live_gpio_pin) {
      tests.push({ name: 'Live', test: () => testLiveGpio() })
    }
    
    if (settings.value.gate_trigger_gpio_enabled && settings.value.gate_trigger_gpio_pin) {
      tests.push({ name: 'Gate Trigger', test: () => testGateTriggerGpio() })
    }
    
    if (tests.length === 0) {
      $q.notify({
        type: 'warning',
        message: 'No GPIO pins enabled for testing',
        icon: 'warning'
      })
      return
    }
    
    for (const { name, test } of tests) {
      $q.notify({
        type: 'info',
        message: `Testing ${name} GPIO...`,
        icon: 'play_arrow'
      })
      await test()
      await new Promise(resolve => setTimeout(resolve, 1000)) // Wait 1 second between tests
    }
    
    $q.notify({
      type: 'positive',
      message: `All GPIO tests completed (${tests.length} pins tested)`,
      icon: 'check_circle'
    })
    
  } catch (error) {
    console.error('All GPIO test error:', error)
    $q.notify({
      type: 'negative',
      message: 'GPIO test sequence failed: ' + error,
      icon: 'error'
    })
  } finally {
    testing.value = false
  }
}

// Reset GPIO configuration to defaults
function resetGpioConfig() {
  $q.dialog({
    title: 'Reset GPIO Configuration',
    message: 'Are you sure you want to reset all GPIO settings to default values?',
    cancel: true,
    persistent: true
  }).onOk(() => {
    settings.value.power_gpio_pin = 24
    settings.value.power_gpio_enabled = false
    settings.value.busy_gpio_pin = 23
    settings.value.busy_gpio_enabled = false
    settings.value.live_gpio_pin = 25
    settings.value.live_gpio_enabled = false
    settings.value.gate_trigger_gpio_pin = 18
    settings.value.gate_trigger_gpio_enabled = false
    settings.value.gpio_active_high = true
    settings.value.gpio_pulse_duration = 500
    
    $q.notify({
      type: 'positive',
      message: 'GPIO configuration reset to defaults',
      icon: 'refresh'
    })
  })
}

// Check GPIO status
async function checkGpioStatus() {
  try {
    const available = await gateService.isRaspberryPi()
    const currentMode = gateService.getControlMode()
    
    $q.notify({
      type: 'info',
      message: `GPIO Available: ${available ? 'Yes' : 'No'}, Current Mode: ${currentMode}`,
      icon: available ? 'check_circle' : 'info'
    })
  } catch (error) {
    console.error('Error checking GPIO status:', error)
    $q.notify({
      type: 'negative',
      message: 'Failed to check GPIO status',
      icon: 'error'
    })
  }
}
</script>

<style scoped>
.q-page {
  background-color: #f5f5f5;
}
</style>
