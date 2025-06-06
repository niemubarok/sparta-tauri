import PouchDB from 'pouchdb';

// Initialize database with correct name
const db = new PouchDB('transactions');

interface DesignDoc {
  _id: string;
  _rev?: string;
  views: {
    [key: string]: {
      map: string;
      reduce?: string;
    };
  };
}

// Define views
const views: { [key: string]: DesignDoc } = {
  transactions: {
    _id: '_design/transactions',
    views: {
      by_date: {
        map: `function(doc) {
          if (doc.type === 'entry') {
            emit(doc.timestamp, 1);
          }
        }`,
        reduce: '_count'
      },
      out_by_date: {
        map: `function(doc) {
          if (doc.type === 'exit') {
            emit(doc.timestamp, 1);
          }
        }`,
        reduce: '_count'
      },      by_gate: {
        map: `function(doc) {
          if (doc.gate_id) {
            emit([doc.gate_id, doc.timestamp], 1);
          }
        }`,
        reduce: '_count'
      },
      by_plate: {
        map: `function(doc) {
          if (doc.plate_number) {
            emit(doc.plate_number, {
              type: doc.type,
              timestamp: doc.timestamp,
              gate_id: doc.gate_id,
              status: doc.status
            });
          }
        }`
      }
    }
  },
  gate_operations: {
    _id: '_design/gate_operations',
    views: {
      manual_opens: {
        map: `function(doc) {
          if (doc.type === 'manual_open') {
            emit([doc.gateId, doc.timestamp], {
              userId: doc.userId
            });
          }
        }`,
        reduce: '_count'
      },
      gate_status: {
        map: `function(doc) {
          if (doc.type === 'gate_status') {
            emit(doc.gateId, {
              status: doc.status,
              timestamp: doc.timestamp
            });
          }
        }`
      }
    }
  }
};

// Create or update views in PouchDB
async function updateViews() {
  let success = true;

  try {
    for (const [name, designDoc] of Object.entries(views)) {
      try {
        // Try to get existing design doc
        const existing = await db.get(designDoc._id);
        designDoc._rev = existing._rev;
      } catch (e: any) {
        if (e.name !== 'not_found') throw e;
      }

      // Update or create design document
      await db.put(designDoc);
      console.log(`✅ Views for ${name} updated successfully`);
    }

    // Test a simple query to verify views
    const testQuery = await db.query('transactions/by_date', {
      reduce: true,
      group: true
    });
    console.log('🔍 Test query result:', testQuery.rows.length === 0 ? 'Empty (OK)' : 'Has data (OK)');

  } catch (error) {
    console.error('❌ Error updating views:', error);
    success = false;
  }

  return success;
}

// Run the update
updateViews()
  .then((success) => {
    if (success) {
      console.log('✨ All views updated successfully');
    }
  })
  .catch((error) => {
    console.error('💥 Fatal error:', error);
  });
