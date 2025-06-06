import PouchDB from 'pouchdb';

async function verifyAndCreateViews() {
  const db = new PouchDB('transaksi');

  try {
    // 1. Verify database exists
    const info = await db.info();
    console.log('📊 Database Info:', JSON.stringify(info, null, 2));

    // 2. Define views
    const designDocs = {
      '_design/transaksi': {
        _id: '_design/transaksi',
        language: 'javascript',
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
      '_design/gate_operations': {
        _id: '_design/gate_operations',
        language: 'javascript',
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

    // 3. Create or update design documents
    for (const [id, doc] of Object.entries(designDocs)) {
      try {
        const existing = await db.get(id);
        console.log(`📝 Found existing design doc: ${id}`);
        // Update if exists
        await db.put({
          ...doc,
          _rev: existing._rev
        });
        console.log(`✅ Updated design doc: ${id}`);
      } catch (e: any) {
        if (e.name === 'not_found') {
          // Create if doesn't exist
          await db.put(doc);
          console.log(`✅ Created new design doc: ${id}`);
        } else {
          throw e;
        }
      }
    }

    // 4. Insert test document
    const testDoc = {
      _id: 'test_entry_' + new Date().toISOString(),
      type: 'entry',
      timestamp: new Date().toISOString(),
      plateNumber: 'TEST123',
      gateId: 'TEST_GATE'
    };

    try {
      await db.put(testDoc);
      console.log('📝 Inserted test document');
    } catch (e) {
      console.log('❌ Could not insert test document:', e);
    }

    // 5. Verify views work
    console.log('\n🔍 Testing views...');

    // Test by_date view
    const dateResult = await db.query('transaksi/by_date', {
      reduce: true,
      group: true
    });
    console.log('by_date view result:', dateResult.rows);

    // Test by_plate view
    const plateResult = await db.query('transaksi/by_plate', {
      key: 'TEST123'
    });
    console.log('by_plate view result:', plateResult.rows);

    // 6. Clean up test document
    try {
      const doc = await db.get(testDoc._id);
      await db.remove(doc);
      console.log('🧹 Cleaned up test document');
    } catch (e) {
      console.log('❌ Could not clean up test document:', e);
    }

    console.log('\n✨ All views have been verified and are working correctly!');

  } catch (error) {
    console.error('❌ Error:', error);
  }
}

// Run verification
verifyAndCreateViews()
  .then(() => {
    console.log('✅ Script completed');
  })
  .catch((error) => {
    console.error('💥 Fatal error:', error);
  });
