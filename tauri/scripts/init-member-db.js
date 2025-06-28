#!/usr/bin/env node

/**
 * Script untuk menginisialisasi database member
 * Usage: node init-member-db.js [options]
 * Options:
 *   --reset: Reset database sebelum inisialisasi
 *   --sample: Buat data sample member
 *   --verify: Verifikasi setup database
 */

import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { readFileSync } from 'fs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

// Import fungsi inisialisasi database
const { 
  initializeMemberDatabase,
  initializeDefaultMembershipTypes,
  createSampleMembers,
  verifyMemberDatabase,
  resetMemberDatabase
} = await import('./init-member-database.ts')

// Parse command line arguments
const args = process.argv.slice(2)
const options = {
  reset: args.includes('--reset'),
  sample: args.includes('--sample'),
  verify: args.includes('--verify'),
  help: args.includes('--help') || args.includes('-h')
}

// Help text
const helpText = `
Sparta Member Database Initialization Script

Usage: node init-member-db.js [options]

Options:
  --reset     Reset database sebelum inisialisasi (hapus semua data)
  --sample    Buat data sample member untuk testing
  --verify    Verifikasi setup database setelah inisialisasi
  --help, -h  Tampilkan help ini

Examples:
  node init-member-db.js                    # Inisialisasi database normal
  node init-member-db.js --reset --sample   # Reset database dan buat sample data
  node init-member-db.js --verify           # Verifikasi database yang sudah ada
`

// Main function
async function main() {
  console.log('🎯 Sparta Member Database Initialization')
  console.log('=========================================\n')

  if (options.help) {
    console.log(helpText)
    process.exit(0)
  }

  try {
    // Reset database if requested
    if (options.reset) {
      console.log('🔄 Resetting member database...')
      await resetMemberDatabase()
      console.log('✅ Database reset completed\n')
    }

    // Initialize database
    console.log('🚀 Initializing member database...')
    const initResult = await initializeMemberDatabase()
    console.log(`✅ ${initResult.message}\n`)

    // Create sample data if requested
    if (options.sample) {
      console.log('📝 Creating sample member data...')
      const sampleMembers = await createSampleMembers()
      console.log(`✅ Created ${sampleMembers.length} sample members\n`)
    }

    // Verify database if requested
    if (options.verify) {
      console.log('🔍 Verifying database setup...')
      const verifyResult = await verifyMemberDatabase()
      console.log('✅ Database verification completed')
      console.log(`   - Membership Types: ${verifyResult.membershipTypes}`)
      console.log(`   - Members: ${verifyResult.members}\n`)
    }

    console.log('🎉 Member database initialization completed successfully!')
    
    // Display next steps
    console.log('\n📋 Next Steps:')
    console.log('1. Start your Tauri application')
    console.log('2. Navigate to Member Management page')
    console.log('3. Start adding members or use the sample data')
    console.log('4. Test member lookup in gate entry/exit')

  } catch (error) {
    console.error('❌ Error during initialization:', error.message)
    if (error.stack) {
      console.error('\nStack trace:')
      console.error(error.stack)
    }
    process.exit(1)
  }
}

// Package.json info
function displayPackageInfo() {
  try {
    const packagePath = join(__dirname, '..', 'package.json')
    const packageJson = JSON.parse(readFileSync(packagePath, 'utf8'))
    console.log(`📦 ${packageJson.name} v${packageJson.version}`)
    console.log(`📝 ${packageJson.description || 'Sparta Parking System'}\n`)
  } catch (error) {
    console.log('📦 Sparta Parking System\n')
  }
}

// Run script
displayPackageInfo()
main().catch(error => {
  console.error('💥 Unhandled error:', error)
  process.exit(1)
})
