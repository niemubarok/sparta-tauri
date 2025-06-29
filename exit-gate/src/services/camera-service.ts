import { invoke } from '@tauri-apps/api/core'

export interface CameraSettings {
  webcam_enabled: boolean
  cctv_enabled: boolean
  cctv_url?: string
  image_quality: number
  capture_timeout: number
  // CCTV camera settings
  plate_camera_ip?: string
  plate_camera_username?: string
  plate_camera_password?: string
  plate_camera_snapshot_path?: string
  plate_camera_full_url?: string // New field for complete URL
}

export interface CctvResponse {
  is_success: boolean
  base64?: string
  time_stamp: string
  message?: string
}

export interface CapturedImage {
  type: 'webcam' | 'cctv'
  blob: Blob
  timestamp: Date
  fileName: string
}

export interface CameraCapture {
  webcam?: CapturedImage
  cctv?: CapturedImage
  transaction_id: string
}

class CameraService {
  private webcamStream: MediaStream | null = null
  private settings: CameraSettings = {
    webcam_enabled: true,
    cctv_enabled: false,
    cctv_url: '',
    image_quality: 0.8,
    capture_timeout: 10000 // Increase default timeout to 10 seconds
  }

  constructor() {
    this.initializeSettings().then(() => {
      // Ensure CCTV settings exist in database
      this.ensureCctvSettings()
    })
  }

  private async initializeSettings() {
    try {
      const { databaseService } = await import('./database')
      const dbSettings = await databaseService.getSettings()
      
      if (dbSettings) {
        this.settings = {
          webcam_enabled: dbSettings.webcam_enabled ?? true,
          cctv_enabled: dbSettings.cctv_enabled ?? false,
          cctv_url: dbSettings.cctv_url || '',
          image_quality: (dbSettings.image_quality ?? 80) / 100, // Convert percentage to decimal (0.8)
          capture_timeout: dbSettings.capture_timeout ?? 10000, // Increase default timeout
          // CCTV camera settings
          plate_camera_ip: dbSettings.plate_camera_ip,
          plate_camera_username: dbSettings.plate_camera_username,
          plate_camera_password: dbSettings.plate_camera_password,
          plate_camera_snapshot_path: dbSettings.plate_camera_snapshot_path,
          plate_camera_full_url: dbSettings.plate_camera_full_url // New field
        }
        
        console.log('📸 Camera settings loaded:', {
          ...this.settings,
          plate_camera_password: this.settings.plate_camera_password ? '***' : undefined,
          plate_camera_full_url: this.settings.plate_camera_full_url ? 
            this.settings.plate_camera_full_url.replace(/:[^:]+@/, ':***@') : undefined
        })
      }
    } catch (error) {
      console.error('Failed to load camera settings:', error)
    }
  }

