<!-- filepath: tauri/src/components/PrinterTestDialog.vue -->
<template>
  <q-dialog ref="dialogRef" @hide="onDialogHide">
    <q-card style="min-width: 600px; max-width: 800px">
      <q-card-section>
        <div class="text-h6">Test Printer & Barcode EPSON TM-T82X</div>
        <div class="text-caption text-grey-6">
          Test koneksi printer thermal dan pencetakan barcode untuk sistem parkir
        </div>
      </q-card-section>

      <q-card-section>
        <!-- Quick Actions -->
        <div class="row q-gutter-md q-mb-md">
          <q-btn
            color="secondary"
            label="Discover All Printers"
            icon="search"
            @click="discoverPrinters"
            :loading="discovering"
          />
          
          <q-btn
            color="info"
            label="List Thermal Printers"
            icon="print"
            @click="listThermalPrinters"
            :loading="loadingPrinters"
          />

          <q-btn
            color="primary"
            label="Check EPSON Printers"
            icon="local_print_shop"
            @click="checkEpsonPrinters"
            :loading="checkingEpson"
          />
          
          <q-btn
            color="orange"
            label="Clear Cache"
            icon="refresh"
            @click="clearCacheAndRefresh"
            :disable="discovering || loadingPrinters || checkingEpson"
            title="Clear cache dan refresh semua data"
          />
          
          <q-btn
            color="red"
            label="Emergency Reset"
            icon="warning"
            @click="emergencyReset"
            :disable="false"
            title="Reset semua state jika ada masalah"
          />
        </div>

        <!-- Printer Selection -->
        <q-select
          v-model="selectedPrinter"
          :options="printers"
          label="Pilih Printer"
          filled
          emit-value
          map-options
          @update:model-value="onPrinterSelected"
          class="q-mb-md"
        >
          <template v-slot:no-option>
            <q-item>
              <q-item-section class="text-grey">
                Tidak ada printer yang terdeteksi
              </q-item-section>
            </q-item>
          </template>
          
          <template v-slot:prepend>
            <q-icon 
              :name="getSelectedPrinterIcon()" 
              :color="getSelectedPrinterColor()"
            />
          </template>
          
          <template v-slot:append>
            <q-btn
              flat
              dense
              icon="info"
              @click="checkSelectedPrinterStatus"
              :loading="checkingStatus === selectedPrinter"
              :disable="!selectedPrinter"
              title="Check printer status"
            />
          </template>
        </q-select>

        <!-- Test Data Section -->
        <div class="row q-gutter-md q-mb-md">
          <div class="col">
            <q-input
              v-model="testBarcode"
              label="Test Barcode Data"
              placeholder="Masukkan data untuk test barcode"
              filled
            >
              <template v-slot:append>
                <q-btn
                  flat
                  dense
                  icon="refresh"
                  @click="generateRandomBarcode"
                  title="Generate random barcode"
                />
              </template>
            </q-input>
          </div>
          
          <div class="col-auto">
            <q-input
              v-model="testTarif"
              label="Test Tarif"
              type="number"
              filled
              style="width: 120px"
            />
          </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="row q-gutter-sm q-mb-md">
          <q-btn
            color="primary"
            label="Test Print Ticket"
            icon="receipt"
            @click="testPrintBarcode"
            :loading="printing"
            :disable="!testBarcode || !selectedPrinter"
          />
          
          <q-btn
            color="orange"
            label="Test Connection Only"
            icon="cable"
            @click="testConnection"
            :loading="testingConnection"
            :disable="!selectedPrinter"
          />

          <q-btn
            color="purple"
            label="Quick EPSON Test"
            icon="local_print_shop"
            @click="quickEpsonTest"
            :loading="testingEpson"
            :disable="!hasEpsonPrinter"
          />
        </div>

        <!-- Printer Management -->
        <div class="row q-gutter-sm q-mb-md">
          <q-btn
            color="positive"
            label="Set as Default"
            icon="bookmark"
            @click="setAsDefault"
            :disable="!selectedPrinter"
          />
          
          <q-btn
            color="secondary"
            label="Get Default"
            icon="bookmark_border"
            @click="getDefaultPrinter"
            :loading="loadingDefault"
          />

          <q-btn
            color="info"
            label="Refresh Printers"
            icon="refresh"
            @click="refreshAll"
            :loading="refreshing"
          />
        </div>

        <!-- Current Default Printer -->
        <div v-if="defaultPrinter" class="q-mb-md">
          <q-chip 
            :color="defaultPrinter.includes('EPSON') || defaultPrinter.includes('TM-T82') ? 'primary' : 'secondary'" 
            text-color="white" 
            icon="bookmark"
          >
            Default: {{ defaultPrinter }}
          </q-chip>
        </div>

        <!-- EPSON Printers Section -->
        <div v-if="epsonPrinters.length > 0" class="q-mb-md">
          <div class="text-subtitle2 q-mb-sm text-primary">
            <q-icon name="local_print_shop" class="q-mr-sm"/>
            EPSON TM-T82X Printers:
          </div>
          <q-list dense bordered class="rounded-borders">
            <q-item 
              v-for="printer in epsonPrinters" 
              :key="printer"
              :class="{ 'bg-primary text-white': printer === selectedPrinter }"
              clickable
              @click="selectedPrinter = printer"
            >
              <q-item-section avatar>
                <q-icon name="local_print_shop" color="primary" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ printer }}</q-item-label>
                <q-item-label caption class="text-green">
                  EPSON Thermal Printer - Recommended
                </q-item-label>
              </q-item-section>
              <q-item-section side>
                <div class="row q-gutter-xs">
                  <q-btn
                    flat
                    dense
                    icon="cable"
                    @click.stop="testSpecificPrinter(printer)"
                    :loading="testingConnection === printer"
                    title="Test EPSON printer"
                  />
                  <q-btn
                    flat
                    dense
                    icon="print"
                    @click.stop="quickTestPrint(printer)"
                    :loading="printing === printer"
                    title="Quick test print"
                  />
                </div>
              </q-item-section>
            </q-item>
          </q-list>
        </div>

        <!-- Discovered Devices -->
        <div v-if="discoveredDevices.length > 0" class="q-mb-md">
          <div class="text-subtitle2 q-mb-sm">Discovered Devices:</div>
          <q-list dense bordered class="rounded-borders">
            <q-item 
              v-for="device in discoveredDevices" 
              :key="device.name"
              :class="{ 'bg-blue-1': device.name === selectedPrinter }"
              clickable
              @click="selectDevice(device)"
            >
              <q-item-section avatar>
                <q-icon 
                  :name="getDeviceIcon(device)" 
                  :color="getDeviceColor(device)"
                />
              </q-item-section>
              
              <q-item-section>
                <q-item-label>{{ device.name }}</q-item-label>
                <q-item-label caption>
                  {{ device.connection_type }} - {{ device.port }}
                </q-item-label>
              </q-item-section>
              
              <q-item-section side>
                <div class="row items-center q-gutter-xs">
                  <q-chip 
                    :color="getStatusColor(device.status)" 
                    text-color="white" 
                    dense
                  >
                    {{ device.status }}
                  </q-chip>
                  
                  <q-btn
                    flat
                    dense
                    icon="cable"
                    @click.stop="testDeviceConnection(device)"
                    :loading="testingConnection === device.name"
                    title="Test connection"
                  />
                </div>
              </q-item-section>
            </q-item>
          </q-list>
        </div>

        <!-- Simple Printer List -->
        <div v-else-if="printers.length > 0 && epsonPrinters.length === 0" class="q-mb-md">
          <div class="text-subtitle2 q-mb-sm">Available Printers:</div>
          <q-list dense bordered class="rounded-borders">
            <q-item 
              v-for="printer in printers" 
              :key="printer.value"
              :class="{ 'bg-blue-1': printer.value === selectedPrinter }"
              clickable
              @click="selectedPrinter = printer.value"
            >
              <q-item-section avatar>
                <q-icon 
                  :name="printer.label.includes('EPSON') || printer.label.includes('TM-T82') ? 'local_print_shop' : 'print'" 
                  :color="printer.label.includes('EPSON') || printer.label.includes('TM-T82') ? 'primary' : 'grey'"
                />
              </q-item-section>
              
              <q-item-section>{{ printer.label }}</q-item-section>
              
              <q-item-section side>
                <q-btn
                  flat
                  dense
                  icon="info"
                  @click.stop="checkPrinterStatus(printer.value)"
                  :loading="checkingStatus === printer.value"
                />
              </q-item-section>
            </q-item>
          </q-list>
        </div>

        <!-- Status Messages -->
        <div v-if="lastTestResult" class="q-mb-md">
          <q-banner 
            :class="lastTestResult.success ? 'bg-positive' : 'bg-negative'"
            text-color="white"
            rounded
          >
            <template v-slot:avatar>
              <q-icon 
                :name="lastTestResult.success ? 'check_circle' : 'error'" 
                color="white" 
              />
            </template>
            {{ lastTestResult.message }}
            
            <template v-slot:action>
              <q-btn 
                flat 
                color="white" 
                icon="close" 
                @click="lastTestResult = null"
                dense
              />
            </template>
          </q-banner>
        </div>

        <!-- Debug Info -->
        <div v-if="debugMode" class="q-mb-md">
          <q-expansion-item
            icon="bug_report"
            label="Debug Information"
            header-class="text-grey-6"
          >
            <q-card>
              <q-card-section>
                <div class="text-caption">
                  <div><strong>Selected Printer:</strong> {{ selectedPrinter || 'None' }}</div>
                  <div><strong>Default Printer:</strong> {{ defaultPrinter || 'None' }}</div>
                  <div><strong>EPSON Printers Found:</strong> {{ epsonPrinters.length }}</div>
                  <div><strong>Total Devices:</strong> {{ discoveredDevices.length }}</div>
                  <div><strong>Test Barcode:</strong> {{ testBarcode }}</div>
                  <div><strong>Discovery In Progress:</strong> {{ discoveryInProgress ? 'Yes' : 'No' }}</div>
                  <div><strong>Cache Valid:</strong> {{ isCacheValid() ? 'Yes' : 'No' }}</div>
                  <div><strong>Cache Last Update:</strong> {{ printerCache.lastUpdate ? new Date(printerCache.lastUpdate).toLocaleTimeString() : 'Never' }}</div>
                  <div><strong>Cache Timeout:</strong> {{ printerCache.cacheTimeout / 1000 }}s</div>
                </div>
              </q-card-section>
            </q-card>
          </q-expansion-item>
        </div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn 
          flat 
          label="Debug Mode" 
          @click="debugMode = !debugMode"
          :color="debugMode ? 'primary' : 'grey'"
          size="sm"
        />
        <q-btn flat label="Close" @click="onDialogCancel"/>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useDialogPluginComponent } from 'quasar';
