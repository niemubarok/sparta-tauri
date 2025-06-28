export interface CameraSettings {
  webcam_enabled: boolean
  cctv_enabled: boolean
  cctv_url?: string
  image_quality: number
  capture_timeout: number
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
    capture_timeout: 5000
  }

  constructor() {
    this.initializeSettings()
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
          image_quality: dbSettings.image_quality ?? 0.8,
          capture_timeout: dbSettings.capture_timeout ?? 5000
        }
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
    if (!this.settings.cctv_enabled || !this.settings.cctv_url) {
      console.log('CCTV not configured or disabled')
      return null
    }

    try {
      // For CCTV, we'll try to fetch image from the CCTV URL
      // This assumes the CCTV provides a snapshot endpoint
      const response = await fetch(this.settings.cctv_url, {
        method: 'GET',
        timeout: this.settings.capture_timeout
      } as RequestInit)

      if (!response.ok) {
        throw new Error(`CCTV response error: ${response.status}`)
      }

      const blob = await response.blob()
      
      // Verify it's an image
      if (!blob.type.startsWith('image/')) {
        throw new Error('CCTV response is not an image')
      }

      const timestamp = new Date()
      const fileName = `cctv_${transactionId}_${timestamp.getTime()}.jpg`

      return {
        type: 'cctv',
        blob,
        timestamp,
        fileName
      }
    } catch (error) {
      console.error('Failed to capture CCTV image:', error)
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
    if (!this.settings.cctv_url) {
      return false
    }

    try {
      const testCapture = await this.captureCCTV('test')
      return !!testCapture
    } catch (error) {
      console.error('CCTV test failed:', error)
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
}

export const cameraService = new CameraService()
