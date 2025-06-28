import PouchDB from 'pouchdb'

// Transaction interface based on entry gate schema
export interface ParkingTransaction {
  _id: string
  _rev?: string
  type: 'parking_transaction'
  id: string
  no_pol: string
  id_kendaraan: number
  status: number // 0 = entered, 1 = exited
  id_pintu_masuk: string
  waktu_masuk: string
  waktu_keluar?: string
  id_op_masuk: string
  id_shift_masuk: string
  kategori: string
  status_transaksi: string
  jenis_system: string
  tanggal: string
  pic_driver_masuk: string
  pic_no_pol_masuk: string
  pic_driver_keluar?: string
  pic_no_pol_keluar?: string
  sinkron: number
  upload: number
  manual: number
  veri_check: number
  bayar_masuk: number
  bayar_keluar?: number
  id_pintu_keluar?: string
  id_op_keluar?: string
  id_shift_keluar?: string
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
    this.db = new PouchDB('exit_gate_db')
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

  // Find transaction by barcode (using transaction id)
  async findTransactionByBarcode(barcode: string): Promise<ParkingTransaction | null> {
    try {
      const result = await this.db.allDocs({
        include_docs: true,
        startkey: 'transaction_',
        endkey: 'transaction_\ufff0'
      })

      const transaction = result.rows
        .map(row => row.doc as ParkingTransaction)
        .find(doc => 
          doc?.type === 'parking_transaction' && 
          doc?.id === barcode &&
          doc?.status === 0 // Only find transactions that haven't exited yet
        )

      return transaction || null
    } catch (error) {
      console.error('Error finding transaction by barcode:', error)
      return null
    }
  }

  // Update transaction status on exit
  async exitTransaction(transactionId: string, exitData: {
    waktu_keluar: string
    bayar_keluar?: number
    id_pintu_keluar?: string
    id_op_keluar?: string
    id_shift_keluar?: string
    pic_driver_keluar?: string
    pic_no_pol_keluar?: string
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
      cctv_enabled: false,
      cctv_url: '',
      image_quality: 0.8,
      capture_timeout: 5000,
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
          if (!doc || doc.type !== 'parking_transaction' || doc.status !== 1 || !doc.waktu_keluar) {
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
      
      // Initialize multiple remote databases
      this.remoteTransactionsDb = new PouchDB(`${baseUrl}/transactions`)
      this.remoteKendaraanDb = new PouchDB(`${baseUrl}/kendaraan`)
      this.remoteTarifDb = new PouchDB(`${baseUrl}/tarif`)
      
      // Test connections
      await Promise.all([
        this.remoteTransactionsDb.info(),
        this.remoteKendaraanDb.info(),
        this.remoteTarifDb.info()
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
        filter: (doc) => doc.type === 'parking_transaction'
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
          return doc.type === 'parking_transaction'
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
    } catch (error) {
      console.error('Error cleaning up remote databases:', error)
    }
  }
}

export const databaseService = new DatabaseService()
