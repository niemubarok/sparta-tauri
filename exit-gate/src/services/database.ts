import PouchDB from 'pouchdb'

// Transaction interface based on entry gate schema - supports both parking_transaction and member_entry
export interface ParkingTransaction {
  _id: string
  _rev?: string
  type: 'parking_transaction' | 'member_entry'
  
  // Common fields
  status: number // 0 = entered, 1 = exited
  
  // Regular parking transaction fields
  id?: string
  no_pol?: string
  id_kendaraan?: number
  id_pintu_masuk?: string
  waktu_masuk?: string
  waktu_keluar?: string
  id_op_masuk?: string
  id_shift_masuk?: string
  kategori?: string
  status_transaksi?: string
  jenis_system?: string
  tanggal?: string
  pic_driver_masuk?: string
  pic_no_pol_masuk?: string
  pic_driver_keluar?: string
  pic_no_pol_keluar?: string
  sinkron?: number
  upload?: number
  manual?: number
  veri_check?: number
  bayar_masuk?: number
  bayar_keluar?: number
  id_pintu_keluar?: string
  id_op_keluar?: string
  id_shift_keluar?: string
  no_barcode?: string  // Add barcode field for exit gate compatibility
  entry_pic?: string   // Add simplified image fields like entry gate
  exit_pic?: string
  
  // Member entry specific fields
  member_id?: string
  name?: string
  card_number?: string
  plat_nomor?: string // Alternative to no_pol for member entries
  entry_time?: string // Alternative to waktu_masuk for member entries
  vehicle?: {
    type: { label: string; value: string }
    license_plate: string
    brand?: string
    model?: string
    color?: string
    year?: string
  }
  jenis_kendaraan?: {
    id: number
    label: string
  }
  membership_type_id?: string
  created_by?: string
  lokasi?: string
  is_member?: boolean
  tarif?: number
  payment_status?: string
  has_image?: boolean
  
  created_at?: string
  updated_at?: string
}

export interface GateSettings {
  _id: string
  _rev?: string
  type: 'gate_settings'
  serial_port: string
  baud_rate: number
  gate_timeout: number // seconds to auto-close gate
  camera_enabled: boolean
  webcam_enabled: boolean
  cctv_enabled: boolean
  cctv_url?: string
  image_quality: number
  capture_timeout: number
  server_url?: string
  // CCTV Camera configuration
  plate_camera_ip?: string
  plate_camera_username?: string
  plate_camera_password?: string
  plate_camera_snapshot_path?: string
  plate_camera_full_url?: string // Complete snapshot URL for advanced cameras
  driver_camera_ip?: string
  driver_camera_username?: string
  driver_camera_password?: string
  driver_camera_snapshot_path?: string
  driver_camera_full_url?: string // Complete snapshot URL for advanced cameras
  // GPIO configuration for Raspberry Pi
  gpio_pin?: number
  gpio_active_high?: boolean
  control_mode?: 'serial' | 'gpio' // 'serial' for normal mode, 'gpio' for Raspberry Pi
  power_gpio_pin?: number // Pin for power control
  power_gpio_enabled?: boolean // Enable power GPIO
  busy_gpio_pin?: number // Pin for busy indicator
  busy_gpio_enabled?: boolean // Enable busy GPIO
  live_gpio_pin?: number // Pin for live indicator
  live_gpio_enabled?: boolean // Enable live GPIO  
  gate_trigger_gpio_pin?: number // Pin for gate trigger
  gate_trigger_gpio_enabled?: boolean // Enable gate trigger GPIO
  gpio_pulse_duration?: number // Duration in milliseconds to keep GPIO active
  // Remote sync settings
  sync_config?: SyncConfig
  created_at: string
  updated_at: string
}

export interface VehicleType {
  _id: string
  _rev?: string
  type: 'vehicle_type'
  id_kendaraan: number
  nama_kendaraan: string
  tarif: number
  created_at: string
  updated_at: string
}

// Sync configuration interface
export interface SyncConfig {
  remote_url: string // Base URL tanpa nama database, contoh: http://localhost:5984
  username?: string
  password?: string
  auto_sync: boolean
  sync_interval: number // minutes
  retry_attempts: number
  continuous: boolean
}

