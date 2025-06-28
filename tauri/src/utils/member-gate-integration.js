import { useMembershipStore } from 'src/stores/membership-store'

/**
 * Member integration utilities for gate entry/exit system
 */

export class MemberGateIntegration {
  constructor() {
    this.membershipStore = useMembershipStore()
  }

  /**
   * Check if a license plate belongs to an active member
   * @param {string} plateNumber - License plate number
   * @returns {Promise<Object|null>} Member data with discount info or null
   */
  async checkMemberStatus(plateNumber) {
    try {
      if (!plateNumber || plateNumber.trim() === '') {
        return null
      }

      const member = await this.membershipStore.checkMembershipWithDiscount(plateNumber.trim())
      
      if (!member) {
        return null
      }

      // Additional validation
      if (member.active !== 1) {
        return {
          ...member,
          membershipStatus: 'inactive',
          canPark: false,
          message: 'Member tidak aktif'
        }
      }

      if (member.isExpired) {
        return {
          ...member,
          membershipStatus: 'expired',
          canPark: false,
          message: `Membership sudah berakhir ${Math.abs(member.daysUntilExpiry)} hari yang lalu`
        }
      }

      if (member.isExpiringSoon) {
        return {
          ...member,
          membershipStatus: 'expiring',
          canPark: true,
          message: `Membership akan berakhir dalam ${member.daysUntilExpiry} hari`
        }
      }

      return {
        ...member,
        membershipStatus: 'active',
        canPark: true,
        message: 'Member aktif'
      }
    } catch (error) {
      console.error('Error checking member status:', error)
      throw error
    }
  }

  /**
   * Calculate parking fee with member discount
   * @param {number} baseFee - Base parking fee
   * @param {Object} member - Member data
   * @returns {Object} Fee calculation with discount
   */
  calculateMemberFee(baseFee, member) {
    if (!member || !member.hasDiscount || member.membershipStatus !== 'active') {
      return {
        originalFee: baseFee,
        discountPercentage: 0,
        discountAmount: 0,
        finalFee: baseFee,
        isMemberDiscount: false
      }
    }

    const discountAmount = Math.floor(baseFee * (member.discountPercentage / 100))
    const finalFee = baseFee - discountAmount

    return {
      originalFee: baseFee,
      discountPercentage: member.discountPercentage,
      discountAmount: discountAmount,
      finalFee: Math.max(finalFee, 0), // Ensure non-negative
      isMemberDiscount: true,
      memberName: member.name,
      memberType: member.membershipType,
      memberCategory: member.membershipCategory
    }
  }

  /**
   * Record member entry/exit activity
   * @param {Object} member - Member data
   * @param {string} plateNumber - License plate
   * @param {string} action - 'entry' or 'exit'
   * @param {Object} gateInfo - Gate information
   * @returns {Promise<Object>} Usage record
   */
  async recordMemberActivity(member, plateNumber, action, gateInfo = {}) {
    try {
      const activityRecord = {
        member_id: member._id,
        member_name: member.name,
        license_plate: plateNumber.toUpperCase(),
        action,
        timestamp: new Date().toISOString(),
        gate_id: gateInfo.gateId || 'unknown',
        gate_location: gateInfo.location || 'main_gate',
        operator: gateInfo.operator || 'system',
        membership_type: member.membershipType,
        membership_category: member.membershipCategory,
        membership_status: member.membershipStatus
      }

      // Record in membership store
      await this.membershipStore.recordMemberUsage(member._id, plateNumber, action)

      return activityRecord
    } catch (error) {
      console.error('Error recording member activity:', error)
      throw error
    }
  }

  /**
   * Validate member vehicle access
   * @param {Object} member - Member data
   * @param {string} vehicleType - Type of vehicle (Mobil, Motor, etc.)
   * @returns {Object} Validation result
   */
  validateVehicleAccess(member, vehicleType) {
    if (!member || member.membershipStatus !== 'active') {
      return {
        isValid: false,
        message: 'Member tidak aktif'
      }
    }

    // Check if vehicle type is registered
    const registeredVehicle = member.vehicles.find(v => 
      v.type.toLowerCase() === vehicleType.toLowerCase()
    )

    if (!registeredVehicle) {
      return {
        isValid: false,
        message: `Tipe kendaraan ${vehicleType} tidak terdaftar untuk member ini`
      }
    }

    // Check membership type vehicle limits
    const membershipType = this.membershipStore.membershipTypes.find(t => 
      t._id === member.membership_type_id
    )

    if (membershipType) {
      // Check operating hours
      const now = new Date()
      const currentTime = now.toTimeString().slice(0, 5) // HH:MM format
      
      if (membershipType.operating_hours) {
        const startTime = membershipType.operating_hours.start
        const endTime = membershipType.operating_hours.end
        
        if (currentTime < startTime || currentTime > endTime) {
          return {
            isValid: false,
            message: `Akses member hanya berlaku dari ${startTime} - ${endTime}`
          }
        }
      }
    }

    return {
      isValid: true,
      message: 'Akses kendaraan valid',
      vehicleInfo: registeredVehicle
    }
  }