import { invoke } from '@tauri-apps/api/core';
import { Notify } from 'quasar';

const { dialogRef, onDialogHide, onDialogCancel } = useDialogPluginComponent();

// Reactive state
const testBarcode = ref('SPARTA-' + Date.now().toString(36).toUpperCase());
const testTarif = ref(2000);
const printing = ref(false);
const discovering = ref(false);
const loadingPrinters = ref(false);
const loadingDefault = ref(false);
const testingConnection = ref(false);
const checkingStatus = ref('');
const checkingEpson = ref(false);
const testingEpson = ref(false);
const refreshing = ref(false);
const debugMode = ref(false);

// Cache untuk printer discovery
const printerCache = ref({
  printers: [],
  discoveredDevices: [],
  epsonPrinters: [],
  lastUpdate: null,
  cacheTimeout: 30000 // 30 seconds cache
});

// Flag untuk prevent multiple concurrent discovery
const discoveryInProgress = ref(false);

const printers = ref([]);
const discoveredDevices = ref([]);
const epsonPrinters = ref([]);
const selectedPrinter = ref('');
const defaultPrinter = ref('');
const lastTestResult = ref(null);

// Computed properties
const hasEpsonPrinter = computed(() => {
  return epsonPrinters.value.length > 0 || 
         selectedPrinter.value.includes('EPSON') || 
         selectedPrinter.value.includes('TM-T82');
});