export interface SyncStatus {
  connected: boolean
  last_sync: string | null
  sync_active: boolean
  error_message: string | null
  docs_synced: number
  pending_changes: number
}

class DatabaseService {
  private db: PouchDB.Database
  private remoteTransactionsDb: PouchDB.Database | null = null
  private remoteKendaraanDb: PouchDB.Database | null = null
  private remoteTarifDb: PouchDB.Database | null = null
  private remotePetugasDb: PouchDB.Database | null = null
  private syncHandlers: Map<string, PouchDB.Replication.Sync<{}>> = new Map()
  private syncStatus: SyncStatus = {
    connected: false,
    last_sync: null,
    sync_active: false,
    error_message: null,
    docs_synced: 0,
    pending_changes: 0
  }
  private syncStatusListeners: ((status: SyncStatus) => void)[] = []
  private syncTimer: number | null = null

  constructor() {
    // Use same database name as entry gate for consistency
    this.db = new PouchDB('transactions')
  }

  // Initialize database with default settings
  async initialize() {
    try {
      // Check if settings exist
      const settings = await this.getSettings()
      if (!settings) {
        await this.createDefaultSettings()
      }
      
      // Initialize remote sync if configured
      if (settings?.sync_config?.remote_url && 
          settings.sync_config.remote_url.trim() !== '' && 
          settings.sync_config.auto_sync) {
        await this.initializeRemoteSync(settings.sync_config)
      }
    } catch (error) {
      console.error('Failed to initialize database:', error)
    }
  }

  // Find transaction by barcode (using transaction id) - align with entry gate method
  async findTransactionByBarcode(barcode: string): Promise<ParkingTransaction | null> {
    // console.log("🚀 ~ DatabaseService ~ result ~ barcode:", barcode)
    try {
      // Try to get by transaction ID (barcode as suffix)
      try {
        const doc = await this.db.get(`transaction_${barcode}`) as ParkingTransaction
        console.log("🚀 ~ DatabaseService ~ findTransactionByBarcode ~ doc:", doc)
        if (
          doc && 
          doc.status === 0 && 
          (doc.type === 'parking_transaction' || doc.type === 'member_entry')
        ) {
          return doc
        }
      } catch (error) {
        console.log("🚀 ~ DatabaseService ~ findTransactionByBarcode ~ error:", error)
        // Not found by direct ID, continue
      }

      // Try to find by scanning all transactions if direct lookup fails
      // This handles cases where barcode might be in no_barcode field
      try {
        const result = await this.db.allDocs({
          include_docs: true,
          startkey: 'transaction_',
          endkey: 'transaction_\ufff0'
        })

        const transaction = result.rows
          .map(row => row.doc as ParkingTransaction)
          .find(doc => 
            doc && 
            doc.status === 0 && 
            (doc.type === 'parking_transaction' || doc.type === 'member_entry') &&
            (doc._id === `transaction_${barcode}` || doc.no_barcode === barcode)
          )

        return transaction || null
      } catch (error) {
        console.log("🚀 ~ DatabaseService ~ findTransactionByBarcode ~ scan error:", error)
        // Continue to return null
      }

      return null
    } catch (error) {
      console.error('Error finding transaction by barcode:', error)
      return null
    }
  }

  // Find transaction by plate number - additional method like entry gate
  async findTransactionByPlate(plateNumber: string): Promise<ParkingTransaction | null> {
    try {
      const result = await this.db.allDocs({
        include_docs: true,
        startkey: 'transaction_',
        endkey: 'transaction_\ufff0'
      })

      const transaction = result.rows
        .map(row => row.doc as ParkingTransaction)
        .find(doc => 
          doc && 
          (doc.type === 'parking_transaction' || doc.type === 'member_entry') && 
          (
            doc.no_pol?.toUpperCase() === plateNumber.toUpperCase() ||
            doc.plat_nomor?.toUpperCase() === plateNumber.toUpperCase() ||
            doc.vehicle?.license_plate?.toUpperCase() === plateNumber.toUpperCase()
          ) &&
          doc.status === 0 // Only find transactions that haven't exited yet
        )

      return transaction || null
    } catch (error) {
      console.error('Error finding transaction by plate:', error)
      return null
    }
  }