  // Initialize webcam
  async initializeWebcam(): Promise<boolean> {
    if (!this.settings.webcam_enabled) {
      console.log('Webcam is disabled in settings')
      return false
    }

    try {
      this.webcamStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'environment' // Prefer back camera if available
        }
      })
      
      console.log('Webcam initialized successfully')
      return true
    } catch (error) {
      console.error('Failed to initialize webcam:', error)
      return false
    }
  }

  // Capture image from webcam
  async captureWebcam(transactionId: string): Promise<CapturedImage | null> {
    if (!this.settings.webcam_enabled || !this.webcamStream) {
      console.log('Webcam not available or disabled')
      return null
    }

    try {
      // Create video element to capture frame
      const video = document.createElement('video')
      video.srcObject = this.webcamStream
      video.play()

      // Wait for video to be ready
      await new Promise<void>((resolve) => {
        video.onloadedmetadata = () => resolve()
      })

      // Create canvas to capture frame
      const canvas = document.createElement('canvas')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      
      const ctx = canvas.getContext('2d')
      if (!ctx) {
        throw new Error('Failed to get canvas context')
      }

      // Draw current frame to canvas
      ctx.drawImage(video, 0, 0)

      // Convert to blob
      return new Promise<CapturedImage>((resolve, reject) => {
        canvas.toBlob((blob) => {
          if (blob) {
            const timestamp = new Date()
            const fileName = `webcam_${transactionId}_${timestamp.getTime()}.jpg`
            
            resolve({
              type: 'webcam',
              blob,
              timestamp,
              fileName
            })
          } else {
            reject(new Error('Failed to create blob from canvas'))
          }
        }, 'image/jpeg', this.settings.image_quality)
      })
    } catch (error) {
      console.error('Failed to capture webcam image:', error)
      return null
    }
  }

  // Capture image from CCTV camera
  async captureCCTV(transactionId: string): Promise<CapturedImage | null> {
    if (!this.settings.cctv_enabled) {
      console.log('CCTV not enabled')
      return null
    }

    // Check if we have camera settings (either full URL or individual components)
    if (!this.settings.plate_camera_full_url && !this.settings.plate_camera_ip) {
      console.log('CCTV not configured - no URL or IP provided')
      return null
    }

    try {
      // Prepare request arguments
      const requestArgs: any = {}
      
      if (this.settings.plate_camera_full_url) {
        // Use full URL if provided
        requestArgs.full_url = this.settings.plate_camera_full_url
        console.log('🔗 Using full URL for CCTV capture')
      } else {
        // Use individual components
        requestArgs.username = this.settings.plate_camera_username || 'admin'
        requestArgs.password = this.settings.plate_camera_password || 'admin123'
        requestArgs.ip_address = this.settings.plate_camera_ip
        requestArgs.snapshot_path = this.settings.plate_camera_snapshot_path || 'Streaming/Channels/1/picture'
        console.log('🔗 Using component-based URL for CCTV capture')
      }

      console.log('📸 CCTV capture request args:', {
        ...requestArgs,
        password: requestArgs.password ? '***' : undefined,
        full_url: requestArgs.full_url ? requestArgs.full_url.replace(/:[^:]+@/, ':***@') : undefined,
        ip_address: requestArgs.ip_address || 'not set'
      })

      // Use Tauri invoke to capture image from CCTV with timeout
      console.log('🚀 Starting CCTV capture with timeout:', this.settings.capture_timeout, 'ms')
      
      const startTime = Date.now()
      const capturePromise = invoke('capture_cctv_image', { args: requestArgs }).then((result) => {
        const duration = Date.now() - startTime
        console.log('⏱️ CCTV capture completed in:', duration, 'ms')
        return result
      })
      
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => {
          const duration = Date.now() - startTime
          console.log('⏰ CCTV capture timed out after:', duration, 'ms')
          reject(new Error('CCTV capture timeout'))
        }, this.settings.capture_timeout)
      )
      
      const response: CctvResponse = await Promise.race([capturePromise, timeoutPromise]) as CctvResponse

      console.log('📸 CCTV capture response received:', {
        is_success: response?.is_success,
        has_base64: !!(response?.base64),
        base64_length: response?.base64?.length,
        message: response?.message,
        timestamp: response?.time_stamp,
        full_response: response
      })

      if (response && response.is_success && response.base64) {
        // Convert base64 to blob
        const base64Data = response.base64.replace(/^data:image\/[a-z]+;base64,/, '')
        const binaryString = atob(base64Data)
        const bytes = new Uint8Array(binaryString.length)
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i)
        }
        const blob = new Blob([bytes], { type: 'image/jpeg' })
        
        const timestamp = new Date()
        const fileName = `cctv_${transactionId}_${timestamp.getTime()}.jpg`

        console.log('✅ CCTV image captured successfully, size:', bytes.length, 'bytes')

        return {
          type: 'cctv',
          blob,
          timestamp,
          fileName
        }
      } else {
        const errorMsg = response?.message || 'Failed to capture CCTV image'
        console.error('❌ CCTV capture failed:', errorMsg)
        throw new Error(errorMsg)
      }
    } catch (error) {
      console.error('❌ Failed to capture CCTV image:', error)
      return null
    }
  }

  // Capture both webcam and CCTV images
  async captureAll(transactionId: string): Promise<CameraCapture> {
    const capture: CameraCapture = {
      transaction_id: transactionId
    }

    try {
      // Capture webcam and CCTV in parallel
      const [webcamImage, cctvImage] = await Promise.allSettled([
        this.captureWebcam(transactionId),
        this.captureCCTV(transactionId)
      ])

      if (webcamImage.status === 'fulfilled' && webcamImage.value) {
        capture.webcam = webcamImage.value
      }

      if (cctvImage.status === 'fulfilled' && cctvImage.value) {
        capture.cctv = cctvImage.value
      }

      console.log('Camera capture completed:', {
        webcam: !!capture.webcam,
        cctv: !!capture.cctv
      })

      return capture
    } catch (error) {
      console.error('Error during camera capture:', error)
      return capture
    }
  }

  // Upload captured images to server
  async uploadImages(capture: CameraCapture, serverUrl: string): Promise<boolean> {
    if (!capture.webcam && !capture.cctv) {
      console.log('No images to upload')
      return true
    }

    try {
      const formData = new FormData()
      formData.append('transaction_id', capture.transaction_id)

      if (capture.webcam) {
        formData.append('webcam', capture.webcam.blob, capture.webcam.fileName)
      }

      if (capture.cctv) {
        formData.append('cctv', capture.cctv.blob, capture.cctv.fileName)
      }

      const response = await fetch(`${serverUrl}/api/upload-transaction-images`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`)
      }

      console.log('Images uploaded successfully')
      return true
    } catch (error) {
      console.error('Failed to upload images:', error)
      return false
    }
  }

  // Update camera settings
  updateSettings(newSettings: Partial<CameraSettings>) {
    this.settings = { ...this.settings, ...newSettings }
  }

  // Get current settings
  getSettings(): CameraSettings {
    return { ...this.settings }
  }

  // Test webcam
  async testWebcam(): Promise<boolean> {
    const initialized = await this.initializeWebcam()
    if (!initialized) {
      return false
    }

    try {
      const testCapture = await this.captureWebcam('test')
      return !!testCapture
    } catch (error) {
      console.error('Webcam test failed:', error)
      return false
    }
  }

  // Test CCTV
  async testCCTV(): Promise<boolean> {
    console.log('🧪 Testing CCTV with current settings:', {
      cctv_enabled: this.settings.cctv_enabled,
      has_full_url: !!this.settings.plate_camera_full_url,
      has_ip: !!this.settings.plate_camera_ip,
      full_url_masked: this.settings.plate_camera_full_url ? 
        this.settings.plate_camera_full_url.replace(/:[^:]+@/, ':***@') : 'not set'
    })

    if (!this.settings.cctv_enabled) {
      console.log('❌ CCTV test failed: CCTV is disabled in settings')
      return false
    }

    if (!this.settings.plate_camera_full_url && !this.settings.plate_camera_ip) {
      console.log('❌ CCTV test failed: No camera URL or IP configured')
      console.log('💡 Try calling ensureCctvSettings() to update database settings')
      return false
    }

    try {
      const testCapture = await this.captureCCTV('test')
      if (testCapture) {
        console.log('✅ CCTV test successful')
        return true
      } else {
        console.log('❌ CCTV test failed: No image captured')
        return false
      }
    } catch (error) {
      console.error('❌ CCTV test failed:', error)
      return false
    }
  }

  // Stop webcam stream
  stopWebcam() {
    if (this.webcamStream) {
      this.webcamStream.getTracks().forEach(track => track.stop())
      this.webcamStream = null
      console.log('Webcam stream stopped')
    }
  }

  // Cleanup
  destroy() {
    this.stopWebcam()
  }

  // Force reload settings from database
  async reloadSettings(): Promise<void> {
    await this.initializeSettings()
  }

  // Update database settings if CCTV fields are missing
  async ensureCctvSettings(): Promise<void> {
    try {
      const { databaseService } = await import('./database')
      const dbSettings = await databaseService.getSettings()
      
      if (dbSettings) {
        // Check if CCTV fields are missing and add them with empty values
        let needsUpdate = false
        const updatedSettings = { ...dbSettings }
        
        if (dbSettings.plate_camera_ip === undefined) {
          updatedSettings.plate_camera_ip = ''
          needsUpdate = true
        }
        if (dbSettings.plate_camera_username === undefined) {
          updatedSettings.plate_camera_username = 'admin'
          needsUpdate = true
        }
        if (dbSettings.plate_camera_password === undefined) {
          updatedSettings.plate_camera_password = 'admin123'
          needsUpdate = true
        }
        if (dbSettings.plate_camera_snapshot_path === undefined) {
          updatedSettings.plate_camera_snapshot_path = 'ISAPI/Streaming/channels/101/picture'
          needsUpdate = true
        }
        if (dbSettings.plate_camera_full_url === undefined) {
          updatedSettings.plate_camera_full_url = ''
          needsUpdate = true
        }
        if (dbSettings.driver_camera_ip === undefined) {
          updatedSettings.driver_camera_ip = ''
          needsUpdate = true
        }
        if (dbSettings.driver_camera_username === undefined) {
          updatedSettings.driver_camera_username = 'admin'
          needsUpdate = true
        }
        if (dbSettings.driver_camera_password === undefined) {
          updatedSettings.driver_camera_password = 'admin123'
          needsUpdate = true
        }
        if (dbSettings.driver_camera_snapshot_path === undefined) {
          updatedSettings.driver_camera_snapshot_path = 'ISAPI/Streaming/channels/101/picture'
          needsUpdate = true
        }
        if (dbSettings.driver_camera_full_url === undefined) {
          updatedSettings.driver_camera_full_url = ''
          needsUpdate = true
        }
        
        if (needsUpdate) {
          console.log('🔧 Adding missing CCTV settings fields to database...')
          updatedSettings.updated_at = new Date().toISOString()
          
          await databaseService.updateSettings(updatedSettings)
          console.log('✅ CCTV settings fields added to database')
          
          // Reload settings after update
          await this.initializeSettings()
        } else {
          console.log('✅ CCTV settings fields already exist in database')
        }
      }
    } catch (error) {
      console.error('Failed to ensure CCTV settings:', error)
    }
  }
}

export const cameraService = new CameraService()

// Export helper function to manually update CCTV settings
export const updateCctvSettings = async () => {
  await cameraService.ensureCctvSettings()
}
