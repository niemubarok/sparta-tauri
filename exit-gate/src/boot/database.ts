import { boot } from 'quasar/wrappers'
import { databaseService } from '../services/database'
import { audioService } from '../services/audio-service'

export default boot(async ({ app }) => {
  try {
    // Initialize the database service
    await databaseService.initialize()
    console.log('Database service initialized successfully')
    
    // Audio service initializes automatically
    console.log('Audio service ready')
  } catch (error) {
    console.error('Failed to initialize services:', error)
  }
})
