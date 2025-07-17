import { remoteDbs } from '../src/boot/pouchdb'

/**
 * Initialize member database with design documents and indexes
 */
export const initializeMemberDatabase = async () => {
  try {
    console.log('Initializing member database...')

    // Create design document for members
    const memberDesignDoc = {
      _id: '_design/members',
      views: {
        by_member_id: {
          map: `function (doc) {
            if (doc.type === 'member') {
              emit(doc.member_id, doc);
            }
          }`
        },
        by_license_plate: {
          map: `function (doc) {
            if (doc.type === 'member' && doc.vehicles) {
              for (var i = 0; i < doc.vehicles.length; i++) {
                emit(doc.vehicles[i].license_plate.toUpperCase(), doc);
              }
            }
          }`
        },
        by_phone: {
          map: `function (doc) {
            if (doc.type === 'member') {
              emit(doc.phone, doc);
            }
          }`
        },
        by_status: {
          map: `function (doc) {
            if (doc.type === 'member') {
              emit(doc.active, doc);
            }
          }`
        },
        by_membership_type: {
          map: `function (doc) {
            if (doc.type === 'member') {
              emit(doc.membership_type_id, doc);
            }
          }`
        },
        by_expiry_date: {
          map: `function (doc) {
            if (doc.type === 'member') {
              emit(doc.end_date, doc);
            }
          }`
        },
        active_members: {
          map: `function (doc) {
            if (doc.type === 'member' && doc.active === 1) {
              var today = new Date().toISOString().split('T')[0];
              if (doc.end_date >= today) {
                emit(doc.member_id, doc);
              }
            }
          }`
        },
        expiring_members: {
          map: `function (doc) {
            if (doc.type === 'member' && doc.active === 1) {
              var today = new Date();
              var endDate = new Date(doc.end_date);
              var diffTime = endDate.getTime() - today.getTime();
              var diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
              
              if (diffDays <= 30 && diffDays > 0) {
                emit(diffDays, doc);
              }
            }
          }`
        }
      }
    }

    // Create design document for membership types
    const membershipTypeDesignDoc = {
      _id: '_design/membership_types',
      views: {
        by_category: {
          map: `function (doc) {
            if (doc.type === 'membership_type') {
              emit(doc.category, doc);
            }
          }`
        },
        by_price: {
          map: `function (doc) {
            if (doc.type === 'membership_type') {
              emit(doc.price, doc);
            }
          }`
        },
        by_duration: {
          map: `function (doc) {
            if (doc.type === 'membership_type') {
              emit(doc.duration_months, doc);
            }
          }`
        },
        active_types: {
          map: `function (doc) {
            if (doc.type === 'membership_type') {
              emit(doc.name, doc);
            }
          }`
        }
      }
    }

    // Put design documents
    try {
      await remoteDbs.members.put(memberDesignDoc)
      console.log('Member design document created')
    } catch (error) {
      if (error.name !== 'conflict') {
        console.error('Error creating member design document:', error)
      }
    }

    try {
      await remoteDbs.membershipTypes.put(membershipTypeDesignDoc)
      console.log('Membership type design document created')
    } catch (error) {
      if (error.name !== 'conflict') {
        console.error('Error creating membership type design document:', error)
      }
    }

    // Create indexes
    await Promise.all([
      remoteDbs.members.createIndex({
        index: { fields: ['type', 'member_id'] }
      }),
      remoteDbs.members.createIndex({
        index: { fields: ['type', 'active', 'end_date'] }
      }),
      remoteDbs.members.createIndex({
        index: { fields: ['type', 'membership_type_id'] }
      }),
      remoteDbs.members.createIndex({
        index: { fields: ['type', 'vehicles.license_plate'] }
      }),
      remoteDbs.members.createIndex({
        index: { fields: ['type', 'phone'] }
      }),
      remoteDbs.members.createIndex({
        index: { fields: ['type', 'email'] }
      }),
      remoteDbs.members.createIndex({
        index: { fields: ['type', 'createdAt'] }
      }),
      remoteDbs.members.createIndex({
        index: { fields: ['type', 'name'] }
      }),
      remoteDbs.members.createIndex({
        index: { fields: ['createdAt'] }
      }),
      remoteDbs.membershipTypes.createIndex({
        index: { fields: ['type', 'category'] }
      }),
      remoteDbs.membershipTypes.createIndex({
        index: { fields: ['type', 'name'] }
      }),
      remoteDbs.membershipTypes.createIndex({
        index: { fields: ['name'] }
      }),
      // Index for member usage history
      remoteDbs.transactions.createIndex({
        index: { fields: ['type', 'member_id', 'timestamp'] }
      }),
      remoteDbs.transactions.createIndex({
        index: { fields: ['type', 'timestamp'] }
      })
    ])

    console.log('Member database indexes created')

    // Initialize default membership types if none exist
    await initializeDefaultMembershipTypes()

    console.log('Member database initialization completed')
    return { success: true, message: 'Member database initialized successfully' }
  } catch (error) {
    console.error('Error initializing member database:', error)
    throw error
  }
}