// Icons and colors
const getSelectedPrinterIcon = () => {
  if (!selectedPrinter.value) return 'print';
  return (selectedPrinter.value.includes('EPSON') || selectedPrinter.value.includes('TM-T82')) 
    ? 'local_print_shop' : 'print';
};

const getSelectedPrinterColor = () => {
  if (!selectedPrinter.value) return 'grey';
  return (selectedPrinter.value.includes('EPSON') || selectedPrinter.value.includes('TM-T82')) 
    ? 'primary' : 'secondary';
};

const getDeviceIcon = (device) => {
  if (device.connection_type === 'epson_thermal') return 'local_print_shop';
  if (device.connection_type === 'usb') return 'usb';
  if (device.connection_type === 'serial') return 'cable';
  if (device.connection_type === 'network') return 'wifi';
  return 'print';
};

const getDeviceColor = (device) => {
  if (device.connection_type === 'epson_thermal') return 'primary';
  if (device.connection_type === 'usb') return 'blue';
  if (device.connection_type === 'serial') return 'orange';
  if (device.connection_type === 'network') return 'green';
  return 'grey';
};

const getStatusColor = (status) => {
  switch (status.toLowerCase()) {
    case 'available': return 'positive';
    case 'busy': return 'warning';
    case 'offline': return 'negative';
    default: return 'grey';
  }
};

