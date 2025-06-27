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

  // New method to get detailed vehicle out data for today
  const getVehicleOutDetailsToday = async () => {
    try {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const endOfDay = new Date();
      endOfDay.setHours(23, 59, 59, 999);

      console.log("🚀 ~ getVehicleOutDetailsToday ~ Date range:", {
        today: today.toISOString(),
        endOfDay: endOfDay.toISOString()
      });

      const result = await db.allDocs({
        include_docs: true,
        startkey: 'transaction_',
        endkey: 'transaction_\ufff0'
      });
      
      console.log("🚀 ~ getVehicleOutDetailsToday ~ Raw database results:", result.rows.length);
      
      // Debug: Show all transaction types and statuses
      const allDocs = result.rows.map(row => row.doc as any);
      const parkingTransactions = allDocs.filter(doc => doc?.type === 'parking_transaction');
      const statusBreakdown = parkingTransactions.reduce((acc: any, doc: any) => {
        acc[doc.status] = (acc[doc.status] || 0) + 1;
        return acc;
      }, {});
      
      console.log("🚀 ~ Status breakdown of all parking transactions:", statusBreakdown);
      console.log("🚀 ~ All parking transactions:", parkingTransactions.map((doc: any) => ({
        id: doc._id,
        plat: doc.no_pol,
        status: doc.status,
        waktu_masuk: doc.waktu_masuk,
        waktu_keluar: doc.waktu_keluar,
        tanggal: doc.tanggal
      })));

      // Filter for transactions that exited today (status 1 and waktu_keluar today)
      const todayExitTransactions = result.rows
        .map(row => row.doc)
        .filter((doc: any) => {
          // Must be a parking transaction
          if (!doc || doc.type !== 'parking_transaction') {
            return false;
          }
          
          // Must have exit status (1) and exit time
          if (doc.status !== 1 || !doc.waktu_keluar) {
            console.log(`🚀 Skipping transaction ${doc._id}: status=${doc.status}, waktu_keluar=${doc.waktu_keluar}`);
            return false;
          }
          
          // Check if exit time is today
          const exitDate = new Date(doc.waktu_keluar);
          const isToday = exitDate >= today && exitDate <= endOfDay;
          
          console.log(`🚀 Transaction ${doc._id}: status=${doc.status}, waktu_keluar=${doc.waktu_keluar}, isToday=${isToday}`);
          
          return isToday;
        });

      console.log("🚀 ~ Filtered exit transactions today:", todayExitTransactions.length);
      
      if (todayExitTransactions.length > 0) {
        console.log("🚀 ~ Exit transactions details:", todayExitTransactions.map((t: any) => ({
          id: t?._id || 'unknown',
          plat: t?.no_pol || 'unknown',
          status: t?.status || 0,
          waktu_keluar: t?.waktu_keluar || 'unknown',
          bayar_keluar: t?.bayar_keluar || 0,
          id_kendaraan: t?.id_kendaraan || 0
        })));
      } else {
        console.log("🚀 ~ No exit transactions found for today");
      }

      // Get jenis kendaraan data for mapping
      const jenisKendaraanData = await getJenisKendaraan();

      // Group by vehicle type and calculate totals
      const vehicleStats = jenisKendaraanData.map(jenis => {
        const vehicleTransactions = todayExitTransactions.filter((t: any) => 
          t.id_kendaraan === jenis.id
        );

        const count = vehicleTransactions.length;
        const uang_masuk = vehicleTransactions.reduce((total, t: any) => 
          total + (parseInt(t.bayar_keluar || 0)), 0
        );

        if (count > 0) {
          console.log(`🚀 Vehicle type ${jenis.label}: count=${count}, revenue=${uang_masuk}`);
        }

        return {
          id: jenis.id,
          jenis_kendaraan: jenis.label, // Use 'label' instead of 'jenis_kendaraan'
          count,
          uang_masuk
        };
      }).filter(item => item.count > 0); // Only return types with actual exits

      console.log('🚗 Final vehicle out details today:', vehicleStats);
      return vehicleStats;

    } catch (error) {
      console.error('❌ Error fetching vehicle out details:', error);
      return [];
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

  // Initialize design documents and indexes for queries
  const initializeDesignDocs = async (): Promise<void> => {
    // Create indexes for sorting
    try {
      // Index for waktu_masuk field (used for sorting)
      await db.createIndex({
        index: {
          fields: ['type', 'waktu_masuk']
        }
      });

      // Index for status field (used for filtering)
      await db.createIndex({
        index: {
          fields: ['type', 'status']
        }
      });

      // Index for no_pol field (used for filtering)
      await db.createIndex({
        index: {
          fields: ['type', 'no_pol']
        }
      });

      // Index for tanggal field (used for filtering)
      await db.createIndex({
        index: {
          fields: ['type', 'tanggal']
        }
      });

      // Index for id_kendaraan field (used for filtering)
      await db.createIndex({
        index: {
          fields: ['type', 'id_kendaraan']
        }
      });

      // Composite index for complex queries
      await db.createIndex({
        index: {
          fields: ['type', 'status', 'waktu_masuk']
        }
      });

      console.log('✅ Indexes created successfully');
    } catch (err: any) {
      console.warn('Index creation warning:', err);
    }

    // Create design document for views
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

  // Helper function to validate and normalize filter parameters
  const validateFilterParams = (params: any) => {
    const normalized = {
      page: Math.max(1, parseInt(params.page) || 1),
      limit: Math.max(1, Math.min(1000, parseInt(params.limit) || 25)),
      sortBy: params.sortBy?.trim() || 'waktu_masuk',
      sortOrder: params.sortOrder === 'asc' ? 'asc' : 'desc',
      platNomor: params.platNomor?.toString().trim() || '',
      status: params.status !== null && params.status !== undefined && params.status !== '' ? parseInt(params.status) : null,
      tanggalMulai: params.tanggalMulai?.toString().trim() || '',
      tanggalAkhir: params.tanggalAkhir?.toString().trim() || '',
      jenisKendaraan: params.jenisKendaraan?.toString().trim() || ''
    };

    // Validate date format if provided
    if (normalized.tanggalMulai && !/^\d{4}-\d{2}-\d{2}$/.test(normalized.tanggalMulai)) {
      console.warn('⚠️ Invalid tanggalMulai format, should be YYYY-MM-DD:', normalized.tanggalMulai);
      normalized.tanggalMulai = '';
    }
    if (normalized.tanggalAkhir && !/^\d{4}-\d{2}-\d{2}$/.test(normalized.tanggalAkhir)) {
      console.warn('⚠️ Invalid tanggalAkhir format, should be YYYY-MM-DD:', normalized.tanggalAkhir);
      normalized.tanggalAkhir = '';
    }

    // Ensure date range is valid
    if (normalized.tanggalMulai && normalized.tanggalAkhir && normalized.tanggalMulai > normalized.tanggalAkhir) {
      console.warn('⚠️ Invalid date range: start date is after end date');
      [normalized.tanggalMulai, normalized.tanggalAkhir] = [normalized.tanggalAkhir, normalized.tanggalMulai];
    }

    console.log('✅ Normalized filter params:', normalized);
    return normalized;
  };

  // Reusable filter function
  const applyTransactionFilters = (docs: any[], filterParams: any, jenisKendaraanData: any[]) => {
    const { platNomor, status, tanggalMulai, tanggalAkhir, jenisKendaraan } = filterParams;
    
    return docs.filter((doc: any) => {
      // Must be a parking transaction
      if (!doc || doc.type !== 'parking_transaction') {
        return false;
      }

      // Filter by plate number (case insensitive)
      if (platNomor && platNomor !== '') {
        if (!doc.no_pol) {
          return false;
        }
        const regex = new RegExp(platNomor, 'i');
        if (!regex.test(doc.no_pol)) {
          return false;
        }
      }

      // Filter by status (handle string and number values)
      if (status !== null && status !== undefined) {
        const docStatus = parseInt(doc.status);
        if (docStatus !== status) {
          return false;
        }
      }

      // Filter by date range
      if (tanggalMulai && tanggalAkhir) {
        if (!doc.tanggal) {
          return false;
        }
        const docDate = doc.tanggal;
        if (docDate < tanggalMulai || docDate > tanggalAkhir) {
          return false;
        }
      }

      // Filter by vehicle type
      if (jenisKendaraan && jenisKendaraan !== '') {
        if (!doc.id_kendaraan) {
          return false;
        }
        const jenis = jenisKendaraanData.find(j => j.label === jenisKendaraan);
        if (!jenis || doc.id_kendaraan !== jenis.id) {
          return false;
        }
      }

      return true;
    });
  };

  // Method untuk halaman daftar transaksi
  const getAllTransaksi = async (filterParams: any = {}) => {
    try {
      // Validate and normalize filter parameters
      const {
        page,
        limit,
        sortBy,
        sortOrder,
        platNomor,
        status,
        tanggalMulai,
        tanggalAkhir,
        jenisKendaraan
      } = validateFilterParams(filterParams);

      console.log('🔍 getAllTransaksi called with:', filterParams);
      console.log('🔍 Filter parameters breakdown:', {
        platNomor: platNomor ? `"${platNomor}"` : 'empty',
        status: status !== null && status !== undefined ? status : 'not set',
        tanggalMulai: tanggalMulai ? `"${tanggalMulai}"` : 'empty',
        tanggalAkhir: tanggalAkhir ? `"${tanggalAkhir}"` : 'empty',
        jenisKendaraan: jenisKendaraan ? `"${jenisKendaraan}"` : 'empty'
      });

      // Use allDocs to get all transactions, then filter and sort manually
      // This avoids the PouchDB sorting index issues
      const result = await db.allDocs({
        include_docs: true,
        startkey: 'transaction_',
        endkey: 'transaction_\ufff0'
      });

      console.log("📋 Raw database result:", result.rows.length, "documents");

      // Debug: Log all raw documents first
      console.log('📋 Raw docs from database:', result.rows.map(row => {
        const doc = row.doc as any;
        return {
          id: row.id,
          doc_type: doc?.type,
          doc_status: doc?.status,
          doc_bayar_keluar: doc?.bayar_keluar,
          doc_bayar_masuk: doc?.bayar_masuk,
          doc_no_pol: doc?.no_pol
        };
      }));

      // Get jenis kendaraan data once for filtering
      const jenisKendaraanData = await getJenisKendaraan();

      // Apply filters using the reusable function
      let filteredDocs = applyTransactionFilters(
        result.rows.map(row => row.doc),
        { platNomor, status, tanggalMulai, tanggalAkhir, jenisKendaraan },
        jenisKendaraanData
      );

      console.log('🔍 Filtered documents:', filteredDocs.length);
      
      // Debug filter results
      if (filteredDocs.length > 0) {
        console.log('🔍 Sample filtered documents:');
        filteredDocs.slice(0, 3).forEach((doc: any, index) => {
          console.log(`  ${index + 1}. ID: ${doc._id}, Plat: ${doc.no_pol}, Status: ${doc.status}, Date: ${doc.tanggal}, Vehicle: ${doc.id_kendaraan}`);
        });
      } else {
        console.log('⚠️ No documents passed the filter!');
        console.log('🔍 Debug: Total raw docs before filtering:', result.rows.length);
        console.log('🔍 Debug: Parking transactions count:', result.rows.filter(row => (row.doc as any)?.type === 'parking_transaction').length);
      }

      // Sort manually
      if (sortBy && sortBy.trim() !== '') {
        console.log('🔀 Sorting by:', sortBy, 'order:', sortOrder);
        filteredDocs.sort((a: any, b: any) => {
          let aVal = a[sortBy];
          let bVal = b[sortBy];

          // Handle null/undefined values
          if (aVal === null || aVal === undefined) aVal = '';
          if (bVal === null || bVal === undefined) bVal = '';

          // Handle date/time fields
          if (sortBy === 'waktu_masuk' || sortBy === 'waktu_keluar' || sortBy === 'tanggal') {
            aVal = aVal ? new Date(aVal).getTime() : 0;
            bVal = bVal ? new Date(bVal).getTime() : 0;
          }

          // Handle numeric fields
          if (sortBy === 'bayar_keluar' || sortBy === 'bayar_masuk' || sortBy === 'tarif' || sortBy === 'status' || sortBy === 'id_kendaraan') {
            aVal = parseFloat(aVal) || 0;
            bVal = parseFloat(bVal) || 0;
          }

          // Handle string fields
          if (typeof aVal === 'string' && typeof bVal === 'string') {
            aVal = aVal.toLowerCase();
            bVal = bVal.toLowerCase();
          }

          if (sortOrder === 'desc') {
            return bVal > aVal ? 1 : bVal < aVal ? -1 : 0;
          } else {
            return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
          }
        });
        console.log('🔀 Sorting completed');
      }

      // Apply pagination
      const total = filteredDocs.length;
      const startIndex = (page - 1) * limit;
      const endIndex = startIndex + limit;
      const paginatedDocs = filteredDocs.slice(startIndex, endIndex);

      console.log('🔍 Total documents:', total);
      console.log('🔍 Current page results:', paginatedDocs.length);

      // Always return real data from database, even if empty
      return {
        data: paginatedDocs.map((doc: any) => ({
          id: doc._id,
          plat_nomor: doc.no_pol || '',
          jenis_kendaraan: getJenisKendaraanLabel(doc.id_kendaraan || 1),
          waktu_masuk: doc.waktu_masuk || '',
          waktu_keluar: doc.waktu_keluar || null,
          status: doc.status || 0,
          tarif: doc.bayar_keluar || doc.bayar_masuk || 0,
          petugas: doc.id_op_masuk || '',
          lokasi: doc.id_pintu_masuk || '',
          pic_plat_masuk: doc.pic_no_pol_masuk || '',
          pic_body_masuk: doc.pic_driver_masuk || '',
          pic_plat_keluar: doc.pic_no_pol_keluar || '',
          pic_body_keluar: doc.pic_driver_keluar || '',
          ...doc
        })),
        total: total,
        page,
        limit
      };
    } catch (error) {
      console.error('❌ Error getting all transaksi:', error);
      
      // Return empty data on error, no dummy data
      return {
        data: [],
        total: 0,
        page: 1,
        limit: 25
      };
    }
  };

  const getTransaksiStatistics = async (filterParams: any = {}) => {
    try {
      // Validate and normalize filter parameters
      const {
        platNomor,
        status,
        tanggalMulai,
        tanggalAkhir,
        jenisKendaraan
      } = validateFilterParams(filterParams);

      console.log('📊 getTransaksiStatistics called with:', filterParams);

      // Use the same approach as getAllTransaksi - get all docs and filter manually
      const result = await db.allDocs({
        include_docs: true,
        startkey: 'transaction_',
        endkey: 'transaction_\ufff0'
      });

      // Get jenis kendaraan data once for filtering
      const jenisKendaraanData = await getJenisKendaraan();

      // Apply filters using the reusable function
      const filteredDocs = applyTransactionFilters(
        result.rows.map(row => row.doc),
        { platNomor, status, tanggalMulai, tanggalAkhir, jenisKendaraan },
        jenisKendaraanData
      );

      console.log('📊 Found transactions:', filteredDocs.length);

      // Debug pendapatan calculation
      const completedTransactions = filteredDocs.filter((t: any) => t.status === 1);
      console.log('📊 Completed transactions for revenue:', completedTransactions.length);
      
      // Debug: Show all documents first
      console.log('📊 All filtered docs:', filteredDocs.map((t: any) => ({
        id: t._id,
        plat: t.no_pol,
        status: t.status,
        bayar_keluar: t.bayar_keluar,
        bayar_masuk: t.bayar_masuk
      })));
      
      completedTransactions.forEach((t: any, index) => {
        console.log(`📊 Transaction ${index + 1}:`, {
          id: t._id,
          plat: t.no_pol,
          bayar_keluar: t.bayar_keluar,
          bayar_masuk: t.bayar_masuk,
          id_kendaraan: t.id_kendaraan,
          status: t.status
        });
      });

      // Calculate revenue with more detailed logging
      let totalPendapatan = 0;
      
      // Count revenue from completed transactions (status 1)
      const completedRevenue = completedTransactions.reduce((total, t: any) => {
        const revenue = t.bayar_keluar || 0;
        if (revenue > 0) {
          console.log(`📊 Adding exit revenue: ${revenue} from transaction ${t._id}`);
        }
        return total + revenue;
      }, 0);
      
      // Count revenue from active prepaid transactions (status 0 with bayar_masuk)
      const activeTransactions = filteredDocs.filter((t: any) => t.status === 0);
      const prepaidRevenue = activeTransactions.reduce((total, t: any) => {
        const revenue = t.bayar_masuk || 0;
        if (revenue > 0) {
          console.log(`📊 Adding prepaid revenue: ${revenue} from active transaction ${t._id}`);
        }
        return total + revenue;
      }, 0);
      
      totalPendapatan = completedRevenue + prepaidRevenue;
      
      console.log(`📊 Revenue breakdown: Completed: ${completedRevenue}, Prepaid: ${prepaidRevenue}, Total: ${totalPendapatan}`);

      const stats = {
        totalTransaksi: filteredDocs.length,
        transaksiSelesai: completedTransactions.length,
        transaksiAktif: filteredDocs.filter((t: any) => t.status === 0).length,
        totalPendapatan: totalPendapatan
      };

      console.log('📊 Calculated statistics:', stats);
      
      return stats;
    } catch (error) {
      console.error('❌ Error getting statistics:', error);
      
      // Return empty stats on error, no dummy data
      return {
        totalTransaksi: 0,
        transaksiSelesai: 0,
        transaksiAktif: 0,
        totalPendapatan: 0
      };
    }
  };

  const processManualExit = async (transactionId: string) => {
    try {
      // Get transaction from local DB
      const transaction = await db.get(transactionId) as any;
      
      if (!transaction) {
        throw new Error('Transaksi tidak ditemukan');
      }

      if (transaction.status === 1) {
        throw new Error('Transaksi sudah selesai');
      }

      // Update transaction for exit
      const exitTransaction: any = {
        ...transaction,
        status: 1,
        waktu_keluar: getCurrentDateTime(),
        id_op_keluar: pegawai.value?.id || 'SYSTEM',
        id_shift_keluar: shift.value || 'SHIFT1',
        id_pintu_keluar: lokasiPos.value.value || '01'
      };

      // Calculate parking fee
      const parkingFee = calculateParkingFeeForTransaction(exitTransaction);
      exitTransaction.bayar_keluar = parkingFee;

      // Save to local DB
      await db.put(exitTransaction);

      // Try to sync to server if available
      try {
        // Convert to TransaksiParkir format for server
        const serverTransaction: TransaksiParkir = {
          id: exitTransaction._id || exitTransaction.id,
          no_pol: exitTransaction.no_pol,
          id_kendaraan: exitTransaction.id_kendaraan,
          status: exitTransaction.status,
          id_pintu_masuk: exitTransaction.id_pintu_masuk,
          id_pintu_keluar: exitTransaction.id_pintu_keluar,
          waktu_masuk: exitTransaction.waktu_masuk,
          waktu_keluar: exitTransaction.waktu_keluar,
          id_op_masuk: exitTransaction.id_op_masuk,
          id_op_keluar: exitTransaction.id_op_keluar,
          id_shift_masuk: exitTransaction.id_shift_masuk,
          id_shift_keluar: exitTransaction.id_shift_keluar,
          kategori: exitTransaction.kategori,
          status_transaksi: exitTransaction.status_transaksi,
          bayar_masuk: exitTransaction.bayar_masuk,
          bayar_keluar: exitTransaction.bayar_keluar,
          jenis_system: exitTransaction.jenis_system,
          tanggal: exitTransaction.tanggal,
          pic_driver_masuk: exitTransaction.pic_driver_masuk,
          pic_driver_keluar: exitTransaction.pic_driver_keluar,
          pic_no_pol_masuk: exitTransaction.pic_no_pol_masuk,
          pic_no_pol_keluar: exitTransaction.pic_no_pol_keluar,
          sinkron: exitTransaction.sinkron || 0,
          upload: exitTransaction.upload || 0,
          manual: exitTransaction.manual || 0,
          veri_check: exitTransaction.veri_check || 0
        };
        
        await saveTransactionToServer(serverTransaction);
      } catch (syncError) {
        console.warn('Failed to sync to server, saved locally:', syncError);
      }

      return exitTransaction;
    } catch (error) {
      console.error('Error processing manual exit:', error);
      throw error;
    }
  };

  const deleteTransaction = async (transactionId: string) => {
    try {
      const transaction = await db.get(transactionId);
      await db.remove(transaction);
      
      // Try to delete from server if available
      try {
        if (API_URL.value && API_URL.value !== '-') {
          await api.delete(`/transaksi/${transactionId}`);
        }
      } catch (syncError) {
        console.warn('Failed to delete from server:', syncError);
      }

      return true;
    } catch (error) {
      console.error('Error deleting transaction:', error);
      throw error;
    }
  };

  const exportTransaksi = async (filterParams: any = {}) => {
    try {
      const result = await getAllTransaksi({
        ...filterParams,
        limit: 10000, // Get all data for export
        page: 1
      });

      // Create CSV content
      const headers = [
        'ID',
        'Plat Nomor',
        'Jenis Kendaraan',
        'Waktu Masuk',
        'Waktu Keluar',
        'Status',
        'Tarif',
        'Petugas',
        'Lokasi'
      ];

      const csvContent = [
        headers.join(','),
        ...result.data.map(row => [
          row.id,
          row.plat_nomor,
          row.jenis_kendaraan,
          row.waktu_masuk,
          row.waktu_keluar || '',
          row.status === 0 ? 'Aktif' : row.status === 1 ? 'Selesai' : 'Dibatalkan',
          row.tarif,
          row.petugas,
          row.lokasi
        ].join(','))
      ].join('\n');

      // Download CSV file
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `transaksi_${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      return true;
    } catch (error) {
      console.error('Error exporting data:', error);
      throw error;
    }
  };

  const printTicket = (transaction: any) => {
    try {
      // Create printable ticket content
      const ticketContent = `
        <div style="font-family: monospace; width: 300px; padding: 10px;">
          <h3 style="text-align: center; margin: 0;">TIKET PARKIR</h3>
          <hr>
          <p><strong>ID:</strong> ${transaction.id}</p>
          <p><strong>Plat:</strong> ${transaction.plat_nomor}</p>
          <p><strong>Jenis:</strong> ${transaction.jenis_kendaraan}</p>
          <p><strong>Masuk:</strong> ${transaction.waktu_masuk}</p>
          ${transaction.waktu_keluar ? `<p><strong>Keluar:</strong> ${transaction.waktu_keluar}</p>` : ''}
          <p><strong>Tarif:</strong> ${formatCurrency(transaction.tarif)}</p>
          <p><strong>Status:</strong> ${transaction.status === 0 ? 'Aktif' : transaction.status === 1 ? 'Selesai' : 'Dibatalkan'}</p>
          <hr>
          <p style="text-align: center; font-size: 12px;">Terima kasih</p>
        </div>
      `;

      // Open print window
      const printWindow = window.open('', '_blank');
      if (printWindow) {
        printWindow.document.write(`
          <html>
            <head><title>Tiket Parkir</title></head>
            <body>${ticketContent}</body>
          </html>
        `);
        printWindow.document.close();
        printWindow.print();
      }
    } catch (error) {
      console.error('Error printing ticket:', error);
    }
  };

  const getJenisKendaraanLabel = (id: number): string => {
    const jenis = jenisKendaraan.value.find(j => j.id === id);
    return jenis?.label || 'Unknown';
  };

  const calculateParkingFeeForTransaction = (transaction: any): number => {
    if (!transaction.waktu_masuk || !transaction.waktu_keluar) {
      return 0;
    }

    const masuk = new Date(transaction.waktu_masuk);
    const keluar = new Date(transaction.waktu_keluar);
    const durationMs = keluar.getTime() - masuk.getTime();
    const durationHours = Math.ceil(durationMs / (1000 * 60 * 60)); // Round up to nearest hour

    // Get tarif based on vehicle type - use static mapping if jenisKendaraan not loaded
    let baseTarif = 5000; // Default for Mobil
    
    if (jenisKendaraan.value.length > 0) {
      const jenis = jenisKendaraan.value.find(j => j.id === transaction.id_kendaraan);
      baseTarif = jenis?.tarif || 5000;
    } else {
      // Fallback static mapping
      const tarifMap: Record<number, number> = {
        1: 5000,  // Mobil
        2: 2000,  // Motor
        3: 10000  // Truck/Box
      };
      baseTarif = tarifMap[transaction.id_kendaraan] || 5000;
    }

    const totalFee = Math.max(baseTarif, baseTarif * durationHours);
    
    console.log('💰 Calculating parking fee:', {
      id: transaction._id || transaction.id,
      duration_hours: durationHours,
      base_tarif: baseTarif,
      total_fee: totalFee,
      vehicle_type: transaction.id_kendaraan
    });

    return totalFee;
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

  // Testing utilities
  const addSampleDataForTesting = async () => {
    try {
      console.log('🧪 Adding sample data for testing...');
      
      const sampleTransactions = [
        {
          id: generateTransactionId(),
          no_pol: 'B1234ABC',
          id_kendaraan: 1,
          status: 1, // Completed
          id_pintu_masuk: '01',
          id_pintu_keluar: '01',
          waktu_masuk: new Date(Date.now() - 4 * 3600000).toISOString(), // 4 hours ago
          waktu_keluar: new Date(Date.now() - 30 * 60000).toISOString(), // 30 minutes ago
          id_op_masuk: 'ADMIN',
          id_op_keluar: 'ADMIN',
          id_shift_masuk: 'SHIFT1',
          id_shift_keluar: 'SHIFT1',
          kategori: 'UMUM',
          status_transaksi: '0',
          jenis_system: 'MANLESS',
          tanggal: new Date().toISOString().split('T')[0],
          bayar_masuk: 0,
          bayar_keluar: 20000, // 4 hours * 5000
          sinkron: 0,
          upload: 0,
          manual: 0,
          veri_check: 0
        },
        {
          id: generateTransactionId(),
          no_pol: 'B5678DEF',
          id_kendaraan: 2,
          status: 1, // Completed
          id_pintu_masuk: '01',
          id_pintu_keluar: '01',
          waktu_masuk: new Date(Date.now() - 3 * 3600000).toISOString(), // 3 hours ago
          waktu_keluar: new Date(Date.now() - 15 * 60000).toISOString(), // 15 minutes ago
          id_op_masuk: 'ADMIN',
          id_op_keluar: 'ADMIN',
          id_shift_masuk: 'SHIFT1',
          id_shift_keluar: 'SHIFT1',
          kategori: 'UMUM',
          status_transaksi: '0',
          jenis_system: 'MANLESS',
          tanggal: new Date().toISOString().split('T')[0],
          bayar_masuk: 0,
          bayar_keluar: 6000, // 3 hours * 2000
          sinkron: 0,
          upload: 0,
          manual: 0,
          veri_check: 0
        },
        {
          id: generateTransactionId(),
          no_pol: 'B9012GHI',
          id_kendaraan: 1,
          status: 0, // Still parked
          id_pintu_masuk: '01',
          waktu_masuk: new Date(Date.now() - 1 * 3600000).toISOString(), // 1 hour ago
          id_op_masuk: 'ADMIN',
          id_shift_masuk: 'SHIFT1',
          kategori: 'UMUM',
          status_transaksi: '0',
          jenis_system: 'MANLESS',
          tanggal: new Date().toISOString().split('T')[0],
          bayar_masuk: 0,
          sinkron: 0,
          upload: 0,
          manual: 0,
          veri_check: 0
        }
      ];

      for (const transaction of sampleTransactions) {
        await db.post({
          ...transaction,
          _id: `transaction_${transaction.id}`,
          type: 'parking_transaction'
        });
      }
      
      console.log('🧪 Sample data added successfully');
      console.log('📊 Expected revenue: 26000 (20000 + 6000)');
      
      return true;
    } catch (error) {
      console.error('❌ Error adding sample data:', error);
      return false;
    }
  };

  // Function to check if database has any parking transactions
  const checkDatabaseHasData = async () => {
    try {
      const result = await db.find({
        selector: {
          type: 'parking_transaction'
        },
        limit: 1
      });
      
      return result.docs.length > 0;
    } catch (error) {
      console.error('Error checking database:', error);
      return false;
    }
  };

  // Function to process exit for all active transactions (for testing)
  const processExitAllActiveTransactions = async () => {
    try {
      console.log('🚪 Processing exit for all active transactions...');
      
      // Get all active transactions
      const result = await db.allDocs({
        include_docs: true,
        startkey: 'transaction_',
        endkey: 'transaction_\ufff0'
      });
      
      const activeTransactions = result.rows
        .map(row => row.doc as any)
        .filter(doc => doc.type === 'parking_transaction' && doc.status === 0);
      
      console.log(`🚪 Found ${activeTransactions.length} active transactions to process`);
      
      let processedCount = 0;
      for (const transaction of activeTransactions) {
        try {
          // Calculate exit time (random between 30 minutes to 2 hours from now)
          const exitDelayMs = Math.random() * (2 * 3600000 - 30 * 60000) + 30 * 60000;
          const exitTime = new Date(Date.now() - exitDelayMs).toISOString();
          
          // Update transaction for exit
          const exitTransaction = {
            ...transaction,
            status: 1,
            waktu_keluar: exitTime,
            id_op_keluar: pegawai.value?.id || 'SYSTEM',
            id_shift_keluar: shift.value || 'SHIFT1',
            id_pintu_keluar: lokasiPos.value.value || '01'
          };
          
          // Calculate parking fee
          const parkingFee = calculateParkingFeeForTransaction(exitTransaction);
          exitTransaction.bayar_keluar = parkingFee;
          
          // Save back to database
          await db.put(exitTransaction);
          processedCount++;
          
          console.log(`🚪 Processed exit for ${transaction.no_pol}: ${parkingFee} IDR`);
        } catch (error) {
          console.error(`❌ Error processing exit for ${transaction.no_pol}:`, error);
        }
      }
      
      console.log(`✅ Successfully processed exit for ${processedCount} transactions`);
      return processedCount;
    } catch (error) {
      console.error('❌ Error processing exit for active transactions:', error);
      return 0;
    }
  };
        

  // Initialize design documents and indexes for queries
  initializeDesignDocs().then(() => {
    console.log('📊 Transaksi store initialized with indexes');
  }).catch(err => {
    console.error('❌ Error initializing transaksi store:', err);
  });

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
    getVehicleOutDetailsToday,
    getCountVehicleInside,
    searchTransactionByPlateNumber,
    calculateParkingFeeForTransaction,
    getJenisKendaraanLabel,
    
    // New methods for daftar transaksi
    getAllTransaksi,
    getTransaksiStatistics,
    processManualExit,
    deleteTransaction,
    exportTransaksi,
    printTicket,
    
    // Testing utilities
    addSampleDataForTesting,
    checkDatabaseHasData,
    processExitAllActiveTransactions,
    
    // Utilities
    formatCurrency,
    formatDuration,
    generateTransactionId,
    getCurrentDateTime
  };
});