/**
 * Initialize default membership types
 */
export const initializeDefaultMembershipTypes = async () => {
  try {
    // Check if membership types already exist
    const existingTypes = await remoteDbs.membershipTypes.find({
      selector: { type: 'membership_type' }
    })

    if (existingTypes.docs.length > 0) {
      console.log('Membership types already exist, skipping initialization')
      return
    }

    const defaultTypes = [
      {
        _id: `membership_type_${Date.now()}_regular`,
        type: 'membership_type',
        name: 'Regular Member',
        category: 'REGULAR',
        price: 100000,
        area_type: 'residential',
        max_vehicles: 2,
        operating_hours: {
          start: '06:00',
          end: '22:00'
        },
        duration_months: 12,
        description: 'Membership reguler dengan akses standar',
        facilities: ['CCTV 24 Jam', 'Keamanan'],
        benefits: ['Diskon 15%'],
        access_areas: ['main_parking'],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        _id: `membership_type_${Date.now()}_premium`,
        type: 'membership_type',
        name: 'Premium Member',
        category: 'PREMIUM',
        price: 200000,
        area_type: 'residential',
        max_vehicles: 3,
        operating_hours: {
          start: '00:00',
          end: '23:59'
        },
        duration_months: 12,
        description: 'Membership premium dengan fasilitas lengkap',
        facilities: ['CCTV 24 Jam', 'Keamanan', 'Valet Parking', 'Wi-Fi Gratis'],
        benefits: ['Diskon 30%', 'Priority Access'],
        access_areas: ['main_parking', 'premium_area'],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        _id: `membership_type_${Date.now()}_vip`,
        type: 'membership_type',
        name: 'VIP Member',
        category: 'VIP',
        price: 500000,
        area_type: 'commercial',
        max_vehicles: 5,
        operating_hours: {
          start: '00:00',
          end: '23:59'
        },
        duration_months: 12,
        description: 'Membership VIP dengan semua fasilitas dan benefit',
        facilities: ['CCTV 24 Jam', 'Keamanan', 'Valet Parking', 'Wi-Fi Gratis', 'Cuci Mobil', 'Area Tunggu'],
        benefits: ['Diskon 50%', 'Priority Access', 'Extended Hours', 'Premium Support'],
        access_areas: ['main_parking', 'premium_area', 'vip_area'],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        _id: `membership_type_${Date.now()}_corporate`,
        type: 'membership_type',
        name: 'Corporate Member',
        category: 'CORPORATE',
        price: 300000,
        area_type: 'commercial',
        max_vehicles: 10,
        operating_hours: {
          start: '00:00',
          end: '23:59'
        },
        duration_months: 12,
        description: 'Membership khusus untuk perusahaan',
        facilities: ['CCTV 24 Jam', 'Keamanan', 'Wi-Fi Gratis', 'Area Tunggu'],
        benefits: ['Diskon 25%', 'Guest Parking', 'Extended Hours'],
        access_areas: ['main_parking', 'corporate_area'],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]

    // Insert default membership types
    for (const type of defaultTypes) {
      await remoteDbs.membershipTypes.put(type)
    }

    console.log('Default membership types created')
    return defaultTypes
  } catch (error) {
    console.error('Error initializing default membership types:', error)
    throw error
  }
}

/**
 * Create sample member data for testing
 */
export const createSampleMembers = async () => {
  try {
    // Get membership types
    const membershipTypes = await remoteDbs.membershipTypes.find({
      selector: { type: 'membership_type' }
    })

    if (membershipTypes.docs.length === 0) {
      throw new Error('No membership types found. Please initialize membership types first.')
    }

    const sampleMembers = [
      {
        _id: `member_${Date.now()}_sample1`,
        type: 'member',
        member_id: 'MBR001',
        name: 'John Doe',
        email: 'john.doe@email.com',
        phone: '081234567890',
        address: 'Jl. Sudirman No. 123, Jakarta',
        identity_number: '3201234567890123',
        vehicles: [
          {
            type: 'Mobil',
            license_plate: 'B1234ABC',
            brand: 'Toyota',
            model: 'Avanza',
            color: 'Putih',
            year: '2020'
          }
        ],
        membership_type_id: membershipTypes.docs[0]._id,
        start_date: new Date().toISOString().split('T')[0],
        end_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        payment_status: 'paid',
        notes: 'Member reguler aktif',
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
        _id: `member_${Date.now()}_sample2`,
        type: 'member',
        member_id: 'MBR002',
        name: 'Alice Smith',
        email: 'alice.smith@email.com',
        phone: '081234567892',
        address: 'Jl. Thamrin No. 456, Jakarta',
        identity_number: '3201234567890124',
        vehicles: [
          {
            type: 'Mobil',
            license_plate: 'B5678XYZ',
            brand: 'Honda',
            model: 'Civic',
            color: 'Hitam',
            year: '2021'
          },
          {
            type: 'Motor',
            license_plate: 'B9999ZZ',
            brand: 'Yamaha',
            model: 'NMAX',
            color: 'Biru',
            year: '2022'
          }
        ],
        membership_type_id: membershipTypes.docs[1]._id, // Premium
        start_date: new Date().toISOString().split('T')[0],
        end_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        payment_status: 'paid',
        notes: 'Member premium dengan 2 kendaraan',
        emergency_contact: {
          name: 'Bob Smith',
          phone: '081234567893',
          relationship: 'Suami'
        },
        active: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]

    // Insert sample members
    for (const member of sampleMembers) {
      await remoteDbs.members.put(member)
    }

    console.log('Sample members created')
    return sampleMembers
  } catch (error) {
    console.error('Error creating sample members:', error)
    throw error
  }
}

/**
 * Verify member database setup
 */
export const verifyMemberDatabase = async () => {
  try {
    console.log('Verifying member database...')

    // Check design documents
    try {
      await remoteDbs.members.get('_design/members')
      console.log('✓ Member design document exists')
    } catch (error) {
      console.error('✗ Member design document missing')
      throw new Error('Member design document not found')
    }

    try {
      await remoteDbs.membershipTypes.get('_design/membership_types')
      console.log('✓ Membership type design document exists')
    } catch (error) {
      console.error('✗ Membership type design document missing')
      throw new Error('Membership type design document not found')
    }

    // Check membership types
    const membershipTypes = await remoteDbs.membershipTypes.find({
      selector: { type: 'membership_type' }
    })
    console.log(`✓ Found ${membershipTypes.docs.length} membership types`)

    // Check members
    const members = await remoteDbs.members.find({
      selector: { type: 'member' }
    })
    console.log(`✓ Found ${members.docs.length} members`)

    // Test views
    try {
      const activeMembers = await remoteDbs.members.query('members/active_members')
      console.log(`✓ Active members view working: ${activeMembers.rows.length} active members`)
    } catch (error) {
      console.error('✗ Active members view failed:', error)
    }

    console.log('Member database verification completed')
    return {
      success: true,
      membershipTypes: membershipTypes.docs.length,
      members: members.docs.length
    }
  } catch (error) {
    console.error('Member database verification failed:', error)
    throw error
  }
}

/**
 * Reset member database (for development/testing)
 */
export const resetMemberDatabase = async () => {
  try {
    console.log('Resetting member database...')

    // Get all members and membership types
    const [members, membershipTypes] = await Promise.all([
      remoteDbs.members.allDocs({ include_docs: true }),
      remoteDbs.membershipTypes.allDocs({ include_docs: true })
    ])

    // Delete all documents
    const deletePromises: Promise<any>[] = []

    for (const row of members.rows) {
      if (row.doc && !row.id.startsWith('_design/')) {
        deletePromises.push(remoteDbs.members.remove(row.doc))
      }
    }

    for (const row of membershipTypes.rows) {
      if (row.doc && !row.id.startsWith('_design/')) {
        deletePromises.push(remoteDbs.membershipTypes.remove(row.doc))
      }
    }

    await Promise.all(deletePromises)
    console.log('Member database reset completed')

    return { success: true, message: 'Member database reset successfully' }
  } catch (error) {
    console.error('Error resetting member database:', error)
    throw error
  }
}

export default {
  initializeMemberDatabase,
  initializeDefaultMembershipTypes,
  createSampleMembers,
  verifyMemberDatabase,
  resetMemberDatabase
}