// Test print barcode with full ticket
const testPrintBarcode = async () => {
  printing.value = true;
  lastTestResult.value = null;
  
  try {
    const result = await invoke('test_print_barcode', { 
      barcodeData: testBarcode.value,
      printerName: selectedPrinter.value
    });
    
    lastTestResult.value = result;
    
    Notify.create({
      type: 'positive',
      message: result.message || 'Test print berhasil!',
      timeout: 3000
    });
  } catch (error) {
    console.error('Test print error:', error);
    
    lastTestResult.value = {
      success: false,
      message: error.toString()
    };
    
    Notify.create({
      type: 'negative',
      message: `Test print gagal: ${error}`,
      timeout: 5000
    });
  } finally {
    printing.value = false;
  }
};

// Quick test print for specific printer
const quickTestPrint = async (printerName) => {
  printing.value = printerName;
  
  try {
    const result = await invoke('test_print_barcode', { 
      barcodeData: `QUICK-TEST-${Date.now().toString(36).toUpperCase()}`,
      printerName: printerName
    });
    
    Notify.create({
      type: 'positive',
      message: `Quick test berhasil: ${result.message}`,
      timeout: 3000
    });
  } catch (error) {
    Notify.create({
      type: 'negative',
      message: `Quick test gagal: ${error}`,
      timeout: 5000
    });
  } finally {
    printing.value = false;
  }
};

// Check if cache is still valid
const isCacheValid = () => {
  if (!printerCache.value.lastUpdate) return false;
  const now = Date.now();
  return (now - printerCache.value.lastUpdate) < printerCache.value.cacheTimeout;
};

// Load data from cache
const loadFromCache = () => {
  if (isCacheValid()) {
    printers.value = [...printerCache.value.printers];
    discoveredDevices.value = [...printerCache.value.discoveredDevices];
    epsonPrinters.value = [...printerCache.value.epsonPrinters];
    console.log('📦 Loaded printer data from cache');
    return true;
  }
  return false;
};

// Save data to cache
const saveToCache = () => {
  printerCache.value = {
    printers: [...printers.value],
    discoveredDevices: [...discoveredDevices.value],
    epsonPrinters: [...epsonPrinters.value],
    lastUpdate: Date.now(),
    cacheTimeout: 30000
  };
  console.log('💾 Saved printer data to cache');
};

