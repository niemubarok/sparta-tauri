import { defineStore, acceptHMRUpdate } from 'pinia';
import { ref } from 'vue'
import { localDbs } from 'src/boot/pouchdb'

export const useMembershipStore = defineStore('membership', {
  state: () => ({
    members: ref([]),
    membershipTypes: ref([]),
    newTypeModel: ref({
      name: '',
      price: 0,
      area_type: '', // 'residential' or 'commercial'
      max_vehicles: 1, // Maximum vehicles allowed
      operating_hours: {
        start: '00:00',
        end: '23:59'
      },
      description: '', // Additional notes/description
      facilities: [] // Array of included facilities/features
    }),
    loading: ref(false)
  }),

  actions: {
    async loadMembers() {
      try {
        this.loading = true
        const result = await localDbs.members.find({
          selector: {
            type: 'member'
          }
        })
        const membershipTypes = await localDbs.membershipTypes.find({
          selector: {
            type: 'membership_type',
            _id: {
              $in: result.docs.map(doc => doc.membership_type_id)
            }
          }
        })
        this.members = result.docs.map(member => {
          const type = membershipTypes
          return {
            ...member,
            membershipType: type ? type.name : 'Unknown'
          }
        })
        console.log("🚀 ~ loadMembers ~ this.members:", this.members)
      } catch (error) {
        console.error('Failed to load members:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async loadMembershipTypes() {
      try {
        const result = await localDbs.membershipTypes.find({
          selector: {
            type: 'membership_type'
          }
        })
        this.membershipTypes = result.docs
      } catch (error) {
        console.error('Failed to load membership types:', error)
        throw error
      }
    },
    async checkMembership(plateNumber) {
      try {
        const result = await localDbs.members.find({
          selector: {
            type: 'member',
            'vehicles': {
              $elemMatch: {
          'license_plate': plateNumber
              }
            },
            active: 1
          }
        })
        console.log("🚀 ~ checkMembership ~ result:", result)
        return result.docs.length > 0 ? result.docs[0] : null
      } catch (error) {
        console.error('Failed to check membership:', error)
        throw error
      }
    },

    async addMember(memberData) {
      try {
        const doc = {
          _id: `member_${Date.now()}`,
          type: 'member',
          ...memberData,
          createdAt: new Date().toISOString()
        }
        const result = await localDbs.members.put(doc)
        await this.loadMembers()
        return result
      } catch (error) {
        console.error('Failed to add member:', error)
        throw error
      }
    },

    async updateMember(id, memberData) {
      try {
        const doc = await localDbs.members.get(id)
        const updatedDoc = {
          ...doc,
          ...memberData,
          updatedAt: new Date().toISOString()
        }
        const result = await localDbs.members.put(updatedDoc)
        await this.loadMembers()
        return result
      } catch (error) {
        console.error('Failed to update member:', error)
        throw error
      }
    },

    async deleteMember(id) {
      try {
        const doc = await localDbs.membershipTypes.get(id)
        await localDbs.members.remove(doc)
        await this.loadMembers()
      } catch (error) {
        console.error('Failed to delete member:', error)
        throw error
      }
    },

    async addMembershipType(typeData) {
      try {
        const doc = {
          _id: `membership_type_${Date.now()}`,
          type: 'membership_type',
          ...typeData,
          createdAt: new Date().toISOString()
        }
        const result = await localDbs.membershipTypes.put(doc)
        await this.loadMembershipTypes()
        return result
      } catch (error) {
        console.error('Failed to add membership type:', error)
        throw error
      }
    },

    async updateMembershipType(id, typeData) {
      try {
        const doc = await localDbs.members.get(id)
        const updatedDoc = {
          ...doc,
          ...typeData,
          updatedAt: new Date().toISOString()
        }
        const result = await localDbs.members.put(updatedDoc)
        await this.loadMembershipTypes()
        return result
      } catch (error) {
        console.error('Failed to update membership type:', error)
        throw error
      }
    },

    async deleteMembershipType(id) {
      try {
        const doc = await localDbs.members.get(id)
        await localDbs.members.remove(doc)
        await this.loadMembershipTypes()
      } catch (error) {
        console.error('Failed to delete membership type:', error)
        throw error
      }
    }
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useMembershipStore, import.meta.hot));
}