  // Update transaction status on exit - align with entry gate method
  async exitTransaction(transactionId: string, exitData: {
    waktu_keluar: string
    bayar_keluar?: number
    id_pintu_keluar?: string
    id_op_keluar?: string
    id_shift_keluar?: string
    pic_driver_keluar?: string
    pic_no_pol_keluar?: string
    exit_pic?: string  // Add support for simplified exit image
  }): Promise<boolean> {
    try {
      const doc = await this.db.get(transactionId) as ParkingTransaction
      
      const updatedDoc: ParkingTransaction = {
        ...doc,
        ...exitData,
        status: 1, // Mark as exited
        status_transaksi: "1", // Update status transaksi juga
        updated_at: new Date().toISOString()
      }

      await this.db.put(updatedDoc)
      return true
    } catch (error) {
      console.error('Error updating transaction:', error)
      return false
    }
  }

  // Get gate settings
  async getSettings(): Promise<GateSettings | null> {
    try {
      const doc = await this.db.get('settings_gate') as GateSettings
      return doc
    } catch (error) {
      if ((error as any)?.name === 'not_found') {
        return null
      }
      console.error('Error getting settings:', error)
      return null
    }
  }

  // Update gate settings with conflict resolution
  async updateSettings(settings: Partial<GateSettings>): Promise<boolean> {
    const maxRetries = 3
    let retryCount = 0
    
    while (retryCount < maxRetries) {
      try {
        let doc: GateSettings
        
        try {
          doc = await this.db.get('settings_gate') as GateSettings
        } catch (error) {
          if ((error as any)?.name === 'not_found') {
            doc = await this.createDefaultSettings()
          } else {
            throw error
          }
        }

        const updatedDoc: GateSettings = {
          ...doc,
          ...settings,
          updated_at: new Date().toISOString()
        }

        await this.db.put(updatedDoc)
        return true
      } catch (error) {
        if ((error as any)?.name === 'conflict' && retryCount < maxRetries - 1) {
          // Document was updated by another process, retry with fresh copy
          retryCount++
          console.log(`Settings update conflict, retrying (${retryCount}/${maxRetries})...`)
          // Small delay before retry
          await new Promise(resolve => setTimeout(resolve, 100))
          continue
        }
        console.error('Error updating settings:', error)
        return false
      }
    }
    
    return false
  }