// Prevent concurrent discovery dengan timeout fallback
const withConcurrencyControl = async (operation, timeoutMs = 10000) => {
  if (discoveryInProgress.value) {
    console.log('⚠️ Discovery already in progress, waiting...');
    
    // Wait for current operation to complete atau timeout
    const startTime = Date.now();
    while (discoveryInProgress.value && (Date.now() - startTime) < timeoutMs) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    if (discoveryInProgress.value) {
      console.error('❌ Discovery timed out, forcing reset');
      discoveryInProgress.value = false;
      throw new Error('Discovery operation timed out');
    }
    
    // If operation completed during wait, try loading from cache
    if (loadFromCache()) {
      return;
    }
  }
  
  discoveryInProgress.value = true;
  try {
    await operation();
    saveToCache();
  } finally {
    discoveryInProgress.value = false;
  }
};

// Test printer connection
const testConnection = async () => {
  testingConnection.value = true;
  lastTestResult.value = null;
  
  try {
    const result = await invoke('test_printer_connection', { 
      printerIdentifier: selectedPrinter.value 
    });
    
    lastTestResult.value = result;
    
    Notify.create({
      type: 'positive',
      message: result.message,
      timeout: 3000
    });
  } catch (error) {
    console.error('Test connection error:', error);
    
    lastTestResult.value = {
      success: false,
      message: error.toString()
    };
    
    Notify.create({
      type: 'negative',
      message: `Test connection gagal: ${error}`,
      timeout: 5000
    });
  } finally {
    testingConnection.value = false;
  }
};

// Test specific printer connection
const testSpecificPrinter = async (printerName) => {
  testingConnection.value = printerName;
  
  try {
    const result = await invoke('test_printer_connection', { 
      printerIdentifier: printerName 
    });
    
    Notify.create({
      type: 'positive',
      message: `${printerName}: ${result.message}`,
      timeout: 3000
    });
  } catch (error) {
    Notify.create({
      type: 'negative',
      message: `${printerName}: ${error}`,
      timeout: 5000
    });
  } finally {
    testingConnection.value = false;
  }
};

// Test device connection (for discovered devices)
const testDeviceConnection = async (device) => {
  testingConnection.value = device.name;
  
  try {
    const result = await invoke('test_printer_connection', { 
      printerIdentifier: device.port || device.name 
    });
    
    Notify.create({
      type: 'positive',
      message: `${device.name}: ${result.message}`,
      timeout: 3000
    });
  } catch (error) {
    console.error('Test device connection error:', error);
    Notify.create({
      type: 'negative',
      message: `${device.name}: ${error}`,
      timeout: 5000
    });
  } finally {
    testingConnection.value = false;
  }
};

// Quick EPSON test
const quickEpsonTest = async () => {
  testingEpson.value = true;
  
  try {
    // Find first EPSON printer
    const epsonPrinter = epsonPrinters.value[0] || 
                        printers.value.find(p => p.label.includes('EPSON') || p.label.includes('TM-T82'))?.value;
    
    if (!epsonPrinter) {
      throw new Error('No EPSON printer found');
    }
    
    const result = await invoke('test_printer_connection', { 
      printerIdentifier: epsonPrinter 
    });
    
    Notify.create({
      type: 'positive',
      message: `EPSON Test OK: ${result.message}`,
      timeout: 3000
    });
  } catch (error) {
    Notify.create({
      type: 'negative',
      message: `EPSON Test Failed: ${error}`,
      timeout: 5000
    });
  } finally {
    testingEpson.value = false;
  }
};

