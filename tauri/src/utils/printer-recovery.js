// Printer Recovery Utilities
// Digunakan untuk recovery dari masalah printer discovery dan test print

import { ref } from 'vue';
import { Notify } from 'quasar';

// Global state untuk recovery
export const printerRecoveryState = ref({
  discoveryInProgress: false,
  lastRecoveryTime: null,
  recoveryCount: 0,
  maxRecoveryAttempts: 3
});

// Check apakah sistem perlu recovery
export const needsRecovery = () => {
  const now = Date.now();
  const lastRecovery = printerRecoveryState.value.lastRecoveryTime;
  
  // Jika discovery sudah berjalan lebih dari 15 detik, consider as stuck
  if (printerRecoveryState.value.discoveryInProgress && lastRecovery) {
    return (now - lastRecovery) > 15000;
  }
  
  return false;
};

// Force stop semua printer operations
export const forceStopPrinterOperations = async () => {
  console.log('🛑 Force stopping all printer operations...');
  
  // Reset global state
  printerRecoveryState.value.discoveryInProgress = false;
  
  // Call Tauri backend to cancel any ongoing operations
  try {
    const { invoke } = await import('@tauri-apps/api/core');
    await invoke('cancel_printer_operations');
    console.log('✅ Backend operations cancelled successfully');
  } catch (error) {
    console.warn('❌ Backend cancellation failed:', error);
  }
  
  const { Notify } = await import('quasar');
  Notify.create({
    type: 'warning',
    message: 'All printer operations force stopped',
    timeout: 2000
  });
};

// Diagnostic check untuk printer system
export const diagnosticCheck = async () => {
  const results = {
    systemTime: new Date().toISOString(),
    recoveryState: { ...printerRecoveryState.value },
    needsRecovery: needsRecovery(),
    recommendations: []
  };
  
  // Check recovery count
  if (printerRecoveryState.value.recoveryCount > 2) {
    results.recommendations.push('Too many recovery attempts. Restart application.');
  }
  
  // Check stuck discovery
  if (needsRecovery()) {
    results.recommendations.push('Discovery appears stuck. Force stop recommended.');
  }
  
  // Check system resources (if available)
  try {
    // Bisa ditambahkan check system resources jika diperlukan
    results.recommendations.push('System diagnostics completed.');
  } catch (error) {
    results.recommendations.push('System diagnostic failed.');
  }
  
  return results;
};

// Auto recovery mechanism
export const autoRecovery = async () => {
  console.log('🔄 Starting auto recovery...');
  
  const maxAttempts = printerRecoveryState.value.maxRecoveryAttempts;
  
  if (printerRecoveryState.value.recoveryCount >= maxAttempts) {
    const { Notify } = await import('quasar');
    Notify.create({
      type: 'negative',
      message: `Max recovery attempts (${maxAttempts}) reached. Please restart application.`,
      timeout: 5000
    });
    return false;
  }
  
  try {
    // Increment recovery count
    printerRecoveryState.value.recoveryCount++;
    printerRecoveryState.value.lastRecoveryTime = Date.now();
    
    // Force stop operations
    await forceStopPrinterOperations();
    
    // Reset backend state
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      await invoke('reset_printer_operations');
      console.log('✅ Backend state reset successfully');
    } catch (error) {
      console.warn('❌ Backend reset failed:', error);
    }
    
    // Wait a bit for cleanup
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const { Notify } = await import('quasar');
    Notify.create({
      type: 'positive',
      message: `Auto recovery completed (attempt ${printerRecoveryState.value.recoveryCount}/${maxAttempts})`,
      timeout: 3000
    });
    
    return true;
    
  } catch (error) {
    console.error('❌ Auto recovery failed:', error);
    
    const { Notify } = await import('quasar');
    Notify.create({
      type: 'negative',
      message: `Auto recovery failed: ${error.message}`,
      timeout: 5000
    });
    
    return false;
  }
};

// Reset recovery state (call after successful operation)
export const resetRecoveryState = () => {
  printerRecoveryState.value = {
    discoveryInProgress: false,
    lastRecoveryTime: null,
    recoveryCount: 0,
    maxRecoveryAttempts: 3
  };
  console.log('✅ Recovery state reset');
};

// Monitor printer operations (call this when starting discovery)
export const startMonitoring = (operationType = 'discovery') => {
  printerRecoveryState.value.discoveryInProgress = true;
  printerRecoveryState.value.lastRecoveryTime = Date.now();
  
  console.log(`📊 Started monitoring ${operationType} operation`);
  
  // Auto recovery after timeout
  setTimeout(() => {
    if (needsRecovery()) {
      console.warn('⚠️ Operation appears stuck, triggering auto recovery');
      autoRecovery();
    }
  }, 20000); // 20 second timeout
};

// Stop monitoring (call when operation completes)
export const stopMonitoring = () => {
  printerRecoveryState.value.discoveryInProgress = false;
  console.log('📊 Stopped monitoring printer operation');
};

// Export default utilities object
export default {
  needsRecovery,
  forceStopPrinterOperations,
  diagnosticCheck,
  autoRecovery,
  resetRecoveryState,
  startMonitoring,
  stopMonitoring,
  printerRecoveryState
};
