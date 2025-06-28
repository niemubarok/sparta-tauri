/**
 * Quick fix script untuk memperbaiki index PouchDB member database
 * Jalankan script ini di browser console untuk memperbaiki error sorting
 */

export const fixMemberDatabaseIndexes = async () => {
  console.log('🔧 Fixing member database indexes...')
  
  try {
    // Import PouchDB dari boot file
    const { localDbs } = await import('src/boot/pouchdb')
    
    const indexPromises = []
    
    // Members collection indexes
    indexPromises.push(
      localDbs.members.createIndex({
        index: { fields: ['type', 'createdAt'] }
      }).catch(err => console.log('Index already exists:', err.message))
    )
    
    indexPromises.push(
      localDbs.members.createIndex({
        index: { fields: ['type', 'name'] }
      }).catch(err => console.log('Index already exists:', err.message))
    )
    
    indexPromises.push(
      localDbs.members.createIndex({
        index: { fields: ['type', 'member_id'] }
      }).catch(err => console.log('Index already exists:', err.message))
    )
    
    indexPromises.push(
      localDbs.members.createIndex({
        index: { fields: ['type', 'active', 'end_date'] }
      }).catch(err => console.log('Index already exists:', err.message))
    )
    
    indexPromises.push(
      localDbs.members.createIndex({
        index: { fields: ['createdAt'] }
      }).catch(err => console.log('Index already exists:', err.message))
    )
    
    // Membership types collection indexes
    indexPromises.push(
      localDbs.membershipTypes.createIndex({
        index: { fields: ['type', 'name'] }
      }).catch(err => console.log('Index already exists:', err.message))
    )
    
    indexPromises.push(
      localDbs.membershipTypes.createIndex({
        index: { fields: ['name'] }
      }).catch(err => console.log('Index already exists:', err.message))
    )
    
    indexPromises.push(
      localDbs.membershipTypes.createIndex({
        index: { fields: ['type', 'category'] }
      }).catch(err => console.log('Index already exists:', err.message))
    )
    
    // Member usage tracking indexes
    indexPromises.push(
      localDbs.transactions.createIndex({
        index: { fields: ['type', 'member_id', 'timestamp'] }
      }).catch(err => console.log('Index already exists:', err.message))
    )
    
    indexPromises.push(
      localDbs.transactions.createIndex({
        index: { fields: ['type', 'timestamp'] }
      }).catch(err => console.log('Index already exists:', err.message))
    )
    
    // Wait for all indexes to be created
    await Promise.all(indexPromises)
    
    console.log('✅ Member database indexes fixed!')
    console.log('🔄 Recommended: Refresh the page to reload the membership store')
    
    return {
      success: true,
      message: 'Member database indexes fixed successfully'
    }
  } catch (error) {
    console.error('❌ Error fixing member database indexes:', error)
    throw error
  }
}

// Auto-run function untuk console
window.fixMemberDatabaseIndexes = fixMemberDatabaseIndexes

console.log(`
🔧 Member Database Index Fix Script Loaded

To fix the member database indexes, run:
fixMemberDatabaseIndexes()

This will create the necessary indexes for proper sorting and querying.
`)

export default fixMemberDatabaseIndexes
