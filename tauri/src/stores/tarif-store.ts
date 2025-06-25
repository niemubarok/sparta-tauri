import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useQuasar } from 'quasar';
import ls from 'localstorage-slim';
import { localDbs } from 'src/boot/pouchdb';

// Interface untuk tarif berdasarkan struktur database
export interface Tarif {
  id: string;
  id_mobil: string; // Reference to jenis_mobil
  jam_ke: number;
  tarif: number;
  tarif_denda?: number;
  tarif_member?: number;
  time_base: number; // dalam menit
  time_base_maks?: number;
  max_free_same_hour?: number;
  tarif_max_per_hari?: number; // Maksimal tarif per hari
  tarif2?: number; // Tarif jam berikutnya (progressive tariff)
  waktu2?: number; // Durasi untuk tarif kedua
  maksimum?: number; // Maksimal tarif (alias untuk tarif_max_per_hari)
  max_per_hari?: number; // Flag maksimal per hari (0/1)
  status?: number; // 1 = aktif, 0 = tidak aktif
  created_at?: string;
  updated_at?: string;
  created_by?: string;
}

// Interface untuk tarif inap
export interface TarifInap {
  id: string;
  id_mobil: string;
  tarif_inap: number;
  jam_mulai: number; // jam berapa dianggap inap (misal: 22 = 22:00)
  jam_selesai: number; // jam berapa selesai inap (misal: 6 = 06:00)
  status?: number;
  tanggal?: string;
  created_at?: string;
  updated_at?: string;
}

// Interface untuk tarif member
export interface TarifMember {
  id: string;
  id_mobil: string;
  tarif_member: number;
  max_per_hari?: number;
  diskon_persen?: number;
  status?: number;
  created_at?: string;
  updated_at?: string;
}

// Interface untuk tarif stiker/langganan
export interface TarifStiker {
  id: string;
  id_mobil: string;
  jenis_stiker: string; // bulanan, tahunan, dll
  tarif_stiker: number;
  masa_berlaku: number; // dalam hari
  biaya_inap_berlaku?: number;
  max_kendaraan?: number;
  status?: number;
  created_at?: string;
  updated_at?: string;
}

// Interface untuk tarif prepaid (bayar depan)
export interface TarifPrepaid {
  id: string;
  id_mobil: string;
  tarif_prepaid: number; // Tarif flat yang dibayar di awal
  durasi_berlaku: number; // Durasi dalam jam yang sudah dibayar
  tarif_tambahan?: number; // Tarif per jam jika melebihi durasi berlaku
  berlaku_tanpa_batas?: boolean; // Jika true, tidak ada batas waktu
  status?: number; // 1 = aktif, 0 = tidak aktif
  created_at?: string;
  updated_at?: string;
  created_by?: string;
}