// Discover thermal printers (full device info)
const discoverPrinters = async () => {
  // Check cache first
  if (loadFromCache()) {
    console.log('📦 Using cached printer data');
    
    Notify.create({
      type: 'positive',
      message: `Menggunakan data cache: ${discoveredDevices.value.length} device`,
      timeout: 2000
    });
    return;
  }
  
  await withConcurrencyControl(async () => {
    discovering.value = true;
    
    try {
      console.log('🔍 Starting printer discovery...');
      
      // Import recovery utilities
      const { startMonitoring, stopMonitoring } = await import('src/utils/printer-recovery');
      
      // Start monitoring
      startMonitoring('printer_discovery');
      
      // Add timeout untuk discovery dengan fallback
      const devices = await Promise.race([
        invoke('discover_thermal_printers'),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Discovery timeout after 8 seconds')), 8000)
        )
      ]);
      
      // Stop monitoring on success
      stopMonitoring();
      
      discoveredDevices.value = devices;
      
      // Also update simple printers list
      printers.value = devices.map(device => ({
        label: device.name,
        value: device.name
      }));
      
      console.log('✅ Discovery completed:', devices.length, 'devices found');
      
      Notify.create({
        type: 'positive',
        message: `Ditemukan ${devices.length} device`,
        timeout: 3000
      });
    } catch (error) {
      console.error('❌ Discover printers error:', error);
      
      // Stop monitoring on error
      try {
        const { stopMonitoring } = await import('src/utils/printer-recovery');
        stopMonitoring();
      } catch (recoveryError) {
        console.warn('Recovery utility import failed:', recoveryError);
      }
      
      // Fallback: provide manual entry option
      const fallbackDevices = [{
        name: "Manual Entry",
        connection_type: "manual",
        port: "manual",
        status: "available"
      }];
      
      discoveredDevices.value = fallbackDevices;
      printers.value = fallbackDevices.map(device => ({
        label: device.name,
        value: device.name
      }));
      
      Notify.create({
        type: 'warning',
        message: `Discovery gagal: ${error.message || error}. Menggunakan fallback.`,
        timeout: 5000
      });
    } finally {
      discovering.value = false;
    }
  });
};

// List thermal printers (simple names)
const listThermalPrinters = async () => {
  // Check cache first
  if (loadFromCache() && printers.value.length > 0) {
    console.log('📦 Using cached thermal printer list');
    
    Notify.create({
      type: 'positive',
      message: `Menggunakan data cache: ${printers.value.length} printer`,
      timeout: 2000
    });
    return;
  }
  
  await withConcurrencyControl(async () => {
    loadingPrinters.value = true;
    
    try {
      console.log('📝 Starting thermal printer list...');
      
      // Add timeout untuk list printers
      const result = await Promise.race([
        invoke('list_thermal_printers'),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('List timeout after 6 seconds')), 6000)
        )
      ]);
      
      printers.value = result.map(printer => ({
        label: printer,
        value: printer
      }));
      
      // Clear discovered devices when using simple list
      discoveredDevices.value = [];
      
      console.log('✅ Thermal printer list completed:', result.length, 'printers found');
      
      Notify.create({
        type: 'positive',
        message: `Ditemukan ${result.length} printer`,
        timeout: 3000
      });
    } catch (error) {
      console.error('❌ List printers error:', error);
      
      // Fallback: provide manual entry option
      const fallbackPrinters = [
        { label: 'Manual Entry', value: 'Manual Entry' },
        { label: 'EPSON TM-T82X', value: 'EPSON TM-T82X' }
      ];
      
      printers.value = fallbackPrinters;
      
      Notify.create({
        type: 'warning',
        message: `List printer gagal: ${error.message || error}. Menggunakan fallback.`,
        timeout: 5000
      });
    } finally {
      loadingPrinters.value = false;
    }
  });
};

// Check EPSON printers specifically
const checkEpsonPrinters = async () => {
  // Check cache first untuk EPSON printers
  if (loadFromCache() && epsonPrinters.value.length > 0) {
    console.log('📦 Using cached EPSON printer data');
    
    Notify.create({
      type: 'positive',
      message: `Cache: ${epsonPrinters.value.length} EPSON printer`,
      timeout: 2000
    });
    return;
  }
  
  await withConcurrencyControl(async () => {
    checkingEpson.value = true;
    
    try {
      console.log('🖨️ Starting EPSON printer check...');
      
      // Add timeout untuk EPSON check
      const result = await Promise.race([
        invoke('check_epson_printers'),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('EPSON check timeout after 5 seconds')), 5000)
        )
      ]);
      
      epsonPrinters.value = result.filter(name => !name.includes('No EPSON'));
      
      if (epsonPrinters.value.length > 0) {
        console.log('✅ EPSON check completed:', epsonPrinters.value.length, 'EPSON printers found');
        
        Notify.create({
          type: 'positive',
          message: `Ditemukan ${epsonPrinters.value.length} EPSON printer`,
          timeout: 3000
        });
        
        // Auto-select first EPSON printer if none selected
        if (!selectedPrinter.value) {
          selectedPrinter.value = epsonPrinters.value[0];
        }
      } else {
        console.log('⚠️ No EPSON printers found');
        Notify.create({
          type: 'warning',
          message: 'Tidak ada EPSON TM-T82X yang ditemukan',
          timeout: 3000
        });
      }
    } catch (error) {
      console.error('❌ Check EPSON printers error:', error);
      
      // Fallback: assume there might be EPSON printer
      epsonPrinters.value = ['EPSON TM-T82X (Fallback)'];
      
      Notify.create({
        type: 'warning',
        message: `EPSON check gagal: ${error.message || error}. Menggunakan fallback.`,
        timeout: 5000
      });
    } finally {
      checkingEpson.value = false;
    }
  });
};

