import { defineStore } from 'pinia';
import { ref } from 'vue';
import PouchDB from 'pouchdb';
import { useSettingsService } from './settings-service';

export const useTransaksiStore = defineStore('transaksi', () => {
  const db = new PouchDB('transaksi');
  const settingsService = useSettingsService();
  
  const totalVehicleIn = ref(0);
  const totalVehicleOut = ref(0);
  const totalVehicleInside = ref(0);
  const gateStatuses = ref<Record<string, boolean>>({});

  const getCountVehicleInToday = async () => {
    try {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      const result = await db.query('transaksi/by_date', {
        startkey: today.toISOString(),
        endkey: new Date().toISOString(),
        reduce: true
      });
      
      totalVehicleIn.value = result.rows[0]?.value || 0;
    } catch (error) {
      console.error('Error getting vehicle in count:', error);
      totalVehicleIn.value = 0;
    }
  };

  const getCountVehicleOutToday = async () => {
    try {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      const result = await db.query('transaksi/out_by_date', {
        startkey: today.toISOString(),
        endkey: new Date().toISOString(),
        reduce: true
      });
      
      totalVehicleOut.value = result.rows[0]?.value || 0;
    } catch (error) {
      console.error('Error getting vehicle out count:', error);
      totalVehicleOut.value = 0;
    }
  };

  const getCountVehicleInside = async () => {
    try {
      totalVehicleInside.value = totalVehicleIn.value - totalVehicleOut.value;
    } catch (error) {
      console.error('Error calculating vehicles inside:', error);
      totalVehicleInside.value = 0;
    }
  };

  const setManualOpenGate = async (gateId: string) => {
    try {
      const gate = await settingsService.getGateById(gateId);
      if (!gate) throw new Error('Gate not found');

      // Record the manual gate opening
      await db.post({
        type: 'manual_open',
        gateId,
        timestamp: new Date().toISOString(),
        userId: 'manual' // You might want to get this from your auth store
      });

      gateStatuses.value[gateId] = true;
      
      // Auto close after 5 seconds
      setTimeout(() => {
        gateStatuses.value[gateId] = false;
      }, 5000);

      return true;
    } catch (error) {
      console.error('Error opening gate:', error);
      return false;
    }
  };

  // Initialize design documents for queries
  const initializeDesignDocs = async () => {
    const designDoc = {
      _id: '_design/transaksi',
      views: {
        by_date: {
          map: function (doc: any) {
            if (doc.type === 'entry') {
              emit(doc.timestamp, 1);
            }
          }.toString(),
          reduce: '_count'
        },
        out_by_date: {
          map: function (doc: any) {
            if (doc.type === 'exit') {
              emit(doc.timestamp, 1);
            }
          }.toString(),
          reduce: '_count'
        }
      }
    };

    try {
      await db.put(designDoc);
    } catch (err: any) {
      if (err.name !== 'conflict') {
        console.error('Error creating design document:', err);
      }
    }
  };

  // Initialize the store
  initializeDesignDocs();

  return {
    totalVehicleIn,
    totalVehicleOut,
    totalVehicleInside,
    gateStatuses,
    getCountVehicleInToday,
    getCountVehicleOutToday,
    getCountVehicleInside,
    setManualOpenGate
  };
});