  /**
   * Get member parking privileges
   * @param {Object} member - Member data
   * @returns {Object} Parking privileges
   */
  getMemberPrivileges(member) {
    if (!member || member.membershipStatus !== 'active') {
      return {
        hasPreferredParking: false,
        hasValetService: false,
        hasExtendedHours: false,
        hasGuestParking: false,
        maxParkingHours: 24,
        accessAreas: ['main_parking']
      }
    }

    const membershipType = this.membershipStore.membershipTypes.find(t => 
      t._id === member.membership_type_id
    )

    if (!membershipType) {
      return {
        hasPreferredParking: false,
        hasValetService: false,
        hasExtendedHours: false,
        hasGuestParking: false,
        maxParkingHours: 24,
        accessAreas: ['main_parking']
      }
    }

    const privileges = {
      hasPreferredParking: membershipType.category === 'VIP' || membershipType.category === 'PREMIUM',
      hasValetService: membershipType.facilities?.includes('Valet Parking') || false,
      hasExtendedHours: membershipType.benefits?.includes('Extended Hours') || false,
      hasGuestParking: membershipType.benefits?.includes('Guest Parking') || false,
      maxParkingHours: membershipType.category === 'VIP' ? 48 : 24,
      accessAreas: membershipType.access_areas || ['main_parking'],
      facilities: membershipType.facilities || [],
      benefits: membershipType.benefits || []
    }

    return privileges
  }

  /**
   * Check if member can use a specific parking area
   * @param {Object} member - Member data
   * @param {string} areaId - Parking area ID
   * @returns {boolean} Access allowed
   */
  canAccessParkingArea(member, areaId) {
    if (!member || member.membershipStatus !== 'active') {
      return false
    }

    const privileges = this.getMemberPrivileges(member)
    return privileges.accessAreas.includes(areaId) || privileges.accessAreas.includes('all_areas')
  }

  /**
   * Generate member parking notification
   * @param {Object} member - Member data
   * @param {string} action - 'entry' or 'exit'
   * @returns {Object} Notification data
   */
  generateMemberNotification(member, action) {
    const notifications = []

    // Welcome/goodbye message
    if (action === 'entry') {
      notifications.push({
        type: 'welcome',
        title: `Selamat Datang, ${member.name}!`,
        message: `Member ${member.membershipCategory}`,
        icon: 'wave',
        color: 'positive'
      })

      // Discount notification
      if (member.hasDiscount) {
        notifications.push({
          type: 'discount',
          title: 'Diskon Member Aktif',
          message: `Anda mendapat diskon ${member.discountPercentage}%`,
          icon: 'local_offer',
          color: 'primary'
        })
      }

      // Expiring warning
      if (member.isExpiringSoon) {
        notifications.push({
          type: 'warning',
          title: 'Membership Akan Berakhir',
          message: `Membership akan berakhir dalam ${member.daysUntilExpiry} hari`,
          icon: 'warning',
          color: 'warning'
        })
      }
    } else if (action === 'exit') {
      notifications.push({
        type: 'goodbye',
        title: `Terima Kasih, ${member.name}!`,
        message: 'Sampai jumpa kembali',
        icon: 'sentiment_satisfied',
        color: 'positive'
      })
    }

    return notifications
  }

  /**
   * Format member data for display
   * @param {Object} member - Member data
   * @returns {Object} Formatted display data
   */
  formatMemberDisplay(member) {
    if (!member) return null

    return {
      id: member.member_id,
      name: member.name,
      type: member.membershipType,
      category: member.membershipCategory,
      status: member.membershipStatus,
      statusLabel: this.getStatusLabel(member.membershipStatus),
      statusColor: this.getStatusColor(member.membershipStatus),
      expiryDate: member.end_date,
      expiryText: this.getExpiryText(member),
      discount: member.hasDiscount ? `${member.discountPercentage}%` : null,
      vehicles: member.vehicles?.map(v => v.license_plate).join(', ') || '',
      phone: member.phone
    }
  }

  /**
   * Helper methods
   */
  getStatusLabel(status) {
    const labels = {
      'active': 'Aktif',
      'expiring': 'Akan Berakhir',
      'expired': 'Kadaluarsa',
      'inactive': 'Tidak Aktif'
    }
    return labels[status] || 'Unknown'
  }

  getStatusColor(status) {
    const colors = {
      'active': 'green',
      'expiring': 'orange',
      'expired': 'red',
      'inactive': 'grey'
    }
    return colors[status] || 'grey'
  }

  getExpiryText(member) {
    if (!member.daysUntilExpiry) return ''
    
    const days = member.daysUntilExpiry
    if (days < 0) return `Lewat ${Math.abs(days)} hari`
    if (days === 0) return 'Hari ini'
    if (days === 1) return 'Besok'
    return `${days} hari lagi`
  }
}

// Export singleton instance
export const memberGateIntegration = new MemberGateIntegration()

// Export utility functions
export const {
  checkMemberStatus,
  calculateMemberFee,
  recordMemberActivity,
  validateVehicleAccess,
  getMemberPrivileges,
  canAccessParkingArea,
  generateMemberNotification,
  formatMemberDisplay
} = memberGateIntegration

export default memberGateIntegration