// Get default printer
const getDefaultPrinter = async () => {
  loadingDefault.value = true;
  try {
    const result = await invoke('get_default_printer');
    defaultPrinter.value = result;
    if (!selectedPrinter.value) {
      selectedPrinter.value = result;
    }
    
    Notify.create({
      type: 'info',
      message: `Default printer: ${result}`,
      timeout: 2000
    });
  } catch (error) {
    console.log('No default printer set');
    Notify.create({
      type: 'warning',
      message: 'Tidak ada default printer yang diset'
    });
  } finally {
    loadingDefault.value = false;
  }
};

// Set default printer
const setAsDefault = async () => {
  try {
    const result = await invoke('set_default_printer', { 
      printerName: selectedPrinter.value 
    });
    
    defaultPrinter.value = selectedPrinter.value;
    
    Notify.create({
      type: 'positive',
      message: result.message || 'Printer default berhasil diset!'
    });
  } catch (error) {
    console.error('Set default printer error:', error);
    Notify.create({
      type: 'negative',
      message: `Gagal set default printer: ${error}`
    });
  }
};

// Check printer status
const checkPrinterStatus = async (printerName) => {
  checkingStatus.value = printerName;
  try {
    const result = await invoke('get_printer_status', { 
      printerName 
    });
    
    Notify.create({
      type: 'positive',
      message: result,
      timeout: 3000
    });
  } catch (error) {
    console.error('Printer status error:', error);
    Notify.create({
      type: 'negative',
      message: `Status printer: ${error}`
    });
  } finally {
    checkingStatus.value = '';
  }
};

// Check selected printer status
const checkSelectedPrinterStatus = async () => {
  if (selectedPrinter.value) {
    await checkPrinterStatus(selectedPrinter.value);
  }
};

// Select device from discovered list
const selectDevice = (device) => {
  selectedPrinter.value = device.name;
  onPrinterSelected(device.name);
};

// Generate random barcode for testing
const generateRandomBarcode = () => {
  const timestamp = Date.now().toString(36).toUpperCase();
  const random = Math.random().toString(36).substring(2, 7).toUpperCase();
  testBarcode.value = `SPARTA-${timestamp}-${random}`;
};

// Refresh all printer lists
const refreshAll = async () => {
  refreshing.value = true;
  try {
    // Clear cache first
    printerCache.value = {
      printers: [],
      discoveredDevices: [],
      epsonPrinters: [],
      lastUpdate: null,
      cacheTimeout: 30000
    };
    
    await Promise.all([
      discoverPrinters(),
      checkEpsonPrinters(),
      getDefaultPrinter()
    ]);
    
    Notify.create({
      type: 'positive',
      message: 'Semua printer list berhasil di-refresh',
      timeout: 2000
    });
  } catch (error) {
    Notify.create({
      type: 'negative',
      message: `Error refresh: ${error}`
    });
  } finally {
    refreshing.value = false;
  }
};

