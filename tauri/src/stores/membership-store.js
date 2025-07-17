import { defineStore } from 'pinia'
import { remoteDbs } from 'src/boot/pouchdb'

export const useMembershipStore = defineStore('membership', {
  state: () => ({
    members: [],
    membershipTypes: [],
    isLoading: false,
    isLoadingMembers: false,
    isLoadingTypes: false,
    statistics: {
      totalMembers: 0,
      activeMembers: 0,
      expiringMembers: 0,
      expiredMembers: 0,
      totalRevenue: 0,
      revenueThisMonth: 0
    },
    syncEnabled: false,
    membershipCategories: [
      { value: 'VIP', label: 'VIP Member', color: 'purple' },
      { value: 'PREMIUM', label: 'Premium Member', color: 'orange' },
      { value: 'REGULAR', label: 'Regular Member', color: 'blue' },
      { value: 'CORPORATE', label: 'Corporate Member', color: 'green' }
    ]
  }),

  getters: {
    activeMembersCount: (state) => {
      return state.members.filter(member => 
        member.active && 
        new Date(member.end_date || '2099-12-31') > new Date()
      ).length
    },

    expiringMembersCount: (state) => {
      const thirtyDaysFromNow = new Date()
      thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30)
      
      return state.members.filter(member => {
        if (!member.active) return false
        const endDate = new Date(member.end_date || '2099-12-31')
        const now = new Date()
        return endDate > now && endDate <= thirtyDaysFromNow
      }).length
    },

    expiredMembersCount: (state) => {
      const now = new Date()
      return state.members.filter(member => {
        const endDate = new Date(member.end_date || '2099-12-31')
        return member.active && endDate <= now
      }).length
    },

    membersByType: (state) => {
      const grouped = {}
      state.members.forEach(member => {
        const type = state.membershipTypes.find(t => t._id === member.membership_type_id)
        const typeName = type?.name || 'Unknown'
        
        if (!grouped[typeName]) {
          grouped[typeName] = []
        }
        grouped[typeName].push(member)
      })
      return grouped
    },

    getMemberByPlatOrCard: (state) => (value) => {
      const searchValue = value?.toLowerCase?.() || ''
      return state.members.find(member =>
        member.card_number?.toLowerCase() === searchValue ||
        member.vehicles?.some(vehicle =>
          vehicle.license_plate?.toLowerCase() === searchValue
        )
      )
    },

    // Get member by ID
    getMemberById: (state) => (id) => {
      return state.members.find(member => member._id === id)
    },

    // Get member by member_id (public ID)
    getMemberByMemberId: (state) => (memberId) => {
      return state.members.find(member => member.member_id === memberId)
    },

    // Get member by card number
    getMemberByCardNumber: (state) => (cardNumber) => {
      console.log("🚀 ~ cardNumber:", typeof cardNumber)
      return state.members.find(member => 
        String(member.card_number || '').toLowerCase() === String(cardNumber || '').toLowerCase()
      )
      
    },

    // Get membership type by ID
    getMembershipTypeById: (state) => (id) => {
      return state.membershipTypes.find(type => type._id === id)
    },
    // Check if member is expired
    isExpired: (state) => (endDate) => {
      if (!endDate) return false
      
      const end = new Date(endDate)
      end.setHours(23, 59, 59, 999) // End of day
      
      const now = new Date()
      return end < now
    },
    // Check if member is expiring soon (within 7 days)
    isExpiringSoon: (state) => (endDate) => {
      if (!endDate) return false
      
      const end = new Date(endDate)
      end.setHours(23, 59, 59, 999) // End of day
      
      const now = new Date()
      const sevenDaysFromNow = new Date()
      sevenDaysFromNow.setDate(now.getDate() + 7)
      
      return end > now && end <= sevenDaysFromNow
    },

    // Calculate days until membership expiry
    calculateDaysUntilExpiry: (state) => (endDate) => {
      if (!endDate) return null
      
      const end = new Date(endDate)
      end.setHours(0, 0, 0, 0) // Set to start of day
      
      const now = new Date()
      now.setHours(0, 0, 0, 0) // Set to start of day
      
      const diffTime = end - now
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      return diffDays
    }
    },

    actions: {
    // Initialize store
    async initializeStore() {
      try {
        console.log('🔄 Initializing membership store...')
        
        // Ensure indexes exist
        await this.ensureIndexes()
        
        // Load initial data
        await Promise.all([
          this.loadMembershipTypes(),
          this.loadMembers()
        ])
        
        // Update statistics
        this.updateStatistics()
        
        console.log('✅ Membership store initialized successfully')
        
        return true
      } catch (error) {
        console.error('❌ Failed to initialize membership store:', error)
        throw error
      }
    },

    // Initialize indexes if not exists
    async ensureIndexes() {
      try {
        console.log('🔧 Ensuring member database indexes...')
        
        const indexPromises = []
        
        // Create indexes for members collection
        indexPromises.push(
          remoteDbs.members.createIndex({
            index: { fields: ['type', 'createdAt'] }
          }).catch(err => {
            if (!err.message?.includes('already exists')) {
              console.warn('Index creation warning:', err.message)
            }
          })
        )
        
        indexPromises.push(
          remoteDbs.members.createIndex({
            index: { fields: ['type', 'name'] }
          }).catch(err => {
            if (!err.message?.includes('already exists')) {
              console.warn('Index creation warning:', err.message)
            }
          })
        )
        
        indexPromises.push(
          remoteDbs.members.createIndex({
            index: { fields: ['type', 'member_id'] }
          }).catch(err => {
            if (!err.message?.includes('already exists')) {
              console.warn('Index creation warning:', err.message)
            }
          })
        )
        
        indexPromises.push(
          remoteDbs.members.createIndex({
            index: { fields: ['type', 'active', 'end_date'] }
          }).catch(err => {
            if (!err.message?.includes('already exists')) {
              console.warn('Index creation warning:', err.message)
            }
          })
        )
        
        indexPromises.push(
          remoteDbs.members.createIndex({
            index: { fields: ['type', 'membership_type_id'] }
          }).catch(err => {
            if (!err.message?.includes('already exists')) {
              console.warn('Index creation warning:', err.message)
            }
          })
        )
        
        indexPromises.push(
          remoteDbs.members.createIndex({
            index: { fields: ['createdAt'] }
          }).catch(err => {
            if (!err.message?.includes('already exists')) {
              console.warn('Index creation warning:', err.message)
            }
          })
        )
        
        // Create indexes for membership types collection  
        indexPromises.push(
          remoteDbs.membershipTypes.createIndex({
            index: { fields: ['type', 'name'] }
          }).catch(err => {
            if (!err.message?.includes('already exists')) {
              console.warn('Index creation warning:', err.message)
            }
          })
        )
        
        indexPromises.push(
          remoteDbs.membershipTypes.createIndex({
            index: { fields: ['type', 'category'] }
          }).catch(err => {
            if (!err.message?.includes('already exists')) {
              console.warn('Index creation warning:', err.message)
            }
          })
        )
        
        indexPromises.push(
          remoteDbs.membershipTypes.createIndex({
            index: { fields: ['name'] }
          }).catch(err => {
            if (!err.message?.includes('already exists')) {
              console.warn('Index creation warning:', err.message)
            }
          })
        )
        
        // Create indexes for transactions collection (member usage)
        if (remoteDbs.transactions) {
          indexPromises.push(
            remoteDbs.transactions.createIndex({
              index: { fields: ['type', 'member_id', 'timestamp'] }
            }).catch(err => {
              if (!err.message?.includes('already exists')) {
                console.warn('Transaction index creation warning:', err.message)
              }
            })
          )
          
          indexPromises.push(
            remoteDbs.transactions.createIndex({
              index: { fields: ['type', 'timestamp'] }
            }).catch(err => {
              if (!err.message?.includes('already exists')) {
                console.warn('Transaction index creation warning:', err.message)
              }
            })
          )
        }
        
        // Wait for all indexes to be created
        await Promise.all(indexPromises)
        
        console.log('✅ Member database indexes ensured successfully')
      } catch (error) {
        console.warn('⚠️ Error ensuring indexes:', error.message)
        // Don't throw error, just warn - indexes aren't critical for basic functionality
      }
    },

    // Load members from database
    async loadMembers() {
      try {
        this.isLoadingMembers = true
        
        const result = await remoteDbs.members.allDocs({
          include_docs: true,
          startkey: 'member_',
          endkey: 'member_\uffff'
        })
        
        // Filter and sort members
        const members = result.rows
          .filter(row => row.doc && row.doc.type === 'member')
          .map(row => row.doc)
          .sort((a, b) => {
            const dateA = new Date(a.createdAt || '1970-01-01')
            const dateB = new Date(b.createdAt || '1970-01-01')
            return dateB - dateA // Most recent first
          })
        
        this.members = members
        this.updateStatistics()
        
        console.log(`✅ Loaded ${members.length} members`)
      } catch (error) {
        console.error('❌ Failed to load members:', error)
        throw error
      } finally {
        this.isLoadingMembers = false
      }
    },

    // Load membership types from database
    async loadMembershipTypes() {
      try {
        this.isLoadingTypes = true
        
        const result = await remoteDbs.membershipTypes.allDocs({
          include_docs: true,
          // startkey: 'membership_type_',
          // endkey: 'membership_type_\uffff'
        })
        
        // Filter and sort membership types
        const types = result.rows
          .filter(row => row.doc && row.doc.type === 'membership_type')
          .map(row => row.doc)
          .sort((a, b) => a.name.localeCompare(b.name))
        
        this.membershipTypes = types
        
        console.log(`✅ Loaded ${types.length} membership types`)
      } catch (error) {
        console.error('❌ Failed to load membership types:', error)
        throw error
      } finally {
        this.isLoadingTypes = false
      }
    },

    // Update statistics
    updateStatistics() {
      const now = new Date()
      const currentMonth = now.getMonth()
      const currentYear = now.getFullYear()
      
      this.statistics.totalMembers = this.members.length
      this.statistics.activeMembers = this.activeMembersCount
      this.statistics.expiringMembers = this.expiringMembersCount
      this.statistics.expiredMembers = this.expiredMembersCount
      
      // Calculate revenue
      let totalRevenue = 0
      let revenueThisMonth = 0
      
      this.members.forEach(member => {
        const membershipType = this.membershipTypes.find(t => t._id === member.membership_type_id)
        if (membershipType && membershipType.price) {
          totalRevenue += membershipType.price
          
          // Check if member was created this month
          const memberDate = new Date(member.createdAt || '1970-01-01')
          if (memberDate.getMonth() === currentMonth && memberDate.getFullYear() === currentYear) {
            revenueThisMonth += membershipType.price
          }
        }
      })
      
      this.statistics.totalRevenue = totalRevenue
      this.statistics.revenueThisMonth = revenueThisMonth
    },

    // Add new member
    async addMember(memberData) {
      try {
        // Generate member ID if not provided
        if (!memberData.member_id) {
          memberData.member_id = await this.generateMemberId()
        }
        
        // Validate required fields
        if (!memberData.name || !memberData.phone || !memberData.membership_type_id) {
          throw new Error('Required fields: name, phone, membership_type_id')
        }
        
        // Create member document
        const member = {
          _id: `member_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          type: 'member',
          ...memberData,
          active: true,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
        
        // Save to database
        const result = await remoteDbs.members.put(member)
        member._rev = result.rev
        
        // Add to local state
        this.members.unshift(member)
        this.updateStatistics()
        
        console.log('✅ Member added successfully:', member.name)
        return member
      } catch (error) {
        console.error('❌ Failed to add member:', error)
        throw error
      }
    },

    // Update member
    async updateMember(memberId, updateData) {
      try {
        const member = await remoteDbs.members.get(memberId)
        
        // Update member data
        const updatedMember = {
          ...member,
          ...updateData,
          updatedAt: new Date().toISOString()
        }
        
        // Save to database
        const result = await remoteDbs.members.put(updatedMember)
        updatedMember._rev = result.rev
        
        // Update local state
        const index = this.members.findIndex(m => m._id === memberId)
        if (index !== -1) {
          this.members[index] = updatedMember
        }
        
        this.updateStatistics()
        
        console.log('✅ Member updated successfully:', updatedMember.name)
        return updatedMember
      } catch (error) {
        console.error('❌ Failed to update member:', error)
        throw error
      }
    },

    // Delete member
    async deleteMember(memberId) {
      try {
        const member = await remoteDbs.members.get(memberId)
        await remoteDbs.members.remove(member)
        
        // Remove from local state
        this.members = this.members.filter(m => m._id !== memberId)
        this.updateStatistics()
        
        console.log('✅ Member deleted successfully')
        return true
      } catch (error) {
        console.error('❌ Failed to delete member:', error)
        throw error
      }
    },

    // Add membership type
    async addMembershipType(typeData) {
      try {
        // Validate required fields with proper checks for numbers
        if (!typeData.name || typeData.name.trim() === '') {
          throw new Error('Required field: name cannot be empty')
        }
        if (typeData.price === null || typeData.price === undefined || isNaN(Number(typeData.price))) {
          throw new Error('Required field: price must be a valid number')
        }
        if (typeData.duration_months === null || typeData.duration_months === undefined || isNaN(Number(typeData.duration_months)) || Number(typeData.duration_months) <= 0) {
          throw new Error('Required field: duration_months must be a positive number')
        }
        
        // Generate ID if not provided, or use provided ID
        let membershipTypeId
        if (typeData._id && typeData._id.trim()) {
          membershipTypeId = typeData._id.trim()
          // Check if ID already exists
          try {
            await remoteDbs.membershipTypes.get(membershipTypeId)
            throw new Error(`Membership type with ID ${membershipTypeId} already exists`)
          } catch (err) {
            // If get() throws an error, it means the ID doesn't exist, which is what we want
            if (err.name !== 'not_found') {
              throw err // Re-throw if it's not a "not found" error
            }
          }
        } else {
          membershipTypeId = `membership_type_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        }
        
        // Create membership type document
        const membershipType = {
          _id: membershipTypeId,
          type: 'membership_type',
          ...typeData,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
        
        // Remove the _id from typeData if it was passed in to avoid duplication
        delete membershipType._id
        membershipType._id = membershipTypeId
        
        // Save to database
        const result = await remoteDbs.membershipTypes.put(membershipType)
        membershipType._rev = result.rev
        
        // Add to local state
        this.membershipTypes.push(membershipType)
        this.membershipTypes.sort((a, b) => a.name.localeCompare(b.name))
        
        console.log('✅ Membership type added successfully:', membershipType.name)
        return membershipType
      } catch (error) {
        console.error('❌ Failed to add membership type:', error)
        throw error
      }
    },

    // Renew membership for a member
    async renewMembership(memberId, duration_months) {
      try {
      const member = await remoteDbs.members.get(memberId)
      const membershipType = this.membershipTypes.find(
        t => t._id === member.membership_type_id
      )
      if (!membershipType) {
        throw new Error('Membership type not found')
      }

      // Determine new start date
      let newStartDate
      const currentEnd = new Date(member.end_date || new Date())
      const now = new Date()
      newStartDate = currentEnd > now ? new Date(currentEnd.getTime() + 24 * 60 * 60 * 1000) : now

      // Calculate new end date
      const months = duration_months || membershipType.duration_months
      const newEndDate = new Date(newStartDate)
      newEndDate.setMonth(newEndDate.getMonth() + months)

      // Update member fields
      const updatedMember = {
        ...member,
        start_date: newStartDate.toISOString().split('T')[0],
        end_date: newEndDate.toISOString().split('T')[0],
        active: true,
        updatedAt: new Date().toISOString()
      }

      // Save to database
      const result = await remoteDbs.members.put(updatedMember)
      updatedMember._rev = result.rev

      // Update local state
      const index = this.members.findIndex(m => m._id === memberId)
      if (index !== -1) {
        this.members[index] = updatedMember
      }
      this.updateStatistics()

      console.log('✅ Membership renewed successfully:', updatedMember.name)
      return updatedMember
      } catch (error) {
      console.error('❌ Failed to renew membership:', error)
      throw error
      }
    },

    // Generate unique member ID
    async generateMemberId() {
      const prefix = 'SPT'
      const year = new Date().getFullYear().toString().slice(-2)
      const month = (new Date().getMonth() + 1).toString().padStart(2, '0')
      
      // Find highest existing member ID for this month
      let maxNumber = 0
      const pattern = `${prefix}${year}${month}`
      
      this.members.forEach(member => {
        if (member.member_id && member.member_id.startsWith(pattern)) {
          const number = parseInt(member.member_id.slice(-3))
          if (number > maxNumber) {
            maxNumber = number
          }
        }
      })
      
      const nextNumber = (maxNumber + 1).toString().padStart(3, '0')
      return `${pattern}${nextNumber}`
    },

    // Search members
    async searchMembers(query) {
      try {
        if (!query || query.trim() === '') {
          return this.members
        }
        
        const searchTerm = query.toLowerCase()
        
        return this.members.filter(member => {
          return (
            member.name?.toLowerCase().includes(searchTerm) ||
            member.member_id?.toLowerCase().includes(searchTerm) ||
            member.phone?.toLowerCase().includes(searchTerm) ||
            member.email?.toLowerCase().includes(searchTerm) ||
            member.vehicles?.some(vehicle => 
              vehicle.license_plate?.toLowerCase().includes(searchTerm)
            )
          )
        })
      } catch (error) {
        console.error('❌ Failed to search members:', error)
        throw error
      }
    },

    // Get expiring members
    async getExpiringMembers(days = 30) {
      try {
        const futureDate = new Date()
        futureDate.setDate(futureDate.getDate() + days)
        
        return this.members.filter(member => {
          if (!member.active) return false
          
          const endDate = new Date(member.end_date || '2099-12-31')
          const now = new Date()
          
          return endDate > now && endDate <= futureDate
        })
      } catch (error) {
        console.error('❌ Failed to get expiring members:', error)
        throw error
      }
    },

    // Initialize sample data
    async initializeSampleData() {
      try {
        console.log('🔄 Initializing sample member data...')
        
        // Check if data already exists
        if (this.members.length > 0 || this.membershipTypes.length > 0) {
          console.log('⚠️ Sample data already exists, skipping initialization')
          return false
        }
        
        // Sample membership types
        const membershipTypes = [
          {
            name: 'VIP',
            category: 'premium',
            price: 500000,
            duration_months: 12,
            max_vehicles: 3,
            discount_percentage: 50,
            description: 'Membership VIP dengan fasilitas premium dan diskon 50%'
          },
          {
            name: 'Premium',
            category: 'premium',
            price: 300000,
            duration_months: 6,
            max_vehicles: 2,
            discount_percentage: 30,
            description: 'Membership Premium dengan diskon 30%'
          },
          {
            name: 'Corporate',
            category: 'corporate',
            price: 400000,
            duration_months: 12,
            max_vehicles: 5,
            discount_percentage: 25,
            description: 'Membership Corporate untuk perusahaan'
          },
          {
            name: 'Regular',
            category: 'standard',
            price: 150000,
            duration_months: 3,
            max_vehicles: 1,
            discount_percentage: 15,
            description: 'Membership Regular standar'
          }
        ]
        
        // Add membership types
        const createdTypes = []
        for (const typeData of membershipTypes) {
          const type = await this.addMembershipType(typeData)
          createdTypes.push(type)
        }
        
        // Sample members
        const sampleMembers = [
          {
            name: 'John Doe',
            email: 'john.doe@email.com',
            phone: '081234567890',
            address: 'Jl. Merdeka No. 123, Jakarta',
            identity_number: '3201234567890123',
            membership_type_id: createdTypes[0]._id, // VIP
            start_date: new Date().toISOString().split('T')[0],
            end_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            vehicles: [
              {
                license_plate: 'B 1234 ABC',
                type: 'car',
                brand: 'Toyota',
                model: 'Camry',
                color: 'Silver'
              }
            ],
            emergency_contact: {
              name: 'Jane Doe',
              phone: '081234567891',
              relationship: 'Spouse'
            }
          },
          {
            name: 'Ahmad Santoso',
            email: 'ahmad.santoso@email.com',
            phone: '081234567892',
            address: 'Jl. Sudirman No. 456, Jakarta',
            identity_number: '3201234567890124',
            membership_type_id: createdTypes[1]._id, // Premium
            start_date: new Date().toISOString().split('T')[0],
            end_date: new Date(Date.now() + 183 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            vehicles: [
              {
                license_plate: 'B 5678 DEF',
                type: 'motorcycle',
                brand: 'Honda',
                model: 'CBR150R',
                color: 'Red'
              }
            ]
          }
        ]
        
        // Add sample members
        for (const memberData of sampleMembers) {
          await this.addMember(memberData)
        }
        
        console.log('✅ Sample member data initialized successfully')
        return true
      } catch (error) {
        console.error('❌ Failed to initialize sample data:', error)
        throw error
      }
    }
  }
})
