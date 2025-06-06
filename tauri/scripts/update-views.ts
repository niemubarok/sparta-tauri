import PouchDB from 'pouchdb';
import fs from 'fs';
import path from 'path';

// Initialize database
const db = new PouchDB('transaksi');

// Load views from JSON file
const views = {
  transaksi: {
    _id: '_design/transaksi',
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
      },
      by_gate: {
        map: `function(doc) {
          if (doc.gateId) {
            emit([doc.gateId, doc.timestamp], 1);
          }
        }`,
        reduce: '_count'
      },
      by_plate: {
        map: `function(doc) {
          if (doc.plateNumber) {
            emit(doc.plateNumber, {
              type: doc.type,
              timestamp: doc.timestamp,
              gateId: doc.gateId
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

// Save views to JSON file for reference
const saveViewsToFile = () => {
  const viewsPath = path.join(process.cwd(), 'db', 'views.json');
  fs.mkdirSync(path.dirname(viewsPath), { recursive: true });
  fs.writeFileSync(viewsPath, JSON.stringify(views, null, 2));
  console.log('📝 Views saved to:', viewsPath);
};

// Create or update views in PouchDB
async function updateViews() {
  try {
    for (const [name, designDoc] of Object.entries(views)) {
      try {
        // Try to get existing design doc
        const existing = await db.get(designDoc._id);
        designDoc._rev = existing._rev;
      } catch (e) {
        if (e.name !== 'not_found') throw e;
      }

      // Update or create design document
      await db.put(designDoc);
      console.log(`✅ Views for ${name} updated successfully`);
    }

    // Save views to file for reference
    saveViewsToFile();

    // Test a simple query to verify views
    const testQuery = await db.query('transaksi/by_date', {
      reduce: true,
      group: true
    });
    console.log('🔍 Test query result:', testQuery.rows.length === 0 ? 'Empty (OK)' : 'Has data (OK)');

  } catch (error) {
    console.error('❌ Error updating views:', error);
    process.exit(1);
  }
}

// Run the update
updateViews()
  .then(() => {
    console.log('✨ All views updated successfully');
    process.exit(0);
  })
  .catch((error) => {
    console.error('💥 Fatal error:', error);
    process.exit(1);
  });
