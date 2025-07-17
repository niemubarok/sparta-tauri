/**
 * Browser console script untuk menginisialisasi database member
 * Buka browser console dan jalankan script ini
 */

// Sample membership types
const sampleMembershipTypes = [
  {
    _id: 'membership_type_vip_001',
    type: 'membership_type',
    name: 'VIP Member',
    category: 'VIP',
    price: 2000000,
    area_type: 'commercial',
    max_vehicles: 5,
    operating_hours: {
      start: '00:00',
      end: '23:59'
    },
    duration_months: 12,
    description: 'Paket VIP dengan akses premium dan fasilitas eksklusif',
    facilities: [
      'CCTV 24 Jam',
      'Keamanan',
      'Valet Parking',
      'Cuci Mobil',
      'Pengisian EV',
      'Wi-Fi Gratis',
      'Toilet Premium',
      'Mushola',
      'Area Tunggu VIP'
    ],
    benefits: [
      'Diskon 50%',
      'Priority Access',
      'Extended Hours',
      'Guest Parking',
      'Premium Support',
      'Free Valet'
    ],
    access_areas: ['A', 'B', 'C', 'VIP'],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    _id: 'membership_type_premium_001',
    type: 'membership_type',
    name: 'Premium Member',
    category: 'PREMIUM',
    price: 1200000,
    area_type: 'commercial',
    max_vehicles: 3,
    operating_hours: {
      start: '06:00',
      end: '22:00'
    },
    duration_months: 12,
    description: 'Paket premium dengan fasilitas lengkap',
    facilities: [
      'CCTV 24 Jam',
      'Keamanan',
      'Cuci Mobil',
      'Wi-Fi Gratis',
      'Toilet Bersih',
      'Mushola',
      'Area Tunggu'
    ],
    benefits: [
      'Diskon 30%',
      'Priority Access',
      'Guest Parking'
    ],
    access_areas: ['A', 'B', 'C'],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    _id: 'membership_type_regular_001',
    type: 'membership_type',
    name: 'Regular Member',
    category: 'REGULAR',
    price: 600000,
    area_type: 'residential',
    max_vehicles: 2,
    operating_hours: {
      start: '06:00',
      end: '21:00'
    },
    duration_months: 12,
    description: 'Paket reguler untuk kebutuhan harian',
    facilities: [
      'CCTV 24 Jam',
      'Keamanan',
      'Wi-Fi Gratis',
      'Toilet Bersih'
    ],
    benefits: [
      'Diskon 15%'
    ],
    access_areas: ['A', 'B'],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    _id: 'membership_type_corporate_001',
    type: 'membership_type',
    name: 'Corporate Member',
    category: 'CORPORATE',
    price: 1500000,
    area_type: 'commercial',
    max_vehicles: 10,
    operating_hours: {
      start: '05:00',
      end: '23:00'
    },
    duration_months: 12,
    description: 'Paket corporate untuk perusahaan',
    facilities: [
      'CCTV 24 Jam',
      'Keamanan',
      'Valet Parking',
      'Wi-Fi Gratis',
      'Meeting Room',
      'Area Tunggu Executive'
    ],
    benefits: [
      'Diskon 25%',
      'Bulk Parking',
      'Corporate Rate',
      'Invoice Billing'
    ],
    access_areas: ['A', 'B', 'C', 'Corporate'],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
]

// Sample members
const sampleMembers = [
  {
    _id: 'member_001',
    type: 'member',
    member_id: 'M25060001',
    name: 'John Doe',
    email: 'john.doe@example.com',
    phone: '081234567890',
    address: 'Jl. Sudirman No. 123, Jakarta Pusat',
    identity_number: '3171234567890001',
    vehicles: [
      {
        type: 'Mobil',
        license_plate: 'B1234ABC',
        brand: 'Toyota',
        model: 'Camry',
        color: 'Hitam',
        year: '2022'
      },
      {
        type: 'Motor',
        license_plate: 'B5678DEF',
        brand: 'Honda',
        model: 'PCX',
        color: 'Putih',
        year: '2023'
      }
    ],
    membership_type_id: 'membership_type_vip_001',
    start_date: '2025-01-01',
    end_date: '2025-12-31',
    payment_status: 'paid',
    notes: 'Member VIP dengan layanan premium',
    emergency_contact: {
      name: 'Jane Doe',
      phone: '081234567891',
      relationship: 'Istri'
    },
    active: 1,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    _id: 'member_002',
    type: 'member',
    member_id: 'M25060002',
    name: 'Jane Smith',
    email: 'jane.smith@example.com',
    phone: '081234567892',
    address: 'Jl. Thamrin No. 456, Jakarta Pusat',
    identity_number: '3171234567890002',
    vehicles: [
      {
        type: 'Mobil',
        license_plate: 'B9876XYZ',
        brand: 'Honda',
        model: 'Civic',
        color: 'Silver',
        year: '2023'
      }
    ],
    membership_type_id: 'membership_type_premium_001',
    start_date: '2025-02-01',
    end_date: '2026-01-31',
    payment_status: 'paid',
    notes: 'Member premium dengan fasilitas lengkap',
    emergency_contact: {
      name: 'John Smith',
      phone: '081234567893',
      relationship: 'Suami'
    },
    active: 1,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    _id: 'member_003',
    type: 'member',
    member_id: 'M25060003',
    name: 'Bob Johnson',
    email: 'bob.johnson@example.com',
    phone: '081234567894',
    address: 'Jl. Gatot Subroto No. 789, Jakarta Selatan',
    identity_number: '3171234567890003',
    vehicles: [
      {
        type: 'Motor',
        license_plate: 'B5432QWE',
        brand: 'Yamaha',
        model: 'NMAX',
        color: 'Biru',
        year: '2022'
      }
    ],
    membership_type_id: 'membership_type_regular_001',
    start_date: '2025-03-01',
    end_date: '2026-02-28',
    payment_status: 'paid',
    notes: 'Member reguler untuk kebutuhan harian',
    emergency_contact: {
      name: 'Alice Johnson',
      phone: '081234567895',
      relationship: 'Istri'
    },
    active: 1,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    _id: 'member_004',
    type: 'member',
    member_id: 'M25060004',
    name: 'PT. ABC Corp',
    email: 'admin@abccorp.com',
    phone: '021234567890',
    address: 'Jl. HR Rasuna Said No. 100, Jakarta Selatan',
    identity_number: '1234567890123456',
    vehicles: [
      {
        type: 'Mobil',
        license_plate: 'B1111AAA',
        brand: 'Toyota',
        model: 'Innova',
        color: 'Putih',
        year: '2023'
      },
      {
        type: 'Mobil',
        license_plate: 'B2222BBB',
        brand: 'Honda',
        model: 'CR-V',
        color: 'Hitam',
        year: '2023'
      },
      {
        type: 'Mobil',
        license_plate: 'B3333CCC',
        brand: 'Mitsubishi',
        model: 'Pajero',
        color: 'Silver',
        year: '2022'
      }
    ],
    membership_type_id: 'membership_type_corporate_001',
    start_date: '2025-01-15',
    end_date: '2026-01-14',
    payment_status: 'paid',
    notes: 'Membership corporate untuk kebutuhan kantor',
    emergency_contact: {
      name: 'HR Department',
      phone: '021234567891',
      relationship: 'Admin'
    },
    active: 1,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    _id: 'member_005',
    type: 'member',
    member_id: 'M25060005',
    name: 'Sarah Wilson',
    email: 'sarah.wilson@example.com',
    phone: '081234567896',
    address: 'Jl. Kuningan No. 321, Jakarta Selatan',
    identity_number: '3171234567890005',
    vehicles: [
      {
        type: 'Mobil',
        license_plate: 'B7777WWW',
        brand: 'Mazda',
        model: 'CX-5',
        color: 'Merah',
        year: '2021'
      }
    ],
    membership_type_id: 'membership_type_premium_001',
    start_date: '2024-12-01',
    end_date: '2025-11-30',
    payment_status: 'overdue',
    notes: 'Member premium dengan pembayaran terlambat',
    emergency_contact: {
      name: 'Mike Wilson',
      phone: '081234567897',
      relationship: 'Suami'
    },
    active: 1,
    createdAt: new Date('2024-12-01').toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    _id: 'member_006',
    type: 'member',
    member_id: 'M25060006',
    name: 'David Brown',
    email: 'david.brown@example.com',
    phone: '081234567898',
    address: 'Jl. Senayan No. 654, Jakarta Pusat',
    identity_number: '3171234567890006',
    vehicles: [
      {
        type: 'Motor',
        license_plate: 'B8888DDD',
        brand: 'Kawasaki',
        model: 'Ninja',
        color: 'Hijau',
        year: '2023'
      }
    ],
    membership_type_id: 'membership_type_regular_001',
    start_date: '2024-06-01',
    end_date: '2025-05-31',
    payment_status: 'paid',
    notes: 'Member reguler akan segera berakhir',
    emergency_contact: {
      name: 'Lisa Brown',
      phone: '081234567899',
      relationship: 'Istri'
    },
    active: 1,
    createdAt: new Date('2024-06-01').toISOString(),
    updatedAt: new Date().toISOString()
  }
]

// Function to initialize member database
const initializeMemberDatabase = async () => {
  console.log('🚀 Initializing member database...')
  
  try {
    // Import PouchDB from boot file
    const { remoteDbs } = await import('src/boot/pouchdb')
    
    console.log('📝 Creating membership types...')
    
    // Create membership types
    for (const type of sampleMembershipTypes) {
      try {
        await remoteDbs.membershipTypes.put(type)
        console.log(`✅ Created membership type: ${type.name}`)
      } catch (error) {
        if (error.status === 409) {
          console.log(`⚠️  Membership type already exists: ${type.name}`)
        } else {
          console.error(`❌ Error creating membership type ${type.name}:`, error.message)
        }
      }
    }
    
    console.log('👥 Creating sample members...')
    
    // Create members
    for (const member of sampleMembers) {
      try {
        await remoteDbs.members.put(member)
        console.log(`✅ Created member: ${member.name} (${member.member_id})`)
      } catch (error) {
        if (error.status === 409) {
          console.log(`⚠️  Member already exists: ${member.name}`)
        } else {
          console.error(`❌ Error creating member ${member.name}:`, error.message)
        }
      }
    }
    
    console.log('🔧 Creating database indexes...')
    
    // Create indexes for members
    const memberIndexes = [
      { fields: ['type', 'createdAt'] },
      { fields: ['type', 'name'] },
      { fields: ['type', 'member_id'] },
      { fields: ['type', 'active', 'end_date'] },
      { fields: ['type', 'membership_type_id'] },
      { fields: ['createdAt'] }
    ]
    
    for (const index of memberIndexes) {
      try {
        await remoteDbs.members.createIndex({ index })
        console.log(`✅ Created member index: ${JSON.stringify(index.fields)}`)
      } catch (error) {
        console.log(`⚠️  Member index already exists: ${JSON.stringify(index.fields)}`)
      }
    }
    
    // Create indexes for membership types
    const typeIndexes = [
      { fields: ['type', 'name'] },
      { fields: ['type', 'category'] },
      { fields: ['name'] }
    ]
    
    for (const index of typeIndexes) {
      try {
        await remoteDbs.membershipTypes.createIndex({ index })
        console.log(`✅ Created type index: ${JSON.stringify(index.fields)}`)
      } catch (error) {
        console.log(`⚠️  Type index already exists: ${JSON.stringify(index.fields)}`)
      }
    }
    
    console.log('📊 Checking database statistics...')
    
    // Get statistics
    const memberResult = await remoteDbs.members.find({
      selector: { type: 'member' }
    })
    
    const typeResult = await remoteDbs.membershipTypes.find({
      selector: { type: 'membership_type' }
    })
    
    console.log(`📈 Database initialized successfully!`)
    console.log(`   - Members: ${memberResult.docs.length}`)
    console.log(`   - Membership Types: ${typeResult.docs.length}`)
    
    // Show member summary
    console.log(`\n📋 Member Summary:`)
    memberResult.docs.forEach(member => {
      const vehicleCount = member.vehicles?.length || 0
      const endDate = new Date(member.end_date)
      const daysLeft = Math.ceil((endDate - new Date()) / (1000 * 60 * 60 * 24))
      
      console.log(`   • ${member.name} (${member.member_id})`)
      console.log(`     - Vehicles: ${vehicleCount}`)
      console.log(`     - Status: ${member.payment_status}`)
      console.log(`     - Days left: ${daysLeft > 0 ? daysLeft : 'Expired'}`)
    })
    
    console.log(`\n🎉 Member database initialization completed!`)
    
    return {
      success: true,
      memberCount: memberResult.docs.length,
      typeCount: typeResult.docs.length
    }
    
  } catch (error) {
    console.error('❌ Error initializing database:', error)
    throw error
  }
}

// Auto-expose function for console use
window.initializeMemberDatabase = initializeMemberDatabase

console.log(`
🎯 Member Database Initialization Script Loaded

To initialize the member database with sample data, run:
initializeMemberDatabase()

This will create:
- 4 membership types (VIP, Premium, Regular, Corporate)
- 6 sample members with various statuses
- All necessary database indexes

Note: This is safe to run multiple times - existing data won't be overwritten.
`)

export default initializeMemberDatabase