export const useTarifStore = defineStore('tarif', () => {
  const $q = useQuasar();
  const db = localDbs.tarif;
  
  // State variables
  const daftarTarif = ref<Tarif[]>([]);
  const daftarTarifInap = ref<TarifInap[]>([]);
  const daftarTarifMember = ref<TarifMember[]>([]);
  const daftarTarifPrepaid = ref<TarifPrepaid[]>([]);
  const daftarTarifStiker = ref<TarifStiker[]>([]);
  const isLoading = ref<boolean>(false);
  
  // Computed properties
  const activeTarif = computed(() => 
    daftarTarif.value.filter(t => t.status === 1)
  );

  const activeTarifInap = computed(() => 
    daftarTarifInap.value.filter(t => t.status === 1)
  );

  const activeTarifMember = computed(() => 
    daftarTarifMember.value.filter(t => t.status === 1)
  );

  const activeTarifPrepaid = computed(() => 
    daftarTarifPrepaid.value.filter(t => t.status === 1)
  );

  const activeTarifStiker = computed(() => 
    daftarTarifStiker.value.filter(t => t.status === 1)
  );

  // Tarif for select options
  const tarifForSelect = computed(() => 
    activeTarif.value.map(t => ({
      value: t.id,
      label: `Jam ke-${t.jam_ke}: Rp ${t.tarif.toLocaleString()}`,
      tarif: t.tarif,
      jam_ke: t.jam_ke
    }))
  );

  // Utility functions
  const generateTarifId = (): string => {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    return `TRF${timestamp}${random}`;
  };

  const generateTarifInapId = (): string => {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    return `TRI${timestamp}${random}`;
  };

  const generateTarifMemberId = (): string => {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    return `TRM${timestamp}${random}`;
  };

  const generateTarifStikerId = (): string => {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    return `TRS${timestamp}${random}`;
  };

  // Design document initialization
  const initializeDesignDocs = async (): Promise<void> => {
    const designDoc = {
      _id: '_design/tarif',
      views: {
        by_id_mobil: {
          map: `function (doc) {
            if (doc.type === 'tarif') {
              emit(doc.id_mobil, doc);
            }
          }`
        },
        by_jam_ke: {
          map: `function (doc) {
            if (doc.type === 'tarif') {
              emit([doc.id_mobil, doc.jam_ke], doc);
            }
          }`
        },
        tarif_inap_by_mobil: {
          map: `function (doc) {
            if (doc.type === 'tarif_inap') {
              emit(doc.id_mobil, doc);
            }
          }`
        },
        tarif_member_by_mobil: {
          map: `function (doc) {
            if (doc.type === 'tarif_member') {
              emit(doc.id_mobil, doc);
            }
          }`
        },
        tarif_stiker_by_mobil: {
          map: `function (doc) {
            if (doc.type === 'tarif_stiker') {
              emit(doc.id_mobil, doc);
            }
          }`
        },
        tarif_prepaid_by_mobil: {
          map: `function (doc) {
            if (doc.type === 'tarif_prepaid') {
              emit(doc.id_mobil, doc);
            }
          }`
        }
      }
    };

    try {
      await db.put(designDoc);
    } catch (error: any) {
      if (error.name !== 'conflict') {
        console.error('Error creating design document:', error);
      }
    }
  };

  // CRUD Operations for Tarif Reguler
  const addTarif = async (newTarif: Omit<Tarif, 'id'>): Promise<boolean> => {
    try {
      const tarifId = generateTarifId();
      const tarif: Tarif = {
        id: tarifId,
        ...newTarif,
        status: newTarif.status ?? 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        created_by: (ls.get('pegawai') as any)?.id_petugas || 'SYSTEM'
      };

      // Save to local database
      await db.put({
        _id: `tarif_${tarif.id}`,
        type: 'tarif',
        ...tarif
      });

      // Add to local array
      daftarTarif.value.push(tarif);

      $q.notify({
        type: 'positive',
        message: 'Tarif berhasil ditambahkan',
        icon: 'check'
      });

      return true;
    } catch (error) {
      console.error('Error adding tarif:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal menambahkan tarif',
        caption: (error as Error).message,
        icon: 'error'
      });
      return false;
    }
  };

  const editTarif = async (updatedTarif: Tarif): Promise<boolean> => {
    try {
      const tarif = {
        ...updatedTarif,
        updated_at: new Date().toISOString()
      };

      // Update local database
      const doc = await db.get(`tarif_${tarif.id}`);
      await db.put({
        ...doc,
        ...tarif
      });

      // Update local array
      const index = daftarTarif.value.findIndex(t => t.id === tarif.id);
      if (index !== -1) {
        daftarTarif.value[index] = tarif;
      }

      $q.notify({
        type: 'positive',
        message: 'Tarif berhasil diperbarui',
        icon: 'check'
      });

      return true;
    } catch (error) {
      console.error('Error editing tarif:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal memperbarui tarif',
        caption: (error as Error).message,
        icon: 'error'
      });
      return false;
    }
  };

  const deleteTarif = async (tarifId: string): Promise<boolean> => {
    try {
      // Soft delete - set status to 0
      const index = daftarTarif.value.findIndex(t => t.id === tarifId);
      if (index === -1) return false;

      const updatedTarif = {
        ...daftarTarif.value[index],
        status: 0,
        updated_at: new Date().toISOString()
      };

      return await editTarif(updatedTarif);
    } catch (error) {
      console.error('Error deleting tarif:', error);
      return false;
    }
  };

  // Load data from local database
  const loadTarifFromLocal = async (): Promise<void> => {
    try {
      const result = await db.allDocs({
        include_docs: true,
        startkey: 'tarif_',
        endkey: 'tarif_\ufff0'
      });

      daftarTarif.value = result.rows.map(row => {
        const doc = row.doc as any;
        return {
          id: doc.id,
          id_mobil: doc.id_mobil,
          jam_ke: doc.jam_ke,
          tarif: doc.tarif,
          tarif_denda: doc.tarif_denda,
          tarif_member: doc.tarif_member,
          time_base: doc.time_base,
          time_base_maks: doc.time_base_maks,
          max_free_same_hour: doc.max_free_same_hour,
          status: doc.status,
          created_at: doc.created_at,
          updated_at: doc.updated_at,
          created_by: doc.created_by
        } as Tarif;
      });
    } catch (error) {
      console.error('Error loading tarif from local:', error);
      daftarTarif.value = [];
    }
  };

  // CRUD Operations for Tarif Inap
  const addTarifInap = async (newTarifInap: Omit<TarifInap, 'id'>): Promise<boolean> => {
    try {
      const tarifInapId = generateTarifInapId();
      const tarifInap: TarifInap = {
        id: tarifInapId,
        ...newTarifInap,
        status: newTarifInap.status ?? 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      await db.put({
        _id: `tarif_inap_${tarifInap.id}`,
        type: 'tarif_inap',
        ...tarifInap
      });

      daftarTarifInap.value.push(tarifInap);

      $q.notify({
        type: 'positive',
        message: 'Tarif inap berhasil ditambahkan',
        icon: 'check'
      });

      return true;
    } catch (error) {
      console.error('Error adding tarif inap:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal menambahkan tarif inap',
        icon: 'error'
      });
      return false;
    }
  };

  const editTarifInap = async (updatedTarifInap: TarifInap): Promise<boolean> => {
    try {
      const tarifInap = {
        ...updatedTarifInap,
        updated_at: new Date().toISOString()
      };

      // Update local database
      const doc = await db.get(`tarif_inap_${tarifInap.id}`);
      await db.put({
        ...doc,
        ...tarifInap
      });

      // Update local array
      const index = daftarTarifInap.value.findIndex(t => t.id === tarifInap.id);
      if (index !== -1) {
        daftarTarifInap.value[index] = tarifInap;
      }

      $q.notify({
        type: 'positive',
        message: 'Tarif inap berhasil diperbarui',
        icon: 'check'
      });

      return true;
    } catch (error) {
      console.error('Error editing tarif inap:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal memperbarui tarif inap',
        caption: (error as Error).message,
        icon: 'error'
      });
      return false;
    }
  };

  const deleteTarifInap = async (tarifInapId: string): Promise<boolean> => {
    try {
      // Soft delete - set status to 0
      const index = daftarTarifInap.value.findIndex(t => t.id === tarifInapId);
      if (index === -1) return false;

      const updatedTarifInap = {
        ...daftarTarifInap.value[index],
        status: 0,
        updated_at: new Date().toISOString()
      };

      return await editTarifInap(updatedTarifInap);
    } catch (error) {
      console.error('Error deleting tarif inap:', error);
      return false;
    }
  };

  // Load tarif inap from local database
  const loadTarifInapFromLocal = async (): Promise<void> => {
    try {
      const result = await db.allDocs({
        include_docs: true,
        startkey: 'tarif_inap_',
        endkey: 'tarif_inap_\ufff0'
      });

      daftarTarifInap.value = result.rows.map(row => {
        const doc = row.doc as any;
        return {
          id: doc.id,
          id_mobil: doc.id_mobil,
          tarif_inap: doc.tarif_inap,
          jam_mulai: doc.jam_mulai,
          jam_selesai: doc.jam_selesai,
          status: doc.status,
          tanggal: doc.tanggal,
          created_at: doc.created_at,
          updated_at: doc.updated_at
        } as TarifInap;
      });
    } catch (error) {
      console.error('Error loading tarif inap from local:', error);
      daftarTarifInap.value = [];
    }
  };

  // CRUD Operations for Tarif Member
  const addTarifMember = async (newTarifMember: Omit<TarifMember, 'id'>): Promise<boolean> => {
    try {
      const tarifMemberId = generateTarifMemberId();
      const tarifMember: TarifMember = {
        id: tarifMemberId,
        ...newTarifMember,
        status: newTarifMember.status ?? 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      await db.put({
        _id: `tarif_member_${tarifMember.id}`,
        type: 'tarif_member',
        ...tarifMember
      });

      daftarTarifMember.value.push(tarifMember);

      $q.notify({
        type: 'positive',
        message: 'Tarif member berhasil ditambahkan',
        icon: 'check'
      });

      return true;
    } catch (error) {
      console.error('Error adding tarif member:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal menambahkan tarif member',
        icon: 'error'
      });
      return false;
    }
  };

  const editTarifMember = async (updatedTarifMember: TarifMember): Promise<boolean> => {
    try {
      const tarifMember = {
        ...updatedTarifMember,
        updated_at: new Date().toISOString()
      };

      // Update local database
      const doc = await db.get(`tarif_member_${tarifMember.id}`);
      await db.put({
        ...doc,
        ...tarifMember
      });

      // Update local array
      const index = daftarTarifMember.value.findIndex(t => t.id === tarifMember.id);
      if (index !== -1) {
        daftarTarifMember.value[index] = tarifMember;
      }

      $q.notify({
        type: 'positive',
        message: 'Tarif member berhasil diperbarui',
        icon: 'check'
      });

      return true;
    } catch (error) {
      console.error('Error editing tarif member:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal memperbarui tarif member',
        caption: (error as Error).message,
        icon: 'error'
      });
      return false;
    }
  };

  const deleteTarifMember = async (tarifMemberId: string): Promise<boolean> => {
    try {
      // Soft delete - set status to 0
      const index = daftarTarifMember.value.findIndex(t => t.id === tarifMemberId);
      if (index === -1) return false;

      const updatedTarifMember = {
        ...daftarTarifMember.value[index],
        status: 0,
        updated_at: new Date().toISOString()
      };

      return await editTarifMember(updatedTarifMember);
    } catch (error) {
      console.error('Error deleting tarif member:', error);
      return false;
    }
  };

  // Load tarif member from local database
  const loadTarifMemberFromLocal = async (): Promise<void> => {
    try {
      const result = await db.allDocs({
        include_docs: true,
        startkey: 'tarif_member_',
        endkey: 'tarif_member_\ufff0'
      });

      daftarTarifMember.value = result.rows.map(row => {
        const doc = row.doc as any;
        return {
          id: doc.id,
          id_mobil: doc.id_mobil,
          tarif_member: doc.tarif_member,
          max_per_hari: doc.max_per_hari,
          diskon_persen: doc.diskon_persen,
          status: doc.status,
          created_at: doc.created_at,
          updated_at: doc.updated_at
        } as TarifMember;
      });
    } catch (error) {
      console.error('Error loading tarif member from local:', error);
      daftarTarifMember.value = [];
    }
  };

  // CRUD Operations for Tarif Stiker
  const addTarifStiker = async (newTarifStiker: Omit<TarifStiker, 'id'>): Promise<boolean> => {
    try {
      const tarifStikerId = generateTarifStikerId();
      const tarifStiker: TarifStiker = {
        id: tarifStikerId,
        ...newTarifStiker,
        status: newTarifStiker.status ?? 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      await db.put({
        _id: `tarif_stiker_${tarifStiker.id}`,
        type: 'tarif_stiker',
        ...tarifStiker
      });

      daftarTarifStiker.value.push(tarifStiker);

      $q.notify({
        type: 'positive',
        message: 'Tarif stiker berhasil ditambahkan',
        icon: 'check'
      });

      return true;
    } catch (error) {
      console.error('Error adding tarif stiker:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal menambahkan tarif stiker',
        icon: 'error'
      });
      return false;
    }
  };

  const editTarifStiker = async (updatedTarifStiker: TarifStiker): Promise<boolean> => {
    try {
      const tarifStiker = {
        ...updatedTarifStiker,
        updated_at: new Date().toISOString()
      };

      // Update local database
      const doc = await db.get(`tarif_stiker_${tarifStiker.id}`);
      await db.put({
        ...doc,
        ...tarifStiker
      });

      // Update local array
      const index = daftarTarifStiker.value.findIndex(t => t.id === tarifStiker.id);
      if (index !== -1) {
        daftarTarifStiker.value[index] = tarifStiker;
      }

      $q.notify({
        type: 'positive',
        message: 'Tarif stiker berhasil diperbarui',
        icon: 'check'
      });

      return true;
    } catch (error) {
      console.error('Error editing tarif stiker:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal memperbarui tarif stiker',
        caption: (error as Error).message,
        icon: 'error'
      });
      return false;
    }
  };

  const deleteTarifStiker = async (tarifStikerId: string): Promise<boolean> => {
    try {
      // Soft delete - set status to 0
      const index = daftarTarifStiker.value.findIndex(t => t.id === tarifStikerId);
      if (index === -1) return false;

      const updatedTarifStiker = {
        ...daftarTarifStiker.value[index],
        status: 0,
        updated_at: new Date().toISOString()
      };

      return await editTarifStiker(updatedTarifStiker);
    } catch (error) {
      console.error('Error deleting tarif stiker:', error);
      return false;
    }
  };

  // Load tarif stiker from local database
  const loadTarifStikerFromLocal = async (): Promise<void> => {
    try {
      const result = await db.allDocs({
        include_docs: true,
        startkey: 'tarif_stiker_',
        endkey: 'tarif_stiker_\ufff0'
      });

      daftarTarifStiker.value = result.rows.map(row => {
        const doc = row.doc as any;
        return {
          id: doc.id,
          id_mobil: doc.id_mobil,
          jenis_stiker: doc.jenis_stiker,
          tarif_stiker: doc.tarif_stiker,
          masa_berlaku: doc.masa_berlaku,
          biaya_inap_berlaku: doc.biaya_inap_berlaku,
          max_kendaraan: doc.max_kendaraan,
          status: doc.status,
          created_at: doc.created_at,
          updated_at: doc.updated_at
        } as TarifStiker;
      });
    } catch (error) {
      console.error('Error loading tarif stiker from local:', error);
      daftarTarifStiker.value = [];
    }
  };

  // ================================
  // TARIF PREPAID METHODS
  // ================================

  const addTarifPrepaid = async (tarifPrepaidData: Omit<TarifPrepaid, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      isLoading.value = true;
      
      const newTarifPrepaid: TarifPrepaid = {
        id: `TPR${Date.now()}${Math.floor(Math.random() * 1000)}`,
        ...tarifPrepaidData,
        status: tarifPrepaidData.status || 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        created_by: tarifPrepaidData.created_by || 'SYSTEM'
      };

      // Save to PouchDB
      const doc = {
        _id: newTarifPrepaid.id,
        type: 'tarif_prepaid',
        ...newTarifPrepaid
      };

      await db.put(doc);
      
      // Update local state
      daftarTarifPrepaid.value.push(newTarifPrepaid);
      
      $q.notify({
        type: 'positive',
        message: 'Tarif prepaid berhasil ditambahkan',
        icon: 'check'
      });

      return newTarifPrepaid;
    } catch (error) {
      console.error('Error adding tarif prepaid:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal menambahkan tarif prepaid',
        icon: 'error'
      });
      throw error;
    } finally {
      isLoading.value = false;
    }
  };

  const editTarifPrepaid = async (tarifPrepaidData: TarifPrepaid) => {
    try {
      isLoading.value = true;
      
      const updatedTarifPrepaid = {
        ...tarifPrepaidData,
        updated_at: new Date().toISOString()
      };

      // Get existing doc for revision
      const existingDoc = await db.get(tarifPrepaidData.id);
      
      // Update in PouchDB - preserve _id and _rev
      const doc = {
        _id: existingDoc._id,
        _rev: existingDoc._rev,
        type: 'tarif_prepaid',
        ...updatedTarifPrepaid
      };

      await db.put(doc);
      
      // Update local state
      const index = daftarTarifPrepaid.value.findIndex(t => t.id === tarifPrepaidData.id);
      if (index !== -1) {
        daftarTarifPrepaid.value[index] = updatedTarifPrepaid;
      }
      
      $q.notify({
        type: 'positive',
        message: 'Tarif prepaid berhasil diperbarui',
        icon: 'check'
      });

      return updatedTarifPrepaid;
    } catch (error) {
      console.error('Error editing tarif prepaid:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal memperbarui tarif prepaid',
        icon: 'error'
      });
      throw error;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteTarifPrepaid = async (id: string) => {
    try {
      isLoading.value = true;
      
      // Get existing doc for revision
      const existingDoc = await db.get(id);
      
      // Soft delete by setting status to 0 - preserve _id and _rev
      const updatedDoc = {
        ...existingDoc,
        status: 0,
        updated_at: new Date().toISOString()
      };

      await db.put(updatedDoc);
      
      // Update local state
      const index = daftarTarifPrepaid.value.findIndex(t => t.id === id);
      if (index !== -1) {
        daftarTarifPrepaid.value[index].status = 0;
      }
      
      $q.notify({
        type: 'positive',
        message: 'Tarif prepaid berhasil dihapus',
        icon: 'check'
      });

    } catch (error) {
      console.error('Error deleting tarif prepaid:', error);
      $q.notify({
        type: 'negative',
        message: 'Gagal menghapus tarif prepaid',
        icon: 'error'
      });
      throw error;
    } finally {
      isLoading.value = false;
    }
  };

  const loadTarifPrepaidFromLocal = async () => {
    try {
      isLoading.value = true;
      
      const result = await db.allDocs({
        include_docs: true,
        startkey: 'TPR',
        endkey: 'TPR\ufff0'
      });

      const tarifPrepaidList: TarifPrepaid[] = result.rows
        .map(row => row.doc)
        .filter(doc => doc && (doc as any).type === 'tarif_prepaid')
        .map(doc => {
          const { _id, _rev, type, ...tarifPrepaidData } = doc as any;
          return tarifPrepaidData as TarifPrepaid;
        });

      daftarTarifPrepaid.value = tarifPrepaidList;
      console.log('Loaded tarif prepaid from local:', tarifPrepaidList.length);
      
    } catch (error) {
      console.error('Error loading tarif prepaid from local:', error);
    } finally {
      isLoading.value = false;
    }
  };

  const getTarifPrepaidByMobil = (id_mobil: string): TarifPrepaid | undefined => {
    return activeTarifPrepaid.value.find(t => t.id_mobil === id_mobil);
  };

  const getTarifByMobil = (id_mobil: string): Tarif | undefined => {
    return activeTarif.value.find(t => t.id_mobil === id_mobil && t.jam_ke === 1);
  };

  const calculatePrepaidFee = (
    id_mobil: string, 
    durationMinutes: number
  ): { fee: number; isPrepaidActive: boolean; extraFee?: number } => {
    const prepaidTarif = getTarifPrepaidByMobil(id_mobil);
    
    if (!prepaidTarif) {
      return { fee: 0, isPrepaidActive: false };
    }

    const durationHours = Math.ceil(durationMinutes / 60);
    const prepaidHours = prepaidTarif.durasi_berlaku;

    // Jika berlaku tanpa batas waktu
    if (prepaidTarif.berlaku_tanpa_batas) {
      return { 
        fee: prepaidTarif.tarif_prepaid, 
        isPrepaidActive: true 
      };
    }

    // Jika masih dalam durasi prepaid
    if (durationHours <= prepaidHours) {
      return { 
        fee: prepaidTarif.tarif_prepaid, 
        isPrepaidActive: true 
      };
    }

    // Jika melebihi durasi prepaid
    const extraHours = durationHours - prepaidHours;
    const extraFee = extraHours * (prepaidTarif.tarif_tambahan || 0);
    
    return { 
      fee: prepaidTarif.tarif_prepaid + extraFee, 
      isPrepaidActive: true,
      extraFee: extraFee
    };
  };

  const calculateParkingFee = (
    id_mobil: string,
    entryTime: string,
    exitTime: string
  ): { totalFee: number; details: any } => {
    // Check for prepaid tariff first
    const prepaidTarif = getTarifPrepaidByMobil(id_mobil);
    
    if (prepaidTarif) {
      // Calculate duration in minutes
      const entry = new Date(entryTime);
      const exit = new Date(exitTime);
      const durationMinutes = Math.ceil((exit.getTime() - entry.getTime()) / (1000 * 60));
      
      const prepaidResult = calculatePrepaidFee(id_mobil, durationMinutes);
      
      return {
        totalFee: prepaidResult.fee,
        details: {
          type: 'prepaid',
          prepaidAmount: prepaidTarif.tarif_prepaid,
          extraFee: prepaidResult.extraFee || 0,
          durationMinutes: durationMinutes,
          durationHours: Math.ceil(durationMinutes / 60)
        }
      };
    }
    
    // Fallback to regular tariff calculation
    const regularTarif = getTarifByMobil(id_mobil);
    
    if (!regularTarif) {
      return { totalFee: 0, details: { type: 'regular', error: 'No tariff found' } };
    }
    
    // Simple regular tariff calculation (jam pertama)
    return {
      totalFee: regularTarif.tarif,
      details: {
        type: 'regular',
        firstHourFee: regularTarif.tarif,
        vehicleId: id_mobil
      }
    };
  };

  return {
    // State
    daftarTarif,
    daftarTarifInap,
    daftarTarifMember,
    daftarTarifPrepaid,
    daftarTarifStiker,
    isLoading,
    
    // Computed
    activeTarif,
    activeTarifInap,
    activeTarifMember,
    activeTarifPrepaid,
    activeTarifStiker,
    tarifForSelect,
    
    // Methods
    initializeDesignDocs,
    addTarif,
    editTarif,
    deleteTarif,
    loadTarifFromLocal,
    addTarifInap,
    loadTarifInapFromLocal,
    addTarifMember,
    loadTarifMemberFromLocal,
    addTarifStiker,
    loadTarifStikerFromLocal,
    
    // Tarif Prepaid Methods  
    addTarifPrepaid,
    editTarifPrepaid,
    deleteTarifPrepaid,
    loadTarifPrepaidFromLocal,
    getTarifPrepaidByMobil,
    getTarifByMobil,
    calculatePrepaidFee,
    calculateParkingFee
  };
});