// Clear cache dan refresh semua data
const clearCacheAndRefresh = async () => {
  try {
    console.log('🧹 Clearing cache and refreshing...');
    
    // Reset cache
    printerCache.value = {
      printers: [],
      discoveredDevices: [],
      epsonPrinters: [],
      lastUpdate: null,
      cacheTimeout: 30000
    };
    
    // Reset local state
    printers.value = [];
    discoveredDevices.value = [];
    epsonPrinters.value = [];
    selectedPrinter.value = '';
    lastTestResult.value = null;
    
    // Force discovery flag reset
    discoveryInProgress.value = false;
    
    Notify.create({
      type: 'info',
      message: 'Cache cleared, starting fresh discovery...',
      timeout: 2000
    });
    
    // Refresh all data
    await refreshAll();
    
  } catch (error) {
    console.error('❌ Error clearing cache:', error);
    Notify.create({
      type: 'negative',
      message: `Error clearing cache: ${error}`
    });
  }
};

// Emergency reset untuk recovery dari stuck state
const emergencyReset = async () => {
  try {
    console.log('🚨 Emergency reset triggered');
    
    // Import recovery utilities
    const { forceStopPrinterOperations, resetRecoveryState } = await import('src/utils/printer-recovery');
    
    // Stop all ongoing operations
    discovering.value = false;
    loadingPrinters.value = false;
    checkingEpson.value = false;
    testingConnection.value = false;
    printing.value = false;
    checkingStatus.value = '';
    testingEpson.value = false;
    refreshing.value = false;
    
    // Use recovery utility
    await forceStopPrinterOperations();
    
    // Reset discovery flag
    discoveryInProgress.value = false;
    
    // Clear all data
    printers.value = [];
    discoveredDevices.value = [];
    epsonPrinters.value = [];
    selectedPrinter.value = '';
    defaultPrinter.value = '';
    lastTestResult.value = null;
    
    // Reset cache
    printerCache.value = {
      printers: [],
      discoveredDevices: [],
      epsonPrinters: [],
      lastUpdate: null,
      cacheTimeout: 30000
    };
    
    // Reset backend operations
    try {
      await invoke('reset_printer_operations');
      console.log('✅ Backend operations reset');
    } catch (error) {
      console.warn('❌ Backend reset failed:', error);
    }
    
    // Reset recovery state
    resetRecoveryState();
    
    Notify.create({
      type: 'warning',
      message: 'Emergency reset completed. Ready untuk discovery ulang.',
      timeout: 3000
    });
    
  } catch (error) {
    console.error('❌ Error during emergency reset:', error);
    Notify.create({
      type: 'negative',
      message: `Emergency reset error: ${error}`
    });
  }
};

// Printer selection handler
const onPrinterSelected = (printerName) => {
  console.log('Selected printer:', printerName);
  lastTestResult.value = null; // Clear previous test results
};

// Initialize component
onMounted(async () => {
  console.log('🚀 PrinterTestDialog mounting...');
  
  try {
    // Check if cache is available
    if (loadFromCache()) {
      console.log('📦 Loaded from cache, skipping initial discovery');
      
      // Just get default printer since we have cached data
      await getDefaultPrinter();
      
      Notify.create({
        type: 'info',
        message: 'Menggunakan data cache. Klik refresh untuk update.',
        timeout: 3000
      });
      
      return;
    }
    
    // No cache available, start discovery
    console.log('🔍 No cache, starting initial discovery...');
    
    // Start with checking EPSON printers first (fastest usually)
    await checkEpsonPrinters();
    
    // Then discover all printers in background
    if (!discoveryInProgress.value) {
      discoverPrinters().catch(error => {
        console.error('Background discovery failed:', error);
      });
    }
    
    // Get default printer
    await getDefaultPrinter();
    
  } catch (error) {
    console.error('❌ Error during component initialization:', error);
    
    // Emergency fallback
    emergencyReset();
    
    Notify.create({
      type: 'negative',
      message: 'Gagal inisialisasi. Gunakan Emergency Reset jika diperlukan.',
      timeout: 5000
    });
  }
  
  console.log('✅ PrinterTestDialog mounting completed');
});
</script>

<style scoped>
.q-banner {
  border-radius: 8px;
}

.q-chip {
  font-size: 0.75rem;
}

.q-item {
  border-radius: 4px;
  margin-bottom: 2px;
}

.q-item:last-child {
  margin-bottom: 0;
}

.q-expansion-item {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}
</style>