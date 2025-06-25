import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useQuasar } from 'quasar';
import ls from 'localstorage-slim';
import { api } from 'src/boot/axios';
import { useSettingsService } from './settings-service';
import { useTarifStore } from './tarif-store';
import { localDbs } from 'src/boot/pouchdb';

// Interface untuk transaksi parkir berdasarkan parkir_awal.sql
export interface TransaksiParkir {
  id: string;
  no_pol: string;
  id_kendaraan: number;
  status: number; // 0 = masuk, 1 = keluar
  id_pintu_masuk: string;
  id_pintu_keluar?: string;
  waktu_masuk: string;
  waktu_keluar?: string;
  id_op_masuk: string;
  id_op_keluar?: string;
  id_shift_masuk: string;
  id_shift_keluar?: string;
  kategori: string;
  status_transaksi: string; // '0' = normal, '32' = void, '-1' = cancel
  bayar_masuk?: number;
  bayar_keluar?: number;
  jenis_system: string;
  tanggal: string;
  pic_driver_masuk?: string;
  pic_driver_keluar?: string;
  pic_no_pol_masuk?: string;
  pic_no_pol_keluar?: string;
  sinkron: number;
  adm?: string;
  alasan?: string;
  pmlogin?: string;
  pklogin?: string;
  upload: number;
  manual: number;
  veri_kode?: string;
  veri_check?: number;
  veri_adm?: string;
  veri_date?: string;
  denda?: number;
  extra_bayar?: number;
  no_barcode?: string;
  jenis_langganan?: string;
  post_pay?: number;
  reff_kode?: string;
}

// Interface untuk customer/member
export interface Customer {
  id?: number;
  nama: string;
  alamat?: string;
  no_pol: string;
  id_jenis_kendaraan: number;
  jenis_kendaraan: string;
  akhir?: string; // tanggal berakhir membership
  status?: string;
}

// Interface untuk jenis kendaraan
export interface JenisKendaraan {
  id: number;
  label: string;
  shortcut?: string; // shortcut keyboard untuk jenis kendaraan
  tarif?: number;
  interval?: number;
  waktu_tarif?: number;
}

// Interface untuk pegawai/operator
export interface Pegawai {
  id: string;
  nama: string;
  username?: string;
  level?: string;
}

// Interface untuk shift
export interface Shift {
  id: string;
  nama: string;
  jam_mulai?: string;
  jam_selesai?: string;
}

// Interface untuk lokasi pos
export interface LokasiPos {
  value: string;
  label: string;
}