  // Create default settings
  private async createDefaultSettings(): Promise<GateSettings> {
    const defaultSettings: GateSettings = {
      _id: 'settings_gate',
      type: 'gate_settings',
      serial_port: 'COM1',
      baud_rate: 9600,
      gate_timeout: 10,
      camera_enabled: false,
      webcam_enabled: true,
      cctv_enabled: true, // Enable CCTV by default for exit gate
      cctv_url: '',
      image_quality: 0.8,
      capture_timeout: 5000,
      // Default CCTV camera settings - use your URL format
      plate_camera_full_url: 'http://username:password@192.168.1.11/ISAPI/Streaming/channels/101/picture',
      plate_camera_ip: '192.168.1.11', // Backup for component-based URL
      plate_camera_username: 'username',
      plate_camera_password: 'password',
      plate_camera_snapshot_path: 'ISAPI/Streaming/channels/101/picture',
      driver_camera_full_url: 'http://username:password@192.168.1.12/ISAPI/Streaming/channels/101/picture',
      driver_camera_ip: '192.168.1.12',
      driver_camera_username: 'username',
      driver_camera_password: 'password',
      driver_camera_snapshot_path: 'ISAPI/Streaming/channels/101/picture',
      sync_config: {
        remote_url: 'http://localhost:5984', // Base URL tanpa nama database
        auto_sync: false,
        sync_interval: 15, // 15 minutes
        retry_attempts: 3,
        continuous: false
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }

    await this.db.put(defaultSettings)
    return defaultSettings
  }

  // Get vehicle types for exit fee calculation
  async getVehicleTypes(): Promise<VehicleType[]> {
    try {
      const result = await this.db.allDocs({
        include_docs: true,
        startkey: 'vehicle_type_',
        endkey: 'vehicle_type_\ufff0'
      })

      return result.rows
        .map(row => row.doc as VehicleType)
        .filter(doc => doc?.type === 'vehicle_type')
    } catch (error) {
      console.error('Error getting vehicle types:', error)
      return []
    }
  }

  // Calculate parking fee based on duration and vehicle type - align with entry gate logic
  async calculateParkingFee(transaction: ParkingTransaction, exitTime: string = new Date().toISOString()): Promise<number> {
    try {
      // Get entry time from either waktu_masuk (parking_transaction) or entry_time (member_entry)
      const entryTimeString = transaction.waktu_masuk || transaction.entry_time
      if (!entryTimeString) {
        console.error('No entry time found in transaction')
        return 0
      }
      
      const entryTime = new Date(entryTimeString)
      const exit = new Date(exitTime)
      
      // Calculate duration in hours (minimum 1 hour)
      const durationMs = exit.getTime() - entryTime.getTime()
      const durationHours = Math.max(1, Math.ceil(durationMs / (1000 * 60 * 60)))
      
      // For member entries, check if tarif is already set (could be 0 for free parking)
      if (transaction.type === 'member_entry' && transaction.tarif !== undefined) {
        const totalFee = durationHours * transaction.tarif
        
        console.log(`Member parking fee calculation:`, {
          plateNumber: transaction.plat_nomor || transaction.no_pol,
          memberName: transaction.name,
          entryTime: entryTime.toISOString(),
          exitTime,
          durationHours,
          memberRate: transaction.tarif,
          totalFee
        })
        
        return totalFee
      }
      
      // For regular parking transactions, use vehicle type tariff
      const vehicleTypes = await this.getVehicleTypes()
      const vehicleTypeId = transaction.id_kendaraan || transaction.jenis_kendaraan?.id
      const vehicleType = vehicleTypes.find((vt: VehicleType) => vt.id_kendaraan === vehicleTypeId)
      const hourlyRate = vehicleType?.tarif || 5000 // Default 5000 IDR per hour
      
      // Basic calculation: hours * hourly rate
      const totalFee = durationHours * hourlyRate
      
      console.log(`Parking fee calculation:`, {
        plateNumber: transaction.no_pol || transaction.plat_nomor,
        entryTime: entryTime.toISOString(),
        exitTime,
        durationHours,
        hourlyRate,
        totalFee
      })
      
      return totalFee
    } catch (error) {
      console.error('Error calculating parking fee:', error)
      return 0
    }
  }

  // Get today's exit statistics
  async getTodayExitStats() {
    try {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const endOfDay = new Date()
      endOfDay.setHours(23, 59, 59, 999)

      const result = await this.db.allDocs({
        include_docs: true,
        startkey: 'transaction_',
        endkey: 'transaction_\ufff0'
      })

      const todayExits = result.rows
        .map(row => row.doc as ParkingTransaction)
        .filter(doc => {
          if (!doc || (doc.type !== 'parking_transaction' && doc.type !== 'member_entry') || doc.status !== 1 || !doc.waktu_keluar) {
            return false
          }
          
          const exitDate = new Date(doc.waktu_keluar)
          return exitDate >= today && exitDate <= endOfDay
        })

      return {
        totalExits: todayExits.length,
        totalRevenue: todayExits.reduce((sum, t) => sum + (t.bayar_keluar || 0), 0),
        transactions: todayExits
      }
    } catch (error) {
      console.error('Error getting today exit stats:', error)
      return {
        totalExits: 0,
        totalRevenue: 0,
        transactions: []
      }
    }
  }

  // Remote sync methods
  async initializeRemoteSync(config: SyncConfig): Promise<boolean> {
    try {
      // Stop existing sync
      await this.stopSync()
      
      // Validate base URL
      if (!config.remote_url || config.remote_url.trim() === '') {
        throw new Error('Remote URL is required')
      }
      
      let baseUrl = config.remote_url.trim()
      
      // Ensure URL starts with http:// or https://
      if (!baseUrl.startsWith('http://') && !baseUrl.startsWith('https://')) {
        baseUrl = 'http://' + baseUrl
      }
      
      // Remove trailing slash if exists
      if (baseUrl.endsWith('/')) {
        baseUrl = baseUrl.slice(0, -1)
      }
      
      // Configure authentication if provided
      if (config.username && config.password) {
        const url = new URL(baseUrl)
        url.username = config.username
        url.password = config.password
        baseUrl = url.toString()
      }
      
      // Initialize multiple remote databases - align with entry gate structure
      this.remoteTransactionsDb = new PouchDB(`${baseUrl}/transactions`)
      this.remoteKendaraanDb = new PouchDB(`${baseUrl}/kendaraan`)
      this.remoteTarifDb = new PouchDB(`${baseUrl}/tarif`)
      this.remotePetugasDb = new PouchDB(`${baseUrl}/petugas`)
      
      // Test connections
      await Promise.all([
        this.remoteTransactionsDb.info(),
        this.remoteKendaraanDb.info(),
        this.remoteTarifDb.info(),
        this.remotePetugasDb.info()
      ])
      
      // Start sync for all databases
      return await this.startSync(config)
    } catch (error) {
      console.error('Failed to initialize remote sync:', error)
      this.updateSyncStatus({
        connected: false,
        error_message: error instanceof Error ? error.message : 'Unknown sync error'
      })
      return false
    }
  }

  async startSync(config: SyncConfig): Promise<boolean> {
    if (!this.remoteTransactionsDb) {
      console.error('Remote databases not configured')
      return false
    }

    try {
      // Clear existing sync handlers
      this.syncHandlers.clear()

      // Sync transactions database
      const transactionSyncOptions: PouchDB.Replication.SyncOptions = {
        live: config.continuous,
        retry: true,
        back_off_function: (delay) => Math.min(delay * 2, 10000),
        filter: (doc) => doc.type === 'parking_transaction' || doc.type === 'member_entry'
      }

      const transactionSync = this.db.sync(this.remoteTransactionsDb, transactionSyncOptions)
        .on('change', (info) => {
          console.log('Transaction sync change:', info)
          this.updateSyncStatus({
            docs_synced: this.syncStatus.docs_synced + (info.change?.docs_written || 0),
            last_sync: new Date().toISOString(),
            sync_active: true
          })
        })
        .on('paused', () => {
          console.log('Transaction sync paused')
          this.updateSyncStatus({
            sync_active: false,
            last_sync: new Date().toISOString()
          })
        })
        .on('active', () => {
          console.log('Transaction sync active')
          this.updateSyncStatus({
            sync_active: true,
            connected: true,
            error_message: null
          })
        })
        .on('error', (err: any) => {
          console.error('Transaction sync error:', err)
          this.updateSyncStatus({
            connected: false,
            sync_active: false,
            error_message: (err as Error)?.message || 'Transaction sync error'
          })
        })
        .on('complete', (info) => {
          console.log('Transaction sync complete:', info)
          this.updateSyncStatus({
            sync_active: false,
            last_sync: new Date().toISOString()
          })
        })

      this.syncHandlers.set('transactions', transactionSync)

      // Sync vehicle types from kendaraan database
      if (this.remoteKendaraanDb) {
        const kendaraanSync = this.db.sync(this.remoteKendaraanDb, {
          live: config.continuous,
          retry: true,
          back_off_function: (delay) => Math.min(delay * 2, 10000)
        })
        this.syncHandlers.set('kendaraan', kendaraanSync)
      }

      // Sync tariffs from tarif database  
      if (this.remoteTarifDb) {
        const tarifSync = this.db.sync(this.remoteTarifDb, {
          live: config.continuous,
          retry: true,
          back_off_function: (delay) => Math.min(delay * 2, 10000)
        })
        this.syncHandlers.set('tarif', tarifSync)
      }

      // Sync petugas database
      if (this.remotePetugasDb) {
        const petugasSync = this.db.sync(this.remotePetugasDb, {
          live: config.continuous,
          retry: true,
          back_off_function: (delay) => Math.min(delay * 2, 10000)
        })
        this.syncHandlers.set('petugas', petugasSync)
      }

      // Set up periodic sync if not continuous
      if (!config.continuous && config.sync_interval > 0) {
        this.setupPeriodicSync(config)
      }

      this.updateSyncStatus({
        connected: true,
        sync_active: true,
        error_message: null
      })

      return true
    } catch (error) {
      console.error('Failed to start sync:', error)
      this.updateSyncStatus({
        connected: false,
        error_message: error instanceof Error ? error.message : 'Failed to start sync'
      })
      return false
    }
  }

  async stopSync(): Promise<void> {
    // Cancel all sync handlers
    this.syncHandlers.forEach((handler, name) => {
      console.log(`Stopping sync for ${name}`)
      handler.cancel()
    })
    this.syncHandlers.clear()
    
    if (this.syncTimer) {
      clearInterval(this.syncTimer)
      this.syncTimer = null
    }
    
    this.updateSyncStatus({
      connected: false,
      sync_active: false
    })
  }

  private setupPeriodicSync(config: SyncConfig) {
    if (this.syncTimer) {
      clearInterval(this.syncTimer)
    }
    
    this.syncTimer = window.setInterval(async () => {
      if (this.remoteTransactionsDb && !this.syncStatus.sync_active) {
        try {
          console.log('Starting periodic sync...')
          await this.performOneTimeSync()
        } catch (error) {
          console.error('Periodic sync failed:', error)
        }
      }
    }, config.sync_interval * 60 * 1000) // Convert minutes to milliseconds
  }

  private async performOneTimeSync(): Promise<void> {
    if (!this.remoteTransactionsDb) return
    
    try {
      this.updateSyncStatus({ sync_active: true })
      
      const result = await this.db.sync(this.remoteTransactionsDb, {
        filter: (doc) => {
          return doc.type === 'parking_transaction' || doc.type === 'member_entry'
        }
      })
      
      this.updateSyncStatus({
        docs_synced: this.syncStatus.docs_synced + (result.pull?.docs_written || 0) + (result.push?.docs_written || 0),
        last_sync: new Date().toISOString(),
        sync_active: false,
        connected: true,
        error_message: null
      })
    } catch (error) {
      this.updateSyncStatus({
        sync_active: false,
        error_message: error instanceof Error ? error.message : 'Sync failed'
      })
      throw error
    }
  }

  // Manual sync trigger
  async triggerSync(): Promise<boolean> {
    try {
      if (!this.remoteTransactionsDb) {
        throw new Error('Remote database not configured')
      }
      
      await this.performOneTimeSync()
      return true
    } catch (error) {
      console.error('Manual sync failed:', error)
      return false
    }
  }

  // Update sync configuration with conflict resolution
  async updateSyncConfig(config: Partial<SyncConfig>): Promise<boolean> {
    try {
      const settings = await this.getSettings()
      if (!settings) {
        throw new Error('Settings not found')
      }
      
      const currentSyncConfig = settings.sync_config || {
        remote_url: '',
        auto_sync: false,
        sync_interval: 15,
        retry_attempts: 3,
        continuous: false
      }
      
      const updatedSyncConfig: SyncConfig = {
        ...currentSyncConfig,
        ...config
      }
      
      // Only update sync_config, not the entire settings object
      const success = await this.updateSettings({
        sync_config: updatedSyncConfig
      })
      
      if (success && updatedSyncConfig.remote_url) {
        // Reinitialize sync with new config
        if (updatedSyncConfig.auto_sync) {
          await this.initializeRemoteSync(updatedSyncConfig)
        } else {
          await this.stopSync()
        }
      }
      
      return success
    } catch (error) {
      console.error('Failed to update sync config:', error)
      return false
    }
  }

  // Sync status management
  private updateSyncStatus(updates: Partial<SyncStatus>) {
    this.syncStatus = { ...this.syncStatus, ...updates }
    this.syncStatusListeners.forEach(listener => listener(this.syncStatus))
  }

  getSyncStatus(): SyncStatus {
    return { ...this.syncStatus }
  }

  addSyncStatusListener(callback: (status: SyncStatus) => void) {
    this.syncStatusListeners.push(callback)
  }

  removeSyncStatusListener(callback: (status: SyncStatus) => void) {
    const index = this.syncStatusListeners.indexOf(callback)
    if (index > -1) {
      this.syncStatusListeners.splice(index, 1)
    }
  }

  // Get sync conflicts (if any)
  async getSyncConflicts(): Promise<any[]> {
    try {
      const result = await this.db.allDocs({
        include_docs: true,
        conflicts: true
      })
      
      return result.rows
        .filter(row => row.doc?._conflicts)
        .map(row => row.doc)
    } catch (error) {
      console.error('Error getting sync conflicts:', error)
      return []
    }
  }

  // Resolve sync conflict by choosing local version
  async resolveConflictLocal(docId: string): Promise<boolean> {
    try {
      const doc = await this.db.get(docId, { conflicts: true })
      if (!doc._conflicts) return true
      
      // Remove conflicts by deleting conflicted revisions
      for (const conflictRev of doc._conflicts) {
        await this.db.remove(docId, conflictRev)
      }
      
      return true
    } catch (error) {
      console.error('Error resolving conflict:', error)
      return false
    }
  }

  // Get active parking transactions - useful for exit gate statistics
  async getActiveTransactions(): Promise<ParkingTransaction[]> {
    try {
      const result = await this.db.allDocs({
        include_docs: true,
        startkey: 'transaction_',
        endkey: 'transaction_\ufff0'
      })

      return result.rows
        .map(row => row.doc as ParkingTransaction)
        .filter(doc => 
          doc && 
          (doc.type === 'parking_transaction' || doc.type === 'member_entry') && 
          doc.status === 0 // Only active (not exited) transactions
        )
    } catch (error) {
      console.error('Error getting active transactions:', error)
      return []
    }
  }

  // Enhanced exit method with automatic fee calculation
  async processVehicleExit(plateNumberOrBarcode: string, operatorId?: string, gateId?: string): Promise<{
    success: boolean
    transaction?: ParkingTransaction
    fee?: number
    message?: string
  }> {
    try {
      // Try to find transaction by barcode first, then by plate number
      let transaction = await this.findTransactionByBarcode(plateNumberOrBarcode)
      
      if (!transaction) {
        transaction = await this.findTransactionByPlate(plateNumberOrBarcode)
      }
      
      if (!transaction) {
        return {
          success: false,
          message: `No active transaction found for: ${plateNumberOrBarcode}`
        }
      }
      
      const exitTime = new Date().toISOString()
      const calculatedFee = await this.calculateParkingFee(transaction, exitTime)
      
      // Update transaction with exit data
      const exitSuccess = await this.exitTransaction(transaction._id, {
        waktu_keluar: exitTime,
        bayar_keluar: calculatedFee,
        id_pintu_keluar: gateId || 'EXIT_01',
        id_op_keluar: operatorId || 'SYSTEM',
        id_shift_keluar: 'SHIFT1' // Could be dynamic based on current shift
      })
      
      if (exitSuccess) {
        // Get updated transaction
        const updatedTransaction = await this.db.get(transaction._id) as ParkingTransaction
        
        return {
          success: true,
          transaction: updatedTransaction,
          fee: calculatedFee,
          message: `Exit processed successfully for ${transaction.no_pol || transaction.plat_nomor || transaction.vehicle?.license_plate}`
        }
      } else {
        return {
          success: false,
          message: 'Failed to update transaction in database'
        }
      }
    } catch (error) {
      console.error('Error processing vehicle exit:', error)
      return {
        success: false,
        message: `Error processing exit: ${error instanceof Error ? error.message : 'Unknown error'}`
      }
    }
  }

  // Get pending changes count
  async getPendingChangesCount(): Promise<number> {
    try {
      if (!this.remoteTransactionsDb) return 0
      
      const changes = await this.db.changes({
        since: 'now',
        limit: 0
      })
      
      return (changes as any).pending || 0
    } catch (error) {
      console.error('Error getting pending changes:', error)
      return 0
    }
  }

  // Force refresh settings (useful after conflicts)
  async forceRefreshSettings(): Promise<GateSettings | null> {
    try {
      // Try to get latest version directly from database
      const doc = await this.db.get('settings_gate', { 
        revs: true,
        conflicts: true 
      }) as any
      
      // If there are conflicts, resolve them automatically
      if (doc._conflicts && doc._conflicts.length > 0) {
        console.log('Found conflicts in settings, resolving...')
        await this.resolveConflictLocal('settings_gate')
        // Get the resolved document
        return await this.db.get('settings_gate') as GateSettings
      }
      
      return doc as GateSettings
    } catch (error) {
      console.error('Error force refreshing settings:', error)
      return null
    }
  }

  // Cleanup method
  async destroy() {
    await this.stopSync()
    this.syncStatusListeners = []
    
    // Cleanup remote database connections
    try {
      this.remoteTransactionsDb = null
      this.remoteKendaraanDb = null
      this.remoteTarifDb = null
      this.remotePetugasDb = null
    } catch (error) {
      console.error('Error cleaning up remote databases:', error)
    }
  }
}

export const databaseService = new DatabaseService()