export const useTransaksiStore = defineStore('transaksi', () => {
  const $q = useQuasar();
  const db = localDbs.transactions;
  const settingsService = useSettingsService();
  const tarifStore = useTarifStore();
  
  // State variables
  const platNomor = ref<string>('');
  const selectedJenisKendaraan = ref<JenisKendaraan | null>(null);
  const jenisKendaraan = ref<JenisKendaraan[]>([]); // untuk menyimpan daftar jenis kendaraan
  const dataCustomer = ref<Customer | null>(null);
  const isCheckedIn = ref<boolean>(false);
  const isMemberExpired = ref<boolean>(false);
  
  // Payment data
  const biayaParkir = ref<number>(0);
  const bayar = ref<number>(0);
  
  // Transaction data
  const currentTransaction = ref<TransaksiParkir | null>(null);
  const transactionHistory = ref<TransaksiParkir[]>([]);
  
  // Images
  const pic_body_masuk = ref<string>('');
  const pic_body_keluar = ref<string>('');
  const pic_plat_masuk = ref<string>('');
  const pic_plat_keluar = ref<string>('');
  
  // Statistics
  const vehicleInToday = ref(0);
  const totalVehicleOut = ref(0);
  const totalVehicleInside = ref(0);
  const gateStatuses = ref<Record<string, boolean>>({});
  
  // Configuration
  const API_URL = ref<string>(ls.get('API_URL') || '');
  const lokasiPos = ref<LokasiPos>(ls.get('lokasiPos') || { value: '', label: '' });

  // Computed properties
  const isAdmin = computed(() => ls.get('isAdmin') || false);
  const pegawai = computed((): Pegawai => ls.get('pegawai') || { id: 'SYSTEM', nama: 'System' });
  const shift = computed((): string => ls.get('shift') || 'SHIFT1');

  // Methods
  const generateTransactionId = (): string => {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    return `${timestamp}${random}`;
  };

  const getCurrentDateTime = (): string => {
    return new Date().toISOString();
  };

  const getCustomerByNopol = async (): Promise<void> => {
    try {
      if (!platNomor.value) {
        throw new Error('Plat nomor tidak boleh kosong');
      }

      // Check if API_URL is configured
      if (!API_URL.value || API_URL.value === '-') {
        console.warn('API URL not configured, using local data only');
        dataCustomer.value = null;
        return;
      }

      const response = await api.get(`/customer/by-nopol/${platNomor.value}`);
      
      if (response.data && response.data.data) {
        dataCustomer.value = response.data.data;
        
        // Check if membership is expired
        if (dataCustomer.value?.akhir) {
          const expiryDate = new Date(dataCustomer.value.akhir);
          const today = new Date();
          isMemberExpired.value = expiryDate < today;
        }
      } else {
        dataCustomer.value = null;
      }
    } catch (error) {
      console.error('Error fetching customer:', error);
      dataCustomer.value = null;
      
      $q.notify({
        type: 'warning',
        message: 'Data customer tidak ditemukan atau terjadi kesalahan koneksi',
        position: 'top'
      });
    }
  };

  const getEntryTarif = (): number => {
    if (!selectedJenisKendaraan.value) {
      console.warn('No vehicle type selected for tariff calculation');
      return 0;
    }
    
    // For now, use basic tariff from selected vehicle type
    // In production, this should query the tarif store for prepaid or regular tariffs
    const basicTarif = selectedJenisKendaraan.value.tarif || 0;
    
    console.log('Basic entry tariff for vehicle:', selectedJenisKendaraan.value, 'tariff:', basicTarif);
    
    // Update biayaParkir untuk display
    biayaParkir.value = basicTarif;
    
    return basicTarif;
  };

  const getJenisKendaraan = async (): Promise<JenisKendaraan[]> => {
    try {
      // Return static data with shortcuts based on database structure
      // This matches the jenis_mobil table structure from parkir_awal.sql
      const data = [
        {
          id: 1,
          label: 'Mobil',
          shortcut: 'A',
          tarif: 5000,
          interval: 1,
          waktu_tarif: 60
        },
        {
          id: 2,
          label: 'Motor',
          shortcut: 'C',
          tarif: 2000,
          interval: 1,
          waktu_tarif: 60
        },
        {
          id: 3,
          label: 'Truck/Box',
          shortcut: 'D',
          tarif: 10000,
          interval: 1,
          waktu_tarif: 60
        }
      ];
      
      jenisKendaraan.value = data; // simpan ke state
      return data;
    } catch (error) {
      console.error('Error getting jenis kendaraan:', error);
      return [];
    }
  };

  const createEntryTransaction = async (isPrepaidMode: boolean = false): Promise<TransaksiParkir> => {
    // Dapatkan tarif entry berdasarkan mode pembayaran
    const entryFee = isPrepaidMode ? getEntryTarif() : 0;
    
    const transaction: TransaksiParkir = {
      id: generateTransactionId(),
      no_pol: platNomor.value.toUpperCase(),
      id_kendaraan: selectedJenisKendaraan.value?.id || 1,
      status: 0, // 0 = entry
      id_pintu_masuk: lokasiPos.value.value || '01',
      waktu_masuk: getCurrentDateTime(),
      id_op_masuk: pegawai.value?.id || 'SYSTEM',
      id_shift_masuk: shift.value || 'SHIFT1',
      kategori: dataCustomer.value ? 'MEMBER' : 'UMUM',
      status_transaksi: '0', // Normal transaction
      jenis_system: isPrepaidMode ? 'PREPAID' : 'MANLESS',
      tanggal: new Date().toISOString().split('T')[0],
      pic_driver_masuk: pic_body_masuk.value,
      pic_no_pol_masuk: pic_plat_masuk.value,
      sinkron: 0,
      upload: 0,
      manual: 0,
      veri_check: 0,
      bayar_masuk: entryFee // Bayar di depan untuk prepaid mode
    };

    currentTransaction.value = transaction;
    isCheckedIn.value = true;
    
    return transaction;
  };

  const createExitTransaction = async (): Promise<TransaksiParkir> => {
    if (!currentTransaction.value) {
      throw new Error('Tidak ada transaksi masuk yang ditemukan');
    }

    const exitTransaction: TransaksiParkir = {
      ...currentTransaction.value,
      status: 1, // 1 = exit
      id_pintu_keluar: lokasiPos.value.value || '01',
      waktu_keluar: getCurrentDateTime(),
      id_op_keluar: pegawai.value?.id || 'SYSTEM',
      id_shift_keluar: shift.value || 'SHIFT1',
      pic_driver_keluar: pic_body_keluar.value,
      pic_no_pol_keluar: pic_plat_keluar.value,
      bayar_keluar: calculateParkingFee()
    };

    return exitTransaction;
  };

  const calculateParkingFee = (): number => {
    if (!currentTransaction.value || !selectedJenisKendaraan.value) {
      return 0;
    }

    const entryTime = new Date(currentTransaction.value.waktu_masuk);
    const exitTime = new Date();
    const durationMs = exitTime.getTime() - entryTime.getTime();
    const durationHours = Math.ceil(durationMs / (1000 * 60 * 60));

    // Basic calculation - can be enhanced based on tariff rules
    const hourlyRate = selectedJenisKendaraan.value.tarif || 5000;
    return durationHours * hourlyRate;
  };

  const saveTransactionToLocal = async (transaction: TransaksiParkir): Promise<void> => {
    try {
      // Save to PouchDB using the internal db instance
      const response = await db.post({
        ...transaction,
        _id: `transaction_${transaction.id}`,
        type: 'parking_transaction'
      });

      console.log('Transaction saved locally:', response);
    } catch (error) {
      console.error('Error saving transaction locally:', error);
      throw error;
    }
  };

  const saveTransactionToServer = async (transaction: TransaksiParkir): Promise<void> => {
    try {
      if (!API_URL.value || API_URL.value === '-') {
        console.warn('API URL not configured, skipping server save');
        return;
      }

      const response = await api.post('/transactions/parking', transaction);
      console.log('Transaction saved to server:', response.data);
    } catch (error) {
      console.error('Error saving transaction to server:', error);
      // Don't throw error here, allow local save to succeed
    }
  };

  const processEntryTransaction = async (isPrepaidMode: boolean = false): Promise<void> => {
    try {
      const transaction = await createEntryTransaction(isPrepaidMode);
      
      // Save locally first
      await saveTransactionToLocal(transaction);
      
      // Try to save to server
      await saveTransactionToServer(transaction);
      
      // Add to history
      transactionHistory.value.unshift(transaction);
      
      const message = isPrepaidMode 
        ? 'Transaksi prepaid berhasil disimpan' 
        : 'Transaksi masuk berhasil disimpan';
      
      $q.notify({
        type: 'positive',
        message: message,
        position: 'top'
      });
    } catch (error) {
      console.error('Error processing entry transaction:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal menyimpan transaksi masuk',
        position: 'top'
      });
    }
  };

  const processExitTransaction = async (): Promise<void> => {
    try {
      const transaction = await createExitTransaction();
      
      // Save locally first
      await saveTransactionToLocal(transaction);
      
      // Try to save to server
      await saveTransactionToServer(transaction);
      
      // Update history
      const existingIndex = transactionHistory.value.findIndex(t => t.id === transaction.id);
      if (existingIndex >= 0) {
        transactionHistory.value[existingIndex] = transaction;
      } else {
        transactionHistory.value.unshift(transaction);
      }
      
      // Reset transaction state
      resetTransactionState();
      
      $q.notify({
        type: 'positive',
        message: 'Transaksi keluar berhasil disimpan',
        position: 'top'
      });
    } catch (error) {
      console.error('Error processing exit transaction:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal menyimpan transaksi keluar',
        position: 'top'
      });
    }
  };

  const resetTransactionState = (): void => {
    platNomor.value = '';
    selectedJenisKendaraan.value = null;
    dataCustomer.value = null;
    isCheckedIn.value = false;
    isMemberExpired.value = false;
    biayaParkir.value = 0;
    bayar.value = 0;
    currentTransaction.value = null;
    pic_body_masuk.value = '';
    pic_body_keluar.value = '';
    pic_plat_masuk.value = '';
    pic_plat_keluar.value = '';
  };

  // Statistics methods
  const getCountVehicleInToday = async (): Promise<void> => {
    try {
      if (API_URL.value && API_URL.value !== '-') {
        const response = await api.get('/statistics/vehicle-in-today');
        vehicleInToday.value = response.data?.count || 0;
      } else {
        // Local count from PouchDB
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        const result = await db.query('transaksi/by_date', {
          startkey: today.toISOString(),
          endkey: new Date().toISOString(),
          reduce: true
        });
        
        vehicleInToday.value = result.rows[0]?.value || 0;
      }
    } catch (error) {
      console.error('Error fetching vehicle in count:', error);
      vehicleInToday.value = 0;
    }
  };

  const getCountVehicleOutToday = async (): Promise<void> => {
    try {
      if (API_URL.value && API_URL.value !== '-') {
        const response = await api.get('/statistics/vehicle-out-today');
        totalVehicleOut.value = response.data?.count || 0;
      } else {
        // Local count from PouchDB
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        const result = await db.query('transaksi/out_by_date', {
          startkey: today.toISOString(),
          endkey: new Date().toISOString(),
          reduce: true
        });
        
        totalVehicleOut.value = result.rows[0]?.value || 0;
      }
    } catch (error) {
      console.error('Error fetching vehicle out count:', error);
      totalVehicleOut.value = 0;
    }
  };

  const getCountVehicleInside = async (): Promise<void> => {
    try {
      if (API_URL.value && API_URL.value !== '-') {
        const response = await api.get('/statistics/vehicle-inside');
        totalVehicleInside.value = response.data?.count || 0;
      } else {
        totalVehicleInside.value = vehicleInToday.value - totalVehicleOut.value;
      }
    } catch (error) {
      console.error('Error calculating vehicles inside:', error);
      totalVehicleInside.value = 0;
    }
  };

  const setManualOpenGate = async (gateId: string): Promise<boolean> => {
    try {
      // Create manual entry transaction
      const transaction: TransaksiParkir = {
        id: generateTransactionId(),
        no_pol: platNomor.value.toUpperCase() || 'MANUAL',
        id_kendaraan: selectedJenisKendaraan.value?.id || 1,
        status: 0,
        id_pintu_masuk: gateId || lokasiPos.value.value || '01',
        waktu_masuk: getCurrentDateTime(),
        id_op_masuk: pegawai.value?.id || 'OPERATOR',
        id_shift_masuk: shift.value || 'SHIFT1',
        kategori: 'MANUAL',
        status_transaksi: '0',
        jenis_system: 'MANUAL',
        tanggal: new Date().toISOString().split('T')[0],
        pic_driver_masuk: pic_body_masuk.value,
        pic_no_pol_masuk: pic_plat_masuk.value,
        sinkron: 0,
        upload: 0,
        manual: 1, // Mark as manual
        veri_check: 0,
        bayar_masuk: 0,
        alasan: 'Manual gate open by operator'
      };

      await saveTransactionToLocal(transaction);
      await saveTransactionToServer(transaction);
      
      transactionHistory.value.unshift(transaction);

      // Record the manual gate opening in logs
      await db.post({
        type: 'manual_open',
        gateId,
        timestamp: new Date().toISOString(),
        userId: pegawai.value?.id || 'OPERATOR',
        transactionId: transaction.id
      });

      gateStatuses.value[gateId] = true;
      
      // Auto close after 5 seconds
      setTimeout(() => {
        gateStatuses.value[gateId] = false;
      }, 5000);

      $q.notify({
        type: 'positive',
        message: 'Gate dibuka secara manual',
        position: 'top'
      });

      return true;
    } catch (error) {
      console.error('Error in manual gate open:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal membuka gate secara manual',
        position: 'top'
      });
      return false;
    }
  };

  // Initialize design documents for queries
  const initializeDesignDocs = async (): Promise<void> => {
    const designDoc = {
      _id: '_design/transaksi',
      views: {
        by_date: {
          map: `function (doc) {
            if (doc.type === 'parking_transaction' && doc.status === 0) {
              emit(doc.tanggal, 1);
            }
          }`,
          reduce: '_count'
        },
        out_by_date: {
          map: `function (doc) {
            if (doc.type === 'parking_transaction' && doc.status === 1) {
              emit(doc.tanggal, 1);
            }
          }`,
          reduce: '_count'
        },
        by_no_pol: {
          map: `function (doc) {
            if (doc.type === 'parking_transaction') {
              emit(doc.no_pol, doc);
            }
          }`
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

  // Utility functions
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR'
    }).format(amount);
  };

  const formatDuration = (startTime: string, endTime?: string): string => {
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const durationMs = end.getTime() - start.getTime();
    
    const hours = Math.floor(durationMs / (1000 * 60 * 60));
    const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${hours}j ${minutes}m`;
  };

  const searchTransactionByPlateNumber = async (plateNumber: string): Promise<TransaksiParkir[]> => {
    try {
      const result = await db.query('transaksi/by_no_pol', {
        key: plateNumber.toUpperCase(),
        include_docs: true
      });
      
      return result.rows.map((row: any) => row.doc as TransaksiParkir);
    } catch (error) {
      console.error('Error searching transaction by plate number:', error);
      return [];
    }
  };

  // Initialize the store
  initializeDesignDocs();

  return {
    // State
    platNomor,
    selectedJenisKendaraan,
    jenisKendaraan,
    dataCustomer,
    isCheckedIn,
    isMemberExpired,
    biayaParkir,
    bayar,
    currentTransaction,
    transactionHistory,
    pic_body_masuk,
    pic_body_keluar,
    pic_plat_masuk,
    pic_plat_keluar,
    vehicleInToday,
    totalVehicleOut,
    totalVehicleInside,
    gateStatuses,
    API_URL,
    lokasiPos,
    
    // Computed
    isAdmin,
    pegawai,
    shift,
    
    // Methods
    getCustomerByNopol,
    getEntryTarif,
    getJenisKendaraan,
    createEntryTransaction,
    createExitTransaction,
    processEntryTransaction,
    processExitTransaction,
    setManualOpenGate,
    resetTransactionState,
    saveTransactionToLocal,
    saveTransactionToServer,
    calculateParkingFee,
    getCountVehicleInToday,
    getCountVehicleOutToday,
    getCountVehicleInside,
    searchTransactionByPlateNumber,
    
    // Utilities
    formatCurrency,
    formatDuration,
    generateTransactionId,
    getCurrentDateTime
  };
});
